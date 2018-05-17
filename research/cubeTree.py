#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Todo list tras completar validators y setters
-> en repeatable add debe dividirse en (insert after, insert before, append). General de editTree
-> Incluir llamada a la consulta de guia
-> Incluir llamada al grand total
-> Las fechas artificiales (trimestres, cuatrimestres, ...) como opciones de menu aqui y no en info2*
-> Para sqlite que el selector de base de datos sea el selector de ficheros del sistema

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

import user as uf
import math 

from support.util.uf_manager import *
from base.ufhandler import functionFromName
from support.util.jsonmgr import *
from support.gui.widgets import WMultiCombo,WPowerTable, WMultiList 
from support.util.record_functions import norm2List,norm2String

import base.config as config

from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel,pyqtSignal,QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView, QStyledItemDelegate, QSpinBox, QListWidget, QPushButton, QVBoxLayout,QLabel, QWidget, QCheckBox,QStatusBar,QDialogButtonBox

from support.util.treeEditorUtil import *

from support.datalayer.access_layer import DRIVERS, AGR_LIST, DEFAULT_SCHEMA 
from support.util.fechas import CLASES_INTERVALO, TIPOS_INTERVALO
from admin.cubemgmt.cubeTypes import GUIDE_CLASS, ENUM_FORMAT,LOGICAL_OPERATOR

from support.util.jsonmgr import load_cubo
from admin.wizardmgmt.pages.guidePreview import guidePreview
from base.core import Cubo    

import os

#from admin.cubemgmt.cubeTypes import 
"""
utility functions to read from DD

"""
def _toConfName(confData):
    return '{}::{}@{}:{}'.format(
            confData['driver'],confData['dbname'],_getNorm(confData,'dbhost','localhost'),_getNorm(confData,'dbuser'))

def _exists(dd,id):
    """
    comprueba si una determinada conexion ya existe. id puede ser el texto ya procesado o un diccionario connect
    
    """
    if isinstance(id,dict):
        nombre = _toConfName(id)
    else:
        nombre = id
    lista = list(dd.configData['Conexiones'].keys())
    if nombre in lista:
        return True
    else:
        return False
    
def _getNorm(diccionario,parametro,default=''):
    """
    normaliza el valor nulo a '' para un determinado elemento de un diccionario
    """
    result = diccionario.get(parametro,default)
    if not result or result.lower() == "none":
        result = default
    return result

def _hName(item):
    """
    para un arbol como el diccionario (ver que tiene  metodo .text()) la jerarquia de claves
    
    """
    fullName = []
    fullName.append(item.text())
    pai = item.parent()
    while pai:
        fullName.insert(0,pai.text())
        pai = pai.parent()
    return fullName

def getFKLinks(tableDdItem,order='FK'):
    """
    parent y child son siempre en el sentido FK, en el caso de FK_REFERENCE realmetne es al refves
    """
    
    def _getFKs(tabla,order):
        entradas = []
        for k in range(tabla.rowCount()):
            if tabla.child(k).text() ==order:
                fklist = tabla.child(k)
                for j in range(fklist.rowCount()):
                    fkelem = fklist.child(j)
                    tabla_ref = fkelem.getRow()[1].split('.')[-1]
                    #entradas.append([tabla_ref,fkelem,tabla.text()])
                    entradas.append({'parent':tabla_ref,'ref':fkelem,'child':tabla.text()})
        return entradas
    
    def _locateFile(entrada):
        pai =entrada['ref'].parent()
        while pai.getTypeText().lower() != 'schema':
            pai = pai.parent()
        for k in range(pai.rowCount()):
            if pai.child(k,0).text() == entrada['parent']:  #no del todo
                tabla =pai.child(k,0)
                return tabla
        return None
    
    def _getNextLevel(visited,pendientes,processed,order):
            nextlevel = []
            for entrada in pendientes:
                if entrada['ref'].text() in processed:
                    continue
                else:
                    processed.add(entrada['ref'].text())
                    
                if entrada['parent'] not in visited:
                    tabla = _locateFile(entrada)
                    if not tabla:
                        continue
                    npendientes = _getFKs(tabla,order)
                    visited[entrada['parent']] = npendientes
                else:
                    npendientes = visited[entrada['parent']]
                    for k in range(len(npendientes)):
                        npendientes[k]['child'] = entrada['parent']
                nextlevel += npendientes
            return nextlevel
        
    def _getDest(hacia,biglist,maxlevel):
        results = []
        for row in range(maxlevel):
            destinos = [ k for k,entrada in enumerate(biglist[row]) if entrada['parent'] == hacia ]
            #destinos = [ entrada[0] for entrada in biglist[k]]
            for col in destinos:
                results.append((row,col))
        #print('hay ',len(results),' rutas directas posibles para ',hacia,' en el nivel',maxlevel -1)
        return results
  
    def _navega(hacia,rutas,biglist,maxlevel,desde):
        if maxlevel <0:
            return rutas
        nrutas = []
        caminos = _getDest(hacia,biglist,maxlevel)
        for entry in caminos:
            row = entry[0]
            col = entry[1]
            entrada = biglist[row][col]
            #print('estoy en',entrada,row)
            fuente = biglist[row][col]['child']
            if fuente == desde:
                nrutas += [ [entrada,],]
                continue
            else:
                #print('ahora voy a',fuente,row)
                nrutas += _navega(fuente,[[entrada,],],biglist,row,desde)
        resultado = []
        if len(rutas) == 0:
            resultado = nrutas
        else:
            for ruta in rutas:
                for nruta in nrutas:
                    resultado.append(nruta + ruta)
        #print('hacia',hacia,' maxlevel',maxlevel)
        #pprint(resultado)
        return resultado

    def _path2cadena(path):
        cadena = ''
        for arc in path:
            cadena += '-> {} ({}) '.format(arc['parent'],arc['ref'].text().replace('_fkey',''))
        return cadena

    desde = tableDdItem.text()
    visited = dict()
    processed = set()        
    pendientes = _getFKs(tableDdItem,order)
    if not pendientes:
        print('sin fks definidas, mal vamos')
        return None
    if tableDdItem.text() not in visited:
        visited[tableDdItem.text()] = pendientes
    biglist = []
    biglist.append(pendientes)
    cantidaz = len(processed)
    k = 1
    while True: 
        thislevel = _getNextLevel(visited,biglist[ -1],processed,order)
        if len(thislevel) != 0:
            biglist.append(thislevel)
        else:
            break
        if len(processed) == cantidaz:  #no he encontrado una FK nueva
            break
        cantidaz = len(processed)
        k += 1
        if k == 10:
            print('salgo escopetado')
            break
    

    tdict = {}    
    superres = []
    for row,lista in enumerate(biglist):
        for linea in lista:
            resultado = _navega(linea['parent'],[],biglist,row +1,desde)
            superres += resultado
            for entrada in resultado:
                parent = entrada[-1]['parent']
                child     = entrada[0]['child']
                if parent in tdict:
                    tdict[parent][_path2cadena(entrada)] =entrada
                else:
                    tdict[parent]= dict()
                    tdict[parent][_path2cadena(entrada)] =entrada
    return tdict
    pprint(tdict)
    
