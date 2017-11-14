#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''

from pprint import pprint

  
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

#def traverse(root,base=None):
    #if base is not None:
       #yield base
       #queue = base.listChildren() 
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = queue[0].listChildren() 
        #if expansion is None:
            #del queue[0]
        #else:
            #queue = expansion  + queue[1:]             
    

DEBUG = True
TRACE=True
DELIMITER=':'

#from util.record_functions import *
#from util.tree import *

#from datalayer.access_layer import *
#from datalayer.query_constructor import *

#from util.numeros import stats

#from datalayer.datemgr import getDateIndex,getDateEntry
#from pprint import *

#from core import Cubo

#from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from cubemgmt.cubeutil import changeSchema,changeTableName
#from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
#from cubemgmt.cubeCRUD import insertInList
from dictmgmt.tableInfo import FQName2array,TableInfo

#from dialogs import propertySheetDlg

#import cubebrowse as cb

#import time


from wizardmgmt.cubewizard import *
from wizardmgmt.pages.guidePreview import guidePreview

@keep_tree_layout()
def openContextMenu(cubeMgr,position):
    """
    """
    indexes = cubeMgr.view.selectedIndexes()
    if len(indexes) > 0:
        index = indexes[0]
        item = cubeMgr.baseModel.itemFromIndex(index)
    else:
        return
    menu = QMenu()
    setMenuActions(menu,cubeMgr,item)
    action = menu.exec_(cubeMgr.view.viewport().mapToGlobal(position))
    #getContextMenu(item,action,self)

def setMenuActions(menu,context,item):      
    menuActions = []
    if ( item.type() in  TYPE_LIST_DICT  and item.type() == item.text())  :
        menuActions.append(menu.addAction("Add",lambda:execAction(item,context,"add")))
    if item.type() in (TYPE_ARRAY) :
        menuActions.append(menu.addAction("Add",lambda:execAction(item,context,"add")))
    
    if  ( item.type() in NO_EDIT_LIST or
         (item.type() in TYPE_ARRAY  and item.type() == item.text()) or
         (item.text() in ('guides') )
         ):
        pass
    else:
        menuActions.append(menu.addAction("Edit",lambda:execAction(item,context,"edit")))
        
    #TODO hay algunos imborrables
    if item.type() in NO_DELETE_LIST or item.text() in ('connect','fields','guides','prod','clause'):
        pass
    else:
        menuActions.append(menu.addAction("Delete",lambda:execAction(item,context,"delete")))
        
    if item.type() != item.text() and item.type() not in TYPE_EDIT:
        menuActions.append(menu.addAction("Rename",lambda:execAction(item,context,"rename")))
        #menuActions[-1].setEnabled(False)
    if item.type() == 'base':
        menu.addSeparator()
        hijo = item.getChildrenByName('date filter')
        if not hijo:
            menuActions.append(menu.addAction("Add Date Filter",lambda:execAction(item,context,"add date filter")))
    #if item.type() in ('base','guides'):
        menu.addSeparator()
        menuActions.append(menu.addAction("Copy",lambda:execAction(item,context,"copy")))
        menuActions[-1].setEnabled(False)
    if item.type() == 'guides' and item.text() != 'guides' : #TODO
        menu.addSeparator()
        menuActions.append(menu.addAction("Sample",lambda:execAction(item,context,"sample")))
        menuActions.append(menu.addAction("Copy",lambda:execAction(item,context,"copy")))
        menuActions[-1].setEnabled(False)
    if item.type() in (TYPE_LIST | TYPE_LIST_DICT ) and item.type() != item.text() :  #TODO
        menu.addSeparator()
        menuActions.append(menu.addAction("Sube",lambda:execAction(item,context,"add")))
        menuActions[-1].setEnabled(False)
        menuActions.append(menu.addAction("Baja",lambda:execAction(item,context,"add")))
        menuActions[-1].setEnabled(False)
        menu.addSeparator()
            

def execAction(item,context,action):
    if action == 'sample':
        pos = item.getPos()
        pai = item.parent()
        while pai.type() != 'base':
            pai = pai.parent()
        cubo = tree2dict(pai,isDictionaryEntry)
        pprint(cubo)
        form = guidePreview(cubo,pos)
        form.show()
        if form.exec_():
            pass

    else:
        context.model().beginResetModel()
        manage(item,context,action)
        context.model().endResetModel()

