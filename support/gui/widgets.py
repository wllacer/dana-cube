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
 

class WMultiList(QWidget):
    """
    WIP
    Widget para seleccionar elementos de una lista y enviarlos a otra.
    """
    def __init__(self,lista=None,initial=None,parent=None):
        super().__init__(parent)
        self.disponible = QListWidget()
        self.selecto = QListWidget()
        self.anyade = QPushButton('Añadir')
        self.elimina = QPushButton('Eliminar')
        
        origenlayout=QVBoxLayout()
        self.origenCabecera = QLabel('Elementos disponibles')
        origenlayout.addWidget(self.origenCabecera)
        origenlayout.addWidget(self.disponible)
        
        destinolayout=QVBoxLayout()
        self.destinoCabecera = QLabel('Elementos seleccionados')
        destinolayout.addWidget(self.destinoCabecera)
        destinolayout.addWidget(self.selecto)

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
        checked is not used
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

        
        