def changeTable(string,oldName,newName):
    import re
    """
    replace strings which are first level on a dot hierarchy
    re explanation ... find a chain oldname (conveniently stripped of its dots) between
                                SOL or a delimiter -except . and
                                any delimiter or EOL
    """
    pattern = r'(^|[^A-Za-z0-9_\.])('+oldName.replace('.',r'\.') + ')(\W|\.|$)'
    fileRepl   = r'\1'+ newName + r'\3'
    result = re.sub(pattern,fileRepl,string)
    return result

def file2datadict(fileName,secure=True,exclude=True):
    """
    de cubo a DataDictionary
    
    """
    mis_cubos = load_cubo('testcubo.json')
    dd = None
    for cubo in mis_cubos:
        if cubo == 'default':
            continue
        confData = mis_cubos[cubo]['connect']
        #el driver tambien forma parte de la identificacion
        confName = _toConfName(confData)
        if not dd:
            dd = DataDict(conName = confName,confData=confData,secure=secure,sysExclude=exclude)
        elif _exists(dd,confName):
            print('conexion <',confName,'> ya existe')
            continue
        else:
            dd.appendConnection(confName=confName,confData=confData,secure=secure,sysExclude=exclude)
    return dd

def datadict2dict(head):
    """
    convierte el QStandardItemModel de un DataDict en un diccionario. 
    La estructura de un DD puede ser buena para danabrowse, pero es un petardo autentico para programar

    head es el elemento raiz
    """
    resultado = {}
    for entry in traverse(head):
        fName = _hName(entry)
        # la linea de conexiones se trata por separado
        if len(fName) == 1:
            if fName[0] not in resultado:   #probablemente overkill
                resultado[fName[0]] = {'@tipo':entry.getTypeText(),'@engine':entry.getRow()[1]}
            continue
        
        if entry.text() in ('FIELDS','FK','FK_REFERENCE') and not entry.hasChildren():
            continue
        
        padre = resultado
        for nombre in fName[0:-1]:
            try:
                padre = padre[nombre]
            except KeyError:
                print('Horror',nombre,' de ',fName,' en ',padre)
                exit()
        if entry.getTypeText() in ('Schema','Table','View','FIELDS','FK','FK_REFERENCE'):
            padre[entry.text()] = {'@tipo':entry.getTypeText()}
            
        else:
            if len(fName) >2 and fName[-2] == 'FIELDS':
                padre[entry.text()] = {'@tipo':'Field','@fmt':entry.getRow()[1]}
            elif len(fName) >2  and fName[-2] in ( 'FK_REFERENCE','FK'):
                #TODO discriminar cual es cual
                agay = entry.getRow()
                name = agay[0]
                fields = agay[1:]
                padre[entry.text()] = {'@tipo':'FK_reference','@name':name,'@fields':fields}
            else: 
                padre[entry.text()] = {'@tipo':entry.text() }

    return resultado



def isDictFromDef(item):
    """
    determina si el nodo es la cabeza de un diccionario viendo como son los hijos.
    Es demasiado simple para otra cosa que lo que tenemos
    
    FIXME depende de getItemContext()
    """
    if item.hasChildren():
        contexto = Context(item)
        repeat = contexto.get('repeteable',False)
        if repeat:
            return False
        objtype_context =  contexto.get('edit_tree',{}).get('objtype')
        if objtype_context == 'dict':
            return True
        elif objtype_context is not None:
            return False
        
        firstChild = item.child(0,0)
        firstChildTipo = item.child(0,2)
        if not firstChildTipo:                             #los elementos de una lista pura no tienen tipo y no deberian tener ese elemento
            return False
        elif firstChildTipo.data() is None:
            return False
        elif firstChild.data() is None:                 #los elementos de una lista no tienen nombre
            return False
        else:
            return True
    else:
        return False

"""
   auxiliares para los callbacks
"""
        
def getSchemaFromConnection(item):
    """
    orden preferencia

    1) esquema de la tabla
    2) esquema de la conexion
    3) esquema defecto del gestor
        
    """    
    fileItem = getChildByType(getParentByType(item,'base'),'table')
    fileItem = fileItem.parent().child(fileItem.row(),1).data()  
    schema,fName = padd(fileItem.split('.'),2,pos='before')
    if schema:
        return schema
    
    confData = getConnection(item,name=False)
    if 'schema' in confData:
        return confData['schema']
    else:
        esquema = DEFAULT_SCHEMA[confData.get('driver')]
        if esquema[0] == '@':
            esquema = confData.get(esquema[1:])
        return esquema

"""
principales
"""
def getConnection(item,**kwparm):
    #from research.cubeTree import _toConfName
    conItem = getChildByType(getParentByType(item,'base'),'connect')
    n,i,t = getRow(conItem)
    datos = {}
    print('nombre',n.data())
    for k in range(n.rowCount()):
        nh = n.child(k,0)
        ih  = n.child(k,1)
        datos[nh.data()] = ih.data()
    if kwparm.get('name',False):
        dd = kwparm.get('dict',None)
        if dd:
            defConex = dd.configData['Conexiones'] #just debug
        else :
            defConex ={}
        normName = _toConfName(datos)
        if dd and normName not in defConex:
            attrlist = ('driver','dbhost','dbname','dbuser')
            for entrada in defConex:
                es = True
                for attr in attrlist:
                    if ( _getNorm(defConex[entrada],attr,'' if attr != 'dbhost' else 'localhost') != 
                        _getNorm(datos,attr,'' if attr != 'dbhost' else 'localhost') ):
                        es = False
                        break
                if not es:
                    continue
                return entrada,datos
            else:
                raise ValueError('Conexion ',normName,' no existe en diccionario')
                
        else:
            return _toConfName(datos),datos
    else:
        return datos

        
def getSchema(item,file=None):

    schema = None
    if file is not None:
        schema,fName = padd(file.split('.'),2,pos='before')
        if schema:
            return schema
    return getSchemaFromConnection(item)
        
        
def getFile(item,show='fqn'):
    """
    tres salidas:
    fqn  o fullqualifiedName -> el nombre cualificado (de hecho el que aparece en el item
    base -> solo basename
    list   -> array [schema,basename]
    """
    n,i,t = getRow(item)
    fileItem = None
    if t.data () == 'rel_elem':
        fileItem = getChildByType(getParentByType(item,'link via'),'table')
    elif t.data() == 'base_elem':
        link_via = getParentByType(item,'link via')
        pos = link_via.row()
        if pos == 0:
            fileItem = getChildByType(getParentByType(item,'base'),'table')
        else:
            lvg = getParentByType(link_via,'link via')
            link_via = lvg.child(pos)
            fileItem  = getChildByType(link_via,'table')
    elif t.data() in ('code','desc'):
        fileItem = getChildByType(getParentByType(item,'domain'),'table')
        if not fileItem: #¿seguro que es esto lo que quiero?
            fileItem = getChildByType(getParentByType(item,'base'),'table')
    elif t.data() in ('elem'):
        pai = item.parent()
        fileItem = getChildByType(pai,'table')
        if not fileItem:
            lvg = getChildByType(pai,'link via')
            if lvg:
                fileItem = getChildByType(lvg.child(lvg.rowCount() -1),'table')
            else:
                fileItem = getChildByType(getParentByType(item,'base'),'table')
        else:
            fileItem = getChildByType(getParentByType(item,'base'),'table')
    else:
    #elif t.data() in ( 'fields','date_filter'):
        fileItem = getChildByType(getParentByType(item,'base'),'table')
    # la sintaxis para obtener erma
    fileName = fileItem.parent().child(fileItem.row(),1).data()  
    if show == 'fqn':
        return fileName
    esquema,baseName = padd(fileName.split('.'),2,pos='before')
    if show == 'base':
        return baseName
    elif show == 'list':
        return esquema,baseName

    
