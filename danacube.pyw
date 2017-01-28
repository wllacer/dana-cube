#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint


from PyQt5.QtCore import Qt,QSortFilterProxyModel
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView , QTabWidget

from core import Cubo,Vista, mergeString
from dialogs import *
from util.jsonmgr import *
from models import *

from user_functions import *
from util.decorators import *

#from util.tree import traverse
from filterDlg import filterDialog
from dictmgmt.datadict import DataDict
from cubemgmt.cubetree import traverseTree
from datalayer.query_constructor import searchConstructor

from util.mplwidget import SimpleChart

import exportWizard as eW

from util.treestate import *
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


class DanaCubeWindow(QMainWindow):
    def __init__(self):
        super(DanaCubeWindow, self).__init__()
        #
        # movidas aqui por colisiones con checkChanges
        #
        self.filterActions = dict()
        self.dateRangeActions = dict()
        self.restorator = None
        
        self.tabulatura	= QTabWidget()
        self.tabulatura.currentChanged[int].connect(self.checkChanges)

        self.views = list()
        self.selectCube(True)
        
        #CHANGE here. En este caso defino el menu tras los widgets porque si no no compila
        self.cubeMenu = self.menuBar().addMenu("&Cubo")
        self.cubeMenu.addAction("Abrir Cubo ...", self.selectCube, "Ctrl+O")
        self.cubeMenu.addSeparator()
        self.cubeMenu.addAction("Convertir vista actual a defecto", self.defaultVista, "Ctrl+H")

        self.viewMenu = self.menuBar().addMenu("&Vista")
        self.viewMenu.addAction("&Abrir Vista ...",lambda a='new': self.openView(a), "Ctrl+O")
        self.viewMenu.addAction("Cambiar vista actual", lambda a='active': self.openView(a), "Ctrl+H")     
        self.viewMenu.addAction("Cerrar vista actual", self.closeView, "Ctrl+H")     
 
        self.filtersMenu = self.menuBar().addMenu("&Usar Filtros")

        self.filterActions['create'] = self.filtersMenu.addAction('Editar &Filtro',
                                    self.tabulatura.currentWidget().tree.setFilter,
                                    "Ctrl+K")
        self.filterActions['drop'] = self.filtersMenu.addAction('Borrar &Filtros',
                                    self.tabulatura.currentWidget().tree.dropFilter,
                                    "Ctrl+K")
        self.filterActions['save'] = self.cubeMenu.addAction('Guardar &Filtros permanentemente',
                                    self.tabulatura.currentWidget().tree.saveFilter,
                                    "Ctrl+K")
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)
        self.filtersMenu.addSeparator()
        
        self.dateRangeActions['dates'] = self.filtersMenu.addAction('Editar &Rango fechas',
                                    self.tabulatura.currentWidget().tree.setRange,
                                    "Ctrl+K")
        self.dateRangeActions['drop'] = self.filtersMenu.addAction('Borrar &Rango fechas',
                                    self.tabulatura.currentWidget().tree.dropRange,
                                    "Ctrl+K")
        self.dateRangeActions['save'] = self.cubeMenu.addAction('Salvar &Rango fechas',
                                    self.tabulatura.currentWidget().tree.saveRange,
                                    "Ctrl+K")
        self.dateRangeActions['drop'].setEnabled(False)
        self.dateRangeActions['save'].setEnabled(False)
 
        self.optionsMenu = self.menuBar().addMenu("&Opciones")
        self.optionsMenu.addAction("&Exportar datos ...",
                                   self.tabulatura.currentWidget().tree.export,
                                   "CtrlT")
        self.optionsMenu.addAction("&Trasponer datos",
                                   self.tabulatura.currentWidget().tree.traspose,
                                   "CtrlT")
        self.optionsMenu.addAction("&Presentacion ...",
                                   self.tabulatura.currentWidget().tree.setNumberFormat,
                                   "Ctrl+F")
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction("&Graficos",self.tabulatura.currentWidget().setGraph,"Ctrl+G")
        ##
        
        self.userFunctionsMenu = self.menuBar().addMenu("&Funciones de usuario")
        self.restorator = self.userFunctionsMenu.addAction("&Restaurar valores originales"
            ,self.tabulatura.currentWidget().tree.restoreData,"Ctrl+R")
        self.restorator.setEnabled(False)
        self.userFunctionsMenu.addSeparator()
        
        for ind,item in enumerate(USER_FUNCTION_LIST):
             self.userFunctionsMenu.addAction(USER_FUNCTION_LIST[ind][0],
                                              lambda  idx=ind: self.tabulatura.currentWidget().dispatch(idx))        

        
        # esto al final para que las distintas opciones raras que van al menu de cubos vayan en su sitio
        self.cubeMenu.addSeparator()
        self.cubeMenu.addAction("E&xit", self.close, "Ctrl+Q")


        self.setCentralWidget(self.tabulatura)
      
    def checkChanges(self,destino):
        currentWidget = self.tabulatura.currentWidget()   #.tree
        if not self.filterActions or not self.dateRangeActions or not self.restorator:
            return
        if not currentWidget:
            self.filterActions['drop'].setEnabled(False)
            self.filterActions['save'].setEnabled(False)
            self.restorator.setEnabled(False)
            return 
        
        if currentWidget.tree.filtroCampos != '':
            self.filterActions['drop'].setEnabled(True)
            self.filterActions['save'].setEnabled(True)
        else:
            self.filterActions['drop'].setEnabled(False)
            self.filterActions['save'].setEnabled(False)
            

        if currentWidget.tree.filtroFechas != '':
            self.dateRangeActions['drop'].setEnabled(True)
            self.dateRangeActions['save'].setEnabled(True)
        else:
            self.dateRangeActions['drop'].setEnabled(False)
            self.dateRangeActions['save'].setEnabled(False)

        if currentWidget.tree.isModified:
            self.restorator.setEnabled(True)
        else:
            self.restorator.setEnabled(False)

    def selectCube(self,inicial=False):
        #FIXME casi funciona ... vuelve a leer el fichero cada vez. NO es especialmente malo
        my_cubos = load_cubo()
        viewData =dict()
        defaultViewData = None
        if 'default' in my_cubos and inicial:
            defaultViewData = my_cubos['default']
            self.cubeName=defaultViewData['cubo']
            viewData['row'] = int(defaultViewData['vista']['row'])
            viewData['col'] = int(defaultViewData['vista']['col'])
            viewData['agregado'] = defaultViewData['vista']['agregado']
            viewData['campo'] = defaultViewData['vista']['elemento']
            viewData['totalizado'] = True
            viewData['stats'] = True
            #del my_cubos['default']
        else:
            dialog = CuboDlg(my_cubos, self)
            if dialog.exec_():
                self.cubeName = str(dialog.cuboCB.currentText())
            elif inicial:
                exit()
            else:
                return None
        self.setupCubo(my_cubos,self.cubeName)
        if not inicial:
            self.reinitialize()
            return None
            pass #crea primer tab con los datos de la ventana
        else:
            self.addView(**viewData)
            
    def reinitialize(self):
        for k in range(len(self.views)):
            self.tabulatura.removeTab(self.tabulatura.indexOf(self.views[k]))
            self.views[k].close()
        del self.views[:]
        self.addView()

        
    def setupCubo(self,my_cubos,seleccion):
        self.cubo = Cubo(my_cubos[seleccion])
        self.cubo.nombre = seleccion #FIXME es que no tengo sitio en Cubo para definirlo
        self.cubo.recordStructure = self.summaryGuia()
        self.setWindowTitle(self.cubo.nombre)
    
    @waiting_effects
    def summaryGuia(self):
        result = []
        #self.cubo.fillGuias()
        for k,guia in enumerate(self.cubo.lista_guias):
            arbolGuia = self.cubo.fillGuia(k)
            dataGuia = []
            for item in arbolGuia.traverse(mode=1,output=1):
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

    def defaultVista(self):
        entrada = self.tabulatura.currentWidget().tree
        datos_defecto = {}
        datos_defecto["cubo"] =  self.cubo.nombre
        datos_defecto["vista"] = {
            "elemento": entrada.vista.campo,
            "agregado": entrada.vista.agregado,
            "row": entrada.vista.row_id,
            "col": entrada.vista.col_id
            }
        if entrada.filtroCampos != '':  #NO los rangos de fecha que son por naturaleza variables
            datos_defecto["vista"]["filter"] = entrada.filtroCampos
        my_cubos = load_cubo()
        my_cubos['default'] = datos_defecto
        dump_structure(my_cubos)
        
        
    def requestVista(self,vista=None):
        parametros = [None for k in range(6)]
        viewData = dict()
        if vista is not  None:
            parametros[0]=vista.row_id
            parametros[1]=vista.col_id
            parametros[2]=self.cubo.getFunctions().index(vista.agregado)
            parametros[3]=self.cubo.getFields().index(vista.campo)
            parametros[4]=vista.totalizado
            parametros[5]=vista.stats
        
        vistaDlg = VistaDlg(self.cubo,parametros, self)
            
        if vistaDlg.exec_():
            viewData['row'] = parametros[0]
            viewData['col'] = parametros[1]
            viewData['agregado'] = self.cubo.getFunctions()[parametros[2]]
            #campo = self.cubo.getFunctions()[parametros[1]]
            viewData['campo'] = vistaDlg.sheet.cellWidget(3,0).currentText() #otra manera de localizar
            viewData['totalizado'] = parametros[4]
            viewData['stats'] = parametros[5]
        
        return viewData

    def addView(self,**viewData):
        if viewData:  #¿Es realmente necesario ?
            self.views.append(TabMgr(self,**viewData))
        else:
            self.views.append(TabMgr(self))
        idx = self.tabulatura.addTab(self.views[-1],self.views[-1].getTitleText())
        self.tabulatura.setCurrentIndex(idx)

    
    def closeView(self):
        tabId = self.tabulatura.currentIndex()
        self.tabulatura.removeTab(tabId)
        self.views[tabId].close()
        del self.views[tabId]

    def openView(self,action):
        currentWgt = self.tabulatura.currentWidget()
        viewData = self.requestVista(currentWgt.tree.vista if currentWgt else None)
        if not viewData:
            return
        if action == 'new':
            self.addView(**viewData)
        elif action == 'active':
            currentWgt.tree.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], total=viewData['totalizado'], estad=viewData['stats'])
        else:
            return
        
