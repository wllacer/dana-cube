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

from dictmgmt.datadict import *    
#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import  QSortFilterProxyModel, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter, QMenu, QLineEdit, QComboBox, QLabel, QPlainTextEdit

from datalayer.query_constructor import *
from dictmgmt.tableInfo import *

from dialogs import dataEntrySheetDlg
from util.numeros import fmtNumber               
from cubemgmt.cubeTypes import LOGICAL_OPERATOR
from filterDlg import filterDialog

from util.decorators import waiting_effects 
from util.record_functions import defaultFromContext
DEBUG = True

DEFAULT_FORMAT = dict(thousandsseparator=".",
                            decimalmarker=",",
                            decimalplaces=2,
                            rednegatives=False,
                            yellowoutliers=False)

class CursorItemModel(QStandardItemModel):
    def __init__(self,parent=None):
        super(CursorItemModel, self).__init__(parent)
        self.recordStructure = None
        
class CursorItem(QStandardItem):
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        super(CursorItem, self).__init__(*args)
    
    def data(self,role=Qt.UserRole +1):
        if self.model() and self.model().recordStructure and role in (Qt.DisplayRole, Qt.TextAlignmentRole):
            index = self.index()
            format = self.model().recordStructure[index.column()]['format']
            if format in ('numerico','entero'):
                if role == Qt.TextAlignmentRole:
                    return Qt.AlignRight| Qt.AlignVCenter
                else:
                    defFmt = DEFAULT_FORMAT.copy()
                    try:
                        if format == 'numerico':
                            defFmt['decimalplaces'] = 2
                        else:
                            defFmt['decimalplaces'] = 0
                        rawData = super(CursorItem,self).data(role)
                        text, sign = fmtNumber(float(rawData),defFmt)
                        return '{}{}'.format(sign,text)
                    except ValueError:
                        if rawData == 'None':
                            return ''
                        else:
                            if DEBUG:
                                print ('error de formato en ',
                                self.model().recordStructure[index.column()],index.row(),
                                super(CursorItem,self).data(role))
                            return rawData
            #else:
                #return Qt.AlignLeft| Qt.AlignVCenter
        return super(CursorItem,self).data(role)
    


def localQuery(conn,info,iters=None):
    sqlContext = setLocalQuery(conn,info,iters=None)
    sqls = sqlContext['sqls'] #solo por compatibilidad
    return getCursor(conn,sqls,LIMIT=1000)


class SortProxy(QSortFilterProxyModel):
    def lessThan(self, left, right):
        leftData = left.data(Qt.EditRole)
        rightData = right.data(Qt.EditRole)
        try:
            return float(leftData) < float(rightData)
        except (ValueError, TypeError):
            pass
        return leftData < rightData
    
class TableBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None,iters=0):
        super(TableBrowserWin, self).__init__()
        self.view = TableBrowser(confName,schema,table,pdataDict,iters)
        if DEBUG:
            print('inicializacion completa')
        ##CHANGE here
    
        self.querySplitter = QSplitter(Qt.Horizontal)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.view)
        self.setCentralWidget(self.querySplitter)
               
        self.setWindowTitle("Visualizador de base de datos")