"""
Callbacks del editor
Ahora mismo tengo los siguientes callbacks
* getter
* setter
* digger (para el brrado)
* validator
* source ->
previsto
* default
parametros comunes
    item
    TreeView
    
"""
def srcSchemas(*lparm):
    item = lparm[0]
    view = lparm[1]
    context = Context(item)
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    resultado = [ entrada for entrada in view.diccionario[confName].keys() if entrada[0] != '@' ]
    return resultado
          
def defaultSchema(*lparm):
    """
    orden preferencia

    1) esquema de la tabla
    2) esquema de la conexion
    3) esquema defecto del gestor
    """
    item = lparm[0]
    view = lparm[1]
    context = Context(item)
    #context = Context(item)
    
    baseFile = getChildByType(getParentByType(item,'base'),'table')
    n,baseName,t = getRow(baseFile)
    return getSchema(baseName.data())
    
    tableid,tablename,tabletype = view.getHierarchy(item,['table'])  #FIXME debe ser jerarquia relativa
    if tablename:
        fqntable = tablename.split('.')
        if len(fqntable) > 1:                #podria tener la base de datos (lo dudo). Overkill
            esquema = fqntable[-2]
            return esquema

    confName,confData = view.getConnection(context['rowHead'])
    esquema = confData.get('schema',None)
    if esquema:
        return esquema
    
    esquema = DEFAULT_SCHEMA[confData.get('driver')]
    if esquema[0] == '@':
        esquema = confData.get(esquema[1:])
    return esquema
    
def srcTables(*lparm):
    item = lparm[0]
    view = lparm[1]
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    schema = getSchema(item)
    resultado = [ ['{}.{}'.format(schema,entrada),entrada]
                            for entrada in view.diccionario[confName][schema].keys() 
                            if entrada[0] != '@']
    return resultado

def srcNumFields(*lparm):
    kparm = list(lparm)
    kparm.insert(2,'@fmt') #formato
    kparm.insert(3,lambda i:i in ('entero', 'numerico'))
    return srcFields(*kparm)

def srcFields(*lparm,**kparm):
    item = lparm[0]
    view = lparm[1] 
    if len(lparm) > 2:
        idx = lparm[2] 
        delta = lparm[3]
    else:
        idx = '@fmt'
        delta = lambda i:True
    
    context = Context(item)
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    if 'file' in kparm:
        esquema,table = padd(kparm['file'].split('.'),2,pos='before')  # FIXME de momento asumo que es fqntable
    else:
        esquema,table = getFile(item,show='list')
    if not esquema:   
        esquema = getSchema(item,table)

    dict_ref = view.diccionario[confName][esquema][table]['FIELDS']
    resultado = [ ['{}.{}.{}'.format(esquema,table,entrada),entrada]
                            for entrada in dict_ref.keys() 
                            if entrada[0] != '@' and delta(dict_ref[entrada][idx])]

    return resultado
    
  
def defaultTable(*lparm):
    return None

def addConnectionMenu(*lparms):
    item = lparms[0]
    view = lparms[1]
    menuStruct = lparms[2]
    menu = lparms[3]
    text = lparms[4]
    menuStruct.append(menu.addAction(text,lambda i=item:addConnection(i,view)))

def addConnection(*lparms):
    item = lparms[0]
    view = lparms[1]
    pai = item.parent()
    while pai.parent():
        pai = pai.parent()
    nombre = pai.data()
    view.connChanged.emit(nombre,item.data())

def addCategoryMenu(*lparms):
    item = lparms[0]
    view = lparms[1]
    menuStruct = lparms[2]
    menu = lparms[3]
    text = lparms[4]
    
    if item.column() == 0:
        n = item
    else:
        n = item.model().itemFromIndex(item.index().sibling(item.row(),0) )                       
    if n.data() != 'categories':
        return 
    
    for  k in range(item.rowCount()):
        pai = item.child(k,0)
        if pai.hasChildren() and  pai.child(0,0).data() == 'default':
            return
    menuStruct.append(menu.addAction(text,lambda i=item:addDefault(i,view)))
    
def addDefault(*lparms):
    """
    la manera de añadir un valor de defecto es un poco asi, pero es lo que exige la compatibilidad con  lo viejo
    """
    item = lparms[0]
    view = lparms[1]
    text,ok = QInputDialog.getText(None, "Valor de defecto para la categoría: "+item.data(),"Valor", QLineEdit.Normal,'')
    if ok and text:
        intRow = makeRow('default',None,'categories')
        item.appendRow(intRow)
        pai = intRow[0]
        newRow = makeRow('default',text,'default')
        pai.appendRow(newRow)
    
def _getDictTable(dd,confName,schema,table):
    baseName = table.split('.')[-1]
    for k in range(dd.hiddenRoot.rowCount()):
        if dd.hiddenRoot.child(k,0).text() == confName:
            conn = dd.hiddenRoot.child(k,0)
            break
    else:
        raise ValueError('{} {} no en diccionario'.format('Conexión',confName))
    for k in range(conn.rowCount()):
        if conn.child(k,0).text() == schema:
            schem = conn.child(k,0)
            break
    else:
        raise ValueError('{} {} no en diccionario para {}'.format('Esquema',schema,confName))
    for k in range(schem.rowCount()):
        if schem.child(k,0).text() == baseName:
            break
    else:
        raise ValueError('{} {} no en diccionario para {}.{}'.format('Tabla',baseName,confName,schema))

    return schem.child(k)

def addNetworkMenuItem(*lparms):
    """
    aqui incluyo las opciones de menu para las guias. ¿Deberia separarlo?
    """
    item = lparms[0]
    view = lparms[1]
    menuStruct = lparms[2]
    menu = lparms[3]
    text = lparms[4]
    n,i,t=getRow(item)
    print('ANMI',n.data())
    if n.data() == 'guides':
        menuStruct.append(menu.addAction(text,lambda i=item,j=view:addNetworkPath(i,j)))
    else:
        menuStruct.append(menu.addAction('Ver conjunto de prueba',lambda i=lparms:sampleData(*lparms)))
        classItem = getChildByType(item,'class')
        if classItem:
            clase = getRow(classItem)[1].data()
        else:
            clase = 'o'
        if clase == 'd':
            menuStruct.append(menu.addAction('Añadir agrupaciones especiales por fecha',lambda i=lparms:addDateGroups(*lparms)))

