#!/usr/bin/python
# -*- coding: utf-8 -*-

## Copyright (c) 2008 Qtrac Ltd. All rights reserved.
## This program or module is free software: you can redistribute it and/or
## modify it under the terms of the GNU General Public License as published
## by the Free Software Foundation, either version 2 of the License, or
## version 3 of the License, or (at your option) any later version. It is
## provided for educational purposes and is distributed in the hope that
## it will be useful, but WITHOUT ANY WARRANTY; without even the implied
## warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
## the GNU General Public License for more details.
#
from __future__ import division
#from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import math
import random
import string
import sys
from PyQt4.QtCore import (Qt, SIGNAL)
from PyQt4.QtGui import (QApplication, QDialog, QHBoxLayout, QPushButton,
        QTableWidget, QTableWidgetItem, QVBoxLayout)
#import numberformatdlg1
#import numberformatdlg2
#import numberformatdlg3
from dialogs import CuboDlg,  VistaDlg
from core import *
#
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
class Form(QDialog):


    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.X_MAX=0
        self.Y_MAX =0
        self.numberFormatDlg = None
        self.format = dict(thousandsseparator=".", 
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False, 
                                    yellowoutliers=False)
        self.numbers = {}
#        for x in range(self.X_MAX):
#            for y in range(self.Y_MAX):
#                self.numbers[(x, y)] = (10000 * random.random()) - 5000

        self.table = QTableWidget()
        formatButton1 = QPushButton("&Parametrizar vista")
        formatButton2 = QPushButton("Boton 2")
        formatButton3 = QPushButton("Boton 3")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(formatButton1)
        buttonLayout.addWidget(formatButton2)
        buttonLayout.addWidget(formatButton3)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        


        self.connect(formatButton1, SIGNAL("clicked()"),
                     self.requestVista)
#        self.connect(formatButton2, SIGNAL("clicked()"),
#                     self.setNumberFormat2)
#        self.connect(formatButton3, SIGNAL("clicked()"),
#                     self.setNumberFormat3)
        self.setWindowTitle("Cubo ")
                        
        self.initCube()
        if self.vista is None:
            self.requestVista()
        self.refreshTable()
        
    def initCube(self):
        my_cubos = load_cubo()
        #realiza la seleccion del cubo
        dialog = CuboDlg(my_cubos, self)
        if dialog.exec_():
            seleccion = str(dialog.cuboCB.currentText())
            self.cubo = Cubo(my_cubos[seleccion])
            self.cubo.putGuidesModelo()
            self.vista = None
#            self.requestVista()
        
    def requestVista(self):
        vistaDlg = VistaDlg(self.cubo, self)
        #TODO.  dar valores iniciales a la vista
        if self.vista is not None:
            pass
            
        if vistaDlg.exec_():
            row =vistaDlg.rowCB.currentIndex()
            col = vistaDlg.colCB.currentIndex()
#        
            if self.vista is None:
                self.vista = Vista(self.cubo, row, col)       
            else:
                self.vista.setNewView(row,  col)
            
            self.refreshTable()
#
#
    def fmtHeader(self, indice, separador='\t', sparse=False):
        cab_col = []
        #for linea in self.vista.col_idx:
        for i, entrada in(enumerate(indice)):
            linea = entrada[:]
            if sparse and i >0:
                for k, campo in enumerate(linea):
                    if campo == indice[i -1][k] and campo is not None:
                        linea[k] = ' '*len(campo)
                    else:
                        break
            texto = ''
            for col in linea:
                if col is None and texto == '':
                    pass
                elif col is None:
                    texto +=separador
                elif texto == '':
                    texto = str(col)
                else:
                    texto += separador + col
            cab_col.append(texto)
        return cab_col
        
    def refreshTable(self):

        self.X_MAX = len(self.vista.row_idx)
        self.Y_MAX = len(self.vista.col_idx)
        self.numbers = self.vista.array
        
        self.table.clear()
        self.table.setColumnCount(self.Y_MAX)
        self.table.setRowCount(self.X_MAX)
        cab_col = self.fmtHeader(self.vista.col_idx, '\n')
        cab_row = self.fmtHeader(self.vista.row_idx, '\t', True)


        self.table.setHorizontalHeaderLabels(
                cab_col)
        self.table.setVerticalHeaderLabels(
                cab_row)
        for x in range(self.X_MAX):           # 
            for y in range(self.Y_MAX):
                if self.numbers[x][y] is None:
                    continue
                text, sign = fmtNumber(self.numbers[x][y][0], self.format)    
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight|
                                      Qt.AlignVCenter)
                if sign and self.format["rednegatives"]:
                    item.setBackgroundColor(Qt.red)
                self.table.setItem(x, y, item)
        self.show()
#
#
#    def setNumberFormat1(self):
#        dialog = numberformatdlg1.NumberFormatDlg(self.format, self)
#        if dialog.exec_():
#            self.format = dialog.numberFormat()
#            self.refreshTable()
#
#
#    def setNumberFormat2(self):
#        dialog = numberformatdlg2.NumberFormatDlg(self.format, self)
#        self.connect(dialog, SIGNAL("changed"), self.refreshTable)
#        dialog.show()
#
#
#    def setNumberFormat3(self):
#        if self.numberFormatDlg is None:
#            self.numberFormatDlg = numberformatdlg3.NumberFormatDlg(
#                    self.format, self.refreshTable, self)
#        self.numberFormatDlg.show()
#        self.numberFormatDlg.raise_()
#        self.numberFormatDlg.activateWindow()


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
