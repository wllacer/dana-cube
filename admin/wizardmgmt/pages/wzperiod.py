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

def defPeriodItemComboBox(wP,k):
    # para que coja valores distintos de k en cada ejecucion !!???
    wP.formFechaLabel[k] = QLabel("Formato del {}er nivel:".format(k))
    wP.formFechaCombo[k] = QComboBox()
    if k == 0:
        wP.formFechaCombo[k].addItems(wP.fmtFecha[k:])
    else:
        wP.formFechaCombo[k].addItems(['',] + wP.fmtFecha[k:])
    wP.formFechaCombo[k].setCurrentIndex(0)
    wP.formFechaLabel[k].setBuddy(wP.formFechaCombo[k])
    wP.formFechaCombo[k].currentIndexChanged.connect(lambda:periodSeleccion(wP,k))

def periodSeleccion(wP,idx):
    #TODO sería mas interesante pasar tambien el valor, pero sigo sin acertar
    if idx < 0:
        return 
    # que hemos cambiado ?
    valor = wP.formFechaCombo[idx].currentText()
    if valor == '':
        if idx != 0:
            posActual = wP.fmtFecha.index(wP.formFechaCombo[idx -1].currentText())+1
        else:
            posActual = 0
    else:
        posActual = wP.fmtFecha.index(valor)
    
    for k in range(idx +1,wP.maxTImeLevel):
        j = k - idx
        #if posActual >= (wP.formFechaCombo[idx].count() -1):
        if len(wP.fmtFecha[posActual + j:]) == 0:
            wP.formFechaLabel[k].hide()
            wP.formFechaCombo[k].hide()
        else:
            wP.formFechaCombo[k].blockSignals(True)  #no veas el loop en el que entra si no
            if not wP.formFechaCombo[k].isVisible():
                wP.formFechaLabel[k].show() #por lo de arriba
                wP.formFechaCombo[k].show()
            wP.formFechaCombo[k].clear()
            wP.formFechaCombo[k].addItems(['',] + wP.fmtFecha[posActual + j :])
            wP.formFechaCombo[k].blockSignals(False)  

def periodForm(wP):
    wP.fmtFecha = [ item[1] for item in FECHADOR ]
    wP.fmtFechaCode = [ item[0] for item in FECHADOR ]
    wP.maxTImeLevel = 4  
    wP.formFechaLabel = [None for k in range(wP.maxTImeLevel)]
    wP.formFechaCombo = [None for k in range(wP.maxTImeLevel)]
    
    for k in range(wP.maxTImeLevel):
        defPeriodItemComboBox(wP,k)

    meatLayout = QGridLayout()
    for k in range(wP.maxTImeLevel):
        meatLayout.addWidget(wP.formFechaLabel[k],k,0)
        meatLayout.addWidget(wP.formFechaCombo[k],k,1)
    
    return meatLayout
    
def periodFormLoad(wP,dataContext):
    mascara = ''
    if dataContext.get('mask'):
        mascara = dataContext['mask']
    elif dataContext.get('type'):
        mascara = dataContext['type']
    for k,letra in enumerate(mascara):
        wP.formFechaCombo[k].setCurrentIndex(wP.fmtFechaCode.index(letra))
        periodSeleccion(wP,k)
    wP.iterator = wP.wizard().page(ixWzProdBase).iterations
    if isinstance(wP.wizard().diccionario,(list,tuple)):
        #varias entradas
        dataContext = wP.wizard().diccionario[wP.iterator -1]
    else:
        dataContext = wP.wizard().diccionario
    pass

def periodFormValidate(wP,dataContext):
    mask = ''
    for k in range(wP.maxTImeLevel):
        if wP.formFechaCombo[k].currentText() != '':
            idx = wP.fmtFecha.index(wP.formFechaCombo[k].currentText())
            mask += wP.fmtFechaCode[idx]
        else:
            break
    if mask != '':
        dataContext['mask'] = mask
    if dataContext.get('type'):
        del dataContext['type']
            
    return True

class WzTime(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzTime,self).__init__(parent)
        
        self.setFinalPage(True)
        
        self.setTitle("Guía tipo fecha")
        self.setSubTitle(""" Introduzca la jerarquía de criteros temporales que desea  """)

        
        self.setLayout(periodForm(self))
    
    def initializePage(self):
        #TODO no inicializa si no esta en la regla de produccion
        base = self.wizard().page(ixWzProdBase) 
        if not base:
            self.iterator = -1
        else:
            self.iterator = self.wizard().page(ixWzProdBase).iterations

        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        
        periodFormLoad(self,self.midict)
    
    def nextId(self):
        return -1

    def validatePage(self):
        if not periodFormValidate(self,self.midict):
            return False

            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True


