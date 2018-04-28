#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

import user as uf
import math 

from support.util.uf_manager import *
from base.ufhandler import functionFromName
from support.util.jsonmgr import *
from support.gui.widgets import WMultiCombo,WPowerTable, WMultiList, WNameValue
from support.util.record_functions import norm2List,norm2String
import base.config as config

from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView, QStyledItemDelegate, QSpinBox, QListWidget, QPushButton, QVBoxLayout,QLabel, QWidget, QCheckBox

from research.ufTreeUtil import *
"""
Funciones para leer la configuracion de user functions. Reutilizadas, creo
"""


 
class ufTreeMgr(QTreeView):
    """
    """
    def __init__(self,model,treeDef,firstLevelDef,ctxFactory,parent=None):
        """
        parametros model .-> modelo a procesar
                           treeDef -> Definicion del arbol
                           firstLevelDef -> List of first level elements
                           ctxFactory -> generador de contexto
        """
        super(ufTreeMgr, self).__init__(parent)
        self.parentWindow = parent
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.treeDef = treeDef
        self.firstLevelDef = firstLevelDef
        self.ctxFactory = ctxFactory
        self.view.setAlternatingRowColors(True)
        #self.view.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        
        self.baseModel  = model
        parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        self.view.setModel(self.baseModel)
        
        if not config.DEBUG:
            self.view.hideColumn(2) # eso no interesa al usuario final        

        self.view.expandAll() # es necesario para el resize
        for m in range(self.baseModel.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.collapseAll()

        delegate = ufTreeDelegate(self)
        self.setItemDelegate(delegate)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)


        print('inicializacion completa')
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def openContextMenu(self,position):
        menu = QMenu()
        self.ctxMenu = []
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        context = self.ctxFactory(index)
        n = context.get('rowHead')
        
        edit_data = self.treeDef.get(context.get('editType'),{})
        if context.get('topLevel',False):
            for entrada in self.firstLevelDef:
                self.ctxMenu.append(menu.addAction("Add new {}".format(entrada),
                                    lambda i=self.model().invisibleRootItem(),j=entrada:self.actionAddTop(i,j))) 
            self.ctxMenu.append(menu.addAction("Copy",lambda i=n:self.actionCopy(i)))
            self.ctxMenu.append(menu.addAction("Rename",lambda i=n:self.actionRename(i))) 
            menu.addSeparator()
        if 'elements' in edit_data:
            # creo que es lo mas sensible hacer. Localizo los elementos que ya existen
            existentes = set()
            for k in range(n.rowCount()):
                child = n.child(k,0)
                ns,js,ts = getRow(child.index())
                if ts.data():
                    existentes.add(ts.data())
            for elemento in edit_data['elements']:
                if elemento[0] in existentes:
                    pass
                else:
                    self.ctxMenu.append(menu.addAction("Add {}".format(elemento[0]),
                                                   lambda i=n,j=elemento[0]:self.actionAdd(i,j)))
            menu.addSeparator()

        if edit_data.get('objtype','atom') == 'dict' and edit_data.get('elements',None) is None:
            self.ctxMenu.append(menu.addAction("Add name/value pair",lambda i=n:self.actionNameValue(n)))

        if context.get('topLevel',False) or ( not context.get('mandatory',False)):
            self.ctxMenu.append(menu.addAction("Borrar",lambda i=n:self.actionRemove(i)))
        else:
            pass
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def actionRemove(self,item):
        rownr = item.row()
        pai = item.parent()
        if pai is None: #topLevel
            item.model().removeRow(rownr)
        else:
            item.model().removeRow(rownr,pai.index())
    
    def actionAdd(self,item,newItemType):
        edit_data = self.treeDef.get(newItemType,{})
        if item.column() == 0:
            parent = item
        else:
            parent = item.model().itemFromIndex(item.index().sibling(item.row(),0))
        newRow = makeRow(newItemType,edit_data.get('default',None),newItemType)
        if parent is None:
            self.model().appendRow(newRow)
        else:
            parent.appendRow(newRow)
        if edit_data.get('elements'):
            for entrada in edit_data.get('elements'):
                self.actionAdd(newRow[0],entrada[0])
        #TODO falta colocar el foco y validar obligatorios
        for funcion in edit_data.get('setter',[]):
            funcion(newRow[0],self)
        return newRow[0]
    
    def actionAddTop(self,item,newItemType):
        pos = self.actionAdd(item,newItemType)
        self.actionRename(pos)
       
    def actionRename(self,item):
        text = QInputDialog.getText(None, "Nuevo nombre para el nodo: "+item.data(),"Nodo", QLineEdit.Normal,item.data())
        if text[0] and text[0] != '':
            item.setData(text[0],Qt.EditRole)
            item.setData(text[0],Qt.UserRole +1)
       
    def actionCopy(self,item):
        newHead = cloneSubTree(item)
        self.actionRename(newHead)
        
    def actionNameValue(self,item):

        context = self.ctxFactory(item)
        form = WNameValue()
        form.show()
        form.raise_()
        if form.exec():
            values = form.sheet.values()
            for funcion in context.get('edit_tree',{}).get('validators',[]):
                if not funcion(item,values):
                    print('validacion fallida')  #TODO a mensaje o similar
                    #form.sheet.cellWidget(0,0).setFocus()
                    return
            for entrada in values:
                item.appendRow(makeRow(entrada[0],entrada[1],entrada[0]))
            for funcion in context.get('edit_tree',{}).get('setters',[]):
                funcion(item,values)
            
          
class ufTreeDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.context = None 

    def createEditor(self,parent,option,index):
        """
        
        une las funciones de createEditor and setEditorData al mismo tiempo. Simplemente la logica es demasiado enlazada en este caso para separarlo
        
        """
        if index.column() != 1:
            return 
        self.context = self.parent().ctxFactory(index)
        #nomItem, item, tipoItem, headItem, objtype = getRow(index,True)
        #item = headItem
        
        if self.context.get('topLevel',False):
            return 
        if self.context.get('readonly',False):
            return
        #edit_format = treeDef.get(self.context.get('editType'),{})
        edit_format = self.context.get('edit_tree',{})

        item = self.context.get('editPos')
        display = item.data(Qt.DisplayRole)
        dato = item.data(Qt.UserRole +1)
        tipo = type(dato)
        defeditor = edit_format.get('editor',QLineEdit)
        
 
        if tipo == bool or defeditor ==  QCheckBox:
            #TODO hay que ponerle un nombre
            editor = QCheckBox(self.context.get('name'))
            if dato is not None:
                editor.setCheckState(dato)
            else:
                editor.setChecked(edit_format.get('default',False))
        elif defeditor ==  QSpinBox:
            editor = QSpinBox()
            editor.setMaximum(edit_format.get('max',99))
            editor.setMinimum(edit_format.get('min',0))
            if dato is not None:
                editor.setValue(dato)
            else:
                editor.setValue(edit_format.get('default',0))
        elif defeditor in (QComboBox,WMultiCombo,WMultiList):
            editor = defeditor()
            orlist = edit_format.get('source',[])
            if callable(orlist):
                lista = sorted(orlist(item))
            else:
                lista = orlist
            if defeditor ==  QComboBox:
                editor.addItems(lista)
                if dato is not None:
                    editor.setCurrentIndex(lista.index(dato))
                elif edit_format.get('default') is not None:
                    editor.setCurrentIndex(lista.index(edit_format.get('default')))

            elif defeditor in (WMultiCombo,) :
                editor.load(lista)
                aceptados = norm2List(dato)
                for entrada in aceptados:
                    editor.set(entrada)
            elif defeditor in (WMultiList,):
                inicial = []
                if item.column() != 0:
                    item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
                if item.hasChildren():
                    for x in range(item.rowCount()):
                        hijo = item.child(x)
                        valor = index.model().itemFromIndex(hijo.index().sibling(hijo.row(),1))
                        inicial.append(valor.data())
                editor.load(lista,inicial)
        elif defeditor == WPowerTable :
            if item.column() != 0:
                item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            editor = defeditor(item.rowCount() +2,2)
            editor.setHorizontalHeaderLabels(('nombre','valor'))
            context = []
            context.append((QLineEdit,{'setEnabled':False},None))
            context.append((QLineEdit,{'setEnabled':True},None))
            data = []
            for x in range(item.rowCount()):
                childIdx = item.index().child(x,0)
                nomItem,sitem,typeItem = getRow(childIdx)
                datos = [nomItem.data(),branch2text(nomItem)]
                for y,colDef in enumerate(context):
                    editor.addCell(x,y,colDef,defVal=datos[y])


            editor.resizeRowsToContents()
        else:
            if self.context.get('rowHead').hasChildren():
                return
            editor = defeditor()
            editor.setText(dato)
        return editor
            
    def setModelData(self,editor,model,index):

        model = index.model()
        if isinstance(editor, WMultiList):
            values = editor.seleList

            if not self.validator(editor,values):
                print('Rechazada la validacion')
                return
            item = self.context.get('editPos')
            # aqui el proceso de borrado y carga
            if item.column() != 0:
                item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            contador = item.rowCount()
            for k in range(contador):
                model.removeRow(0,item.index())
            for entrada in values:
                item.appendRow(makeRow(None,entrada))
        else:
            if isinstance(editor, QComboBox):
                dvalue = ivalue = editor.currentText() #Un poco valiente
                if dvalue in ('True','False'):
                    ivalue = str2bool(dvalue)            
            elif isinstance(editor, QSpinBox):
                ivalue = editor.value()
                dvalue = str(ivalue)
            elif isinstance(editor, QCheckBox):
                ivalue = editor.isChecked()
                dvalue = str(ivalue)
            elif isinstance(editor, WMultiCombo):
                dvalue = ivalue = editor.get()
            elif isinstance(editor,WPowerTable):
                return
            else:
                dvalue = ivalue = editor.text()
    
            if not self.validator(editor,dvalue,ivalue):
                print('Rechazada la validacion')
                return
            
            if not dvalue:
                model.setData(index,str(index.data(Qt.UserRole +1)),Qt.EditRole)
            else:
                model.setData(index,dvalue, Qt.EditRole)                
            model.setData(index,ivalue, Qt.UserRole +1)
            item = model.itemFromIndex(index.sibling(index.row(),0))
        
        setters = self.context.get('edit_tree',{}).get('setters',[])
        for funcion in setters:
            funcion(item,self.parent())

    def validator(self,editor,*lparms,**kwparms):
        if isinstance(editor,(WMultiList,)):
            values = lparms[0]
            if self.context.get('mandatory') and len(values) == 0:
                print('No hay entradas')
                return False
        else:
            dvalue,ivalue = lparms[0:2]
            if self.context.get('mandatory') and (ivalue is None or dvalue == ''):
                print('sin valor')
                return False
        validators = self.context.get('edit_tree',{}).get('validators',[])
        if len(validators) == 0:
            return True
        else:
            for entry in validators:
                if not validators(self.context.get('editPos'),editor,*lparms,**kwparms):
                    return False
        return True
                

 
if __name__ == '__main__':
    exit()


