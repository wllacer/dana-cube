#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012,2016 Werner Llacer. All rights reserved.. Under the terms of the LGPL 2
"""


    
"""

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
from base.tree import traverse #FIXME esto rompe la division

USER,DISP,EDIT = (Qt.UserRole +1,Qt.DisplayRole,Qt.EditRole)

def makeTableSize(widget):
    widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    ##self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    #self.resizeColumnsToContents()
    widget.setMinimumSize(widget.horizontalHeader().length()+widget.verticalHeader().width() +4, 
                                widget.verticalHeader().length()+widget.horizontalHeader().height()+4)

def setWidgetData(parent,editor,dato,valor_defecto):
    if isinstance(editor,WMultiList):
        if dato:
            editor.setEntries(dato)
        if not dato and valor_defecto is not None:
            editor.selectEntry(valor_defecto)

    elif isinstance(editor,(WComboMulti,)): # WMC siemre antes que QCB porque es una especializacion
        for entrada in dato:
            editor.set(entrada)
        if len(dato) == 0 and valor_defecto is not None:
            editor.set(valor_defecto)
    elif isinstance(editor,WComboBox):
        if dato:
            editor.setCurrentValue(dato)
        elif valor_defecto:
            editor.setCurrentValue(valor_defecto)
        else:
            editor.setCurrentIndex(-1)
    elif isinstance(editor,WComboBoxIdx):
        if dato:
            if is_number(dato):
                editor.setCurrentIndex(dato)
            else:
                editor.setCurrentIndex(parent.currentList.index(dato))
        elif valor_defecto:
            if is_number(valor_defecto):
                editor.setCurrentIndex(valor_defecto)
            else:
                editor.setCurrentIndex(parent.currentList.index(valor_defecto))
        else:
            editor.setCurrentIndex(-1)
            
    elif isinstance(editor,QComboBox):
        if dato:
            editor.setCurrentIndex(editor.findText(dato))
        elif valor_defecto:
            editor.setCurrentIndex(editor.findText(valor_defecto))
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
        return  editor.get() # __multiListUnload(parent,editor)
    elif isinstance(editor, (WComboMulti,)):
        return editor.get()                
    elif isinstance(editor,QTextEdit):
        return editor.document().toPlainText()
    elif isinstance(editor,QDialog):
        return editor.getData()
    elif isinstance(editor,WComboBox):
        return editor.currentItemInfo()
        #return [editor.currentIndex(),editor.currentText()]
    elif isinstance(editor, QComboBox):
        return editor.currentText()
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



