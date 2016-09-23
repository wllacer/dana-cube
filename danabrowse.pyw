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
from  sqlalchemy.exc import CompileError, OperationalError
from  sqlalchemy.sql import text

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from dictTree import *

def setContextMenu(obj,menu):
    if type(obj) == ConnectionTreeItem:
        obj.menuActions = []
        obj.menuActions.append(menu.addAction("Refresh"))
        obj.menuActions.append(menu.addAction("Edit ..."))
        obj.menuActions.append(menu.addAction("Delete"))
        if obj.isOpen():
            obj.menuActions.append(menu.addAction("Disconnect"))
        else:
            obj.menuActions.append(menu.addAction("Connect"))


    elif type(obj) == SchemaTreeItem :
        obj.menuActions = []
        obj.menuActions.append(menu.addAction("Refresh"))


    elif type(obj) == TableTreeItem :
        obj.menuActions = []
        obj.menuActions.append(menu.addAction("Refresh"))
        obj.menuActions.append(menu.addAction("Properties ..."))
        obj.menuActions.append(menu.addAction("Browse Data"))
        obj.menuActions.append(menu.addAction("Browse Data with Foreign Key"))
        obj.menuActions.append(menu.addAction("Browse Data with Foreign Key Recursive"))
        obj.menuActions.append(menu.addAction("Generate Cube"))

    elif type(obj) == BaseTreeItem :
        if obj.text() in ('FK','FK_REFERENCE'):
            obj.menuActions = []
            obj.menuActions.append(menu.addAction("Go to reverse FK"))
            obj.menuActions.append(menu.addAction("Set descriptive fields"))


def getContextMenu(obj,action,exec_object=None):
    if action is None:
        return
    if type(obj) == ConnectionTreeItem:
 
        ind = obj.menuActions.index(action)
                    
        if ind == 0:
            obj.model().beginResetModel()
            obj.refresh()
            obj.model().endResetModel()
        if ind == 1 :
            exec_object.modConnection(obj.text())
            pass  # edit item, save config, refresh tree
        elif ind == 2:
            exec_object.delConnection(obj.text())
            pass  # close connection, delete tree, delete config
        elif ind == 3:
            if obj.isOpen():
                obj.data().close()
                obj.model().beginResetModel()
                obj.deleteChildren()
                #FIXME no podemos poner el icono de momento
                obj.setIcon(QIcon('icons/16/database_lightning.png'))
                obj.setData(None)
                obj.model().endResetModel()
            else:
                exec_object.updateModel(obj.text())

    elif type(obj) == SchemaTreeItem :
 
        ind = obj.menuActions.index(action)

        if ind == 0 :
            obj.model().beginResetModel()
            obj.refresh()
            obj.model().endResetModel()

    elif type(obj) == TableTreeItem :
 
        ind = obj.menuActions.index(action)
        if ind == 0 :
            obj.model().beginResetModel()
            obj.refresh()
            obj.model().endResetModel()
        # show properties sheet
        elif ind == 1:
            pass  #  query 
        elif ind in (2,3,4):
            pprint(obj.getFields(simple=False))
            if ind in (3,4):
                pprint(obj.getFK(simple=False))
        elif ind == 5:
            pass # generate cube

    elif type(obj) == BaseTreeItem :
 
        ind = obj.menuActions.index(action)
        if obj.text() in ('FK','FK_REFERENCE'):
            if ind == 0 :
                pass # get element with same name, selecte that item
            elif ind == 1:
                pass # select field from referred table


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
        except OperationalError as e:
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

        self.setupModel()
        self.readConfigData()
        self.cargaModelo(self.model)
        self.setupView()
        print('inicializacion completa')
        #CHANGE here
        
        self.queryView = QTableView()
        
        self.fileMenu = self.menuBar().addMenu("&Conexiones")
        self.fileMenu.addAction("&New ...", self.newConnection, "Ctrl+N")
        self.fileMenu.addAction("&Modify ...", self.modConnection, "Ctrl+M")
        self.fileMenu.addAction("&Delete ...", self.delConnection, "Ctrl+D")
        self.fileMenu.addAction("&Save Config File", self.saveConfigFile, "Ctrl+S")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        #self.fileMenu = self.menuBar().addMenu("&Opciones")

        
        #self.definitionSplitter = QSplitter(Qt.Vertical)
        #self.definitionSplitter.addWidget(self.view)
