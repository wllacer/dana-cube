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
    

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *

from wizardmgmt.guihelper import *

from widgets import *    
from util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

class WzFieldList(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzFieldList,self).__init__(parent)
        fieldList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in fieldList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass
    def validatePage(self):
        return True
   
class WzGuideList(QWizardPage):
    def __init__(self,parent=None):
        super(WzGuideList,self).__init__(parent)
        guideList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in guideList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass
    def validatePage(self):
        return True

class uno(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super().__init__(parent)
        prodNameLabel = QLabel("Nombre ...")
        self.prodNameLE = QLineEdit()
        
        dataLabel   = QLabel("Especifique los datos que desea agrupar")
        domainLabel = QLabel("Especifique el dominio de de valores de la guia")
 
        self.iterations = 0
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['Tabla ...',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.datalistOfFields = []
        self.datalistOfFieldsCode = []
        self.baseIdx = self.listOfTablesCode.index(cache['tabla_ref'])

        self.dataTableCombo = QComboBox()
        self.dataTableCombo.addItems(self.listOfTables)
        self.dataFieldCombo = WMultiCombo()
        
        
        self.linkCheck = QCheckBox("¿Requiere de un enlace externo?")

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.dataTableCombo,0,0)
        meatLayout.addWidget(self.dataFieldCombo,0,1)
        meatLayout.addWidget(self.linkCheck,1,1)
        
        self.setLayout(meatLayout)
        
        self.dataTableCombo.currentIndexChanged[int].connect(self.amaga)
        self.linkCheck.stateChanged.connect(self.dispara)
      
    def initializePage(self):
        self.setFinalPage(True)
        self.completeChanged.emit()
        
    def dispara(self,idx):
        if idx == 2:
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)
            
        self.completeChanged.emit()
    
    def amaga(self,idx):
        if idx < 1:
            return
        if idx != self.baseIdx:
            self.linkCheck.setChecked(True)
      
    def nextId(self):
        if self.linkCheck.isChecked():
            return ixWzLink
        else:
            return -1
        
class dos(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super().__init__(parent)