class WSheet(QTableWidget):
    """
    """
    resized = pyqtSignal()
    contextChange = pyqtSignal()
    rowAdded = pyqtSignal(int)
    rowRemoved =pyqtSignal(int)

    def __init__(self,row,col,delegate=None,parent=None):
        super().__init__(row,col,parent)
        self.editContext = {}
        self.auxContext = {}
        self.initialize()
        if delegate:
            sheetDelegate = delegate(self)
            self.setItemDelegate(sheetDelegate)
       
        #FIXME no funciona
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        if row < 10:
            makeTableSize(self)

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

    def setAuxContext(self,data=None,**kwparm):
        """
        probably obsolete
        """
        changed = False
        for dato in kwparm:
            if self.auxContext.get(dato) != kwparm.get(dato):
                changed = True
                break
        if changed:
            self.contextChange.emit()
            self.initialize()
        for dato in kwparm:
            self.auxContext[dato] = kwparm[dato]
            
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
                        result[row][col] = self.get(row,col) #.data(USER)
                    else:
                        result[row][col] = None
        if self.columnCount() == 1:
            return [ elem[0] for elem in result]
        else:
            return result
    
    def setData(self,row,col,dato,role=None,split=False):

        item =  self.item(row,col)
        if not item:
            self.initializeCell(row,col)
        if not role:
            if split or self.hasSplitData(row,col,dato):
                cdato = self.getSplitData(row,col,dato)
                item.setData(USER,cdato[0])
                item.setData(DISP,cdato[1])
            else:
                item.setData(DISP,dato)
                #item.setData(USER,dato)
        else:
            item.setData(role,dato)
            
    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def set(self,x,y,value):
        return self.setData(x,y,value)

    def getData(self,x,y,role=None):
        if not role:
            return self.get(x,y)
        else:
            item = self.item(x,y)
            return item.data(role)

    
    def get(self,x,y):
        item = self.item(x,y)
        dato = item.data(USER)
        if dato is None:
            dato = item.data(DISP)
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
        if isinstance(dato,(list,tuple)):
            return dato[0:2]
        else:
            return [dato,dato]
    
    def setEnabled(self,*lparm): #x,y,state):
        state = lparm[-1]
        if len(lparm) == 1:
            super().setEnabled(state)
            return 
        if state:
            self.item(x,y).setFlags( Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled )
            self.item(x,y).setBackground(QColor(Qt.white))
        else:
            self.item(x,y).setFlags(Qt.ItemIsSelectable )
            self.item(x,y).setBackground(QColor(Qt.gray))
            
    def getContextConstraint(self,x,y):
        if self.editContext:
            for clave in ((x,y),('*',y),(x,'*'),('*','*')):
                if clave in self.editContext:
                    return self.editContext[clave]
        return None

            
class WListView(QListView):
    extIdx = 1 
    intIdx = 0
    def __init__(self,parent=None):
        super().__init__(parent)
        self.baseList = None
        self.keepPosition = True
        self.setModel(QStandardItemModel())
        """
        Las siguientes lineas hacen la magia de activar el drag and drop
        """
        self.setSelectionMode(self.SingleSelection)
        self.setAcceptDrops(True);
        self.setDragEnabled(True);
        #self.setSelectionBehavior(self.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
       
    def _makeItem(self,data):
        if isinstance(data,(list,tuple)):
            extdata = data[WListView.extIdx]
            intdata = data[WListView.intIdx]
        else:
            extdata = intdata = data
        item = QStandardItem(extdata)
        item.setData(intdata,Qt.UserRole +1)
        return item
    
    def _appendRow(self,rowData):
        self.model().appendRow((self._makeItem(rowData),))
        
    def _insertRow(self,elem,pos):
        self.model().insertRow(pos,(self._makeItem(elem),))

    def _getRow(self,item):
        ext = item.data(Qt.DisplayRole)
        intnl = item.data(Qt.UserRole +1)
        if intnl is None:
            intnl = ext
        return [intnl,ext]

    def find(self,value,role=None):
        start = self.model().index(0,0,QModelIndex())
        if role is not None:
            resultIdx = self.model().match(start,role,value,-1,Qt.MatchExactly|Qt.MatchCaseSensitive)
        else:
            resultIdx = self.model().match(start,Qt.UserRole  +1,value,-1,Qt.MatchExactly|Qt.MatchCaseSensitive)
            if not resultIdx:
                resultIdx = self.model().match(start,Qt.DisplayRole,value,-1,Qt.MatchExactly|Qt.MatchCaseSensitive)
        if not resultIdx:
            return None
        else:
            retorno = [self.model().itemFromIndex(idx) for idx in resultIdx ]
            return retorno

    def addItems(self,array=None):
        self.model().clear()
        if not array:
            self.baseList = None
        else:
            self.baseList = array
            for elem in array:
                self._appendRow(elem)
       
    def addRow(self,elem):
        self._appendRow(elem)
        
    def insertRow(self,pos,elem):
        self._insertRow(self,elem,pos)
       
    def index(self,value):
        result = self.find(value)
        if not result:
            return None
        else:
            return [ item.row() for item in result ]
  
    def content(self,pos=None):
        agay = []
        for item in traverse(self.model()):
            # it only works with plain models
            if pos is None:
                agay.append(self._getRow(item))
            else:
                agay.append(self._getRow(item)[pos])
        return agay

    def removeEntry(self,value):
        entryList = []
        donde = self.find(value)
        if donde:
            for elem in donde:
                entryList.append(self.model().takeRow(elem.row()))
        return entryList
            
    def takeRow(self,row):
        return self.model().takeRow(row)
    
    def joinRow(self,row):
        self.model().appendRow(row)
       
    def itemValue(self,item):
        return self.getRow(item)

    def selectedItems(self):
        result = []
        for index in self.selectedIndexes():
            result.append(self.model().itemFromIndex(index))
        return result
 
