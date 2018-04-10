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

from decimal import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox

from base.datadict import *    
from admin.dictmgmt.tableInfo import *

from support.datalayer.query_constructor import *
from support.datalayer.access_layer import dbDict2Url,internal2genericDriver
from admin.tablebrowse import *
from support.datalayer.datemgr import genTrimestreCode
from support.util.jsonmgr import *
from support.util.numeros import is_number
from support.gui.dialogs import propertySheetDlg

from base.cubetree import *
from admin.cubemgmt.cubeTypes import *

(_ROOT, _DEPTH, _BREADTH) = range(3)



"""
   cubo --> lista de cubos
   col,row
"""
def info2cube(dataDict,confName,schema,table,maxlevel=1):
    """
       de la informacion de la tabla en DANACUBE crea un cubo por defecto

    """
    tableInfo = TableInfo(dataDict,confName=confName,schemaName=schema,tableName=table,maxlevel=maxlevel)
    
    return tableInfo.info2cube()
    

def action_class(obj):
    tipo = obj.type()
    if tipo in FREE_FORM_ITEMS:
        return 'input'
    if tipo in STATIC_COMBO_ITEMS:
        return 'static combo'
    if tipo in DYNAMIC_COMBO_ITEMS:
        return 'dynamic combo'
    if tipo in TYPE_LEAF:  #temporal
        return 'input'
    return None

def isDictionaryEntry(rootElem):
    #result = False
    #if rootElem.type() in TYPE_DICT or ( rootElem.type() in TYPE_LIST_DICT and rootElem.text() != rootElem.type() ):
        #result = True
    #return result
    result = True
    #if not rootElem.hasChildren(): #?seguro
        #return False
    if rootElem.type() in TYPE_LIST or ( rootElem.type() in TYPE_LIST_DICT and rootElem.text() == rootElem.type() ):
        result = False
    return result
    

"""
   cubo --> lista de cubos
   col,row
"""
#def constructFKsheet(elemento, path_array,routier):    
    #path_array_local = path_array[:]
    #path_array_local.append(elemento)
    #routier.append(path_array_local)
    #for fkr in elemento.get('FK',list()):
        #constructFKsheet(fkr,path_array_local,routier)

#def getDescList(fk):
    #desc_fld = []
    #for fld in fk['CamposReferencia']:
        #if fld[1] == 'texto':
            #desc_fld.append(fld[0])
    #if len(desc_fld) == 0:
        #print('No proceso correctamente por falta de texto',fk['Name'],fk['ParentTable'])
        #desc_fld = fk['ParentField']
    #return desc_fld



    
def getCubeList(rootElem,restricted=True):
    entradas_especiales = ('default',)
    if restricted:
        lista = [ item.text() for item in childItems(rootElem) if item.text() not in entradas_especiales ]
    else:
        lista = [ item.text() for item in childItems(rootElem) ]
    return lista

def getCubeItemList(rootElem,restricted=True):
    """
    """
    entradas_especiales = ('default',)
    if restricted:
        lista = [ item for item in childItems(rootElem) if item.text() not in entradas_especiales ]
    else:
        lista = [ item for item in childItems(rootElem) ]
    return lista

def getCubeInfo(rootElem):
    if rootElem.type() == 'base': 
        guidemaster = childByName(rootElem,'guides')
        fieldmaster = childByName(rootElem,'fields')
        guias =  getItemList(guidemaster,'guides') 
        campos = getDataList(fieldmaster,1)  #los campos no tienen nombre
        #print (campos,fieldmaster)
        return guias,campos
    else:
        return [],[]


        
 
def getCubeTarget(obj):
    if obj.type() == 'base':
        pai = obj
    else:
        pai = obj.parent()
        while pai and pai.type() != 'base' :
            pai = pai.parent()
    if pai: #o sea hay padre
        tablaItem = childByName(pai,'table')
        FQtablaArray = FQName2array(tablaItem.getColumnData(1))
        connItem = childByName(pai,'connect')
        #print(connItem)
        #pprint(tree2dict(connItem,isDictionaryEntry))
        conn_data = tree2dict(connItem,isDictionaryEntry)
    return FQtablaArray,dbDict2Url(conn_data)

