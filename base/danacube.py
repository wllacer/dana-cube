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
#from base.cubetree import traverseTree
from support.datalayer.query_constructor import searchConstructor

from support.gui.mplwidget import * #ChartTab
from support.util.uf_manager import *

#import base.exportWizard as eW
from base.exportSelector import exportDialog

from support.util.treestate import *
from base.tree import GuideItem,_getHeadColumn,traverseBasic,searchHierarchyUnsorted
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

    experimental_parser = parser.add_mutually_exclusive_group(required=False)
    experimental_parser.add_argument('--experimental','-x',dest='experimental', action='store_true', help='Activa funciones experimentales')
    experimental_parser.add_argument('--no-experimental','-nx', dest='experimental', action='store_false')
    parser.set_defaults(experimental=False)

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
        self.experimental = args.experimental
        
        self.filterActions = dict()
        self.dateRangeActions = dict()
        self.editActions = dict()
        
        self.editActions = {}
        
        self.tabulatura	= QTabWidget()
        self.tabulatura.setTabsClosable(True)
        self.tabulatura.currentChanged[int].connect(self.checkChanges)
        self.tabulatura.tabCloseRequested[int].connect(self.closeView)
        self.views = list()
        self.selectCube(True)
        
        #CHANGE here. En este caso defino el menu tras los widgets porque si no no compila
        self.cubeMenu = self.menuBar().addMenu("&Cubo")
        self.cubeMenu.addAction("Abrir Cubo ...", self.selectCube, "Ctrl+O")
        self.cubeMenu.addSeparator()
        self.cubeMenu.addAction("Convertir vista actual a defecto", self.defaultVista)

        self.viewMenu = self.menuBar().addMenu("&Vista")
        self.viewMenu.addAction("Abrir Vista ...",lambda a='new': self.openView(a), "Ctrl+V")
        self.viewMenu.addAction("Cambiar vista actual ...", lambda a='active': self.openView(a), "Ctrl+M")     
        self.viewMenu.addAction("Cerrar vista actual", self.closeView)     
        if self.experimental:
            self.viewMenu.addSeparator()
            self.viewMenu.addAction("Añadir criterio de agrupacion", self.addLevel)     
        self.filtersMenu = self.menuBar().addMenu("Usar &Filtros")

        self.filterActions['create'] = self.filtersMenu.addAction('Editar Filtro ...',
                                    self.setFilter,
                                    "Ctrl+S")
        self.filterActions['drop'] = self.filtersMenu.addAction('Borrar Filtros',
                                    self.dropFilter)
        self.filterActions['save'] = self.cubeMenu.addAction('Guardar Filtros permanentemente',
                                    self.saveFilter)
        self.filterActions['drop'].setEnabled(False)
        self.filterActions['save'].setEnabled(False)
        self.filtersMenu.addSeparator()

        
        self.dateRangeActions['dates'] = self.filtersMenu.addAction('Editar Rango fechas ...',
                                    self.setRange,
                                    "Ctrl+F")
        self.dateRangeActions['drop'] = self.filtersMenu.addAction('Borrar Rango fechas',
                                    self.dropRange)
        self.dateRangeActions['save'] = self.cubeMenu.addAction('Salvar Rango fechas',
                                    self.saveRange)
        self.dateRangeActions['drop'].setEnabled(False)
        self.dateRangeActions['save'].setEnabled(False)


        # esta es la version nueva del menu funcional
        
        self.userFunctionsMenu = self.menuBar().addMenu("Funciones de &usuario")
        self.editActions['restore'] = self.userFunctionsMenu.addAction("Restaurar valores originales"
            ,self.tabulatura.currentWidget().tree.restoreData,"Ctrl+R")
        self.editActions['restore'].setEnabled(False)

        self.userFunctionsMenu.addSeparator()
        self.editActions['active'] = self.userFunctionsMenu.addAction("Activar edicion celdas"
            ,self.tabulatura.currentWidget().tree.activateEdit,"Ctrl+E")
        self.editActions['active'].setEnabled(True)
        self.editActions['inactive'] = self.userFunctionsMenu.addAction("Desactivar edicion celdas"
            ,self.tabulatura.currentWidget().tree.deactivateEdit,"Ctrl+D")
        self.editActions['inactive'].setEnabled(False)
        
        self.userFunctionsMenu.addSeparator()
        
        self.ufHandler = Uf_handler(self.userFunctionsMenu,self.cubo,self.dispatch,self.contextFile)
        self.plugins = self.ufHandler.plugins
        self.pluginDbMenu = self.ufHandler.specUfMenu
        ## opciones
        self.optionsMenu = self.menuBar().addMenu("&Opciones")
        self.optionsMenu.addAction("Graficos",self.setGraph,"Ctrl+G")
        self.optionsMenu.addAction("Exportar datos ...",
                                   self.exportData,
                                   "Ctrl+X")
        self.optionsMenu.addAction("Trasponer datos",
                                   self.trasposeData,
                                   "Ctrl+T")
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction("Ocultar / Mostrar")
        self.optionsMenu.addAction("                            Columnas...",self.hiddenColumns)
        self.optionsMenu.addAction("                            Filas...",self.hiddenRows)
        self.optionsMenu.addSeparator()
        self.optionsMenu.addAction("Presentacion ...",
                                   self.setNumberFormat,
                                   "Ctrl+F")
        self.optionsMenu.addAction("Mantenimiento de funciones de usuario",self.adminUF,"Ctrl+U")
        ## esto al final para que las distintas opciones raras que van al menu de cubos vayan en su sitio
        self.cubeMenu.addSeparator()
        self.cubeMenu.addAction("E&xit", self.close, "Ctrl+Q")


        self.setCentralWidget(self.tabulatura)
    
    def adminUF(self):
        """ 
        manejo el editor de funciones a traves de un dialogo
        Cuando retorna elimino todas las funciones del menu que no son genericas y reinicializo el gestor de funciones
        de usuario.
        TODO La pena es que en teoria al menos no recoge los cambios en los modulos, sólo en el menú. para eso tengo que modificar el proceso de import en ufHandler
        """
        from support.util.uf_menuEditor import ufTreeMgrDialog
        form = ufTreeMgrDialog(self.contextFile)#(lista,initial)
        form.show()
        if form.exec_():
            # la logica para borrar entrqas del menu a veces es un poco esoterica. Aqui tengo claro cuantos elementos
            # quedan, tres entradas y dos separadores, asi que puedo ir directamente por el numero
            acciones = self.userFunctionsMenu.actions()
            for k in range(5,len(acciones)):
                #print('borro',acciones[k].text())
                self.userFunctionsMenu.removeAction(acciones[k])
            #reinicializo el contexto
            self.ufHandler = Uf_handler(self.userFunctionsMenu,self.cubo,self.dispatch,self.contextFile)
            self.plugins = self.ufHandler.plugins
            self.pluginDbMenu = self.ufHandler.specUfMenu
            if self.cubo:
                self.fillUserFunctionMenu(self.pluginDbMenu,self.cubo.nombre)

