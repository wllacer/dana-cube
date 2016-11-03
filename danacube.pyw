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

from core import Cubo,Vista, mergeString
from dialogs import *
from util.jsonmgr import *
from models import *

from user_functions import *
from util.decorators import waiting_effects 

from util.tree import traverse
from filterDlg import filterDialog
from dictmgmt.datadict import DataDict
from cubemgmt.cubetree import traverseTree

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
        
        self.optionsMenu = self.menuBar().addMenu("&Opciones")
        #TODO skipped has to be retougth with the new interface
        #self.optionsMenu.addAction("&Zoom View ...", self.zoomData, "Ctrl+Z")
        self.filterActions = dict()
        self.filterActions['create'] = self.optionsMenu.addAction('Crear &Filtro',self.setFilter,"Ctrl+K")
        self.filterActions['drop'] = self.optionsMenu.addAction('Borrar &Filtro',self.dropFilter,"Ctrl+K")
        self.filterActions['save'] = self.optionsMenu.addAction('Guardar &Filtro permanentemente',self.saveFilter,"Ctrl+K")
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)
        self.optionsMenu.addSeparator()

        self.optionsMenu.addAction("&Trasponer datos",self.traspose,"CtrlT")
        self.optionsMenu.addAction("&Presentacion ...",self.setNumberFormat,"Ctrl+F")
        #
        self.userFunctionsMenu = self.menuBar().addMenu("&Funciones de usuario")
        self.restorator = self.userFunctionsMenu.addAction("&Restaurar valores originales",self.restoreData,"Ctrl+R")
        self.restorator.setEnabled(False)
        self.userFunctionsMenu.addSeparator()
        
        for ind,item in enumerate(USER_FUNCTION_LIST):
             self.userFunctionsMenu.addAction(USER_FUNCTION_LIST[ind][0],lambda  idx=ind: self.dispatch(idx))        
        
        self.format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)

        self.vista = None
        self.baseModel = None
        self.cubo =  None
        self.view = QTreeView(self)
        self.view.setModel(self.baseModel)
        self.filtro = ''

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
        self.baseModel = newModel #proxyModel
        self.view.expandToDepth(2)
        # estas vueltas para permitir ordenacion
        # para que aparezcan colapsados los indices jerarquicos
        self.max_row_level = self.vista.dim_row
        self.max_col_level  = self.vista.dim_col
        self.row_range = [0, self.vista.row_hdr_idx.count() -1]
        self.col_range = [0, self.vista.col_hdr_idx.count() -1]
        
    @waiting_effects
    def autoCarga(self,my_cubos):
        #FIXME horror con los numeros
        base = my_cubos['default']
        self.setupCubo(my_cubos,base['cubo'])

        self.vista = Vista(self.cubo, int(base['vista']['row']), int(base['vista']['col']),base['vista']['agregado'],base['vista']['elemento'])
        self.vista.format = self.format
        self.defineModel()
        
        
    def changeView(self,row, col, agregado, campo, total=True, estad=True):
        self.vista.setNewView(row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro)
        self.vista.toTree2D()
        self.baseModel.beginResetModel()       
        self.baseModel.datos=self.vista
        self.baseModel.getHeaders()
        self.baseModel.rootItem = self.vista.row_hdr_idx.rootItem
        self.baseModel.endResetModel()
        self.view.expandToDepth(2)
        
    @waiting_effects
    def cargaVista(self,row, col, agregado, campo, total=True, estad=True):
        if self.vista is None:
            self.vista = Vista(self.cubo, row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro)
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
            self.setupCubo(my_cubos,seleccion)
            
        self.setWindowTitle("Cubo "+ seleccion)
       
    def setupCubo(self,my_cubos,seleccion):
        self.cubo = Cubo(my_cubos[seleccion])
        self.cubo.nombre = seleccion #FIXME es que no tengo sitio en Cubo para definirlo
        self.filtro = ''
        self.vista = None
        self.recordStructure = self.summaryGuia()
        
    def requestVista(self):

        parametros = [None for k in range(6)]
       
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
        self.baseModel.beginResetModel()
        self.vista.traspose()
        self.baseModel.getHeaders()
        self.baseModel.rootItem = self.vista.row_hdr_idx.rootItem
        self.baseModel.endResetModel()
        self.view.expandToDepth(2)

        #self.refreshTable()
        #app.restoreOverrideCursor()
        #self.refreshTable()file:///home/werner/projects/dana-cube.git/danacube.pyw


    @waiting_effects
    def restoreData(self):
        #app.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.baseModel.beginResetModel()
        for key in self.baseModel.datos.row_hdr_idx.traverse(mode=1):
            item = self.baseModel.datos.row_hdr_idx[key]
            item.restoreBackup()
            if self.vista.stats :
               item.setStatistics()

        #self.baseModel.rootItem = self.vista.row_hdr_idx.rootItem    
        self.baseModel.endResetModel()
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
               guia = self.baseModel.datos.col_hdr_idx
           else:
               guia = self.baseModel.datos.row_hdr_idx
               
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
              
        for key in self.baseModel.datos.row_hdr_idx.traverse(mode=1):
            item = self.baseModel.datos.row_hdr_idx[key]
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
        self.baseModel.beginResetModel()

        for elem in USER_FUNCTION_LIST[ind][1]:
            self.funDispatch(elem,ind)
            if len(elem) > 2: 
                if elem[2] == 'leaf':
                    self.vista.recalcGrandTotal()
        self.baseModel.endResetModel()
        self.view.expandToDepth(2)

            
    
        
    def refreshTable(self):
        self.baseModel.emitModelReset()
        
    def setFilter(self):
        #self.areFiltered = True
        filterDlg = filterDialog(self.recordStructure,self)
        if filterDlg.exec_():
            #self.loadData(pFilter=filterDlg.result)
            self.filtro=filterDlg.result  #¿ no deberia ponero en self.vista.filtro ?
            self.cargaVista(self.vista.row_id,self.vista.col_id,
                            self.vista.agregado,self.vista.campo,
                            self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui faltan todos los parametros
            self.filterActions['drop'].setEnabled(True)
            self.filterActions['save'].setEnabled(True)


    def dropFilter(self):
        self.filtro = ''
        self.cargaVista(self.vista.row_id,self.vista.col_id,
                        self.vista.agregado,self.vista.campo,
                        self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui     def saveFilter(self):
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)

    
    def saveFilter(self):
        nuevo_filtro = mergeString(self.filtro,self.cubo.definition['base filter'],'AND')
        my_cubos = load_cubo()
        my_cubos[self.cubo.nombre]['base filter'] = nuevo_filtro
        dump_structure(my_cubos)
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)

    
    def summaryGuia(self):
        result = []
        for k,guia in enumerate(self.cubo.lista_guias):
            #self.cubo.fillGuia(k) LLENADO DE GUIA
            dataGuia = []
            for item in traverse(guia['dir_row']):
                dataGuia.append((item.key,item.desc))
            result.append({'name':guia['name'],'format':guia.get('fmt','texto'),
                                'source':guia['elem'] if guia['class'] != 'c' else guia['name'] ,
                                'values':dataGuia,
                                'class':guia['class']}
                                )
        
        confData = self.cubo.definition['connect']
        confName = '$$TEMP'
        (schema,table) = self.cubo.definition['table'].split('.')
        if table == None:
            table = schema
            schema = ''  #definitivamente necesito el esquema de defecto
        iters = 0
        dict = DataDict(conn=confName,schema=schema,table=table,iters=iters,confData=confData) #iters todavia no procesamos
        tabInfo = []
        gotcha = False
        for item in traverseTree(dict.hiddenRoot):
            if item == dict.hiddenRoot:
                continue
            if gotcha:
                if item.isAuxiliar():
                    gotcha = False
                    break
                else:
                    result.append({'name':item.fqn(),'format':item.getColumnData(1),})
            if item.isAuxiliar():
                gotcha = 'True'
        return result
    
if __name__ == '__main__':

    import sys
    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