def dbUrlSplit(url):
    agay= url.split('://')
    if len(agay) == 2:
        fullinterface = agay[0]
        resto  = agay[1]
    elif len(agay) == 1:
        fullinterface = None
        resto = agay[0]

    if fullinterface is not None:
        agay = fullinterface.split('+')
        driver = agay[0]
        if len(agay) == 2:
            sqlaDriver = agay[1]
        else:
            sqlaDriver = None
    else:
        driver = None
        sqlaDriver  = None
            

    agay = resto.split('@')
    if len(agay) == 2:
        login = agay[0]
        reference  = agay[1]
    elif len(agay) == 1:
        login = None
        reference = agay[0]
    
    if not reference:
        host= None
        dbref = None
    elif reference[0] == '/':
        host = None
        dbref = reference
    else:
        agay = reference.split('/',1)
        if len(agay) >2:
            host = agay[0]
            dbref = '/'.join(agay[1:])
        elif len(agay) == 2:
            host = agay[0]
            dbref = agay[1]
        else:
            host= None
            dbref = reference
    #print('{:20}{:20} {:20} {:20} {}'.format(dialect,driver,login,host,dbref)
    return driver,sqlaDriver,login,host,dbref

def getOpenConnections(dataDict):
    conns = childItems(dataDict.hiddenRoot)
    for conn in conns:
        if conn.getConnection().data():
            print(conn.getConnection().data().engine.url)
        else:
            print(conn,'Inactiva')
    return

def connMatch(dataDict,pUrl):
    conns = childItems(dataDict.hiddenRoot)
    available = False
    for conn in conns:
        if str(conn.getConnection().data().engine.url) == pUrl:  #¿? el str
            available = True
            break
    if available:
        return conn  #ConnectionTreeObject
    else:
        return None
    

def getListAvailableTables(obj,exec_object):
    FQtablaArray,connURL = getCubeTarget(obj)
    actConn = connMatch(exec_object.dataDict,connURL)
    array = []
    if actConn:
        for sch in childItems(actConn):
            schema = sch.text()
            for tab in childItems(sch):
                array.append(tab.fqn())

    else:
        print(connURL,'NO ESTA A MANO')
    return array

def getFldTable(exec_object,obj,refTable=None):
    #TODO determinar que es lo que necesito hacer cuando no esta disponible
    #TODO  Unificar con la de abajo
    #TODO base elem probablemente trasciende esta definicion
    #TODO calcular dos veces FQ ... es un exceso. simplificar
    FQtablaArray,connURL = getCubeTarget(obj)
    if refTable:
        if isinstance(refTable,CubeItem):
            FQtablaArray = FQName2array(refTable.getColumnData(1))
        else:
            FQtablaArray = FQName2array(refTable)
    #print(FQtablaArray,connURL)
    actConn = connMatch(exec_object.dataDict,connURL)
    if actConn:
        tableItem = actConn.findElement(FQtablaArray[1],FQtablaArray[2])
        if tableItem:
            fieldIdx = childByName(tableItem,'FIELDS')
            #array = getDataList(fieldIdx,0)
            array = [ (item.fqn(),item.text(),item.getColumnData(1))  for item in fieldIdx.listChildren() ]
            return array
        else:
            print(connURL,'ESTA DISPONIBLE y el fichero NOOOOOR')
            return None
    else:
        print(connURL,'NO ESTA A MANO')
    return None

def traverseFiltered(root,funcion):
    if isinstance(root,CubeItem):
        if funcion(root):
            yield root
        queue = root.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        if funcion(queue[0]):
            yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]    

def changeTableName(root,oldName,newName):
    matchpattern=r'(\W*\w*\.)?('+oldName+')'
    filematch = matchpattern+'\W'
    filerepl  = r'\1'+ newName
    fieldmatch=matchpattern+r'(\..*)'
    fieldrepl = r'\1' + newName +r'\3'
    changeDD(root,filematch,filerepl,fieldmatch,fieldrepl)
        
def changeSchema(root,oldSchema,newSchema):
    matchpattern=r'('+oldSchema+'\.)'
    filematch = matchpattern+'(\w.*)'
    filerepl  = newSchema +r'.\2'
    fieldmatch= filematch
    fieldrepl = filerepl
    changeDD(root,filematch,filerepl,fieldmatch,fieldrepl)

def changeDD(root,filematch,filerepl,fieldmatch,fieldrepl):
    import re
    
    for node in traverseFiltered(root,lambda x:x.type()=='table'):
        pai = node.parent()
        fichero = node.getColumnData(1,Qt.EditRole)
        if re.search(filematch,fichero): #.find(oldFile) >= 0:
            for dnode in traverseFiltered(pai,lambda x:x.type() in COLUMN_ITEMS):
                if dnode.getColumnData(1) is None:
                    continue
                campo = dnode.getColumnData(1,Qt.EditRole)
                if re.search(fieldmatch,campo):# 
                    dnode.setColumnData(1,re.sub(fieldmatch,fieldrepl,campo),Qt.EditRole)
            node.setColumnData(1,re.sub(filematch,filerepl,fichero),Qt.EditRole)
