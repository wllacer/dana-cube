#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''

from pprint import pprint
import datetime
import argparse
from decimal import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout

from base.core import Cubo,GuideItemModel,GuideItem

class guidePreview(QDialog):
    def __init__(self,cubo,pos=0,parent=None):
        super(guidePreview,self).__init__(parent)
        self.tree = previewTree(cubo,guia=pos)
        meatLayout=QGridLayout()
        meatLayout.addWidget(self.tree)
        self.setLayout(meatLayout)

class previewTree(QTreeView):
    def __init__(self,cubo,guia=0,parent=None):
        super(previewTree, self).__init__(parent)
        self.parentWindow = parent

        self.cubo = Cubo(cubo)
        self.setupModel(guia) 
        
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.setupView()

        print('inicializacion completa')

    def setupModel(self,guia):
  
        self.baseModel,dummy = self.cubo.fillGuia(guia,display=True)
        self.hiddenRoot = self.baseModel.invisibleRootItem()       
        parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        
    def setupView(self):
        self.view.setModel(self.baseModel)
        self.baseModel.setHorizontalHeaderLabels(('Código','Descripcion'))
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)

def main():
    from support.util.jsonmgr import load_cubo
    app = QApplication(sys.argv)
    mis_cubos = load_cubo()
    cubo = mis_cubos['datos light']
    form = guidePreview(cubo)
    form.show()
    if form.exec_():
        pass
        sys.exit()

if __name__ == '__main__':
        # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    main()