class WMultiList(QWidget):
    """
    WIP
    Widget para seleccionar elementos de una lista y enviarlos a otra.
    """
    def __init__(self,lista=None,initial=None,format=None,cabeceras=None,parent=None):
        super().__init__(parent)
        self.disponible = WListView()
        self.selecto =WListView()
        self.anyade = QPushButton('Añadir')
        self.elimina = QPushButton('Eliminar')
        self.keepPosition = True  #so this behaviour is  selectable
        
        origenlayout=QVBoxLayout()
        self.origenCabecera = QLabel(cabeceras[0] if cabeceras else 'Elementos disponibles')
        origenlayout.addWidget(self.origenCabecera)
        origenlayout.addWidget(self.disponible)
        
        destinolayout=QVBoxLayout()
        self.destinoCabecera = QLabel(cabeceras[1] if cabeceras else 'Elemenos seleccionados')
        destinolayout.addWidget(self.destinoCabecera)
        destinolayout.addWidget(self.selecto)

        if format == 'm':
            texto = 'Seleccione origen/destino pulsando doble click'
            textoWdt = QLabel(texto)
            meatlayout = QGridLayout()
            meatlayout.addWidget(self.origenCabecera,1,0)
            meatlayout.addWidget(self.destinoCabecera,1,1)
            meatlayout.addWidget(self.disponible,2,0)
            meatlayout.addWidget(self.selecto,2,1)
            meatlayout.addWidget(textoWdt,3,0)
        elif format == 'c':
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

        #TODO itemDoubleClicked not avaliable
        self.disponible.doubleClicked.connect(self.setSelectItem)
        self.selecto.doubleClicked.connect(self.unsetSelectItem)
        self.anyade.clicked.connect(self.setSelectItem)
        self.elimina.clicked.connect(self.unsetSelectItem)
    
        
        self.origList = []
        
        self.load(lista,initial)
     
    def clear(self):
        self.disponible.model().clear()
        self.selecto.model().clear()
        
    def addItems(self,lista):
        self.clear()
        if lista is not None:
            self.origList = lista #[ entry for entry in lista ]
            self.disponible.addItems(lista)
   
        
    def load(self,lista,initial):
        self.addItems(lista)
        selectModel = QStandardItemModel()
        self.selecto.setModel(selectModel)
        if initial is not None:
            self.setEntries(initial)

    def setItem(self,item):
        mitem = self.disponible.model().takeRow(item.row())
        self.selecto.joinRow(mitem)
    
    def unsetItem(self,item):
        if self.keepPosition:
            opos = self._getOrigPos(self.selecto._getRow(item)[0])
            mirow = self.selecto.model().takeRow(item.row())
            if opos <0:
                self.disponible.joinRow(mirow)
            else:
                self.disponible.model().insertRow(opos,mirow)
        else:
            mirow = self.selecto.model().takeRow(item.row())
            self.disponible.joinRow(mirow)


    def _getOrigPos(self,value):
        """
        permite devolver un item a su posicion original en disponible tras removerlo.
        Es un esfuerzo un poco costoso, pero ...
        
        """
        listaValores = [entry[0] if isinstance(entry,(list,tuple)) else entry for entry in  self.origList]
        try:
            pos =   listaValores.index(value)
        except ValueError:
            return -1
        if pos < 0:
            return pos
        for k in range(pos -1,-1,-1):
            anterior = listaValores[k]
            opos = self.disponible.index(anterior)
            if opos: 
                return opos[0] +1
            else:
                continue
        return 0
        

    # slots
    def setSelectItem(self,checked):
        """
        checked is not used
        """
        lista = self.disponible.selectedItems()
        for item in lista:
            self.setItem(item)
            
        
    def unsetSelectItem(self,checked):
        """
        checked is not used, but demanded by signal.
        self.keepPosition determines whether the removed value returns to its original place or not
            pretty from the user's point of view,  consuming internally
        """
        lista = self.selecto.selectedItems()
        for item in lista:
            self.unsetItem(item)
            
            #TODO falta restaurar la posicion
            
    def setEntries(self,lista):
        #FIXME ¿y si ya existe?
        conjunto = norm2List(lista)
        for entrada in conjunto:
            orig = self.disponible.find(entrada)
            if not orig:
                self.selecto.addRow(entrada)
            else:
                self.setItem(orig[0])

    def unsetEntries(self,lista):
        conjunto = norm2List(lista)
        for entrada in conjunto:
            orig = self.selecto.find(entrada)
            if not orig:
                pass
            else:
                self.unsetItem(self,orig[0])

    def set(self,lista):
        return self.setEntries(lista)
    def get(self,pos=0):
        return self.selecto.content(pos)

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