def info_cache(cubeMgr,cube_root):
    """
        esto realmente debe ser un metodo de cubeMgr.
        Debe añadirse uno si cambian datos claves del cubo (conexion y/o tabla)
    """
    cube_ref = cube_root.text()
    #
    # A partir de aqui podria guardarse como un cache
    #
    if not cubeMgr.cache.get(cube_ref):
        print('Nuevo en la plaza')
        tabla_ref = cube_root.getChildrenByName('table').getColumnData(1)
        conn_root = cube_root.getChildrenByName('connect')
        conn_dict = {'dbhost':conn_root.getChildrenByName('dbhost').getColumnData(1),
                    'dbname':conn_root.getChildrenByName('dbname').getColumnData(1),
                    'driver':conn_root.getChildrenByName('driver').getColumnData(1)
                    }
        #FIXME correcciones al vuelo
        if conn_dict['dbhost'] == 'None':
            conn_dict['dbhost'] = ''
        if conn_dict['driver'].lower() == 'qsqlite':
            conn_dict['driver'] = 'sqlite'    
        dd=cubeMgr.dataDict
        
        confName,schema,tabla = FQName2array(tabla_ref)
        if confName == '':
            for conexion in dd.configData['Conexiones']:
                entrada = dd.configData['Conexiones'][conexion]
                match = True
                for entry in ('dbhost','dbname','driver'):
                    match = match and (entrada[entry] == conn_dict [entry])
                if match:
                    confName = conexion
                    confData = entrada
                    break
        else:
            confData = dd.configData['Conexiones'][confName]
        
        #TODO algo como esto deberia ser generico
        if schema == '':
            if confData['driver'] == 'sqlite':
                schema = 'main'
            elif confData['driver'] == 'mysql':
                schema = confData['dbname']
            elif confData['driver'] == 'postgresql':
                schema = 'public'
            elif confData['driver'] == 'oracle':
                schema = confData['dbuser']
        
        tabInfo = TableInfo(dd,confName,schema,tabla,2)
        info = tabInfo.lista
        cubeMgr.cache[cube_ref] = {'confName':confName,
                                   'confData':confData,
                                   'schema':schema,
                                   'tabla':tabla,
                                   'tabla_ref':tabla_ref,
                                   'info':info }
    # fin del proceso de cache
    return cubeMgr.cache[cube_ref]

def manage(item,cubeMgr,action):
    '''
       item    -> cubeTree item
       cubeMgr -> cubeMgr actual
    '''

    tipo = item.type()
    texto = item.text()
    valor = item.getColumnData(1)

    cube_root = item
    while cube_root.type() not in ('base','default_base'):
        cube_root = cube_root.parent()
    if cube_root.type() == 'default base':
        return

    cube_ref = cube_root.text()
    cache_data = info_cache(cubeMgr,cube_root)
    #confName =cache_data['confName']
    #confData =cache_data['confData']
    #schema = cache_data['schema']
    #tabla  = cache_data['tabla']
    #tabla_ref = cache_data['tabla_ref']
    #info = cache_data['info']
    if action in ('add','edit','add date filter'):
        if tipo in TYPE_LEAF:
            resultado = leaf_management(item,cubeMgr,action,cube_root,cube_ref,cache_data)
        else:
            resultado = block_management(item,cubeMgr,action,cube_root,cube_ref,cache_data)
    if action in ('change schema'):
        pass
    elif action == 'delete':

        if item.type() == 'base': #no puedo borrarlo pero si vaciarlo, es un probleam de logica. ver cubebrowewin.close()
            indice = item.index()
            while item.hasChildren():
                item.model().item(indice.row()).removeRow(0)
            item.setEnabled(False)
        else:
            item.suicide()

    elif action == 'rename':
        if tipo == texto:
            return
        text = QInputDialog.getText(None, "Renombrar el nodo :"+item.text(),"Nodo", QLineEdit.Normal,item.text())
        print(text[0])
        if text[0] and text[0] != '':
            item.setData(text[0],Qt.EditRole)
            for elemento in ('name','result'): #,'default'):
                nombre = item.getChildrenByName(elemento)
                if nombre:
                    nombre.setColumnData(1,text[0],Qt.EditRole)
                    break
            else:
                item.appendRow((CubeItem('name'),CubeItem(text[0],)))


