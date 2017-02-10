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
from core import Cubo,Vista
#from datalayer.query_constructor import *
#from operator import attrgetter,methodcaller

from pprint import pprint

from  PyQt5.QtWidgets import QApplication


#import exportWizard as eW
#from util.numeros import fmtNumber
#from util.jsonmgr import dump_structure
from util.mplwidget import SimpleChart
  
#import math
#import matplotlib.pyplot as plt
#import numpy as np


from PyQt5 import QtCore
#from PyQt5.QtGui import QSizePolicy
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGridLayout, QSizePolicy, QWidget, QTreeView, QHBoxLayout

from dictmgmt.datadict import DataDict
from cubemgmt.cubeutil import FQName2array

from datalayer.query_constructor import *

DEBUG = True

(_ROOT, _DEPTH, _BREADTH) = range(3)


def getTabRef(dd,confName,schemaName,tableName):
    con = dd.getConnByName(confName)
    if con is None:
        if DEBUG:
            print('Conexion {} no definida'.format(confName))
        return None
    sch = con.getChildrenByName(schemaName)
    if sch is None:
        if DEBUG:
            print('Esquema {} no definido'.format(schemaName))
        return None
    tab = sch.getChildrenByName(tableName)
    if tab is None:
        if DEBUG:
            print('Tabla {} no definida'.format(tableName))
        return None
    if DEBUG:
        print('get Table ->',tab.getFullDesc())
                  
    return tab

class TableInfo():
    def __init__(self,dd,confName,schemaName,tableName,maxlevel=0):
        """
        Devuelve dict
        fqn: dict of 
        Fields (de get Fields)
        schemaName
        tableName
        FK: array of dict
                Name of FK
                parent table
                parent field
                field of linkage
                
        """
        
        if not dd or not isinstance(dd,DataDict):
            print('Necesito un diccionario abierto previamente')
            return None
        
        self.driver = dd.getConnByName(confName).data()
                
        tab = getTabRef(dd,confName,schemaName,tableName)
        self.lista = dict()
        self.mainTable = tab.fqn()
        self.maxlevel = maxlevel
        self.lista[tab.fqn()] = tab.getTableInfo()
        
        currentlevel = set()
        nextlevel = set()
        nextlevel.add(tab.fqn())
        for j in range(maxlevel):
            currentlevel = set(nextlevel)
            nextlevel.clear()
            if len(currentlevel) == 0:
                break
            while len(currentlevel) > 0:
                entrada = currentlevel.pop()
                if not self.lista[entrada].get('FK') or  len(self.lista[entrada]['FK']) == 0:
                    continue
                for fk in self.lista[entrada]['FK']:
                    if fk['parent table'] not in self.lista:
                        nextlevel.add(fk['parent table'])
                        splitname = FQName2array(fk['parent table'])
                        mtab = getTabRef(dd,confName,splitname[1],splitname[2])
                        if mtab:
                            self.lista[mtab.fqn()] = mtab.getTableInfo()
                        else:
                            print(fk['parent table'],' not in dictionary')
                            nextlevel.discard(fk['parent table'])
                            
    def getFKShallow(self):
        result = []
        idx = 0
        if 'FK' in self.lista[self.mainTable]:
            result.append([ [entry,] for entry in self.lista[self.mainTable]['FK'] ])
        else: #no tiene fks
            return result
        while idx < self.maxlevel:
            level = []
            for entry in result[-1]:
                tabla_referenciada = entry[-1]['parent table']
                if not 'FK' in self.lista[tabla_referenciada]:
                    continue
                for clave in self.lista[tabla_referenciada]['FK']:
                    tmp = list(entry) 
                    tmp.append(clave)
                    level.append(tmp)
            result.append(level)
            idx +=1
        return result
    
    def getFKDeep(self):
        """
        No usada por el momento
        """
        def getderived(base,level):
            if level >= self.maxlevel:
                return None
            if not self.lista[base]['FK'] or len(self.lista[base]['FK']) == 0:
                return None
            result = dict()
            for entry in self.lista[base]['FK']:
                result[entry['name']]={ key:entry[key] for key in entry if key != 'name'}
                result[entry['name']]['follow']=getderived(entry['parent table'],level +1)
            return result
            
        final = getderived(self.mainTable,0)
        return final
        

        
    def prepareJoin(self,joinList):
        #
        # el juego es que utilzo tuplas (relationship,table) como clave del diccionario de tablas
        #
        tableDict = dict() #key is tuple (relationship,table): DataShow,Alias
        #
        fieldList = [ [('base',self.mainTable),item['basename'],item['format']] for item in self.lista[self.mainTable]['Fields'] ]
        tableDict[('base',self.mainTable)] = [True,None]
        #
        joinDict = dict()
        if not joinList or len(joinList) == 0:
            return tableDict,fieldList,joinDict
            #sqlContext['fields'] = [ item[2] for item in fieldList]
            #sqlContext['formats'] = [item[3] for item in fieldList ]
            #sqlContext['tables'] = [ self.mainTable, ]
            #return sqlContext
        #vamos al shallow
        for link in joinList:
            childTable = self.mainTable
            childRel = 'base'
            for k,entry in enumerate(link):
                nombre = '.'.join([ item['name'] for item in link[:k +1] ])
                destTable = entry['parent table']
                childField  = entry['ref field']
                destField = entry['parent field']
                if (nombre,destTable) not in tableDict:
                    tableDict[(nombre,destTable)] = [False,None]
                if k == len(link) -1:
                    #TODO me falta colocar los campos en el sitio adecuado
                    fieldList +=[ [(nombre,destTable),item['basename'],item['format']] for item in self.lista[destTable]['Fields'] if item['basename'] != destField] 
                    tableDict[(nombre,destTable)][0]=True
                # no me molesto en comprobar si existe, es lo bueno de los diccionarios
                joinDict[(nombre,destTable)] = [(childRel,childTable),childField,destField]
                # aqui algo para poder grabar los joins y final
                childTable = destTable
                childRel   = nombre
        # antes de generar codigo sql tengo que definir alias.
        # Una implementacion alternativa:  base la tabla base y rn el resto de referencias
        #idx = 1
        #for id in tableDict:
            #print(id)
            #if id == ('base',self.mainTable):
                #tableDict[('base',self.mainTable)][1]='base'
            #else:
                #tableDict[id][1]='r{}'.format(idx)
                #idx +=1
        ## 
        nombres = dict()
        for id in tableDict:
            knombre = id[1].split('.')[-1]
            if knombre in nombres:
                nombres[knombre] +=1
            else:
                nombres[knombre] = 0
            tableDict[id][1]='{}_{}'.format(knombre,nombres[knombre])
            
        return tableDict,fieldList,joinDict

    def prepareBulkSql(self,pFilter=None):

        sqlContext = dict()
        sqlContext['driver']=self.driver.dialect.name
        sqlContext['tables']=None
        sqlContext['fields']=None
        sqlContext['join'] = []
        sqlContext['formats'] = None

        lista = self.getFKShallow()
        klista = []
        for k in range(self.maxlevel):
            klista += lista[k]

        tableDict,fieldList,joinDict = self.prepareJoin(klista)
        

        base_id = ('base',self.mainTable)
        alias =  tableDict[base_id][1]
        if alias:
            sqlContext['tables'] = '{} AS {}'.format(self.mainTable,alias)
        else:
            sqlContext['tables'] = self.mainTable
            
        if len(tableDict) == 1:
            sqlContext['fields'] = [ item[1] for item in fieldList]
            sqlContext['formats'] = [item[2] for item in fieldList ]
            sqlContext['sqls'] = queryConstructor(**sqlContext)
            return sqlContext
         
        sqlContext['fields'] = [ '{}.{}'.format(tableDict[item[0]][1],item[1]) for item in fieldList ]
        sqlContext['formats'] = [item[2] for item in fieldList ]

        sqlContext['join'] = []
        for link_key in sorted(joinDict):
                link = joinDict[link_key]
                clausula = {'join_modifier':'LEFT OUTER','table':None,'join_clause':None}
                clausula['table']= '{} AS {}'.format(link_key[1],tableDict[link_key][1])
                clausula['join_clause']=(('{}.{}'.format(tableDict[link[0]][1],link[1].split('.')[-1]),
                                 '=',
                                '{}.{}'.format(tableDict[link_key][1],link[2].split('.')[-1])
                                ),)
                sqlContext['join'].append(clausula)  
        if pFilter:
            sqlContext['base_filter'] = pFilter #TODO necesita que se le introduzcan los alias

        sqlContext['sqls'] = queryConstructor(**sqlContext)
        
        if DEBUG:
            print(queryFormat(sqlContext['sqls']))
        return sqlContext #

