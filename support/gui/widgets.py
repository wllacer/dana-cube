#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012,2016 Werner Llacer. All rights reserved.. Under the terms of the LGPL 2


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pprint import pprint
from support.util.record_functions import norm2List,norm2String

def makeTableSize(widget):
    widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    #self.resizeColumnsToContents()
    widget.setMinimumSize(widget.horizontalHeader().length()+widget.verticalHeader().width() +4, 
                                widget.verticalHeader().length()+widget.horizontalHeader().height()+4)

class WDelegateSheet(QTableWidget):
    """
    """
    resized = pyqtSignal()
    contextChange = pyqtSignal()
    rowAdded = pyqtSignal(int)
    rowRemoved =pyqtSignal(int)

    def __init__(self,row,col,delegate=None,parent=None):
        super().__init__(row,col,parent)
        makeTableSize(self)
        self.initialize()
        if delegate:
            sheetDelegate = delegate(self)
            self.setItemDelegate(sheetDelegate)
       
        #FIXME no funciona
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        self.editContext = {}
        # en esta posicion para que las señales se activen tras la inicializacion
        #self.currentItemChanged.connect(self.moveSheetSel)
        #self.itemChanged.connect(self.itemChanged)

    def initialize(self):
        for i in range(self.rowCount()):
            self.initializeRow(i)
        self.setItemPrototype(QTableWidgetItem(''))
    
    def initializeRow(self,x):
        for j in range(self.columnCount()):
            self.initializeCell(x,j)

    def initializeCell(self,x,y):
        self.setItem(x,y,QTableWidgetItem(""))

    def openContextMenu(self,position):
        item = self.itemAt(position)
        row = item.row()
        menu = QMenu()
        menu.addAction("Insert row before",lambda i=row:self.addRow(i))
        menu.addAction("Insert row after",lambda i=row:self.addRow(i +1))
        menu.addAction("Append row",self.addRow)
        menu.addSeparator()
        menu.addAction("Remove",lambda i=row:self.removeRow(i))
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
                
    def addRow(self,idx=None,emit=True):
        if not idx:
            idx = self.rowCount()
        self.insertRow(idx)
        for j in range(self.columnCount()):
                self.initializeCell(idx,j)
        if emit:
            self.rowAdded.emit(idx)
        item = self.item(idx,0)
        self.setCurrentItem(item)
        self.setFocus()
        
    def removeRow(self,idx=None,emit=True):
        if not idx:
            return
        self.removeRow(idx)
        if emit:
            self.rowRemoved.emit(idx)
        self.setCurrentItem(self.sheet.item(idx -1,0))
        self.setFocus()

    def setContext(self,data=None,**kwparm):
        changed = False
        for dato in kwparm:
            if self.editContext.get(dato) != kwparm.get(dato):
                changed = True
                break
        if changed:
            self.contextChange.emit()
            self.initialize()
        for dato in kwparm:
            self.editContext[dato] = kwparm[dato]
            
        if data:
            self.loadData(data)
        #self.resizeColumnsToContents()

    def loadData(self,data):
        """
        before use it might be of interest to disconnect the rowAdded pyqtSignal
        FIXME setText o setData
        """
        print('load data')
        for ind,entry in enumerate(data):
            if ind >= self.rowCount():
                self.addRow(emit=False)
            if isinstance(entry,(list,tuple)):
                for col,dato in enumerate(entry):
                    if col >= self.columnCount():
                        break
                    #self.setData(ind,col,dato)
                    self.setData(ind,col,dato)
            else:
                self.setData(ind,0,entry)
    
    def unloadData(self):
        result = [ [ None for k in range(self.columnCount()) ] for j in range (self.rowCount()) ]
        for row  in range(self.rowCount()):
                for col in range(self.columnCount()):
                    if self.item(row,col):
                        result[row][col] = self.item(row,col).data(Qt.EditRole)
                    else:
                        result[row][col] = None
        if self.columnCount() == 1:
            return [ elem[0] for elem in result]
        else:
            return result
    
    def setData(self,row,col,dato):
        print('set data')
        item =  self.item(row,col)
        if not item:
            self.initializeCell(row,col)
        if self.hasSplitData(row,col,dato):
            cdato = self.getSplitData(row,col,dato)
            item.setData(Qt.EditRole,cdato[0])
            item.setData(Qt.DisplayRole,cdato[1])
        else:
            item.setData(Qt.EditRole,dato)

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def set(self,x,y,value):
        return self.setData(x,y,value)

    def get(self,x,y):
        item = self.item(x,y)
        return item.data(Qt.EditRole)

    def values(self):
        return self.unloadData()
    
    def fill(self,data):
        return self.loadData(data)

    def getItem(self,x,y):
        return self.item(x,y)
    
    def hasSplitData(self,x,y,dato):
        """
        specialize as you need in your cases
        """
        return False
    
    def getSplitData(self,x,y,dato):
        return [dato,dato]
    
