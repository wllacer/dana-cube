#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Todo list tras completar validators y setters
-> en repeatable add debe dividirse en (insert after, insert before, append). General de editTree
-> DONE Incluir llamada a la consulta de guia
-> Incluir llamada al grand total
-> DONE Las fechas artificiales (trimestres, cuatrimestres, ...) como opciones de menu aqui y no en info2*
-> Para sqlite que el selector de base de datos sea el selector de ficheros del sistema
-> Copy to other place
-> Restore

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from support.gui.treeEditor import *
from research.cubeTree import *
from support.gui.widgets import WMultiCombo,WPowerTable,WMultiList,WDelegateSheet,makeTableSize

from base.datadict import DataDict

from PyQt5.QtWidgets import QFrame

def srcTables(*lparm,**kwparm):
    return ['pepe','paco','hugo','mariano' ]
"""
GETTERS
    executed at start of SetEditorData 
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist 
    input
            editor,
            item,
            view,
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)
    output
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)

SETTERS
    executed at the end of SetModelData
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist
        input  *lparm
            item = lparm[0]
            view = lparm[1]
            context = lparm[2]   Fundamentalmente para obtener el valor original context['data']
            ivalue / values = lparm[3]
            dvalue = lparm[4]
        output
            item, the edited item
"""

def getCategories(*lparm):
    editor = lparm[0]
    item = lparm[1]
    view = lparm[2]
    dato = lparm[3]
    display = lparm[4]
    
    n,i,t = getRow(item)
    if n.data() ==  'categories':
        dato = []
        for k in range(n.rowCount()):
            hijo = n.child(k,0)
            linea = [ None for m in range(3) ]
            for l in range(hijo.rowCount()):
                base = hijo.child(l,0).data()
                valor = hijo.child(l,1).data()
                if base == 'result':
                    linea[0] = valor
                elif base == 'condition':
                    linea[1] = valor
                elif base == 'values':
                    valores = []
                    for m in range(hijo.child(l,0).rowCount()):
                        valores.append(hijo.child(l,0).child(m,1).data())
                    linea[2] = norm2String(valores)
                elif base == 'default':
                    linea[0] = base
                    linea[2] = valor
            dato.append(linea)
    else:
        linea = [ None for m in range(3) ]
        for l in range(n.rowCount()):
            base = n.child(l,0).data()
            valor = n.child(l,1).data()
            if base == 'result':
                linea[0] = valor
            elif base == 'condition':
                linea[1] = valor
            elif base == 'values':
                hijo = n.child(l,0)
                valores = []
                for m in range(hijo.rowCount()):
                    valores.append(hijo.child(m,1).data())
                linea[2] = norm2String(valores)
                
            elif base == 'default':
                linea[0] = base
                linea[2] = valor
                break
        dato = linea
        
    return dato,display
                
def setCategories(*lparm):
    item = lparm[0]
    view = lparm[1]
    context = lparm[2]  
    values = lparm[3]

    if isinstance(values[0],(list,tuple)):
        model = item.model()
        if item.column() != 0:
            item = model.itemFromIndex(item.index().sibling(item.row(),0))
        contador = item.rowCount()
        for k in range(contador):
            model.removeRow(0,item.index())
        for entrada in values:
            if entrada[0] == '':
                continue
            item.appendRow(makeRow(entrada[0],None,'categories'))
            kitem = item.child(item.rowCount() -1,0)
            if entrada[0] == "default":
                kitem.appendRow(makeRow('default',entrada[2],'default'))
                continue
            kitem.appendRow(makeRow('result',entrada[0],'result'))
            kitem.appendRow(makeRow('condition',entrada[1],'condition'))
            kitem.appendRow(makeRow('values',entrada[2],'values'))
            view.convertToList(kitem.child(kitem.rowCount()-1))

        #pajaro = tree2dict(item,isDictFromDef)
        #pprint(pajaro)
    elif values[0] == 'default':
        model = item.model()
        if item.column() != 0:
            item = model.itemFromIndex(item.index().sibling(item.row(),0))
        dataItm = item.child(0,1)
        item.setData(values[2],Qt.DisplayRole)
        dataItm.setData(values[2])
        dataItm.setData(values[2],Qt.DisplayRole)
    else:
        model = item.model()
        if item.column() != 0:
            item = model.itemFromIndex(item.index().sibling(item.row(),0))
        contador = item.rowCount()
        for k in range(contador):
            hijo = item.child(k,2)
            if k == 2:
                rowHead = hijo.parent().child(2,0)
                for j in range(rowHead.rowCount()):
                    model.removeRow(0,rowHead.index())
                for entrada in norm2List(values[k]):
                    rowHead.appendRow(makeRow(None,entrada))
            else:
                hijo.setData(values[k])
            
    return item


def validateCategories():
    pass

class catDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.condiciones = ('in','between','not in','not between','=','!=','>','<=','>','>=')
        
    def createEditor(self,parent,option,index):
        if index.column() in (0,2):
            return super().createEditor(parent,option,index)
        elif  index.column() == 1:
            editor = QComboBox(parent)
            editor.addItems(self.condiciones)
        return editor
    def setEditorData(self, editor, index):
        if index.column() in (0,2):
            return super().setEditorData(editor,index)
        elif  index.column() == 1:
            if index.data():
                pos = self.condiciones.index(index.data())
                editor.setCurrentIndex(pos)
            else:
                editor.setCurrentIndex(-1)
            
    def setModelData(self,editor,model,index):
        #TODO con la estructura real debe ser mas complejo
        if index.column() in (0,2):
            return super().setModelData(editor,model,index)
        elif  index.column() == 1:
            if editor.currentIndex() == -1:
                return
            nuevo = editor.currentText()
            if nuevo == index.data():
                return 
            model.setData(index,nuevo)
  