"""
 a partir de aqui es solo pruebas 
"""
def generaArgParser():
    import argparse
    parser = argparse.ArgumentParser(description='Cubo de datos')
    parser.add_argument('--cubeFile','--cubefile','-c',
                        nargs='?',
                        default='cubo.json',
                        help='Nombre del fichero de configuración del cubo actual')    
    parser.add_argument('--configFile','--configfile','-cf',
                        nargs='?',
                        default='.danabrowse.json',
                        help='Nombre del fichero de configuración del cubo actual')    

    security_parser = parser.add_mutually_exclusive_group(required=False)
    security_parser.add_argument('--secure','-s',dest='secure', action='store_true',
                                 help='Solicita la clave de las conexiones de B.D.')
    security_parser.add_argument('--no-secure','-ns', dest='secure', action='store_false')
    parser.set_defaults(secure=False)

    return parser

def traverse(root,base=None):
    if base is not None:
       yield base
       queue = base.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]      
def prueba():
    parser = generaArgParser()
    args = parser.parse_args()
    print(args)
    #dd = DataDict(defFile=args.configFile,secure=args.secure)
    # dd= DataDict(conn=confName,schema=schema)
    confName=  '$$TEMP'
    schema=  'public' # None #'dana_sample'
    table=  'rental' #None #'votos_locales'
    iters=  2
    confData=  {'driver': 'postgresql', 'dbname': 'pagila', 'dbhost': 'localhost', 'dbuser': 'werner', 'dbpass': ''}

    dd= DataDict(conName=confName,schema=schema,table=table,iters=iters +1
                 ,confData=confData,
                 defFile=args.configFile,secure=args.secure) 
    #pprint(dd.configData)
    ##print(dd.baseModel)
    #pprint(dd.conn)
    #print(dd.hiddenRoot)
    for entry in traverse(dd.hiddenRoot):
        tabs = '\t'*entry.depth()
        if not entry.isAuxiliar() and not entry.getTypeText() == '' :
            print(tabs,entry.getTypeText(),':',entry.getFullDesc()) #entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    #getTable(dd,confName,schemaName,tableName,maxlevel=1):
    ds = TableInfo(dd,confName,schema,table,maxlevel= iters)
    print( [ table for table in ds.lista] )
    ds.prepareBulkSql()
    #pprint(ds.getFKDeep()[2])
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    #aw = ApplicationWindow()
    #aw.show()
    prueba()
