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

  
from admin.tablebrowse import *

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

def caseEditorForm(wP):
    #FIXME no admite mandatory
    wP.editArea = QPlainTextEdit()
    meatLayout = QGridLayout()
    meatLayout.addWidget(wP.editArea,0,0,1,0)
    return meatLayout

def caseEditorFormLoad(wP,dataContext):
    if wP.wizard().obj.type() not in TYPE_EDIT :
        caseStmt = dataContext.get('case_sql')
    else:
        caseStmt = dataContext
        
    if isinstance(caseStmt,(list,tuple)):
        wP.editArea.setPlainText('\n'.join(caseStmt))
    else:    
        wP.editArea.setPlainText(caseStmt)
    pass

def caseEditorFormValidate(wP,dataContext):
    texto = wP.editArea.document().toPlainText()
    if isinstance(dataContext,dict):
        area = dataContext.get('case_sql')
    else:
        area = dataContext
        
    if texto and texto.strip() != '':
        area.clear()
        area += texto.split('\n')
    elif area is not None: #dataContext is not None: 
        area.clear()
        
    return True

class WzRowEditor(QWizardPage):
    def __init__(self,parent=None,cache=None):
        #TODO hay que buscar/sustituir nombres de campos
        # o como alternativa presentar como pares when / then
        super(WzRowEditor,self).__init__(parent)
        
        self.setFinalPage(True)

        self.setTitle("Definicion de texto libre")
        self.setSubTitle(""" Introduzca el codigo SQL que desea utilizar para agrupar.
        Recuerde sustituir el nombre del campo guia por $$1 """)
        
        self.setLayout(caseEditorForm(self))
    
    def initializePage(self):
        self.iterator = -1
        if self.wizard().obj.type() not in TYPE_EDIT :
            self.iterator = self.wizard().page(ixWzProdBase).iterations
            if isinstance(self.wizard().diccionario,(list,tuple)):
                #varias entradas
                self.midict = self.wizard().diccionario[self.iterator -1]
            else:
                self.midict = self.wizard().diccionario
        else:
            self.midict = self.wizard().diccionario
            
        caseEditorFormLoad(self,self.midict)
        
    def nextId(self):
        return -1
    def validatePage(self):
        
        if not caseEditorFormValidate(self,self.midict):
            return False
        
        if self.iterator == -1:
            return True
            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
