#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

'''
Documentation, License etc.

@package estimaciones
# 0.3
'''
from PyQt5.QtCore import Qt,QRegExp
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QRegExpValidator
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QLineEdit,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox, QFileDialog,QPushButton,QHBoxLayout


(ixWFilter,ixWDestination,ixWGraph) = range(3)


class ExportWizard(QWizard):
    def __init__(self):
        super(ExportWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.setPage(ixWDestination, WzDestination())
        self.setPage(ixWFilter, WzFilter())
#        self.setPage(ixWGraph, WzGraph())
        self.setWindowTitle('Exportar datos del cubo')
        self.show()

class WzDestination(QWizardPage):
    def __init__(self,parent=None):
        super(WzDestination,self).__init__(parent)
        self.setTitle("Destino")
        self.setSubTitle(""" Seleccione el destino de los datos que quiere exportar""")
    
        punctuationRe = QRegExp(r"[ ,;:.'\"\/]")
        decimalRe = QRegExp(r"[,.]")
        self.tipo = None
        
        nomFicheroLbl = QLabel("&Nombre:")
        self.nomFichero = QLineEdit()
        nomFicheroLbl.setBuddy(self.nomFichero)
        self.nomFichero.setReadOnly(True)

        tipoFicheroLbl = QLabel("&Tipo")
        self.tipoFichero = QLineEdit()
        tipoFicheroLbl.setBuddy(self.tipoFichero)
        self.tipoFichero.setEnabled(False)
        
        selFicheroBtn = QPushButton('Cambiar')
        selFicheroBtn.clicked.connect(self.selecciona)
        
        separadorCamposLbl = QLabel("Separador &Campos")
        self.separadorCampos = QLineEdit()
        separadorCamposLbl.setBuddy(self.separadorCampos)
        self.separadorCampos.setMaxLength(1)
        self.separadorCampos.setValidator(QRegExpValidator(punctuationRe,self))
        self.separadorCampos.setText(';')
        
        separadorDecimalesLbl = QLabel("Marca de &Decimales")
        self.separadorDecimales = QLineEdit()
        separadorDecimalesLbl.setBuddy(self.separadorDecimales)
        self.separadorDecimales.setMaxLength(1)
        self.separadorDecimales.setValidator(QRegExpValidator(decimalRe,self))
        self.separadorDecimales.setText(',')

        separadorTextosLbl = QLabel("Marca de &Textos")
        self.separadorTextos = QLineEdit()
        separadorTextosLbl.setBuddy(self.separadorTextos)
        self.separadorTextos.setMaxLength(1)
        self.separadorTextos.setValidator(QRegExpValidator(punctuationRe,self))
        self.separadorTextos.setText('"')
        
        edicionLbl= QLabel("¿Quiere formatear los numeros?")
        self.edicion = QCheckBox()
        edicionLbl.setBuddy(self.edicion)

        gLayout = QGridLayout()
        gLayout.addWidget(nomFicheroLbl,0,0)
        gLayout.addWidget(self.nomFichero,0,1)
        gLayout.addWidget(selFicheroBtn,0,4)
        gLayout.addWidget(tipoFicheroLbl,1,0)
        gLayout.addWidget(self.tipoFichero,1,1)
        gLayout.addWidget(separadorCamposLbl,3,0)
        gLayout.addWidget(self.separadorCampos,3,1)
        gLayout.addWidget(separadorDecimalesLbl,4,0)
        gLayout.addWidget(self.separadorDecimales,4,1)
        gLayout.addWidget(separadorTextosLbl,5,0)
        gLayout.addWidget(self.separadorTextos,5,1)
        gLayout.addWidget(edicionLbl,6,0)
        gLayout.addWidget(self.edicion,6,1)
        self.setLayout(gLayout)
        
        self.registerField('Nombre*',self.nomFichero)
        self.registerField('Tipo*',self.tipoFichero)
        
    def initializePage(self):
       self.selecciona()
       
    def selecciona(self):
    
        filename,filter = QFileDialog.getSaveFileName(self,
                                                  caption="Nombre del fichero",
                                                  directory="datos",
                                                  filter = "CSV (*.csv);; Excel (*.xlsx);; Json (*.json) ;; HTML (*.html)",
                                                  initialFilter="CSV (*.csv)",
                                                  )
        if filename:
            self.nomFichero.setText(filename)
            self.tipoFichero.setText(filter)

class WzFilter(QWizardPage):
    def __init__(self,parent=None):
        super(WzFilter,self).__init__(parent)
        self.setTitle("Contenido")
        self.setSubTitle(""" Seleccione que datos exactamente desea exportar """)

        #extentBox = QGroupBox("¿Qué desea exportar?")

        #self.allRB = QRadioButton("&Todo")
        #self.visibleRB = QRadioButton("Sólo las columnas visibles")
        #self.selectRB = QRadioButton("Sólo el área seleccionada")

        #self.allRB.setChecked(True)
        ##TEMPORAL init
        #self.visibleRB.setEnabled(False)
        #self.selectRB.setEnabled(False)
        ##TEMPORAL end
        #extentBoxLayout = QHBoxLayout()
        #extentBoxLayout.addWidget(self.allRB)
        #extentBoxLayout.addWidget(self.visibleRB)
        #extentBoxLayout.addWidget(self.selectRB)

        #extentBox.setLayout(extentBoxLayout)
        #extentBox.setAlignment(Qt.AlignHCenter)
        RowBox = QGroupBox()
        
        detailRowBox = QGroupBox("\t¿Qué filas desea exportar?")

        self.RowFullRB = QRadioButton("&Todo")
        self.RowBranchRB = QRadioButton("Sólo &Ramas")
        self.RowLeavesRB = QRadioButton("Sólo &hojas")
        self.RowLeavesRB.setChecked(True)
                
        detailRowBoxLayout = QHBoxLayout()
        detailRowBoxLayout.addWidget(self.RowFullRB)
        detailRowBoxLayout.addWidget(self.RowBranchRB)
        detailRowBoxLayout.addWidget(self.RowLeavesRB)
        detailRowBox.setLayout(detailRowBoxLayout)
        detailRowBox.setAlignment(Qt.AlignHCenter)
        
        addRowBoxLayout = QHBoxLayout()
        self.totalRowCB = QCheckBox("Con Totales")
        
        self.rowHdrCB = QCheckBox("Cabeceras sin duplicados")
        self.rowHdrCB.setChecked(True)
        
        addRowBoxLayout.addWidget(self.totalRowCB)
        addRowBoxLayout.addWidget(self.rowHdrCB)
        
        RowBoxLayout= QVBoxLayout()
        RowBoxLayout.addWidget(detailRowBox)
        RowBoxLayout.addLayout(addRowBoxLayout)
        RowBox.setLayout(RowBoxLayout)
        
        ColBox = QGroupBox()
        
        detailColBox = QGroupBox("\t¿Qué columans desea exportar?")

        self.ColFullRB = QRadioButton("&Todo")
        self.ColBranchRB = QRadioButton("Sólo &Ramas")
        self.ColLeavesRB = QRadioButton("Sólo &hojas")
        self.ColLeavesRB.setChecked(True)
                
        detailColBoxLayout = QHBoxLayout()
        detailColBoxLayout.addWidget(self.ColFullRB)
        detailColBoxLayout.addWidget(self.ColBranchRB)
        detailColBoxLayout.addWidget(self.ColLeavesRB)
        detailColBox.setLayout(detailColBoxLayout)
        detailColBox.setAlignment(Qt.AlignHCenter)
        
        addColBoxLayout = QHBoxLayout()
        self.totalColCB = QCheckBox("Con Totales")
        
        self.colHdrCB = QCheckBox("Cabeceras sin duplicados")
        self.colHdrCB.setChecked(True)
        
        addColBoxLayout.addWidget(self.totalColCB)
        addColBoxLayout.addWidget(self.colHdrCB)
        
        ColBoxLayout= QVBoxLayout()
        ColBoxLayout.addWidget(detailColBox)
        ColBoxLayout.addLayout(addColBoxLayout)
        ColBox.setLayout(ColBoxLayout)

        mainLayout = QVBoxLayout()
#        mainLayout.addWidget(extentBox)
        mainLayout.addWidget(RowBox)
        mainLayout.addWidget(ColBox)
        #mainLayout.addWidget(self.totalCB)
        #mainLayout.addWidget(self.horHdrCB)
        self.setLayout(mainLayout)
    
    def controlTotal(self,enabled):
        if self.fullRB.isChecked():
            self.totalCB.setEnabled(True)
        else:
            self.totalCB.setChecked(False)
            self.totalCB.setEnabled(False)

class WzGraph(QWizardPage):
    def __init__(self,parent=None):
        super(WzGraph,self).__init__(parent)
        self.setTitle("Gráfico elegido")
        self.setSubTitle(""" Introduzca el campo por el que desea agrupar los resultados y como determinar el texto asociado a los valores de estos campos""")

    
    #def estadoLink(self):
        #if self.linkCheck.isChecked():
            #self.wizard().setStartId(ixWFilter);
            #self.wizard().restart()        
    #def initializePage(self):
    


def exportWizard():
    parms = dict()
    wizard = ExportWizard()        
    if wizard.exec_() :
        parms['file'] = wizard.page(ixWDestination).nomFichero.text()
        parms['type'] = tipoCorto(wizard.page(ixWDestination).tipoFichero.text())
        parms['csvProp'] = dict()
        parms['csvProp']['fldSep'] =wizard.page(ixWDestination).separadorCampos.text()
        parms['csvProp']['decChar'] =wizard.page(ixWDestination).separadorDecimales.text()
        parms['csvProp']['txtSep'] = wizard.page(ixWDestination).separadorTextos.text()
        parms['NumFormat'] = wizard.page(ixWDestination).edicion.isChecked()
        parms['filter'] = dict()
        parms['filter']['scope'] = 'all'
        parms['filter']['row'] = dict()
        parms['filter']['col'] = dict()
        if wizard.page(ixWFilter).RowFullRB.isChecked():
            parms['filter']['row']['content'] = 'full'
        elif wizard.page(ixWFilter).RowBranchRB.isChecked():
            parms['filter']['row']['content'] = 'branch'
        elif wizard.page(ixWFilter).RowLeavesRB.isChecked():    
            parms['filter']['row']['content'] = 'leaf'
        parms['filter']['row']['totals'] = wizard.page(ixWFilter).totalRowCB.isChecked()
        parms['filter']['row']['Sparse'] = wizard.page(ixWFilter).rowHdrCB.isChecked()

        if wizard.page(ixWFilter).ColFullRB.isChecked():
            parms['filter']['col']['content'] = 'full'
        elif wizard.page(ixWFilter).ColBranchRB.isChecked():
            parms['filter']['col']['content'] = 'branch'
        elif wizard.page(ixWFilter).ColLeavesRB.isChecked():    
            parms['filter']['col']['content'] = 'leaf'
        parms['filter']['col']['totals'] = wizard.page(ixWFilter).totalColCB.isChecked()
        parms['filter']['col']['Sparse'] = wizard.page(ixWFilter).colHdrCB.isChecked()

    return parms

def tipoCorto(tipoLargo):
    tipo = 'csv'
    if 'csv' in tipoLargo.lower():
        pass
    elif 'xls' in tipoLargo.lower():
        tipo = 'xls'
    elif 'json' in tipoLargo.lower():
        tipo = 'json'
    elif 'htm' in tipoLargo.lower():
        tipo = 'html'
    return tipo   
    
if __name__ == '__main__':
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    app = QApplication(sys.argv)
    #miniCube()
    exportWizard()
