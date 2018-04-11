#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from pprint import pprint

import datetime
import argparse

#from base.datadict import *    

from PyQt5.QtCore import  Qt,QModelIndex
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
            if isinstance(baseData,str) and len(baseData) > 0 and baseData[0] == '=':
                baseData =  self.ss[baseData]
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
        super(CursorItem, self).__init__(*args)
    

    
class QueryTab(QWidget):
    #def __init__(self,conn,confName,holder=None,parent=None):
    """
    confName no usado
    
    """
    def __init__(self,conn,**kwparms): #holder=None,script=None,parent=None):
        super(QueryTab,self).__init__(kwparms.get('parent',None))
        self.conn = conn
        self.holder = kwparms.get('holder',None)
        self.script = kwparms.get('script',None)
        self.fileName = None
        self.browser = QTableView()
        self.browser.setSortingEnabled(True)  
        self.browser.setAlternatingRowColors(True)

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
            cursor = getCursorLim(self.conn,sqlString,LIMIT=1000)
        except Exception as e:
            if cursor is not None:
                cursor.close()
            self.msgLine.show()
            self.msgLine.setText(norm2String(e.orig.args))
            return
            
        self.baseModel = CursorItemModel()
        self.baseModel.setHorizontalHeaderLabels(cursor.keys())
        for row in cursor:
            modelRow = [ CursorItem(str(fld)) for fld in row ]
            self.baseModel.appendRow(modelRow)
        self.browser.setModel(self.baseModel)
        cursor.close() #INNECESARIO pero recomendable

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
            #FIXME fugly
            #pos = self.holder.tabSesiones.currentWidget().tabQueries.currentIndex()
            #self.holder.tabSesiones.currentWidget().tabQueries.setTabText(pos,filename)
            
    def writeQuery(self,saveAs=False):
        if not self.sqlEdit.document().isModified():
            return
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
        with open(self.fileName,"w") as file:
            file.write(self.sqlEdit.document().toPlainText())
            
        #if self.fileName is None or saveAs is True:
            #self.fileName = filename
            ##FIXME fugly
            #pos = self.holder.tabSesiones.currentWidget().tabQueries.currentIndex()
            #self.holder.tabSesiones.currentWidget().tabQueries.setTabText(pos,filename)
    
        self.sqlEdit.document().setModified(False)
    def reformat(self):
        sqlString = self.sqlEdit.document().toPlainText()
        self.sqlEdit.setText(queryFormat(sqlString))
  
    def close(self):
        #TODO salvar si es fichero
        if self.fileName is not None:
            pass
        self.conn.close()
        super().close()