class WMultiList(QWidget):
    """
    WIP
    Widget para seleccionar elementos de una lista y enviarlos a otra.
    """
    def __init__(self,lista=None,initial=None,format=None,cabeceras=None,parent=None):
        super().__init__(parent)
        self.disponible = QListWidget()
        self.selecto = QListWidget()
        self.anyade = QPushButton('Añadir')
        self.elimina = QPushButton('Eliminar')
        
        
        origenlayout=QVBoxLayout()
        self.origenCabecera = QLabel(cabeceras[0] if cabeceras else 'Elementos disponibles')
        origenlayout.addWidget(self.origenCabecera)
        origenlayout.addWidget(self.disponible)
        
        destinolayout=QVBoxLayout()
        self.destinoCabecera = QLabel(cabeceras[1] if cabeceras else 'Elemenos seleccionados')
        destinolayout.addWidget(self.destinoCabecera)
        destinolayout.addWidget(self.selecto)

        if format == 'c':
            origenlayout.addWidget(self.anyade)
            destinolayout.addWidget(self.elimina)
            meatlayout = QGridLayout()
            meatlayout.addLayout(origenlayout,0,0)
            meatlayout.addLayout(destinolayout,0,1)
        elif format == 'x':
            sp = self.disponible.sizePolicy();
            sp.setHorizontalPolicy(QSizePolicy.Minimum);
            self.disponible.setSizePolicy(sp);
            meatlayout = QVBoxLayout()
            meatlayout.addWidget(self.origenCabecera)
            meatlayout.addWidget(self.disponible)
            meatlayout.addWidget(self.anyade)
            meatlayout.addWidget(self.destinoCabecera)
            meatlayout.addWidget(self.selecto)
            meatlayout.addWidget(self.elimina)
        else:
            boxlayout = QGridLayout()
            boxlayout.addWidget(self.anyade,2,0)
            boxlayout.addWidget(self.elimina,3,0)
            
            meatlayout = QGridLayout()
            meatlayout.addLayout(origenlayout,0,0)
            meatlayout.addLayout(boxlayout,0,2)
            meatlayout.addLayout(destinolayout,0,3)
        
        self.setLayout(meatlayout)

        self.anyade.clicked.connect(self.selectItem)
        self.elimina.clicked.connect(self.removeItem)
        
        self.origList = []
        self.freeList = []
        self.seleList = []
        
        self.load(lista,initial)
     
    def clear(self):
        self.disponible.clear()
        self.selecto.clear()
        self.freeList.clear()
        self.seleList.clear()
        
    def load(self,lista,initial):
        self.disponible.clear()
        if lista is not None:
            self.origList = lista #[ entry for entry in lista ]
        self.freeList = [ entry for entry in self.origList]
        self.disponible.addItems(self.freeList)
        self.selecto.clear()
        self.seleList = []
        if initial is not None:
            self.setSelectedEntries(initial)
    
    # slots
    def selectItem(self,checked):
        """
        checked is not used
        """
        lista = self.disponible.selectedItems()
        for item in lista:
            valor = item.data(0)
            idx = self.freeList.index(valor)
            del self.freeList[idx]
            self.seleList.append(valor)
            mitem = self.disponible.takeItem(idx)
            self.selecto.addItem(mitem)

    def removeItem(self,checked):
        """
        checked is not used, but demanded by signal
        #TODO devolver a la posicion original
        """
        lista = self.selecto.selectedItems()
        for item in lista:
            valor = item.data(0)
            idx = self.seleList.index(valor)
            del self.seleList[idx]
            self.freeList.append(valor)
            mitem = self.selecto.takeItem(idx)
            self.disponible.addItem(mitem)

    def removeSelection(self):
        for item in self.seleList:
            self.removeEntry(item.data(0))

    def selectEntry(self,entrada):
        if entrada not in self.seleList:
            self.seleList.append(entrada)
            self.selecto.addItem(entrada)
        try:
            ande = self.freeList.index(entrada)
            self.disponible.takeItem(ande)
            del self.freeList[ande]
        except ValueError:                           
            self.origList.append(entrada)
            
    def removeEntry(self,entrada):
        if entrada not in self.freeList:
            self.freeList.append(entrada)  #TODO devolver a la posicion original
            self.disponible.addItem(entrada)
        ande = self.seleList.index(entrada)
        self.selecto.takeItem(ande)
        del self.seleList[ande]

    def setSelectedEntries(self,lista):
        conjunto = norm2List(lista)
        for entrada in conjunto:
            self.selectEntry(entrada)

    ## signals
    #def itemSelected(self,item): #signal
        #pass
    #def itemRemoved(self,item):  #signal
        #pass
    ## methods
    
    #def getAvailableItems(self):
        #pass
    #def setAvailableItems(self,lista):
        #pass
    #def getAvailableItemsLabel(self):
        #pass
    #def setAvailableItemsLabel(self,label):
        #pass
    #def getSelectedItems(self):
        #pass
    #def setSelectedItems(self,lista):
        #pass
    #def getSelectedItemsLabel(self):
        #pass    
    #def setSelectedItemsLabel(self,label):
        #pass
    ## protected member
    #def addSelectedItem(self):
        #pass
    #def removeSelectedItem(self):
        #pass

        