#            self.fillUserFunctionMenu()        
    def fillUserFunctionMenu(self,menu,db=''):
        self.ufHandler.fillUserFunctionMenu(db)
        
    def checkChanges(self,destino):
        currentWidget = self.tabulatura.currentWidget()   #.tree
        if not self.filterActions or not self.dateRangeActions or not self.editActions['restore']:
            return
        if not currentWidget:
            self.filterActions['drop'].setEnabled(False)
            self.filterActions['save'].setEnabled(False)
            self.editActions['restore'].setEnabled(False)
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
            self.editActions['restore'].setEnabled(True)
        else:
            self.editActions['restore'].setEnabled(False)

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
        for item in traverseBasic(dict.hiddenRoot):
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
            parametros[2]=vista.agregado #self.cubo.getFunctions().index(vista.agregado)
            parametros[3]=vista.campo #self.cubo.getFields().index(vista.campo)
            parametros[4]=vista.totalizado
            parametros[5]=vista.stats
        
        vistaDlg = VistaDlg(self.cubo,parametros, self)
            
        if vistaDlg.exec_():
            viewData['row'] = vistaDlg.data[0]
            viewData['col'] = vistaDlg.data[1]
            viewData['agregado'] = vistaDlg.data[2]  
            viewData['campo'] = vistaDlg.data[3] 
            viewData['totalizado'] = vistaDlg.data[4]
            viewData['stats'] = vistaDlg.data[5]
        
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

    
    def closeView(self,idx=None):
        if idx:
            tabId = idx
        else:
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
            attrs = { clave:viewData[clave] for clave in viewData if clave not in ('row','col','agregado','campo') }
            areView,areAttr = currentWgt.tree.vista.getAttributes()
            if areAttr.get('cartesian') and areView[0] == viewData['row']:
                attrs['cartesian'] = areAttr['cartesian']
            currentWgt.tree.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], **attrs)
        else:
            return

    def addLevel(self,action='new'):
        currentWgt = self.tabulatura.currentWidget()
        if not currentWgt:
            return        
        viewData ={'row': currentWgt.tree.vista.row_id,
                            'col'  : currentWgt.tree.vista.col_id,
                            'agregado': currentWgt.tree.vista.agregado,
                            'campo': currentWgt.tree.vista.campo,
                            'totalizado':currentWgt.tree.vista.totalizado,
                            'stats':currentWgt.tree.vista.stats
                            }
        guias = self.cubo.getGuideNames()
        dialog = eligeFiltroDlg(guias)
        dialog.show()
        if dialog.exec_():
            #return dialog.resultado,dialog.residx
            viewData['cartesian']=dialog.cartesian
            if dialog.resultado.startswith('_'):
                viewData['row'] = dialog.residx
            else:
                elem1 = self.cubo.definition['guides'][viewData['row']]
                elem2 = self.cubo.definition['guides'][dialog.residx]
                nname = '_'+self.cubo.getGuideNames()[viewData['row']].strip()+'_'+dialog.resultado.strip()
                #FIXME y si ya lo he fabricado ¿?
                newElem = { 'class':'h','name':nname,'prod':[] }
                newElemRef= {'name':newElem['name'],'class':newElem['class'],'contexto':[],'elem':[]}
                for rule in (elem1.get('prod') + elem2.get('prod')):
                    newElem['prod'].append(rule)
                self.cubo.definition['guides'].append(newElem)
                self.cubo.lista_guias.append(newElemRef)
                viewData['row'] = len(self.cubo.lista_guias) -1
                
            if action == 'new':
                self.addView(**viewData)
            #TODO esta desactivado   
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
       
    def hiddenColumns(self):
        self.tabulatura.currentWidget().hiddenColumns()
    def hiddenRows(self):
        self.tabulatura.currentWidget().hiddenRows()
    
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
        self.chart = ChartTab()
        self.chartType = None #'barh'
        self.lastItemUsed = None
        #self.tree.clicked.connect(self.drawChart)
        
        split.addWidget(self.tree)
        split.addWidget(self.chart)
        
        lay.addWidget(split,0,0)

        self.drawChart(None)
    
    def setGraph(self):
        dialog = GraphDlg(self.chartType, parent=self)
        if dialog.exec_():
            self.chartType = dialog.result
        self.drawChart()
    
    def getTitleText(self):
        return self.tree.getTitleText()
    
    def dispatch(self,FcnName):
        self.tree.dispatch(FcnName)
        #self.drawChart()
        self.tree.reloadGraph()

    def drawChart(self,index=None):
        if self.chartType:
            self.processChartItem(index,tipo=self.chartType)
        else:
            self.chart.hide()
    
    def processChartItem(self,index=None,tipo='bar',visibleOnly=True):
        if index:
            if index.isValid():
                item = self.tree.model().itemFromIndex(index)
                rowid = item.getHead()
            else:
                return
            
        elif len(self.tree.selectedIndexes()) > 0:
            indice = self.tree.selectedIndexes()[0]
            item = self.tree.model().itemFromIndex(indice)
            rowid = item.getHead()

        elif self.lastItemUsed is not None:
            item = self.lastItemUsed
            rowid = item

        else:
            item = self.tree.model().invisibleRootItem().child(0)
            rowid = item
        self.lastItemUsed = rowid
        if visibleOnly:
            pFilter = lambda x,y=self.tree,z='col':y.isItemVisible(x,z)
        else:
            pFilter = None
        self.chart.loadData(self.tree.vista,rowid,graphType=tipo,dir='row',filter=pFilter)  #TODO filter    
        self.chart.draw()
        self.chart.show()
        
    def hiddenColumns(self):
        self.tree.hiddenColsMgr()
        self.tree.reloadGraph()
    def hiddenRows(self):
        self.tree.hiddenRowsMgr()
        self.tree.reloadGraph()
        
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
        
        
    
    def currentChanged(self,hacia,desde):
        if not self.parent.tabulatura:
            pass
        elif not self.parent.tabulatura.currentWidget().chart:
            pass
        elif not self.parent.tabulatura.currentWidget().chart.isHidden():
            chart = self.parent.tabulatura.currentWidget().chart
            #print(self.model().itemFromIndex(desde),desde.row(),desde.column(),self.model().itemFromIndex(desde.parent()),
                     #self.model().itemFromIndex(hacia),hacia.row(),hacia.column(),self.model().itemFromIndex(hacia.parent()) 
                     #)
            if desde is None or hacia is None:
                pass
            elif chart.dir == 'row' and  desde.row() == hacia.row() and desde.parent() == hacia.parent():
                pass
            elif chart.dir == 'col' and desde.column() == hacia.column():
                pass
            elif chart.dir == 'row':
                    head = self.model().itemFromIndex(hacia.siblingAtColumn(0))
                    self.reloadGraph(head)                  
            elif chart.dir == 'col':
                    head = self.vista.col_hdr_idx.pos2item(hacia.column() -1)
                    self.reloadGraph(head)  
            else:
                print('No hay parametros correctos')
        super().currentChanged(desde,hacia)

    def reloadGraph(self,item=None):
        chart = self.parent.tabulatura.currentWidget().chart
        if not chart or chart.isHidden():
            return
        chart.reLoad(item)
        
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
                    self.parent.editActions['restore'].setEnabled(True)
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
        #TODO viewData
        attrs = { clave:viewData[clave] for clave in viewData if clave not in ('row','col','agregado','campo') }
        self.cargaVista(viewData['row'], viewData['col'], viewData['agregado'], viewData['campo'], **attrs)
        
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
    def cargaVista(self,*lparm, **kparm):
        """ row, col, agregado, campo, """
        """:total=True, estad=True,force=False,cartesian=False):"""
        row,col,agregado,campo = lparm[:4]
        if self.vista is None:
            self.vista = Vista(self.cubo, row, col, agregado, campo, **kparm)
            self.vista.toNewTree2D()
            self.defineModel()
        else:
            self.changeView(row, col, agregado, campo, **kparm)
            #self.refreshTable()
        #self.vista.format = self.format

    @waiting_effects
    @stopwatch
    def changeView(self,row, col, agregado, campo, **kparm):
        """ total=True, estad=True,force=False,cartesian=False) """
        self.vista.setNewView(row, col, agregado, campo, **kparm) 
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
        if self.vista.cartesian:
            for item in self.vista.row_hdr_idx.traverse():
                row = item.row()
                pai = item.parent().index() if item.parent() else QModelIndex()
                if item.hasPayload():
                    self.setRowHidden(row,pai,False)
                else:
                    self.setRowHidden(row,pai,True)
        else:
            for item in self.vista.row_hdr_idx.traverse():
                row = item.row()
                pai = item.parent().index() if item.parent() else QModelIndex()
                self.setRowHidden(row,pai,False)
            
        for pos,item in enumerate(self.vista.col_hdr_idx.traverse()):
            self.setColumnHidden(pos +1,False)

                
            
        
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
            if self.isRowHidden(item.row(),item.parent().index() if item.parent() else QModelIndex()):
                self.setRowHidden(item.row(),item.parent().index() if item.parent() else QModelIndex(),False)
                
        for j in range(self.vista.col_hdr_idx.len()):
            if self.isColumnHidden(j +1):
                self.setColumnHidden(j +1,False)

        #self.model().endResetModel()
        #restoreExpandedState(expList,self)
        #self.expandToDepth(2)
        #app.restoreOverrideCursor()
        self.isModified = False
        self.parent.editActions['restore'].setEnabled(False)

    #@waiting_effects 
    def dispatch(self,fcnName):
        
        self.parent.ufHandler.dispatch(self.model(),fcnName,tree=self)
        self.parent.editActions['restore'].setEnabled(True)

    def setFilter(self):
        #self.areFiltered = True
        #self.cubo.recordStructure = self.getCubeRecordInfo()
        
        filterDlg = filterDialog(self.cubo.recordStructure,self.filterValues,'Aplicar filtro a la consulta',self,driver=self.cubo.dbdriver)
        if filterDlg.exec_():
            self.filtroCampos=filterDlg.result
            self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
            self.filterValues = [ data for data in filterDlg.data]
            viewDef,viewData = self.vista.getAttributes()
            viewData['filtro'] = self.filtro
            self.cargaVista(*viewDef,**viewData)
            self.parent.filterActions['drop'].setEnabled(True)
            self.parent.filterActions['save'].setEnabled(True)


    def dropFilter(self):
        self.filtroCampos=''
        self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
        self.filterValues = None
        viewDef,viewData = self.vista.getAttributes()
        viewData['filtro'] = self.filtro
        self.cargaVista(*viewDef,**viewData)
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
                intervalo = dateRange(item['date class'],item['date range'],periodo=int(item['date period']))
                datos.append([ item['date class'],
                             item['date range'],
                             item['date period'],
                             str(intervalo[0]),str(intervalo[1])])
        for item in camposFecha:
            if item[0] in descriptores:
                continue
            else:
                descriptores.append(item[0])
                datos.append([0,0,1,None,None])
        #descriptores = [ item[0] for item in camposFecha ]
        form = dateFilterDlg(descriptores=descriptores,datos=datos)
        if form.exec_():
            sqlGrp = []
            #if self.cubo.definition.get('date filter'):
                #pass
            #else:
                #self.cubo.definition['date filter'] = []
            self.cubo.definition['date filter'] = []        
            for k,entry in enumerate(form.result.get('datos',[])):
                if entry[1] != 0:
                    formato = queFormato(entry[0])
                    self.cubo.definition['date filter'].append({
                                                'elem':entry[0],
                                                'date class': entry[1],
                                                'date range': entry[2],
                                                'date period': entry[3],
                                                'date start': None,
                                                'date end': None,
                                                'date format': formato
                                                })
                    intervalo = dateRange(entry[1],entry[2],periodo=entry[3],fmt=formato)
                    sqlGrp.append((entry[0],'BETWEEN',intervalo,'f'))
            if len(sqlGrp) > 0:
                #self.filtroFechas = searchConstructor('where',where=sqlGrp,driver=self.cubo.dbdriver)
                #self.filtro = mergeString(self.filtroCampos,self.filtroFechas,'AND')
                viewDef,viewData = self.vista.getAttributes()
                self.cargaVista(*viewDef,**viewData)


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
        viewDef,viewData = self.vista.getAttributes()
        viewData['filtro'] = self.filtro
        self.cargaVista(*viewDef,**viewData)
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
        dlg = exportDialog()
        dlg.show()
        if dlg.exec_():
            parms = dlg.resultado
            selArea = None
            if not parms.get('file'):
                return
            if parms.get('filter',{}).get('scope') == 'visible':
                selArea = self
            resultado = self.vista.export(parms,selArea)
            
        #parms = eW.callExportWizard()
        #pprint(parms)
        #selArea = dict()
        #if not parms.get('file'):
            #return
        #resultado = self.vista.export(parms,selArea)

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
            self.reloadGraph()
        elif function == 'unhide':
            self.setColumnHidden(columna -1,False)
            self.reloadGraph()
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
        if self.parent.experimental:
            self.ctxMenu.append(menu.addAction("Ocultar  fila",lambda :self.execAction("hide",position)))
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def execAction(self,function,position):
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        if function == 'graph':
            self.drawGraph('row',index)
        elif function == 'add':
            self.insertElement('row',index)
        elif function == 'hide':
            self.setRowHidden(index.row(),index.parent(),True)
     
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

    
    def drawGraph(self,source,id,visibleOnly=True):
        dialog = GraphDlg(self.parent.tabulatura.currentWidget().chartType, source, self)
        if dialog.exec_():
            chart = self.parent.tabulatura.currentWidget().chart
            if dialog.result:
                if source == 'row':  
                    head = self.model().itemFromIndex(id)
                else:
                    head =  self.vista.col_hdr_idx.pos2item(id -1)
                if visibleOnly:
                    if source == 'row':
                        pFilter = lambda x,y=self,z='col':y.isItemVisible(x,z)
                    else:
                        pFilter = lambda x,y=self,z='row':y.isItemVisible(x,z)
                else:
                    pFilter = None
                chart.loadData(self.vista,head,dialog.result,dir=source,filter=pFilter)
                chart.draw()
                chart.show()

            else:
                chart.hide()
               

    #def hiddenColumns(self):
        ## la columna 0 son las cabeceras de fila. De momento NO las oculto via este procedimiento
        ##FIXME no hay manara de borrar la primera columna
        #valores = []
        #for k in range(1,self.model().columnCount()):
            #if self.isColumnHidden(k):
                #valores.append(self.colHdr[k -1])
        #dialogo = hiddenElemsSelector(self.colHdr,valores)
        #dialogo.show()
        #if dialogo.exec():
            ##copiado directamente de la definicion de get
            #for k in range(dialogo.lista.count()):
                #if dialogo.lista.itemData(k,Qt.CheckStateRole) == Qt.Checked :
                    #if not self.isColumnHidden(k):
                        #self.setColumnHidden(k,True)
                #else:
                    #if self.isColumnHidden(k):
                        #self.setColumnHidden(k,False)
    #def hiddenRows(self):
        ##solo para el analisis primario
        #self.rowHdr = self.vista.row_hdr_idx.asHdr()
        #valores = []
        ## la columna 0 son las cabeceras de fila. De momento NO las oculto via este procedimiento
        #for item in self.model().traverse():
            #if self.isRowHidden(item.row(),item.parent().index() if item.parent() else QModelIndex()):
                #valores.append(item.text())
        #dialogo = hiddenElemsSelector(self.rowHdr,valores)
        #dialogo.show()
        #if dialogo.exec():
            ##copiado directamente de la definicion de get
            #k = 1
            #for item in self.model().traverse():
                #row = item.row()
                #pai = item.parent().index() if item.parent() else QModelIndex()
                #if dialogo.lista.itemData(k,Qt.CheckStateRole) == Qt.Checked :
                    #if not self.isRowHidden(row,pai):
                        #self.setRowHidden(row,pai,True)
                #else:
                    #if self.isRowHidden(row,pai):
                        #self.setRowHidden(row,pai,False)
                #k += 1

    def hiddenColsMgr(self):
        # la columna 0 son las cabeceras de fila. De momento NO las oculto via este procedimiento
        #TODO que hacer con los elementos jerarquicos ¿?
        #TODO textos no editables en el dialogo
        
        valores = []
        for k in range(1,self.model().columnCount()):
            if self.isColumnHidden(k):
                valores.append(self.vista.col_hdr_idx.pos2item(k -1).getFullHeadInfo(format='string'))
        #dialogo = hiddenElemsSelector(self.vista.col_hdr_idx,valores)
        dialogo = hiddenElemsMgr('col',valores,self)
        dialogo.show()
                

    def hiddenRowsMgr(self):
        # la columna 0 son las cabeceras de fila. De momento NO las oculto via este procedimiento
        #TODO que hacer con los elementos jerarquicos ¿?
        
        valores = []
        for item in self.model().traverse():
            if self.isRowHidden(item.row(),item.parent().index() if item.parent() else QModelIndex()):
                valores.append(item.getFullHeadInfo(format='string'))
        dialogo = hiddenElemsMgr('row',valores,self)
        dialogo.show()
    
    def isItemVisible(self,item,direccion):
        if direccion == 'col':
            pos = self.vista.col_hdr_idx.item2pos(item)
            if self.isColumnHidden(pos +1):
                return False
            else:
                return True
        elif direccion == 'row':
            entry = item
            hidden = False
            while entry:
                row = entry.row()
                pai = entry.parent().index() if entry.parent() else QModelIndex()
                if self.isRowHidden(row,pai):
                    hidden = True
                    break
                entry = entry.parent()
            if hidden:
                return False
            else:
                return True
        return True

        