class FKNetworkDialog(QDialog):
    def __init__(self,item,view,cubeTable,routeData,parent=None):

        super().__init__(parent)
        self.setMinimumSize(QSize(640,330))
        
        self.manualBB = QPushButton('Ir a manual')
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonBox.addButton(self.manualBB, QDialogButtonBox.ActionRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        buttonBox.clicked.connect(self.procBotones)
        
        self.msgLine = QLabel()
        titleLabel = QLabel('Nombre de la guia')
        destLabel =QLabel('Tabla por la que queremos agrupar')
        destFLabel    =QLabel('Campos por los que queremos agrupar')
        routeLabel  = QLabel('Ruta para acceder a al tabla destino')
        
        self.titleText = QLineEdit()
        self.titleText.setStyleSheet("background-color:yellow;")

        
        self.destTable = QComboBox()
        self.destField = WMultiCombo()
        self.destRoutes = QComboBox()
        
        meatlayout = QGridLayout()
        x = 0
        meatlayout.addWidget(titleLabel,x,0)
        meatlayout.addWidget(self.titleText,x,1)
        x +=1
        meatlayout.addWidget(destLabel,x,0)
        meatlayout.addWidget(self.destTable,x,1)
        x +=1
        meatlayout.addWidget(destFLabel,x,0)
        meatlayout.addWidget(self.destField,x,1)
        x += 1
        meatlayout.addWidget(routeLabel,x,0)
        meatlayout.addWidget(self.destRoutes,x,1,1,2)
        x += 2
        meatlayout.addWidget(self.msgLine,x,0)
        x += 1
        meatlayout.addWidget(buttonBox,x,1)
        
        self.setLayout(meatlayout)
        self.prepareData(item,view,cubeTable,routeData)

        self.manual = False

    def prepareData(self,item,view,cubeTable,routeData):
        self.item = item
        self.routeData = routeData
        self.view = view
        self.cubeTable = cubeTable
        self.all = False
        # load destTable. TODO ¿todas las tablas o solo las que tienen conexion FK?
        if self.all:  #todas las tablas (no esta definido asi que)
            self.TablesFullList = srcTables(item,view)
            x,y = zip(*self.TablesFullList)
            self.tablesCurrentList = list(y)
        else:
            self.tablesCurrentList = list(routeData.keys())
        self.destTable.addItems(self.tablesCurrentList)
        self.destTable.setCurrentIndex(-1)
        self.destTable.currentIndexChanged[int].connect(self.seleccionTabla)
 
    def seleccionTabla(self,idx):
        #FIXME y si no hay rutas .... ¿?
        # preparamos la lista de campos
        self.FieldsFullList = srcFields(self.item,self.view,file=self.tablesCurrentList[idx])
        x,y = zip(*self.FieldsFullList)
        self.fieldsCurrentList = list(y)
        self.destField.clear()
        self.destField.load([ entry[0] for entry in self.FieldsFullList],self.fieldsCurrentList)
        
        # preparamos la lista de rutas
        rutasTabla = list(self.routeData.get(self.tablesCurrentList[idx],{}).keys())
        #FIXME esto tiene que ser un map
        for k in range(len(rutasTabla)):
            entrada = rutasTabla[k][2:]
            rutasTabla[k] = entrada.replace('->','\n\t')
        self.destRoutes.clear()
        self.destRoutes.addItems(rutasTabla)
        self.destRoutes.setCurrentIndex(-1)
        
    def accept(self):
        #TODO validaciones
        name = self.titleText.text()
        schema = self.cubeTable.split('.')[0] # se supone que viene cargado
        if self.all:
            table = self.TablesFullList[self.destTable.currentIndex()][0]
            baseTable = table.split('.')[-1]
        else:
            baseTable = self.tablesCurrentList[self.destTable.currentIndex()]
            table = '{}.{}'.format(schema, baseTable)
        values = norm2List(self.destField.get())
        print(name,table,baseTable,values)
        # ahora el link link_via
        electedPath = self.destRoutes.currentText() #que valiente
        electedPath = '->' + electedPath.replace('\n\t','->')
        electedPathDatos = self.routeData[baseTable][electedPath]
        path = []
        for arc in electedPathDatos:
            arcInfo = arc['ref'].getRow()
            arcDict = {'table':arcInfo[1],'filter':'','clause':[{'base_elem':arcInfo[2],'rel_elem':arcInfo[3]},]}
            path.append(arcDict)
            
        self.result = {'name':name,
                                            'class':'o',
                                            'prod':[{'name':name,
                                                            'elem':values,
                                                            'table':table,
                                                            'link via':path
                                                          }
                                                        ,]
                                }
        super().accept()


        
    def procBotones(self,button):
        if button == self.manualBB:
            self.manual = True
            self().reject()
            
def addNetworkPath(*lparm):
    item = lparm[0]
    view = lparm[1]
    # me fascina como obtener los datos
    baseTableItm = getChildByType(getParentByType(item,'base'),'table')
    baseTable = baseTableItm.parent().child(baseTableItm.row(),1).data()
    
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    schema = getSchema(item,baseTable)
    fqtable = schema + '.' + baseTable.split('.')[-1]  #solo por ir seguro
    
    tableDdItem = _getDictTable(view.dataDict,confName,schema,baseTable)
    
    arbolNavegacion = getFKLinks(tableDdItem)
    if not arbolNavegacion:
        view.msgLine.setText('Tabla {} no tiene claves extranjeras. Debe definirlo a mano'.format(baseTable))
        #TODO aqui una buena powertable haria maravillas
        return        
    selDlg = FKNetworkDialog(item,view,fqtable,arbolNavegacion)
    selDlg.show()
    if selDlg.exec_():
        # no he encontrado otra manera que generara correctamente el arbol que borrando todas las guias
        estructura = tree2dict(item,isDictFromDef)
        estructura.append(selDlg.result)
        item.parent().removeRow(item.row())
        dict2tree(item.parent(),'guides',estructura)
   
def addDateGroups(*lparm):
    """
    TODO   traer de la generacion en danabrowse
    """
    item = lparm[0]
    view = lparm[1]
    n,i,t = getRow(item)
 
def sampleData(*lparm):
    """
    FIXME el codigo no esta aparenciendo en el preview
    """

    
    item = lparm[0]
    view = lparm[1]
    n,i,t = getRow(item)
    pos = item.row()
    cubo  = tree2dict(getParentByType(item,'base'),isDictFromDef)
    form = guidePreview(cubo,pos)
    form.setWindowTitle('Ejemplo de valores para {}'.format(n.data()))
    form.show()
    if form.exec_():
        pass

def discProd(*lparm):
    """
    ('prod_std','prot_cat','prod_case','prod_date')
    """
    
    item = lparm[0]
    view = lparm[1]
    n,i,t = getRow(item)

    elem_hijos = []
    type = None    
    # obtenemos todos los nombres de los hijos (o deberia ser los tipos. En este caso es indiferente, y es mas facil
    for k in range(n.rowCount()):
        elem_hijos.append(n.child(k).data())
    if 'mask' in elem_hijos :
        return 'prod_date'
    elif 'categories' in elem_hijos:
        return 'prod_cat'
    elif 'case_sql' in elem_hijos:
            return 'prod_case'
    elif 'elem' in elem_hijos:
        return 'prod_std'
    else:
        return 'prod'
        
#    return None
                
def discCat(*lparm):
    """
    default, cat item
    """
    item = lparm[0]
    view = lparm[1]
    n,i,t = getRow(item)

    elem_hijos = set()
    type = None    
    # obtenemos todos los nombres de los tipos (o deberia ser los tipos. En este caso es indiferente, y es mas facil
    for k in range(n.rowCount()):
        elem_hijos.add(n.child(k,2).data())
    if 'default' in elem_hijos:
        return 'default'
    else:
        return 'category item'
        

def setClass(*lparm):
    conversor = {'prod_std':'o',
                          'prod_case':'c',
                        'prod_cat':'c',
                        'prod_date':'d'
                        }
    item = lparm[0]
    view = lparm[1]
    if len(lparm) > 2:
        context = lparm[2] 
    else:
        context = Context(item)
    
    tipo = conversor.get(context.get('editType',None),'o')
    
    # defino la clase en el elemento
    claseHead = getChildByType(item,'class')
    if claseHead:
        n,i,t = getRow(claseHead)
        if i.data() != tipo:
            i.setData(tipo,Qt.EditRole)
            i.setData(tipo,Qt.UserRole +1)
    else:
       newRow = makeRow('class',tipo,'class')
       item.appendRow(newRow)
    #ahora viene lo complicado, ir para arriba
    
    guia = getParentByType(item,'guides')
    #¿cuantas prods hay?
    claseGuide = getChildByType(guia,'class')
    prodHead = getChildByType(guia,'prod')
    numReglas = prodHead.rowCount()
    if claseGuide:
        n,i,t = getRow(claseGuide)
        if numReglas > 1:
            tipo = 'h'
        if i.data() != tipo:
            i.setData(tipo,Qt.EditRole)
            i.setData(tipo,Qt.UserRole +1)
    else:
       newRow = makeRow('class',tipo,'class')
       claseGuide.appendRow(newRow)
  
def setTable(*lparm):
    def _cmpTableName(value1,value2):
        resultado = False
        val1 = value1.split('.')
        val2 = value2.split('.')
        if len(val1) == len(val2):   # ambos con los mismos componentes
            if value1 != value2:
                return False
            else:
                return True
        if val1[-1] == val2[-1]:
            return True
        else:
            return False
            
    def _propagateTableName(item,view,oldValue,newValue):
        """
        #absolutamente a lo bruto ... busca cadena con el contenido de la tabla y luego lo convierte
        """
        if oldValue is None:  #FIXME no tengo claro que sea universal
            return
        n,i,t = getRow(item)
        view.expand(item.index())
        if not i or not i.data():
            return
        if not isinstance(i.data(),str):
            return
        oval = i.data()
        schema,ofName = padd(oldValue.split('.'),2,pos='before') #FIXME y si no es un fichero ¿?
        #if ofName not in i.data():
            #continue
        nValue = oval
        if oldValue in oval:  #fqn
            nValue = changeTable(oval,oldValue,newValue)
        elif ofName in oval:
            nValue = changeTable(oval,ofName,newValue)        
        if oval == nValue:
            pass
        else:
            i.setData(nValue,Qt.UserRole +1)
            i.setData(nValue,Qt.DisplayRole)
            i.setData(QColor(Qt.darkYellow),Qt.BackgroundRole)
       
    print('set table',lparm)
    item = lparm[0]
    view = lparm[1]
    if len(lparm) > 2:   
        context = lparm[2] 
    else:
        context = Context(item)
    #WARNING realmente solo funciona bien si se pasa el contexto
    oldValue = context.get('data')
    newValue =  item.parent().child(item.row(),1).data()
    #ahora buscamos el subarbol para el que es válida
    # a continuacion rectifico los datos
    # caso general:
    #      a continuacion
    # caso particular
    #   table en prod rule
    #        si no existe link via -> crear con table en ultimo elemento
    #   table en link via
    #       ver lv[row()-1] ahi tambien se referencia el elemento
    #        si row() == -1 la regla de produccion tambien esta afectada
    pai = item.parent()
    np,ip,tp = getRow(pai)
    if tp and tp.data() in ('base','domain'):
        head = pai
    elif tp and tp.data() == 'link via':
        head = pai.parent()  #el abuelo (que deberia ser link_via a secas), ya que aparece en lv(n) como rel y en lv(n+1) como base
        if pai.row() == head.rowCount() -1: #es el ultimo link
            head = pai.parent() #la propia regla de produccion debe ser, ya que elem pertence a esta tabla. No me gusta ver el caso de prod
    elif tp and tp.data() == 'prod':
        head = pai
        lv = getChildByType(head,'link via')
        if not lv or lv.rowCount() == 0:
            # no existe link via a ella, debemos crearla
            pass
        else:
            last_link = getChildByType(lv.child(lv.rowCount() -1,0),'table') #asi abrevio
            # tres casos last_link = oldValue -> nfa; last_link = newValue -> nfa, otro caso --> ir al de arriba
            rh,ih,th = getRow(last_link)
            if _cmpTableName(oldValue,ih.data()):
                pass # atropella luego la propagacion
            elif _cmpTableName(newValue,ih.data()):
                pass #estamos hablando de la misma tabla, FIXME propagar FQN 
            else:
                pass #aqui si requiero trabajo de marqueteria fina
            
    for item in traverse(head):
        _propagateTableName(item,view,oldValue,newValue)
    view.setCurrentIndex(head.index())
    
    

    
def digClass(*lparm):
    conversor = {'prod_std':'o',
                          'prod_case':'c',
                        'prod_cat':'c',
                        'prod_date':'d'
                        }

    item = lparm[0]
    view = lparm[1]
    rowHead,i,t = getRow(item)
    if t.data() != 'prod':
        return #algo falla
    numero = rowHead.rowCount()
    tipo = None
    if numero == 1:
        lastProd = getChildByType(rowHead,'prod')
        claseProd = getChildByType(lastProd,'class')
        if claseProd:
            tipo = getRow(claseProd)[1].data()  #sintaxis simplifcada ... overkill ???
        else:
            tipo = conversor.get(discProd(lastProd,None),'o')
    elif numero > 1:
            tipo = 'h'
    claseGuide = getChildByType(getParentByType(rowHead,'guides'),'class')
    if tipo:
        rowHead,i,t = getRow(claseGuide)
        if i.data() != tipo:
            i.setData(tipo,Qt.EditRole)
            i.setData(tipo,Qt.UserRole +1)
    if numero == 0:
        item.model().removeRow(claseGuide.row(),claseGuide.parent().index())
        
def valConnect(context,editor,*lparms,**kwparms):
    ok = True
    Text = 'Compruebe que es posible realizar la conexion con la opcion correspondiente en connect'

    item = context.get('editPos')
    ovalue = context.get('data')
    attr = context.get('editType')
    dvalue = lparms[0]
    ivalue = lparms[1]
    if ovalue == ivalue:
        return ok,Text
    conData = getConnection(item,name=False)
    conData[attr]=ivalue
    """
    sqlite el fichero debe existir
    ^sqlite,pgsql usuario debe estar definido
    ^sqlite host debe estar definido
    """
    if conData['driver'] == 'sqlite':
        #verificar la existencia del fichero
        if not os.path.isfile(conData['dbname']):
            return False,'Fichero {} no existe'.format(conData['dbname'])
        
    if  conData['driver'] not in ('sqlite','postgresql')  and _getNorm(conData,'dbuser') == '':
            return False,'{} necesita de usuario'.format(conData['driver'])
            
    if conData['driver'] not in ('sqlite','oracle') and _getNorm(conData,'dbhost') == '':
            return False,'{} necesita especificar un host. Utilice "localhost" para el local'.format(conData['driver'])
    #TODO o no. Verificar que es posible la conexion
    return ok,Text
"""

Nuevo mojo del arbol

no example of validators attribute 
elements list is (element name,mandatory,readonly,repeatable, subtype_selector)
still no process for repeatable 
class & name are not to be edited (even shown) as derived DONE

"""

TOP_LEVEL_ELEMS = ['base','default_base']
EDIT_TREE = {
    'base': {'objtype': 'dict',
                    'elements': [
                        ('base filter',False,False),
                        ('connect',True,False),
                        ('fields',True,False),
                        ('guides',True,False,True),
                        ('table',True,False), 
                        ('date filter',False,False,True),
                    ],
                    'getters':[],                   #antes de editar
                    'setters':[],      #despues de editar (por el momento tras add
                    'validators':[],                 #validacion de entrada
                    'text':'definción de cubo',
                    },
    'connect': { 'objtype':'dict',
                     'elements':[
                         ('driver',True,False),
                         ('dbname',True,False),
                         ('dbhost',False,False),
                         ('dbuser',True,False),
                         ('dbpass',False,False),
                         ('schema',False,False),
                        ],
                     'getters':[],
                     'setters':[],
                    'validators':[],
                    'menuActions':[ [addConnectionMenu,'Comprueba la conexión'],],
                    'text':'parámetros de conexion a la base de datos',
                    },
    'driver': {'editor':QComboBox, 'source':DRIVERS,
               'text':'gestor de base de datos a usar',
               'validators':[valConnect,],
               },
    'dbname':{ 'editor':QLineEdit,
              'text':'Nombre de la instancia de  base de datos',
              'validators':[valConnect,],},
    'dbhost':{'editor':QLineEdit,
              'text':'Servidor donde reside la base de datos',
              'validators':[valConnect,],},
    'dbuser':{'editor':QLineEdit, 'default':'',
              'text':'Usuario de la base de datos por defecto',
              'validators':[valConnect,],},
    'dbpass':{'editor':QLineEdit, 'hidden':True,
              'text':'clave del usuario en la B.D. (desaconsejado)'},   
    'schema':{'editor':QComboBox,'source':srcSchemas,'default':defaultSchema,
              'text':'Esquema de la B.D. a utilizar por defecto',
              },
    'table' : { 'editor':QComboBox, 'source':srcTables,'editable':True,'setters':[setTable,] },
    'base filter': {'editor':QLineEdit},   #aceptaria un validator
    'date filter': {'objtype':'list'},
    'fields' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcNumFields,
                'children': 'field',
                },
    'field' : { 'editor' : QLineEdit},   #experimento a ver si funciona
    'guides':{'objtype':'dict',
                   'elements':[
                       ('name',True,True),
                       ('class',True,True),
                       ('fmt',False,False),
                       ('prod',True,False,True,'class'),                       
                       ],
                    'text':'Guia de agrupación',
                    'menuActions':[[addNetworkMenuItem,'Añada una regla remota'],],
                   },
    'name':{'editor':QLineEdit },
    'class' :{'editor':QComboBox,'source':GUIDE_CLASS,'default':'o'},
    'fmt' :{'editor':QComboBox,'source': ENUM_FORMAT ,'default':'txt' },
    'prod':{'objtype':'dict','subtypes':('prod_std','prod_cat','prod_case','prod_date'),
            'discriminator':discProd,
            'setters':[setClass,],
            'diggers':[digClass,],
            'elements':[
                    ('name',True,True),
                    ('class',False,True),         
                    ('fmt',False,False),
                ],
            'text':'Regla de produccion de guía',
            },
    'prod_std':{'objtype':'dict',
                'elements':[
                    ('elems',True,False),
                    ('domain',False,False),
                    ],
                'text':'Guía ordinaria',
                },
    'prod_cat':{'objtype':'dict',                 # es o categories o case sql tengo que ver como lo asocio
                    'elements':[
                        ('elems',True,False),
                        ('categories',True,False,True),
                        ('fmt_out',False,False),
                    ],
                'text':'Guía por tabla de categorias',
                },
    'prod_case':{'objtype':'dict',                 # es o categories o case sql tengo que ver como lo asocio
                    'elements':[
                        ('elems',True,False),
                        ('case_sql',True,True),
                        ('fmt_out',False,False),
                    ],
                'text':'Guía por sentencia directa',
                },
    'prod_date':{'objtype':'dict',
                    'elements':[
                        ('elems',True,False),
                        ('mask',True,False),
                    ],
                'text':'Guía por fecha',
                },

    'elems':{'objtype':'group', 
            'elements':[
                ('elem',True,False),
                ('table',False,False),
                ('link via',False,False),
                ],
            },
    'domain': { 'objtype':'dict',
               'elements':[
                    ('table',True,False),
                    ('code',True,False),
                    ('desc',False,False),
                    ('filter',False,False),
                    ('grouped by',False,False),
                   ],
               },
    'elem' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    'code' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    'desc' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    'grouped by' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,   #source probably not
                'children': 'field',
                },
    'filter': {'editor':QLineEdit,'default':''},   #aceptaria un validator
    #TODO como hacer que solo haya un default. ¿Necesito otro callback para los menus ?
    #'menuActions':[ [addConnection,'Comprueba la conexión'],],
    #'categories': { 'objtype':'dict','subtypes':['default','category item'],'discriminator':discCat, },
    #'default':{'editor':QLineEdit },
    'categories':{'objtype':'dict',    #FIXME nombre
                     'elements':[
                         ('result',True,False),
                         ('condition',False,False),
                         ('values',True,False),  #FIXME a ver si
                         ],
                         'menuActions':[ [addCategoryMenu,'Add default value'],],
                     },
    'case_sql': { 'editor':QLineEdit }, #FIXME el editor es un area de edicion no un  campo
    'result':{'editor':QLineEdit }, #TODO necesita un setter
    'condition':{'editor':QComboBox,'source':LOGICAL_OPERATOR,'default':'='},
    'values' : { 'objtype':'list'},

    'fmt_out' :{'editor':QComboBox,'source': ENUM_FORMAT ,'default':'txt' },
    'link via' : { 'objtype':'list',
                'children': 'link path',
                },
    'link path': {'obtype':'dict',
                'elements':[
                    ('table',True,False),
                    ('clause',True,False,True), #FIXME presentacion
                    ('filter',False,False),
                    ],
                },
    'clause':{'objtype':'dict',
              'elements':[
                  ('base_elem',True,False),
                  ('condition',False,False),
                  ('rel_elem',True,False)
                  ],
              },
    'base_elem':{'editor':QComboBox,'editable':True,'source':srcFields},  #TODO source
    'rel_elem':{'editor':QComboBox,'editable':True,'source':srcFields},     #TODO source
    #TODO concretar cuando puede usarse date start,date end, date format. Es cuestion de teoria
    'date filter':{'objtype':'dict',
                   'elements': [
                       ('elem',True,False),
                       ('date class',True,False),
                       ('date range',False,False),
                       ('date period',False,False),
                       ('date start',False,True),
                       ('date end',False,True),
                       ('date format',False,True),
                    ],
                   },
    'date class':{'editor':QComboBox,'source':CLASES_INTERVALO},
    'date range':{'editor':QComboBox,'source':TIPOS_INTERVALO},
    'date period':{'editor':QSpinBox,'min':1},
    'date format':{'default':'fecha'},
    'default base': { 'objtype':'dict',
                     'elements':[],
                     'getters':[],
                     'setters':[],
                    'validators':[],
                    },
    
    #'entry':{'editor':QComboBox,'source':funclist},
    #'type': {'editor':WMultiCombo,
                #'source':['item','leaf','colparm','rowparm','colkey','rowkey','kwparm'],
                #'default':'item'
            #},
    #'text':{'editor':QLineEdit},
    #'aux_parm':{'objtype':'dict'},  #TODO mejorable
    #'db': {'editor':QLineEdit},
    #'seqnr': {'editor':QSpinBox},
    #'sep': {'editor':QComboBox,'source':['True','False'],'default':False},
    #'hidden':{'editor':QComboBox,'source':['True','False'],'default':False},
    #'sep': {'editor':QCheckBox,'default':False},
    #'hidden':{'editor':QCheckBox,'default':False},
    #'list' : {'editor':WMultiList,'source':modlist},
    #'api': {'editor':QSpinBox,'default':1,'max':1,'min':1},
    #'class':{'editor':QComboBox,'source':('function','sequence')}
    
}
    
