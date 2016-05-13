#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012,2016 Werner Llacer. All rights reserved.. Under the terms of the LGPL 2
## numberFormatDlg inspired by Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2

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
        super(WPropertySheet, self).__init__(len(context),1,parent)
        # cargando parametros de defecto
        self.context = context

        #self.setRowCount(len(context))
        #self.setColumnCount(1)
        
        cabeceras = [ k[0] for k in self.context ]
        for k in range(len(self.context)):
            self.add(k)
        #cdata     = [ k[1] for k in self.context ]
        #for k,item in enumerate(cdata):
            ##tableItem= QTableWidgetItem(str(item))
            ##self.sheet.setItem(k,0,tableItem)
            ##self.sheet.setCellWidget(k,0,QLineEdit(str(item) if item is not None else None))
            #editItem = QLineEdit()
            #editItem.setText(str(item) if item is not None else '')
            #self.setCellWidget(k,0,editItem)


        self.setVerticalHeaderLabels(cabeceras)
        
        #self.resizeColumnsToContents()
        self.resizeRowsToContents()
    """
      skeletor:
        if type is None or type == QLineEdit:
            pass
        elif type == QCheckBox:
            pass
        elif type == QSpinBox:
            pass
        else:
            print('Noooop',x)
      
    """
    def add(self,x,y=0):
        item = self.context[x][1]
        type = self.context[x][2]
        editItem = None
        if type is None or type == QLineEdit:
            editItem = QLineEdit()
            editItem.setText(str(item) if item is not None else '')
        elif type == QCheckBox:
            editItem = QCheckBox()
            editItem.setChecked(item)
        elif type == QSpinBox:
            editItem = QSpinBox()
            editItem.setValue(item)
        else:
            print('Noooop',x)
        if self.context[x][3] is not None:
            #TODO ejecuto los metodos dinamicamente. por ahora solo admite parametros en lista  
            #TODO vale como funcion utilitaria
            for func in self.context[x][3]:
                shoot = getattr(editItem,func)
                if isinstance(self.context[x][3][func],(list,tuple)):
                    parms = self.context[x][3][func]
                else:
                    parms = (self.context[x][3][func],)
                shoot(*parms)

        self.setCellWidget(x,y,editItem)

    def set(self,x,y,value):
        type = self.context[x][2]
        if type is None or type == QLineEdit:
            self.cellWidget(x,y).setText(value)
        elif type == QCheckBox:
            self.cellWidget(x,y).setChecked(value)
        elif type == QSpinBox:
            self.cellWidget(x,y).setValue(value)
        else:
            print('Noooop',x)

        
    def get(self,x,y):
        type = self.context[x][2]
        if type is None or type == QLineEdit:
            return self.cellWidget(x,y).text()
        elif type == QCheckBox:
            return self.cellWidget(x,y).isChecked()
        elif type == QSpinBox:
            return self.cellWidget(x,y).value()
        else:
            print('Noooop',x)
        

    
    def values(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            #if self.sheet.cellWidget(k,0) is None:
                #print('elemento {} vacio'.format(k))
                #continue
            valores.append(self.get(k,0))
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

    def __init__(self, format, callback, parent=None):
        super(NumberFormatDlg, self).__init__(parent)

        punctuationRe = QRegExp(r"[ ,;:.]")
        
        self.context=[]
        """
context[0] titulos de las filas
           context[1] valores iniciales
           context[2] widget a utilizar (defecto QLineEdit)
           context[3] llamadas de configuracion del widget
           context[4] signal,slots (me temo que a mano)
        """        
        thousands = [None for j in range(5)]
        thousands[0]="&Thousands separator"
        thousands[1]=format["thousandsseparator"]
        thousands[2]=QLineEdit
        thousands[3]={'setMaxLength':1,
                 'setValidator':QRegExpValidator(punctuationRe, self)
                 }
        #thousands[4]={"textEdited['QString']":self.checkAndFix}
        thousands[4]={"textEditedEvent":self.checkAndFix}
        
        decimalmarker = [None for j in range(5)]
        decimalmarker[0]="Decimal &marker"
        decimalmarker[1]=format["decimalmarker"]
        decimalmarker[2]=QLineEdit
        decimalmarker[3]={'setMaxLength':1,
                 'setValidator':QRegExpValidator(punctuationRe, self),
                 'setInputMask':"X"
                 }
        
        
        decimalplaces = [None for j in range(5)]
        decimalplaces[0]="&Decimal places"
        decimalplaces[1]=format["decimalplaces"]
        decimalplaces[2]=QSpinBox
        decimalplaces[3]={"setRange":(0,6)}
                          
        rednegatives = [None for j in range(5)]
        rednegatives[0]="Red negative numbers"
        rednegatives[1]=format["rednegatives"]
        rednegatives[2]=QCheckBox
        rednegatives[3]=None        

        yellowoutliers = [None for j in range(5)]
        yellowoutliers[0]="&Yellow outliers"
        yellowoutliers[1]=format["yellowoutliers"]
        yellowoutliers[2]=QCheckBox
        yellowoutliers[3]=None        
        
        self.context.append(thousands)
        self.context.append(decimalmarker)
        self.context.append(decimalplaces)
        self.context.append(rednegatives)
        self.context.append(yellowoutliers)
        
        
        self.format = format
        self.callback = callback

        
        grid = QGridLayout()
        self.sheet = WPropertySheet(self.context)
        grid.addWidget(self.sheet, 0, 0)
        self.setLayout(grid)
        self.setMinimumSize(QSize(300,220))

        self.sheet.cellWidget(0,0).textEdited['QString'].connect(self.checkAndFix)
        self.sheet.cellWidget(1,0).textEdited['QString'].connect(self.checkAndFix)
        self.sheet.cellWidget(2,0).valueChanged[int].connect(self.apply)
        self.sheet.cellWidget(3,0).toggled[bool].connect(self.apply)
        self.sheet.cellWidget(4,0).toggled[bool].connect(self.apply)
        
        self.setWindowTitle("Set Number Format (`Live')")


    def checkAndFix(self):
        #thousands = unicode(self.thousandsEdit.text())
        #decimal = unicode(self.decimalMarkerEdit.text())
        thousands = self.sheet.get(0,0)
        decimal = self.sheet.get(1,0)
        if thousands == decimal:
            self.sheet.cellWidget(0,0).clear()
            self.sheet.cellWidget(0,0).setFocus()
        if len(decimal) == 0:
            self.sheet.set(1,0,".")
            self.sheet.cellWidget(1,0).selectAll()
            self.sheet.cellWidget(1,0).setFocus()
        
        self.apply()


    def apply(self):
        self.format["thousandsseparator"] = (
                #unicode(self.thousandsEdit.text()))
                self.sheet.get(0,0))
        self.format["decimalmarker"] = (
                #unicode(self.decimalMarkerEdit.text()))
                self.sheet.get(1,0))
        self.format["decimalplaces"] = (
                self.sheet.get(2,0))
        self.format["rednegatives"] = (
                self.sheet.get(3,0))
        self.format["yellowoutilers"] = (
                self.sheet.get(3,0))

        self.callback()

def main():
    app = QApplication(sys.argv)

    format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)

     
    #title = 'Hoja de seleccion de propiedades'
    #ctexts = (u"C's", u'EH Bildu', u'EAJ-PNV', u'PP', u'PSOE', u'PODEMOS', u'GBAI', u'CCa-PNC', u'IU-UPeC', u'M\xc9S', u'DL', u'PODEMOS-COMPROM\xcdS', u'N\xd3S', u'EN COM\xda', u'PODEMOS-En Marea-ANOVA-EU', u'ERC-CATSI')
    #context=[[ctexts[k],None] for k in range(len(ctexts))]
    #context[3][1]='oleole'
    #context[4][1]=5
    #form = propertySheetDlg(context)
    
    form = NumberFormatDlg(format,None)
    form.show()
    if form.exec_():
        cdata = [context[k][1] for k in range(len(ctexts))]
        print('a la vuelta de publicidad',cdata)
        sys.exit()

if __name__ == '__main__':
    main()