class TabMgr(QWidget):
    def __init__(self,parent,**kwargs):
        super(TabMgr,self).__init__()
        lay = QGridLayout()
        self.setLayout(lay)
        self.tree = DanaCube(parent,**kwargs)
        self.chart = SimpleChart()
        self.chartType = None #'barh'
        self.lastItemUsed = None
        self.tree.clicked.connect(self.drawChart)
        
        lay.addWidget(self.tree,0,0,1,1)
        lay.addWidget(self.chart,0,1,1,4)

        self.drawChart(None)
    
    def setGraph(self):
        dialog = GraphDlg(self.chartType, self)
        if dialog.exec_():
            self.chartType = dialog.result
        self.drawChart()
    
    def getTitleText(self):
        return self.tree.getTitleText()
    
    def dispatch(self,FcnIdx):
        self.tree.dispatch(FcnIdx)
        self.drawChart()
        
    def drawChart(self,index=None):
        if self.chartType:
            self.processChartItem(index,tipo=self.chartType)
        else:
            self.chart.hide()
    
    def processChartItem(self,index=None,tipo='bar'):
        if index:
            if index.isValid():
                item = self.tree.baseModel.item(index)
            else:
                return
        elif self.lastItemUsed:
            item = self.lastItemUsed
        else:
            item = self.tree.baseModel.item('//')
        self.lastItemUsed = item
        #textos_col = ytree.getHeader('col')
        #textos_row = xtree.getHeader('row')
        #line = 0
        #col  = 0
        titulo = self.tree.baseModel.datos.row_hdr_idx.name+'> '+item.getFullDesc()[-1] +  '\n' + \
            '{}({})'.format(self.tree.baseModel.datos.agregado,self.tree.baseModel.datos.campo) 
        x_text = self.tree.baseModel.datos.col_hdr_idx.name
        y_text = ''
        
        if tipo == 'multibar': 
            datos,kcabeceras = item.simplifyHierarchical() #msimplify(mdatos,self.textos_col)
        else:
            datos,kcabeceras = item.simplify() #item.getPayload(),self.textos_col)
        cabeceras = [ self.tree.baseModel.colHdr[k] for k in kcabeceras ]

        if len(datos) == 0:
            self.chart.axes.cla()
        else:
            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,item.getFullDesc())  
        self.chart.draw()
        self.chart.show()
        