def leaf_management(obj,cubeMgr,action,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    modo = action_class(obj)
    if action == 'edit':
        value = obj.getColumnData(1)
    else:
        value = None
        
    specs,values = getInputWidget(obj,cubeMgr,cube_root,cube_ref,cache_data)
    
    result = None
    context = []
    context.append(specs[0:4])

    parmDialog = propertySheetDlg('Edite '+obj.text(),context,values)
    if parmDialog.exec_():
        retorno = parmDialog.sheet.values()[0]
        
        if specs[1] == QLineEdit :
            result = retorno
        elif specs[5]: #descriptivo
            comboList = specs[3]
            claveList = specs[4]
            #print(retorno,comboList,claveList)
            # en un combo tengo que tener cuidado que no se hayan añadido/modificado
            # entradas durante la ejecucion (p.e de campo a funcion(campo)
            if retorno >= len(comboList):  #nueva entrada dinamica en el combo
                result = parmDialog.sheet.cellWidget(0,0).currentText() 
            elif parmDialog.sheet.cellWidget(0,0).currentText() != comboList[retorno]:
                result = parmDialog.sheet.cellWidget(0,0).currentText()
            else:
                result = claveList[retorno] 
        else:
           result = parmDialog.sheet.cellWidget(0,0).currentText()  #pues no lo tengo tan claro
   

    if result:   
        if tipo in TABLE_ITEMS:
            oldFile = obj.getColumnData(1,Qt.EditRole)
            changeTableName(obj,oldFile,result)
            pai = obj.parent()
            if pai.type() == 'base':
                del cubeMgr.cache[pai.text()]
                info_cache(cubeMgr,pai)

        if tipo in TYPE_LIST and action == 'add': #TODO ojillo a la accion
            insertInList(obj,tipo,result)
        else:
            if result and result != value:
                obj.setColumnData(1,result,Qt.EditRole) 
        return result
    else:
        return None
    # efectos secundarios
    # 1) referencia en conexion
    # 2) table name
def block_management(obj,cubeMgr,action,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    texto = obj.text() 
    padre = obj.parent()
    wizard = CubeWizard(obj,cubeMgr,action,cube_root,cube_ref,cache_data)
    if wizard.exec_() :
        CubeWizardExec(obj,cubeMgr,wizard,action,cube_root,cube_ref,cache_data)

@model_change_control(1)
def CubeWizardExec(obj,cubeMgr,wizard,action,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    texto = obj.text() 
    padre = obj.parent()
    if tipo == 'connect':
        """"
        TODO por el momento no se realiza la verificación de mas abajo
           si solo cambio el esquema ---> reprocesar
           si se cambio algo
           si la conexion existe

           si no existe
                si puede conectarse
                    añadir a conexiones posibles
                elif preguntar si deseo proceder
           realizar los cambios necesarios (esquema. fechas manipuladas ¿?)
        """
        schema = wizard.diccionario['schema']
        del wizard.diccionario['schema']
        if schema != cache_data['schema']:
            pai = obj.parent()
            changeSchema(pai,cache_data['schema'],schema)
            if pai.type() == 'base':
                del cubeMgr.cache[pai.text()]
                info_cache(cubeMgr,pai)

            if pai.type() == 'base':
                del cubeMgr.cache[pai.text()]
                info_cache(cubeMgr,pai)
        added, removed, modified, same = dict_compare(wizard.diccionario,tree2dict(obj,isDictionaryEntry))
        if len(modified) == 0 :
            return
        else:
            nudict = {texto:wizard.diccionario }
            obj.suicide()


    elif action == 'add date filter':
        padre = obj
        texto = tipo = 'date filter'     
        if texto in wizard.diccionario:
            nudict = {texto:wizard.diccionario[texto]}
        else:
            nudict = {texto:wizard.diccionario }
        if len(nudict[texto]) == 0:
            print('tengo que escapar')
            return
    #TODO aqui tengo que realizar la vuelta de una regla de produccion
    elif tipo in TYPE_LIST_DICT:
        if tipo != texto:
            yayo = padre.parent()
            nudict = tree2dict(yayo,isDictionaryEntry)
            lista = nudict[tipo]
            if obj.getPos() is not None:
                print('pille entrada')
                lista[obj.getPos()] = wizard.diccionario
            else: #hay que retocar cosas aqui para append e insert before
                print('no pille entrada')
                lista.append(wizard.diccionario)
            padre.suicide()
            padre= yayo
            texto = tipo

        elif action == 'add' :
            nudict = tree2dict(padre,isDictionaryEntry)
            lista = nudict[tipo]
            lista.append(wizard.diccionario)
            obj.suicide()
            #padre= yayo
            #texto = tipo
        else:
            nudict = {texto:wizard.diccionario }
            obj.suicide()
    else:
        nudict = {texto:wizard.diccionario }
        obj.suicide()
    dict2tree(padre,tipo,nudict[texto])
