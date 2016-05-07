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
from util.fivenumbers import isOutlier

from json2tree import *


class TreeModel(QAbstractItemModel):
    def __init__(self, datos, parent=None):
        super(TreeModel, self).__init__(parent)
        self.datos = load(datos)
        self.rootItem = self.datos.rootItem
        #self.getHeaders()
        #self.setupModelData(datos, self.rootItem)
        
        
    def columnCount(self, parent):
        max_col=20
        #for k in self.datos.content:
            #e=self.datos.content[k]
            #if isinstance(e.itemData,(list,tuple)) and len(e.itemData) >= max_col:
                #max_col = len(e.itemData) +1
        return max_col
              
        #return self.datos.col_hdr_idx.count() + 1

    def data(self, index, role):

        if not index.isValid():
            return None
        item = index.internalPointer()
        
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignLeft| Qt.AlignVCenter
            else:
                return Qt.AlignLeft| Qt.AlignVCenter
               
        elif role not in (Qt.DisplayRole,33,):
            return None
        #FIXME por que ese desplazamiento    
        if index.column() == 0:
            #TODO hay que reformatear fechas
            return item.key.split(DELIMITER)[-1]
        elif item.data(index.column() -1) is None:
            return None
        else:
            return item.data(index.column() -1)
            #return item.data(1) #OJO para este caso
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
                    return ""
                else:
                    #return self.colHdr[section]
                    return ""
            elif orientation == Qt.Vertical:
                #chapuza para solo coger parte de las fechas
                #return self.rowHdr[section].split(DELIMITER)[-1]
                #return self.rowHdr[section]
                return ""
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()
    
    def getHeaders(self):
        return
        #self.rowHdr = self.datos.fmtHeader('row',separador='', sparse=True)
        #self.colHdr = self.datos.fmtHeader('col',separador='\n', sparse=False)
        
    def emitModelReset(self):
        self.modelReset.emit()
        
    def emitDataChanged(self):
        print('entro')
        self.dataChanged.emit(QModelIndex(),QModelIndex())