class WComboBox(QComboBox):
    """
    
    Un intento para que los combos con valor interno y externo sean transparentes (lo mas posible)
    He  sobrecargado las add* y las insert* para que admitan cualquier tipo de valor
    Ademas he creado dos metodos genericos currentValue y currentItemInfo para obtener los datos interno y todos respectivamente
    He creado un metodo index que hace que el combo se comporte como una lista
    
    """
    def addItems(self,datos):
        for item in datos:
            self.addItem(item)
            
    def addItem(self,*lparm,**kwparm):
        if kwparm:
            super().addItem(*lparm,**kwparm)
        else:
            if isinstance(lparm[-1],(list,tuple)):
                gparm = list(lparm[:])
                gparm[-1]=lparm[-1][1]
                super().addItem(*gparm,userData=lparm[-1][0])
            else:
                super().addItem(*lparm)
             
    def insertItems(self,index,datos):
        for idx,item in enumerate(datos):
            self.insertItem(index + idx,item)
        
    def insertItem(self,*lparm,**kwparm):
        if kwparm:
            super().insertItem(*lparm,**kwparm)
        else:
            if isinstance(lparm[-1],(list,tuple)):
                gparm = list(lparm[:])
                gparm[-1]=lparm[-1][1]
                super().insertItem(*gparm,userData=lparm[-1][0])
            else:
                super().insertItem(*lparm)
                
    def currentValue(self):
        dato = self.itemData(self.currentIndex())
        if not dato:
            return self.currentText()
        else:
            return dato

    def currentItemInfo(self):
        idx = self.currentIndex()
        txt = self.currentText()
        val = self.itemData(idx)
        if not val:
            val = txt
        return [val,txt,idx]

    def index(self,dato,role=None):
        if role:
            return self.findData(dato,role)
        else:
            idx = self.findData(dato)
            if idx < 0:
                idx = self.findText(dato)
            return idx
        
    def setCurrentValue(self,value,role=None):
        #TODO ¿y si es una estructura?
        idx = self.index(value,role)
        if idx < 0:
            if self.isEditable():
                self.addItem(value)
                idx = self.count() -1
            else:
                raise(ValueError)
        self.setCurrentIndex(idx)
        
        
    def listText(self):
        pass
    
    def listData(self,role=Qt.UserRole):
        pass
        
