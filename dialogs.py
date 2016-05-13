#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012 Werner Llacer. All rights reserved.. Under the terms of the GPL 2
## Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pprint import pprint

        
class WPropertySheet(QTableWidget):
    """
        Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
           context[0] titulos de las filas
           context[1] valores iniciales
           context[2] widget a utilizar (defecto QLineEdit)
           context[3] listas de valores para el widget (combos)
           context[4] rutinas de validacion
           ...
       TODO procesar los parametros del 2 en adelante
    """
    def __init__(self,context,parent=None):   
        super(WPropertySheet, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context

        self.setRowCount(len(context))
        self.setColumnCount(1)
        
        cabeceras = [ k[0] for k in self.context ]
        cdata     = [ k[1] for k in self.context ]
        for k,item in enumerate(cdata):
            #tableItem= QTableWidgetItem(str(item))
            #self.sheet.setItem(k,0,tableItem)
            #self.sheet.setCellWidget(k,0,QLineEdit(str(item) if item is not None else None))
            editItem = QLineEdit()
            editItem.setText(str(item) if item is not None else '')
            self.setCellWidget(k,0,editItem)


        self.setVerticalHeaderLabels(cabeceras)
        
        #self.resizeColumnsToContents()
        self.resizeRowsToContents()

    def values(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            #if self.sheet.cellWidget(k,0) is None:
                #print('elemento {} vacio'.format(k))
                #continue
            valores.append(self.cellWidget(k,col).text())
        return valores

        
        
class propertySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
    """
    def __init__(self,title,context,parent=None):   
        super(propertySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(context)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)


        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        
        #formLayout.addLayout(meatLayout)        
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(480,480))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

    def accept(self):
        datos = self.sheet.values()
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.context[k][1] = valor
        QDialog.accept(self)
        
class CuboDlg(QDialog):
    def __init__(self, dict_cubos, parent=None):
        super(CuboDlg, self).__init__(parent)
        
        self.definiciones = dict_cubos
        InicioLabel = QLabel("Seleccione y conectese a un cubo")
        cuboLbl = QLabel("&Cubo")
        self.cuboCB = QComboBox()
        self.cuboCB.addItems(sorted(self.definiciones.keys()))
        cuboLbl.setBuddy(self.cuboCB)
 
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                                        QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(InicioLabel, 0, 0)
        grid.addWidget(cuboLbl, 1, 0)
        grid.addWidget(self.cuboCB, 1, 1)
        grid.addWidget(buttonBox, 4, 0, 1, 2)


        self.setLayout(grid)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        

                            
class VistaDlg(QDialog):
    def __init__(self, cubo_eleg,  parent=None):
        super(VistaDlg, self).__init__(parent)
        
        self.cubo = cubo_eleg
        datos_cubo = self.cubo.lista_guias
        
        listaCampos = [ item['name'] for item in datos_cubo]
        
        InicioLabel = QLabel("Defina los parametros de la vista")
        rowLbl = QLabel("&Row")
        self.rowCB = QComboBox()
        self.rowCB.addItems(listaCampos)
        rowLbl.setBuddy(self.rowCB)
 
        colLbl = QLabel("&Col")
        self.colCB = QComboBox()
        self.colCB.addItems(listaCampos)
        colLbl.setBuddy(self.colCB)
        
        agrLbl = QLabel("&Functiom")
        self.agrCB=QComboBox()
        self.agrCB.addItems(self.cubo.getFunctions())
        agrLbl.setBuddy(self.agrCB)

        fldLbl = QLabel("&Element")
        self.fldCB=QComboBox()
        self.fldCB.addItems(self.cubo.getFields())
        fldLbl.setBuddy(self.fldCB)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                                        QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(InicioLabel, 0, 0)
        grid.addWidget(rowLbl, 1, 0)
        grid.addWidget(self.rowCB, 1, 1)
        grid.addWidget(colLbl, 2, 0)
        grid.addWidget(self.colCB, 2, 1)
        grid.addWidget(agrLbl, 3,  0)
        grid.addWidget(self.agrCB, 3, 1)
        grid.addWidget(fldLbl, 4, 0)
        grid.addWidget(self.fldCB, 4, 1)
        grid.addWidget(buttonBox, 6, 0, 1, 2)
        self.setLayout(grid)
  
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        
        
class ZoomDlg(QDialog):
    def __init__(self, vista,  parent=None):
        super(ZoomDlg, self).__init__(parent)
        
        self.vista = vista

        cab_row = vista.fmtHeader('row', '\t',True) # max_col_level, row_range)
        cab_col = vista.fmtHeader('col', '\t', True)  #max_row_level, col_range)
        
        InicioLabel = QLabel("Defina el rango de seleccion")
        
        rowFLbl = QLabel("&Row  from")
        self.rowFCB = QComboBox()
        self.rowFCB.addItems(cab_row)
        rowFLbl.setBuddy(self.rowFCB)
 
        rowTLbl = QLabel("&Row  to")
        self.rowTCB = QComboBox()
        self.rowTCB.addItems(cab_row)
        rowTLbl.setBuddy(self.rowTCB)

        colFLbl = QLabel("&Col  from")
        self.colFCB = QComboBox()
        self.colFCB.addItems(cab_col)
        colFLbl.setBuddy(self.colFCB)
 
        colTLbl = QLabel("&Col  to")
        self.colTCB = QComboBox()
        self.colTCB.addItems(cab_col)
        colTLbl.setBuddy(self.colTCB)
        
        rowDimLbl= QLabel("Row &Dimensions")
        self.rowDimSpinBox = QSpinBox()
        rowDimLbl.setBuddy(self.rowDimSpinBox)
        self.rowDimSpinBox.setRange(1, self.vista.dim_row)
         
        colDimLbl= QLabel("col &Dimensions")
        self.colDimSpinBox = QSpinBox()
        colDimLbl.setBuddy(self.colDimSpinBox)
        self.colDimSpinBox.setRange(1, self.vista.dim_col)

        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(InicioLabel, 0, 0)
        grid.addWidget(rowFLbl, 1, 0)
        grid.addWidget(self.rowFCB, 1, 1)
        grid.addWidget(rowTLbl, 1, 2)
        grid.addWidget(self.rowTCB, 1, 3)
        grid.addWidget(colFLbl, 3, 0)
        grid.addWidget(self.colFCB, 3, 1)
        grid.addWidget(colTLbl, 3, 2)
        grid.addWidget(self.colTCB, 3, 3)
        
        grid.addWidget(rowDimLbl, 5, 0)
        grid.addWidget(self.rowDimSpinBox, 5, 1)
        grid.addWidget(colDimLbl, 5, 2)
        grid.addWidget(self.colDimSpinBox, 5, 3)

        
        
        grid.addWidget(buttonBox, 7, 0, 1, 2)
        self.setLayout(grid)
  
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

class NumberFormatDlg(QDialog):
    # Copyright (c) 2008 Qtrac Ltd. All rights reserved. Under the terms of GPL2.
    # portions modified by Werner Llacer
    def __init__(self, format, callback, parent=None):
        super(NumberFormatDlg, self).__init__(parent)

        punctuationRe = QRegExp(r"[ ,;:.]")
        
        thousandsLabel = QLabel("&Thousands separator")
        self.thousandsEdit = QLineEdit(format["thousandsseparator"])
        thousandsLabel.setBuddy(self.thousandsEdit)
        self.thousandsEdit.setMaxLength(1)
        self.thousandsEdit.setValidator(QRegExpValidator(
                punctuationRe, self))
        
        decimalMarkerLabel = QLabel("Decimal &marker")
        self.decimalMarkerEdit = QLineEdit(format["decimalmarker"])
        decimalMarkerLabel.setBuddy(self.decimalMarkerEdit)
        self.decimalMarkerEdit.setMaxLength(1)
        self.decimalMarkerEdit.setValidator(QRegExpValidator(
                punctuationRe, self))
        self.decimalMarkerEdit.setInputMask("X")
        
        decimalPlacesLabel = QLabel("&Decimal places")
        self.decimalPlacesSpinBox = QSpinBox()
        decimalPlacesLabel.setBuddy(self.decimalPlacesSpinBox)
        self.decimalPlacesSpinBox.setRange(0, 6)
        self.decimalPlacesSpinBox.setValue(format["decimalplaces"])
        
        self.redNegativesCheckBox = QCheckBox("&Red negative numbers")
        self.redNegativesCheckBox.setChecked(format["rednegatives"])
        
        self.yellowOutlierCheckBox = QCheckBox("&Yellow outliers")
        self.yellowOutlierCheckBox.setChecked(format["yellowoutliers"])
        
        self.format = format
        self.callback = callback

        grid = QGridLayout()
        grid.addWidget(thousandsLabel, 0, 0)
        grid.addWidget(self.thousandsEdit, 0, 1)
        grid.addWidget(decimalMarkerLabel, 1, 0)
        grid.addWidget(self.decimalMarkerEdit, 1, 1)
        grid.addWidget(decimalPlacesLabel, 2, 0)
        grid.addWidget(self.decimalPlacesSpinBox, 2, 1)
        grid.addWidget(self.redNegativesCheckBox, 3, 0, 1, 2)
        grid.addWidget(self.yellowOutlierCheckBox, 4, 0, 1, 2)
        self.setLayout(grid)

        self.thousandsEdit.textEdited['QString'].connect(self.checkAndFix)
        self.decimalMarkerEdit.textEdited['QString'].connect(self.checkAndFix)
        self.decimalPlacesSpinBox.valueChanged[int].connect(self.apply)
        self.redNegativesCheckBox.toggled[bool].connect(self.apply)
        self.yellowOutlierCheckBox.toggled[bool].connect(self.apply)
        self.setWindowTitle("Set Number Format (`Live')")


    def checkAndFix(self):
        #thousands = unicode(self.thousandsEdit.text())
        #decimal = unicode(self.decimalMarkerEdit.text())
        thousands = self.thousandsEdit.text()
        decimal = self.decimalMarkerEdit.text()
        if thousands == decimal:
            self.thousandsEdit.clear()
            self.thousandsEdit.setFocus()
        if len(decimal) == 0:
            self.decimalMarkerEdit.setText(".")
            self.decimalMarkerEdit.selectAll()
            self.decimalMarkerEdit.setFocus()
        self.apply()


    def apply(self):
        self.format["thousandsseparator"] = (
                #unicode(self.thousandsEdit.text()))
                self.thousandsEdit.text())
        self.format["decimalmarker"] = (
                #unicode(self.decimalMarkerEdit.text()))
                self.decimalMarkerEdit.text())
        self.format["decimalplaces"] = (
                self.decimalPlacesSpinBox.value())
        self.format["rednegatives"] = (
                self.redNegativesCheckBox.isChecked())
        self.format["yellowoutilers"] = (
                self.yellowOutlierCheckBox.isChecked())

        self.callback()


def main():
    app = QApplication(sys.argv)
    
    title = 'Hoja de seleccion de propiedades'
    ctexts = (u"C's", u'EH Bildu', u'EAJ-PNV', u'PP', u'PSOE', u'PODEMOS', u'GBAI', u'CCa-PNC', u'IU-UPeC', u'M\xc9S', u'DL', u'PODEMOS-COMPROM\xcdS', u'N\xd3S', u'EN COM\xda', u'PODEMOS-En Marea-ANOVA-EU', u'ERC-CATSI')
    context=[[ctexts[k],None] for k in range(len(ctexts))]
    context[3][1]='oleole'
    context[4][1]=5
 
    form = propertySheetDlg(title,context)
    form.show()
    if form.exec_():
        cdata = [context[k][1] for k in range(len(ctexts))]
        print('a la vuelta de publicidad',cdata)
        sys.exit()

if __name__ == '__main__':
    main()
