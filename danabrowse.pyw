#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import os

from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize
from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,\
          QPushButton, QMessageBox, \
          QTableView

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError
from  sqlalchemy.sql import text

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from dictmgmt.dictTree import *
from dictmgmt.datadict import *

from tablebrowse import *
from cubebrowse import info2cube, CubeMgr

DEBUG = True
def waiting_effects(function):
    """
      decorator from http://stackoverflow.com/questions/8218900/how-can-i-change-the-cursor-shape-with-pyqt
      para poner el cursor en busy/libre al ejectuar una funcion que va a tardar
      
      TODO unificar en un solo sitio
      
    """
    def new_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise e
            QMessageBox.warning(self,
                            "Warning",
                            "Error {}".format(e.args[0]))
            if DEBUG:
                print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()
    return new_function


class SelectConnectionDlg(QDialog):
    def __init__(self,configDict,parent=None):
        super(SelectConnectionDlg,self).__init__(parent)
        if 'Conexiones' in configDict:
            ambito = configDict['Conexiones']
        else:
            ambito = configDict
        self.listConnections = [ name for name in ambito]
        self.conexion = None
        
        self.etiqueta = QLabel("Eliga una conexion")
        self.lista = QComboBox()
        self.lista.addItems(self.listConnections)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)       
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        meatLayout.addWidget(self.etiqueta)
        meatLayout.addWidget(self.lista)
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
 
        self.setLayout(meatLayout)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def accept(self):
        self.conexion = self.lista.currentText()
        QDialog.accept(self)
        
        
class ConnectionSheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
    """
    def __init__(self,title,context,data,parent=None):   
        super(ConnectionSheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(context,data)
       
        actionButton = QPushButton('Test')
        actionButton.setDefault(True)
        
        

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)
        buttonBox.addButton(actionButton,QDialogButtonBox.ActionRole)

        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)
        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
        #formLayout.addLayout(meatLayout)        
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(382,382))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        actionButton.clicked.connect(self.test)
        
        self.setWindowTitle("Connection editor")
      
    def validate(self):
        datos = self.sheet.values()
        if datos[0] == '':
            self.sheet.cellWidget(0,0).setFocus()
            self.msgLine.setText('Nombre es Obligatorio')
            return None
        if datos[2] == '':
            self.sheet.cellWidget(2,0).setFocus()
            self.msgLine.setText('Base de datos es Obligatorio')
            return None
        self.msgLine.clear()
        return datos
    
    def test(self):       
        self.msgLine.clear()
        attr_list =  ('driver','dbname','dbhost','dbuser','dbpass','dbport','debug')
        datos = self.validate()
        if datos is None:
            return
        datos[1]=DRIVERS[datos[1]]
        conf = row2dict(datos[1:],attr_list)
        try:
            if conf['driver'] == 'sqlite':
                if not os.path.isfile(datos[2]):
                    self.msgLine.setText('Fichero {} no existe'.format(datos[2]))
                    return
            else:
                conn = dbConnectAlch(conf)
                conn.close()
        except ( OperationalError, ProgrammingError)  as e:
            showConnectionError(datos[0],norm2String(e.orig.args))
            self.msgLine.setText('Error en la conexión')
            return
        self.msgLine.setText('Conexión validada correctamente')
        
    def accept(self):
        datos = self.validate()
        if datos is None:
            return
        self.msgLine.clear()
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.data[k] = valor
        QDialog.accept(self)

    
def showConnectionError(context,detailed_error):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Error en la conexion con {}".format(context))
    #msg.setInformativeText(detailed_error)
    msg.setWindowTitle("Error de Conexion")
    msg.setDetailedText(detailed_error)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #Leeo la configuracion


        self.dictionary = DataDict()
        #TODO variables asociadas del diccionario. Reevaluar al limpiar
        self.model = self.dictionary.model
        self.configData = self.dictionary.configData
        self.conn = self.dictionary.conn
        if self.dictionary.isEmpty:
            self.newConfigData()
            self.dictionary._cargaModelo(self.dictionary.model)
        self.setupView()
        self.cubeMgr = None # necesito mas adelante que este definida
        if DEBUG:
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
        
        self.queryModel = self.queryView.model

        self.querySplitter = QSplitter(Qt.Vertical)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.queryView)

        self.configSplitter = QSplitter(Qt.Horizontal)
        self.configSplitter.addWidget(self.querySplitter)
        
        self.setCentralWidget(self.configSplitter)

        self.setWindowTitle("Visualizador de base de datos")
        
    def setupView(self):
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        self.view.resizeColumnToContents(0)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)


        self.view.expandAll()
        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.collapseAll()
        self.view.setHeaderHidden(True)
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
            self.dictionary._cargaModelo(self.dictionary.model)
        else:
            QMessageBox.critical(self,
                                "Error Fatal",
                                "No se ha encontrado una conexión valida.\nFin de proceso")
            self.close()
            
    def saveConfigFile(self):
        dump_structure(self.configData,getConfigFileName())
    
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
     
        

    def openContextMenu(self,position):
        """
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
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
        
    @waiting_effects
    def cubebrowse(self,confName,schema,table):
        infox = info2cube(self.dictionary,confName,schema,table)
        #cubeMgr = CubeBrowserWin(confName,schema,table,self.dictionary,self)
        if self.cubeMgr and not self.cubeMgr.isHidden():
            self.hideCube()
        self.cubeMgr = CubeMgr(self,confName,schema,table,self.dictionary)
        self.cubeMgr.expandToDepth(3)        
        #if self.configSplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
        self.configSplitter.addWidget(self.cubeMgr)

        self.cubeMgr.show()
        self.cubeMenu.setEnabled(True)
 
 
    def saveCubeFile(self):
        self.cubeMgr.saveConfigFile()
    
    def restoreCubeFile(self):
        self.cubeMgr.restoreConfigFile()
        
    def hideCube(self):
        self.cubeMgr.saveConfigFile()
        self.cubeMgr.hide()
        self.cubeMenu.setEnabled(False)

    def test(self,index):
        return
        print(index.row(),index.column())
        item = self.model.itemFromIndex(index)
        print(item.text(),item.model())

    def refreshTable(self):
        self.model.emitModelReset()

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