class DanaCube(QTreeView):    
    def __init__(self,parent,**kwargs):
        super(DanaCube, self).__init__()
        
        self.format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)

        self.vista = None
        self.baseModel = None
        self.parent= parent  #la aplicacion en la que esta. Lo necesito para los cambios de título
        self.cubo =  self.parent.cubo
        self.setupFilters()
        #self.filtro = ''
        #self.filtroCampos = ''
        #self.filtroFechas = ''

        self.view = self #esto es un por si acaso
        #
        self.initData(True,**kwargs)
        #self.defineModel()            
        #self = QTreeView(self)
        #self.setModel(modeloActivo)
        
        self.expandToDepth(2)
        self.setSortingEnabled(True)
        #self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.AscendingOrder)



        
    def initData(self,inicial=False,**viewData):
        #FIXME casi funciona ... vuelve a leer el fichero cada vez. NO es especialmente malo
        #my_cubos = load_cubo()
        #viewData =dict()
        #defaultViewData = None
        #if 'default' in my_cubos and inicial:
            #defaultViewData = my_cubos['default']
            #self.cubo.nombre=defaultViewData['cubo']
            #viewData['row'] = int(defaultViewData['vista']['row'])
            #viewData['col'] = int(defaultViewData['vista']['col'])
            #viewData['agregado'] = defaultViewData['vista']['agregado']
            #viewData['campo'] = defaultViewData['vista']['elemento']
            #viewData['totalizado'] = True
            #viewData['stats'] = True
            ##del my_cubos['default']
        #else:
            #dialog = CuboDlg(my_cubos, self)
            #if dialog.exec_():
                #self.cubo.nombre = str(dialog.cuboCB.currentText())
            #elif inicial:
                #exit()
            #else:
                #return
        #self.setupFilters(my_cubos,self.cubo.nombre)
        if viewData:
            pass
        else:
            viewData = self.parent.requestVista()
        #if not viewData:
        self.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], total=viewData['totalizado'], estad=viewData['stats'])
        
        #self.setTitle() debe hacerse fuera para evitar colocarlo en el sitio equivocado
        
        self.setModel(self.defineModel())

    def getTitleText(self):
        return "{} X {} : {}({})".format(
                    self.vista.row_hdr_idx.name.split('.')[-1],
                    self.vista.col_hdr_idx.name.split('.')[-1],
                    self.vista.agregado,
                    self.vista.campo.split('.')[-1]
                    )
    def setTitle(self):
        tabId = self.parent.tabulatura.currentIndex()
        self.parent.tabulatura.setTabText(tabId,self.getTitleText())
            
    def setupFilters(self): #,my_cubos,seleccion):
        #self.cubo = Cubo(my_cubos[seleccion])
        #self.cubo.nombre = seleccion #FIXME es que no tengo sitio en Cubo para definirlo
        self.filtro = ''
        self.filtroCampos = ''
        self.filtroFechas = ''
        #self.vista = None
        self.filterValues = None
        self.isModified = False
        #self.cubo.recordStructure = self.summaryGuia()

            #self.cargaVista(row,col,agregado,campo,totalizado,stats)

    @waiting_effects
    def cargaVista(self,row, col, agregado, campo, total=True, estad=True):
        if self.vista is None:
            self.vista = Vista(self.cubo, row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro)
            self.vista.toTree2D()
            self.expandToDepth(2)
        else:
            self.changeView(row, col, agregado, campo, total,estad)
            #self.refreshTable()
        self.vista.format = self.format
     
    @waiting_effects
    def changeView(self,row, col, agregado, campo, total=True, estad=True):
        self.vista.setNewView(row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro)
        self.vista.toTree2D()
        #
        self.setModel(self.defineModel())  #esto no deberia ser asi, sino dinámico, pero no lo he conseguido
        self.expandToDepth(2)
        
        self.setTitle()
        
    def defineModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO NO he conseguido hacerlo dinamicamente
        """
        newModel = TreeModel(self.vista, self)
        newModel.hiddenRoot = self.vista.row_hdr_idx.rootItem
        #newModel.setContext(format=self.format) #nueva version
        #self.setModel(newModel)
        #self.modelo=self.model
        proxyModel = QSortFilterProxyModel()
        proxyModel.setSourceModel(newModel)
        proxyModel.setSortRole(33)
        #self.setModel(proxyModel)
        self.baseModel = newModel #proxyModel
        #self.expandToDepth(2)
        # estas vueltas para permitir ordenacion
        # para que aparezcan colapsados los indices jerarquicos
        self.max_row_level = self.vista.dim_row
        self.max_col_level  = self.vista.dim_col
        self.row_range = [0, self.vista.row_hdr_idx.len() -1]
        self.col_range = [0, self.vista.col_hdr_idx.len() -1]
        return proxyModel
    
        
    def changeVista(self):
        viewData = self.requestVista()
        if not viewData:
            return
        self.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], total=viewData['totalizado'], estad=viewData['stats'])
        
        self.setTitle()
        
    @waiting_effects
    @model_change_control()
    def traspose(self):
        #self.baseModel.beginResetModel()
        self.vista.traspose()
        self.baseModel.getHeaders()
        self.baseModel.rootItem = self.vista.row_hdr_idx.rootItem
        #self.baseModel.endResetModel()
        self.expandToDepth(2)

        self.setTitle()

    def refreshTable(self):
        """
            La eleccion de una u otra señal no es casualidad.
            Si utilizo layoutChanged el dialogo setNumberFormat cruje inmisericordemente al cerrar si no se le define el WA_DeleteOnClose !!!!???
        """
        self.baseModel.emitModelReset()
        #self.baseModel.layoutChanged.emit()
        
     
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """
        self.numberFormatDlg = NumberFormatDlg(self.format, self.refreshTable, self)
        #self.numberFormatDlg.setAttribute(Qt.WA_DeleteOnClose) #si no cruje inmisericordemente ¿ o no?
        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()
        #self.refreshTable()  #creo que es innecesario
    
    @keep_tree_layout()
    @waiting_effects
    @model_change_control()
    def restoreData(self):
        #app.setOverrideCursor(QCursor(Qt.WaitCursor))
        #expList = saveExpandedState(self)
        #self.baseModel.beginResetModel()
        for item in self.baseModel.traverse(mode=1,output=1):
            item.restoreBackup()
            if self.vista.stats :
               item.setStatistics()

        #self.baseModel.rootItem = self.vista.row_hdr_idx.rootItem    
        #self.baseModel.endResetModel()
        #restoreExpandedState(expList,self)
        #self.expandToDepth(2)
        #app.restoreOverrideCursor()
        self.isModified = False
        self.parent.restorator.setEnabled(False)

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
              
        for item in self.baseModel.traverse(mode=1,output=1):
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
               
    @keep_tree_layout()         
    @waiting_effects
    @model_change_control()
    def dispatch(self,ind):
        #TODO reducir el numero de arrays temporales
        #self.baseModel.beginResetModel()
        for elem in USER_FUNCTION_LIST[ind][1]:
            self.funDispatch(elem,ind)
            if len(elem) > 2: 
                if elem[2] == 'leaf':
                    self.vista.recalcGrandTotal()
        #self.baseModel.endResetModel()
        self.isModified = True
        self.parent.restorator.setEnabled(True)
        #self.expandToDepth(2)

        
    def setFilter(self):
        #self.areFiltered = True
        #self.cubo.recordStructure = self.summaryGuia()
        
        filterDlg = filterDialog(self.cubo.recordStructure,self)
        if self.filterValues :
            for k in range(len(self.filterValues)):
                filterDlg.sheet.set(k,2,self.filterValues[k][0])
                filterDlg.sheet.set(k,3,self.filterValues[k][1])
                
        if filterDlg.exec_():
            #self.loadData(pFilter=filterDlg.result)
            self.filtroCampos=filterDlg.result
            self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
            self.filterValues = [ (data[2],data[3],) for data in filterDlg.data]
            self.cargaVista(self.vista.row_id,self.vista.col_id,
                            self.vista.agregado,self.vista.campo,
                            self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui faltan todos los parametros
            self.parent.filterActions['drop'].setEnabled(True)
            self.parent.filterActions['save'].setEnabled(True)


    def dropFilter(self):
        self.filtroCampos=''
        self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
        self.filterValues = None
        self.cargaVista(self.vista.row_id,self.vista.col_id,
                        self.vista.agregado,self.vista.campo,
                        self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui     def saveFilter(self):
        self.parent.filterActions['drop'].setEnabled(False)
        self.parent.filterActions['save'].setEnabled(False)

    
    def saveFilter(self):
        nuevo_filtro = mergeString(self.filtroCampos,self.cubo.definition['base filter'],'AND')
        my_cubos = load_cubo()
        my_cubos[self.cubo.nombre]['base filter'] = nuevo_filtro
        dump_structure(my_cubos)
        self.parent.filterActions['drop'].setEnabled(False)
        self.parent.filterActions['save'].setEnabled(False)

        
    def setRange(self):
        descriptores = [ item['name'] for item in self.cubo.recordStructure if item['format'] == 'fecha' ]
        if len(descriptores) == 0:
            #TODO que hago con Sqlite
            return
        form = dateFilterDlg(descriptores)
        if form.exec_():
            sqlGrp = []
            for entry in form.result:
                if entry[1] != 0:
                    intervalo = dateRange(entry[1],entry[2],periodo=entry[3])
                    sqlGrp.append((entry[0],'BETWEEN',intervalo))
            if len(sqlGrp) > 0:
                self.filtroFechas = searchConstructor('where',{'where':sqlGrp})
                self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
                self.cargaVista(self.vista.row_id,self.vista.col_id,
                            self.vista.agregado,self.vista.campo,
                            self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui faltan todos los parametros

                self.parent.dateRangeActions['drop'].setEnabled(False)
                #self.parent.dateRangeActions['save'].setEnabled(False)
            
    def dropRange(self):
        self.filtroFechas=''
        self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
        self.cargaVista(self.vista.row_id,self.vista.col_id,
                        self.vista.agregado,self.vista.campo,
                        self.vista.totalizado,self.vista.stats) #__WIP__ evidentemente aqui     def saveFilter(self):
        self.parent.dateRangeActions['drop'].setEnabled(False)
        #self.parent.dateRangeActions['save'].setEnabled(False)

    def saveRange(self):
        pass
    
    
    def export(self):
        #TODO 
        #rowHidden = [ None  for k in range (self.baseModel.count()) ]
        #def getHiddenRows(baseElem,rowHidden):
            #for k,item in enumerate(baseElem.childItems) :                
        #getHiddenRows(self.baseModel.rootItem,rowHidden)
        #print(rowHidden)
        parms = eW.exportWizard()
        selArea = dict()
        #TEMPORAL init
        #if parms['scope']['visible']:
            ## probar con self.isColumnHidden(x)
            #selArea['hiddenColumn'] = [ self.header().isSectionHidden(k) for k in range(self.header().count())]
            ## is self.isRowHidden(x,parent)
            #selArea['hiddenRow'] = []
            #del selArea['hiddenColumn'][0] #no me interesa el estado de los titulos
        #TEMPORAL end
        if not parms.get('file'):
            return
        resultado = self.vista.export(parms,selArea)

    def openHeaderContextMenu(self,position):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        menu = QMenu()
        self.ctxMenuHdr = []
        self.ctxMenuHdr.append(menu.addAction("Ocultar Columna",lambda :self.execHeaderAction("hide",position)))
        columna=self.header().logicalIndexAt(position)
        if self.header().isSectionHidden(columna -1):
            self.ctxMenuHdr.append(menu.addAction("Mostrar Columna oculta",lambda :self.execHeaderAction("unhide",position)))
        self.ctxMenuHdr.append(menu.addAction("Gráfico de la columna",lambda :self.execHeaderAction("graph",position)))
        #self.ctxMenu.append(menu.addAction("Exportar seleccion",lambda :self.execAction("export",position)))
        action = menu.exec_(self.viewport().mapToGlobal(position))
    
    def execHeaderAction(self,function,position):
        columna=self.header().logicalIndexAt(position)
        if function == 'hide':
                self.setColumnHidden(columna,True)
        elif function == 'unhide':
            ## eso me interesa para otras cosas
            #for k in range(self.header().count()):
                #print(columna,k,self.header().isSectionHidden(k))
            #if self.header().isSectionHidden(columna -1):
            self.setColumnHidden(columna -1,False)
        elif function == 'graph':
            self.drawGraph('col',columna)

    def openContextMenu(self,position):
        menu = QMenu()
        self.ctxMenu = []
        self.ctxMenu.append(menu.addAction("Gráfico de la fila",lambda :self.execAction("graph",position)))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def execAction(self,function,position):
        print(position)
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            self.drawGraph('row',index)
        
    def drawGraph(self,source,id):
        if source == 'row':
            item = self.baseModel.item(id)
            titulo = item['key']
            datos = item.getPayload()
            etiquetas = self.baseModel.colHdr[1:]
        elif source == 'col':
            titulo = self.baseModel.colHdr[id]
            datos = []
            for key in self.vista.row_hdr_idx.traverse(mode=1):
                datos.append(self.vista.row_hdr_idx[key].gpi(id -1))
            etiquetas = self.baseModel.rowHdr[1:]
        print(source,titulo,datos,etiquetas)
        
if __name__ == '__main__':
    import sys
    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    app = QApplication(sys.argv)
    window = DanaCubeWindow()
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
