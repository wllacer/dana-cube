#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTreeView

from core import Cubo,Vista
from dialogs import *
from util.yamlmgr import load_cubo
from models import *

#FIXED 1 zoom view breaks. Some variables weren't available 
#     FIXME zoom doesn't trigger any action with the new interface
#FIXED 1 config view doesn't fire. Definition too early     
#     FIXED 2 there's no code to handle it now
#          FIXME right justified
#          FIXME refreshTable
#
#FIXED 1 cursor en trabajo app.setOverrideCursor             
# TODO formateo de la tabla
#FIXED 2 formateo de los elementos
#DONE 2 implementar sort en modelo
#TODO uso de formato numerico directamente en la view setNumberFormat
#ALERT dopado para que vaya siempre a datos de prueba
'''
# decorador para el cursor. tomado de http://stackoverflow.com/questions/8218900/how-can-i-change-the-cursor-shape-with-pyqt
# estoy verde para usarlo
def waiting_effects(function):
    def new_function(*args, **kwargs):
        app.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()
    return new_function
'''
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
        self.format = dict(thousandsseparator=".", 
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False, 
                                    yellowoutliers=True)

        self.vista = None
        self.model = None

        self.view = QTreeView(self)
        self.view.setModel(self.model)
        
        
        self.view.setSortingEnabled(True);
        #self.view.setRootIsDecorated(False)
        self.view.setAlternatingRowColors(True)
        self.view.sortByColumn(0, Qt.AscendingOrder)
        #ALERT
        self.initCube()


        self.setCentralWidget(self.view)
        self.setWindowTitle("Cubos")
        
    def autoCarga(self,my_cubos):
        base = my_cubos['default']
        pprint(base)
        self.cubo=Cubo(my_cubos[base['cubo']])
        app.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.cubo.fillGuias()
        self.vista = Vista(self.cubo, base['vista']['row'], base['vista']['col'],base['vista']['agregado'],base['vista']['elemento']) 
        app.restoreOverrideCursor()   
        self.vista.format = self.format
        newModel = TreeModel(self.vista, self)
        #self.view.setModel(newModel)
        #self.modelo=self.view.model
        #self.model = newModel
        proxyModel = NumberSortModel()
        proxyModel.setSourceModel(newModel)
        self.view.setModel(proxyModel)
        self.model = proxyModel
        self.max_row_level = self.vista.dim_row
        self.max_col_level  = self.vista.dim_col
        self.max_row_level = 1
        self.max_col_level  = 1
        self.row_range = [0, len(self.vista.row_hdr_idx) -1]
        self.col_range = [0, len(self.vista.col_hdr_idx) -1]
        
    def initCube(self):
        #FIXME casi funciona ... vuelve a leer el fichero cada vez
        my_cubos = load_cubo()
        if 'default' in my_cubos:
            self.autoCarga(my_cubos)
            del my_cubos['default']
        else:
        #realiza la seleccion del cubo
        
            dialog = CuboDlg(my_cubos, self)
            if dialog.exec_():
                seleccion = str(dialog.cuboCB.currentText())
                self.cubo = Cubo(my_cubos[seleccion])
                
                app.setOverrideCursor(QCursor(Qt.WaitCursor))
                self.cubo.fillGuias()
                app.restoreOverrideCursor()
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
            
            app.setOverrideCursor(QCursor(Qt.WaitCursor))
            if self.vista is None:
                self.vista = Vista(self.cubo, row, col, agregado, campo) 
                self.vista.format = self.format
            else:  

                self.vista.setNewView(row, col, agregado, campo)
            app.restoreOverrideCursor()
            # estas vueltas para permitir ordenacion
            newModel = TreeModel(self.vista, self)
            #self.view.setModel(newModel)
            #self.modelo=self.view.model
            proxyModel = NumberSortModel()
            proxyModel.setSourceModel(newModel)
            self.view.setModel(proxyModel)
            self.model = proxyModel

            # para que aparezcan colapsados los indices jerarquicos
            # TODO hay que configurar algun tipo de evento para abrirlos y un parametro de configuracion
            self.max_row_level = self.vista.dim_row
            self.max_col_level  = self.vista.dim_col
            self.max_row_level = 1
            self.max_col_level  = 1
            self.row_range = [0, len(self.vista.row_hdr_idx) -1]
            self.col_range = [0, len(self.vista.col_hdr_idx) -1]
            
            ##@waiting_effects
            #app.setOverrideCursor(QCursor(Qt.WaitCursor))
            #self.refreshTable()
            #app.restoreOverrideCursor()
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
                #@waiting_effects
                app.setOverrideCursor(QCursor(Qt.WaitCursor))
                self.refreshTable()
                app.restoreOverrideCursor()

                
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """        
        #FIXME no funciona con la nueva arquitectura
        self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)

        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()

    def refreshTable(self):
        self.model.emitDataChanged()
if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
