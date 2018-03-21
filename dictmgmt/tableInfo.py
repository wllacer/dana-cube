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

from datalayer.query_constructor import *

import config

(_ROOT, _DEPTH, _BREADTH) = range(3)


def FQName2array(fqname):
    dbmanager = '' #no deberia existir pero por si acaso
    schema = ''
    filename = ''
    splitdata = fqname.split('.')
    if len(splitdata) == 3:
        dbmanager,schema,filename = splitdata
    elif len(splitdata) == 2:
        schema,filename = splitdata
    elif len(splitdata) == 1:
       filename = fqname
    return dbmanager,schema,filename

def getTabRef(dd,confName,schemaName,tableName):
    con = dd.getConnByName(confName)
    if con is None:
        if config.DEBUG:
            print('Conexion {} no definida'.format(confName))
        return None
    sch = con.getChildrenByName(schemaName)
    if sch is None:
        if config.DEBUG:
            print('Esquema {} no definido'.format(schemaName))
        return None
    tab = sch.getChildrenByName(tableName)
    if tab is None:
        if config.DEBUG:
            print('Tabla {} no definida'.format(tableName))
        return None

    if config.DEBUG:
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
        
        self.dd = dd
        self.confName = confName
        self.schemaName = schemaName
        self.tableName = tableName
        self.lista = dict()
        
        if not dd.getConnByName(confName):
            print('Conexion inexistente ',confName)
            exit()
            
        self.driver = dd.getConnByName(confName).data()
                
        tab = getTabRef(dd,confName,schemaName,tableName)
        if not tab:
            print('Tabla {}.{}.{} no encontrada'.format(confName,schemaName,tableName))
            return 
        

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
        

    def locate(self,fieldList,relName,tableName,fldName):
        # no parece la mas eficiente de las soluciones ... pero no veo de momento posiblidad sin convertirlo en un dict
        # tampoco es que tenga mucho sentido como metodo de la clase
        for k,elem in enumerate(fieldList):
            if elem[0] == (relName,tableName):
                if elem[1] == fldName:
                    return k
        return None
    
    def prepareStmt(self,joinList):
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
                    # localizar la posicion de childRel,childTable,childField
                    pos = self.locate(fieldList,childRel,childTable,childField)
                    thisTableFields = [ [(nombre,destTable),item['basename'],item['format']] for item in self.lista[destTable]['Fields'] if item['basename'] != destField] 
                    if pos:
                        fieldList[pos +1:pos +1]= thisTableFields
                    else:
                        fieldList += thisTableFields
                        
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

        tableDict,fieldList,joinDict = self.prepareStmt(klista)
        

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
                leftTable =  tableDict[link[0]][1]  #childTable
                leftFields = norm2List(link[1])
                rightTable = tableDict[link_key][1] #parent Table
                rightFields = norm2List(link[2])
                if len(leftFields) != len(rightFields):
                    print('No se como procesar ',link)
                    continue
                clausula['join_clause']=[
                                 ('{}.{}'.format(leftTable,leftFields[k].split('.')[-1].strip()),
                                 '=',
                                '{}.{}'.format(rightTable,rightFields[k].split('.')[-1].strip()))
                                 for k in range(len(leftFields)) ]
                sqlContext['join'].append(clausula)  
        if pFilter:
            sqlContext['base_filter'] = pFilter #TODO necesita que se le introduzcan los alias

        sqlContext['sqls'] = queryConstructor(**sqlContext)
        
        if config.DEBUG:
            print(queryFormat(sqlContext['sqls']))
        return sqlContext #

    def info2cube(self):
        from datalayer.datemgr import genCuatrimestreCode,genTrimestreCode,genQuincenaCode

        conn = self.dd.getConnByName(self.confName)
        inspector = conn.inspector
        pkstring = norm2String(inspector.get_pk_constraint(self.tableName,self.schemaName)['constrained_columns'])
        uqlist = [pkstring,] + [ norm2String(item['column_names']) for item in inspector.get_unique_constraints(self.tableName,self.schemaName)]
        cubo = dict()
        basename = self.mainTable.split('.')[-1]
        cubo[basename]=dict() # si hubiera algo ... requiescat in pace
        entrada = cubo[basename] #para simplificar la escritura
        # la informacion basica
        entrada['base filter']=""
        entrada['table'] = self.mainTable
        entrada['connect']=self.dd.configData['Conexiones'][self.confName]
        # reseteamos la password
        entrada['connect']['dbpass'] = ''
        #
        entrada['guides']=[]
        entrada['fields']=[]
        
        info = self.lista[self.mainTable]
        
        for fld in info['Fields']:
            simpleName = fld['name'].split('.')[-1]
            if simpleName in uqlist:
                continue
            
            if fld['format'] in ('numerico','entero'):
                entrada['fields'].append(fld['name'])
            elif fld['format'] in ('fecha','fechahora'):
                entrada['guides'].append({'name':fld['basename'],
                                        'class':'d',
                                        'prod':[{'fmt':'date','elem':fld['name'],'mask':'Ym'},]
                                        })  #no es completo
                entrada['guides'].append( genCuatrimestreCode(fld['name'],self.driver.dialect.name))
                entrada['guides'].append( genTrimestreCode(fld['name'],self.driver.dialect.name))
                entrada['guides'].append( genQuincenaCode(fld['name'],self.driver.dialect.name))

            else:
                entrada['guides'].append({'name':fld['basename'],
                                        'class':'o',
                                        'prod':[{'elem':fld['name'],},]})  #no es completo

        if self.maxlevel == 0 or 'FK' not in self.lista[self.mainTable] or len(self.lista[self.mainTable]['FK']) == 0:
            return cubo

        lista = self.getFKShallow()
        fkList = []
        for k in range(self.maxlevel):
            fkList += lista[k]

        
        for entry in fkList:
            relationship = entry[-1]
            nombre = '_'.join([ item['name'] for item in entry ])
            entrada['guides'].append({'name':nombre,
                        'class':'o',
                        'prod':[{'domain': {
                                "filter":"",
                                "table":relationship['parent table'],
                                "code":relationship['parent field'],
                                "desc":relationship['parent field']
                            },
                            'link via':[ ],
                                #[{ "table":actor['parent table'],
                                #"clause":[
                                            #{"rel_elem":actor["parent field"],"base_elem":actor['ref field']}
                                         #],
                                #"filter":"" } for actor in entry[:-1]] ,

                            'elem':entry[-1]['ref field']},]
                            })  
            for k,actor in enumerate(entry[:-1]):
                link_dict = dict()
                link_dict['table'] = actor['parent table']
                link_dict['filter'] = ""
                leftTable = self.mainTable if k == 0 else entry[k -1]['parent table']
                rightTable = link_dict['table']
                leftFields = [ '{}.{}'.format(leftTable,item) for item in  norm2List(actor['ref field']) ]
                rightFields = [ '{}.{}'.format(rightTable,item) for item in  norm2List(actor['parent field']) ]
                if len(leftFields) != len(rightFields):
                    print('No puede procesarse la FK',entry)
                    continue
                link_dict['clause'] = [ {'rel_elem':rightFields[k],'base_elem':leftFields[k] } for k in range(len(leftFields)) ]
                if link_dict:
                    entrada['guides'][-1]['prod'][-1]['link via'].append(link_dict)
            if entrada['guides'][-1]['prod'][-1]['link via'] == [] :
                                del entrada['guides'][-1]['prod'][-1]['link via']
            # creamos relaciones jerarquizadas. 
            # de momento dos tipos solo fks multicampo y fks de mas de un nivel separadas
            if len(entry) == 1 and len(norm2List(entry[0]['ref field'])) > 1:

                nombre = '.'.join([ item['name'] for item in entry ]) + 'jerarquizada'
                entrada['guides'].append({'name':nombre,
                            'class':'h',
                            'prod':[]
                            })
                actor = entry[-1]
                leftFields = norm2List(actor['ref field'])
                rightFields = norm2List(actor['parent field'])
                if len(leftFields) != len(rightFields):
                    print('No puede procesarse la FK',entry)
                    continue
                for k in range(len(leftFields)):
                    paso = {'domain': {
                                    "filter":"",
                                    "table":relationship['parent table'],
                                    "code":rightFields[k],
                                    "desc":rightFields[k],
                                    },
                                #'link via':[ ],
                                    ##[{ "table":actor['parent table'],
                                    ##"clause":[
                                                ##{"rel_elem":actor["parent field"],"base_elem":actor['ref field']}
                                            ##],
                                    ##"filter":"" } for actor in entry[:-1]] ,

                                'elem':leftFields[k]}
                    if k > 0:
                        print(norm2String(rightFields[0:k]))
                        paso['domain']['grouped by']=norm2String(rightFields[0:k])
                    
                    entrada['guides'][-1]['prod'].append(paso)
                                
            #if len(entry) > 1:
                #nombre = '.'.join([ item['name'] for item in entry ]) + 'jerarquizada'
                #entrada['guides'].append({'name':nombre,
                            #'class':'h',
                            #'prod':[]
                            #})


        return cubo

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
