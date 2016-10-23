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
from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError
from  sqlalchemy.sql import text

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from dictTree import *
from datadict import *
from tablebrowse import *
from cubebrowse import info2cube, CubeMgr

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
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
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
        print('inicializacion completa')
        #CHANGE here
        
        self.queryView = QTableView() #!!!!???? debe ir delante de la definicion de menu
        self.fileMenu = self.menuBar().addMenu("&Conexiones")
        self.fileMenu.addAction("&New ...", self.newConnection, "Ctrl+N")
        self.fileMenu.addAction("&Modify ...", self.modConnection, "Ctrl+M")
        self.fileMenu.addAction("&Delete ...", self.delConnection, "Ctrl+D")        
        self.fileMenu.addAction("&Save Config File", self.saveConfigFile, "Ctrl+S")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        
        
        #self.queryView = QTableView(self)
        self.queryModel = QStandardItemModel()
        self.queryView.setModel(self.queryModel)        

        
        self.querySplitter = QSplitter(Qt.Vertical)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.queryView)
        self.setCentralWidget(self.querySplitter)

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
            #TODO mensaje informativo
            self.close()
            
    def saveConfigFile(self):
        dump_structure(self.configData,getConfigFileName())
    
    def closeEvent(self, event):
        self.close()
        
    def close(self):

        for conid in self.conn:
            if self.conn[conid] is None:
                continue
            if self.conn[conid].closed :
                self.conn[conid].close()
        self.saveConfigFile()

        sys.exit()
        
    #TODO actualizar el arbol tras hacer la edicion   
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
            
        #self.model.beginResetModel()   
        self.dictionary.dropConnection(confName)
        #for item in self.model.findItems(confName,Qt.MatchExactly,0):
            #if type(item) == ConnectionTreeItem:
                #self.model.removeRow(item.row())
                #break
        #self.model.endResetModel()
        #del self.conn[confName]
        #del self.configData['Conexiones'][nombre]

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
            #TODO modificar el arbol, al menos desde ahí
     
        

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
        #self.queryView = QTableView(self)
        #self.queryModel = QStandardItemModel()
        #self.queryView.setModel(self.queryModel)        
        
        self.queryModel.beginResetModel()
        self.queryModel.clear()
        
        info = getTable(self.dictionary,confName,schema,table)
        sqlContext= setLocalQuery(self.dictionary.conn[confName],info,iters)
        sqls = sqlContext['sqls'] 
        cabeceras = [ fld for fld in sqlContext['fields']]
        self.queryModel.setHorizontalHeaderLabels(cabeceras)
        #cursor = getCursor(self.dictionary.conn[confName],sqls,LIMIT=100)
        cursor = getCursor(self.dictionary.conn[confName],sqls)
        for row in cursor:
            modelRow = [ QStandardItem(str(fld)) for fld in row ]
            self.queryModel.appendRow(modelRow)
            
        self.queryModel.endResetModel()
 
        
        self.queryView.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.queryView.customContextMenuRequested.connect(self.openContextMenu)
        #self.queryView.doubleClicked.connect(self.test)
        
        for m in range(self.queryModel.columnCount()):
            self.queryView.resizeColumnToContents(m)
        self.queryView.verticalHeader().hide()
        #self.queryView.setSortingEnabled(True)
        self.queryView.setAlternatingRowColors(True)
        #self.queryView.sortByColumn(0, Qt.AscendingOrder)

        if self.querySplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
            self.querySplitter.addWidget(self.queryView)
        
    @waiting_effects
    def cubebrowse(self,confName,schema,table):
        infox = info2cube(self.dictionary,confName,schema,table)
        #cubeMgr = CubeBrowserWin(confName,schema,table,self.dictionary,self)
        self.cubeMgr = CubeMgr(self,confName,schema,table,self.dictionary)
        self.cubeMgr.expandToDepth(3)
        self.querySplitter.addWidget(self.cubeMgr)
        self.cubeMgr.show()
 
 
    def saveCubeFile(self):
        self.cubeMgr.saveConfigFile()
        
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