class hiddenElemsMgr(QDialog):
    #def __init__(self,entradas,valores,parent=None):
    def __init__(self,direccion,valores,parent=None):
        super().__init__(parent)
        self.direccion = direccion
        self.parent = parent
        self.propagate = QCheckBox('Propagar a lo largo de la jerarquia') 
        #TODO lo mismo que en la descarga (multi cosas)
        self.soloLeaf = QCheckBox('Mostrar solo las hojas')
        self.soloBranch = QCheckBox('Mostrar solo las ramas')
        
        self.lista = QTreeView()
        self.lista.header().hide()
        #TODO las lineas de arbol, ¿puedo eliminarlas?
        if self.direccion == 'col':
            self.source = self.parent.vista.col_hdr_idx
        elif self.direccion == 'row':
            self.source = self.parent.vista.row_hdr_idx
            
        self.propagate.setVisible(False)
        self.soloLeaf.setVisible(False)
        self.soloBranch.setVisible(False)
        
        if (self.direccion == 'col' and self.parent.vista.dim_col == 1) or (self.direccion == 'row' and self.parent.vista.dim_row == 1):
            pass
        elif self.direccion == 'row':
            self.soloBranch.setVisible(True)
        else:
            self.propagate.setVisible(True)
            self.soloLeaf.setVisible(True)
            self.soloBranch.setVisible(True)

        imodel = self.source.cloneSubTree(ordRole=Qt.UserRole +1)
        self.lista.setModel(imodel)
        self.lista.expandAll()

        for item in imodel.traverse():
            item.setCheckable(True)
            if item.getFullHeadInfo(format='string') in valores:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            
        lay = QVBoxLayout()
        lay.addWidget(self.lista)
        lay.addWidget(self.propagate)
        lay.addWidget(self.soloBranch)
        lay.addWidget(self.soloLeaf)
        self.setLayout(lay)
        

        self.lista.model().itemChanged.connect(self.itemChanged)
        #self.source.itemChanged.connect(self.itemChanged)
        self.soloLeaf.stateChanged.connect(self.hideBranch)
        self.soloBranch.stateChanged.connect(self.hideLeaf)
   
    def hideLeaf(self,state):
        for item in self.lista.model().traverse():
            if item.isLeaf():
                item.setCheckState(state)    
                
    def hideBranch(self,state):
        if state == 0:
            action = False
        else:
            action = True

        propState = self.propagate.checkState()
        self.propagate.setCheckState(False)
        for item in  self.lista.model().traverse():
            if item.isBranch():
                item.setCheckState(action)
        self.propagate.setCheckState(propState)
        
    def itemChanged(self,item):
        if item.isLeaf() or self.direccion == 'row':
            self.switchVectorVisibility(item,self.direccion,item.checkState())
        else:
            self.switchVectorVisibility(item,self.direccion,item.checkState())
            if self.propagate.checkState():
                for k in range(item.rowCount()):
                    item.child(k,0).setCheckState(item.checkState())
                
    def switchVectorVisibility(self,item,dir,state):
            clave = item.getFullHeadInfo(role=Qt.UserRole +1,format='array')
            ref_elem = self.source.searchHierarchy(clave,role=Qt.UserRole +1)
            # si ha habido un sort sobre la vista es probable que lo anterior no encuentre los datos de referencia
            if not ref_elem:  
                ref_elem = searchHierarchyUnsorted(self.source,clave,role=Qt.UserRole +1)
            if dir == 'col':
                pos = self.source.item2pos(ref_elem)
                if state:
                    self.parent.setColumnHidden(pos +1,True)
                else:
                    self.parent.setColumnHidden(pos +1,False)
            elif dir == 'row':
                row = ref_elem.row()
                pai = ref_elem.parent().index() if ref_elem.parent() else QModelIndex()
                if state:
                    self.parent.setRowHidden(row,pai,True)
                else:
                    self.parent.setRowHidden(row,pai,False)
                    
class eligeFiltroDlg(QDialog):
    def __init__(self,listGuides,parent=None):
        super().__init__(parent)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.msgLine = QLabel()
        #nameLbl = QLabel('Nombre de la guia')
        #self.name = QLineEdit()
        
        clauseLbl = QLabel('Eliga la condicion por la que desea agurpar adicionalmente')

        self.selector = QComboBox()
        self.selector.addItems(listGuides)
        
        self.cartCheck = QCheckBox('Como producto cartesiano')
        self.cartCheck.setChecked(True)
        meatlayout = QVBoxLayout()
        meatlayout.addWidget(clauseLbl)
        meatlayout.addWidget(self.selector)
        meatlayout.addWidget(self.cartCheck)
        meatlayout.addWidget(self.msgLine)
        meatlayout.addWidget(buttonBox)
        
        self.setLayout(meatlayout)
        # en esta posicion para que las señales se activen tras la inicializacion
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        

    def accept(self):
        self.resultado = self.selector.currentText()
        self.residx = self.selector.currentIndex()
        self.cartesian = self.cartCheck.isChecked()
        super().accept()
        
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
