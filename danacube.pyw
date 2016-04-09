#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTreeView
from PyQt5.QtXml import QDomDocument

from core import Cubo,Vista
from dialogs import *
from util.yamlmgr import load_cubo
from models import *

#TODO cursor en trabajo
#TODO formateo de la tabla
#TODO formateo de los elementos

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #CHANGE here
        self.fileMenu = self.menuBar().addMenu("&Cubo")
        self.fileMenu.addAction("&Open Cube ...", self.initCube, "Ctrl+O")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        self.fileMenu = self.menuBar().addMenu("&Vista")
        self.fileMenu.addAction("C&hange View ...", self.requestVista, "Ctrl+H")
        self.fileMenu.addAction("&Zoom View ...", self.zoomData, "Ctrl+Z")
        self.fileMenu.addAction("&Config ...",self.setNumberFormat,"Ctrl+F")
        #
        #self.format = dict(thousandsseparator=".", 
                                    #decimalmarker=",",
                                    #decimalplaces=2,
                                    #rednegatives=False, 
                                    #yellowoutliers=True)

        #CHANGE here
        # ¿Por que he de sustituir QDomDocument() ?
        self.vista = None
        self.model = None
        #self.model = ViewModel(QDomDocument(), self)
        self.view = QTreeView(self)
        self.view.setModel(self.model)

        self.setCentralWidget(self.view)
        self.setWindowTitle("Cubos")

    def initCube(self):
        my_cubos = load_cubo()
        #realiza la seleccion del cubo
        dialog = CuboDlg(my_cubos, self)
        if dialog.exec_():
            seleccion = str(dialog.cuboCB.currentText())
            self.cubo = Cubo(my_cubos[seleccion])
            self.cubo.fillGuias()
            self.vista = None
        self.setWindowTitle("Cubo "+ seleccion)
        self.requestVista()

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
            if self.vista is None:
                self.vista = Vista(self.cubo, row, col, agregado, campo)       
            else:             
                self.vista.setNewView(row, col, agregado, campo)

            newModel = TreeModel(self.vista, self)
            self.view.setModel(newModel)
            self.model = newModel

            # para que aparezcan colapsados los indices jerarquicos
            # TODO hay que configurar algun tipo de evento para abrirlos y un parametro de configuracion
            #self.max_row_level = self.vista.dim_row
            #self.max_col_level  = self.vista.dim_col
            self.max_row_level = 1
            self.max_col_level  = 1
            self.row_range = [0, len(self.vista.row_hdr_idx) -1]
            self.col_range = [0, len(self.vista.col_hdr_idx) -1]
          
            #self.refreshTable()
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
                #self.refreshTable()
                return
                
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """        
        #FIXME no funciona con la nueva arquitectura
        return
        if self.numberFormatDlg is None:
            print('paso cero')
            self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)
        print('defino')
        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()
        print('blablabla')


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
