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

from wizardmgmt.pages.wzcategory import *
from wizardmgmt.pages.wzdomain import *
from wizardmgmt.pages.wzperiod import *
from wizardmgmt.pages.wzrowedit import *

def setBaseFK(wP,entry,fromTable,toTable):
    claves = wP.cache['info'][fromTable].get('FK')
    if not claves:
        return 
    for fkey in claves:
        #FIXME si hay varias solo coge la primera
        if fkey.get('parent table') == toTable:
            base = norm2List(fkey.get('ref field'))
            dest = norm2List(fkey.get('parent field'))
            entry['clause'] = []
            for i in range(len(base)):  #mas vale que coincidan
                entry['clause'].append({'base_elem':base[i],'ref elem':dest[i]})
                break
            
def short2FullName(wP,file):
    if file not in wP.listOfTablesCode:
        try:
            idx = wP.listOfTables.index(file)
            return wP.listOfTablesCode(idx)
        except ValueError:
            return None
    else:
        return file
    pass
    



class WzProdBase(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzProdBase,self).__init__(parent)

        #self.setFinalPage(True)
        
        self.iterations = 0
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['Tabla ...',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.domainlistOfFields = []
        self.domainlistOfFieldsCode = []
        self.datalistOfFields = []
        self.datalistOfFieldsCode = []
        
        #self.setTitle("Dominio de definición")
        #self.setSubTitle(""" Defina el dominio con el que creará la guía  """)
        
        self.setTitle("Definición de la guía")
        self.setSubTitle(""" Introduzca la localización donde estan los valores por los que vamos a agrupar """)
        
        nombre = QLabel("&Nombre:")
        self.nombreLE = QLineEdit()
        nombre.setBuddy(self.nombreLE)
        
        clase = QLabel("&Clase")
        self.claseCB = QComboBox()
        self.claseCB.addItems([ elem[1] for elem in GUIDE_CLASS])
        self.claseCB.setCurrentIndex(0)
        clase.setBuddy(self.claseCB)

        self.prodTB = QTableWidget(5,1)
        self.prodTB.horizontalHeader().setStretchLastSection(True)  
        self.prodTB.setContextMenuPolicy(Qt.CustomContextMenu)
        self.prodTB.customContextMenuRequested.connect(self.openContextMenu)

        prodNameLabel = QLabel("Nombre ...")
        self.prodNameLE = QLineEdit()
        
        dataLabel   = QLabel("Especifique los datos que desea agrupar")
        domainLabel = QLabel("Especifique el dominio de de valores de la guia")
        
        self.dataTableCombo = QComboBox()
        self.dataTableCombo.addItems(self.listOfTables)
        self.dataFieldCombo = WMultiCombo()
        
        
        self.linkCheck = QCheckBox("¿Requiere de un enlace externo?")

        self.noneRB    = QRadioButton("Sólo dominio")
        self.catCtorRB = QRadioButton("Agrupado en Categorias")
        self.caseCtorRB = QRadioButton("Directamente via código SQL")
        self.dateCtorRB = QRadioButton("Agrupaciones de fechas")
        
        self.domainLayout = domainForm(self)
        
        groupBox = QGroupBox("Criterios de agrupacion manuales ")
        groupBoxLayout = QHBoxLayout()
        groupBoxLayout.addWidget(self.noneRB)
        groupBoxLayout.addWidget(self.catCtorRB)
        groupBoxLayout.addWidget(self.caseCtorRB)
        groupBoxLayout.addWidget(self.dateCtorRB)
        groupBox.setLayout(groupBoxLayout)

        #self.prodTB.currentCellChanged[int,int,int,int].connect(self.currentCellChanged)

        self.rowEditor = QWidget()
        self.rowEditor.setLayout(caseEditorForm(self))
        self.timeEditor = QWidget()
        self.timeEditor.setLayout(periodForm(self))
        self.categoryEditor = QWidget()
        self.categoryEditor.setLayout(categoriesForm(self))
        
                    
        self.Stack = QStackedWidget (self)
        self.Stack.addWidget(self.categoryEditor)
        self.Stack.addWidget (self.rowEditor)
        self.Stack.addWidget(self.timeEditor)
        
        meatLayout = QGridLayout()
        left = 0
        k = 0
        meatLayout.addWidget(nombre,k +0,left + 0)
        meatLayout.addWidget(self.nombreLE,k + 0,left + 1,1,2)
        meatLayout.addWidget(clase,k + 0,left + 3)
        meatLayout.addWidget(self.claseCB,k + 0,left + 4)
        
        meatLayout.addWidget(self.prodTB,left + 1,0,5,1)

        center = left +1
        k = 1
        meatLayout.addWidget(prodNameLabel,k,center + 0)
        meatLayout.addWidget(self.prodNameLE,k,center + 1)
        k = k + 1
        meatLayout.addWidget(dataLabel,k,center + 0,1,2)
        meatLayout.addWidget(self.dataTableCombo,k+1,center + 0)
        meatLayout.addWidget(self.dataFieldCombo,k+1,center + 1)
        meatLayout.addWidget(self.linkCheck,k+2,center + 1)
        k = k + 3
        meatLayout.addWidget(domainLabel,k,center + 0,1,2)
        meatLayout.addLayout(self.domainLayout,k +1,center + 0,1,2)
        k= k + 2
        self.setLayout(meatLayout)
        meatLayout.addWidget(groupBox,k,center + 0,1,2)
        
        right=center +2
        j=1
        meatLayout.addWidget(self.Stack,j,right,k-1,2)
        
        self.dataTableCombo.currentIndexChanged[int].connect(self.dataTablaElegida)
        self.domainTableCombo.currentIndexChanged[int].connect(self.domainTablaElegida)
        self.linkCheck.stateChanged.connect(self.estadoLink)
        self.catCtorRB.clicked.connect(self.setDetail)
        self.caseCtorRB.clicked.connect(self.setDetail)
        self.dateCtorRB.clicked.connect(self.setDetail)
        self.noneRB.clicked.connect(self.setDetail)
        
    def initializePage(self):

        self.setFinalPage(True)
        self.completeChanged.emit()

        self.iterator = 0
        obj = self.wizard().obj
        if obj.type() == 'guides':
            self.nombreLE.show()
            self.claseCB.show()
            self.prodTB.show()
        else:
            self.nombreLE.hide()
            self.claseCB.hide()
            if obj.type() != obj.text():
                self.prodTB.hide()
            else:
                self.prodTB.show()
            
         
        self.midict = self.wizard().diccionario        
        if obj.type() == 'guides':
            self.nombreLE.setText(self.midict.get('name',''))
            clase = self.midict.get('class','o')
            self.claseCB.setCurrentIndex([ elem[0] for elem in GUIDE_CLASS].index(clase))
            if clase == 'c':
                if self.midict.get('prod',[])[-1].get('categories'):
                    self.catCtorRB.setChecked(True)
                elif self.midict.get('prod',[])[-1].get('case_sql'):
                    self.caseCtorRB.setChecked(True)
                else:
                    self.catCtorRB.setChecked(True)
            elif clase == 'd':
                self.dateCtorRB.setChecked(True)
            self.setDetail()         


        if obj.type() == 'guides':
            if not self.midict.get('prod'):
                self.midict['prod']=[{},]
            self.listaProd = self.midict['prod']
        else :
            if isinstance(self.midict,(list,set,tuple)):
                self.listaProd = self.midict
            else:
                self.listaProd = [ self.midict, ]
        
        for k,entrada in enumerate(self.listaProd):
            self.prodTB.setItem(k,0,QTableWidgetItem(entrada.get('name',str(k))))
        self.initializeEntry(self.iterator)
                    
  
        #self.initializeEntry(self.iterator)
        #self.iterations += 1
        
    def initializeEntry(self,numEntry):
        
        #self.dataFieldCombo.setCurrentIndex(0)
        #self.dataTableCombo.setCurrentIndex(0)   #si no lo elimino no funciona correctamente
        self.domainTableCombo.setCurrentIndex(0)
        self.domainCodeList.setCurrentIndex(0)
        self.domainDescList.setCurrentIndex(0)
        self.domainFilterLE.setText(None)
        #self.linkCheck.setChecked(False)
        self.noneRB.setChecked(True)

        dataContext = self.listaProd[numEntry]
        #vamos ahora al proceso de add
        #TODO si no esta en la lista
        self.prodNameLE.setText(dataContext.get('name',str(numEntry)))
        domainFormLoad(self,dataContext.get('domain',{}))
                       
        if dataContext.get('link via'):
            self.linkCheck.setChecked(True)
            #TODO multiples criterios 
            setAddComboElem(dataContext['link via'][-1].get('table'),
                            self.dataTableCombo,
                        self.listOfTablesCode,self.listOfTables)
            self.dataFieldCombo.set(norm2String(dataContext.get('elem')))
        else:    
            setAddComboElem(self.cache['tabla_ref'],
                            self.dataTableCombo,
                            self.listOfTablesCode,self.listOfTables)
            #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
            if dataContext.get('elem'):
                self.dataFieldCombo.set(norm2String(dataContext.get('elem')))
            #else:
                #self.dataFieldCombo.setCurrentIndex(-1)  #FIXME

        clase=dataContext.get('class','o')
        if clase == 'd' or dataContext.get('fmt','txt') == 'date':
            self.dateCtorRB.setChecked(True)   
            periodFormLoad(self,dataContext)
        if dataContext.get('categories'):
            self.catCtorRB.setChecked(True)
            categoriesFormLoad(self,dataContext)
        elif dataContext.get('case_sql'):
            self.caseCtorRB.setChecked(True)
            caseEditorFormLoad(self,dataContext)
        self.setDetail() #el set Checked no lo dispara

        
    def validatePage(self):
        # falta el nombre y la clase en el padre
        # verificar que los campos obligatorios estan rellenos
        
        if not self.validateEntry(self.iterator):
            return False
        
        self.wizard().iterations = self.iterator
        
        obj = self.wizard().obj
        if obj.type() == 'guides':
            if self.nombreLE.text().strip() == '':
                self.nombreLE.setFocus()
                return False
            self.midict['name'] = self.nombreLE.text()
            self.midict['class'] = GUIDE_CLASS[self.claseCB.currentIndex()][0]
            if len(self.listaProd) > 1:
                self.midict['class'] = 'h'
                
        #self.estadoLink(self.iterator)
        return True
    
    def validateEntry(self,row):
        if self.dataTableCombo.currentIndex() <= 0:
            self.dataTableCombo.setFocus()
            return False
        if len(self.dataFieldCombo.selectedItems()) == 0:
            self.dataFieldCombo.setFocus()
            return False
                
        dataContext = self.listaProd[row]
        
        nombre = self.prodNameLE.text().strip()
        if len(nombre) == 0:
            pass
        elif nombre.isnumeric() :
            pass
        else:
            dataContext['name'] = nombre
            
        dataContext['elem'] = norm2List(self.dataFieldCombo.get())
        tablaDatos = self.listOfTablesCode[self.dataTableCombo.currentIndex()]
        if (tablaDatos != self.cache['tabla_ref'] ):
            #necesitamos un data link
            if not dataContext.get('link via'):
                dataContext['link via'] = []
                entry = {}
                entry['table'] = tablaDatos
                entry['filter'] = ''
                setBaseFK(self,entry,self.cache['tabla_ref'],tablaDatos)
                self.linkCheck.setChecked(True)
                dataContext['link via'].append(entry)
            else:
                ultimaTabla = short2FullName(self,dataContext['link via'][-1]['table'])
                if tablaDatos == ultimaTabla :
                    pass
                else:
                    try:
                        pos = [ short2FullName(self,entry['table']) for entry in dataContext['link via']].index(tablaDatos)
                        del dataContext['link via'][pos +1:]
                    except ValueError:
                        entry = {}
                        entry['table'] = tablaDatos
                        entry['filter'] = ''
                        setBaseFK(self,entry,ultimaTabla,tablaDatos)
                        dataContext['link via'].append(entry)
                        self.linkCheck.setChecked(True)

        
        dominio = dataContext.get('domain',{})
        if not  domainFormValidate(self,dominio):
            return False
        if len(dominio) != 0:
            dataContext['domain'] = dominio
        elif 'domain' in dataContext:
            del dataContext['domain']
        
        orclass = dataContext.get('class','o')
        if dataContext.get('fmt','txt') == 'date':
            orclass = 'd'
            
        if self.noneRB.isChecked():
            if 'class' in dataContext:
                dataContext['class'] = 'o'
            if dataContext.get('fmt','txt') == 'date':
                dataContext['fmt'] = 'txt'
            for name in ('categories','case_sql','mask'):
                if name in dataContext:
                    del dataContext[name]
        if  self.catCtorRB.isChecked():
            if not categoriesFormValidate(self,dataContext):
                return False
            dataContext['class'] = 'c'
            if 'case_sql' in dataContext :
                del dataContext['case_sql']
            if 'mask' in dataContext:
                del dataContext['mask']        
        elif self.caseCtorRB.isChecked():
            if not caseEditorFormValidate(self,dataContext):
                return False
            dataContext['class'] = 'c'
            if 'categories' in dataContext:
                del dataContext['categories']
            if 'mask' in dataContext:
                del dataContext['mask']
        elif self.dateCtorRB.isChecked():
            dataContext['class'] = 'd'
            if not periodFormValidate(self,dataContext):
                return False
            if 'categories' in dataContext:
                del dataContext['categories']
            if 'case_sql' in dataContext :
                    del dataContext['case_sql']
                
        if orclass != dataContext.get('class','o'):
            pai = self.wizard().obj
            if pai.type != 'guides':
                while pai.type() != 'guides':
                    pai = pai.parent()
                clase = pai.getChildrenByName('class')
                
                if not clase:
                    pai.appendRow((CubeItem('class'),CubeItem(dataContext.get('class','o')),CubeItem('class'),))                
                elif clase.getColumnData(1) == 'h':
                    pass
                else:
                    clase.setColumnData(1,dataContext.get('class','o'),Qt.EditRole)
            else:
                self.midict['class'] = dataContext.get('class','o')
                
        #if self.isFinalPage() and (self.iterator != -1 or self.iterator < self.wizard().prodIters):
            #self.wizard().setStartId(ixWzProdBase);
            #self.wizard().restart()        
            #return False

        return True

    def setDetail(self):
        self.Stack.hide()
        if  self.noneRB.isChecked():
            return
        if  self.catCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(0)
        elif self.caseCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(1)            
        elif self.dateCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(2)

    def nextId(self):
        if self.linkCheck.isChecked():
            return ixWzLink
        else:
            return -1
        
    def estadoLink(self,newState):
        if newState == 2:  #True
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)
            
        self.completeChanged.emit()
        
    def dataTablaElegida(self,idx):
        if idx < 1:
            return
        tabname = self.listOfTablesCode[idx]
        self.datalistOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.datalistOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.dataFieldCombo.load(self.datalistOfFieldsCode,self.datalistOfFields)
        if tabname != self.cache['tabla_ref']:
            self.linkCheck.setChecked(True)
        else:
            self.linkCheck.setChecked(False)
            
    def domainTablaElegida(self,idx):
        if idx < 1:
            return
        print('Algo encuentra',idx)
        tabname = self.listOfTablesCode[idx]
        self.domainlistOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.domainlistOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.domainCodeList.load(self.domainlistOfFieldsCode,self.domainlistOfFields)
        self.domainDescList.load(self.domainlistOfFieldsCode,self.domainlistOfFields)

    def openContextMenu(self,position):
        """
        """
        row = self.prodTB.currentRow()
        menuActions = []
        menu = QMenu()
        menuActions.append(menu.addAction("Append",lambda item=row:self.execAction(item,"append")))
        if row != len(self.midict.get('prod',[])) -1:
            menuActions.append(menu.addAction("Insert After",lambda item=row:self.execAction(item,"after")))
        if row != 0:
            menuActions.append(menu.addAction("Insert Before",lambda item=row:self.execAction(item,"before")))
        menu.addSeparator()
        menuActions.append(menu.addAction("Delete",lambda item=row:self.execAction(item,"delete")))
        action = menu.exec_(self.prodTB.viewport().mapToGlobal(position))
    
    def execAction(self,row,action):

        if row >= len(self.midict['prod']):
            return
        
        if action == 'delete':
            del self.midict['prod'][row]
        else:
            if not self.validateEntry(row):
                return False
            if action == 'append':
                self.midict['prod'].append({})
                pos = self.prodTB.rowCount()
            elif action == 'after':
                pos = row +1
                self.midict['prod'].insert(pos,{})
            elif action == 'before':
                pos = row
                self.midict['prod'].insert(pos,{})
            
        self.prodTB.blockSignals(True)
        self.prodTB.clear()
        for k,entrada in enumerate(self.midict['prod']):
            self.prodTB.setItem(k,0,QTableWidgetItem(entrada.get('name',str(k))))
        self.prodTB.blockSignals(False)
        self.prodTB.setCurrentCell(row,0)
 
    def currentCellChanged ( self, currentRow, currentColumn, previousRow, previousColumn): 
        if currentRow == previousRow:
            return 
        try:
            datos = self.prodTB.item(currentRow,0).data(0)
        except AttributeError:
            return
 
        #if self.validatePageLinkEntry(self.midict[previousRow]):
        if previousRow != -1:
            estadoAnterior =  self.validateEntry(previousRow)
        else:
            estadoAnterior = True
            
        if estadoAnterior:     
            self.iterator = currentRow
            self.initializeEntry(currentRow)
        else:
            self.prodTB.scrollToItem(self.prodTB.item(previousRow,previousColumn))

