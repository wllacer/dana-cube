#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Nueva versiion. TodoList para volcar
         FIXED
            restore valores originales 
         TESTED Cubo
            Abrir Cubo 
            Convertir vista actual a defecto
         TESTED Vista
            Abrir Vista
            Cambiar vista actual
            Cerrar vista actual
         TESTED Usar Filtros
            Editar &Filtro
            Borrar &Filtros
            Guardar &Filtros permanentemente
         TESTED Rangos de Fechas
            Editar &Rango fechas
            Borrar &Rango fechas
            Salvar &Rango fechas
         Opciones
            DONE (as tested) Exportar datos
            DONE Trasponer datos
            DONE Presentacion ...
            
         TESTED Graficos
            SOLVED multibar
            SOLVED llamada inicial

         TESTED Funciones de usuario
            TESTED funcion de merge
            TESTED Simulaciones
         TESTED Restaurar valores originales   
         
        TESTED menus de contexto de cabeceras
         
        TESTED recalcGrandTotal
        revisar recalcGrandTotal sin gran total
        DONE revisar estadisticas
            look as if they have disappeared
        TESTED revisar restaurar valores originales c
        TESTED activar sort
        BUG .
            Un problema con valores '' en la clave, pero no en el valor. No aparecen en el mismo lugar y "joden" el traspose.  
            En datos light la entrada de C.A. con valor '' España aparece en distintos lugares en el traverse. 
        TODO
            investigar el uso de locales (Python o Qt) en lugar/ademas de numberFormat)
            sort por otros criterios o sin problemas con acentos
            mejorar los graficos de cabecera de columna con criterios de seleccion
            revisar estadisticas cuando hay muchos 1 (ver diputados por provincia)
        NO reproduzco
            File "/home/werner/projects/dana-cube.git/util/tree.py", line 614, in data
            text, sign = fmtNumber(datos,self.datos.format)
            File "/home/werner/projects/dana-cube.git/util/numeros.py", line 64, in fmtNumber
                cadena = formatter.format(number)
            ValueError: Cannot specify ',' or '_' with 's'.
        NO reproduzco
            El error es previo; debia estar resuelto, se suponia
            sqlalchemy.exc.ProgrammingError: (psycopg2.ProgrammingError) constante no entera en GROUP BY
                LÍNEA 1: ...ntal.inventory_id)  FROM public.rental   GROUP BY '//', staf...
        
    [SQL: " SELECT  '//', staff_id, sum(public.rental.inventory_id)  FROM public.rental   GROUP BY '//', staff_id ORDER BY 1 , 2  "]
    
        DONE __COSMETIC__
            fechas no acaban de salir bien (ver datos light)
        DONE
            Cabeceras de las pestañas es siempre la misma
        TODO
            context menu con los datos estadisticos en la linea

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from PyQt5.QtCore import Qt #,QSortFilterProxyModel
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView , QTabWidget, QSplitter, QAbstractItemView

from base.core import Cubo,Vista 
from support.gui.dialogs import *
from support.util.jsonmgr import *
from support.util.cadenas import * #mergeString
from support.util.numeros import s2n
        
from support.util.decorators import *

#from base.tree import traverse
from base.filterDlg import filterDialog
from base.datadict import DataDict
from base.cubetree import traverseTree
from support.datalayer.query_constructor import searchConstructor

from support.util.mplwidget import SimpleChart
from support.util.uf_manager import *

import base.exportWizard as eW

from support.util.treestate import *
from base.tree import GuideItem,_getHeadColumn
import base.config as config

from base.ufhandler import Uf_handler
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

def generaArgParser():
    parser = argparse.ArgumentParser(description='Cubo de datos')
    parser.add_argument('--cubeFile','--cubefile','-c',
                        nargs='?',
                        default='cubo.json',
                        help='Nombre del fichero de configuración del cubo actual')    
    parser.add_argument('--contextFile','--contextfile','--context','-xf',
                        nargs='?',
                        default='danacube.json',
                        help='Nombre del fichero de contexto de danacube')    
    security_parser = parser.add_mutually_exclusive_group(required=False)
    security_parser.add_argument('--secure','-s',dest='secure', action='store_true',
                                 help='Solicita la clave de las conexiones de B.D.')
    security_parser.add_argument('--no-secure','-ns', dest='secure', action='store_false')
    parser.set_defaults(secure=False)

    return parser