class WMultiCombo(QComboBox):
    """ Una variante de combo con seleccion multiple
    """
    def __init__(self,parent=None):
        super(WMultiCombo,self).__init__(parent)
        self.Head = None
        self.view().pressed.connect(self.handleItemPressed)
        
    def load(self,data,dataDisplay=None):
        model = QStandardItemModel()
        item = QStandardItem('Seleccione los elementos')
        model.setItem(0,0,item)
        self.Head = item.index()
        if not dataDisplay:
            dataDisplay = data
        for i,entrada in enumerate(dataDisplay):
            item = QStandardItem(entrada)
            item.setData(Qt.Unchecked,Qt.CheckStateRole)
            item.setFlags(Qt.ItemIsEnabled)
            item.setData(data[i],Qt.UserRole+1)
            model.setItem(i+1,0,item)
        self.setModel(model)

    def updateHeader(self,status,item):
        if not self.Head:
            self.Head = self.model().item(0).index()
        hdr = self.model().itemFromIndex(self.Head)
        extra = set(norm2List(hdr.data()))
        if status == 'add':
            extra.add(item.data(Qt.DisplayRole))
        elif status == 'remove':
            try:
                extra.remove(item.data(Qt.DisplayRole))
            except KeyError:
                pass
        if len(extra) > 0:
            hdr.setData(norm2String(list(extra)))
            hdr.setData(norm2String(list(extra)),Qt.DisplayRole)
        else:
            hdr.setData(norm2String(None))
            hdr.setData(norm2String(None),Qt.DisplayRole)

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)

        if index.row() == 0:
            return
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.updateHeader('remove',item)
        else:
            item.setCheckState(Qt.Checked)
            self.updateHeader('add',item)

    def checkElemText(self,text):
        # find data choca con el elemento 0
        for k in range(1,self.count()):
            if text in (self.itemData(k,Qt.DisplayRole),self.itemData(k,Qt.UserRole +1)):
                return k
        return -1
      
    def addCell(self,data,dataDisplay=None,values=None):
        if not dataDisplay:
            display = data
        else:
            display = dataDisplay
        self.load(data,display)
        
        if values is None :
            return 
        self.set(values)

    def set(self,values):
        elementos = norm2List(values)
        for entry in elementos:
            idx = self.checkElemText(entry)
            if idx < 0:
                item = QStandardItem(entry)
                item.setData(Qt.Checked,Qt.CheckStateRole)
                item.setFlags(Qt.ItemIsEnabled)
                item.setData(entry,Qt.UserRole+1)
                self.model().appendRow(item)
                idx = self.model().rowCount() -1
                
            self.setItemData(idx,Qt.Checked,Qt.CheckStateRole)
            self.updateHeader('add',self.model().item(idx))
    
    def unset(self,values):
        elementos = norm2List(values)
        for item in elementos:
            idx = self.checkElemText(item)
            if idx > 0:
                self.setItemData(idx,Qt.Unchecked,Qt.CheckStateRole)
                self.updateHeader('remove',self.model().item(idx))
                
    def reset(self):
        for idx in range(1,self.count()):
            if self.itemData(idx,Qt.CheckStateRole) == Qt.Checked:
                self.setItemData(idx,Qt.Unchecked,Qt.CheckStateRole)
                
        self.setItemData(0,'Seleccione los elementos')
                                 
    
    def get(self):
        result = []
        for k in range(1,self.count()):
            if self.itemData(k,Qt.CheckStateRole) == Qt.Checked :
                result.append(self.itemData(k,Qt.UserRole +1))
        return norm2String(result)
            
    def selectedItems(self):
        result = []
        for k in range(1,self.count()):
            if self.itemData(k,Qt.CheckStateRole) == Qt.Checked :
                result.append(self.model().item(k))
        return result
            