def editAsTree(file=None,rawCube=None):
    if not file and not rawCube:
        raise NameError('Para editAsTree no se especificaron los parametros necesarios')
    
    if not rawCube:
        definiciones = load_cubo(file)
        mis_cubos = definiciones
    else:
        mis_cubos = rawCube

    #cubo = Cubo(mis_cubos['experimento'])
    model = displayTree() #QStandardItemModel()
    model.setItemPrototype(QStandardItem())
    hiddenRoot = model.invisibleRootItem()
    parent = hiddenRoot
    for entrada in mis_cubos:
        if entrada == 'default':
            tipo = 'default_base'
        else:
            tipo = 'base'
        dict2tree(parent,entrada,mis_cubos[entrada],tipo)
    return model

#def Context(item_ref):
    ##obtengo la referencias sea item_ref index o item 
    #if isinstance(item_ref,QModelIndex):
        #item = item_ref.model().itemFromIndex(item_ref)
    #else:
        #item = item_ref
    #model = item.model()  
    #if item == model.invisibleRootItem():
        #print('Cabecera de cartel, nada que hacer de momento')
        #return
    
    ##obtengo la fila entera y cargo los defectos
    #n,d,t = getRow(item.index())
    ## obtengo el padre
    #if n.parent() is None:
        #isTopLevel = True
        #np = dp = tp = None
    #else:
        #np,dp,tp = getRow(n.parent().index())
        #isTopLevel = False
    #editPosition = d
    #if t:
        #editType,edit_data = getRealEditDefinition(item,EDIT_TREE,t.data())
    #else:
        #editType = None
        #edit_data = {}
    
    #if editType:
        #dataType = EDIT_TREE.get(editType,{}).get('objtype','atom')
    #else:
        #dataType = 'atom'
   ## corrigo para listas implicitas
    #if n.hasChildren() and dataType == 'atom':
        #nh,dh,th = getRow(n.child(0,0).index())
        #if nh.data() is None:
            #dataType = 'list'
        #else:
            #dataType = 'dict'

    ## ahora determino los atributos que dependen del padre
    #isMandatory = False
    #isReadOnly = False
    #isRepeteable = False
    #isRepeatInstance = False
    #isListMember = False

    #if tp:
        #tpType,tpEdit_data = getRealEditDefinition(np,EDIT_TREE,tp.data())
        #tipoPadre =  tpEdit_data.get('objtype')
        #if tipoPadre == 'dict':
            #elementosPadre = tpEdit_data.get('elements',[]) #ya esta expandido
            #if t and t.data():
                #try:
                    #idx  = [ dato[0] for dato in elementosPadre ].index(t.data())
                    #isMandatory = elementosPadre[idx][1]
                    #isReadOnly = elementosPadre[idx][2]
                    #if len(elementosPadre[idx]) > 3:
                        #isRepeteable = elementosPadre[idx][3]
                #except ValueError:
                    #pass
            ##de momento desactivado
            ##if edit_data.get('editor') is None:
                ##editPosition = dp
                ##editType,edit_data = getRealEditDefinition(np,EDIT_TREE,tpType)
                ##dataType = 'dict'
                ##if tpEdit_data.get('editor') is None:
                    ##edit_data['editor'] = WNameValue
        #elif tipoPadre == 'list':
            #isListMember = True
            #hijosPadre = tpEdit_data.get('children')
            #edit_ctx_hijo = EDIT_TREE.get(hijosPadre)
            ##cuando es una lista sin tipos hijo, solo dejamos editar en la cabeza
            #if edit_ctx_hijo:
                #if not t:
                    #editType,edit_data = getRealEditDefinition(np,EDIT_TREE,hijosPadre)
            #else:
                #editPosition = dp
                #editType,edit_data = getRealEditDefinition(np,EDIT_TREE,tpType)
                #dataType = 'list'
                
        #else: #es hijo de un atom
            #isListMember = True
            #if not t or t.data() is None:
                #editPosition = dp
                #editType,edit_data = getRealEditDefinition(np,EDIT_TREE,tpType) if tp else [None,{}]
                #dataType = 'list'
           
        #if t and t.data() and t.data() == tpType:  #es un elemento repetible
            #isRepeatInstance = True
    
        
     ##TODO puede ser interesante para name vlaue paisrs
    #hasName = False if not isTopLevel else True
    #if edit_data and  'elements' in edit_data:
        #elementos = [ elements[0] for elements in getFullElementList(EDIT_TREE,edit_data['elements']) ]
        #if editType == 'category item':
            #print(elementos)
        #if 'name' in elementos or 'result' in elementos:
            #hasName = True
   
    #return {
            #'rowHead':n,
            #'name':n.data(),
            #'data':d.data(),
            #'type':t.data() if t else None,
            #'dtype':dataType,
            #'topLevel':isTopLevel,
            #'listMember':isListMember,
            #'editPos': editPosition,
            #'editType':editType,
            #'mandatory':isMandatory,
            #'readonly':isReadOnly,
            #'repeteable':isRepeteable,
            #'repeatInstance':isRepeatInstance,
            #'edit_tree':edit_data,
            #'hasname':hasName,
            #}
    
 
        