class DanaCubeWindow(QMainWindow):
    def __init__(self,args):
        super(DanaCubeWindow, self).__init__()
        #
        # movidas aqui por colisiones con checkChanges
        #

        self.cubeFile = args.cubeFile
        self.secure = args.secure
        self.contextFile = args.contextFile
        
        self.filterActions = dict()
        self.dateRangeActions = dict()
        self.editActions = dict()
        
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
                                    self.setFilter,
                                    "Ctrl+K")
        self.filterActions['drop'] = self.filtersMenu.addAction('Borrar &Filtros',
                                    self.dropFilter,
                                    "Ctrl+K")
        self.filterActions['save'] = self.cubeMenu.addAction('Guardar &Filtros permanentemente',
                                    self.saveFilter,
                                    "Ctrl+K")
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)
        self.filtersMenu.addSeparator()

        
        self.dateRangeActions['dates'] = self.filtersMenu.addAction('Editar &Rango fechas',
                                    self.setRange,
                                    "Ctrl+K")
        self.dateRangeActions['drop'] = self.filtersMenu.addAction('Borrar &Rango fechas',
                                    self.dropRange,
                                    "Ctrl+K")
        self.dateRangeActions['save'] = self.cubeMenu.addAction('Salvar &Rango fechas',
                                    self.saveRange,
                                    "Ctrl+K")
        self.dateRangeActions['drop'].setEnabled(False)
        self.dateRangeActions['save'].setEnabled(False)

        self.optionsMenu = self.menuBar().addMenu("&Opciones")
        self.optionsMenu.addAction("&Exportar datos ...",
                                   self.exportData,
                                   "CtrlT")
        self.optionsMenu.addAction("&Trasponer datos",
                                   self.trasposeData,
                                   "CtrlT")
        self.optionsMenu.addAction("&Presentacion ...",
                                   self.setNumberFormat,
                                   "Ctrl+F")
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction("&Graficos",self.setGraph,"Ctrl+G")

        # esta es la version nueva del menu funcional
        
        self.userFunctionsMenu = self.menuBar().addMenu("&Funciones de usuario")
        self.restorator = self.userFunctionsMenu.addAction("&Restaurar valores originales"
            ,self.tabulatura.currentWidget().tree.restoreData,"Ctrl+R")
        self.restorator.setEnabled(False)

        self.userFunctionsMenu.addSeparator()
        self.editActions['active'] = self.userFunctionsMenu.addAction("&Activar edicion celdas"
            ,self.tabulatura.currentWidget().tree.activateEdit,"Ctrl+R")
        self.editActions['active'].setEnabled(True)
        self.editActions['inactive'] = self.userFunctionsMenu.addAction("&Desactivar edicion celdas"
            ,self.tabulatura.currentWidget().tree.deactivateEdit,"Ctrl+R")
        self.editActions['inactive'].setEnabled(False)
        
        self.userFunctionsMenu.addSeparator()
        
        self.ufHandler = Uf_handler(self.userFunctionsMenu,self.cubo,self.dispatch,self.contextFile)
        self.plugins = self.ufHandler.plugins
        self.pluginDbMenu = self.ufHandler.specUfMenu
        ## esto al final para que las distintas opciones raras que van al menu de cubos vayan en su sitio
        self.cubeMenu.addSeparator()
        self.cubeMenu.addAction("E&xit", self.close, "Ctrl+Q")


        self.setCentralWidget(self.tabulatura)
     
    def fillUserFunctionMenu(self,menu,db=''):
        self.ufHandler.fillUserFunctionMenu(db)
    #def fillUserFunctionMenu(self,menu,db=''):
        #if db != '':
            #menu.clear()
            #menu.setTitle('Funciones especificas para '+ db)
            #subset = { k:self.plugins[k] for k in self.plugins if db in self.plugins[k].get('db','') }
        #else:
            #subset = { k:self.plugins[k] for k in self.plugins if self.plugins[k].get('db','') == '' }
        #if len(subset) == 0:
            #return
        #for k in sorted(subset,
                    #key=lambda x:self.plugins[x].get('seqnr', float('inf'))):
            #entry = self.plugins[k]
            #if entry.get('hidden',False):
                #continue
            #menu.addAction(entry['text'],lambda  idx=k: self.dispatch(idx))
            #if entry.get('sep',False):
                #menu.addSeparator()
        
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

        #print(currentWidget.tree.editTriggers().text(),self.editActions['active'].text())
        if currentWidget.tree.editTriggers() == QAbstractItemView.NoEditTriggers:
            self.editActions['active'].setEnabled(True)
            self.editActions['inactive'].setEnabled(False)
        else:
            self.editActions['active'].setEnabled(False)
            self.editActions['inactive'].setEnabled(True)
            
    def selectCube(self,inicial=False):
        #FIXME casi funciona ... vuelve a leer el fichero cada vez. NO es especialmente malo
        my_cubos = load_cubo(self.cubeFile)
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
        if not inicial:
            self.cubo.db.close()
        self.setupCubo(my_cubos,self.cubeName)
        if not inicial:
            self.reinitialize()
            self.fillUserFunctionMenu(self.pluginDbMenu,self.cubo.nombre)
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
        #ALPHA aqui es donde debo implementar el login seguro
        #
        if self.secure and my_cubos[seleccion]['connect']['driver'] not in ('sqlite','QSQLITE'):
            self.editConnection(my_cubos[seleccion],seleccion)
        self.cubo = Cubo(my_cubos[seleccion])
        self.cubo.nombre = seleccion #FIXME es que no tengo sitio en Cubo para definirlo
        self.cubo.recordStructure = self.getCubeRecordInfo()
        self.setWindowTitle(self.cubo.nombre)

        
    @waiting_effects
    def getCubeRecordInfo(self):
        """
           Determinamos con el la estructura del registro que el cubo analiza.
           TODO Probablemente deberia estar mejor en Core
        """
        result = []
        confData = self.cubo.definition['connect']
        confName = '$$TEMP'
        (schema,table) = self.cubo.definition['table'].split('.')
        if table == None:
            table = schema
            schema = ''  #definitivamente necesito el esquema de defecto
        iters = 0
        # dict = DataDict(conName=confName,schema=schema,table=table,iters=iters,confData=confData) #iters todavia no
        dict = DataDict(conn=self.cubo.db,schema=schema,table=table,iters=iters) #,confData=confData) #iters todavia noprocesamos
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
        my_cubos = load_cubo(self.cubeFile)
        my_cubos['default'] = datos_defecto
        dump_structure(my_cubos,self.cubeFile)
        
        
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
            viewData = self.requestVista()
            if not viewData:
                return
            self.views.append(TabMgr(self,**viewData))
            
        titulo = self.views[-1].getTitleText()
        idx = self.tabulatura.addTab(self.views[-1],titulo)
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

    def setFilter(self):
        self.tabulatura.currentWidget().tree.setFilter()
    def dropFilter(self):
        self.tabulatura.currentWidget().tree.dropFilter()
    def saveFilter(self):
        self.tabulatura.currentWidget().tree.saveFilter()

    def setRange(self):
        self.tabulatura.currentWidget().tree.setRange()
    def dropRange(self):
        self.tabulatura.currentWidget().tree.dropRange()
    def saveRange(self):
        self.tabulatura.currentWidget().tree.saveRange()

    def exportData(self):
        self.tabulatura.currentWidget().tree.export()
    def trasposeData(self):
        self.tabulatura.currentWidget().tree.traspose()
    def setNumberFormat(self):
        self.tabulatura.currentWidget().tree.setNumberFormat()
    def setGraph(self):
        self.tabulatura.currentWidget().setGraph()
       
    def dispatch(self,FcnName):
        self.tabulatura.currentWidget().dispatch(FcnName)
        
    def editConnection(self,configData,nombre=None):         
        from support.util.record_functions import dict2row, row2dict
        from support.datalayer.conn_dialogs import ConnectionSheetDlg
        
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        if nombre is None:
            datos = [None for k in range(len(attr_list) +1) ]
        else:
            datos = [nombre, ] + dict2row(configData['connect'],attr_list)
        #contexto
        context = (
                ('Nombre',
                    QLineEdit,
                    {'setReadOnly':True,'setStyleSheet':"background-color: rgb(211, 211, 211);"},
                    None,
                ),
                # driver
                ("Driver ",
                    QLineEdit,
                    {'setReadOnly':True,'setStyleSheet':"background-color: rgb(211, 211, 211);"},
                    None,
                ),
                ("DataBase Name",
                    QLineEdit,
                    None,
                    None,
                ),
                ("Host",
                    QLineEdit,
                    None,
                    None,
                ),
                ("User",
                    QLineEdit,
                    None,
                    None,
                ),
                ("Password",
                    QLineEdit,
                    {'setEchoMode':QLineEdit.Password},
                    None,
                ),
                ("Port",
                    QLineEdit,
                    None,
                    None,
                ),
                ("Debug",
                    QCheckBox,
                    None,
                    None,
                )
                
                )
        parmDialog = ConnectionSheetDlg('Edite la conexion',context,datos, self)
        if parmDialog.exec_():
            #TODO deberia verificar que se han cambiado los datos
            configData['connect'] = row2dict(datos[1:],attr_list)
            return datos[0]
     

