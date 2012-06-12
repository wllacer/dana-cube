#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012 Werner Llacer. All rights reserved.. Under the terms of the GPL 2
## Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from future_builtins import *

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

#from core import *

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
        
        self.connect(buttonBox, SIGNAL("accepted()"),
                            self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                            self, SLOT("reject()"))
                            
class VistaDlg(QDialog):
    def __init__(self, cubo_eleg,  parent=None):
        super(VistaDlg, self).__init__(parent)
        
        self.cubo = cubo_eleg
        datos_cubo = self.cubo.lista
        
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
  
        self.connect(buttonBox, SIGNAL("accepted()"),
                            self, SLOT("accept()"))
        self.connect(buttonBox, SIGNAL("rejected()"),
                           self, SLOT("reject()"))


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

        self.connect(self.thousandsEdit,
                SIGNAL("textEdited(QString)"), self.checkAndFix)
        self.connect(self.decimalMarkerEdit,
                SIGNAL("textEdited(QString)"), self.checkAndFix)
        self.connect(self.decimalPlacesSpinBox,
                SIGNAL("valueChanged(int)"), self.apply)
        self.connect(self.redNegativesCheckBox,
                SIGNAL("toggled(bool)"), self.apply)
        self.setWindowTitle("Set Number Format (`Live')")


    def checkAndFix(self):
        thousands = unicode(self.thousandsEdit.text())
        decimal = unicode(self.decimalMarkerEdit.text())
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
                unicode(self.thousandsEdit.text()))
        self.format["decimalmarker"] = (
                unicode(self.decimalMarkerEdit.text()))
        self.format["decimalplaces"] = (
                self.decimalPlacesSpinBox.value())
        self.format["rednegatives"] = (
                self.redNegativesCheckBox.isChecked())
        self.format["yellowoutilers"] = (
                self.yellowOutlierCheckBox.isChecked())

        self.callback()