"""
Funciones GUI principales 
"""
from support.gui.treeEditor import *
from base.datadict import DataDict
import argparse

class cubeTree(TreeMgr):
    # señal para controlar el cambio de la conexion. Realmente solo la usa en el check. Overkill ¿?
    connChanged = pyqtSignal(str,str)
    
    def __init__(self,treeDef,firstLevelDef,ctxFactory,file,msgLine,**kwparms):
        Context.EDIT_TREE = treeDef
        if 'dataDict' in kwparms:
            self.dataDict = kwparms['dataDict']
        else:
            secure = kwparms.get('secure',True)
            sysEx =   kwparms.get('sysExclude',True)
            self.dataDict  = file2datadict(file,secure,sysEx)
            
        self.diccionario = datadict2dict(self.dataDict.hiddenRoot)
        
        if 'rawCube' in kwparms:
            self.tree = editAsTree(rawCube = kwparms['rawCube'])
        else:
            self.tree = editAsTree(file=file)
        self.cubeFile = file
        super().__init__(self.tree,treeDef,firstLevelDef,ctxFactory,msgLine)
        
        self.connChanged.connect(self.checkConexion)
    """
    slots
    """
    def checkConexion(self,cubeName,itemName):
        """
        slot para procesar el añade conexion. Quizas se ejecute demasiadas veces
        """
        #FIXME como hago que solo se ejecute si cambia
        # el principio podria sustituirse por getConnection()
        namehier = [cubeName,'connect']
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        confData = {}
        for entrada in childItems(item):
            n, i, t = getRow(entrada)
            confData[n.data()] = i.data()
        confName = _toConfName(confData)
        dd = self.dataDict
        if _exists(dd,confName):
            print('conexion <',confName,'> ya existe')
            return
        else:
            print('conexion <',confName,'> no existe. Voy a crearla')
            dd.appendConnection(confName=confName,confData=confData,secure=True)
        #FIXME esto es caro de recursos
            self.diccionario = datadict2dict(self.dataDict.hiddenRoot)
        pass
    """
    data access methods
    
    """
    def _getTopLevel(self,item):
        pai = item
        nombre = None
        while pai:
            n,i,t = getRow(pai)
            nom = n.data()
            tipo = t.data() if t else None
            if t and t.data() == 'base':
                nombre = n.data()
                break
            elif t and t.data() == 'default_base':
                #TODO
                pass
            pai = n.parent()
        return nombre

    def getHierarchy(self,item,hierarchy):
        """
        obtener un elemento del arbol conociendo la jerarquia
        
        """
        namehier = hierarchy[:]
        toplevel = self._getTopLevel(item)
        namehier.insert(0,toplevel)
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        n,i,t = getRow(item)
        return n.data(),i.data(),t.data() if t else None
    
    def getConnection(self,item):
        nombre = self._getTopLevel(item)
        if not nombre:
            return None
        namehier = [nombre,'connect']
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        confData = {}
        for entrada in childItems(item):
            n, i, t = getRow(entrada)
            confData[n.data()] = i.data()
        confName = _toConfName(confData)
        return confName,confData

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False


    def saveCubeFile(self):
        if self.saveDialog():
            print('Voy a salvar el fichero')
            newcubeStruct = tree2dict(self.model().invisibleRootItem(),isDictFromDef)
            if isinstance(self.parentWindow,(cubeMgrWindow,cubeMgrDialog)):
                total=True
            else:
                total = False
            dump_structure(newcubeStruct,self.cubeFile,total=total)
            

    #@waiting_effects
    #@model_change_control()
    def restoreCubeFile(self):
        #self.baseModel.beginResetModel()
        self.baseModel.clear()
        if self.particular:
            self.setupModel(*self.particularContext)
        else:
            self.setupModel()
        self.setupView()
        #self.baseModel.endResetModel()
    
    def test(self):
        return


