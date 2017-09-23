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
#from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
#from cubemgmt.cubeCRUD import insertInList
grepfrom dictmgmt.tableInfo import FQName2array,TableInfo

#from dialogs import propertySheetDlg

#import cubebrowse as cb

#import time


from wizardmgmt.cubewizard import *

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
    menuActions.append(menu.addAction("Add",lambda:execAction(item,context,"add")))
    menuActions.append(menu.addAction("Edit",lambda:execAction(item,context,"edit")))
    #TODO hay algunos imborrables
    menuActions.append(menu.addAction("Delete",lambda:execAction(item,context,"delete")))
    if item.type() != item.text():
        menuActions.append(menu.addAction("Rename",lambda:execAction(item,context,"rename")))
        #menuActions[-1].setEnabled(False)
    if item.type() == 'base':
        menu.addSeparator()
        hijo = item.getChildrenByName('date filter')
        if not hijo:
            menuActions.append(menu.addAction("Add Date Filter",lambda:execAction(item,context,"add date filter")))
            
@model_change_control(1)
def execAction(item,context,action):
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
            nombre = item.getChildrenByName('name')
            if nombre:
                item.setColumnData(1,text[0],Qt.EditRole)
            else:
                item.appendRow((CubeItem('name'),CubeItem(text[0],)))



def block_management(obj,cubeMgr,action,cube_root,cube_ref,cache_data):
    print(action,obj.type(),obj.text())
    tipo = obj.type()
    texto = obj.text() 
    padre = obj.parent()
    #if tipo == 'base':
        #children = ('base_filter','date_filter','fields','guides')
    #elif tipo == 'default_base':
        #children = ('cubo','vista')
    #elif tipo == 'connect':
        #children = ('driver','dbname','dbhost','dbuser','dbpass','port','debug')
    #elif tipo == 'domain':
        #children == ('table','code','desc','filter','grouped_by')
    #elif tipo == 'vista':
        #children = ('agregado','elemento','row','col')
    #elif tipo == 'categories':
        #children = ('elem','default','condition','values','result','enum_fmt')
    #elif tipo == 'clause':
        #children = ('base_elem','rel_elem'),
    #elif tipo == 'guides':
        #children = ('class','name','prod'),
    #elif tipo == 'prod':
        #children = ('elem','class','domain','link_via','case_sql','type','fmt','categorias')
    #elif tipo == 'link via':
        #children = ('table','clause','filter'),
    #elif tipo == 'date filter':
        #children = ('elem','date class','date period','date range','date start','date end')


    wizard = CubeWizard(obj,cubeMgr,action,cube_root,cube_ref,cache_data)
    if wizard.exec_() :
        #print('Milagro',wizard.page(1).contador,wizard.page(2).contador,wizard.page(3).contador)
        if action == 'add date filter':
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
        elif tipo == 'prod':
            nudict = {texto:wizard.diccionario }
        else:
            nudict = {texto:wizard.diccionario }
            obj.suicide()
            
        dict2tree(padre,tipo,nudict[texto])
