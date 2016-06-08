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
          QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from widgets import WPropertySheet

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError
from  sqlalchemy.sql import text

def getConfigFileName():
            # Configuration file
    name = '.danabrowse.json'
    if os.name == "nt":
        appdir = os.path.expanduser('~/Application Data/Dana')
        if not os.path.isdir(appdir):
            os.mkdir(appdir)
        configFilename = appdir + "/"+name
    else:
        configFilename = os.path.expanduser('~/'+name)
    return configFilename

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

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)


        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        
        #formLayout.addLayout(meatLayout)        
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(382,382))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Connection editor")
        

    def accept(self):
        datos = self.sheet.values()
        if datos[0] == '':
            self.sheet.cellWidget(0,0).setFocus()
            return
        if datos[2] == '':
            self.sheet.cellWidget(2,0).setFocus()
            return
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
        self.setData(self)
        
    def getTypeName(self):
        return self.__class__.__name__ 
    
    def type(self):
        return self.__class__
     
    def getModel(self):
        item = self
        while item is not None and type(item) is not TreeModel:
            item = item.parent
        return item

    def getConnection(self):
        item = self
        while item is not None and type(item) is not ConnectionTreeItem:
            item = item.parent
        return item

    def getSchema(self):
        item = self
        while item is not None and type(item) is not SchemaTreeItem:
            item = item.parent
        return item

    def getTable(self):
        item = self
        while item is not None and type(item) is not TableTreeItem:
            item = item.parent
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
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database_server"))

    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Edit ..."))
        self.menuActions.append(menu.addAction("Delete ..."))
        self.menuActions.append(menu.addAction("Disconnect"))
        self.menuActions.append(menu.addAction("Connect"))
       

    def getContextMenu(self,action):
        if action is not None:
            ind = self.menuActions.index(action)

            if ind == 0 :
                pass  # edit item, save config, refresh tree
            elif ind == 1:
                pass  # close connection, delete tree, delete config
            elif ind == 2:
                pass  # disconnect, delete tree
            elif ind == 3:
                pass  # connect, recreate tree
            elif ind == 5:
                pass

class SchemaTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database"))
    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh"))

    def getContextMenu(self,action):
        if action is not None:
            ind = self.menuActions.index(action)

            if ind == 0 :
                pass  # edit item, save config, refresh tree
       

class TableTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/database_table"))
    def setContextMenu(self,menu):
        self.menuActions = []
        self.menuActions.append(menu.addAction("Properties ..."))
        self.menuActions.append(menu.addAction("Browse Data"))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key"))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key Recursive"))
        self.menuActions.append(menu.addAction("Generate Cube"))

    def getContextMenu(self,action):
        if action is not None:
            ind = self.menuActions.index(action)
            if ind == 0 :
                pass   # show properties sheet
            elif ind == 1:
                pass  #  query 
            elif ind == 2:
                pass  # get fk, query
            elif ind == 3:
                pass # get fk tree, query
            elif ind == 5:
                pass # generate cube


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

