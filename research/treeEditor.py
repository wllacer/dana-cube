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


 
class TreeMgr(QTreeView):
    """
    """
    def __init__(self,model,treeDef,firstLevelDef,ctxFactory,parent=None):
        """
        parametros model .-> modelo a procesar
                           treeDef -> Definicion del arbol
                           firstLevelDef -> List of first level elements
                           ctxFactory -> generador de contexto
        """
        super(TreeMgr, self).__init__(parent)
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

        delegate = TreeDelegate(self)
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
        
        for linea in edit_data.get('menuActions',[]):
            self.ctxMenu.append(menu.addAction(linea[1],lambda i=n:linea[0](i,self)))
            
        if context.get('topLevel',False) or ( not context.get('mandatory',False)):
            self.ctxMenu.append(menu.addAction("Borrar",lambda i=n:self.actionRemove(i)))
            menu.addSeparator()

        self.getMenuOptionsDetail(menu,n,context)
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def getMenuOptionsDetail(self,menu,rowHead,context):
        """
        parameters:
        menu
        n -> rowHead
        context
        
        aqui pongo las funciones que dependen del tipo de objeto
        """
        edit_data = self.treeDef.get(context.get('editType'),{})
        
        if context.get('repeteable',False):
            tipoAEditar = context.get('editType')    
            self.ctxMenu.append(menu.addAction("Add {}".format(tipoAEditar),
                                                   lambda i=rowHead,j=tipoAEditar:self.actionAdd(i,j)))
        
        else:
            if context.get('repeatInstance',False):
                self.ctxMenu.append(menu.addAction("Copy",lambda i=rowHead:self.actionCopy(i)))
                self.ctxMenu.append(menu.addAction("Rename",lambda i=rowHead:self.actionRename(i))) 
                menu.addSeparator()
            if 'subtypes' in edit_data:
                subtipo = subTypeDiscover(rowHead,edit_data)
                if subtipo :
                    context['editType'] = subtipo
                    edit_data = mergeEditData(edit_data,self.treeDef.get(subtipo,{}))
                
            if 'elements' in edit_data:
            # creo que es lo mas sensible hacer. Localizo los elementos que ya existen
                existentes = set()
                for k in range(rowHead.rowCount()):
                    child = rowHead.child(k,0)
                    ns,js,ts = getRow(child.index())
                    if ts.data():
                        existentes.add(ts.data())
                        
                elementos = getFullElementList(self.treeDef,edit_data.get('elements',[]))                    
                for elemento in elementos:
                    if elemento[0] in existentes:
                        pass
                    else:
                        self.ctxMenu.append(menu.addAction("Add {}".format(elemento[0]),
                                                    lambda i=rowHead,j=elemento[0]:self.actionAdd(i,j)))
            menu.addSeparator()
        
        if edit_data.get('objtype','atom') == 'dict' and edit_data.get('elements',None) is None:
            self.ctxMenu.append(menu.addAction("Add name/value pair",lambda i=rowHead:self.actionNameValue(n)))

    def actionRemove(self,item):
        rownr = item.row()
        diggers= self.ctxFactory(item).get('edit_tree',{}).get('diggers',[])
        pai = item.parent()
        if pai is None: #topLevel
            item.model().removeRow(rownr)
        else:
            item.model().removeRow(rownr,pai.index())
        
        if len(diggers) >0:
            for dig in diggers:
                dig(pai,self)
    
    def actionAdd(self,item,newItemType):
        edit_data = self.treeDef.get(newItemType,{})
        if item.column() == 0:
            parent = item
        else:
            parent = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            
        def_val = edit_data.get('default',None)
        valor_defecto = None
        if def_val and callable(def_val):
            valor_defecto = def_val(item,self)
        else:
            valor_defecto = def_val
        
        if edit_data.get('objtype','atom') != 'group':
            newRow = makeRow(newItemType,valor_defecto,newItemType)
            if parent is None:
                self.model().appendRow(newRow)
            else:
                parent.appendRow(newRow)
                
            self.addChildren(newRow[0],edit_data,newItemType)
            
            self.setCurrentIndex(newRow[0].index())
        # este es el sitio para realizar el cambio de nombre
            if 'elements' in edit_data:
                campos = [elem[0] for elem in getFullElementList(self.treeDef,edit_data['elements']) ]
                if 'name' in campos or 'result' in campos:
                    self.actionRename(newRow[0])
                for funcion in edit_data.get('setters',[]):
                    funcion(newRow[0],self)
        
            return newRow[0]
        else:
            self.addChildren(item,edit_data,newItemType)
            self.setCurrentIndex(item.index())
            return item
            
        

    def addChildren(self,newHead,edit_data,tipo):
        """
        separada 
        """
        if edit_data.get('subtypes'):
            ok = False
            lista = []
            ilista = []
            for entrada in edit_data.get('subtypes'):
                lista.append(self.treeDef.get(entrada,{}).get('text','{} de tipo {}'.format(tipo,entrada)))
                ilista.append(entrada)
            text,ok = QInputDialog.getItem(None,'Seleccione el tipo de {} a añadir'.format(tipo),'tipo',lista,0,False)
            if ok and text:
                subtipo =ilista[lista.index(text)]
            else:
                return

            edit_data = mergeEditData(edit_data,self.treeDef.get(subtipo,{}))
            self.addChildren(newHead,edit_data,subtipo)
        else:
            if edit_data.get('elements'):
                for entrada in getFullElementList(self.treeDef,edit_data['elements']) :
                    #FIXME solo los obligatorios:
                    if len(entrada) > 3 and entrada[3]: # es solo un repeat
                        newHead.appendRow(makeRow(entrada[0],None,entrada[0]))
                    elif entrada[1]:
                        self.actionAdd(newHead,entrada[0])
        #TODO falta colocar el foco y validar obligatorios
    
    def actionAddTop(self,item,newItemType):
        pos = self.actionAdd(item,newItemType)
        self.actionRename(pos)
       
    def actionRename(self,item):
        text = QInputDialog.getText(None, "Nuevo nombre para el nodo: "+item.data(),"Nodo", QLineEdit.Normal,item.data())
        if text[0] and text[0] != '':
            item.setData(text[0],Qt.EditRole)
            item.setData(text[0],Qt.UserRole +1)
        #propago
        n,i,t = getRow(item)
        if n.hasChildren():
            for k in range(n.rowCount()):
                nh,ih,th = getRow(n.child(k))
                if nh.data() in ('name','result'):
                    ih.setData(text[0],Qt.EditRole)
                    ih.setData(text[0],Qt.UserRole +1)
                    break
       
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
            

class TreeDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.context = None 
        #para los objetos con lista
        self.isDouble = False
        self.fullList = None
        self.currentList = None 
        
    def createEditor(self,parent,option,index):
        """

        """
        if index.column() != 1:
            return 
        self.context = self.parent().ctxFactory(index)
        if self.context.get('topLevel',False):
            return 
        if self.context.get('readonly',False):
            return
        edit_format = self.context.get('edit_tree',{})

        item = self.context.get('editPos')
        defeditor = edit_format.get('editor',QLineEdit)
        
        if defeditor ==  QCheckBox:
            #TODO hay que ponerle un nombre
            editor = QCheckBox(self.context.get('name'),parent)
            
        elif defeditor ==  QSpinBox:
            editor = QSpinBox(parent)
            editor.setMaximum(edit_format.get('max',99))
            editor.setMinimum(edit_format.get('min',0))
            
        elif defeditor in (QComboBox,WMultiCombo,WMultiList):
            #FIXME parche de presentacion
            if defeditor != WMultiList:   
                editor = defeditor(parent=parent )
            else:
                editor = defeditor()
                
            orlist = edit_format.get('source',[])
            if callable(orlist):
                self.fullList = sorted(orlist(item,self.parent()))
            else:
                self.fullList = orlist
            if isinstance(self.fullList[0],(list,tuple)):
                x,y = zip(*self.fullList)
                self.currentList = list(y)
                self.isDouble = True
            else:
                self.currentList = self.fullList
                self.isDouble = False

            if defeditor in (WMultiCombo,) :   #WMC siempre antes que QCB ya que es una especializacion
                if self.isDouble:
                    editor.load([ entry[0] for entry in self.fullList],self.currentList)
                else:
                    editor.load(self.currentList)
                #TODO  WMultiCombo as editable ... no lo veo
                #editor.setEditable(edit_format.get('editable',False))
            if defeditor ==  QComboBox:
                editor.addItems(self.currentList)
                editor.setEditable(edit_format.get('editable',False))
            elif defeditor in (WMultiList, ):
                editor.load(self.currentList,[])
                
        elif defeditor == WPowerTable :
            editor = defeditor(self.context('rowHead').rowCount() +2,2)
            editor.setHorizontalHeaderLabels(('nombre','valor'))
            context = []
            context.append((QLineEdit,{'setEnabled':False},None))
            context.append((QLineEdit,{'setEnabled':True},None))
            for x in range(item.rowCount()):
                for y,colDef in enumerate(context):
                    editor.addCell(x,y,colDef,defVal=None)
            editor.resizeRowsToContents()
            
        else:
            if self.context.get('rowHead').hasChildren():
                return
            editor = defeditor(parent)
            if isinstance(editor,QLineEdit) and edit_format.get('hidden',False):
                editor.setEchoMode(QLineEdit.Password)
            #editor.setText(dato)
        return editor
            
    def setEditorData(self, editor, index):
        model = index.model()

        edit_format = self.context.get('edit_tree',{})
        item = self.context.get('editPos')
        display = item.data(Qt.DisplayRole)
        dato = item.data(Qt.UserRole +1)
        tipo = type(dato)

        setters = self.context.get('setters')
        if setters:
            for funcion in setters:
                dato,display = funcion(item,self.parent(),dato,display)
            
        valor_defecto = None    
        if isinstance(editor,QSpinBox):
            def_value = self.context.get('default',0)
        elif isinstance(editor,QCheckBox):
            def_value = self.context.get('default',False)
        else:
            def_value = self.context.get('default')
        if callable(def_value):
            valor_defecto = def_value(item,self.parent())
        else:
            valor_defecto = def_value
            
        if isinstance(editor,WMultiList):
            inicial = []
            n,i,t = getRow(item)
            if n.hasChildren():
                for x in range(n.rowCount()):
                    nh,ih,th = getRow(n.child(x))
                    dato = ih.data()
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
            elif valor_defecto is not None:
                editor.selectEntry(valor_defecto)
                
        elif isinstance(editor,WMultiCombo): # WMC siemre antes que QCB porque es una especializacion
            #TODO doble seleccion 
            # TODO con insercion
            if self.context.get('dtype','atom') == 'list':
                aceptados = []
                n,i,t = getRow(item)
                if n.hasChildren():
                    for x in range(n.rowCount()):
                        nh,ih,th = getRow(n.child(x))
                        aceptados.append(ih.data())
            else:
                aceptados = norm2List(dato)
            for entrada in aceptados:
                editor.set(entrada)
            if len(aceptados) == 0 and valor_defecto is not None:
                editor.set(valor_defecto)
                
        elif isinstance(editor,QComboBox):
            
            isEditable = edit_format.get('editable',False)
            
            if dato is not None:
                try:
                    pos = self.currentList.index(dato)
                except ValueError:
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
            elif valor_defecto is not None:
                editor.setCurrentIndex(self.currentList.index(valor_defecto))

        elif isinstance(editor, QSpinBox):
            if dato is not None:
                editor.setValue(dato)
            else:
                editor.setValue(valor_defecto)

        elif isinstance(editor, QCheckBox):
            if dato is not None:
                editor.setCheckState(dato)
            else:
                editor.setChecked(valor_defecto)

        elif isinstance(editor,WPowerTable):
            for x in range(item.rowCount()):
                childIdx = item.index().child(x,0)
                nomItem,sitem,typeItem = getRow(childIdx)
                datos = [nomItem.data(),branch2text(nomItem)]
                for y in range(2):
                    editor.cellWidget(x,y).setText(datos[y])
            editor.resizeRowsToContents()
        
        else:
            if dato is not None:
                editor.setText(dato)
            elif valor_defecto is not None:
                editor.setText(valor_defecto)
        
    def setModelData(self,editor,model,index):
        """
        TODO dobleSeleccion
        """
        def _redoTree(item,values):
            if item.column() != 0:
                item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            contador = item.rowCount()
            for k in range(contador):
                model.removeRow(0,item.index())
            for entrada in values:
                item.appendRow(makeRow(None,entrada))
            
        def _changeItem(model,index,ivalue,dvalue):
            if not dvalue:
                model.setData(index,str(index.data(Qt.UserRole +1)),Qt.EditRole)
            else:
                model.setData(index,dvalue, Qt.EditRole)                
            model.setData(index,ivalue, Qt.UserRole +1)
            item = model.itemFromIndex(index.sibling(index.row(),0))
            return item
        
        model = index.model()
        if isinstance(editor, WMultiList):
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
                                  
            if not self.validator(editor,values):
                print('Rechazada la validacion')
                return
            item = self.context.get('editPos')
            _redoTree(item,values)
            
        elif isinstance(editor, WMultiCombo):
                #TODO insercion
            if self.context.get('dtype','atom') == 'list':
                values = norm2List(editor.get())
                item = self.context.get('editPos')
                _redoTree(item,values)
            else:
                dvalue = ivalue = editor.get()
                if not self.validator(editor,dvalue,ivalue):
                    print('Rechazada la validacion')
                    return
                item = _changeItem(model,index,ivalue,dvalue)
                
        else:
            if isinstance(editor, QComboBox):
                if self.isDouble:
                    dvalue = self.currentList[editor.currentIndex()]
                    ivalue =  self.fullList[editor.currentIndex()][0]
                else:
                    dvalue = ivalue = self.currentList[editor.currentIndex()]
                if dvalue in ('True','False'):
                    ivalue = str2bool(dvalue)            
            elif isinstance(editor, QSpinBox):
                ivalue = editor.value()
                dvalue = str(ivalue)
            elif isinstance(editor, QCheckBox):
                ivalue = editor.isChecked()
                dvalue = str(ivalue)
            elif isinstance(editor,WPowerTable):
                return
            elif isinstance(editor,QLineEdit) and self.context.get('edit_tree',{}).get('hidden',False):
                dvalue = '****'
                ivalue = editor.text()
            else:
                dvalue = ivalue = editor.text()
    
            if not self.validator(editor,dvalue,ivalue):
                print('Rechazada la validacion')
                return
            
            item = _changeItem(model,index,ivalue,dvalue)
        
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
                if not entry(self.context.get('editPos'),self.parent()): #editor,*lparms,**kwparms):
                    return False
        return True
                

 
          
if __name__ == '__main__':
    exit()