class WPowerTable(QTableWidget):
    # TODO mas tipos
    # TODO un defecto razonable

    def __init__(self,rows=0,cols=0,parent=None):
        super(WPowerTable,self).__init__(rows,cols,parent)
        #self.horizontalHeader().setStretchLastSection(True)
        #self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum);
        #self.resizeRowsToContents()
        #self.resizeColumnsToContents()
        self.rowModelDef = None
        
    def openContextMenu(self,position):
        print('abro menu')
        row = self.currentRow()
        menuActions = []
        menu = QMenu()
        menuActions.append(menu.addAction("Append lines",lambda item=row:self.execAction(item,"append")))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def execAction(self,row,action):
        print('exec menu')
        if action == 'append':
            self.appendRow(self.rowCount())

    def setRowModelDef(self,contexto):
        """
        contexto es un array que define cada una de las columnas de una fila .
        Muy util para el add row
        """
        self.rowModelDef = contexto
    def addCell(self,x,y,colDef=None,defVal=None):
        item = defVal
        if colDef:
            type = colDef[0]
            typeSpec = colDef[1]
            if len(colDef) > 2:
                listVals = colDef[2]
            else:
                listVals = None
        elif self.rowModelDef and len(self.rowModelDef) < y:
            type = self.rowModelDefault[y][0]
            typeSpec = self.rowModelDefault[y][1]
            if len(self.rowModelDefault[y]) > 2:
                listVals = self.rowModelDefault[y][2]
            else:
                listVals = None
        else:
            #fall back to standard widget
            return 
            
        editItem = None
        if type is None or type == QLineEdit:
            editItem = QLineEdit()
            editItem.setText(str(item) if item is not None else '')
        elif type == QCheckBox:
            editItem = QCheckBox()
            if item is None:
                editItem.setChecked(False)
            else:
                editItem.setChecked(item)
        elif type == QSpinBox:
            editItem = QSpinBox()
            if item is None:    
                editItem.setValue(0)
            else:
                editItem.setValue(item)
        elif type == WMultiCombo:
            editItem = WMultiCombo()
            if listVals is not None:
                """
                aqui list vals es un array de dos elementos interno y display 
                """
                if len(listVals) == 2:
                    display = listVals[1]
                    datos = listVals [0]
                else:
                    display = datos = listVals[0]
                    editItem.addCell(datos,display,item)

            
        elif type == QComboBox:
            editItem = QComboBox()
            if listVals is not None:
                editItem.addItems(listVals)
            if item is None:
                pass
            else:
                if isinstance(item,int):
                    editItem.setCurrentIndex(item)
                else:  #esto es para el caso en que no existe en origen (prefijos, por ejemplo)
                    editItem.addItem(item)
                    editItem.setCurrentIndex(editItem.count() -1)
              
        else:
            print('Noooop',x)
        if typeSpec is not None:
            #TODO ejecuto los metodos dinamicamente. por ahora solo admite parametros en lista  
            #TODO vale como funcion utilitaria
            for func in typeSpec:
                try:
                    shoot = getattr(editItem,func)
                except AttributeError:
                    print(typeSpec,item)
                    exit()
                if isinstance(typeSpec[func],(list,tuple)):
                    parms = typeSpec[func]
                else:
                    parms = (typeSpec[func],)
                shoot(*parms)

        self.setCellWidget(x,y,editItem)
        self.cellWidget(x,y).setContextMenuPolicy(Qt.CustomContextMenu)
        self.cellWidget(x,y).customContextMenuRequested.connect(self.openContextMenu)

    def values(self):
        valores=[]
        for x in range(self.rowCount()):
            linea=[]
            for y in range(self.columnCount()):
                linea.append(self.get(x,y))
            valores.append(linea)
        return valores

    def set(self,x,y,value):
        if isinstance(self.cellWidget(x,y),QLineEdit):
            if isinstance(value,(int,float)):
                self.cellWidget(x,y).setText(str(value))
            else:
                self.cellWidget(x,y).setText(value)
        elif isinstance(self.cellWidget(x,y),QCheckBox):
            if value is None:
                self.cellWidget(x,y).setChecked(False)
            else:
                self.cellWidget(x,y).setChecked(value)
        elif isinstance(self.cellWidget(x,y),QSpinBox):
            self.cellWidget(x,y).setValue(value)
        elif isinstance(self.cellWidget(x,y),WMultiCombo):
            self.cellWidget(x,y).set(value)
        elif isinstance(self.cellWidget(x,y),QComboBox):
            if value is None:
                self.cellWidget(x,y).setCurrentIndex(-1)
            elif isinstance(value,int):
                self.cellWidget(x,y).setCurrentIndex(value)
            else:
                self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).findText(value,Qt.MatchExactly))
                #FIXME no se si no debe sustituirse por esta de abajo
                #TODO comprobar matches parciales
                #try:
                    #self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).findText(value))
                #except IndexError :
                    #self.cellWidget(x,y).addItem(value)
                    #self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).count() -1)

        else:
            self.cellWidget(x,y).setText(value)
            print('Noooop',x,y)

        
    def get(self,x,y):
        if isinstance(self.cellWidget(x,y),QLineEdit):
            return self.cellWidget(x,y).text()
        elif isinstance(self.cellWidget(x,y),QCheckBox):
            return self.cellWidget(x,y).isChecked()
        elif isinstance(self.cellWidget(x,y),QSpinBox):
            return self.cellWidget(x,y).value()
        elif isinstance(self.cellWidget(x,y),WMultiCombo):
            return self.cellWidget(x,y).get()

        elif isinstance(self.cellWidget(x,y),QComboBox):
            return self.cellWidget(x,y).currentIndex()
        else:
            print('Noooop',x,y)
            return self.cellWidget(x,y).text()
        
   
    def appendRow(self,row):
        self.insertRow(row)
        if self.rowModelDef:
            for k in range(min(len(self.rowModelDef),self.columnCount())):
                self.addCell(row,k,self.rowModelDef[k])

       
