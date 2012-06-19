#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012 Werner Llacer. All rights reserved.. Under the terms of the GPL 2
## Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2
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
        QTableWidget, QTableWidgetItem, QVBoxLayout, QColor)

from dialogs import CuboDlg,  VistaDlg,  NumberFormatDlg
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
                                    yellowoutliers=True)
        self.numbers = {}

        self.table = QTableWidget()
        formatButton1 = QPushButton("&Parametrizar vista")
        formatButton2 = QPushButton("&Formateo presentacion")
        #formatButton3 = QPushButton("Boton 3")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(formatButton1)
        buttonLayout.addWidget(formatButton2)
        #buttonLayout.addWidget(formatButton3)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        


        self.connect(formatButton1, SIGNAL("clicked()"),
                     self.requestVista)
        self.connect(formatButton2, SIGNAL("clicked()"),
                     self.setNumberFormat)
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
            #self.cubo.putGuidesModelo()
            self.cubo.getGuides()
            self.vista = None
#            self.requestVista()
        
    def requestVista(self):
        vistaDlg = VistaDlg(self.cubo, self)
 
        #TODO  falta el filtro
        if self.vista is  None:
            pass
        else:
            vistaDlg.rowCB.setCurrentIndex(self.vista.row_id)
            vistaDlg.colCB.setCurrentIndex(self.vista.col_id)
            vistaDlg.agrCB.setCurrentIndex(self.cubo.getFunctions().index(self.vista.agregado))
            vistaDlg.fldCB.setCurrentIndex(self.cubo.getFields().index(self.vista.campo))
 
        if vistaDlg.exec_():
            row =vistaDlg.rowCB.currentIndex()
            col = vistaDlg.colCB.currentIndex()
            agregado = vistaDlg.agrCB.currentText()
            campo = vistaDlg.fldCB.currentText()
#        
            if self.vista is None:
                self.vista = Vista(self.cubo, row, col, agregado, campo)       
            else:
                self.vista.setNewView(row, col, agregado, campo)
            
            self.refreshTable()
#
#
    def fmtHeader(self, indice, separador='\t', sparse=False, max_level=99, range= None):
        cab_col = []
  
        for i, entrada in(enumerate(indice)):
            if getLevel(entrada)> max_level:
                continue
            if range is not None:
                if range[0] <= i <= range[1]:
                    pass
                else:
                    continue
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
                    texto = unicode(col)
                else:
                    texto += separador + unicode(col)
            cab_col.append(texto)
        return cab_col
        
    def addTableItem(self, tabla,  elemento, row, col, level_x, level_y,outlier=False):
        if elemento is None:
            item = QTableWidgetItem(' ')
            if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1) :
                item.setBackgroundColor(QColor('grey').lighter())
            if self.vista.dim_col > 1 and level_y < (self.vista.dim_col -1):
                item.setBackgroundColor(QColor('grey').lighter())
            tabla.setItem(row, col, item)
            return
            
        numero = elemento[0] #para ser mas comodo
        text, sign = fmtNumber(numero, self.format)    
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)

        if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1):
            item.setBackgroundColor(QColor('grey').lighter())
        if self.vista.dim_col  > 1 and level_y < (self.vista.dim_col -1):
            item.setBackgroundColor(QColor('grey').lighter())
        if sign and self.format["rednegatives"]:
            item.setBackgroundColor(QColor("red"))
        if outlier: 
            item.setBackgroundColor(QColor("yellow"))
        tabla.setItem(row, col, item)

    def refreshTable(self):

        
        self.numbers = self.vista.array
        #
        max_row_level = 99
        max_col_level  = 99
        row_range = [0, len(self.vista.row_idx) -1]
        col_range = [0, len(self.vista.col_idx) -1]
        
        
        cab_col = self.fmtHeader(self.vista.col_hdr_idx, '\n', False, max_row_level, col_range)
        cab_row = self.fmtHeader(self.vista.row_hdr_idx, '\t',True, max_col_level, row_range)


        self.X_MAX = len(self.vista.row_idx)
        self.Y_MAX = len(self.vista.col_idx)

        metrics=None
        if self.format['yellowoutliers']:
            metrics = self.vista.fivepointsmetric()
  
        self.table.clear()

        self.table.setColumnCount(len(cab_col))
        self.table.setRowCount(len(cab_row))

        self.table.setHorizontalHeaderLabels(cab_col)
        self.table.setVerticalHeaderLabels(cab_row)
        
        row_i = 0
        for x in range(self.X_MAX):
            level_x = getLevel(self.vista.row_idx[x])     
            if level_x > max_row_level :
                continue
            if row_range[0] <= x <= row_range[1] :
                pass
            else:
                continue
            #print (row_range[1] <= self.vista.row_idx[x] => row_range[0] )
            col_i  = 0
            for y in range(self.Y_MAX):
                level_y = getLevel(self.vista.col_idx[y])
                if level_y > max_col_level:
                    continue
                if col_range[0] <= y <= col_range[1] :
                    pass
                else:
                    continue
                #determine if outlier
                outlier = False
                if self.format['yellowoutliers'] and self.numbers[x][y] is not None:
                    if (self.numbers[x][y][0]< metrics[level_x][level_y][1] 
                                or self.numbers[x][y][0]  > metrics[level_x][level_y][5] ):
                        outlier=True
                
                self.addTableItem(self.table, self.numbers[x][y], row_i, col_i, level_x, level_y, outlier)
                col_i += 1
            row_i += 1
        self.show()
        
