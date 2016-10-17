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

from datadict import *    
from datalayer.query_constructor import *
from datalayer.access_layer import dbDict2Url
from tablebrowse import *
from datemgr import genTrimestreCode
from util.jsonmgr import *
from util.fivenumbers import is_number
from dialogs import propertySheetDlg

from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *

(_ROOT, _DEPTH, _BREADTH) = range(3)



"""
   cubo --> lista de cubos
   col,row
"""
def constructFKsheet(elemento, path_array,routier):    
    path_array_local = path_array[:]
    path_array_local.append(elemento)
    routier.append(path_array_local)
    for fkr in elemento.get('FK',list()):
        constructFKsheet(fkr,path_array_local,routier)

def getDescList(fk):
    desc_fld = []
    for fld in fk['CamposReferencia']:
        if fld[1] == 'texto':
            desc_fld.append(fld[0])
    if len(desc_fld) == 0:
        print('No proceso correctamente por falta de texto',fk)
        desc_fld = fk['ParentField']
    return desc_fld



    
def getCubeList(rootElem):
    entradas_especiales = ('default',)
    lista = [ item.text() for item in childItems(rootElem) if item.text() not in entradas_especiales ]
    return lista

def getCubeInfo(rootElem):
    if rootElem.type() == 'base': 
        guidemaster = childByName(rootElem,'guides')
        fieldmaster = childByName(rootElem,'fields')
        guias =  getItemList(guidemaster,'guides') 
        campos = getDataList(fieldmaster,1)  #los campos no tienen nombre
        print (campos,fieldmaster)
        return guias,campos
    else:
        return [],[]

def FQName2array(fqname):
    dbmanager = '' #no deberia existir pero por si acaso
    schema = ' '
    filename = ''
    splitdata = fqname.split('.')
    if len(splitdata) == 3:
        dbmanager,schema,filename = splitdata
    elif len(splitdata) == 2:
        schema,filename = splitdata
    elif len(splitdata) == 1:
       filename = fqname
    return dbmanager,schema,filename

        
def isDictionaryEntry(rootElem):
    result = False
    if rootElem.type() in TYPE_DICT or ( rootElem.type() in TYPE_LIST_DICT and rootElem.text() != rootElem.type() ):
        result = True
    return result
    
 
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
        print(connItem)
        pprint(tree2dict(connItem,isDictionaryEntry))
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
        dialect = agay[0]
        if len(agay) == 2:
            driver = agay[1]
        else:
            driver = None
    else:
        dialect = None
        driver  = None
            

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
    return dialect,driver,login,host,dbref

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



