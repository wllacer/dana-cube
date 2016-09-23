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


from dictTree import *

#from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize

#from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          #QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,\
          #QPushButton, QMessageBox, \
          #QTableView

from datalayer.access_layer import *
#from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
#from widgets import WPropertySheet

#from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError
#from  sqlalchemy.sql import text


class DataDict():
    def __init__(self,defFile=None):
        self.model = None
        self.hiddenRoot  = None  #self.hiddenRoot
        self.configData = None
        self.conn = dict()
        
        self.setupModel()
        if self.readConfigData(defFile):
            self.cargaModelo()
        else:
            print('No hay fichero de configuración o no tiene conexiones definidas')
            exit()
        
        
    def setupModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(5)
        self.hiddenRoot = newModel.invisibleRootItem()
        #self.multischema(newModel)        
        #proxyModel = QSortFilterProxyModel()
        #proxyModel.setSourceModel(newModel)
        #proxyModel.setSortRole(33)
        self.model = newModel #proxyModel
        
    def readConfigData(self,fileName=None):
        self.configData = load_cubo(getConfigFileName(fileName))
        if self.configData is None or self.configData.get('Conexiones') is None:
            return False
        else:
            return True
        
    def cargaModelo(self):
        definition = self.configData.get('Conexiones')
        for confName in sorted(definition):
            print('intentando',confName)
            conf =definition[confName]
            self.appendConnection(self.hiddenRoot,confName,conf)


    def appendConnection(self,padre,confName,conf):
        pos = padre.rowCount()
        try:
            self.conn[confName] = dbConnectAlch(conf)
            conexion = self.conn[confName]
            engine=conexion.engine 
            padre.insertRow(pos,(ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
            curConnection = padre.child(pos)

        except OperationalError as e:
            #TODO deberia ampliar la informacion de no conexion
            self.conn[confName] = None
            showConnectionError(confName,norm2String(e.orig.args))             
            padre.insertRow(pos,(ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
            curConnection = padre.child(pos)

        curConnection.refresh()
    

#def traverse(tree, key=None, mode=1):
    #if key is not None:
        #yield key
        #queue = tree.content[key].childItems
    #else:
        #queue = tree.rootItem.childItems
        #print(queue)
        #print('')
    #while queue:
        #yield queue[0].key
        #expansion = queue[0].childItems
        #if mode == _DEPTH:
            #queue = expansion + queue[1:]  # depth-first
        #elif mode == _BREADTH:
            #queue = queue[1:] + expansion  # width-first

def traverse(root,base=None):
    if base is not None:
       yield base
       queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        queue = expansion + queue[1:]             
    
def browse(base):
    numConn = base.rowCount()
    for i in range(0,numConn):
        conn = base.child(i)
        print(conn.text(),conn.getRow())
        numSch = conn.rowCount()
        if numSch == 0:
            continue
        for j in range(0,numSch):
            schema = conn.child(j)
            print('\t',schema.text())
            numTab = schema.rowCount()
            if numTab == 0:
                continue
            for k in range(0,numTab):
                table = schema.child(k)
                print('\t\t',table.text(),table.getRow())
                
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    #dict=DataDict('JeNeQuitePas')
    dataDict=DataDict()
    #browse(dataDict.hiddenRoot)
    for entry in traverse(dataDict.hiddenRoot):
        tabs = '\t'*entry.depth()
        print(tabs,entry.text(),'\t',entry.getRow())

    