#    def refreshTableOrig(self):
#
#        
#        self.X_MAX = len(self.vista.row_idx)
#        self.Y_MAX = len(self.vista.col_idx)
#        self.numbers = self.vista.array
#        #
#        if self.format['yellowoutliers']:
#            metrics = self.vista.fivepointsmetric()
#  
#        self.table.clear()
#        self.table.setColumnCount(self.Y_MAX)
#        self.table.setRowCount(self.X_MAX)
#        cab_col = self.fmtHeader(self.vista.col_idx, '\n')
#        cab_row = self.fmtHeader(self.vista.row_idx, '\t', True)
#        self.table.setHorizontalHeaderLabels(cab_col)
#        self.table.setVerticalHeaderLabels(cab_row)
#        
#        for x in range(self.X_MAX):
#            level_x = getLevel(self.vista.row_idx[x])           
#            for y in range(self.Y_MAX):
#                level_y = getLevel(self.vista.col_idx[y])
#                if self.numbers[x][y] is None:
#                    item = QTableWidgetItem(' ')
#                    if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1) :
#                        item.setBackgroundColor(QColor('grey').lighter())
#                    if self.vista.dim_col > 1 and level_y < (self.vista.dim_col -1):
#                        item.setBackgroundColor(QColor('grey').lighter())
#                    self.table.setItem(x, y, item)
#                    continue
#
#                numero = self.numbers[x][y][0] #para ser mas comodo
#                text, sign = fmtNumber(numero, self.format)    
#                item = QTableWidgetItem(text)
#                item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)
#
#                if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1):
#                    item.setBackgroundColor(QColor('grey').lighter())
#                if self.vista.dim_col  > 1 and level_y < (self.vista.dim_col -1):
#                    item.setBackgroundColor(QColor('grey').lighter())
#                if sign and self.format["rednegatives"]:
#                    item.setBackgroundColor(QColor("red"))
#                if self.format['yellowoutliers']: 
#                    if (numero< metrics[level_x][level_y][1] or numero  > metrics[level_x][level_y][5] ):
#                        item.setBackgroundColor(QColor("yellow"))
#                self.table.setItem(x, y, item)
#            
#        self.show()#



        
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """        
        if self.numberFormatDlg is None:
            self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)
        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()


app = QApplication(sys.argv)
form = Form()
form.show()
app.exec_()
