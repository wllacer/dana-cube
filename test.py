#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''
from base.core import Cubo,Vista
#from support.datalayer.query_constructor import *
#from operator import attrgetter,methodcaller

from pprint import pprint

from  PyQt5.QtWidgets import QApplication


#import base.exportWizard as eW
#from support.util.numeros import fmtNumber
#from support.util.jsonmgr import dump_structure
from support.gui.mplwidget import SimpleChart
  
#import math
#import matplotlib.pyplot as plt
#import numpy as np
from support.util.decorators import *

from PyQt5 import QtCore
#from PyQt5.QtGui import QSizePolicy
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGridLayout, QSizePolicy, QWidget, QTreeView, QHBoxLayout

from base.datadict import DataDict
from admin.dictmgmt.tableInfo import TableInfo

from admin.cubemgmt.cubeTreeUtil import *

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

def traverse(root,base=None,order='depth'):
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
            if order == 'depth':
                queue = expansion  + queue[1:]      
            else:
                queue = queue[1:] +expansion
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
    #from support.datalayer.access_layer import getCursor
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
    #confName=  '$$TEMP'
    #schema=  'public' # None #'dana_sample'
    #table=  'rental' #None #'votos_locales'
    #confData=  {'driver': 'postgresql', 'dbname': 'pagila', 'dbhost': 'localhost', 'dbuser': 'werner', 'dbpass': ''}
    #iters=  2
    #dd= DataDict(conName=confName,schema=schema,table=table,iters=iters +1
                 #,confData=confData,
                 ##defFile=args.configFile,secure=args.secure) 
                 #)
    #pprint(tree2dict(dd.hiddenRoot,isDictFromDef))
    #pprint(dd.configData)
    ##print(dd.baseModel)
    #pprint(dd.conn)
    #print(dd.hiddenRoot)
    dd = file2datadict('testcubo.json')
    diccionario = tree2dict(dd.hiddenRoot)
    pprint(diccionario)
    #
    #for entry in traverse(dd.hiddenRoot):
        #tabs = '\t'*entry.depth()
        #print(tabs,entry.text(),' > ',entry.fqn(),':',entry.getRow())
        #print(tabs,entry.getTypeText(),':',entry.getRow())
        #if not entry.isAuxiliar():# and not entry.getTypeText() == '' :
            #print(tabs,entry.getTypeText(),':',entry.getFullDesc(),entry.gpi()[0],entry.gpi()[1]) #entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())

    #ds = TableInfo(dd,confName,schema,table,maxlevel= iters)
    #pprint(ds.info2cube())
    ##print( [ table for table in ds.lista] )
    #ds.prepareBulkSql()
    ##pprint(ds.getFKDeep()[2])

def numeros():
    from support.util.numeros import s2n
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
    
res = {
'Almería':(20.39328112594321,None,None,34.070481245359105,34.99994270926594,10.536294919431741,None,None,None,None,None,None,None,None,None,None),
'Cádiz':(21.57317665399801,None,None,25.722487800463316,35.1636124577351,17.54072308780357,None,None,None,None,None,None,None,None,None,None),
'Córdoba':(17.321445512157016,None,None,27.855521238254205,39.790138231693376,15.032895017895383,None,None,None,None,None,None,None,None,None,None),
'Granada':(19.901452748963663,None,None,28.148365523293545,37.95736373760612,13.992817990136658,None,None,None,None,None,None,None,None,None,None),
'Huelva':(16.823293886701787,None,None,25.732152512451346,44.74551772146849,12.699035879378375,None,None,None,None,None,None,None,None,None,None),
'Jaén':(15.039737879983354,None,None,27.985540776410467,46.17628613787271,10.79843520573347,None,None,None,None,None,None,None,None,None,None),
'Málaga':(24.662032230583907,None,None,26.38991724849689,33.22289333418562,15.725157186733592,None,None,None,None,None,None,None,None,None,None),
'Sevilla':(18.82199422414816,None,None,22.967621782713486,41.94061369360607,16.269770299532297,None,None,None,None,None,None,None,None,None,None), 
}
party =     "geo,C's,EH Bildu,EAJ-PNV,PP,PSOE,PODEMOS,GBAI,CCa-PNC,IU-UPeC,MÉS,DL,PODEMOS-COMPROMÍS,NÓS,EN COMÚ,PODEMOS-En Marea-ANOVA-EU,ERC-CATSI".split(',')

from userfunctions.electoral import dhont
provs = {
'Almería':12,
'Cádiz':15.,
'Córdoba':12,
'Granada':13,
'Huelva':11,
'Jaén':11,
'Málaga':17,    
'Sevilla':18,
}


def andazulia():
    zumatorio = [ 0 for k in range(len(party) -1) ]
    for prov in provs:
        provincia = dhont(int(provs[prov]),res[prov])
        for k in range(len(provincia)):
            zumatorio[k] += provincia[k] if provincia[k] else 0
    print(zumatorio)
    
def andazulia_jun():
    zumatorio = [ 0 for k in range(len(party) -1) ]
    for prov in provs:
        datos = list(res[prov])
        datos[3] += datos[0]
        datos[0] = 0
        provincia = dhont(int(provs[prov]),datos)
        for k in range(len(provincia)):
            zumatorio[k] += provincia[k] if provincia[k] else 0
    print(zumatorio)

if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #app = QApplication(sys.argv)
    #aw = ApplicationWindow()
    #aw.show()
    #prueba()
    #numeros()
    andazulia()
    andazulia_jun()