##        self.definitionSplitter.addWidget(self.messageView)
        self.querySplitter = QSplitter(Qt.Horizontal)
        #self.querySplitter.addWidget(self.definitionSplitter)
        self.querySplitter.addWidget(self.view)
        self.querySplitter.addWidget(self.queryView)
        self.setCentralWidget(self.querySplitter)

        #self.querySplitter.setStretchFactor(0, 1)
        #self.querySplitter.setStretchFactor(1, 3)
        #self.definitionSplitter.setStretchFactor(0, 1)
        #self.definitionSplitter.setStretchFactor(1, 2)

#        self.setCentralWidget(self.view)
               
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


        #self.view.setSortingEnabled(True)
        #self.view.setRootIsDecorated(False)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)

    def setupModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(5)
        
        
        self.hiddenRoot = newModel.invisibleRootItem()
        #self.multischema(newModel)        
        #self.view.setModel(newModel)
        #self.modelo=self.view.model
        #proxyModel = QSortFilterProxyModel()
        #proxyModel.setSourceModel(newModel)
        #proxyModel.setSortRole(33)
        self.model = newModel #proxyModel

    def readConfigData(self):
        self.configData = load_cubo(getConfigFileName())
        self.conn = dict()        
        if self.configData is None or self.configData.get('Conexiones') is None:
            self.configData = dict()
            self.configData['Conexiones']=dict()
            self.editConnection(None)
            if self.configData['Conexiones']:
                self.saveConfigFile()
            else:
                #TODO mensaje informativo
                self.close()
            #self.configData['Conexiones']=crea_defecto()
            #dump_structure(self.configData,getConfigFileName())
            
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
        self.appendConnection(confName)
        
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
        
    def delConnection(self,nombre=None):
        if nombre is None:
            selDialog = SelectConnectionDlg(self.configData['Conexiones'])
            if selDialog.exec_():
                confName = selDialog.conexion
            else:
                return 
        else:
            confName = nombre
            
        self.model.beginResetModel()   
        for item in self.model.findItems(confName,Qt.MatchExactly,0):
            if type(item) == ConnectionTreeItem:
                self.model.removeRow(item.row())
                break
        self.model.endResetModel()
        del self.conn[nombre]
        del self.configData['Conexiones'][nombre]

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
            #self.updateModel(datos[0])
            #dump_structure(self.configData,getConfigFileName())
     
    def appendConnection(self,pos,confName,conf):
        try:
            self.conn[confName] = dbConnectAlch(conf)
            conexion = self.conn[confName]
            engine=conexion.engine 
            self.hiddenRoot.insertRow(pos,(ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
            curConnection = self.hiddenRoot.child(pos)

        except OperationalError as e:
            #TODO deberia ampliar la informacion de no conexion
            self.conn[confName] = None
            showConnectionError(confName,norm2String(e.orig.args))             
            self.hiddenRoot.insertRow(pos,(ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
            curConnection = self.hiddenRoot.child(pos)
        curConnection.refresh()
        
    def updateModel(self,confName=None):
        """
        """
        self.model.beginResetModel()       
        if confName is None:
            self.model.clear()
            self.hiddenRoot = self.model.invisibleRootItem()
            #self.cargaModelo(self.model)
        else:
            # limpio la tabla de conexiones
            conexion = self.conn.get(confName)
            if conexion is not None:  #conexion nueva
                self.conn[confName].close()
            self.conn[confName] = None
            # limpio el arbol (podia usar findItem, pero no se, no se ...)
            pos = self.hiddenRoot.rowCount()
            for k in range(self.hiddenRoot.rowCount()):
                item = self.hiddenRoot.child(k)
                if item.text() != confName:
                    continue
                if type(item) != ConnectionTreeItem:
                    continue
                self.hiddenRoot.removeRow(k)
                pos = k
                break
                    # es un elemento que no estaba en el modelo
            
            conf =self.configData['Conexiones'][confName]
            self.appendConnection(pos,confName,conf)

        self.model.endResetModel()
        

    def openContextMenu(self,position):
        """
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
        menu = QMenu()
        setContextMenu(item,menu)        
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        getContextMenu(item,action,self)
        
    def test(self,index):
        print(index.row(),index.column())
        item = self.model.itemFromIndex(index)
        print(item.text(),item.model())

    def cargaModelo(self,model):
        definition = self.configData.get('Conexiones')
        self.conn = dict()
        for confName in sorted(definition):
            print('intentando',confName)
            conf =definition[confName]
            self.appendConnection(self.hiddenRoot.rowCount(),confName,conf)

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