class WDataSheet(WPowerTable):
    def __init__(self,context,rows,parent=None): 
        
        cols=len(context) -1

        super(WDataSheet, self).__init__(rows,cols,parent)
        # cargando parametros de defecto
        self.context = context
        self.initializeTable(rows)
        
        #FIXME es un desastre
    def initializeTable(self,rows):
        cabeceras = [ item  for item in self.context[0] ]
        for k in range(rows):
            self.addRow(k)

        self.setHorizontalHeaderLabels(cabeceras)
        

        #self.resizeColumnsToContents()

    def changeContext(self,context):
        #FIXME y que pasa con el contenido actual
        self.context = context
        self.clearContents()
        self.initializeTable(self.rowCount())

    def changeContextColumn(self,context,column):
        #FIXME y que pasa con el contenido actual
        self.context[column] = context
        for k in range(self.rowCount()):
            if self.context[column][0] == QComboBox:
                self.cellWidget(k,column -1).clear()
                self.cellWidget(k,column -1).addItems(self.context[column][2])
            else:
                self.set(k,column - 1,None)

         
    def addRow(self,line):
        for y,colDef in enumerate(self.context[1:]):
            self.addCell(line,y,colDef)
            
    def fill(self,data):
        if len(data) == 0:
            return
        rows=min(self.rowCount(),len(data))
        cols=min(self.columnCount(),len(data[0]))
        for x in range(rows):
            for y in range(cols):
                self.set(x,y,data[x][y])
            
    def values(self):
        valores=[]
        for x in range(self.rowCount()):
            linea=[]
            for y in range(self.columnCount()):
                linea.append(self.get(x,y))
            valores.append(linea)
        return valores
     
    def valueCol(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            #if self.sheet.cellWidget(k,0) is None:
                #print('elemento {} vacio'.format(k))
                #continue
            valores.append(self.get(k,col))
        return valores
 
 
class WPropertySheet(WPowerTable):
    """
        Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
           context[0] titulos de las filas
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] parametrizacion del widget (metodo:valor)
           ...
       FIXME que pasa cuando context != data
       
    """
    def __init__(self,context,data,parent=None): 
        
        rows=len(context)
        cols=1
        super(WPropertySheet, self).__init__(rows,cols,parent)
        # cargando parametros de defecto
        self.context = context
        cabeceras = [ k[0] for k in self.context ]
        for k in range(len(self.context)):
                self.addCell(k,0,context[k][1:],None)
                if data:
                    self.set(k,0,data[k])
                else:
                    self.set(k,0,None)
        self.setVerticalHeaderLabels(cabeceras)
        #no necesito cabeceras horizontales en este caso
        self.horizontalHeader().hide()


        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)

        
    def values(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            valores.append(self.get(k,0))
        return valores

"""
delegados estandar

"""        
class columnSheetDelegate(QStyledItemDelegate):
    def __init__(self,context,parent=None):
        super().__init__(parent)
        self.context = context
        
    def createEditor(self,parent,option,index):
        col = index.column()
        specs = self.context[col +1]
        if len(specs) < 4:
            for k in range(len(specs),4):
                specs.append(None)
        return self._setupEditorFromContext(specs,parent,option,index)
    
    def _setupEditorFromContext(self,specs,parent,option,index):
        editorObj = specs[1] if specs[1] else super().createEditor(parent,option,index)
        editor = editorObj(parent)
        typeSpec = specs[2]
        if typeSpec is not None:
            #TODO ejecuto los metodos dinamicamente. por ahora solo admite parametros en lista  
            #TODO vale como funcion utilitaria
            for func in typeSpec:
                try:
                    shoot = getattr(editor,func)
                except AttributeError:
                    print('Error de atributos',typeSpec)
                    exit()
                if isinstance(typeSpec[func],(list,tuple)):
                    parms = typeSpec[func]
                else:
                    parms = (typeSpec[func],)
                shoot(*parms)
        self.fullList = specs[3]
        if self.fullList is not None:
            if isinstance(self.fullList[0],(list,tuple)):
                self.isDouble = True
                self.currentList = [ elem[1] for elem in self.fullList]
            else:
                self.isDouble = False
                self.currentList = self.fullList
            if editorObj in  (WMultiCombo,QComboBox):
                editor.addItems(self.currentList)
        return editor
        
    def setEditorData(self, editor, index):
        col = index.column()
        dato = index.data()
        def_value = None

        self._setWidgetData(editor,dato,def_value)
        
    def setModelData(self,editor,model,index):
        dato = self._getWidgetData(editor)
        if type(editor) == QComboBox and self.isDouble:
            model.setData(index,dato[0],Qt.EditRole)
            model.setData(dato[1],Qt.DisplayRole)
            return 
        elif isinstance(dato,(list,tuple)):
            dato = norm2String(dato)
        model.setData(index,dato)
        
        
    def _setWidgetData(self,editor,dato,valor_defecto):
        
        if isinstance(editor,WMultiList):
            for entrada  in dato:
                self.__multiListLoad(editor,entrada)           
            if not dato and valor_defecto is not None:
                editor.selectEntry(valor_defecto)

        if isinstance(editor,WMultiCombo): # WMC siemre antes que QCB porque es una especializacion
            for entrada in dato:
                editor.set(entrada)
            if len(dato) == 0 and valor_defecto is not None:
                editor.set(valor_defecto)
                
        elif isinstance(editor,QComboBox):
            if dato:
                self.__comboLoad(editor,dato)
            elif valor_defecto:
                editor.setCurrentIndex(self.currentList.index(valor_defecto))
            else:
                editor.setCurrentIndex(-1)

        elif isinstance(editor, QSpinBox):
            if dato is not None:
                editor.setValue(dato)
            else:
                editor.setValue(valor_defecto)

        elif isinstance(editor, QCheckBox):
            if dato is not None:
                editor.setCheckState(dato)
            else:
                if valor_defecto:
                    editor.setChecked(valor_defecto)
                else:
                    editor.setChecked(False)

        elif isinstance(editor,QTextEdit):
            # FIXME esto tiene que mejorar. Solo me sirve para el caso de case_sql
            if dato is not None:
                editor.setText(dato)
            else:
                editor.setText(valor_defecto)
            editor.setMinimumHeight(220)
            #editor.resize(editor.document().size().width(), editor.document().size().height() + 10)
            
        elif isinstance(editor,WPowerTable):
            for x,linea in enumerate(dato):
                for y in range(2):
                    editor.cellWidget(x,y).setText(linea[y])
            editor.resizeRowsToContents()
        elif isinstance(editor,QDialog):
            if dato:
                editor.setData(dato)
            elif valor_defecto is not None:
                editor.setData(valor_defecto)
        else:
            if dato is not None:
                editor.setText(dato)
            elif valor_defecto is not None:
                editor.setText(valor_defecto)

    def _getWidgetData(self,editor):
        
        if isinstance(editor, WMultiList):
            return self.__multiListUnload(self,editor)
        elif isinstance(editor, WMultiCombo):
            return editor.get()                
        elif isinstance(editor,QTextEdit):
            return editor.document().toPlainText()
        elif isinstance(editor,QDialog):
            return editor.getData()
        elif isinstance(editor, QComboBox):
            if self.isDouble:
                return [self.fullList[editor.currentIndex()][0] , self.currentList[editor.currentIndex()]]
            else:
                return self.currentList[editor.currentIndex()]
        elif isinstance(editor, QSpinBox):
            return editor.value()
        elif isinstance(editor, QCheckBox):
            return editor.isChecked()
        elif isinstance(editor,WPowerTable):
            return editor.values()
        else:
            return editor.text()

    def __multiListLoad(self,editor,dato):
        """
        convenience for just this
        """
        if self.isDouble:                            #para presentar correctamente
            try:
                pos = self.currentList.index(dato)
            except ValueError:
                try:
                    pos  = [ entry[0] for entry in self.fullList ].index(dato)
                except ValueError:
                    self.currentList.append(dato)
                    self.fullList.append([dato,dato])
                    pos = len(self.currentList) -1
            dato = self.currentList[pos]
        editor.selectEntry(dato)
 
    def __comboLoad(self,editor,dato):
        """
        convenience for just this
        """
        isEditable = editor.isEditable()
        try:
            pos = self.currentList.index(dato)
        except ValueError:
            print('falla ',dato,'para ',self.currentList)
            if self.isDouble:
                try:
                    pos =  [ entry[0] for entry in self.fullList].index(dato)
                except ValueError:
                    if isEditable:
                        self.currentList.append(dato)
                        self.fullList.append([dato,dato])
                        editor.addItem(dato)
                        pos = len(self.currentList) -1
                    else:
                        raise
            else:
                if isEditable:
                    self.currentList.append(dato)
                    editor.addItem(dato)
                    pos = len(self.currentList) -1
                else:
                    raise
        editor.setCurrentIndex(pos)
                
    def __multiListUnload(self,editor):
        if not self.isDouble:
            values = editor.seleList
        else:
            values = []
            tmpval = editor.seleList
            for entry in tmpval:
                idx = self.currentList.index(entry)
                try:
                    values.append(self.fullList[idx][0])
                except IndexError:
                    values.append(entry)
        return values

class rowSheetDelegate(columnSheetDelegate):
    """
            Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
           context[0] titulos de las filas
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] parametrizacion del widget (metodo:valor)
           ...
    """
    def createEditor(self,parent,option,index):

        row = index.row()
        specs = [None,] + list(self.context[row][1:])
        if len(specs) < 4:
            for k in range(len(specs),4):
                specs.append(None)
        #specs = (None,self.context[row][1],self.context[row][2],self.context[row][3])
        return self._setupEditorFromContext(specs,parent,option,index)
        
class WDataSheet2(WDelegateSheet):
    """
        No real example now
        Version del TableWidget para simular hojas de entrada de datos
        se inicializa con el context
           context[0] titulos de las filas
           context[1 -n] columnas
                (??)context[k][0] valores iniciales (si es comun)
                context[k][1] widget a utilizar (defecto QLineEdit)
                context[k][2] parametrizacion del widget (metodo:valor)
                context[k][3] lista adicinal de valores (para QComboBox y similares)
           ...
           m numero de filas a generar
           
    """
    def __init__(self,context,rows,parent=None):
        cols = len(context) -1
        super().__init__(rows,cols,parent=parent)
        self.editContext = context
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setVerticalHeaderLabels(context[0])
        self.setHorizontalHeaderLabels(('Operador','>                Valores                       <'))
        delegate = columnSheetDelegate
        sheetDelegate = delegate(self.editContext)
        self.setItemDelegate(sheetDelegate)

    def initializeTable(self,rows):
        if rows <= self.rowCount():
            self.initialize(self)
        else:
            self.initialize(self)
            original = self.rowCount()
            for k in range(original,rows):
                self.addRow()
            
    def changeContext(self,context):
        """
        hay que probarlo, pero deberia bastar con eso
        """
        self.editContext = context
        self.contextChange.emit()
        
    def changeContextColumn(self,context,column):
        self.editContext = context
        self.contextChange.emit()
        
    def addRow(self,line=None):
        super().addRow(line)
    def valueCol(self,col=0):
        pass
    #** from powertable **
    #def __init__(self,rows=0,cols=0,parent=None):
    #def openContextMenu(self,position):
    #def execAction(self,row,action):
    #def setRowModelDef(self,contexto):
    #def addCell(self,x,y,colDef=None,defVal=None):
    #def values(self):
    #def appendRow(self,row):
    #** from WDelegateSheet
    #def __init__(self,row,col,delegate=None,parent=None):
    #def initialize(self):
    #def initializeRow(self,x):
    #def initializeCell(self,x,y):
    #def openContextMenu(self,position):
    #def addRow(self,idx=None,emit=True):
    #def removeRow(self,idx=None,emit=True):
    #def setContext(self,data=None,**kwparm):
    #def loadData(self,data):
    #def unloadData(self):
    #def setData(self,row,col,dato):
    #def resizeEvent(self, event):

class WPropertySheet2(WDelegateSheet):
    """
            Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
           context[0] titulos de las filas
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] parametrizacion del widget (metodo:valor)
           ...
    """
    def __init__(self,context,data,parent=None): 
        cols = 1
        rows = len(context) 
        super().__init__(rows,cols,parent=parent)  # super().__init__ ANTES de los self.
        self.editContext = context
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setVerticalHeaderLabels([ elem[0] for elem in context])
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        delegate = rowSheetDelegate
        sheetDelegate = delegate(self.editContext)
        self.setItemDelegate(sheetDelegate)
        if data:
            self.loadData(data)
            
    def hasSplitData(self,x,y,dato):
        """
        specialize as you need in your cases
        """
        specs = self.editContext[x]
        if  specs[1] in (QComboBox,WMultiCombo) :
            if specs[3] and isinstance(specs[3][0],(list,tuple,set)):
                  return True
            elif specs[3] and isinstance(dato,int):
                return True
            else:
                return False
        else:
            return False
    
    def getSplitData(self,x,y,dato):
        fullList = self.editContext[x][3]
        if isinstance(fullList[0],(list,tuple)):
            internalList = [ elem[1] for elem in fullList]
            try:
                pos = internalList.index(dato)
            except ValueError:
                try:
                    pos  = [ entry[1] for entry in fullList ].index(dato)
                except ValueError:
                    pos = -1
            if pos >= 0:
                print('extraigo',fullList[pos][0:1])
                return fullList[pos][0:1]
            else:
                return [dato,dato]
        elif isinstance(dato,int):
            return [dato,fullList[dato]]
      
        return [dato,dato]
#** from powertable **
    #def __init__(self,rows=0,cols=0,parent=None):
    #def openContextMenu(self,position):
    #def execAction(self,row,action):
    #def setRowModelDef(self,contexto):
    #def addCell(self,x,y,colDef=None,defVal=None):
    #def values(self):
    #def appendRow(self,row):
#** from WDelegateSheet
    #def __init__(self,row,col,delegate=None,parent=None):
    #def initialize(self):
    #def initializeRow(self,x):
    #def initializeCell(self,x,y):
    #def openContextMenu(self,position):
    #def addRow(self,idx=None,emit=True):
    #def removeRow(self,idx=None,emit=True):
    #def setContext(self,data=None,**kwparm):
    #def loadData(self,data):
    #def unloadData(self):
    #def setData(self,row,col,dato):
    #def resizeEvent(self, event):