class TabMgr(QWidget):
    def __init__(self,parent,**kwargs):
        super(TabMgr,self).__init__()
        split = QSplitter(Qt.Vertical,self)
        lay = QGridLayout()
        self.setLayout(lay)
        self.tree = DanaCube(parent,**kwargs)
        if self.tree.vista is None:
            return 
        self.chart = SimpleChart()
        self.chartType = None #'barh'
        self.lastItemUsed = None
        self.tree.clicked.connect(self.drawChart)
        
        split.addWidget(self.tree)
        split.addWidget(self.chart)
        
        lay.addWidget(split,0,0)

        self.drawChart(None)
    
    def setGraph(self):
        dialog = GraphDlg(self.chartType, self)
        if dialog.exec_():
            self.chartType = dialog.result
        self.drawChart()
    
    def getTitleText(self):
        return self.tree.getTitleText()
    
    def dispatch(self,FcnName):
        self.tree.dispatch(FcnName)
        self.drawChart()

    def drawChart(self,index=None):
        if self.chartType:
            self.processChartItem(index,tipo=self.chartType)
        else:
            self.chart.hide()
    
    def processChartItem(self,index=None,tipo='bar'):
        if index:
            if index.isValid():
                item = self.tree.model().itemFromIndex(index)
                #esta vuelta es para localizar el nombre de la fila y evitar que los valores nulos, que son QStandardItem peten el proceso
                if index.column() != 0:
                    rowid = self.tree.model().itemFromIndex(index.sibling(index.row(),0))
                else:
                    rowid = item
            else:
                return
        elif len(self.tree.selectedIndexes()) > 0:
            indice = self.tree.selectedIndexes()[0]
            item = self.tree.model().itemFromIndex(indice)
            if item.column() != 0:
                rowid = self.tree.model().itemFromIndex(indice.sibling(indice.row(),0))
            else:
                rowid = item
        elif self.lastItemUsed is not None:
            item = self.lastItemUsed
            rowid = item
        else:
            item = self.tree.model().invisibleRootItem().child(0)
            rowid = item
        self.lastItemUsed = item
        #textos_col = ytree.getHeader('col')
        #textos_row = xtree.getHeader('row')
        #line = 0
        #col  = 0
        x_text = self.tree.vista.col_hdr_idx.name
        y_text = ''
        titleParms = {}
        if tipo == 'multibar': 
            datos,kcabeceras = rowid.simplifyHierarchical() #msimplify(mdatos,self.textos_col)
            titleParms = {'format':'string', 'delimiter':' > '}
        else:
            datos,kcabeceras = rowid.simplify() #item.getPayload(),self.textos_col)

            
        titulo = self.tree.vista.row_hdr_idx.name+'> '+rowid.getFullHeadInfo(**titleParms) +  '\n' + \
                '{}({})'.format(self.tree.vista.agregado,self.tree.vista.campo) 
            
        cabeceras = [ self.tree.colHdr[k] for k in kcabeceras ] 

        if len(datos) == 0:
            self.chart.axes.cla()
        else:
            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,rowid.getFullDesc())  
        self.chart.draw()
        self.chart.show()
        
