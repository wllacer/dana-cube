#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
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

from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel,pyqtSignal
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView, QStyledItemDelegate, QSpinBox, QListWidget, QPushButton, QVBoxLayout,QLabel, QWidget, QCheckBox,QStatusBar

from support.util.treeEditorUtil import *

from support.datalayer.access_layer import DRIVERS, AGR_LIST 
from support.util.fechas import CLASES_INTERVALO, TIPOS_INTERVALO
from admin.cubemgmt.cubeTypes import GUIDE_CLASS, ENUM_FORMAT,LOGICAL_OPERATOR
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


def file2datadict(fileName):
    """
    de cubo a DataDictionary
    
    """
    from support.util.jsonmgr import load_cubo
    mis_cubos = load_cubo('testcubo.json')
    dd = None
    for cubo in mis_cubos:
        if cubo == 'default':
            continue
        confData = mis_cubos[cubo]['connect']
        #el driver tambien forma parte de la identificacion
        confName = _toConfName(confData)
        if not dd:
            dd = DataDict(conName = confName,confData=confData,secure=True)
        elif _exists(dd,confName):
            print('conexion <',confName,'> ya existe')
            continue
        else:
            dd.appendConnection(confName=confName,confData=confData,secure=True)
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
        type_context =  contexto.get('edit_tree',{}).get('objtype')
        if type_context == 'dict':
            return True
        elif type_context is not None:
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
    from support.datalayer.access_layer import DEFAULT_SCHEMA
    
    fileItem = getChildByType(getParentByType(item,'base'),'table')
    fileItem = fileItem.parent().child(fileItem.row(),1).data()  
    schema,fName = padd(file.split('.'),2,pos='before')
    if schema:
        return schema
    
    confName,confData = getConnection(item,name=True)
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
    from research.cubeTree import _toConfName
    conItem = getChildByType(getParentByType(item,'base'),'connect')
    n,i,t = getRow(conItem)
    datos = {}
    print('nombre',n.data())
    for k in range(n.rowCount()):
        nh = n.child(k,0)
        ih  = n.child(k,1)
        datos[nh.data()] = ih.data()
    if kwparm.get('name',False):
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
    confName,confData = getConnection(item,name=True)
    resultado = [ entrada for entrada in view.diccionario[confName].keys() if entrada[0] != '@' ]
    return resultado
          
def defaultSchema(*lparm):
    """
    orden preferencia

    1) esquema de la tabla
    2) esquema de la conexion
    3) esquema defecto del gestor
    """
    from support.datalayer.access_layer import DEFAULT_SCHEMA
    item = lparm[0]
    view = lparm[1]
    context = Context(item)
    context = Context(item)
    
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
    confName,confData = getConnection(item,name=True)
    schema = getSchema(item)
    resultado = [ ['{}.{}'.format(schema,entrada),entrada]
                            for entrada in view.diccionario[confName][schema].keys() 
                            if entrada[0] != '@']
    pprint(resultado)
    return resultado

def srcNumFields(*lparm):
    kparm = list(lparm)
    kparm.insert(2,'@fmt') #formato
    kparm.insert(3,lambda i:i in ('entero', 'numerico'))
    return srcFields(*kparm)

def srcFields(*lparm):
    item = lparm[0]
    view = lparm[1] 
    if len(lparm) > 2:
        idx = lparm[2] 
        delta = lparm[3]
    else:
        idx = '@fmt'
        delta = lambda i:True
        
    context = Context(item)
    confName,confData = getConnection(item,name=True)
    esquema,table = getFile(item,show='list')
    if not esquema:   
        esquema = getSchema(item,table)

    dict_ref = view.diccionario[confName][esquema][table]['FIELDS']
    resultado = [ ['{}.{}.{}'.format(esquema,table,entrada),entrada]
                            for entrada in dict_ref.keys() 
                            if entrada[0] != '@' and delta(dict_ref[entrada][idx])]

    return resultado
    
  
def defaultTable(*lparm):
    return 'esta es de prueba'

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
    else:
        return 'prod_std'
        
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
                    'validator':[],                 #validacion de entrada
                    },
    'connect': { 'objtype':'dict',
                     'elements':[
                         ('driver',True,False),
                         ('dbname',True,False),
                         ('dbhost',True,False),
                         ('dbuser',True,False),
                         ('dbpass',False,False),
                         ('schema',False,False),
                        ],
                     'getters':[],
                     'setters':[],
                    'validator':[],
                    'menuActions':[ [addConnectionMenu,'Comprueba la conexión'],],
                    },
    'driver': {'editor':QComboBox, 'source':DRIVERS},
    'dbname':{ 'editor':QLineEdit},
    'dbhost':{'editor':QLineEdit},
    'dbuser':{'editor':QLineEdit, 'default':''},
    'dbpass':{'editor':QLineEdit, 'hidden':True},   # manipulando displayRole en presentacion
    'schema':{'editor':QComboBox,'source':srcSchemas,'default':defaultSchema},
    'table' : { 'editor':QComboBox, 'source':srcTables, 'default':defaultTable,'editable':True },
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
                       ]
                   },
    'name':{'editor':QLineEdit },
    'class' :{'editor':QComboBox,'source':GUIDE_CLASS,'default':'o'},
    'fmt' :{'editor':QComboBox,'source': ENUM_FORMAT ,'default':'txt' },
    'prod':{'objtype':'dict','subtypes':('prod_std','prod_cat','prod_case','prod_date'),'discriminator':discProd,
            'setters':[setClass,],'diggers':[digClass,],
            'elements':[
                    ('name',True,True),
                    ('class',False,True),         
                    ('fmt',False,False),
                ],
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
                    'validator':[],
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
    
def editAsTree(fichero):
    from base.core import Cubo
    from support.util.jsonmgr import load_cubo
    definiciones = load_cubo(fichero)
    mis_cubos = definiciones

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

class cubeTree(TreeMgr):
    # señal para controlar el cambio de la conexion. Realmente solo la usa en el check. Overkill ¿?
    connChanged = pyqtSignal(str,str)
    
    def __init__(self,treeDef,firstLevelDef,ctxFactory,file,msgLine,parent=None):
        Context.EDIT_TREE = treeDef
        self.dataDict  = file2datadict(file)
        self.diccionario = datadict2dict(self.dataDict.hiddenRoot)
        self.tree = editAsTree(file)
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
            
class cubeMgrWindow(QMainWindow):
    """
    """
    def __init__(self,parent=None):
        super(cubeMgrWindow,self).__init__(parent)
        self.cubeFile = 'testcubo.json'
        Context.EDIT_TREE = EDIT_TREE
        
        self.statusBar = QStatusBar()
        self.msgLine = QLabel()
        self.statusBar.addWidget(self.msgLine)
        self.tree = cubeTree(
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            self.cubeFile,
                                            msgLine = self.msgLine)
        self.setCentralWidget(self.tree)
        self.setStatusBar(self.statusBar)
        
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        #self.saveFile()
        return True
 
    def saveFile(self):
        if self.saveDialog():
            definiciones = load_cubo(self.cubeFile)
            definiciones['user functions'] = tree2dict(self.tree.model().invisibleRootItem(),isDictFromDef)
            dump_config(definiciones, self.cubeFile,total=True,secure=False)

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False

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
        
    def close(self):

        self.saveFile()
        return True
 
    def saveFile(self):
        if self.saveDialog():
            definiciones = load_cubo(self.cubeFile)
            definiciones['user functions'] = tree2dict(self.tree.model().invisibleRootItem(),isDictFromDef)
            dump_json(definiciones,self.cubeFile)

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False
 


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



