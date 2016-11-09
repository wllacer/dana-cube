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

   
def sql():
  pepe=dict()
  clause1=dict()
  pepe['tables']='votos_locales'
  pepe['fields']=['geo_rel.padre','partido',('votes_presential','sum')]
  pepe['group']=['partido',]
  pepe['join']={'table':'geo_rel',
                'join_filter':"geo_rel.tipo_padre = 'P'",
                'join_clause':(('padre','=','votos_locales.municipio'),),
               }

  #clause2=dict()
  #pepe['fields']=(""" case 
        #when partido in (3316,4688) then '1 derecha'
    #when partido in (1079,4475) then '2 centro'
        #when partido in (3484) then '3 izquierda'
    #when partido in (3736,5033,4850,5008,5041,2744,5026) then '4 extrema'
        #when partido in (5063,4991,1528) then '5 separatistas'
        #when partido in (1533,4744,4223) then '6 nacionalistas'
    #else
         #'otros'
    #end as categoria""" ,'partido',('seats','sum'))
  #pepe['tables']='votos_provincia'
  #pepe['group']=('categoria',)
  #pepe['lfile']='sempronio'
  #pepe['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
  #pepe['tables'] = 'paco'
  ##pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
  #pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
  ##pepe['tables'] = 'paco'
  ##pepe['select_modifier'] = 'DISTINCT'
  #pepe['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
                    #('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
                  #)
  ##pepe['where']=((clause1,'OR',clause2),)
  ##pepe['group']=('julia','claudia')
  ##pepe['having']=(('campo','=','345'),)
  #pepe['base_filter']=''
  #pepe['order']=(1,(2,'DESC'),3)
  #pprint(pepe)
  ##pepe['fields'] = '*'

  print(queryConstructor(**pepe))



#from datadict import *    
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

from datalayer.query_constructor import *


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
    

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from util.tree import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.fivenumbers import stats

from datemgr import getDateIndex,getDateEntry
from pprint import *

from core import Cubo

from cubemgmt.cubeutil import info2cube
import cubebrowse as cb

import time


def miniCube():
    app = QApplication(sys.argv)
    win = QMainWindow()
    confName = 'MariaBD Local'
    schema = 'sakila'
    table = 'payment'
    dataDict=DataDict(conn=confName,schema=schema)
    cubo = info2cube(dataDict,confName,schema,table,2)   
    cubeMgr = cb.CubeMgr(win,confName,schema,table,dataDict,rawCube=cubo)
    cubeMgr.expandToDepth(1)        
    #if self.configSplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
    win.setCentralWidget(cubeMgr)
    win.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    win.show()
    app.exec_()
    exit()
    
class MiniWizard(QWizard):
    def __init__(self):
        super(MiniWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.setPage(1, Wz1())
        self.setPage(2, Wz2())
        self.setPage(3, Wz3())
        self.setPage(4, Wz4())
        self.setWindowTitle('Tachan')
        self.show()

class Wz1(QWizardPage):
    def __init__(self,parent=None):
        super(Wz1,self).__init__(parent)
        self.contador = 0
        self.diccionario = {'alfa':'omega'}
        
    def initializePage(self):
        self.contador += 1

class Wz2(QWizardPage):
    def __init__(self,parent=None):
        super(Wz2,self).__init__(parent)
        self.contador = 0
    def initializePage(self):
        self.contador += 1
        self.wizard().page(1).diccionario[self.contador] = 'iteracion' + str(self.contador)

class Wz3(QWizardPage):
    def __init__(self,parent=None):
        super(Wz3,self).__init__(parent)

        linkLabel = QLabel("¿Quiere volver a empezar?")
        self.linkCheck = QCheckBox()
        linkLabel.setBuddy(self.linkCheck)
        self.linkCheck.stateChanged.connect(self.estadoLink)
        

        layout = QGridLayout()
        layout.addWidget(linkLabel,0,0)
        layout.addWidget(self.linkCheck,0,1)
        self.setLayout(layout)

        self.contador = 0
    
    def estadoLink(self):
        if self.linkCheck.isChecked():
            self.wizard().setStartId(2);
            self.wizard().restart()        
    def initializePage(self):
        self.contador += 1

class Wz4(QWizardPage):
    def __init__(self,parent=None):
        super(Wz4,self).__init__(parent)
        self.contador = 0
    def initializePage(self):
        self.contador += 1
        


def miniWizard():
    
    app = QApplication(sys.argv)
    wizard = MiniWizard()        
    if wizard.exec_() :
        print('Milagro',wizard.page(1).contador,wizard.page(2).contador,wizard.page(3).contador)
        print(wizard.page(1).diccionario)
        exit()

if __name__ == '__main__':
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    #app = QApplication(sys.argv)
    miniCube()
    #miniWizard()
    #window = TableBrowserWin('MariaBD Local','sakila','film',pdataDict=None)
    #dataDict=DataDict()
    #window = TableBrowserWin('MariaBD Local','sakila','film',pdataDict=dataDict)
    ##window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    #window.show()
    #sys.exit(app.exec_())

    #dict=DataDict('JeNeQuitePas')
    dataDict=DataDict()
    #dataDict=DataDict(conn='MariaBD Local',schema='sakila')
    #dataDict=DataDict(conn='Pagila',schema='public')
    for entry in traverse(dataDict.hiddenRoot):
        tabs = '\t'*entry.depth()
        if not entry.isAuxiliar():
            print(entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    #browse(dataDict.hiddenRoot)
    #browseTables(dataDict.hiddenRoot)
    #browse0(dataDict.hiddenRoot)
    #info = getTable(dataDict,'MariaBD Local','sakila','rental')            
    #info = getTable(dataDict,'MariaBD Local','sakila','film')            
    #cubo = info2cube(dataDict,'MariaBD Local','sakila','customer',2)   
    #pprint(cubo)
    #dump_structure(cubo,'experimento.json')
    #info2cube(dataDict,'Pagila','public','rental')            
    #pprint(info)
    #pprint(cubo)
    #cursor = localQuery(dataDict.conn['MariaBD Local'],info,1)
    #modelo = QStandardItemModel()
    #for row in cursor:
        #modelRow = [ QStandardItem(str(fld)) for fld in row ]
        #modelo.appendRow(modelRow)
    #print(modelo.rowCount(),modelo.columnCount())
    #for k in range(modelo.rowCount()):
        #datos = [ modelo.item(k,j).data(Qt.DisplayRole) for j in range(modelo.columnCount()) ]
        ##datos = [ itm.data(Qt.DisplayRole) for itm in deRow ]
        #print(datos)
    ##getTable(dataDict,'Elecciones 2105','','partidos')            
"""
SELECT  geo_rel.padre, partido, sum(votes_presential)  
FROM votos_locales  
     JOIN geo_rel ON geo_rel.hijo = votos_locales.municipio AND geo_rel.tipo_padre = 'P'  
     GROUP BY geo_rel.padre, partido  
     
"related via":[{
    "table": "geo_rel",
    "clause": [
        {
            "rel_elem":"hijo",
            "base_elem":"votos_locales.municipio"
        }
        ],
    "filter": "geo_rel.tipo_padre = 'P'"
                        }
                        ],

"""