class WComboBoxIdx(WComboBox):
    """
    Un nombre distinto para el combobox que usa como dato el indice, no el valor.
    Sobrecargamos currentValue para que devuelva el  índice En lo demás absolutamente identico al combo
    """
    def currentValue(self):
        return self.currentIndex()
 
    def setCurrentValue(self,value,role=Qt.UserRole):
        #TODO ¿y si es una estructura?
        if is_number(value):
            self.setCurrentIndex(value)
        else:
            self.setCurrentIndex(self.index(value,DISP))
            
class WComboMulti(QComboBox):
    """ Una variante de combo con seleccion multiple
    """
    textoCabecera = 'Seleccione los elementos'
    
    def __init__(self,parent=None):
        super(WComboMulti,self).__init__(parent)
        self.modelo = QStandardItemModel()
        self.setModel(self.modelo)
        self.view().pressed.connect(self.handleItemPressed)
   

    def _makeItem(self,entrada):
            item = QStandardItem()
            if isinstance(entrada,(list,tuple)):
                item.setData(entrada[0],USER)
                item.setData(entrada[1],DISP)
            else:
                item.setData(entrada,USER)
                item.setData(entrada,DISP)
            item.setData(Qt.Unchecked,Qt.CheckStateRole)
            item.setFlags(Qt.ItemIsEnabled)
            return item
        
    def addItem(self,entrada):
        self.modelo.appendRow(self._makeItem(entrada))
        
    def insertItem(self,pos,entrada):
        self.modelo.insertRow(pos,self._makeItem(entrada))
        
    def addItems(self,data):
        self.modelo.clear()
        item = QStandardItem(WComboMulti.textoCabecera)
        self.model().setItem(0,0,item)
        for entrada in data:
            self.addItem(entrada)

    def insertItems(self,pos,data):
        self.modelo.clear()
        for k,entrada in enumerate(data):
            self.insertItem(pos +k,entrada)
        
    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if index.row() == 0:
            return
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
            self.updateHdr('remove',item.data(DISP))
        else:
            item.setCheckState(Qt.Checked)
            self.updateHdr('set',item.data(DISP))
            
    def set(self,dato):
        values = norm2List(dato)
        for value in values:
            pos = self.index(value)
            if pos > 0:
                item = self.model().item(pos,0)
            elif pos < 1 and self.isEditable():
                self.model().appendRow(self._makeItem(value))
                item = self.model().item(self.model().rowCount() -1,0)
            else:
                return None
            item.setData(Qt.Checked,Qt.CheckStateRole)
            self.updateHdr('set',item.data(DISP))
                
    def unset(self,values):
        for value in values:
            pos = self.index(value)
            if pos > 0:
                item = self.model().item(pos,0)
                item.setData(Qt.Unchecked,Qt.CheckStateRole)
                self.updateHdr('remove',item.data(DISP))

                
    def reset(self):
        for idx in range(1,self.count()):
            if self.itemData(idx,Qt.CheckStateRole) == Qt.Checked:
                self.setItemData(idx,Qt.Unchecked,Qt.CheckStateRole)
        cabItem = self.model().item(0,0)
        cabItem.setData(WComboMulti.textoCabecera,DISP)
    
    def get(self,role=USER):
        result = []
        for k in range(1,self.count()):
            if self.itemData(k,Qt.CheckStateRole) == Qt.Checked :
                result.append(self.itemData(k,role))
        return norm2String(result)
    
    def updateHdr(self,action,value):
        cabecera = self.itemData(0,DISP)
        if cabecera ==WComboMulti.textoCabecera:
            elementos = set()
        else:
            elementos = set(norm2List(cabecera))
        if action == 'set':
            elementos.add(value)
        else:
            elementos.remove(value)
            
        cabItem = self.model().item(0,0)
        if len(elementos) == 0:
            cabItem.setData(WComboMulti.textoCabecera,DISP)
        else:
            cabItem.setData(norm2String(elementos),DISP)
        self.setCurrentIndex(0)
        
    def index(self,text):
        # find data choca con el elemento 0
        for k in range(1,self.count()):
            if text in (self.itemData(k,DISP),self.itemData(k,USER)):
                return k
        return -1
      
            

