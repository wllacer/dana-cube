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


(ixWDestination,ixWFilter,ixWGraph) = range(3)


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

        extentBox = QGroupBox("¿Qué desea exportar?")

        self.allRB = QRadioButton("&Todo")
        self.visibleRB = QRadioButton("Sólo las columnas visibles")
        self.selectRB = QRadioButton("Sólo el área seleccionada")

        self.allRB.setChecked(True)
        #TEMPORAL init
        self.visibleRB.setEnabled(False)
        self.selectRB.setEnabled(False)
        #TEMPORAL end
        extentBoxLayout = QHBoxLayout()
        extentBoxLayout.addWidget(self.allRB)
        extentBoxLayout.addWidget(self.visibleRB)
        extentBoxLayout.addWidget(self.selectRB)

        extentBox.setLayout(extentBoxLayout)
        extentBox.setAlignment(Qt.AlignHCenter)
        
        detailBox = QGroupBox("¿Qué información desea exportar?")

        self.fullRB = QRadioButton("&Todo")
        self.branchRB = QRadioButton("Sólo &Ramas")
        self.leavesRB = QRadioButton("Sólo &hojas")
        self.leavesRB.setChecked(True)
        
        self.fullRB.clicked.connect(self.controlTotal)
        self.branchRB.clicked.connect(self.controlTotal)
        self.leavesRB.clicked.connect(self.controlTotal)
        
        detailBoxLayout = QHBoxLayout()
        detailBoxLayout.addWidget(self.fullRB)
        detailBoxLayout.addWidget(self.branchRB)
        detailBoxLayout.addWidget(self.leavesRB)

        detailBox.setLayout(detailBoxLayout)
        detailBox.setAlignment(Qt.AlignHCenter)
        
        self.totalCB = QCheckBox("Con Totales")
        self.totalCB.setEnabled(False)
        self.vertHdrCB = QCheckBox("Con cabeceras horizontales sin duplicados")
        self.horHdrCB = QCheckBox("Con cabeceras verticales  sin duplicados")
        self.vertHdrCB.setChecked(True)
        self.horHdrCB.setChecked(True)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(extentBox)
        mainLayout.addWidget(detailBox)
        mainLayout.addWidget(self.totalCB)
        mainLayout.addWidget(self.vertHdrCB)
        mainLayout.addWidget(self.horHdrCB)
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
        if wizard.page(ixWFilter).allRB.isChecked():
            parms['filter']['scope'] = 'all'
        elif wizard.page(ixWFilter).visibleRB.isChecked():
            parms['filter']['scope'] = 'visible'
        elif wizard.page(ixWFilter).selectRB.isChecked():
            parms['filter']['scope'] = 'select'
        if wizard.page(ixWFilter).fullRB.isChecked():
            parms['filter']['content'] = 'full'
        elif wizard.page(ixWFilter).branchRB.isChecked():
            parms['filter']['content'] = 'branch'
        elif wizard.page(ixWFilter).leavesRB.isChecked():    
            parms['filter']['content'] = 'leaf'
        parms['filter']['totals'] = wizard.page(ixWFilter).totalCB.isChecked()
        parms['filter']['horSparse'] = wizard.page(ixWFilter).horHdrCB.isChecked()
        parms['filter']['verSparse']= wizard.page(ixWFilter).vertHdrCB.isChecked()
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