class TableBrowser(QTableView):
    """
    """
    def __init__(self,confName=None,schema=None,table=None,pdataDict=None,iters=0):
        super(TableBrowser, self).__init__()
        #self.view = self # sinomimo para no tener que tocar codigo mas abajo
        self.baseModel = CursorItemModel()
        self.setupModel(confName,schema,table,pdataDict,iters)
        self.setupView()
    
    @waiting_effects
    def setupModel(self,confName,schema,table,pdataDict,iters,pFilter=None): 
        if isinstance(pdataDict,DataDict):
            dataDict = pdataDict
        else:
            dataDict=DataDict(conName=confName,schema=schema,table=table,iters=iters) #iters todavia no procesamos
        
        #if not dataDict.getConnByName(confName):
            #print('Salimos por ausencia de diccionario')
            #exit()
            
        self.localContext = (dataDict,confName,schema,table,iters)    
        if not confName or confName == '':
            return
        
        self.tableInfo = TableInfo(dataDict,confName=confName,schemaName=schema,tableName=table,maxlevel=iters)
        sqlContext = self.tableInfo.prepareBulkSql(pFilter)
        self.baseModel.recordStructure = []

        for  idx,fld in enumerate(sqlContext['fields']):
            self.baseModel.recordStructure.append({'name':fld,'format':sqlContext['formats'][idx]})
        sqls = sqlContext['sqls'] 
        cabeceras = [ fld for fld in sqlContext['fields']]
        self.baseModel.setHorizontalHeaderLabels(cabeceras)

        cursor = getCursor(dataDict.conn[confName],sqls,LIMIT=1000)
        for row in cursor:
            modelRow = [ CursorItem(str(fld)) for fld in row ]
            self.baseModel.appendRow(modelRow)
        cursor = [] #operacion de limpieza, por si las mac-flies
    
    def setupView(self):
        #        self.view = QTableView(self)
        # aqui por coherencia --es un tema de presentacion
        sortProxy = SortProxy()
        sortProxy.setSourceModel(self.baseModel)
        self.setModel(sortProxy)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)
        self.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(self.openContextMenu)

        self.doubleClicked.connect(self.test)

        #for m in range(self.baseModel.columnCount()):
            #self.resizeColumnToContents(m)
        self.verticalHeader().hide()
        self.setSortingEnabled(True)  
        self.setAlternatingRowColors(True)
        #self.sortByColumn(0, Qt.AscendingOrder)
        self.areHidden = False
        self.areFiltered = False
  
    
    @waiting_effects
    @model_change_control()
    def loadData(self, pconfName=None,pschema=None,ptable=None,pdataDict=None,piters=1,pFilter=None):
        (dataDict,confName,schema,table,iters) = defaultFromContext(self.localContext,*(pdataDict,pconfName,pschema,ptable,piters))
        #self.baseModel.beginResetModel()
        self.baseModel.clear()
        self.setupModel(confName,schema,table,dataDict,iters,pFilter)
        #self.baseModel.endResetModel()
        for m in range(self.baseModel.columnCount()):
            self.resizeColumnToContents(m)
    
    def openContextMenu(self,position):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            columna = index.column()
            fila    = index.row()
        else:
            columna=self.horizontalHeader().logicalIndexAt(position)
            fila = -1
        
        menu = QMenu()
        self.menuActions = []
        self.menuActions.append(menu.addAction("Filter query",self.filterQuery))
        if fila != -1:
            self.menuActions.append(menu.addAction("Filter query (pick this value)",lambda a=index:self.filterQueryPick(a)))
        if self.areFiltered:
            self.menuActions.append(menu.addAction("remove Filter",self.filterRemove))
        self.menuActions.append(menu.addSeparator())
        self.menuActions.append(menu.addAction("HideColumn",lambda a = columna:self.hideColumn(a)))
        if self.areHidden:
            self.menuActions.append(menu.addAction("Show hidden columns",self.unhideColumns))
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def hideColumn(self,pos):
        self.setColumnHidden(pos,True)
        self.areHidden = True
        
    def unhideColumns(self):
        for k in range(self.baseModel.columnCount()): #TableView no tiene colimn count, pero si el modelo)
            if self.isColumnHidden(k):
                self.showColumn(k)
        self.areHidden = False
     

    def filterRemove(self):
        self.areFiltered = False
        self.loadData()
        pass
    

    def filterQuery(self):
        driver=self.localContext[0].conn[self.localContext[1]].dialect.name
        self.areFiltered = True
        filterDlg = filterDialog(self.baseModel.recordStructure,self,driver=driver)
        if filterDlg.exec_():
            self.loadData(pFilter=filterDlg.result)


    def filterQueryPick(self,index):
        """
            index es QModelIndex
            El enredo de codigo es cuando tenemos un sort proxy y entonces los indices no
            cuadran con los del modelo base y hay que hacer la traduccion esa ...
            Eso si, con columnas ocultas funciona
        """
        row = index.row()
        column = index.column()
        field = self.baseModel.headerData(column, Qt.Horizontal)
        valueIndex = self.model().mapToSource(QModelIndex(index))
        value = self.baseModel.itemFromIndex(valueIndex).text()
        # es la unica manera de encontrar el formato
        for item in  self.baseModel.recordStructure:
            if item['name'] == field:
                formato = item['format']
                break
        #TODO esto deberia sacarse con lo del dialogo
        qfmt = 't'     
        if formato in ('entero','numerico'):
            qfmt = 'n'
        elif formato in ('fecha','fechahora','hora'):
            qfmt = 'f'
        elif formato in ('booleano'):
            qfmt = 'n' #me parece 
        pfilter = searchConstructor('where',{'where':((field,'=',value,qfmt),)})
        self.areFiltered = True
        self.loadData(pFilter=pfilter)
        
        pass 
    
    def test(self):
        return
    
   
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    window = TableBrowserWin('Pagila','public','rental',iters=1)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
