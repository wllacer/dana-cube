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

from widgets import * 
 
"""
  DEBUG DATA start
"""
cubo = None

        
class propertySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
    """
    def __init__(self,title,context,data,parent=None):   
        super(propertySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(context,data)
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
        self.setMinimumSize(QSize(480,310))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

    def accept(self):
        datos = self.sheet.values()
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.data[k] = valor
        QDialog.accept(self)

from util.fechas import *

class dateFilterDlg(QDialog):
    def __init__(self,descriptores=None,datos=None,parent=None):   
        """
        """
        if descriptores is None:
            return 
        else:
            self.descriptores = descriptores

        if datos is None:
            self.data = []
        else:
            self.data = datos
            
        super(dateFilterDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = []

        for k in self.descriptores:
            self.context.append(('\t {}'.format(k),
                                  (QComboBox,None,CLASES_INTERVALO),
                                  (QComboBox,None,TIPOS_INTERVALO),
                                  (QSpinBox,{"setRange":(1,366)},None,1),
                                  (QLineEdit,{"setEnabled":False},None),
                                  (QLineEdit,{"setEnabled":False},None),
                                  )
                        )
        rows = len(self.context)
        cols = max( [len(item) -1 for item in self.context ])  #FIXME
        self.sheet1=WPowerTable(rows,cols)
        for i,linea in enumerate(self.context):
            for j in range(1,len(linea)):
                self.sheet1.addCell(i,j -1,linea[j])
            self.sheet1.set(i,2,1)                
            self.sheet1.cellWidget(i,0).currentIndexChanged.connect(lambda :self.seleccionCriterio(i))
            self.sheet1.cellWidget(i,1).currentIndexChanged.connect(lambda :self.seleccionIntervalo(i))
            self.sheet1.cellWidget(i,2).valueChanged.connect(lambda :self.seleccionIntervalo(i))
            self.flipFlop(i,self.sheet1.get(i,0))

       #FIXME valor inicial        
        campos = [ k[0] for k in self.context ]
        self.sheet1.setVerticalHeaderLabels(campos)
        self.sheet1.resizeColumnsToContents()
        cabeceras = ('Tipo','Periodo','Rango','desde','hasta')
        self.sheet1.setHorizontalHeaderLabels(cabeceras)
        #
        InicioLabel1 = QLabel('Filtre el rango temporal que desea')

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)



        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        

        meatLayout.addWidget(InicioLabel1)
        meatLayout.addWidget(self.sheet1)
       
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(800,200))
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        
    def flipFlop(self,line,value):
        # puede ser un poco repetitivo, pero no se si es mas costoso el enable/disable que comprobar cada
        # vez si lo esta. Por lo menos el codigo es menos complejo y todavia no veo una razon para modificarlo
        if value == 0:
            self.sheet1.cellWidget(line,1).setEnabled(False)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        elif value == 1: 
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        else:
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(True)
        # ponemos los valores ejemplo

    def seleccionCriterio(self,idx):
        self.flipFlop(idx,self.sheet1.get(idx,0))
        self.seleccionIntervalo(idx)
            
    def seleccionIntervalo(self,idx):
        if self.sheet1.get(idx,0)  == 0:
            self.sheet1.set(idx,3,None)
            self.sheet1.set(idx,4,None)
        else:
            desde,hasta = dateRange(self.sheet1.get(idx,0),self.sheet1.get(idx,1),periodo=self.sheet1.get(idx,2))
            self.sheet1.set(idx,3,str(desde))
            self.sheet1.set(idx,4,str(hasta))

   
    def accept(self):
        self.data = self.sheet1.values()
        self.result = []
        self.result = []
        for k,valor in enumerate(self.data):
            if valor[0] == 0:
                continue
            else:
                self.result.append((self.descriptores[k],valor[0],valor[1],valor[2]))
        print(self.result)
        QDialog.accept(self)
    
class dataEntrySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de entrada de datos
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
    """
    def __init__(self,title,context,numrows,data,parent=None):   
        super(dataEntrySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WDataSheet(context,numrows)
        self.sheet.fill(data)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)

        #formLayout = QHBoxLayout()
        self.meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        formLayout = QVBoxLayout()
       
        self.meatLayout.addWidget(InicioLabel)
        self.meatLayout.addWidget(self.sheet)
        
        buttonLayout.addWidget(buttonBox)
        
        formLayout.addLayout(self.meatLayout)        
        formLayout.addLayout(buttonLayout)
        
        self.setLayout(formLayout)
        self.setMinimumSize(QSize(480,480))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

    def accept(self):
        tmp_data = self.sheet.values()
        for x in range(self.sheet.rowCount()):
            for y in range(self.sheet.columnCount()):
                self.data[x][y] = tmp_data[x][y]
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
        

