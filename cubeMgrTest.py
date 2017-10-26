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

from datalayer.query_constructor import *



DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from util.tree import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.numeros import stats

from datalayer.datemgr import getDateIndex,getDateEntry
from pprint import *

from core import Cubo

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList,changeTableName,changeSchema
from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
#from cubemgmt.cubeCRUD import insertInList
from dictmgmt.tableInfo import FQName2array,TableInfo

from dialogs import propertySheetDlg

import cubebrowse as cb

import time

from wizardmgmt.dispatcher import *

def traverse(root,funcion=None):
    if isinstance(root,CubeItem):
        if funcion is None or funcion(root):
            yield root
        queue = root.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        if funcion is None or funcion(queue[0]):
            yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]    
            
TIPOS = set([
     u'base_elem', #             field of  Reference  table
     u'code',      #             field of FK table (key)
     u'desc',       #             field of FK table (values)
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'fields',    #
     u'grouped by',#              field of FK table or derived value ??
     u'rel_elem',  #              field of FK table
    ])

def accion():
    import types
    import re
    app = QApplication(sys.argv)    
    confName = 'Pagila'
    schema = 'public'
    table = 'rental'
    dataDict=DataDict() #conName=confName) #,schema=schema)
    cubo = info2cube(dataDict,confName,schema,table,2) 
    print(dataDict)
    hiddenRoot = dataDict.hiddenRoot
    for item in traverse(hiddenRoot,lambda x:isinstance(x,SchemaTreeItem)):
        print(item.type(),item.text())
    #model = QStandardItemModel()
    #hiddenRoot = model.invisibleRootItem()
    #parent = hiddenRoot
    #for entrada in cubo:
        #if entrada == 'default':
            #tipo = 'default_base'
        ##elif entrada in types:
            ##tipo = entrada
        #else:
            #tipo = 'base'
        #recTreeLoader(parent,entrada,cubo[entrada],tipo)
    #raiz = None
    
    
def miniCube():
    app = QApplication(sys.argv)
    win = QMainWindow()
    confName = 'Pagila'
    schema = 'public'
    table = 'rental'
    dataDict=DataDict(conName=confName,schema=schema)
    cubo = info2cube(dataDict,confName,schema,table,3)   
    cubeMgr = cb.CubeMgr(win,confName,schema,table,dataDict,rawCube=cubo)
    cubeMgr.cache = dict()  #OJO OJO OJO
    cubeMgr.view.setContextMenuPolicy(Qt.CustomContextMenu)
    cubeMgr.view.customContextMenuRequested.disconnect()
    #print('desconectada')
    cubeMgr.view.customContextMenuRequested.connect(lambda i,j=cubeMgr:openContextMenu(j,i))

    cubeMgr.expandToDepth(1)        
    #if self.configSplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
    win.setCentralWidget(cubeMgr)
    win.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    win.show()
    app.exec_()
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
    #accion()
