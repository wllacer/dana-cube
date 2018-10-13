#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Part of  Global Common modules by Werner Llácer (c) 2012-2018

As an integral part of a project distributed under an Open Source Licence, the licence of the proyect
Used as  standalone module or outside the scope of  a project valid according to the  previous paragraph, or when  in doubt, distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from pprint import pprint

import datetime
import argparse

#from base.datadict import *    

from PyQt5.QtCore import  Qt,QModelIndex, QSortFilterProxyModel, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMenu, QComboBox, QLabel, QTableView, QDockWidget, QTextEdit, QListView, QTabWidget, QSplitter, QVBoxLayout, QWidget, QGridLayout, QFileDialog

#from  sqlalchemy import create_engine,inspect,MetaData, types
#from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError


from support.util.numeros import fmtNumber,is_number,s2n               
from support.util.jsonmgr import load_cubo,getConfigFileName
from support.util.decorators import waiting_effects 
from support.util.record_functions import norm2String

from support.datalayer.access_layer import SYSTEM_SCHEMAS, getCursorLim
from support.datalayer.query_constructor import queryFormat
#from support.datalayer.conn_dialogs import directConnectDlg

import base.config as config

DEFAULT_FORMAT = dict(thousandsseparator=".",
                            decimalmarker=",",
                            decimalplaces=2,
                            rednegatives=False,
                            yellowoutliers=False)

class CursorItemModel(QStandardItemModel):
    def __init__(self,parent=None):
        super(CursorItemModel, self).__init__(parent)
        self.recordStructure = None
        
    def data(self,index,role):
        """
        Reimplementation of QStandardItemModel.data for the needs of danacube. It will be invoked when a view associated with the model is redrawn
        
        * Input parameters
            * __index__ a QIndexModel which identifies the item
            * __role__ which Qt.Role are we handling
            
        * Programming notes
        We define special actions for following cases
            * Qt.BackgroundRole. Color if the conditions in TreeFormat are met 
            * Qt.DisplayRole. Formats the numeric vector
        """
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        retorno = item.data(role)
        displayData = baseData = item.data(Qt.DisplayRole)
        if  role not in (Qt.DisplayRole, Qt.UserRole +2) and baseData and isinstance(baseData,str) and baseData[0] == '=':
            displayData = self.data(index,Qt.UserRole + 2)
            
        if role == Qt.TextAlignmentRole:
            if not baseData:
                return retorno
            if is_number(displayData):
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
            
        if role == Qt.BackgroundRole:
            if baseData is None:
                return retorno
            else:
                datos = baseData
                if datos is None or datos == '':
                    return  retorno
                if is_number(displayData):
                    datos = float(displayData)
                    if DEFAULT_FORMAT['rednegatives'] and datos < 0 :
                        retorno = QColor(Qt.red)
                    else:
                        return retorno
                else:
                    return retorno
            return retorno   
         
        elif role == Qt.DisplayRole:
            if not baseData or baseData == '':
                return None
            #if isinstance(baseData,str) and len(baseData) > 0 and baseData[0] == '=':
                #baseData =  self.ss[baseData]
            if is_number(baseData):
                text, sign = fmtNumber(s2n(baseData),DEFAULT_FORMAT)
                return '{}{}'.format(sign if sign == '-' else '',text)               
            else:
                return baseData
            
        elif role == Qt.UserRole + 2:  #es como el display pero sin formatos numericos            
            if not baseData or baseData == '':
                return None
            if isinstance(baseData,str) and len(baseData) > 0 and baseData[0] == '=':
                baseData =  self.ss[baseData]
                return baseData
            else:
                return baseData
        else:
            return item.data(role)

        
