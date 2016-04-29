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




def fmtNumber(number, fmtOptions):
    """ taken from Rapid development with PyQT book (chapter 5) """

    fraction, whole = math.modf(number)
    sign = "-" if whole < 0 else ""
    whole = "{0}".format(int(math.floor(abs(whole))))
    digits = []
    for i, digit in enumerate(reversed(whole)):
        if i and i % 3 == 0:
            digits.insert(0, fmtOptions["thousandsseparator"])
        digits.insert(0, digit)
    if fmtOptions["decimalplaces"]:
        fraction = "{0:.7f}".format(abs(fraction))
        fraction = (fmtOptions["decimalmarker"] +
                fraction[2:fmtOptions["decimalplaces"] + 2])
    else:
        fraction = ""
    text = "{0}{1}{2}".format(sign, "".join(digits), fraction)#
    
    return text, sign

class TreeModel(QAbstractItemModel):
    def __init__(self, datos, parent=None):
        super(TreeModel, self).__init__(parent)
        datos.toTree2D()
        self.rootItem = datos.row_hdr_idx.rootItem
        self.datos = datos
        self.getHeaders()
        #self.setupModelData(datos, self.rootItem)
        
        
    def columnCount(self, parent):
        return self.datos.col_hdr_idx.count() + 1

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
                if self.datos.format['yellowoutliers']:
                    if isOutlier(item.data(index.column()),item.aux_data):
                        return QColor(Qt.yellow)
                if self.datos.format['rednegatives'] and item.data(index.column() < 0) :
                    return QColor(Qt.red)
                    
               
        elif role not in (Qt.DisplayRole,33,):
            return None
            
        if index.column() == 0:
            #TODO hay que reformatear fechas
            return item.data(0)
        elif item.data(index.column()) is None:
            return None
        else:
            if role == Qt.DisplayRole:
                text, sign = fmtNumber(item.data(index.column()),self.datos.format)
                return '{}{}'.format(sign,text)
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
                    return ""
                else:
                    return self.colHdr[section]
            elif orientation == Qt.Vertical:
                return self.rowHdr[section]
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
        self.rowHdr = self.datos.fmtHeader('row',separador='', sparse=True)
        self.colHdr = self.datos.fmtHeader('col',separador='\n', sparse=False)
        
    def emitModelReset(self):
        self.modelReset.emit()
        
    def emitDataChanged(self):
        print('entro')
        self.dataChanged.emit(QModelIndex(),QModelIndex())
