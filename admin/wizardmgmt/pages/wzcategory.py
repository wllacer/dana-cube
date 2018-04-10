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

def catAddLines(wP,numLines):
    count = wP.catSheet.rowCount()
    for k in range(numLines):
        wP.catSheet.insertRow(count+k)
        wP.catSheet.addRow(count+k)
    wP.catSheet.setCurrentCell(count,0)

def categoriesForm(wP):
    Formatos = [ item[1] for item in ENUM_FORMAT ]

    catResultFormatLabel = QLabel("Formato del &Resultado:")
    wP.catResultFormatCombo = QComboBox()
    wP.catResultFormatCombo.addItems(Formatos)
    wP.catResultFormatCombo.setCurrentIndex(0)
    catResultFormatLabel.setBuddy(wP.catResultFormatCombo)

    catValueFormatLabel = QLabel("Formato de los &Valores:")
    wP.catValueFormatCombo = QComboBox()
    wP.catValueFormatCombo.addItems(Formatos)
    catValueFormatLabel.setBuddy(wP.catValueFormatCombo)
    
    #OJO notar que su posicion es posterior, pero lo necesito para cargar valor
    wP.catResultDefaultLabel = QLabel("Resultado por &Defecto:")
    wP.catResultDefaultLine = QLineEdit()
    wP.catResultDefaultLabel.setBuddy(wP.catResultDefaultLine)

    wP.catContext=[]
    wP.catContext.append(('categoria','condicion','valores'))
    wP.catContext.append((QLineEdit,None,None))
    wP.catContext.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
    wP.catContext.append((QLineEdit,None,None))
    wP.catNumRows=5
    wP.catData = None
    wP.catSheet = WDataSheet(wP.catContext,wP.catNumRows)
    #wP.catSheet.fill(wP.catData)
    wP.simpleContext=(
        ('categoria',QLineEdit,None,None),
        ('condicion',QComboBox,None,tuple(LOGICAL_OPERATOR)),
        ('valores',QLineEdit,None,None),
        )
    wP.catSimpleSheet = WPropertySheet(wP.simpleContext,wP.catData)
    wP.catSimpleSheet.hide()


    meatLayout = QGridLayout()
    meatLayout.addWidget(catValueFormatLabel,0,0)
    meatLayout.addWidget(wP.catValueFormatCombo,0,1)
    meatLayout.addWidget(catResultFormatLabel,1,0)
    meatLayout.addWidget(wP.catResultFormatCombo,1,1)
    meatLayout.addWidget(wP.catSheet, 2, 0, 1, 2)
    meatLayout.addWidget(wP.catSimpleSheet, 2, 0, 1, 3)
    meatLayout.addWidget(wP.catResultDefaultLabel,8,0)
    meatLayout.addWidget(wP.catResultDefaultLine,8,1)    
    
    return meatLayout

def categoriesFormLoad(wP,dataContext):
    obj = wP.wizard().obj
    if obj.type() == 'prod':
        if dataContext.get('fmt'):
            wP.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(dataContext['fmt']))
        if dataContext.get('enum_fmt'): #es el formato del campo origen
            wP.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(dataContext['enum_fmt']))

    elif obj.type() == 'categories':
        if obj.text() == obj.type() :  #las categorias al completo
            pai = wP.wizard().obj.parent()
        else:
            pai = wP.wizard().obj.parent().parent()  
            wP.catSheet.hide()
            if dataContext.get('default'):
                pass
            else:
                wP.catSimpleSheet.show()
                wP.catResultDefaultLabel.hide()
                wP.catResultDefaultLine.hide()
                
        fmtObj = pai.getChildrenByName('fmt')
        if not fmtObj:
            fmt = 'txt'
        else:
            fmt = fmtObj.getColumnData(1)
        enum_fmtObj = pai.getChildrenByName('enum_fmt')
        if not enum_fmtObj:
            enum_fmt = 'txt'
        else:
            enum_fmt = enum_fmtObj.getColumnData(1)
            
        wP.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(fmt))
        wP.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(enum_fmt))
        wP.catResultFormatCombo.setEnabled(False)
        wP.catValueFormatCombo.setEnabled(False)

    wP.catData = [] #'categoria','condicion','valores'  || 'result','condition','values'
    if dataContext.get('categories'): #usa sheet
        lista = dataContext['categories']
        for entry in lista:
            if entry.get('default'):
                wP.catResultDefaultLine.setText(entry['default'])
                continue
            tmp = [ None for i in range(3) ]
            tmp[0] = entry['result']
            tmp[1] = LOGICAL_OPERATOR.index(entry['condition'])
            tmp[2] = norm2String(entry['values'])
            wP.catData.append(tmp)
        
        if len(wP.catData) > wP.catNumRows:
            diff = len(wP.catData) - wP.catNumRows
            catAddLines(wP,diff)
    
        wP.catSheet.fill(wP.catData)

    else:
        entry = dataContext
        if entry.get('default'):
            wP.catResultDefaultLine.setText(entry['default'])
        else:
            for k,clave in enumerate(('result','condition','values')):
                if wP.simpleContext[k][1] == QComboBox:
                    wP.catSimpleSheet.set(k,0,wP.simpleContext[k][3].index(dataContext.get(clave,'in')))
                wP.catSimpleSheet.set(k,0,norm2String(dataContext.get(clave)))
    
        