class catEditor(QDialog):
    """
    """
    def __init__(self,parent=None,):
        super().__init__(parent)
        
        self.defaultData = None
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.msgLine = QLabel()
        
        clauseLbl = QLabel('Eliga el proceso de categorias')
        self.sheet = WDelegateSheet(5,3,catDelegate)
        self.sheet.setHorizontalHeaderLabels(('Resultado','Op','Valores                     '))
        defaultLbl = QLabel('Valor por defecto ')
        self.defaultValue = QLineEdit()
        
        resultLbl = QLabel('Valor a devolver')
        self.resultLE = QLineEdit()
        self.conditionCB = QComboBox()
        conditionLbl = QLabel('Clausula logica')
        self.conditionCB.addItems(('in','between','not in','not between','=','!=','>','<=','>','>=')) #FIXME normalizar
        valoresLb = QLabel('Valores')
        self.valuesLE = QLineEdit()
        
        self.groupFrame = QFrame()
        self.detailFrame = QFrame()
        groupLayout = QVBoxLayout()
        detailLayout = QVBoxLayout()
        
        meatlayout = QVBoxLayout()
    
        groupLayout.addWidget(clauseLbl)
        groupLayout.addWidget(self.sheet)
        groupLayout.addWidget(defaultLbl)
        groupLayout.addWidget(self.defaultValue)
        
        self.groupFrame.setLayout(groupLayout)

        detailLayout.addWidget(resultLbl)
        detailLayout.addWidget(self.resultLE)
        detailLayout.addWidget(conditionLbl)
        detailLayout.addWidget(self.conditionCB)
        detailLayout.addWidget(valoresLb)
        detailLayout.addWidget(self.valuesLE)
        
        self.detailFrame.setLayout(detailLayout)
        
        meatlayout.addWidget(self.groupFrame)
        meatlayout.addWidget(self.detailFrame)
        meatlayout.addWidget(self.msgLine)
        meatlayout.addWidget(buttonBox)
        
        self.setLayout(meatlayout)
        
        self.detailFrame.hide()
        self.groupFrame.show()
        
        # en esta posicion para que las señales se activen tras la inicializacion
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        self.sheet.resized.connect(self.resizeSheet)
 
    def setData(self,dato):
        self.defaultData = dato
        self.__setData(dato)
        
    def __setData(self,dato):
        if not dato:
            return
        if isinstance(dato[0],(list,tuple)):
            self.groupFrame.show()
            self.detailFrame.hide()
            if len(dato) > self.sheet.rowCount():
                for k in range(self.sheet.rowCount(),len(dato)):
                    self.sheet.addRow(emit=False)
            i = 0
            for linea in dato:
                if linea[0] == "default":
                    self.defaultValue.setText(linea[2])
                    continue
                for j,campo in enumerate(linea):
                    if j >= self.sheet.columnCount():
                        break
                    self.sheet.setData(i,j,campo)
                i += 1
            for i in range(len(dato),self.sheet.rowCount()):
                self.sheet.initializeRow(i)
        elif dato[0] == 'default':
            self.groupFrame.hide()
            self.detailFrame.show()
            self.resultLE.setText(dato[0])
            self.conditionCB.setCurrentText(dato[1])
            self.valuesLE.setText(dato[2])
            self.resultLE.setEnabled(False)
            self.conditionCB.hide()
        else:
            self.groupFrame.hide()
            self.detailFrame.show()
            self.resultLE.setText(dato[0])
            self.conditionCB.setCurrentText(dato[1])
            self.valuesLE.setText(dato[2])
            self.resultLE.setEnabled(True)
            self.conditionCB.show()

    def getData(self):
        if not self.defaultData or isinstance(self.defaultData[0],(list,tuple)):
            dato = []
            for i in range(self.sheet.rowCount()):
                linea = []
                for j in range(self.sheet.columnCount()):
                    linea.append(self.sheet.item(i,j).text())
                dato.append(linea)
            if self.defaultValue.text() != "":
                dato.append(["default",None,self.defaultValue.text()])
            return dato
        elif self.defaultData[0] == 'default':
            dato = [ None for k in range(3) ]
            dato[0] = 'default'
            dato[2] = self.valuesLE.text()
            return dato
        else:
            dato = [ None for k in range(3) ]
            dato[0] = self.resultLE.text()
            dato[1] = self.conditionCB.currentText()
            dato[2] = self.valuesLE.text()
            return dato
        
    def reject(self):
        self.__setData(self.defaultData)
        super().reject()

    def resizeSheet(self):
        #makeTableSize(self.sheet)
        totalwidth = self.sheet.size().width()
        self.sheet.setColumnWidth(0,totalwidth * 2 // 10)
        self.sheet.setColumnWidth(1,totalwidth * 1 //10)
        self.sheet.setColumnWidth(2,totalwidth * 7 //10)
 
