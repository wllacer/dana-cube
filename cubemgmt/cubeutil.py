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

from dictmgmt.datadict import *    
from datalayer.query_constructor import *
from datalayer.access_layer import dbDict2Url,internal2genericDriver
from tablebrowse import *
from datalayer.datemgr import genTrimestreCode
from util.jsonmgr import *
from util.numeros import is_number
from dialogs import propertySheetDlg

from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *

(_ROOT, _DEPTH, _BREADTH) = range(3)



"""
   cubo --> lista de cubos
   col,row
"""
def info2cube(dataDict,confName,schema,table,maxlevel=1):
    """
       de la informacion de la tabla en DANACUBE crea un cubo por defecto

    """
    info = getTable(dataDict,confName,schema,table,maxlevel)                
    #pprint(info)
    
    #cubo = load_cubo()
    cubo = dict()
    cubo[table]=dict() # si hubiera algo ... requiescat in pace
    entrada = cubo[table]
    #entrada = dict()
    entrada['base filter']=""
    entrada['table'] = '{}.{}'.format(schema,table) if schema != "" else table
    
    entrada['connect']=dict()
    conn = dataDict.getConnByName(confName).data().engine
    
    print('Conexion ',conn.url,conn.driver,internal2genericDriver(conn.driver))  #TODO borrar
    entrada['connect']["dbuser"] = None 
    entrada['connect']["dbhost"] =  None
    entrada['connect']["driver"] =  internal2genericDriver(conn.driver)
    entrada['connect']["dbname"] =  str(conn.url) #"/home/werner/projects/dana-cube.git/ejemplo_dana.db"
    entrada['connect']["dbpass"] =  None
    
    entrada['guides']=[]
    entrada['fields']=[]
    for fld in info['Fields']:
        if fld[1] in ('numerico','entero'):
            entrada['fields'].append(fld[0])
        elif fld[1] in ('fecha'):
            entrada['guides'].append({'name':fld[0],
                                      'class':'d',
                                      'type':'Ymd',
                                      'prod':[{'fmt':'date','elem':fld[0]},]
                                      })  #no es completo
            entrada['guides'].append( genTrimestreCode(fld[0],conn.driver))

        else:
            entrada['guides'].append({'name':fld[0],
                                      'class':'o',
                                      'prod':[{'elem':fld[0],},]})  #no es completo
    if maxlevel == 0:
        pass
    elif maxlevel == 1:
        for fk in info.get('FK',list()):
            desc_fld = getDescList(fk)
                
            entrada['guides'].append({'name':fk['Name'],
                                        'class':'o',
                                        'prod':[{'domain': {
                                                "filter":"",
                                                "table":fk['ParentTable'],
                                                "code":fk['ParentField'],
                                                "desc":desc_fld
                                            },
                                            'elem':fk['Field']},]
                                            })  #no es completo
    else:
        routier = []
        #path = ''
        path_array = []
        for fk in info.get('FK',list()):
            constructFKsheet(fk,path_array,routier)
        
        for elem in routier:
            nombres = [ item['Name'] for item in elem]
            nombres.reverse()
            nombre = '@'.join(nombres)
            activo = elem[-1]
            base   = elem[0]
            rule =   {'domain': {
                                    "filter":"",
                                    "table":activo['ParentTable'],
                                    "code":activo['ParentField'],
                                    "desc":getDescList(activo)
                                },
                         'elem':activo['Field']}   #?no lo tengo claro
            if len(elem) > 1:
                rule['link via']=list()
                for idx in range(len(elem)-1):
                    actor = elem[idx]
                    join_clause = { "table":actor['ParentTable'],
                                    "clause":[{"rel_elem":actor["ParentField"],"base_elem":actor['Field']},],
                                    "filter":"" }
                    rule['link via'].append(join_clause)
                
            entrada['guides'].append({'name':nombre,
                                        'class':'o',
                                        'prod':[rule ,]
                                            })  #no es completo
    return cubo

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
        print('No proceso correctamente por falta de texto',fk['Name'],fk['ParentTable'])
        desc_fld = fk['ParentField']
    return desc_fld



    
def getCubeList(rootElem,restricted=True):
    entradas_especiales = ('default',)
    if restricted:
        lista = [ item.text() for item in childItems(rootElem) if item.text() not in entradas_especiales ]
    else:
        lista = [ item.text() for item in childItems(rootElem) ]
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


