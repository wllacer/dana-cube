#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import os
import argparse

from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,\
          QPushButton, QMessageBox, \
          QTableView, QSpinBox

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError
from  sqlalchemy.sql import text

from datalayer.access_layer import *
from datalayer.conn_dialogs import *

from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from dictmgmt.dictTree import *
from dictmgmt.datadict import *

from tablebrowse import *
from cubemgmt.cubeutil import info2cube
from cubebrowse import CubeMgr
from util.decorators import *

import config

class GenerationSheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
    """
    def __init__(self,title,tableName,maxLevel,parent=None):   
        super(GenerationSheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = (('Nombre del cubo',QLineEdit,None),
                        ('Profundidad de enlaces',QSpinBox,{"setRange":(1,5)}),
                       )
        self.data = [ tableName,maxLevel ]
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(self.context,self.data)
       

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)

        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(382,200))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        self.setWindowTitle("Generation manager")
        
        

              
    def accept(self):
        self.data = self.sheet.values()
        QDialog.accept(self)
    
def generaArgParser():
    parser = argparse.ArgumentParser(description='Cubo de datos')
    parser.add_argument('--cubeFile','--cubefile','-c',
                        nargs='?',
                        default='cubo.json',
                        help='Nombre del fichero de configuración del cubo actual')    
    parser.add_argument('--configFile','--configfile','-cf',
                        nargs='?',
                        default='.danabrowse.json',
                        help='Nombre del fichero de configuración del cubo actual')    

    security_parser = parser.add_mutually_exclusive_group(required=False)
    security_parser.add_argument('--secure','-s',dest='secure', action='store_true',
                                 help='Solicita la clave de las conexiones de B.D.')
    security_parser.add_argument('--no-secure','-ns', dest='secure', action='store_false')
    parser.set_defaults(secure=True)
    schema_parser = parser.add_mutually_exclusive_group(required=False)
    schema_parser.add_argument('--sys','-S',dest='sysExclude', action='store_false',
                                 help='Incluye los esquemas internos del gestor de B.D.')
    parser.set_defaults(sysExclude=True)
    return parser

class DanaBrowseWindow(QMainWindow):
    def __init__(self,args):
        super(DanaBrowseWindow, self).__init__()
        #Leeo la configuracion
        self.configFile = args.configFile
        self.secure = args.secure
        self.cubeFile = args.cubeFile
        self.sysExclude = args.sysExclude
        
        self.maxlevel = 2  #para poder modificarlo luego
        self.dictionary = DataDict(defFile=args.configFile,secure=args.secure,sysExclude=args.sysExclude)
        #TODO variables asociadas del diccionario. Reevaluar al limpiar
        
        self.baseModel = self.dictionary.baseModel
        self.configData = self.dictionary.configData
        self.conn = self.dictionary.conn
        if self.dictionary.isEmpty:
            self.newConfigData()
            #self.dictionary._cargaModelo(self.dictionary.baseModel)
        self.setupView()
        self.cubeMgr = None # necesito mas adelante que este definida
        if config.DEBUG:
            print('inicializacion completa')
        #CHANGE here
        
         
        self.queryView = TableBrowser(pdataDict=self.dictionary)  #!!!!???? debe ir delante de la definicion de menu
        
        self.dictMenu = self.menuBar().addMenu("&Conexiones")
        self.dictMenu.addAction("&New ...", self.newConnection, "Ctrl+N")
        self.dictMenu.addAction("&Modify ...", self.modConnection, "Ctrl+M")
        self.dictMenu.addAction("&Delete ...", self.delConnection, "Ctrl+D")        
        self.dictMenu.addAction("&Save Config File", self.saveConfigFile, "Ctrl+S")
        self.dictMenu.addAction("E&xit", self.close, "Ctrl+Q")
        
        
        self.queryMenu = self.menuBar().addMenu('C&onsulta de datos')
        self.queryMenu.addAction("Cerrar",self.hideDatabrowse)
        self.queryMenu.setEnabled(False)
        
        self.cubeMenu = self.menuBar().addMenu("Cubo")
        self.cubeMenu.addAction("&Salvar", self.saveCubeFile, "Ctrl+S")
        self.cubeMenu.addAction("&Restaurar", self.restoreCubeFile, "Ctrl+M")
        self.cubeMenu.addAction("S&alir", self.hideCube, "Ctrl+D")
        self.cubeMenu.setEnabled(False)
        
        self.queryModel = self.queryView.baseModel

        self.querySplitter = QSplitter(Qt.Vertical)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.queryView)

        self.configSplitter = QSplitter(Qt.Horizontal)
        self.configSplitter.addWidget(self.querySplitter)
        
        self.setCentralWidget(self.configSplitter)

        self.setWindowTitle("Visualizador de base de datos")
        """
            estas funciones son para soportar para los decoradores keep position y tal
        """        
    def model(self):
        return self.baseModel
    def isExpanded(self,idx):
        return self.view.isExpanded(idx)
    def setExpanded(self,idx,state):
        return self.view.setExpanded(idx,state)
    
    def setupView(self):
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.baseModel)
        #self.view.resizeColumnToContents(0)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)


        self.view.expandAll()
        for m in range(self.baseModel.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.collapseAll()
        self.view.expandToDepth(0)     
        #self.view.setHeaderHidden(True)
        #self.view.setSortingEnabled(True)
        #self.view.setRootIsDecorated(False)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)


    def newConfigData(self):
        self.configData = dict()
        self.configData['Conexiones']=dict()
        self.editConnection(None)
        if self.configData['Conexiones']:
            self.saveConfigFile()
            print(self.configData)
            self.dictionary._cargaModelo(confData=self.configData['Conexiones']) #self.dictionary.baseModel)
        else:
            QMessageBox.critical(self,
                                "Error Fatal",
                                "No se ha encontrado una conexión valida.\nFin de proceso")
            self.close()
            
    def saveConfigFile(self):
        dump_config(self.configData,getConfigFileName(self.configFile),secure=self.secure) #TODO de momento
    
    def closeEvent(self, event):
        self.close()
        
    def close(self):

        if self.cubeMgr:
            self.cubeMgr.saveConfigFile()
            
        for conid in self.conn:
            if self.conn[conid] is None:
                continue
            if self.conn[conid].closed :
                self.conn[conid].close()
        self.saveConfigFile()

        sys.exit()
        
    def newConnection(self):
        confName=self.editConnection(None)
        # esta claro que sobran parametros
        self.dictionary.appendConnection(confName)
        
    def modConnection(self,nombre=None):
        if nombre is None:
            selDialog = SelectConnectionDlg(self.configData['Conexiones'])
            if selDialog.exec_():
                confName = selDialog.conexion
            else:
                return
        else:
            confName = nombre
        self.editConnection(confName)   
        self.updateModel(confName)
    
    @waiting_effects
    def updateModel(self,nombre=None):
        self.dictionary.updateModel(nombre)
        
    def delConnection(self,nombre=None):
        if nombre is None:
            selDialog = SelectConnectionDlg(self.configData['Conexiones'])
            if selDialog.exec_():
                confName = selDialog.conexion
            else:
                return 
        else:
            confName = nombre
        self.dictionary.dropConnection(confName)

    def editConnection(self,nombre=None):        
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        if nombre is None:
            datos = [None for k in range(len(attr_list) +1) ]
        else:
            datos = [nombre, ] + dict2row(self.configData['Conexiones'][nombre],attr_list)
            datos[1]=DRIVERS.index(datos[1])
        #contexto
        context = (
                ('Nombre',
                    QLineEdit,
                    {'setReadOnly':True} if nombre is not None else None,
                    None,
                ),
                # driver
                ("Driver ",
                    QComboBox,
                    None,
                    DRIVERS,
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
            datos[1]=DRIVERS[datos[1]]
            self.configData['Conexiones'][datos[0]] = row2dict(datos[1:],attr_list)
            return datos[0]
     
        

    @keep_tree_layout()
    def openContextMenu(self,position):
        """
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.baseModel.itemFromIndex(index)
        menu = QMenu()
        item.setMenuActions(menu,self)
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        #getContextMenu(item,action,self)
  
    @waiting_effects
    def databrowse(self,confName,schema,table,iters=0):
        self.queryView.loadData(confName,schema,table,self.dictionary,iters)
        
        self.queryMenu.setEnabled(True)
        if self.querySplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
            self.querySplitter.addWidget(self.queryView)
            
    def hideDatabrowse(self):
        self.queryView.hide()
        self.queryModel.clear()
        self.queryMenu.setEnabled(False)
        

    def cubebrowse(self,confName,schema,table):
        # aqui tiene que venir un dialogo para seleccionar nombre del cubo
        maxLevel = self.maxlevel
        parmDlg = GenerationSheetDlg('Parámetros de generación',table,maxLevel)   
        if parmDlg.exec_():
            kname = parmDlg.data[0]
            maxLevel = parmDlg.data[1]
        infox = info2cube(self.dictionary,confName,schema,table,maxLevel)
        if kname != table:
            infox[kname] = infox.pop(table)
        #cubeMgr = CubeBrowserWin(confName,schema,table,self.dictionary,self)
        if self.cubeMgr and not self.cubeMgr.isHidden():
            self.hideCube()
        self.cubeMgr = CubeMgr(self,confName,schema,table,self.dictionary,rawCube=infox,cubeFile=self.cubeFile)
        self.cubeMgr.expandToDepth(1)        
        #if self.configSplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
        self.configSplitter.addWidget(self.cubeMgr)

        self.cubeMgr.show()
        self.cubeMenu.setEnabled(True)
 
 
    def saveCubeFile(self):
        self.cubeMgr.saveCubeFile()
    
    def restoreCubeFile(self):
        self.cubeMgr.restoreConfigFile()
        
    def hideCube(self):
        self.cubeMgr.saveCubeFile()
        self.cubeMgr.hide()
        self.cubeMenu.setEnabled(False)

    def test(self,index):
        return
        print(index.row(),index.column())
        item = self.baseModel.itemFromIndex(index)
        print(item.text(),item.model())

    def refreshTable(self):
        self.baseModel.emitModelReset()

if __name__ == '__main__':

    import sys
    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    app = QApplication(sys.argv)
    parser = generaArgParser()
    args = parser.parse_args()

    window = DanaBrowseWindow(args)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