def generaArgParser():
    parser = argparse.ArgumentParser(description='Cubo de datos')
    parser.add_argument('--cubeFile','--cubefile','-c',
                        nargs='?',
                        default='cubo.json',
                        help='Nombre del fichero de configuración del cubo actual')    
    security_parser = parser.add_mutually_exclusive_group(required=False)
    security_parser.add_argument('--secure','-s',dest='secure', action='store_true',
                                 help='Solicita la clave de las conexiones de B.D.')
    security_parser.add_argument('--no-secure','-ns', dest='secure', action='store_false')
    parser.set_defaults(secure=True)

    schema_parser = parser.add_mutually_exclusive_group(required=False)
    schema_parser.add_argument('--sys','-S',dest='sysExclude', action='store_false',
                                 help='Incluye los esquemas internos del gestor de B.D.')
    parser.set_defaults(sysExclude=True)

    return parser

class cubeMgrWindow(QMainWindow):
    """
    """
    def __init__(self,parent=None):
        super(cubeMgrWindow,self).__init__(parent)

        parser = generaArgParser()
        args = parser.parse_args()
        self.cubeFile = args.cubeFile #'cubo.json'   #DEVELOP
        self.secure = args.secure
        self.sysExclude = args.sysExclude

        Context.EDIT_TREE = EDIT_TREE
        
        self.statusBar = QStatusBar()
        self.msgLine = QLabel()
        self.statusBar.addWidget(self.msgLine)
        self.tree = cubeTree(
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            self.cubeFile,
                                            msgLine = self.msgLine,
                                            secure = self.secure,
                                            sysExclude = self.sysExclude)
        self.setCentralWidget(self.tree)
        self.setStatusBar(self.statusBar)
        
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.tree.saveCubeFile()
        return True
 

