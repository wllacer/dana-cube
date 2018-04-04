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
from util.decorators import *

from PyQt5 import QtCore
#from PyQt5.QtGui import QSizePolicy
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGridLayout, QSizePolicy, QWidget, QTreeView, QHBoxLayout

from dictmgmt.datadict import DataDict
from dictmgmt.tableInfo import TableInfo

(_ROOT, _DEPTH, _BREADTH) = range(3)

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
    parser.set_defaults(secure=True)

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
#def pruebaTableInfo():
    #parser = generaArgParser()
    #args = parser.parse_args()
    #print(args)
    ##dd = DataDict(defFile=args.configFile,secure=args.secure)
    ## dd= DataDict(conn=confName,schema=schema)
    #confName= '$$TEMP' #'Elecciones 2105' #'$$TEMP'
    #schema= 'public' # 'main' # None #'dana_sample'
    #table=  'main' #'datos_electorales_2015' #'votos_locales' #'votos_prov_ref' #None #'votos_locales'
    #iters=  2
    #confData=  {'driver': 'postgresql', 'dbname': 'libgen', 'dbhost': 'localhost', 'dbuser': 'werner', 'dbpass': ''}
    ##confData=   {
            ##"dbport": "",
            ##"dbhost": "",
            ##"driver": "sqlite",
            ##"dbpass": "",
            ##"debug": False,
            ##"dbuser": "",
            ##"dbname": "/home/werner/projects/dana-cube.git/ejemplo_dana.db"
        ##}
    ##confData = {'dbname':"/home/werner/projects/dana-cube.git/ejemplo_dana.db",'driver':'sqlite'}
    ##confData=  {'driver': 'sqlite', 'dbname': "/home/werner/projects/dana-cube.git/ejemplo_dana.db", 'dbhost': '', 'dbuser': '', 'dbpass': ''}
    ##confData=  {'driver': 'mysql', 'dbname': 'libgen', 'dbhost': 'localhost', 'dbuser': 'demo', 'dbpass': 'demo123'}
    ##dd= DataDict(conName=confName,schema=schema,table=table,iters=iters +1,
    ##            defFile=args.configFile,secure=args.secure) 
    ##dd= DataDict(defFile=args.configFile,secure=args.secure) 
    ##dd= DataDict(conName=confName,defFile=args.configFile,secure=args.secure) 
    #dd= DataDict(conName=confName,schema=schema,table=table,iters=iters +1,confData = confData)
    ##pprint(dd.configData)
    ###print(dd.baseModel)
    #conn = dd.getConnByName(confName)
    #inspector = conn.inspector
    ##pprint(inspector.get_check_constraints(table,schema))
    #pprint(inspector.get_pk_constraint(table,schema))
    #pprint(inspector.get_unique_constraints(table,schema))
    ##pprint(inspector.get_columns(table,schema))
    ##pprint(dd.conn)
    ##print(dd.hiddenRoot)
    #campos = []
    #for entry in traverse(dd.hiddenRoot):
        #tabs = '\t'*entry.depth()
        #if not entry.isAuxiliar() and entry.getTypeText() == '' :
            #campos.append(entry)
            ##print(tabs,entry.getTypeText(),':',entry.getFullDesc()) #entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    ## peor que individual . 50 * 8 s frente a 12 m
    #sqlstring = 'SELECT '
    #for k,item in enumerate(campos):
        #if k == 0:
            #sqlstring += ' COUNT(DISTINCT {})'.format(item.text())
        #else:
            #sqlstring = ', '.join((sqlstring,'COUNT(DISTINCT {})'.format(item.text())))
    #sqlstring += ' FROM {}.{}'.format(schema,table)
    #print(sqlstring)
    ##ds = TableInfo(dd,confName,schema,table,maxlevel= iters)
    ##getValueSpread(conn,sqlstring)
    ##pprint(ds.lista)
    ##pprint(ds.info2cube())
    ##print(dd.isEmpty)

#@stopwatch
#def getValueSpread(conn,sqls):
    #from datalayer.access_layer import getCursor
    #result = getCursor(conn.data().engine,sqls)
    #pprint(result)
    
#def testea():
    #definition = dict()
    #for item in definition.get('lista',[]):
        #print(item)
#if __name__ == '__main__':
    ## para evitar problemas con utf-8, no lo recomiendan pero me funciona
    #import sys
    ## para evitar problemas con utf-8, no lo recomiendan pero me funciona
    #if sys.version_info[0] < 3:
        #reload(sys)
        #sys.setdefaultencoding('utf-8')
    #app = QApplication(sys.argv)
    ##aw = ApplicationWindow()
    ##aw.show()
    #pruebaTableInfo()

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
    pprint(ds.info2cube())
    print( [ table for table in ds.lista] )
    ds.prepareBulkSql()
    #pprint(ds.getFKDeep()[2])

def numeros():
    from util.numeros import s2n
    a = 1234
    b = 1234.
    c = '1234'
    d = '1234.0'
    e = '    123.4'
    f = '  1234.5  '
    g = '1234.5    '
    print(s2n(a),type(a))
    print(s2n(b),type(b))
    print(s2n(c),type(c))
    print(s2n(d),type(d))
    print(s2n(e),type(e))
    print(s2n(f),type(f))
    print(s2n(g),type(g))
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
    #prueba()
    numeros()