class WPowerTable(WSheet):
    """
 
    """
    def __init__(self,row,col,context=None,parent=None):
        super().__init__(row,col,delegate=None,parent=parent)
        self.editContext = context
        self.initialize()
    #def initialize(self):
    #def initializeRow(self,x):
    def initializeCell(self,x,y):
        constraint = self.getContextConstraint(x,y)
        if not constraint:
            super().initializeCell(x,y)
        else:
            editor = self._setupEditorFromContext(constraint)
            if not editor:
                super().initializeCell(x,y)
            else:
                self.setCellWidget(x,y,editor)
                self.setData(x,y,constraint.get('default'))

    #def openContextMenu(self,position):
    #def addRow(self,idx=None,emit=True):
    #def removeRow(self,idx=None,emit=True):
    #def setContext(self,data=None,**kwparm):
    #def loadData(self,data):
    #def unloadData(self):
    def setData(self,row,col,dato,role=None,split=False):
        constraint = self.getContextConstraint(row,col)
        if not constraint:
            super().setData(row,col,role,split)
            return
        self._createComboContext(constraint)
        editor = self.cellWidget(row,col)
        setWidgetData(self,editor,dato,constraint.get('default'))
    #def resizeEvent(self, event):
    #def set(self,x,y,value):
    def getData(self,row,col,role=None):
        constraint = self.getContextConstraint(row,col)
        if not constraint:
            return super().getData(row,col,role)
        self._createComboContext(constraint)
        editor = self.cellWidget(row,col)
        return getWidgetData(self,editor)
        
    def get(self,x,y):
        constraint = self.getContextConstraint(x,y)
        if not constraint:
            return super().get(x,y)
        else:
            return self.getData(x,y)
    #def values(self):
    #def fill(self,data):
    #def getItem(self,x,y):
    #def hasSplitData(self,x,y,dato):
    #def getSplitData(self,x,y,dato):
    #def setEnabled(self,x,y,state):
    def _setupEditorFromContext(self,specs): #,parent,option,index):
        if not specs or not specs.get('editor'):
            return None
        editorObj = specs['editor'] 
        editor = editorObj()
        """
        __REUSABLE__
        Ejecucion dinamica de acciones de un widget (o cualquier objeto python)
        podría ser reusable (ver tambien "user functions", que es un poco mas complejo
        """
        typeSpec = specs.get('options')
        if typeSpec is not None:
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
        fullList = specs.get('source')
        if editorObj in (WComboBox,WComboBoxIdx,WComboMulti,QComboBox):
             editor.addItems(fullList)
        #if fullList is not None:
            #if isinstance(fullList[0],(list,tuple)):
                #currentList = [ elem[1] for elem in fullList]
            #else:
                #isDouble = False
                #currentList = fullList
            #if editorObj in  (WComboBoxIdx,QComboBox):
                #editor.addItems(currentList)
        return editor
        
    def _createComboContext(self,specs):
        if not specs or not specs.get('source'):
            self.fullList = None
            self.currentList = None
            self.isDouble = False
            return
        self.fullList = specs.get('source')
        self.currentList = self.fullList
        if isinstance(self.fullList[0],(list,tuple)):
            self.isDouble = True
            self.currentList = [ elem[1] for elem in self.fullList]
        else:
            self.isDouble = False


    """
    """
    #def __init__(self,row,cols,parent=None):
        #super().__init__(self,row,cols,parent=parent)
    #def setRowModelDef(self,contexto):
        #self.edtiContext = contexto
    #def addCell(self,x,y,colDef,defVal):
        #print(" Clase obsoleta y funcion no compatible ")
        #return
    #def appendRow(self,row):
        #self.addRow(row)
        
"""
delegados estandar

"""
    