class CursorItem(QStandardItem):
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        if isinstance(args[0],str):
            super(CursorItem, self).__init__(*args)
        elif isinstance(args[0],(int,float)):
            super(CursorItem, self).__init__() #no enviar los datos. Valores altos > 10M probablemente provocan bug
            self.setData(args[0],Qt.DisplayRole)
        elif isinstance(args[0],(datetime.date,datetime.datetime)):
            super(CursorItem, self).__init__(str(args[0]))
        else:
            super(CursorItem, self).__init__()
            self.setData(str(args[0]),Qt.DisplayRole)

        
class SortProxy(QSortFilterProxyModel):
    def lessThan(self, left, right):
        leftData = left.data(Qt.EditRole)
        if not leftData:
            return True
        rightData = right.data(Qt.EditRole)
        if not rightData:
            return False
        try:
            return float(leftData) < float(rightData)
        except (ValueError, TypeError):
            pass
        return leftData < rightData
    
class QueryTab(QWidget):
    """
    
    """
    def __init__(self,conn,**kwparms): #holder=None,script=None,parent=None):
        super(QueryTab,self).__init__(kwparms.get('parent',None))
        self.limit = 1000
        self.conn = conn
        self.connClose = kwparms.get('connClose',False)
        self.holder = kwparms.get('holder',None)
        self.script = kwparms.get('script',None)
        self.fileName = None
        self.browser = QTableView()
        self.baseModel = None
        self.sqlEdit = QTextEdit()
        self.msgLine = QTextEdit()
        self.msgLine.setReadOnly(True)
        self.msgLine.setText("Bienvenido al query masta")
        
        split = QSplitter(Qt.Vertical)
        split.addWidget(self.sqlEdit)
        split.addWidget(self.browser)
        split.addWidget(self.msgLine)
        split.setSizes([50,250,25])
        #split.setRubberBand(1)
        if self.script:
            self.sqlEdit.setText(queryFormat(self.script))
            self.sqlEdit.hide()
        meatLayout = QVBoxLayout()
        meatLayout.addWidget(split)
        self.setLayout(meatLayout)

    def setupView(self):
        #        self.view = QTableView(self)
        # aqui por coherencia --es un tema de presentacion
        sortProxy = SortProxy()
        sortProxy.setSourceModel(self.baseModel)
        self.browser.setModel(sortProxy)
        
        self.browser.setContextMenuPolicy(Qt.CustomContextMenu)
        self.browser.customContextMenuRequested.connect(self.openContextMenu)

        #self.browser.doubleClicked.connect(self.browser.test)

        #for m in range(self.browser.baseModel.columnCount()):
            #self.browser.resizeColumnToContents(m)
        self.browser.verticalHeader().hide()
        self.browser.setSortingEnabled(True)  
        self.browser.setAlternatingRowColors(True)
        #self.sortByColumn(0, Qt.AscendingOrder)
        self.areHidden = False
        self.areFiltered = False
        self.filtro = None  #estas dos ultimas son redundantes, realmente

    @waiting_effects
    def execute(self):
        sqlString = self.sqlEdit.document().toPlainText()
        if len(sqlString) == 0:
            return 
        cursor = None

        self.msgLine.hide()
        self.msgLine.setText('')
        try:
            #TODO opcion para poner un limit
            cursor = getCursorLim(self.conn,sqlString,LIMIT=self.limit)
        except Exception as e:
            if cursor is not None:
                cursor.close()
            self.msgLine.show()
            #self.msgLine.setText(e)
            self.msgLine.setText(norm2String(e.args)+' '+sqlString)
            return

        if not self.baseModel:
            self.baseModel = CursorItemModel()
        else:
            self.baseModel.clear()
        self.setupView()

        self.baseModel.setHorizontalHeaderLabels(cursor.keys())
        idx = 0
        for row in cursor:
            #if idx == 0:
                #self.getDescription(row)                
            #modelRow = [ CursorItem(str(fld)) for fld in row ]
            modelRow = [ CursorItem(fld) for fld in row ]
            self.baseModel.appendRow(modelRow)
            idx += 1
        self.browser.setModel(self.baseModel)
        cursor.close() #INNECESARIO pero recomendable

    def getDescription(self,row):
        if not row:
            return 
        idx = 0
        desc = []
        for col in row:
            info = {}
            info['name'] = row.keys()[idx]
            info['pyformat'] = type(col)
            desc.append(info)
            idx += 1
        pprint(desc)
            
    def readQuery(self):
        #TODO y el contenido actual del script ?
        if self.fileName is not None and self.sqlEdit.document().isModified():
            #dialogo de confirmar el salvado de los datos
             pass
        filename,filter = QFileDialog.getOpenFileName(self,
                                                  caption="Nombre del fichero de comandos a editar",
                                                  directory="script",
                                                  filter = "sql (*.sql);; All files (*)",
                                                  initialFilter="sql (*.sql)",
                                                  )
        if filename:
            with open(filename,"r") as file:
                self.sqlEdit.document().setPlainText(file.read())
                self.sqlEdit.document().setModified(False)
            self.fileName = filename
        self.execute()
    def writeQuery(self,saveAs=False):
        """
        con el editor es necesario filtrar, 
        si se utiliza como widget de visualizacion utilizar saveQuery
        """
        if not self.sqlEdit.document().isModified():
            return
        self.saveQuery(saveAs)
    def saveQuery(self,saveAs=False):
        if self.fileName is None:
            filename,filter = QFileDialog.getSaveFileName(self,
                                                    caption="Salvar el script como",
                                                    directory="script",
                                                    filter = "sql (*.sql);; All files (*)",
                                                    initialFilter="sql (*.sql)",
                                                    )
            if filename:
                pass
            else:
                return

        elif saveAs:
            filename,filter = QFileDialog.getSaveFileName(self,"Save as",self.fileName)
            if filename:
                pass
            else:
                return
        else:
            filename = self.fileName
        with open(filename,"w") as file:
            file.write(self.sqlEdit.document().toPlainText())
        self.sqlEdit.document().setModified(False)
        
    def reformat(self):
        sqlString = self.sqlEdit.document().toPlainText()
        self.sqlEdit.setText(queryFormat(sqlString))
  
    def setLimit(self,limit):
        self.limit = limit
    def getLimit(self):
        return self.limit
    
    def openContextMenu(self,position):
        indexes = self.browser.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            columna = index.column()
            fila    = index.row()
        else:
            index = None
            columna=self.browser.horizontalHeader().logicalIndexAt(position)
            fila = -1
        
        self.menu = QMenu()
        self.menuActions = []
        self.addContextMenuActions(index,fila,columna)
        action = self.menu.exec_(self.browser.viewport().mapToGlobal(position))
    
    def addContextMenuActions(self,index,fila,columna):
        self.menu.addAction("HideColumn",lambda a = columna:self.hideColumn(a))
        if self.areHidden:
            self.menu.addAction("Show hidden columns",self.unhideColumns)
        if not self.holder:
            self.menu.addAction("save query",self.saveQuery)
        
    def hideColumn(self,pos):
        self.browser.setColumnHidden(pos,True)
        self.areHidden = True
        
    def unhideColumns(self):
        for k in range(self.baseModel.columnCount()): #TableView no tiene colimn count, pero si el modelo)
            if self.browser.isColumnHidden(k):
                self.browser.showColumn(k)
        self.areHidden = False
     
    def reconnect(self,newConn,connClose=False):
        if not newConn:
            return
        if self.conn and self.connClose:
            self.conn.close()
        if self.baseModel:
            self.baseModel.clear()
        else:
            self.baseModel = CursorItemModel()
        self.conn = newConn
        self.connClose = connClose
     
    def executeNewScript(self,script):
        self.sqlEdit.setText(queryFormat(script))
        self.execute()
        
    def close(self):
            #TODO salvar si es fichero
            if self.fileName is not None:
                pass
            if self.connClose:
                self.conn.close()
            super().close()
