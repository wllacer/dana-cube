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

from models import *

from datalayer.access_layer import *

from sqlalchemy.exc import *

(_ROOT, _DEPTH, _BREADTH) = range(3)




#def simplify(payload,cabeceras):
    #npay = list()
    #ncab = list()
    #for k,item in enumerate(payload):
        #if not item:
            #continue
        #npay.append(item)
        #ncab.append(cabeceras[k +1])
    #return npay,ncab

#def msimplify(payload,cabeceras):
    #if not isinstance(payload[0],(list,tuple)):
        #return simplify(payload,cabeceras)
    #profundidad = len(payload)
    #npay = [ list() for k in range(profundidad)]
    #ncab = list()
    #for k,item in enumerate(payload[-1]):
        #if not item:
            #continue
        #for j in range(profundidad):
            #npay[j].append(payload[j][k])
        #ncab.append(cabeceras[k +1])
    #return npay,ncab


#def processTree(grid,xtree,ytree):
    #textos_col = ytree.getHeader('col')
    #textos_row = xtree.getHeader('row')
    #line = 0
    #col  = 0
    #chart = dict()
    #for item in xtree.traverse(mode=1,output=1):
        #chart[item.key] = SimpleChart()
        #datos,cabeceras = simplify(item.getPayload(),textos_col)
        #if len(datos) == 0:
            #continue
        #chart[item.key].loadData('tarta',cabeceras,datos,xtree.name+'>'+item.getFullDesc()[-1],ytree.name,'sum(votes_presential)')  
        #grid.addWidget(chart[item.key],line,0)
        #chart[item.key].draw()
        #line +=1
   
    
def experimental():
    from util.jsonmgr import load_cubo
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['datos light'])
    #for ind,guia in enumerate(cubo.lista_guias):
        #print(ind,guia['name'])

    ind=2
    pprint(cubo.definition)
    vista=Vista(cubo,5,1,'sum','votes_presential',totalizado=True)
    model = TreeModel(vista)
    return model
    #k=vista.toTree2D()
    #return(vista.row_hdr_idx,vista.col_hdr_idx)

class ApplicationWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        #self.showMaximized()
        #self.main_widget = QWidget(self)
        
        #defwidget = QWidget()
        #self.grid = QGridLayout()
        #defwidget.setLayout(self.grid)
        #xtree,ytree = experimental()
        self.tree = QTreeView()
        self.tree.clicked.connect(self.drawChart)
        self.modelo = experimental()
        
        self.modelo.datos.format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)
        self.textos_col = self.modelo.datos.col_hdr_idx.getHeader('col')
        self.textos_row = self.modelo.datos.row_hdr_idx.getHeader('row')
        
        self.tree.setModel(self.modelo)
        self.tree.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding))
        for k in range(self.modelo.datos.col_hdr_idx.count()):  
            self.tree.hideColumn(k+1)
            
        self.chart = SimpleChart()
        self.chart.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        self.chartType = 'multibar'
        if self.modelo.datos.totalizado:
            self.processChartItem(tipo=self.chartType)
        mainWidget = QWidget()
        lay = QGridLayout()
        mainWidget.setLayout(lay)
        
        lay.addWidget(self.tree,0,0,1,1)
        lay.addWidget(self.chart,0,1,1,4)

        self.setCentralWidget(mainWidget)
        
        
    def drawChart(self,index):
        self.processChartItem(index,tipo=self.chartType)

    def processChartItem(self,index=None,tipo='bar'):
        if index:
            item = self.modelo.item(index)
        else:
            item = self.modelo.item('//')
            
        #textos_col = ytree.getHeader('col')
        #textos_row = xtree.getHeader('row')
        #line = 0
        #col  = 0
        titulo = self.modelo.datos.row_hdr_idx.name+'> '+item.getFullDesc()[-1] +  '\n' + \
            '{}({})'.format(self.modelo.datos.agregado,self.modelo.datos.campo) 
        x_text = self.modelo.datos.col_hdr_idx.name
        y_text = ''
        
        if tipo == 'multibar': 
            datos,kcabeceras = item.simplifyHierarchical() #msimplify(mdatos,self.textos_col)
        else:
            datos,kcabeceras = item.simplify() #item.getPayload(),self.textos_col)
        cabeceras = [ self.modelo.colHdr[k] for k in kcabeceras ]

        if len(datos) == 0:
            self.chart.axes.cla()
        else:
            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,item.getFullDesc())  
        self.chart.draw()