class DanaCube(QTreeView):    
    def __init__(self,parent,**kwargs):
        super(DanaCube, self).__init__()        
        #self.format = dict(thousandsseparator=".",
                                    #decimalmarker=",",
                                    #decimalplaces=2,
                                    #rednegatives=False,
                                    #yellowoutliers=True)

        self.vista = None
        self.parent= parent  #la aplicacion en la que esta. Lo necesito para los cambios de título
        self.cubo =  self.parent.cubo
        self.colHdr = None
        self.setupFilters()
        #self.filtro = ''
        #self.filtroCampos = ''
        #self.filtroFechas = ''

        self.view = self #esto es un por si acaso
        #
        if not self.initData(True,**kwargs):   #con el codigo actual es imposible, pero conviene tenerlo en cuenta
            return
        #self.defineModel()            
        #self = QTreeView(self)
        #self.setModel(modeloActivo)
        
        #self.expandToDepth(1)
        self.setSortingEnabled(True)
        #self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.AscendingOrder)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        self.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.header().customContextMenuRequested.connect(self.openHeaderContextMenu)

        self.editAllowed = False
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
    def dataChanged(self, *args,**kwargs):
        topLeft = args[0]
        bottomRight = args[1]
        roles = args[2]
        if topLeft == bottomRight:
            # debo desactivar las señales porque en caso contrario, el limpiado provoca un recursivo
            self.model().blockSignals(True)
            item = self.model().itemFromIndex(topLeft)
            nuevoDato = s2n(item.data(Qt.DisplayRole))
            viejoDato = s2n(item.data(Qt.UserRole +1))
            item.setData(None,Qt.DisplayRole) # ahora reseto. La aplicacion no espera DR en general
            if nuevoDato != viejoDato:  #ha cambiado
                if nuevoDato == '':  #revierto los cambios
                    pass
                else:
                    self.parent.restorator.setEnabled(True)
                    delta = nuevoDato - viejoDato
                    if type(item) == QStandardItem:
                        col = topLeft.column() 
                        cabecera = _getHeadColumn(item)
                        item = cabecera.setColumn(col,nuevoDato)
                    else:
                        item.setData(nuevoDato,Qt.UserRole +1)
                    #FIXME Solo funciona para sum puros
                    #self.vista.recalcGrandTotal()
                    pai = item.parent()
                    while pai:
                        pai.spi(topLeft.column() -1,s2n(pai.gpi(topLeft.column() -1)) + delta)
                        pai = pai.parent()
            self.model().blockSignals(False)
        super().dataChanged(*args,**kwargs)
     
    def activateEdit(self):
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.editAllowed = True
        self.parent.editActions['active'].setEnabled(False)
        self.parent.editActions['inactive'].setEnabled(True)
        
    def deactivateEdit(self):
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.editAllowed = False
        self.parent.editActions['active'].setEnabled(True)
        self.parent.editActions['inactive'].setEnabled(False)

    def initData(self,inicial=False,**viewData):
        #FIXME debo poder escapar y ahora no lo permito
        if viewData:
            pass
        else:
            viewData = self.parent.requestVista()
        
        if not viewData:
            return False 
        self.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], total=viewData['totalizado'], estad=viewData['stats'])
        
        self.defineModel()
        return True

    def getTitleText(self):
        return "{} X {} : {}({})".format(
                    self.vista.row_hdr_idx.name,
                    self.vista.col_hdr_idx.name,
                    self.vista.agregado,
                    self.vista.campo.split('.')[-1]
                    )
    
    def setTitle(self):
        tabId = self.parent.tabulatura.currentIndex()
        if tabId < 0:
            return
        curWidget = self.parent.tabulatura.currentWidget()
        self.parent.tabulatura.setTabText(tabId,curWidget.getTitleText())
            
    def setupFilters(self): #,my_cubos,seleccion):
        #self.cubo = Cubo(my_cubos[seleccion])
        #self.cubo.nombre = seleccion #FIXME es que no tengo sitio en Cubo para definirlo
        self.filtro = ''
        self.filtroCampos = ''
        self.filtroFechas = ''
        #self.vista = None
        self.filterValues = None
        self.isModified = False
        #self.cubo.recordStructure = self.getCubeRecordInfo()

            #self.cargaVista(row,col,agregado,campo,totalizado,stats)

    @waiting_effects
    @stopwatch
    def cargaVista(self,row, col, agregado, campo, total=True, estad=True,force=False):
        if self.vista is None:
            self.vista = Vista(self.cubo, row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro)
            self.vista.toNewTree2D()
            self.defineModel()
        else:
            self.changeView(row, col, agregado, campo, total,estad,force)
            #self.refreshTable()
        #self.vista.format = self.format

    @waiting_effects
    @stopwatch
    def changeView(self,row, col, agregado, campo, total=True, estad=True,force=False):
        self.vista.setNewView(row, col, agregado, campo, totalizado=total, stats=estad,filtro=self.filtro,force=force)
        self.vista.toNewTree2D()
        #
        self.defineModel()
        
    def defineModel(self):
        self.setModel(self.vista.row_hdr_idx)
        self.colHdr = self.vista.col_hdr_idx.asHdr()
        self.vista.row_hdr_idx.setHorizontalHeaderLabels(
            [self.vista.row_hdr_idx.name,]+ 
            self.colHdr )
            #[item.data(Qt.DisplayRole) for item in self.vista.col_hdr_idx.traverse()])
        self.expandToDepth(0)
        self.setTitle()

        
    #def changeVista(self):
        #viewData = self.requestVista()
        #if not viewData:
            #return
        #self.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], total=viewData['totalizado'], estad=viewData['stats'])
        
        #self.setTitle()
        
    @waiting_effects
    @model_change_control()
    def traspose(self):
        #self.model().beginResetModel()
        self.vista.traspose()
        #self.model().getHeaders()
        #self.model().rootItem = self.vista.row_hdr_idx.rootItem
        #self.model().endResetModel()
        self.defineModel()

    @keep_tree_layout
    def refreshTable(self):
        """
            La eleccion de una u otra señal no es casualidad.
            Si utilizo layoutChanged el dialogo setNumberFormat cruje inmisericordemente al cerrar si no se le define el WA_DeleteOnClose !!!!???
        """
        self.model().modelReset.emit()
        #self.model().emitModelReset()
        #self.model().layoutChanged.emit()
        
     
    def setNumberFormat(self):
        """ adapted from Rapid development with PyQT book (chapter 5) """
        self.numberFormatDlg = NumberFormatDlg(self.model().datos.format, self.setTreeFormat, self)
        #self.numberFormatDlg.setAttribute(Qt.WA_DeleteOnClose) #si no cruje inmisericordemente ¿ o no?
        self.numberFormatDlg.show()
        self.numberFormatDlg.raise_()
        self.numberFormatDlg.activateWindow()
        #self.refreshTable()  #creo que es innecesario
    
    def setTreeFormat(self):
        #for entrada in self.format:
            #self.model().datos.format[entrada] = self.format[entrada]
        self.refreshTable()
        
    @keep_tree_layout()
    @waiting_effects
    @model_change_control()
    def restoreData(self):
        #app.setOverrideCursor(QCursor(Qt.WaitCursor))
        #expList = saveExpandedState(self)
        #self.model().beginResetModel()
        for item in self.model().traverse():
            item.restoreBackup()
            if self.vista.stats :
               item.setStatistics()

        #self.model().rootItem = self.vista.row_hdr_idx.rootItem    
        #self.model().endResetModel()
        #restoreExpandedState(expList,self)
        #self.expandToDepth(2)
        #app.restoreOverrideCursor()
        self.isModified = False
        self.parent.restorator.setEnabled(False)

    #@waiting_effects 
    def dispatch(self,fcnName):
        self.parent.ufHandler.dispatch(self.model(),fcnName)
        self.parent.restorator.setEnabled(True)

    def setFilter(self):
        #self.areFiltered = True
        #self.cubo.recordStructure = self.getCubeRecordInfo()
        
        filterDlg = filterDialog(self.cubo.recordStructure,self,driver=self.cubo.dbdriver)
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
        nuevo_filtro = mergeString(self.filtroCampos,self.cubo.definition.get('base filter',''),'AND')
        my_cubos = load_cubo(self.parent.cubeFile)
        my_cubos[self.cubo.nombre]['base filter'] = nuevo_filtro
        dump_structure(my_cubos,self.parent.cubeFile,secure=True)
        self.parent.filterActions['drop'].setEnabled(False)
        self.parent.filterActions['save'].setEnabled(False)

        
    def setRange(self):
        #FIXME ¿deberia incluir los filtros incluidos en la definicion ?
        camposFecha= [ (item['name'],item['format']) for item in self.cubo.recordStructure if item['format'] in ('fecha','fechahora') ]
        if len(camposFecha) == 0:
            #TODO que hago con Sqlite
            return
        def queFormato(fieldName):
            formato = 'fecha'
            for item in camposFecha:
                if fieldName == item[0]:
                    formato = item[1]
                    break
            return formato
        datos = []
        descriptores = []
        if self.cubo.definition.get('date filter'):
            for item in self.cubo.definition.get('date filter'):
                descriptores.append(item['elem'])
                intervalo = dateRange(CLASES_INTERVALO.index(item['date class']),TIPOS_INTERVALO.index(item['date range']),periodo=int(item['date period']))
                datos.append([CLASES_INTERVALO.index(item['date class']),
                             TIPOS_INTERVALO.index(item['date range']),
                             item['date period'],
                             str(intervalo[0]),str(intervalo[1])])
        for item in camposFecha:
            if item[0] in descriptores:
                continue
            else:
                descriptores.append(item[0])
                datos.append([0,0,1,None,None])
        #descriptores = [ item[0] for item in camposFecha ]
        form = dateFilterDlg(descriptores,datos)
        if form.exec_():
            sqlGrp = []
            #if self.cubo.definition.get('date filter'):
                #pass
            #else:
                #self.cubo.definition['date filter'] = []
            self.cubo.definition['date filter'] = []        
            for k,entry in enumerate(form.result):
                if entry[1] != 0:
                    formato = queFormato(entry[0])
                    self.cubo.definition['date filter'].append({
                                                'elem':entry[0],
                                                'date class': CLASES_INTERVALO[entry[1]],
                                                'date range': TIPOS_INTERVALO[entry[2]],
                                                'date period': entry[3],
                                                'date start': None,
                                                'date end': None,
                                                'date format': formato
                                                })
                    intervalo = dateRange(entry[1],entry[2],periodo=entry[3],fmt=formato)
                    sqlGrp.append((entry[0],'BETWEEN',intervalo,'f'))
            if len(sqlGrp) > 0:
                #self.filtroFechas = searchConstructor('where',{'where':sqlGrp,'driver':self.cubo.dbdriver})
                #self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
                self.cargaVista(self.vista.row_id,self.vista.col_id,
                            self.vista.agregado,self.vista.campo,
                            self.vista.totalizado,self.vista.stats,force=True) #__WIP__ evidentemente aqui faltan todos los parametros

                self.parent.dateRangeActions['drop'].setEnabled(True)
                self.parent.dateRangeActions['save'].setEnabled(True)
    
    def restoreRangeDef(self):
        my_cubos = load_cubo(self.parent.cubeFile)
        if my_cubos[self.cubo.nombre].get('date filter'):
            self.cubo.definition['date filter'] = my_cubos[self.cubo.nombre]['date filter']  
        else:
            del self.cubo.definition['date filter']
        self.filtroFechas=''
        self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')

    def dropRange(self):
        self.restoreRangeDef()
        self.cargaVista(self.vista.row_id,self.vista.col_id,
                        self.vista.agregado,self.vista.campo,
                        self.vista.totalizado,self.vista.stats,force=True) #__WIP__ evidentemente aqui     def saveFilter(self):
        self.parent.dateRangeActions['drop'].setEnabled(False)
        self.parent.dateRangeActions['save'].setEnabled(False)

    def saveRange(self):
        my_cubos = load_cubo(self.parent.cubeFile)
        my_cubos[self.cubo.nombre]['date filter'] = self.cubo.definition['date filter']
        dump_structure(my_cubos,self.parent.cubeFile,secure=True)
        self.parent.filterActions['drop'].setEnabled(False)
        self.parent.filterActions['save'].setEnabled(False)

    
    
    def export(self):
        #TODO poder hacer una seleccion de area
        parms = eW.callExportWizard()
        selArea = dict()
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
        self.ctxMenuHdr.append(menu.addAction("Añadir Columna",lambda :self.execHeaderAction("add",position)))
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
        elif function == "add":
            arbol = self.vista.col_hdr_idx
            count = 1
            kindex= None
            for item in arbol.traverse():
                if count == columna:
                    kindex = item.index()
                    break
                else:
                    count += 1
            self.insertElement('column',kindex)

    def openContextMenu(self,position):
        menu = QMenu()
        self.ctxMenu = []
        self.ctxMenu.append(menu.addAction("Insertar fila",lambda :self.execAction("add",position)))
        self.ctxMenu.append(menu.addAction("Gráfico de la fila",lambda :self.execAction("graph",position)))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def execAction(self,function,position):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        if function == 'graph':
            self.drawGraph('row',index)
        elif function == 'add':
            self.insertElement('row',index)

     
    @model_change_control()    
    def insertElement(self,tipo,index):
        if not tipo:
            return 
        elif tipo == 'row':
            arbol = self.vista.row_hdr_idx
            complemento = self.vista.col_hdr_idx
            kindex = index
        elif tipo == 'column':            
            arbol = self.vista.col_hdr_idx
            complemento = self.vista.row_hdr_idx
            kindex= index
        else:
            return
        spec = [ ('Nombre',QLineEdit,None) ,
                 #('Funcion Carga',QLineEdit, None)
                 ]
        values = [ None for k in range(len(spec))]
        parmDialog = propertySheetDlg('Introduzca los datos de {}'.format(tipo),spec,values, self)
        if parmDialog.exec_():
            value = values[0]
            key = kindex.data(Qt.UserRole +1) + '1'
        else:
            return
        parent = arbol.itemFromIndex(kindex.parent())
        if not parent:
            parent = arbol.invisibleRootItem()
        pos = kindex.row()
        item = GuideItem(key,value)
        #item.setData(value,Qt.DisplayRole)
        #item.setData(key,Qt.UserRole +1)
        parent.insertRow(pos +1,(item,))
        #
        self.vista.toNewTree2D()
        self.defineModel()

    
    def drawGraph(self,source,id):
        dialog = GraphDlg(self.parent.tabulatura.currentWidget().chartType, source, self)
        if dialog.exec_():
            chart = self.parent.tabulatura.currentWidget().chart
            if dialog.result:
                if source == 'row':
                    item = self.model().item(id)
                    titulo = item['key']
                    datos = item.getPayload()
                    etiquetas = self.colHdr()
                elif source == 'col':
                    titulo = self.colHdr[id - 1]
                    datos = []
                    etiquetas = []
                    for entrada in self.model().traverse():
                        if dialog.hojas and not entrada.isLeaf():
                            continue
                        if entrada.gpi(id -1) is None:
                            continue
                        datos.append(entrada.gpi(id -1))
                        etiquetas.append(entrada.getFullHeadInfo())
                        
                
                x_text = self.model().name
                y_text = ''
                if len(datos) == 0:
                    chart.axes.cla()
                else:
                    chart.loadData(dialog.result,etiquetas,datos,titulo,x_text,y_text)  
                chart.draw()
                chart.show()
            else:
                chart.hide()
if __name__ == '__main__':
    import sys

    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    parser = generaArgParser()
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = DanaCubeWindow(args)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
