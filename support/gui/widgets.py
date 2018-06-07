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
from support.util.numeros import is_number

def makeTableSize(widget):
    widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    #self.resizeColumnsToContents()
    widget.setMinimumSize(widget.horizontalHeader().length()+widget.verticalHeader().width() +4, 
                                widget.verticalHeader().length()+widget.horizontalHeader().height()+4)

def setWidgetData(parent,editor,dato,valor_defecto):
    if isinstance(editor,WMultiList):
        for entrada  in dato:
            __multiListLoad(parent,editor,entrada)           
        if not dato and valor_defecto is not None:
            editor.selectEntry(valor_defecto)

    elif isinstance(editor,WMultiCombo): # WMC siemre antes que QCB porque es una especializacion
        for entrada in dato:
            editor.set(entrada)
        if len(dato) == 0 and valor_defecto is not None:
            editor.set(valor_defecto)
        
    elif isinstance(editor,QComboBoxIdx):
        # Si no existe lo dejo abendar. No deberia pasar con este tipo de combos
        if dato:
            if is_number(dato):
                editor.setCurrentIndex(dato)
            else:
                editor.setCurrentIndex(parent.currentList.index(dato))
        elif valor_defecto:
            editor.setCurrentIndex(valor_defecto)
        else:
            editor.setCurrentIndex(-1)
            
    elif isinstance(editor,QComboBox):
        if dato:
            __comboLoad(parent,editor,dato)
        elif valor_defecto:
            editor.setCurrentIndex(parent.currentList.index(valor_defecto))
        else:
            editor.setCurrentIndex(-1)

    elif isinstance(editor, QSpinBox):
        if dato:
            editor.setValue(int(dato))
        elif valor_defecto:
            editor.setValue(int(valor_defecto))
        else:
            editor.setValue(1)

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
            for y in range(len(linea)):
                editor.set(x,y,linea[y])
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

def getWidgetData(parent,editor):
    if isinstance(editor, WMultiList):
        return __multiListUnload(parent,editor)
    elif isinstance(editor, WMultiCombo):
        return editor.get()                
    elif isinstance(editor,QTextEdit):
        return editor.document().toPlainText()
    elif isinstance(editor,QDialog):
        return editor.getData()
    elif isinstance(editor,QComboBoxIdx):
        return editor.currentIndex()
    elif isinstance(editor, QComboBox):
        if parent.isDouble:
            return [parent.fullList[editor.currentIndex()][0] , parent.currentList[editor.currentIndex()]]
        else:
            return parent.currentList[editor.currentIndex()]
    elif isinstance(editor, QSpinBox):
        return int(editor.value())
    elif isinstance(editor, QCheckBox):
        return editor.isChecked()
    elif isinstance(editor,WPowerTable):
        return editor.values()
    elif isinstance(editor,QDialog):
        return editor.getData()
    else:
        return editor.text()

def __multiListLoad(parent,editor,dato):
    """
    convenience for just this
    """
    if parent.isDouble:                            #para presentar correctamente
        try:
            pos = parent.currentList.index(dato)
        except ValueError:
            try:
                pos  = [ entry[0] for entry in parent.fullList ].index(dato)
            except ValueError:
                parent.currentList.append(dato)
                parent.fullList.append([dato,dato])
                pos = len(parent.currentList) -1
        dato = parent.currentList[pos]
    editor.selectEntry(dato)
 
def __comboLoad(parent,editor,dato):
    """
    convenience for just this
    """
    isEditable = editor.isEditable()
    try:
        pos = parent.currentList.index(dato)
    except ValueError:
        if parent.isDouble:
            try:
                pos =  [ entry[0] for entry in parent.fullList].index(dato)
            except ValueError:
                if isEditable:
                    parent.currentList.append(dato)
                    parent.fullList.append([dato,dato])
                    editor.addItem(dato)
                    pos = len(parent.currentList) -1
                else:
                    raise
        else:
            if isEditable:
                parent.currentList.append(dato)
                editor.addItem(dato)
                pos = len(parent.currentList) -1
            else:
                raise
    editor.setCurrentIndex(pos)
            
