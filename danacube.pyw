#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint


from PyQt5.QtCore import Qt,QSortFilterProxyModel
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView

from core import Cubo,Vista
from dialogs import *
from util.jsonmgr import load_cubo
from models import *

from user_functions import *


#FIXED 1 zoom view breaks. Some variables weren't available
#     FIXME zoom doesn't trigger any action with the new interface
#FIXED 1 config view doesn't fire. Definition too early
#     FIXED 2 there's no code to handle it now
#          FIXED right justified
#          FIXED refreshTable
#
#FIXED 1 cursor en trabajo app.setOverrideCursor
#FIXED formateo de la tabla
#FIXED 2 formateo de los elementos
#FIXED implementar sort en modelo
#TODO uso de formato numerico directamente en la view setNumberFormat
#ALERT dopado para que vaya siempre a datos de prueba

def waiting_effects(function):
    """
      decorator from http://stackoverflow.com/questions/8218900/how-can-i-change-the-cursor-shape-with-pyqt
      para poner el cursor en busy/libre al ejectuar una funcion que va a tardar
    """
    def new_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise e
            print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()
    return new_function

#def model_change(model):
    #"""
    #""" 
    #def new_function(*args, **kwargs):
        #model.beginResetModel()       
        #try:
            #return function(*args, **kwargs)
        #except Exception as e:
            #raise e
            #print("Error {}".format(e.args[0]))
        #finally:
            #model.endResetModel()
    #return new_function

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
        self.fileMenu = self.menuBar().addMenu("&Funciones de usuario")
        self.restorator = self.fileMenu.addAction("&Restaurar valores originales",self.restoreData,"Ctrl+R")
        self.restorator.setEnabled(False)
        for ind,item in enumerate(USER_FUNCTION_LIST):
             self.fileMenu.addAction(USER_FUNCTION_LIST[ind][0],lambda  idx=ind: self.dispatch(idx))        
        
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

        #TODO como crear menu de contexto https://wiki.python.org/moin/PyQt/Creating%20a%20context%20menu%20for%20a%20tree%20view
        
        self.view.setSortingEnabled(True)
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
        self.view.expandToDepth(2)
        # estas vueltas para permitir ordenacion
        # para que aparezcan colapsados los indices jerarquicos
        self.max_row_level = self.vista.dim_row
        self.max_col_level  = self.vista.dim_col
        self.row_range = [0, self.vista.row_hdr_idx.count() -1]
        self.col_range = [0, self.vista.col_hdr_idx.count() -1]
        
    @waiting_effects
    def autoCarga(self,my_cubos):
        base = my_cubos['default']
        self.cubo=Cubo(my_cubos[base['cubo']])
        self.vista = Vista(self.cubo, base['vista']['row'], base['vista']['col'],base['vista']['agregado'],base['vista']['elemento'])
        self.vista.format = self.format
        self.defineModel()
        
        
    def changeView(self,row, col, agregado, campo, total=True, estad=True):
        self.vista.setNewView(row, col, agregado, campo, totalizado=total, stats=estad)
        self.vista.toTree2D()
        self.model.beginResetModel()       
        self.model.datos=self.vista
        self.model.getHeaders()
        self.model.rootItem = self.vista.row_hdr_idx.rootItem
        self.model.endResetModel()
        self.view.expandToDepth(2)
        
    @waiting_effects
    def cargaVista(self,row, col, agregado, campo, total=True, estad=True):
        if self.vista is None:
            self.vista = Vista(self.cubo, row, col, agregado, campo, totalizado=total, stats=estad)
            self.vista.format = self.format
            self.defineModel()
        else:
            self.changeView(row, col, agregado, campo, total,estad)
            self.refreshTable()

        
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

        parametros = [None for k in range(6)]
       
        #TODO  falta el filtro
        if self.vista is not  None:
            parametros[0]=self.vista.row_id
            parametros[1]=self.vista.col_id
            parametros[2]=self.cubo.getFunctions().index(self.vista.agregado)
            parametros[3]=self.cubo.getFields().index(self.vista.campo)
            parametros[4]=self.vista.totalizado
            parametros[5]=self.vista.stats
        
        vistaDlg = VistaDlg(self.cubo,parametros, self)
            
        if vistaDlg.exec_():
            row = parametros[0]
            col = parametros[1]
            agregado = self.cubo.getFunctions()[parametros[2]]
            #campo = self.cubo.getFunctions()[parametros[1]]
            campo = vistaDlg.sheet.cellWidget(3,0).currentText() #otra manera de localizar
            totalizado = parametros[4]
            stats = parametros[5]

            self.cargaVista(row,col,agregado,campo,totalizado,stats)


    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """
        self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)

        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()
        self.refreshTable()
        
    @waiting_effects
    def traspose(self):
        self.model.beginResetModel()
        self.vista.traspose()
        self.model.getHeaders()
        self.model.rootItem = self.vista.row_hdr_idx.rootItem
        self.model.endResetModel()
        self.view.expandToDepth(2)

        #self.refreshTable()
        #app.restoreOverrideCursor()
        #self.refreshTable()file:///home/werner/projects/dana-cube.git/danacube.pyw


    @waiting_effects
    def restoreData(self):
        #app.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.model.beginResetModel()
        for key in self.model.datos.row_hdr_idx.traverse(mode=1):
            item = self.model.datos.row_hdr_idx[key]
            item.restoreBackup()
            if self.vista.stats :
               item.setStatistics()

        #self.model.rootItem = self.vista.row_hdr_idx.rootItem    
        self.model.endResetModel()
        self.view.expandToDepth(2)
        #app.restoreOverrideCursor()
        self.restorator.setEnabled(False)

    def requestFunctionParms(self,spec,values):
        app.restoreOverrideCursor()
        parmDialog = propertySheetDlg('Introduzca los valores a simular',spec,values, self)
        if parmDialog.exec_():
            pass
            #print([a_spec[k][1] for k in range(len(a_spec))])
        app.setOverrideCursor(QCursor(Qt.WaitCursor))

        
    def funDispatch(self,entry,ind):
        #FIXME clarificar codificacion. es enrevesada
        if entry[1] in ('colkey','colparm','rowparm'):
           if entry[1] in ('colkey','colparm'):
               guia = self.model.datos.col_hdr_idx
           else:
               guia = self.model.datos.row_hdr_idx
               
           a_key = [None for k in range(guia.count())]
           a_desc = [None for k in range(guia.count())]
           a_data = [ None for k in range(guia.count())]
           
           idx = 0
           for key in guia.traverse(mode=1):
               a_key[idx] = key.split(':')[-1]
               a_desc[idx] = guia[key].desc
               idx += 1
               
           if entry[1] in ('colparm','rowparm'):
              a_spec = [ [a_desc[k],None,None] for k in range(len(a_desc))]
              self.requestFunctionParms(a_spec,a_data)
              
        elif entry[1] in 'kwargs':
              a_spec = [ [argumento,None,None] for argumento in USER_KWARGS_LIST[entry[0]]]
              a_data = [ None for k in range(len(a_desc))]
              self.requestFunctionParms(a_spec,a_data)            
              
        for key in self.model.datos.row_hdr_idx.traverse(mode=1):
            item = self.model.datos.row_hdr_idx[key]
            item.setBackup()
            if entry[1] == 'row':
                item.setPayload(entry[0](item.getPayload()))
            elif entry[1] == 'item':
                entry[0](item)
            elif entry[1] == 'map':
                 item.setPayload(list(map(entry[0],item.getPayload())))
            elif entry[1] in ('colkey',):
                entry[0](item,a_key)
            elif entry[1] in ('colparm','rowparm','kwargs'):
                col_parm=[(a_spec[k][0],a_data[k]) for k in range(len(a_spec))] #nombre y valor
                entry[0](item,col_parm)
            if self.vista.stats :
               item.setStatistics()
               
             
    @waiting_effects    
    def dispatch(self,ind):
        #TODO reducir el numero de arrays temporales

        self.restorator.setEnabled(True)
        self.model.beginResetModel()

        for elem in USER_FUNCTION_LIST[ind][1]:
            self.funDispatch(elem,ind)
            if len(elem) > 2: 
                if elem[2] == 'leaf':
                    self.vista.recalcGrandTotal()
        self.model.endResetModel()
        self.view.expandToDepth(2)

            
    
        
    def refreshTable(self):
        self.model.emitModelReset()

if __name__ == '__main__':

    import sys
    # con utf-8, no lo recomiendan pero me funciona
    reload(sys)
    sys.setdefaultencoding('utf-8')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
