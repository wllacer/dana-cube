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

class WzLink(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzLink,self).__init__(parent)
               
        self.cube = cube
        self.cache = cache

        self.setTitle("Definición del enlace entre tablas")
        self.setSubTitle(""" Introduzca la definición del enlace entre la tabla base y la guía  """)

        self.tipo = None
        
        tableArray = getAvailableTables(self.cube,self.cache)
        self.baseTable = None
        self.targetTable = None
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []

        numrows=5
        
        #self.joinListArray = WDataSheet(self.context,numrows)
        self.joinListArray = QTableWidget(numrows,2)
        self.joinListArray.setHorizontalHeaderLabels(('Tabla Origen ','Tabla Destino'))
        self.joinListArray.resizeColumnsToContents()
        #
        self.joinListArray.setContextMenuPolicy(Qt.CustomContextMenu)
        self.joinListArray.customContextMenuRequested.connect(self.openContextMenu)

        # ahora para el detalle

        self.baseLabel = QLabel('Desde ')
        self.baseTableCombo = QComboBox()
        self.baseTableCombo.addItems(self.listOfTables)
        self.baseTableCombo.setCurrentIndex(0)
        self.baseTableCombo.currentIndexChanged[int].connect(lambda i,w='source':self.tableChanged(i,w))
                                                             
        self.destLabel = QLabel('Hacia ')
        self.destTableCombo = QComboBox()
        self.destTableCombo.addItems(self.listOfTables)
        self.destTableCombo.setCurrentIndex(0)
        self.destTableCombo.currentIndexChanged[int].connect(lambda i,w='dest':self.tableChanged(i,w))
        
        self.clauseContext=[]
        
        self.clauseContext.append(['campo tabla base','condicion','campo tabla destino'])
        self.clauseContext.append([QComboBox,None,['',]+list(self.listOfFields)])
        self.clauseContext.append([QComboBox,None,tuple(LOGICAL_OPERATOR)])
        self.clauseContext.append([QComboBox,None,None])
        
        numrows=3
        
        self.joinClauseArray = WDataSheet(self.clauseContext,numrows)
        self.joinClauseArray.resizeColumnsToContents()
        
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        self.joinClauseArray.resizeColumnToContents(0)
        self.joinListArray.currentCellChanged[int,int,int,int].connect(self.currentCellChanged)

        self.joinFilterLabel = QLabel("&Filtro:")
        self.joinFilterLineEdit = QLineEdit()
        self.joinFilterLabel.setBuddy(self.joinFilterLineEdit)
            
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.joinListArray,0,0,7,2)
        meatLayout.addWidget(self.baseLabel,0,3)
        meatLayout.addWidget(self.baseTableCombo,0,4)
        meatLayout.addWidget(self.destLabel,1,3)
        meatLayout.addWidget(self.destTableCombo,1,4)
        meatLayout.addWidget(self.joinClauseArray,2,3,3,4)
        meatLayout.addWidget(self.joinFilterLabel,6,3)
        meatLayout.addWidget(self.joinFilterLineEdit,6,3)

        #fullLayout = QHBoxLayout()
        #fullLayout.addWidget(self.joinListArray)
        #fullLayout.addLayout(meatLayout)
        
        self.setLayout(meatLayout)
        #self.setLayout(fullLayout)


        self.joinListArray.hide()

    def initializePage(self):

        obj = self.wizard().obj
        self.iterator = -1
        if obj.type() in ('prod','guides'):
            self.tipo = 'LinkList'
            base = self.wizard().page(ixWzProdBase) 
            if not base:
                self.iterator = 0
            else:
                self.iterator = base.iterations
            self.iterator +1
            if obj.type() == 'prod':
                if obj.text() == obj.type():
                    self.midict = self.wizard().diccionario[self.iterator -1].get('link via',[])
                else:
                    self.midict = self.wizard().diccionario.get('link via',[])
            else:
                self.midict = self.wizard().diccionario['prod'][self.iterator -1].get('link via',[])
            self.initializePageLinkList()
            
        elif obj.type() == 'link via':
            if obj.text() == obj.type():
                self.tipo = 'LinkList'
                self.midict = self.wizard().diccionario 
                self.initializePageLinkList()
            else:
                # aqui viene el proceso de una sola entrada. De momento lo dejo
                self.tipo = 'LinkEntry'
                self.midict = self.wizard().diccionario 
                self.initializePageLinkEntry()
        else:
            print(obj,obj.type(),self.wizard().diccionario)
        if len(self.midict) == 0:
            # no hay elementos. No deberia ocurrir (si es nueva creacion debe hacerse uno con los datos del prod)
            pass
        
        if self.tipo == 'LinkList':
            self.joinListArray.show()
            self.joinListArray.cellChanged[int,int].connect(self.checkList)


    #def nextId(self):
        #return -1

    def validatePage(self):
        if self.tipo == 'LinkList':
            return self.validatePageLinkList()
        elif self.tipo == 'LinkEntry':
            return self.validatePageLinkEntry(self.midict)
    
      
    def initializePageLinkEntry(self):
        obj = self.wizard().obj
        pos = obj.getPos()
        auxobj = obj.getPrevious()
        if auxobj is not None:
            origTable = auxobj.getChildrenByName('table').getColumnData(1)
        else:
            origTable = self.cache['tabla_ref']
        destTable = self.midict.get('table')
        self.loadPageLinkEntry(origTable,destTable,self.midict)
        self.baseTableCombo.setEnabled(False)
        self.destTableCombo.setEnabled(False)
        
    def loadPageLinkEntry(self,origTable,destTable,entry_data):    
        #self.baseTableCombo.show()
        baseField = [ item.get('base_elem') for item in entry_data.get('clause',[]) ]
        relField = [ item.get('rel_elem') for item in entry_data.get('clause',[]) ]
        
       
        pos = setAddComboElem(origTable,self.baseTableCombo,self.listOfTablesCode,self.listOfTables)
        self.tablaElegida(pos,'source')
        pos = setAddComboElem(destTable,self.destTableCombo,self.listOfTablesCode,self.listOfTables)
        self.tablaElegida(pos,'dest')
        #self.baseTableCombo.setEnabled(False)
        #self.destTableCombo.setEnabled(False)
 
        #self.joinClauseArray.resizeColumnsToContents()
            
        if entry_data.get('clause'):
            while len(entry_data.get('clause',[])) > self.joinClauseArray.rowCount():
                self.joinClauseArray.addRow(self.joinClauseArray.rowCount())   
            for i,clausula in enumerate(entry_data.get('clause')):
                setAddComboElem(clausula.get('condition','='),
                                self.joinClauseArray.cellWidget(i,1),
                                LOGICAL_OPERATOR,LOGICAL_OPERATOR)
                setAddComboElem(clausula.get('base_elem',''),
                                self.joinClauseArray.cellWidget(i,0),
                                self.sourceFieldsBase,self.sourceFields,1)

                setAddComboElem(clausula.get('rel_elem',''),
                                self.joinClauseArray.cellWidget(i,2),
                                self.targetFieldsBase,self.targetFields,1)
        
        

        self.joinFilterLineEdit.setText(entry_data.get('filter',''))
    

    def validatePageLinkEntry(self,entry_data):
        resultado = self.joinClauseArray.values()
        # ser pestiño pero primero tengo que eliminar los huecos
        resultado = self.joinClauseArray.values()
        lastNonEmpty = len(resultado) -1
        for k in range(len(resultado) -1,-1,-1):
            if resultado[k][0] > 0:
                lastNonEmpty = k
                break
        try:
            pos = [ linea[0] for linea in resultado[0:lastNonEmpty +1]].index(0)
            self.joinClauseArray.removeRow(pos)
            return False
        except ValueError:
            pass

        for row,entrada in enumerate(resultado):
            if entrada[0] <= 0 and entrada[2] <= 0:
                continue #linea vacia
            elif entrada[0] > 0 and entrada[2] <= 0:
                self.joinClauseArray.cellWidget(row,2).setFocus()
                return False #uno no especificado
            
        entry_data['table'] = self.listOfTablesCode[self.destTableCombo.currentIndex()]
        entry_data['filter'] = self.joinFilterLineEdit.text()
        if entry_data.get('clause'):
            entry_data['clause'].clear()
        else:
            entry_data['clause'] = []
        for linea in resultado:
            if linea[0] <= 0:
                continue  #deberia ser break, pero por si acaso no funciona lo de arriba
            entry = {}
            entry['base_elem'] = self.sourceFieldsBase[linea[0] -1]
            entry['rel_elem'] = self.targetFieldsBase[linea[2] -1]
            if linea[1] != 3:
                entry['condition'] = LOGICAL_OPERATOR[linea[1]]
            entry_data['clause'].append(entry)
            
        if self.tipo == 'LinkList':
            self.checkList(0,0)
        return True
    
    def validatePageLinkList(self):
        #TODO eliminar lineas en blanco
        # ser pestiño pero primero tengo que eliminar los huecos
        
        # valido la ultima linea procesada
        row = self.joinListArray.currentRow()
        if not self.validatePageLinkEntry(self.midict[row]):
            return False
        
    
        if self.iterator == -1:
           return True
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

        return True

        
    def setBaseFK(self,fromTableIdx,toTableIdx):
        fromTable = self.listOfTablesCode[fromTableIdx]
        toTable = self.listOfTablesCode[toTableIdx]
        claves = self.cache['info'][fromTable].get('FK')
        if not claves:
            return 
        #FIXME solo tengo sitio para una primaria
        for fkey in claves:
            #FIXME si hay varias solo coge la primera
            if fkey.get('parent table') == toTable:
                setAddComboElem(fkey.get('ref field'),
                                self.joinClauseArray.cellWidget(0,0),
                                ['',]+[ entry[0] for entry in getFieldsFromTable(fromTable,self.cache,self.cube)],
                                ['',]+[ entry[1] for entry in getFieldsFromTable(fromTable,self.cache,self.cube)])
                setAddComboElem(fkey.get('parent field'),
                                self.joinClauseArray.cellWidget(0,2),
                                ['',]+[ entry[0] for entry in getFieldsFromTable(toTable,self.cache,self.cube)],
                                ['',]+[ entry[1] for entry in getFieldsFromTable(toTable,self.cache,self.cube)])
        for row in range(1,self.joinClauseArray.rowCount()):
            self.joinClauseArray.set(row,0,None)
            self.joinClauseArray.set(row,2,None)
                
    def initializePageLinkList(self):
        for i in range(self.joinListArray.rowCount()):
            if ( i != 0 and i >= len(self.midict) ):
                break
            if i == 0:
                sourceItem = QTableWidgetItem(self.cache['tabla_ref'])
            else:
                sourceItem = QTableWidgetItem(self.midict[i -1]['table'])
            sourceItem.setFlags(Qt.ItemIsEnabled)
            targetItem = QTableWidgetItem(self.midict[i]['table'])
            targetItem.setFlags(Qt.ItemIsEnabled)
            self.joinListArray.setItem(i,0,sourceItem)
            self.joinListArray.setItem(i,1,targetItem)

    def currentCellChanged ( self, currentRow, currentColumn, previousRow, previousColumn): 
        if currentRow == previousRow:
            return 
        try:
            datos = self.joinListArray.item(currentRow,0).data(0)
        except AttributeError:
            return
 
        #if self.validatePageLinkEntry(self.midict[previousRow]):
        if self.dumpDetailSheet(previousRow):
            self.initializeDetailSheet(currentRow)
        else:
            self.joinListArray.scrollToItem(self.joinListArray.item(previousRow,previousColumn))

    def initializeDetailSheet(self,row):
        origTable = self.joinListArray.item(row,0).data(0)
        destTable = self.joinListArray.item(row,1).data(0)
        if row == 0:
            self.baseTableCombo.setEnabled(False)
        else:    
            self.baseTableCombo.setEnabled(True)
        self.loadPageLinkEntry(origTable,destTable,self.midict[row])


    def dumpDetailSheet(self,row):
        if row != -1:
            pass
            return self.validatePageLinkEntry(self.midict[row]  )
        else:
            return True

    def tableChanged(self,idx,status):
        if status == 'source':
            origTable = idx
            destTable = self.destTableCombo.currentIndex()
        elif status == 'dest':
            origTable = self.baseTableCombo.currentIndex()
            destTable = idx
        self.tablaElegida(idx,status)
        #FIXME al iniciarse que pasa con los datos que vienen (nada en teoría)
        self.setBaseFK(origTable,destTable)
        #
        if self.tipo == 'LinkList':
            row = self.joinListArray.currentRow()
            if status == 'source':
                self.joinListArray.item(row,0).setData(0,self.listOfTablesCode[idx])
            elif status == 'dest':
                self.joinListArray.item(row,1).setData(0,self.listOfTablesCode[idx])
                if row < len(self.midict) -1:
                    self.joinListArray.item(row +1,0).setData(0,self.listOfTablesCode[idx])
        
    def tablaElegida(self,idx,status):
        if idx == -1:
            return
        tabname = self.listOfTablesCode[idx]
        print('Current Index Changed',status,tabname)
        if status == 'source':
            self.sourceFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            self.sourceFieldsBase= [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            column = 1
            self.clauseContext[column][2] = ['',] + list(self.sourceFields)
            self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
        elif status == 'dest':
        
            self.targetFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            self.targetFieldsBase= [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            column = 3
            self.clauseContext[column][2] = ['',] + list(self.targetFields)
            self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
 
    
    def openContextMenu(self,position):
        """
        """
        row = self.joinListArray.currentRow()
        menuActions = []
        menu = QMenu()
        menuActions.append(menu.addAction("Append",lambda item=row:self.execAction(item,"append")))
        if row != len(self.midict) -1:
            menuActions.append(menu.addAction("Insert After",lambda item=row:self.execAction(item,"after")))
        if row != 0:
            menuActions.append(menu.addAction("Insert Before",lambda item=row:self.execAction(item,"before")))
        menu.addSeparator()
        menuActions.append(menu.addAction("Delete",lambda item=row:self.execAction(item,"delete")))
        action = menu.exec_(self.joinListArray.viewport().mapToGlobal(position))
    
    def execAction(self,row,action):
        if row >= len(self.midict):
            return
        if action == 'delete':
            del self.midict[row]
            curPos = row -1 if row != 0 else 0
            #FIXME la 0
        elif action == 'append':
            entry = {'table':self.midict[-1]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.append(entry)
            curPos = len(self.midict) -1
            self.destTableCombo.setFocus()
        elif action == 'after':
            entry = {'table':self.midict[row]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.insert(row + 1,entry)
            curPos = row +1
            self.destTableCombo.setFocus()
        elif action == 'before':
            entry = {'table':self.midict[row -1]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.insert(row,entry)
            curPos = row +1
            self.destTableCombo.setFocus()
            
        self.joinListArray.blockSignals(True)
        self.joinListArray.clear()
        self.initializePageLinkList()
        self.joinListArray.blockSignals(False)
        self.joinListArray.setCurrentCell(curPos,0)
 
    def checkList(self,row,colum):
        for row,entry in enumerate(self.midict):
            destList = self.joinListArray.item(row,1).data(0)
            baseList = self.joinListArray.item(row,0).data(0)
            dest = entry.get('table')
            correcta = True
            if row == 0:
                base = self.cache['tabla_ref']
            else:
                base = self.midict[row -1]['table']
                if not dest or dest == base : #no es un error pero debe dar warning
                    correcta = False
            if destList != dest or baseList != base:
                correcta = False
            if correcta:
                if len(entry.get('clause',[])) == 0:
                    correcta = False
            
            if correcta:
                baseFields = [ item[0] for item in getFieldsFromTable(base,self.cache,self.cube)]  #solo FQN si no puede haber diplicidades
                destFields = [ item[0] for item in getFieldsFromTable(dest,self.cache,self.cube)]  #solo FQN si no puede haber
                
                for clausula in entry.get('clause'):
                    if clausula['base_elem'] not in baseFields:
                        correcta = False
                        break
                    if clausula['rel_elem'] not in destFields:
                        correcta = False
                        break
            
            if not correcta:
                self.joinListArray.item(row,0).setBackground(Qt.yellow)
                self.joinListArray.item(row,1).setBackground(Qt.yellow)
            else:
                self.joinListArray.item(row,0).setBackground(Qt.white)
                self.joinListArray.item(row,1).setBackground(Qt.white)