def __multiListUnload(parent,editor):
    if not parent.isDouble:
        values = editor.seleList
    else:
        values = []
        tmpval = editor.seleList
        for entry in tmpval:
            idx = parent.currentList.index(entry)
            try:
                values.append(parent.fullList[idx][0])
            except IndexError:
                values.append(entry)
    return values


class WDelegateSheet(QTableWidget):
    """
    """
    resized = pyqtSignal()
    contextChange = pyqtSignal()
    rowAdded = pyqtSignal(int)
    rowRemoved =pyqtSignal(int)

    def __init__(self,row,col,delegate=None,parent=None):
        super().__init__(row,col,parent)
        self.initialize()
        if delegate:
            sheetDelegate = delegate(self)
            self.setItemDelegate(sheetDelegate)
       
        #FIXME no funciona
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        if row < 10:
            makeTableSize(self)
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
                        result[row][col] = self.get(row,col) #.data(Qt.UserRole +1)
                    else:
                        result[row][col] = None
        if self.columnCount() == 1:
            return [ elem[0] for elem in result]
        else:
            return result
    
    def setData(self,row,col,dato):

        item =  self.item(row,col)
        if not item:
            self.initializeCell(row,col)
        if self.hasSplitData(row,col,dato):
            cdato = self.getSplitData(row,col,dato)
            item.setData(Qt.UserRole +1,cdato[0])
            item.setData(Qt.DisplayRole,cdato[1])
        else:
            item.setData(Qt.DisplayRole,dato)

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def set(self,x,y,value):
        return self.setData(x,y,value)

    def get(self,x,y):
        item = self.item(x,y)
        dato = item.data(Qt.UserRole +1)
        if not dato:
            dato = item.data(Qt.DisplayRole)
        return dato

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
    
    def setEnabled(self,x,y,state):
        if state:
            self.item(x,y).setFlags( Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled )
            self.item(x,y).setBackground(QColor(Qt.white))
        else:
            self.item(x,y).setFlags(Qt.ItemIsSelectable )
            self.item(x,y).setBackground(QColor(Qt.gray))
            
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

class QComboBoxIdx(QComboBox):
    """
    Un nombre distinto para el combobox que usa como dato el indice, no el valor.
    En lo demás absolutamente identico al combo
    """
    pass

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
            

class WPowerTable(WDelegateSheet):
    """
    DEPRECATED
    """
    def __init__(self,row,cols,parent=None):
        super().__init__(self,row,cols,parent=parent)
    def setRowModelDef(self,contexto):
        self.edtiContext = contexto
    def addCell(self,x,y,colDef,defVal):
        print(" Clase obsoleta y funcion no compatible ")
        return
    def appendRow(self,row):
        self.addRow(row)
        
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
            if editorObj in  (WMultiCombo,QComboBoxIdx,QComboBox):
                editor.addItems(self.currentList)
        return editor
        
    def setEditorData(self, editor, index):
        col = index.column()
        dato = index.data()
        try:
            def_value = self.context[index.column() +1][4] 
        except IndexError:
            def_value = None

        setWidgetData(self,editor,dato,def_value)
        
    def setModelData(self,editor,model,index):
        dato = getWidgetData(self,editor)
        print(dato)
        if type(editor) == QComboBox and self.isDouble:
            model.setData(index,dato[0],Qt.UserRole +1)
            model.setData(index,dato[1],Qt.DisplayRole)
            return 
        elif isinstance(dato,(list,tuple)):
            dato = norm2String(dato)
        model.setData(index,dato)
        
        


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
        
class WDataSheet(WDelegateSheet):
    """
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
        self.horizontalHeader().setStretchLastSection(True)
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

class WPropertySheet(WDelegateSheet):
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