def dbConnectORA(conDict):

    context = dbDict2Url(conDict)
    if 'debug' in conDict:
        debug=conDict['debug']
    else:
        debug=False
    if 'oracle' in context.lower():
        print('Entro para Oracle')
        engine = create_engine(context,exclude_tablespaces= ["DONOTEXIST",],echo=debug)
    else:
        engine = create_engine(context,echo=debug)
    return engine.connect()
 
def oracle():
    from  sqlalchemy import create_engine,inspect,MetaData, types
    from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError

    definition1={'driver':'sqlite','dbname': '/home/werner/projects/scifi/scifi.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False } 
    definition2={'driver':'mysql','dbname': 'sakila',
                'dbhost':'localhost','dbuser':'root','dbpass':'***','debug':False } 

    definition3={'driver':'mysql','dbname': 'libgen',
                'dbhost':'localhost','dbuser':'root','dbpass':'***','debug':False } 
    
    definition5={'driver':'postgresql','dbname': 'dana_sample',
                'dbhost':'localhost','dbuser':'demo','dbpass':'demo123','debug':False } 
    
    definition4={'driver':'oracle','dbname': 'XE',
                'dbhost':'werner-arch','dbuser':'demo','dbpass':'***','debug':False } 
    
    conn = dbConnectORA(definition4)
    sql_verify = "select * from {}.{} where rownum = 1"
    #for schema in conn.execute(sql_schemas):
        #print(schema)
    engine = conn.engine
    inspector = inspect(engine)
    
    if len(inspector.get_schema_names()) is 0:
        schemata =[None,]
    else:
        schemata=inspector.get_schema_names()  #behaviour with default
    
    for schema in schemata:
        print(schema)
        list_of_files = inspector.get_table_names(schema)
        for table_name in list_of_files:
            print('\t table:',table_name)
            #try:
                #conn.execute(sql_verify.format(schema,table_name))
            #except DatabaseError as e:
                #print('Error ==>',schema,table_name,e.args)

        list_of_views = inspector.get_view_names(schema)
        for view_name in list_of_views:
            print('\t view:',view_name)
            try:
                conn.execute(sql_verify.format(schema,view_name))
            except DatabaseError as e:
                print('Error ==>',schema,table_name,e.args)

    #cursor = getCursor(conn,'select user,table_name from all_tables',LIMIT=10)
    #for (user,table_name) in cursor:
        #print(user,table_name)

def norm2string(entrada):
    import re
    if isinstance(entrada,(list,tuple)):
       return entrada
    elif '(' in entrada:
        return re.split(r',\s*(?=[^)]*(?:\(|$))', entrada)
        #de tackoverflow.com/questions/1648537/how-to-split-a-string-by-commas-positioned-outside-of-parenthesis
    else:
       return entrada.split(',')
    
def fecha():
    from datalayer.datemgr import getDateIndexElement
    inicio = datetime.date(2001,1,1)
    fin = datetime.datetime(2016,12,31)
    print(getDateIndexElement(fin,inicio,'Y'))

def datadict():
    from  sqlalchemy import create_engine,inspect,MetaData, types
    from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError
    
    definition5={'driver':'postgresql','dbname': 'dana_sample',
                'dbhost':'localhost','dbuser':'demo','dbpass':'demo123','debug':False } 

    conn = dbConnect(definition5)
    engine = conn.engine
    inspector = inspect(engine)
    table = 'votos_locales'
    schema = None
    fks =  inspector.get_foreign_keys(table,schema)
    print(fks)
    
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
    #app.exec_()
    #exit()
    #numero = -232145.1234567890123
    #print(fmtNumber(numero))
    #print(fmtNumber(numero,{'decimalmarker':','}))
    #experimental(aw)
    #print(norm2string('Uno'))
    #print(norm2string('Uno,Dos'))
    #print(norm2string('Uno(y medio),Dos'))
    #print(norm2string('Uno(y tres,cuartos),Dos'))
    #print(norm2string('funsion(Uno,dos,tres),cuatro'))
    #print(norm2string('cuatro,funsion(Uno,dos,tres)'))
    #print(norm2string('funsion(Uno,dos,(tres,cuatro))'))
    datadict()