def categoriesFormValidate(wP,dataContext):
        resultado = wP.catSheet.values()
        obj = wP.wizard().obj
        if obj.type() in ('prod','guides'): # cuando la llamada es indirecta
            formato = ENUM_FORMAT[wP.catResultFormatCombo.currentIndex()][0]
            enumFmt = ENUM_FORMAT[wP.catValueFormatCombo.currentIndex()][0]
            
            if dataContext.get('fmt') or formato != 'txt':
                dataContext['fmt'] = formato
            if dataContext.get('enum_fmt') or formato != enumFmt:
                dataContext['enum_fmt'] = enumFmt
            if dataContext.get('categories'):      
                dataContext['categories'].clear()
            else:
                dataContext['categories'] = []
            resultado = wP.catSheet.values()
            for entry in resultado:
                if entry[0] == '' or entry[2] == '':
                    continue
                dataContext['categories'].append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
            
            if wP.catResultDefaultLine.text() != '':
                dataContext['categories'].insert(0,{'default':wP.catResultDefaultLine.text()})

        elif obj.type() == 'categories':
            if obj.text() == obj.type():  #las categorias al completo
                lista_categ = wP.wizard().diccionario
                lista_categ.clear()
                for entry in resultado:
                    if entry[0] == '':
                        continue
                    lista_categ.append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
                
                if wP.catResultDefaultLine.text() != '':
                    lista_categ.insert(0,{'default':wP.catResultDefaultLine.text()})

            else:
                # FIXME no procesa bien el default
                dataContext.clear()
                if wP.catResultDefaultLine.text() != '':
                    dataContext = {'default':wP.catResultDefaultLine.text()}
                    return True
                values = wP.catSimpleSheet.values()
                for k,clave in enumerate(('result','condition','values')):
                    if wP.catContext[k][1] == QComboBox:
                        try:
                            dataContext[clave] = wP.catContext[k][3][values[k]]
                        except IndexError:
                            dataContext[clave] = wP.catSheet.cellWidget(k,0).getCurrentText()
                    else:
                        dataContext[clave] = values[k]
                        print(dataContext,wP.wizard().diccionario)


        return True

class WzCategory(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzCategory,self).__init__(parent)
        
        self.setFinalPage(True)
                
        self.setTitle("Definicion por categorias")
        self.setSubTitle(""" Introduzca la agrupación de valores que constityen cada categoria  """)

        meatLayout = categoriesForm(self)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        base = self.wizard().page(ixWzProdBase) 
        if not base:
            self.iterator = -1
        else:
            self.iterator = self.wizard().page(ixWzProdBase).iterations
        
        obj = self.wizard().obj
        if obj.type() == 'prod': # cuando la llamada es indirecta
            if obj.text() == obj.type():
                self.midict = self.wizard().diccionario[self.iterator - 1]
            else:
                self.midict = self.wizard().diccionario
        elif obj.type() == 'categories':
            if obj.text() == obj.type() :  #las categorias al completo
                self.midict = {'categories':self.wizard().diccionario}
            else:
                self.midict = self.wizard().diccionario
    
        categoriesFormLoad(self,self.midict)
        
    def nextId(self):
        return -1
    
    def validatePage(self):        

        if not categoriesFormValidate(self,self.midict):
            return False
        if self.iterator == -1:
            return True
            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False

        return True
    
