#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   code is based on the simpletreemodel sample of the Qt/PyQt documentation,
           which is BSD licensed by Nokia and successors, and Riverbank
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import math

from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt, QSortFilterProxyModel
from PyQt5.QtWidgets import QApplication, QTreeView
from PyQt5.QtGui import QColor


from core import Cubo,Vista
from util.tree import *
from util.numbers import isOutlier,fmtNumber

""" lo dejo como documentacion
print(trueIndex.internalPointer())
print(type(index.model()),index.row(),index.column(),index.parent(),index.internalId(),index.data())
print(index.sibling(index.row(),0).data())
"""



class TreeModel(QAbstractItemModel):
    def __init__(self, datos, parent=None):
        super(TreeModel, self).__init__(parent)
        datos.toTree2D()
        self.rootItem = datos.row_hdr_idx.rootItem
          
        self.datos = datos
        self.getHeaders()
        #self.setupModelData(datos, self.rootItem)
        
    def columnCount(self, parent=None):
        return self.datos.col_hdr_idx.count() + 1

    def count(self):
        return self.datos.row_hdr_idx.count()
            
    def data(self, index, role):
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignRight| Qt.AlignVCenter
            else:
                return Qt.AlignLeft| Qt.AlignVCenter
        elif role == Qt.BackgroundRole:
            if index.column() != 0:
                if self.datos.format['yellowoutliers'] and self.datos.stats:
                    if isOutlier(item.data(index.column()),item.getStatistics()):
                        return QColor(Qt.yellow)
                if self.datos.format['rednegatives'] and item.data(index.column() < 0) :
                    return QColor(Qt.red)
                    
               
        elif role not in (Qt.DisplayRole,33,):
            return None
        
        if index.column() == 0:
            return item.data(0).split(DELIMITER)[-1]
        elif item.data(index.column()) is None:
            return None
        else:
            if role == Qt.DisplayRole:
                text, sign = fmtNumber(item.data(index.column()),self.datos.format)
                return text #'{}{}'.format(sign,text)
            else:
                return item.data(index.column())
                #return text
            #return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section == 0:
                    texto = ''
                else:
                    texto = self.colHdr[section]
            else:
                texto = self.rowHdr[section]
            if texto:
                ktexto = texto.split('\n')
                ktexto[-1] = ktexto[-1].split(DELIMITER)[-1]
                texto = '\n'.join(ktexto)
            else:
                texto = ''
            return texto
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        return None

    def index(self, row, column, parentIdx):
        
        if not self.hasIndex(row, column, parentIdx):
            return QModelIndex()

        if not parentIdx.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parentIdx.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def item(self,selector):
        """
            Esta funcion esta sobrecargada. Admite dos tipos de parametros:
                QModelIndex o
                Clave del arbol
            En el caso de QModelIndex comprobamos que el indice se refiera a esta clase o
            si pertenece a un QSortFilterProxyModel, porque en este caso hay que retocarlo.
            Chequear esto me permite simplificar el codigo en donde le llame y evitar los problemas del uso
            de QSortFilterProxyModel (que no es transparente, vaya)
        """
        if isinstance(selector,QModelIndex):
            if selector.isValid():
                if isinstance(selector.model(),TreeModel):
                    index = selector
                elif isinstance(selector.model(),QSortFilterProxyModel):
                    index = selector.model().mapToSource(selector)
                else:
                    return None
                return index.internalPointer()
            else:
                return None
            pass
        else:
            return self.datos.row_hdr_idx.item(selector)
        
    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parentIdx):
        if not parentIdx.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parentIdx.internalPointer()

        if parentIdx.column() > 0:
            return 0

        return parentItem.childCount()
    
    def getHeaders(self):
        self.rowHdr = self.datos.fmtHeader('row',separador='', sparse=True)
        self.colHdr = self.datos.fmtHeader('col',separador='\n', sparse=False)
        
    def emitModelReset(self):
        self.modelReset.emit()
        
    def emitDataChanged(self):
        print('entro')
        self.dataChanged.emit(QModelIndex(),QModelIndex())
