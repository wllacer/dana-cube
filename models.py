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


from core import Cubo,Vista





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
"""
class NumberSortModel(QSortFilterProxyModel):

    def lessThan(self, left, right):
        SORT_ROLE = 33
        lvalor = left.data(SORT_ROLE)
        rvalor = right.data(SORT_ROLE)
        if left.column() == 0:
            lvalue = lvalor
            rvalue = rvalor
        else:
            lvalue = float(lvalor) if lvalor is not None else None
            rvalue = float(rvalor) if rvalor is not None else None
        return lvalue < rvalue
"""
class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):

        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TreeModel(QAbstractItemModel):
    def __init__(self, datos, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("", ""))
        self.datos = datos
        self.rowHdr = self.datos.fmtHeader('row',separador='', sparse=True)
        self.colHdr = self.datos.fmtHeader('col',separador='\n', sparse=False)
        self.setupModelData(datos, self.rootItem)
        
        
    def columnCount(self, parent):
        return len(self.datos.col_hdr_idx) + 1

    def data(self, index, role):

        if not index.isValid():
            return None
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignRight| Qt.AlignVCenter
        
        if role not in (Qt.DisplayRole,33,):
            return None
            
        item = index.internalPointer()
        if index.column() == 0:
            return item.data(index.column())
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

    def setupModelData(self, datos, parent):

        parents = [parent]
        elemento = []
        
        guiaId = self.datos.row_id
        iarray = datos.toIndexedTable()
        
        if 'dir_root_node' in self.datos.cubo.lista_guias[guiaId]:
            pass
        else:
           for ind, columnData in enumerate(iarray):
              datos_cabecera = self.rowHdr[ind+1]
              indice = columnData[0]
              celda = [datos_cabecera,] + columnData[1:]
              self.rootItem.appendChild(TreeItem(celda,self.rootItem))
        
        
        #iarray = datos.toIndexedTable()
        #print(len(iarray),len(self.rowHdr))
        #for ind, columnData in enumerate(iarray):
            #try:
                #datos_cabecera = self.rowHdr[ind+1]
                #indice = columnData[0]
                #celda = [datos_cabecera,] + columnData[1:]
            #except IndexError:
                #print('indice >{}<fuera de rango en row_hdr (>{}<)'.format(ind,len(self.rowHdr)))
            #print(celda)
            
            #if indice['parent'] is None:
                #self.rootItem.appendChild(TreeItem(celda,self.rootItem))
            ##if self.datos.dim_row == 1:
                #parents[-1].appendChild(TreeItem(celda, parents[-1]))
            #else:
                #estructura = self.datos.row_hdr_idx[ind].split(':')
                #if len(estructura) > len(elemento): #un nivel mas
                    #if parents[-1].childCount() > 0:
                        #parents.append(parents[-1].child(parents[-1].childCount() - 1))
                    #elemento.append(estructura[-1])
                #else:  
                    #while len(estructura) < len(elemento):
                        #parents.pop()
                        #elemento.pop()
                    #if len(estructura) == len(elemento) and estructura[-1] != elemento[-1]:
                        #elemento[-1] = estructura[-1]
                #parents[-1].appendChild(TreeItem(celda, parents[-1]))

    def emitDataChanged(self):
        self.dataChanged.emit(QModelIndex(),QModelIndex())