class sheetDelegate(QStyledItemDelegate):
    def __init__(self,context,parent=None):
        super().__init__(parent)
        self.context = self.convertContext(context)
        
    def createEditor(self,parent,option,index):
        row = index.row()
        col = index.column()
        specs = self.elemContext(row,col)
        #if len(specs) < 4:
            #for k in range(len(specs),4):
                #specs.append(None)
        return self._setupEditorFromContext(specs,parent,option,index)
    
    def _setupEditorFromContext(self,specs,parent,option,index):
        if not specs or not specs.get('editor'):
            return super().createEditor(parent,option,index)
        editorObj = specs['editor'] 
        editor = editorObj(parent)
        typeSpec = specs.get('options')
        if typeSpec is not None:
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
        self.fullList = specs.get('source')
        if self.fullList is not None:
            if editorObj in (WComboBox,WComboBoxIdx,WComboMulti,QComboBox,WMultiList):
                editor.addItems(self.fullList)
        return editor

    def setEditorData(self, editor, index):
        row = index.row()
        col = index.column()
        dato = index.data()  #Qt.DisplayRole
        specs = self.elemContext(row,col)
        if specs:
            def_value = specs.get('default')
        else:
            def_value = None
        setWidgetData(self,editor,dato,def_value)
        
    def setModelData(self,editor,model,index):
        dato = getWidgetData(self,editor)

        #if type(editor) in (QComboBox,) and self.isDouble:
            #model.setData(index,dato[0],USER)
            #model.setData(index,dato[1],DISP)
        if type(editor) == WComboBoxIdx:
            model.setData(index,dato[2],USER)
            model.setData(index,dato[1],DISP)
        elif type(editor) == WComboBox:
            model.setData(index,dato[0],USER)
            model.setData(index,dato[1],DISP)
        elif isinstance(dato,(list,tuple)):
            dato = norm2String(dato)
            model.setData(index,dato)
        else:
            model.setData(index,dato)

    def elemContext(self,row,col):
        for clave in ((row,col),('*',col),(col,'*'),('*','*')):
            if clave in self.context:
                return self.context[clave]
        return None  #FIXME ¿a default?
    
    def convertContext(self,oldContext,oldStyle=None):
        """
        funcion virtual. Ademas es estática
        """
        return oldContext
    


class rowSheetDelegate(sheetDelegate):
    """
            Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
            context[0] titulos de las filas
            context[1] widget a utilizar (defecto QLineEdit)
            context[2] parametrizacion del widget (metodo:valor)
            ...
    """
    def convertContext(self,oldContext,oldStyle='row'):
        contexto = {}
        for k,item in enumerate(oldContext):
            contexto[(k,0)] = {}
            #if item[0]:
                #contexto[(k,0)]['default']=item[0]
            if item[1]:
                contexto[(k,0)]['editor']=item[1]
            if len(item) > 2 and item[2]:
                contexto[(k,0)]['options']=item[2]
            if len(item) > 3 and item[3]:
                contexto[(k,0)]['source']=item[3]
        return contexto
    
class columnSheetDelegate(sheetDelegate):
    def convertContext(self,oldContext,oldStyle='column'):
        contexto = {}
        for k,item in enumerate(oldContext[1:]):
            contexto[('*',k)] = {}
            if item[0]:
                contexto[('*',k)]['default']=item[0]
            if item[1]:
                contexto[('*',k)]['editor']=item[1]
            if len(item) > 2 and item[2]:
                contexto[('*',k)]['options']=item[2]
            if len(item) > 3 and item[3]:
                contexto[('*',k)]['source']=item[3]
        return contexto
        
class WDataSheet(WSheet):
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
        """
        realmente cambio todo, pero lo necesito por compatibilidad
        """
        self.changeContext(context)
        
    def addRow(self,line=None):
        super().addRow(line)
    def valueCol(self,col=0):
        pass

class WPropertySheet(WSheet):
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
        if  specs[1] in (QComboBox,WComboBoxIdx,WComboMulti,WComboBox) :
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
