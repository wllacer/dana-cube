#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012 Werner Llacer. All rights reserved.. Under the terms of the GPL 2
## Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2
# FIXED cubo.getGuides.  Sustituir por fillGuias()
# FIXED cubo.getFunctions:  generar
# FIXED getLevel    no definida creada en util.record_functions
# FIXME fivepointsmetric no definida. Suspendida de momento
# FIXME cambiar la vista se pega un carajazo. vista.setNewView
# FIXME fmtHdr parece incompatible con el codigo nuevo en fechas
#
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import math
import random
import string
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QVBoxLayout)

from dialogs import CuboDlg,  VistaDlg,  NumberFormatDlg,  ZoomDlg
from core import *

# para evitar problemas con utf-8, no lo recomiendan pero me funciona
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

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
        formatButton3 = QPushButton("&Zoom")

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(formatButton1)
        buttonLayout.addWidget(formatButton2)
        buttonLayout.addWidget(formatButton3)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        
        formatButton1.clicked.connect(self.requestVista)
        formatButton2.clicked.connect(self.setNumberFormat)
        formatButton3.clicked.connect(self.zoomData)
        
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
            self.cubo.fillGuias()
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
                
            self.max_row_level = self.vista.dim_row
            self.max_col_level  = self.vista.dim_col
            self.row_range = [0, len(self.vista.row_hdr_idx) -1]
            self.col_range = [0, len(self.vista.col_hdr_idx) -1]
            
            self.refreshTable()
#
    def zoomData(self):
        zoomDlg = ZoomDlg(self.vista, self)
#
        zoomDlg.rowFCB.setCurrentIndex(self.row_range[0])
        zoomDlg.rowTCB.setCurrentIndex(self.row_range[1])
        zoomDlg.colFCB.setCurrentIndex(self.col_range[0])
        zoomDlg.colTCB.setCurrentIndex(self.col_range[1])
        zoomDlg.rowDimSpinBox.setValue(self.max_row_level)
        zoomDlg.colDimSpinBox.setValue(self.max_col_level)
        
        refrescar = False
        if zoomDlg.exec_():
            if ( zoomDlg.rowFCB.currentIndex() != self.row_range[0] or
                   zoomDlg.rowTCB.currentIndex() != self.row_range[1] or
                   zoomDlg.colFCB.currentIndex() != self.col_range[0] or
                   zoomDlg.colTCB.currentIndex() != self.col_range[1] ) :
                self.row_range[0] = zoomDlg.rowFCB.currentIndex()
                self.row_range[1] = zoomDlg.rowTCB.currentIndex()
                self.col_range[0] = zoomDlg.colFCB.currentIndex()
                self.col_range[1] = zoomDlg.colTCB.currentIndex()
                refrescar = True
            if ( zoomDlg.rowDimSpinBox.value != self.max_row_level or
                    zoomDlg.colDimSpinBox.value != self.max_col_level ):
                self.max_row_level = zoomDlg.rowDimSpinBox.value()
                self.max_col_level = zoomDlg.colDimSpinBox.value()
                refrescar = True
                
            if refrescar:

                self.refreshTable()
                
    def fmtHeader(self, indice, separador='\t', sparse=False, max_level=99, range= None):
        #FIXME parece incompatible con el codigo nuevo
        cab_col = []

        for i, entrada in(enumerate(indice)):
            if getLevel(entrada) >= max_level :
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
                        linea[k] = ' '*8
                    else:
                        break
            texto = ''
            for col in linea:
                if col is None and texto == '':
                    pass
                elif col is None:
                    texto +=separador
                elif texto == '':
                    #texto = unicode(col)
                    texto = col
                else:
                    #texto += separador + unicode(col)
                    texto += separador + col
            cab_col.append(texto)
        return cab_col
        
    def addTableItem(self, tabla,  elemento, row, col, level_x, level_y,outlier=False):
        if elemento is None:
            item = QTableWidgetItem(' ')
            if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1) :
                item.setBackground(QColor('grey').lighter())
            if self.vista.dim_col > 1 and level_y < (self.vista.dim_col -1):
                item.setBackground(QColor('grey').lighter())
            tabla.setItem(row, col, item)
            return
            
        numero = elemento #para ser mas comodo
        text, sign = fmtNumber(numero, self.format)    
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignRight|Qt.AlignVCenter)

        if self.vista.dim_row > 1 and level_x < (self.vista.dim_row -1):
            item.setBackground(QColor('grey').lighter())
        if self.vista.dim_col  > 1 and level_y < (self.vista.dim_col -1):
            item.setBackground(QColor('grey').lighter())
        if sign and self.format["rednegatives"]:
            item.setBackground(QColor("red"))
        if outlier: 
            item.setBackground(QColor("yellow"))
        tabla.setItem(row, col, item)

    def refreshTable(self):

        
        self.numbers = self.vista.array
        #                

        cab_row = self.fmtHeader(self.vista.row_hdr_txt, '\t',True, self.max_row_level, self.row_range)
        cab_col = self.fmtHeader(self.vista.col_hdr_txt, '\n', False, self.max_col_level, self.col_range)


        self.X_MAX = len(self.vista.row_hdr_idx)
        self.Y_MAX = len(self.vista.col_hdr_idx)

        metrics=None
        #FIXME
        #if self.format['yellowoutliers']:
            #metrics = self.vista.fivepointsmetric()
  
        self.table.clear()

        self.table.setColumnCount(len(cab_col))
        self.table.setRowCount(len(cab_row))

        self.table.setHorizontalHeaderLabels(cab_col)
        self.table.setVerticalHeaderLabels(cab_row)
        
        row_i = 0
        for x in range(self.X_MAX):
            level_x = getLevel(self.vista.row_hdr_idx[x])     
            if level_x >= self.max_row_level :
                continue
            if self.row_range[0] <= x <= self.row_range[1] :
                pass
            else:
                continue
            #print (self.row_range[1] <= self.vista.row_idx[x] => self.row_range[0] )
            col_i  = 0
            for y in range(self.Y_MAX):
                level_y = getLevel(self.vista.col_hdr_idx[y])
                if level_y >= self.max_col_level:
                    continue
                if self.col_range[0] <= y <= self.col_range[1] :
                    pass
                else:
                    continue
                #determine if outlier
                outlier = False
                # FIXME fivepointsmetric
                #if self.format['yellowoutliers'] and self.numbers[x][y] is not None:
                    #if (self.numbers[x][y]< metrics[level_x][level_y][1] 
                                #or self.numbers[x][y]  > metrics[level_x][level_y][5] ):
                        #outlier=True
                
                self.addTableItem(self.table, self.numbers[x][y], row_i, col_i, level_x, level_y, outlier)
                col_i += 1
            row_i += 1
        self.show()
        


        
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
