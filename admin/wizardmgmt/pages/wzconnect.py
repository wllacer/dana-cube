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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox
    

import base.config as config

from support.util.record_functions import *

from admin.cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from base.cubetree import *
from admin.cubemgmt.cubeTypes import *

from admin.wizardmgmt.guihelper import *

from support.gui.widgets import *    
from support.util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

class WzConnect(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzConnect,self).__init__(parent)
        
        self.setTitle("Definicion conexión")
        self.setSubTitle(""" Defina los parámetros de conexion con la base de datos """)

        self.cache = cache
        self.cube = cube
        nombre = None
        data = None
        self.midict = None
        self.context = [
                #['Nombre',QLineEdit,{'setReadOnly':True} if nombre is not None else None,None,],
                ## driver
                ["Driver ",QComboBox,None,DRIVERS,],
                ["DataBase Name",QLineEdit,None,None,],
                #["Schema",QComboBox,None,None],
                ["Schema",QLineEdit,None,None],
                ["Host",QLineEdit,None,None,],
                ["User",QLineEdit,None,None,],
                ["Password",QLineEdit,{'setEchoMode':QLineEdit.Password},None,],
                ["Port",QLineEdit,None,None,],
                ["Debug",QCheckBox,None,None,]
            ]
        self.sheet=WPropertySheet(self.context,data)
        self.sheet.cellWidget(0,0).currentIndexChanged[int].connect(self.driverChanged)
        self.sheet.cellWidget(1,0).textChanged.connect(self.dbChanged)
        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)

        meatLayout = QVBoxLayout()
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
        
        self.setLayout(meatLayout)

    def initializePage(self):
        if 'connect' in self.wizard().diccionario:
            self.midict = self.wizard().diccionario['connect']
        else:
            self.midict = self.wizard().diccionario
        for k,clave in enumerate(('driver','dbname','schema','dbhost','dbuser','dbpass','port','debug')):
            if clave == 'schema':
                self.sheet.set(2,0,self.cache['schema'])
                #self.sheet.cellWidget(2,0).clear()
                #confName = self.cache['confName']
                #conn = self.cube.dataDict.getConnByName(confName)
                #esquemas = [ item.text() for item in conn.listChildren() ]
                #self.context[2][3] = esquemas
                #self.sheet.cellWidget(2,0).addItems(esquemas)
                #try:
                    #self.sheet.set(2,0,self.context[2][3].index(self.cache['schema']))
                #except ValueError:
                    #esquemas.append(self.cache['schema'])
                    #self.sheet.cellWidget(2,0).addItem(self.cache['esquema'])
                    #self.sheet.set(2,0,esquemas.rowCount() -1)
                    #self.sheet.cellWidget(2,0).setStyleSheet("background-color:yellow;")
                #continue
            elif self.context[k][1] == QComboBox:
                self.sheet.set(k,0,self.context[k][3].index(self.midict.get(clave)))
            else:
                self.sheet.set(k,0,self.midict.get(clave))
        
    def validatePage(self):
        values = self.sheet.values()
        for k,clave in enumerate(('driver','dbname','schema','dbhost','dbuser','dbpass','port','debug')):
            if self.context[k][1] == QComboBox:
                try:
                    self.midict[clave] = self.context[k][3][values[k]]
                except IndexError:
                    self.midict[clave] = self.sheet.cellWidget(k,0).getCurrentText()
            else:
                self.midict[clave] = values[k]
        return True
    
    def driverChanged(self,idx):
        if DRIVERS[idx] == 'sqlite':
            self.sheet.set(2,0,None)
            for k in range(2,6):
                self.sheet.hideRow(k)
        else: #de momento no alterno nada
            for k in range(2,6):
                self.sheet.showRow(k)

    def dbChanged(self,idx):
        pass