def crea_defecto():
    definition = dict()
    definition['Conexiones']= dict()
    definition['Conexiones']['elecciones 2015'] = {'driver':'sqlite','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False }
    definition['Conexiones']['mysql local'] = {'driver':'mysql','dbname': 'fiction',
                'dbhost':'localhost','dbuser':'root','dbpass':'toor','debug':False }
    definition['Conexiones']['pagila pg'] = {'driver':'postgresql','dbname': 'pagila',
                'dbhost':'localhost','dbuser':'werner','dbpass':None,'debug':False } 
    return definition

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        #Leeo la configuracion
        #self.configData = None
        self.configData = load_cubo(getConfigFileName())
        
        if self.configData is None or self.configData.get('Conexiones') is None:
            print('se va al vacio')
            self.configData = dict()
            self.configData['Conexiones']=dict()
            self.editConnection(None)
            if self.configData['Conexiones']:
                dump_structure(self.configData,getConfigFileName())
            else:
                #TODO mensaje informativo
                print('se va de najas')
                self.close()
            #self.configData['Conexiones']=crea_defecto()
            #dump_structure(self.configData,getConfigFileName())
 
        #CHANGE here
        self.fileMenu = self.menuBar().addMenu("&Conexiones")
        self.fileMenu.addAction("&New ...", self.newCube, "Ctrl+N")
        self.fileMenu.addAction("&Modify ...", self.newCube, "Ctrl+M")
        self.fileMenu.addAction("&Delete ...", self.newCube, "Ctrl+D")
        self.fileMenu.addAction("&Save ...", self.saveCube, "Ctrl+S")
        self.fileMenu.addAction("E&xit", self.close, "Ctrl+Q")
        #self.fileMenu = self.menuBar().addMenu("&Opciones")
        #TODO skipped has to be retougth with the new interface
        #self.fileMenu.addAction("&Zoom View ...", self.zoomData, "Ctrl+Z")
        #self.fileMenu.addAction("&Trasponer datos",traspose,"CtrlT")
        #self.fileMenu.addAction("&Presentacion ...",self.setNumberFormat,"Ctrl+F")
        #

        self.vista = None
        self.model = None
        self.cubo =  None
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        self.defineModel()

        #self.view.setSortingEnabled(True)
        #self.view.setRootIsDecorated(False)
        #self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)

        #ALERT
        #self.initCube()
        #self.defineModel()

        
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
   
    def close(self):
        sys.exit()
    def editConnection(self,nombre):
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
            
    def openMenu(self,position):
        print('llame al menu de contexto')
        
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
        menu = QMenu()
        item.setContextMenu(menu)        
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        item.getContextMenu(action)
        
    def test(self,index):
        print(index.row(),index.column())
        item = self.model.itemFromIndex(index)
        print(item.text(),item.model())

            
                
    def getLastChild(self,parent):
        return parent.child(parent.rowCount() -1)
    
    def multischema(self,model):

        definition = self.configData.get('Conexiones')
        conn = dict()
        for confName in definition:
            conf =definition[confName]
            try:
                conn[confName] = dbConnectAlch(conf)
            except OperationalError as e:
                #TODO deberia ampliar la informacion de no conexion
                print(e.orig.args)
                self.hiddenRoot.appendRow((ConnectionTreeItem(confName),QStandardItem('Disconnected')))
                continue
            conexion = conn[confName]
            engine=conexion.engine 
            self.hiddenRoot.appendRow((ConnectionTreeItem(confName),QStandardItem(str(engine))))
            curConnection = self.getLastChild(self.hiddenRoot)
            #curConnection.appendColumn((QStandardItem(str(engine)),))
            inspector = inspect(engine)
            if len(inspector.get_schema_names()) is 0:
                schemata =[None,]
            else:
                schemata=inspector.get_schema_names()  #behaviour with default
            print(engine,inspector.default_schema_name,schemata)
            
            for schema in schemata:
                curConnection.appendRow(SchemaTreeItem(schema))
                curSchema = self.getLastChild(curConnection)
                if schema == inspector.default_schema_name:
                    schema = None
                for table_name in inspector.get_table_names(schema):
                    curSchema.appendRow(TableTreeItem(table_name))
                    curTable = self.getLastChild(curSchema)
                    curTable.appendRow(BaseTreeItem('FIELDS'))
                    curTableFields = self.getLastChild(curTable)
                    curTable.appendRow(BaseTreeItem('FK'))
                    curTableFK = self.getLastChild(curTable)
                    curTable.appendRow(BaseTreeItem('FK_REFERENCE'))
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
                    except OperationalError:
                        print('error operativo en ',schema,table_name)
                        continue

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
                            for item in model.findItems(confName,Qt.MatchExactly,0):
                                iengine = item
                            for item in model.findItems(kschema,Qt.MatchExactly|Qt.MatchRecursive,0):
                                if item.parent() != iengine :
                                    continue
                                ischema = item
                                break
                            kitem = None
                            for item in model.findItems(fk['referred_table'],Qt.MatchExactly|Qt.MatchRecursive,0):
                                if item.parent() != ischema:
                                    continue
                                if item.parent().parent() != iengine :
                                    continue
                                kitem = item
                                break
                              
                            referencer = kitem.child(2)
                            referencer.appendRow((name,table,referred,constrained))
                            
                     except OperationalError:
                        print('error operativo en ',schema,table_name)
                        continue
                     except AttributeError:
                        print(schema,table_name,fk['referred_table'],'casca')
                        continue
            conexion.close()

    def defineModel(self):
        """
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(4)
        
        
        self.hiddenRoot = newModel.invisibleRootItem()
        self.multischema(newModel)        
        #self.view.setModel(newModel)
        #self.modelo=self.view.model
        #proxyModel = QSortFilterProxyModel()
        #proxyModel.setSourceModel(newModel)
        #proxyModel.setSortRole(33)
        self.model = newModel #proxyModel
        self.view.setModel(newModel)
        self.view.resizeColumnToContents(0)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)


        #self.view.expandAll()
        #for m in range(self.model.columnCount(None)):
            #self.view.resizeColumnToContents(m)
        #self.view.collapseAll()
        # estas vueltas para permitir ordenacion
        # para que aparezcan colapsados los indices jerarquicos
        #self.max_row_level = self.vista.dim_row
        #self.max_col_level  = self.vista.dim_col
        #self.row_range = [0, self.vista.row_hdr_idx.count() -1]
        #self.col_range = [0, self.vista.col_hdr_idx.count() -1]



    #def initCube(self):
        ##FIXME casi funciona ... vuelve a leer el fichero cada vez
        #my_cubos = load_cubo()
        ##if 'default' in my_cubos:
            ##if self.cubo is None:
                ##self.autoCarga(my_cubos)
                ##return
            ##del my_cubos['default']

        ##realiza la seleccion del cubo

        #dialog = CuboDlg(my_cubos, self)
        #if dialog.exec_():
            #seleccion = sdialog.cuboCB.currentText())
            #self.cubo = Cubo(my_cubos[seleccion])

            #self.vista = None

        #self.setWindowTitle("Cubo "+ seleccion)
        #self.requestVista()
    def initCube(self):
        return
    def newCube(self):
        return 
    def saveCube(self):
        return

    #def requestVista(self):

        #vistaDlg = VistaDlg(self.cubo, self)

        ##TODO  falta el filtro
        #if self.vista is  None:
            #pass
        #else:
            #vistaDlg.rowCB.setCurrentIndex(self.vista.row_id)
            #vistaDlg.colCB.setCurrentIndex(self.vista.col_id)
            #vistaDlg.agrCB.setCurrentIndex(self.cubo.getFunctions().index(self.vista.agregado))
            #vistaDlg.fldCB.setCurrentIndex(self.cubo.getFields().index(self.vista.campo))

        #if vistaDlg.exec_():
            #row =vistaDlg.rowCB.currentIndex()
            #col = vistaDlg.colCB.currentIndex()
            #agregado = vistaDlg.agrCB.currentText()
            #campo = vistaDlg.fldCB.currentText()

            #app.setOverrideCursor(QCursor(Qt.WaitCursor))
            #if self.vista is None:
                #self.vista = Vista(self.cubo, row, col, agregado, campo)
                #self.defineModel()
            ##else:
                ##self.model.beginResetModel()
                ##self.vista.setNewView(row, col, agregado, campo)
                ##self.vista.toTree2D()
                ##self.model.datos=self.vista
                ##self.model.getHeaders()
                ##self.model.rootItem = self.vista.row_hdr_idx.rootItem
                ##self.model.endResetModel()
                ##self.refreshTable()




            #app.restoreOverrideCursor()

            ## TODO hay que configurar algun tipo de evento para abrirlos y un parametro de configuracion

            ###@waiting_effects
            ##app.setOverrideCursor(QCursor(Qt.WaitCursor))
            ##self.refreshTable()
            ##app.restoreOverrideCursor()


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
