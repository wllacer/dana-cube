#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint


from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt,QSortFilterProxyModel
from PyQt5.QtGui import QCursor,QColor
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QTreeView

from core import Cubo,Vista
from dialogs import *
from util.jsonmgr import load_cubo
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
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #CHANGE here
        self.fileMenu = self.menuBar().addMenu("&Cubo")
        self.fileMenu.addAction("&Open Cube ...", self.initCube, "Ctrl+O")
        self.fileMenu.addAction("C&hange View ...", self.requestVista, "Ctrl+H")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        self.fileMenu = self.menuBar().addMenu("&Opciones")
        #TODO skipped has to be retougth with the new interface
        #self.fileMenu.addAction("&Zoom View ...", self.zoomData, "Ctrl+Z")
        self.fileMenu.addAction("&Trasponer datos",self.traspose,"CtrlT")
        self.fileMenu.addAction("&Presentacion ...",self.setNumberFormat,"Ctrl+F")
        #
        self.format = dict(thousandsseparator=".", 
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False, 
                                    yellowoutliers=True)

        self.vista = None
        self.model = None
        self.cubo =  None
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
        
    def defineModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = TreeModel(self.vista, self)
        #self.view.setModel(newModel)
        #self.modelo=self.view.model
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(newModel)
        proxyModel.setSortRole(33)
        self.view.setModel(proxyModel)
        self.model = newModel #proxyModel

        # estas vueltas para permitir ordenacion
        # para que aparezcan colapsados los indices jerarquicos
        self.max_row_level = self.vista.dim_row
        self.max_col_level  = self.vista.dim_col
        self.row_range = [0, self.vista.row_hdr_idx.count() -1]
        self.col_range = [0, self.vista.col_hdr_idx.count() -1]

    def autoCarga(self,my_cubos):
        base = my_cubos['default']

        self.cubo=Cubo(my_cubos[base['cubo']])
        
        app.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.vista = Vista(self.cubo, base['vista']['row'], base['vista']['col'],base['vista']['agregado'],base['vista']['elemento']) 
        app.restoreOverrideCursor()   
        
        self.vista.format = self.format
        
        self.defineModel()
        
        
    def initCube(self):
        #FIXME casi funciona ... vuelve a leer el fichero cada vez
        my_cubos = load_cubo()
        if 'default' in my_cubos:
            if self.cubo is None:
                self.autoCarga(my_cubos)
                return
            del my_cubos['default']

        #realiza la seleccion del cubo
        
        dialog = CuboDlg(my_cubos, self)
        if dialog.exec_():
            seleccion = str(dialog.cuboCB.currentText())
            self.cubo = Cubo(my_cubos[seleccion])
            
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
                self.defineModel()
            else:
                self.model.beginResetModel()                
                self.vista.setNewView(row, col, agregado, campo)
                self.vista.toTree2D()
                self.model.datos=self.vista
                self.model.getHeaders()
                self.model.rootItem = self.vista.row_hdr_idx.rootItem
                self.model.endResetModel()
                self.refreshTable()



 
            app.restoreOverrideCursor()
 
            # TODO hay que configurar algun tipo de evento para abrirlos y un parametro de configuracion
            
            ##@waiting_effects
            #app.setOverrideCursor(QCursor(Qt.WaitCursor))
            #self.refreshTable()
            #app.restoreOverrideCursor()
                
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """        
        #FIXME no funciona con la nueva arquitectura
        self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)

        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()
        self.refreshTable()

    def traspose(self):
        self.model.beginResetModel()
        self.vista.traspose()
        self.model.getHeaders()
        self.model.rootItem = self.vista.row_hdr_idx.rootItem
        self.model.endResetModel()
        self.refreshTable()
        
        
    def refreshTable(self):
        self.model.emitModelReset()

if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
