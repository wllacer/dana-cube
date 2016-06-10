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
          QPushButton, QMessageBox

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError
from  sqlalchemy.sql import text


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

class BaseTreeItem(QStandardItem):
    def __init__(self, name):
        QStandardItem.__init__(self, name)
        self.setEditable(False)
        self.setColumnCount(1)
        #self.setData(self)
        
    def deleteChildren(self):
        if self.hasChildren():
            while self.rowCount() > 0:
                self.removeRow(self.rowCount() -1)
                
    def lastChild(self):
        if self.hasChildren():
            return self.child(self.rowCount() -1)
        else:
            return None
        
    def listChildren(self):
        if self.hasChildren():
            lista = []
            for k in range(self.rowCount()):
                lista.append(self.child(k))
        else:
            lista = None
        return lista
     
    def takeChildren(self):
        if self.hasChildren():
            lista = []
            for k in range(self.rowCount()):
                lista.append(self.takeItem(k))
        else:
            lista = None
        return lista
    
    def getTypeName(self):
        return self.__class__.__name__ 
    
    def type(self):
        return self.__class__
     
    def getModel(self):
        item = self
        while item is not None and type(item) is not TreeModel:
            item = item.parent()
        return item

    def getConnection(self):
        item = self
        while item is not None and type(item) is not ConnectionTreeItem:
            item = item.parent()
        return item

    def getSchema(self):
        item = self
        while item is not None and type(item) is not SchemaTreeItem:
            item = item.parent()
        return item

    def getTable(self):
        item = self
        while item is not None and type(item) is not TableTreeItem:
            item = item.parent()
        return item

    def setContextMenu(self,menu):
        if self.text() in ('FK','FK_REFERENCE'):
            self.menuActions = []
            self.menuActions.append(menu.addAction("Go to reverse FK"))
            self.menuActions.append(menu.addAction("Set descriptive fields"))

    def getContextMenu(self,action):
        if action is not None:
            ind = self.menuActions.index(action)
            if self.text() in ('FK','FK_REFERENCE'):
                if ind == 0 :
                    pass # get element with same name, selecte that item
                elif ind == 1:
                    pass # select field from referred table

    
class ConnectionTreeItem(BaseTreeItem):
    def __init__(self, name,connection=None):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database_server"))
        if connection is not None:
            self.setData(connection)
        #else:
            #self.setData(None)

    def findElement(self,schema,table):
        ischema = None
        for item in self.model().findItems(schema,Qt.MatchExactly|Qt.MatchRecursive,0):
            if type(item) != SchemaTreeItem:
                continue
            if item.parent() != self :
                continue
            ischema = item
            break
        
        if ischema is None:
            print ('Esquema {} no encontrado'.format(schema))
            return None
        
        kitem = None
        for item in self.model().findItems(table,Qt.MatchExactly|Qt.MatchRecursive,0):
            if type(item) != TableTreeItem :
                continue
            if item.parent() != ischema:
                continue
            if item.parent().parent() != self :
                continue
            kitem = item
            break
        
        if kitem is None:
            print ('Tabla {}.{} no encontrado'.format(schema,table))
            return None
        
        return kitem
    
    def FK_hierarchy(self,inspector,schemata):
        for schema in schemata:
            for table_name in inspector.get_table_names(schema):
                try:
                    for fk in inspector.get_foreign_keys(table_name,schema):
                        ref_schema = fk.get('referred_schema',inspector.default_schema_name)
                        ref_table  = fk['referred_table']
                        if schema is not None:
                            table = BaseTreeItem(schema +'.'+ table_name)
                        else:
                            table = BaseTreeItem(table_name)
                        if fk['name'] is None:
                            name = BaseTreeItem(table_name+'2'+fk['referred_table']+'*')
                        else:
                            name = BaseTreeItem(fk['name'])
                            
                        constrained = BaseTreeItem(norm2String(fk['constrained_columns']))
                        referred    = BaseTreeItem(norm2String(fk['referred_columns']))
                        
                        kschema = fk.get('referred_schema','')
                        
                        kitem = self.findElement(fk.get('referred_schema',''),ref_table)
                        if kitem is not None:
                            referencer = kitem.child(2)
                            referencer.appendRow((name,table,referred,constrained))
                        
                except OperationalError:
                    print('error operativo en ',schema,table_name)
                    continue
                except AttributeError:
                    print(schema,table_name,fk['referred_table'],'casca')
                    continue
                
    def refresh(self):
        #TODO cambiar la columna 0
        #TODO de desconectada a conectada
        self.deleteChildren()
        if self.isOpen():
            engine = self.getConnection().data().engine
            inspector = inspect(engine)
            
            if len(inspector.get_schema_names()) is 0:
                schemata =[None,]
            else:
                schemata=inspector.get_schema_names()  #behaviour with default
            
            for schema in schemata:
                self.appendRow(SchemaTreeItem(schema))
                curSchema = self.lastChild()
                curSchema.refresh()
                
            self.FK_hierarchy(inspector,schemata)
            
        else:
            # error mesg
            self.setIcon(QIcon('icons/16/database_lightning.png'))
            self.setData(None)


    def isOpen(self):
        if type(self.data()) is ConnectionTreeItem:
            return False
        if self.data() is None or self.data().closed:
            return False
        else:
            #TODO deberia verificar que de verdad lo esta
            return True
        
    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh"))
        self.menuActions.append(menu.addAction("Edit ..."))
        self.menuActions.append(menu.addAction("Delete"))
        if self.isOpen():
            self.menuActions.append(menu.addAction("Disconnect"))
        else:
            self.menuActions.append(menu.addAction("Connect"))
        
    def getContextMenu(self,action,exec_object=None):
        if action is not None:
            ind = self.menuActions.index(action)
                       
            if ind == 0:
                self.model().beginResetModel()
                self.refresh()
                self.model().endResetModel()
            if ind == 1 :
                exec_object.editConnection(self.text())
                pass  # edit item, save config, refresh tree
            elif ind == 2:
                exec_object.delConnection(self.text())
                pass  # close connection, delete tree, delete config
            elif ind == 3:
                if isOpen():
                    self.data().close()
                    self.model().beginResetModel()
                    self.deleteChildren()
                    self.setData(None)
                    self.model().endResetModel()
                else:
                    pass  # disconnect, delete tree
          

class SchemaTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database"))
        
    def refresh(self):
        self.deleteChildren()
        engine = self.getConnection().data().engine
        inspector = inspect(engine)
        schema = self.text() if self.text() != '' else None
        if schema == inspector.default_schema_name:
            schema = None
        for table_name in inspector.get_table_names(schema):
            self.appendRow(TableTreeItem(table_name))
            curTable = self.lastChild()
            curTable.refresh()
        # fk reference
    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh"))

    def getContextMenu(self,action,exec_object=None):
        if action is not None:
            ind = self.menuActions.index(action)

            if ind == 0 :
                self.model().beginResetModel()
                self.refresh()
                self.model().endResetModel()

       

class TableTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database_table"))
        
    def refresh(self):
        self.deleteChildren()
        self.appendRow(BaseTreeItem('FIELDS'))
        curTableFields = self.lastChild()
        self.appendRow(BaseTreeItem('FK'))
        curTableFK = self.lastChild()
        self.appendRow(BaseTreeItem('FK_REFERENCE'))
        #faltan las FK de vuelta
        engine = self.getConnection().data().engine
        inspector = inspect(engine)
        table_name = self.text()
        schema = self.getSchema().text()
        if schema == '':
            schema = None
        try:
            #print('\t',schema,table_name)
            for column in inspector.get_columns(table_name,schema):
                try:
                    name = BaseTreeItem(column['name'])
                    tipo = BaseTreeItem(typeHandler(column.get('type','TEXT')))
                    curTableFields.appendRow((name,tipo))
                except CompileError: 
                #except CompileError:
                    print('Columna sin tipo')
            for fk in inspector.get_foreign_keys(table_name,schema):
                if fk['name'] is None:
                    name = BaseTreeItem(table_name+'2'+fk['referred_table']+'*')
                else:
                    name = BaseTreeItem(fk['name'])
                if fk['referred_schema'] is not None:
                    table = BaseTreeItem(fk['referred_schema']+'.'+fk['referred_table'])
                else:
                    table = BaseTreeItem(fk['referred_table'])
                constrained = BaseTreeItem(norm2String(fk['constrained_columns']))
                referred    = BaseTreeItem(norm2String(fk['referred_columns']))
                curTableFK.appendRow((name,table,constrained,referred))                         
        except OperationalError as e:
            showConnectionError('Error en {}.{}'.format(schema,table_name),norm2String(e.orig.args))
        

        
    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh"))
        self.menuActions.append(menu.addAction("Properties ..."))
        self.menuActions.append(menu.addAction("Browse Data"))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key"))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key Recursive"))
        self.menuActions.append(menu.addAction("Generate Cube"))

    def getContextMenu(self,action,exec_object=None):
        if action is not None:
            ind = self.menuActions.index(action)
            if ind == 0 :
                self.model().beginResetModel()
                self.refresh()
                self.model().endResetModel()
            # show properties sheet
            elif ind == 1:
                pass  #  query 
            elif ind == 2:
                pass  # get fk, query
            elif ind == 3:
                pass # get fk tree, query
            elif ind == 5:
                pass # generate cube
            elif ind == 6:
                pass


    #def getConnectionItem(self):
        #item = self
        #while item is not None and type(item) is not ConnectionTreeItem:
            #item = item.parent()
        #return item

    #def getConnection(self):
        #item = self.getConnectionItem()
        #return item.connection if type(item) is ConnectionTreeItem else None

    #def open(self):
        #self.refresh()

    #def refresh(self):
        #self.setRowCount(0)

    def __repr__(self):
        return "<" + self.__class__.__name__ + " " + self.getName() + ">"


