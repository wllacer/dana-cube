#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import os

from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QCheckBox,\
          QPushButton, QMessageBox, \
          QTableView, QSpinBox

from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError

from support.datalayer.access_layer import *
from support.util.record_functions import norm2String,dict2row, row2dict

from support.util.jsonmgr import *
from support.gui.widgets import WPropertySheet

import base.config as config

class directConnectDlg(QDialog):
    def __init__(self,configDict,parent=None):
        super(directConnectDlg,self).__init__(parent)
        if 'Conexiones' in configDict:
            self.confData = ambito = configDict['Conexiones']
        else:
            exit()

        self.listConnections = [ name for name in ambito]
        self.conn = None
        
        self.etiqueta = QLabel("Eliga una conexion")
        self.lista = QComboBox()
        self.lista.addItems(['Eliga una conexión',] + self.listConnections)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)       
        context = (
                ("Driver ",QComboBox,None,DRIVERS,),
                ("DataBase Name",QLineEdit,None,None,),
                ("Host",QLineEdit,None,None,),
                ("User",QLineEdit,None,None,),
                ("Password",QLineEdit,{'setEchoMode':QLineEdit.Password},None,),
                ("Port",QLineEdit,None,None,),
                ("Debug",QCheckBox,None,None,)
                )
        data =  [ None for k in range(len(context)) ]
        
        self.sheet=WPropertySheet(context,data)
        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)


        meatLayout = QGridLayout()
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonBox)
        
        meatLayout.addWidget(self.etiqueta,0,0)
        meatLayout.addWidget(self.lista,0,1)
        meatLayout.addWidget(self.sheet,1,0,6,2)
        meatLayout.addWidget(self.msgLine,7,0)
        meatLayout.addLayout(buttonLayout,8,0)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(382,382))
        self.setWindowTitle("Seleccione la conexión a utilizar")
        
        self.sheet.hide()
        self.buttonBox.hide()
        
        self.lista.currentIndexChanged[int].connect(self.selecConn)        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
    
    def selecConn(self,idx):
        if idx < 1:
            return
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        self.confName = self.lista.currentText()
        datos = dict2row(self.confData[self.confName],attr_list)
        datos[0]=DRIVERS.index(datos[0])
        for i in range(len(datos)):
            self.sheet.set(i,0,datos[i])
        self.sheet.show()
        self.buttonBox.show()

    def validate(self):
        datos = self.sheet.values()
        if datos[1] == '':
            self.sheet.cellWidget(1,0).setFocus()
            self.msgLine.setText('Base de datos es Obligatorio')
            return None
        self.msgLine.clear()
        return datos
    
    def accept(self):       
        self.msgLine.clear()
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        datos = self.validate()
        if datos is None:
            return
        if isinstance(datos[0],int):
            datos[0]=DRIVERS[datos[0]]
        conf = row2dict(datos,attr_list)
        try:
            if conf['driver'] == 'sqlite':
                if not os.path.isfile(datos[1]):
                    self.msgLine.setText('Fichero {} no existe'.format(datos[1]))
                    return
            conn = dbConnectAlch(conf)
        except Exception  as e:
            showConnectionError(datos[0],norm2String(e.orig.args))
            self.msgLine.setText('Error en la conexión')
            return
    
        self.conn = conn
        self.confInfo = conf
        
        QDialog.accept(self)
        
    def reject(self):
        if self.conn is not None:
            self.conn.close()
        QDialog.reject(self)
        
class SelectConnectionDlg(QDialog):
    def __init__(self,configDict,parent=None):
        super(SelectConnectionDlg,self).__init__(parent)
        if 'Conexiones' in configDict:
            ambito = configDict['Conexiones']
        else:
            ambito = configDict
        self.listConnections = [ name for name in ambito]
        self.conexion = None
        
        self.etiqueta = QLabel("Eliga una conexion")
        self.lista = QComboBox()
        self.lista.addItems(self.listConnections)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)       
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonBox)
        
        meatLayout.addWidget(self.etiqueta)
        meatLayout.addWidget(self.lista)
        meatLayout.addLayout(buttonLayout)

 
        self.setLayout(meatLayout)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def accept(self):
        self.conexion = self.lista.currentText()
        QDialog.accept(self)
        
        
class ConnectionSheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
    """
    def __init__(self,title,context,data,parent=None):   
        super(ConnectionSheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(context,data)
       
        actionButton = QPushButton('Test')
        actionButton.setDefault(True)
        
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)
        buttonBox.addButton(actionButton,QDialogButtonBox.ActionRole)

        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)
        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
        #formLayout.addLayout(meatLayout)        
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(382,382))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        actionButton.clicked.connect(self.test)
        
        self.setWindowTitle("Connection editor")
      
    def validate(self):
        datos = self.sheet.values()
        if datos[0] == '':
            self.sheet.cellWidget(0,0).setFocus()
            self.msgLine.setText('Nombre es Obligatorio')
            return None
        if datos[2] == '':
            self.sheet.cellWidget(2,0).setFocus()
            self.msgLine.setText('Base de datos es Obligatorio')
            return None
        self.msgLine.clear()
        return datos
    
    def test(self):       
        self.msgLine.clear()
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        datos = self.validate()
        if datos is None:
            return
        if isinstance(datos[1],int):
            datos[1]=DRIVERS[datos[1]]
        conf = row2dict(datos[1:],attr_list)
        try:
            if conf['driver'] == 'sqlite':
                if not os.path.isfile(datos[2]):
                    self.msgLine.setText('Fichero {} no existe'.format(datos[2]))
                    return
            else:
                conn = dbConnectAlch(conf)
                conn.close()
        except ( OperationalError, ProgrammingError)  as e:
            showConnectionError(datos[0],norm2String(e.orig.args))
            self.msgLine.setText('Error en la conexión')
            return
        self.msgLine.setText('Conexión validada correctamente')
        
    def accept(self):
        datos = self.validate()
        if datos is None:
            return
        self.msgLine.clear()
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.data[k] = valor
        QDialog.accept(self)

    
def showConnectionError(context,detailed_error):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Error en la conexion con {}".format(context))
    #msg.setInformativeText(detailed_error)
    msg.setWindowTitle("Error de Conexion")
    msg.setDetailedText(detailed_error)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()
