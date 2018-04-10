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


def domainForm(wP):
    domainTableLabel = QLabel("&Tabla origen:")
    wP.domainTableCombo = QComboBox()
    #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
    #                     Use a null value in combos if mandatory
    wP.domainTableCombo.addItems(wP.listOfTables)
    wP.domainTableCombo.setCurrentIndex(0)
    domainTableLabel.setBuddy(wP.domainTableCombo)
    wP.domainTableCombo.setStyleSheet("background-color:khaki;")

    domainFilterLabel = QLabel("&Filtro:")
    wP.domainFilterLE = QLineEdit()
    domainFilterLabel.setBuddy(wP.domainFilterLE)
    

    domainCodeLabel = QLabel("&Clave de enlace:")
    wP.domainCodeList = WMultiCombo()
    domainCodeLabel.setBuddy(wP.domainCodeList)
    wP.domainCodeList.setStyleSheet("background-color:khaki;")

    domainDescLabel = QLabel("&Textos desciptivos:")
    wP.domainDescList = WMultiCombo()
    domainDescLabel.setBuddy(wP.domainDescList)

    meatLayout = QGridLayout()
    meatLayout.addWidget(domainTableLabel,0,0)
    meatLayout.addWidget(wP.domainTableCombo,0,1)
    meatLayout.addWidget(domainCodeLabel,1,0)
    meatLayout.addWidget(wP.domainCodeList,1,1)
    meatLayout.addWidget(domainDescLabel,2,0)
    meatLayout.addWidget(wP.domainDescList,2,1)
    meatLayout.addWidget(domainFilterLabel,3,0)
    meatLayout.addWidget(wP.domainFilterLE,3,1)

    return meatLayout
def domainFormLoad(wP,dataContext):
    setAddComboElem(dataContext.get('table'),
                    wP.domainTableCombo,
                    wP.listOfTablesCode,wP.listOfTables)
    # los elementos vienen ahora
    #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
    wP.domainCodeList.set(norm2String(dataContext.get('code')))
    wP.domainDescList.set(norm2String(dataContext.get('desc')))

    if dataContext.get('filter'):
        wP.domainFilterLE.setText(dataContext['filter'])
    if dataContext.get('grouped by'):
        #TODO TODO
        pass
    
def domainFormValidate(wP,dataContext):
    #if wP.domainTableCombo.currentText() == '':
        #wP.domainTableCombo.setFocus()
        #return False
    ##TODO aqui deberia verificarse que el numero corresponde al numero de elementos de la regla de prod.
    #if len(wP.domainCodeList.selectedItems()) == 0:
        #wP.domainCodeList.setFocus()
        #return False
    tabidx =wP.domainTableCombo.currentIndex()
    if tabidx < 1:
        dataContext = {}
        return True
    if len(wP.domainCodeList.selectedItems()) == 0:
        wP.domainCodeList.setFocus()
        return False
    dataContext['table'] = wP.listOfTablesCode[tabidx]    
    dataContext['code'] = norm2List(wP.domainCodeList.get())
    dataContext['desc'] = norm2List(wP.domainDescList.get())
    dataContext['filter'] = wP.domainFilterLE.text()
         

    return True
class WzDomain(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzDomain,self).__init__(parent)

        self.setFinalPage(True)
        
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        
        self.setTitle("Dominio de definición")
        self.setSubTitle(""" Defina el dominio con el que creará la guía  """)
        
        self.setLayout(domainForm(self))
        self.domainTableCombo.currentIndexChanged[int].connect(self.domainTablaElegida)
        
        
    
    def initializePage(self):

        self.midict = self.wizard().diccionario
        domain = self.midict
        domainFormLoad(self,domain)


    def nextId(self):
        return -1

    def validatePage(self):
        # verificar que los campos obligatorios estan rellenos
        if self.domainTableCombo.currentText() == '':
            self.domainTableCombo.setFocus()
            return False
        #TODO aqui deberia verificarse que el numero corresponde al numero de elementos de la regla de prod.
        if len(self.domainCodeList.selectedItems()) == 0:
            self.domainCodeList.setFocus()
            return False
        return domainFormValidate(self,self.midict)

            
    def domainTablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTablesCode[idx]
        self.listOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.listOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.domainCodeList.load(self.listOfFieldsCode,self.listOfFields)
        self.domainDescList.load(self.listOfFieldsCode,self.listOfFields)