def typeHandler(type):
    if  isinstance(type,(types.Numeric,types.Integer,types.BigInteger)):
          return 'numerico'
    elif isinstance(type,types.String):
          return 'texto'
    elif isinstance(type,(types._Binary,types.LargeBinary)):
          return 'binario'
    elif isinstance(type,types.Boolean):
          return 'booleano'
    elif isinstance(type,(types.Date,types.DateTime)):
          return 'fecha'
    elif isinstance(type,types.Time):
          return 'hora'
    else:
          # print('Tipo {} no contemplado'.format(type))
          return '{}'.format(type)
    return None

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
        self.multischema(self.model)
        self.setupView()
        #CHANGE here
        
        self.fileMenu = self.menuBar().addMenu("&Conexiones")
        self.fileMenu.addAction("&New ...", self.newConnection, "Ctrl+N")
        self.fileMenu.addAction("&Modify ...", self.modConnection, "Ctrl+M")
        self.fileMenu.addAction("&Delete ...", self.delConnection, "Ctrl+D")
        self.fileMenu.addAction("&Save Config File", self.saveConfigFile, "Ctrl+S")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        #self.fileMenu = self.menuBar().addMenu("&Opciones")

        
        self.definitionSplitter = QSplitter(Qt.Vertical)
        self.definitionSplitter.addWidget(self.view)
#        self.definitionSplitter.addWidget(self.messageView)
        self.querySplitter = QSplitter(Qt.Horizontal)
#        self.querySplitter.addWidget(self.groupsList)
#        self.querySplitter.addWidget(self.definitionSplitter)
        self.setCentralWidget(self.definitionSplitter)

        self.querySplitter.setStretchFactor(0, 1)
        self.querySplitter.setStretchFactor(1, 3)
        self.definitionSplitter.setStretchFactor(0, 1)
        self.definitionSplitter.setStretchFactor(1, 2)

#        self.setCentralWidget(self.view)
               
        self.setWindowTitle("Visualizador de base de datos")
        
    def setupView(self):
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        self.view.setModel(self.model)
        self.view.resizeColumnToContents(0)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)


        self.view.expandAll()
        #for m in range(self.model.columnCount(None)):
            #self.view.resizeColumnToContents(m)
        #self.view.collapseAll()


        #self.view.setSortingEnabled(True)
        #self.view.setRootIsDecorated(False)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)

    def setupModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(4)
        
        
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
            if conid is not None and not self.conn[conid].closed :
                self.conn[conid].close()
        self.saveConfigFile()
        sys.exit()
        
    #TODO actualizar el arbol tras hacer la edicion   
    def newConnection(self):
        self.editConnection(None)
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
            #TODO modificar el arbol, al menos desde ahí
            self.updateModel(datos[0])
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
        # es un poco bestia pero para trabajar vale
        self.model.beginResetModel()       
        if confName is None:
            self.model.clear()
            self.hiddenRoot = self.model.invisibleRootItem()
#            self.multischema(self.model)
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
                if item != ConnectionTreeItem:
                    continue
                self.hiddenRoot.removeRow(k)
                pos = k
                break
                    # es un elemento que no estaba en el modelo
            
            conf =self.configData['Conexiones'][confName]
            self.appendConnection(pos,confName,conf)
            #try:
                #self.conn[confName] = dbConnectAlch(conf)
                #conexion = self.conn[confName]
                #engine=conexion.engine 
                #self.hiddenRoot.insertRow(pos,(ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
                #curConnection = self.hiddenRoot.child(pos)
    
            #except OperationalError as e:
                ##TODO deberia ampliar la informacion de no conexion
                #self.conn[confName] = None
                #showConnectionError(confName,norm2String(e.orig.args))             
                #self.hiddenRoot.insertRow(pos,(ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
                #curConnection = self.hiddenRoot.child(pos)
            #curConnection.refresh()

        self.model.endResetModel()
        

    def openMenu(self,position):
        print('llame al menu de contexto')
        
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
        menu = QMenu()
        item.setContextMenu(menu)        
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        item.getContextMenu(action,self)
        
    def test(self,index):
        print(index.row(),index.column())
        item = self.model.itemFromIndex(index)
        print(item.text(),item.model())

            
                
    def getLastChild(self,parent):
        if parent == self.hiddenRoot:
            return parent.child(parent.rowCount() -1)
        else:
            return parent.lastChild()
    
        
    def multischema(self,model):
        definition = self.configData.get('Conexiones')
        self.conn = dict()
        for confName in sorted(definition):
            print('intentando',confName)
            conf =definition[confName]
            self.appendConnection(self.hiddenRoot.rowCount(),confName,conf)
            #try:
                #self.conn[confName] = dbConnectAlch(conf)
                #conexion = self.conn[confName]
                #engine=conexion.engine 
                #self.hiddenRoot.appendRow((ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
                #curConnection = self.getLastChild(self.hiddenRoot)
     
            #except OperationalError as e:
                ##TODO deberia ampliar la informacion de no conexion
                #self.conn[confName] = None
                #showConnectionError(confName,norm2String(e.orig.args))             
                #self.hiddenRoot.appendRow((ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
                #curConnection = self.getLastChild(self.hiddenRoot)
            #if self.conn[confName] is not None:
                #curConnection.refresh()





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
