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

import datetime


from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import  QSortFilterProxyModel, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter, QMenu, QLineEdit, QComboBox, QLabel, QPlainTextEdit

from support.datalayer.query_constructor import *
from support.datalayer.access_layer import getCursor

from support.gui.dialogs import dataEntrySheetDlg
from support.util.numeros import fmtNumber               
#from admin.cubemgmt.cubeTypes import LOGICAL_OPERATOR
from base.filterDlg import filterDialog

from support.util.decorators import waiting_effects,model_change_control 
from support.util.record_functions import defaultFromContext

from base.datadict import DataDict
from admin.dictmgmt.tableInfo import TableInfo

import base.config as config

from support.datalayer.querywidget import *

class TableBrowse(QueryTab):
    """
    overloaded methods
    """
    def __init__(self,confName=None,schema=None,table=None,pdataDict=None,iters=0):
        super().__init__(None)
        print('at init',iters)
        if confName is None or confName == '':
            return
        conn = self.getConnection(pdataDict,confName,schema,table,iters)
        if conn:
            self.baseModel = CursorItemModel()
            self.reconnect(conn)
            self.executeNewScript(self.generateSQL(confName,schema,table,iters,pFilter=None))
        else:
            print('No pude establecer conexion')
            exit()

    def addContextMenuActions(self,index,fila,columna):
        self.menuActions.append(self.menu.addAction("Filter query",self.filterQuery))
        if fila != -1:
            self.menuActions.append(self.menu.addAction("Filter query (pick this value)",lambda a=index:self.filterQueryPick(a)))
        if self.areFiltered:
            self.menuActions.append(self.menu.addAction("remove Filter",self.filterRemove))
        self.menuActions.append(self.menu.addSeparator())
        
        super().addContextMenuActions(index,fila,columna)
    """
    specific methods for DataDict management and SQL generation
    """
    def getConnection(self,pdataDict=None,confName=None,schema=None,table=None,iters=0):
        if isinstance(pdataDict,DataDict):
            dataDict = pdataDict
        else:
            dataDict=DataDict(conName=confName,schema=schema,table=table) #iters todavia no procesamos
        self.localContext = (dataDict,confName,schema,table,iters)    
        return dataDict.conn[confName]
    
    def generateSQL(self,confName,schema,table,iters,pFilter=None): 
        print('ITERACIONES',iters)
        dataDict = self.localContext[0]
        self.tableInfo = TableInfo(dataDict,confName=confName,schemaName=schema,tableName=table,maxlevel=iters)
        sqlContext = self.tableInfo.prepareBulkSql(pFilter)
        self.sqlEdit.hide()
        self.baseModel.recordStructure = []
        for  idx,fld in enumerate(sqlContext['fields']):
            self.baseModel.recordStructure.append({'name':fld,'format':sqlContext['formats'][idx]})
        sqls = sqlContext['sqls'] 
        return sqls
        
    @waiting_effects
    #@model_change_control()
    def loadData(self, pconfName=None,pschema=None,ptable=None,pdataDict=None,piters=1,pFilter=None):
        (dataDict,confName,schema,table,iters) = defaultFromContext(self.localContext,*(pdataDict,pconfName,pschema,ptable,piters))
        self.executeNewScript(self.generateSQL(confName,schema,table,iters,pFilter=pFilter))

    """
    specific context menu actions
    """
    def filterRemove(self):
        self.filtro = None
        self.areFiltered = False
        self.loadData()
        pass
    

    def filterQuery(self):
        #TODO mantener en presentacion el filtro de la ultima ejecución
        driver=self.localContext[0].conn[self.localContext[1]].dialect.name
        self.areFiltered = True
        self.filterDlg = filterDialog(self.baseModel.recordStructure,self.filtro,'Filtre por campos',self,driver=driver)
        if self.filterDlg.exec_():
            self.loadData(pFilter=self.filterDlg.result)
            self.filtro = [ data for data in self.filterDlg.data]


    def filterQueryPick(self,index):
        """
            index es QModelIndex
            El enredo de codigo es cuando tenemos un sort proxy y entonces los indices no
            cuadran con los del modelo base y hay que hacer la traduccion esa ...
            Eso si, con columnas ocultas funciona
        """
        
        row = index.row()
        column = index.column()
        value = index.data(Qt.UserRole +2)
        field = self.baseModel.recordStructure[column]['name']
        formato = self.baseModel.recordStructure[column]['format']
        #TODO esto deberia sacarse con lo del dialogo
        qfmt = 't'     
        if formato in ('entero','numerico'):
            qfmt = 'n'
        elif formato in ('fecha','fechahora','hora'):
            field=str(field)
            qfmt = 'f'
        elif formato in ('booleano'):
            qfmt = 'n' #me parece 
        pfilter = searchConstructor('where',where=((field,'=',value,qfmt),))
        self.areFiltered = True
        self.loadData(pFilter=pfilter)
        
        pass 
    
    def test(self):
        return
        

class TableBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None,iters=2):
        super(TableBrowserWin, self).__init__()
        self.view = TableBrowse(confName,schema,table,pdataDict,iters)
        if config.DEBUG:
            print('inicializacion completa')
        ##CHANGE here
    
        self.querySplitter = QSplitter(Qt.Horizontal)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.view)
        self.setCentralWidget(self.querySplitter)
               
        self.setWindowTitle("Visualizador de base de datos")
    
   
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    window = TableBrowserWin('Pagila','public','rental',iters=2)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