class cubeMgrDialog(QDialog):
    """
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.cubeFile = 'testcubo.json'
        self.msgLine = QLabel()
        
        self.tree = cubeTree(
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            self.cubeFile,
                                            msgLine = self.msgLine)

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.tree,0,0)
        meatLayout.addWidget(self.msgLine,1,1)
        self.setLayout(meatLayout)
        
    def closeEvent(self,event):
        self.close()
        
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.tree.saveCubeFile()
        return True
 

class CubeMgr(cubeTree):
    """
    confName,schema,table son puramente por compatibilidad
    self.cubeMgr = CubeMgr(self,confName,
                                                schema,
                                                table,
                                                self.dictionary,rawCube=infox,
                                                cubeFile=self.cubeFile)
    """
    def __init__(self,parent=None,
                 confName=None,
                 schema=None,
                 table=None,
                 pdataDict=None,
                 cubeFile=None,
                 rawCube=None,
                 msgLine = None
                ):
        config.DEBUG =True
        self.cubeFile = cubeFile if cubeFile else 'testcubo.json'
        if not msgLine:
            self.msgLine = QLabel()
        else:
            self.msgLine = msgLine
        
        super().__init__(EDIT_TREE,
                                TOP_LEVEL_ELEMS,
                                Context,
                                self.cubeFile,
                                msgLine = self.msgLine,
                                dataDict = pdataDict,
                                rawCube=rawCube,
                                confName = confName,
                                schema = schema,
                                table = table,
                                )
        
    #def saveDialog(self):
        #if (QMessageBox.question(self,
                #"Salvar",
                #"Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                #QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            #return True
        #else:
            #return False


    #def saveCubeFile(self):
        #if self.saveDialog():
            #print('Voy a salvar el fichero')
            #newcubeStruct = tree2dict(self.model().invisibleRootItem(),isDictFromDef)
            #if isinstance(self.parentWindow,(cubeMgrWindow,cubeMgrDialog)):
                #total=True
            #else:
                #total = False
            #dump_structure(newcubeStruct,self.cubeFile,total=total)
            

    ##@waiting_effects
    ##@model_change_control()
    #def restoreCubeFile(self):
        ##self.baseModel.beginResetModel()
        #self.baseModel.clear()
        #if self.particular:
            #self.setupModel(*self.particularContext)
        #else:
            #self.setupModel()
        #self.setupView()
        ##self.baseModel.endResetModel()
    
    #def test(self):
        #return


import sys
def pruebaGeneral():
    app = QApplication(sys.argv)
    config.DEBUG = True
    form = cubeMgrWindow()
    form.show()
    #if form.exec_():
        #pass
        #sys.exit()
    sys.exit(app.exec_())

    
 
if __name__ == '__main__':
    #readConfig()
    #testSelector()
    #editAsTree()
    #tools = {}
    #pprint(readUM(uf))
    #pprint(tools)
    #print(readUM(uf))
    pruebaGeneral()
    #modelo =editAsTree()
            
            
    
        #print(getItemContext(item))