class VistaDlg(propertySheetDlg):
    def __init__(self, cubo,parametros,parent=None):
        title = 'Eliga los parametros de la vista'
        self.context = []
        self.context.append(('Guia filas',QComboBox,None,cubo.getGuideNames()),)
        self.context.append(('Guia columnas',QComboBox,None,cubo.getGuideNames()),)
        self.context.append(('Función agregacion',QComboBox,None,cubo.getFunctions()),)
        self.context.append(('Campo de datos',QComboBox,None,cubo.getFields()),)
        self.context.append(('Con totales',QCheckBox,None),)
        self.context.append(('Con estadisticas',QCheckBox,None),)
        
        super(VistaDlg, self).__init__(title,self.context,parametros,parent)
        
        #self.sheet.resizeColumnsToContents()
        
        
        
        
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
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] llamadas de configuracion del widget
           context[3] signal,slots (me temo que a mano)
        """
        self.context = (
                        ("Thousands separator",
                            QLineEdit,
                            {'setMaxLength':1,'setValidator':QRegExpValidator(punctuationRe, self)},
                            None,
                        ),
                        ("Decimal marker",
                            QLineEdit,
                            {'setMaxLength':1,
                                'setValidator':QRegExpValidator(punctuationRe, self),
                                'setInputMask':"X"
                         },
                         None,
                        ),
                        ("Decimal places",
                            QSpinBox,
                            {"setRange":(0,6)},
                            None,
                        ),
                        ("Red negative numbers",
                            QCheckBox,
                            None,
                            None,
                        ),
                        ("&Yellow outliers",
                            QCheckBox,
                            None,
                            None,
                        )
                      )
        self.data = [format["thousandsseparator"],
                        format["decimalmarker"],
                        format["decimalplaces"],
                        format["rednegatives"],
                        format["yellowoutliers"],
                    ]
        
        self.format = format
        self.callback = callback

        
        grid = QGridLayout()
        self.sheet = WPropertySheet(self.context,self.data)
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
                
def mainNF():
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

#OJO requiere de una funcion que ya no existe camposDeTipo. Encontrar en backup/datalayer/directory.py
#from core import Cubo, Vista
#from util.jsonmgr import load_cubo
#from datalayer.directory import camposDeTipo

#def dateFilter():
    #from core import Cubo
    #from util.jsonmgr import load_cubo
    
    #app = QApplication(sys.argv)
    #parametros = [ 1, 0, 2,3, False, False ]
    #mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['film'])
    #vista=Vista(cubo,1,0,'sum','sakila.film.film_id')
    #descriptores = camposDeTipo("fecha",vista.cubo.db,vista.cubo.definition['table'])
    #form = dateFilterDlg(descriptores)
    ##form.show()
    #if form.exec_():
        ##cdata = [form.context[k][1] for k in range(len(parametros))]
        ##print('a la vuelta de publicidad',cdata)
        #sqlGrp = []
        ##OJO form.result lleva los indices desplazados respecto de form.data
        #for entry in form.result:
            #if entry[1] != 0:
                #intervalo = dateRange(entry[1],entry[2],periodo=entry[3])
                #sqlGrp.append((entry[0],'BETWEEN',intervalo))
        #if len(sqlGrp) > 0:
            #print(searchConstructor('where',{'where':sqlGrp}))
        #sys.exit()


if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #app = QApplication(sys.argv)
    #dateFilter()
    mainNF()

