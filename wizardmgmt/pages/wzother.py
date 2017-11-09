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


