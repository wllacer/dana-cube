#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.
TODO list:
    Read/Write sql from file (WIP)
    Edit Undo/Redo
    Export results (CSV/Json)
    Read view definitions
    Generate code from definitions
    Commits/Rollbacks 
        DBAPI is in autocommit mode. Must explore sqlalchemy commit logic when autocommit is off. 
        datalayer.query_constructor.queryTransStatus returns query potential transactional statu
    Limit UI
    
    Threads. Conexion a BD y cursor debe estar en un thread distinto (al menos sqlite). No es lo que yo tenia previsto.
            Ademas al menos self.sqlEdit.document() y self.sqlEdit deben ejecutarse en el mismo thread (Qt)
        
    Icon "ribbon". Ultima funcion a implementar
    Data formating Extra points (May BE via sqlparse)
    
@package estimaciones
# 0.3
'''

from pprint import pprint

import datetime
import argparse

#from base.datadict import *    

from PyQt5.QtCore import  Qt,QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QMenu, QComboBox, QLabel, QTableView, QDockWidget, QTextEdit, QListView, QTabWidget, QSplitter, QVBoxLayout, QWidget, QGridLayout, QFileDialog

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError


from support.util.numeros import fmtNumber               
from support.util.jsonmgr import load_cubo,getConfigFileName
from support.util.decorators import waiting_effects 
from support.util.record_functions import norm2String

from support.datalayer.access_layer import SYSTEM_SCHEMAS, getCursorLim
from support.datalayer.query_constructor import queryFormat
from support.datalayer.conn_dialogs import directConnectDlg

import base.config as config

DEFAULT_FORMAT = dict(thousandsseparator=".",
                            decimalmarker=",",
                            decimalplaces=2,
                            rednegatives=False,
                            yellowoutliers=False)

class CursorItemModel(QStandardItemModel):
    def __init__(self,parent=None):
        super(CursorItemModel, self).__init__(parent)
        self.recordStructure = None
        
class CursorItem(QStandardItem):
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        super(CursorItem, self).__init__(*args)
    
    def data(self,role=Qt.UserRole +1):
        '''
        FIXME realmente no se utiliza (recordStructure es nulo y probablemente tampoco role). Por otro lado el codigo no tiene mucho sentido en este caso (copiado de tablebrowse)
        '''
        if self.model() and self.model().recordStructure and role in (Qt.DisplayRole, Qt.TextAlignmentRole):
            index = self.index()
            format = self.model().recordStructure[index.column()]['format']
            if format in ('numerico','entero'):
                if role == Qt.TextAlignmentRole:
                    return Qt.AlignRight| Qt.AlignVCenter
                else:
                    defFmt = DEFAULT_FORMAT.copy()
                    try:
                        if format == 'numerico':
                            defFmt['decimalplaces'] = 2
                        else:
                            defFmt['decimalplaces'] = 0
                        rawData = super(CursorItem,self).data(role)
                        text, sign = fmtNumber(float(rawData),defFmt)
                        return '{}{}'.format(sign,text)
                    except ValueError:
                        if rawData == 'None':
                            return ''
                        else:
                            if config.DEBUG:
                                print ('error de formato en ',
                                self.model().recordStructure[index.column()],index.row(),
                                super(CursorItem,self).data(role))
                            return rawData
            #else:
                #return Qt.AlignLeft| Qt.AlignVCenter
        return super(CursorItem,self).data(role)
    
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

class dictBand(QWidget):
    def __init__(self,conn,holder=None,exclude=True,parent=None):
        super(dictBand,self).__init__(parent)
        
        self.conn = conn
        self.holder = holder
        self.sysExcluded = exclude
        
        self.schemaList = QComboBox()
        self.tableList = QListView()
        self.rowList = QTableView()

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.schemaList,0,0)
        tabSize = 4
        meatLayout.addWidget(self.tableList,1,0,tabSize,1)
        rowSize = 4
        meatLayout.addWidget(self.rowList,2 + tabSize,0,rowSize,1)
        
        self.setLayout(meatLayout)

        self.tableList.clicked.connect(self.changeTable)
        self.schemaList.currentIndexChanged[int].connect(self.changeSchema)
        self.initializeDictDock(self.conn)
   
    @waiting_effects
    def initializeDictDock(self,conn):
        #TODO admite optimizacion
        if conn is None:
            return
        else:
            self.conn = conn
        self.schemaList.clear()
        
        engine = conn.engine
        self.inspector = inspect(engine)
        self.baseSchema = self.inspector.default_schema_name

        schemata = self.getSchemas()
        self.schemaList.addItems(schemata)
        try:
            idx = schemata.index(self.baseSchema)
        except ValueError:
            idx = 0
            self.changeSchema(idx)
        self.schemaList.model().item(idx).setIcon(QIcon("icons/16/dialog-ok-apply"))
        self.schemaList.setCurrentIndex(idx)

       
    def getSchemas(self):

        if len(self.inspector.get_schema_names()) is 0:
            schemata =[None,]
        else:
            #TODO esquemas excluidos
            driver = self.conn.dialect.name
            if self.sysExcluded and driver in SYSTEM_SCHEMAS:                    
                schemata = [schema for schema in self.inspector.get_schema_names() if schema not in SYSTEM_SCHEMAS[driver] ]
            else:
                schemata=self.inspector.get_schema_names()  #behaviour with default
        return schemata

    def getTables(self):
        tableModel = QStandardItemModel()
        list_of_files = self.inspector.get_table_names(self.currentDictSchema)
        for table_name in sorted(list_of_files):
            item = QStandardItem()
            item.setText(table_name)
            item.setIcon(QIcon("icons/16/database_table"))
            tableModel.appendRow(item)
        list_of_views = self.inspector.get_view_names(self.currentDictSchema)
        for view_name in sorted(list_of_views):
            item = QStandardItem()
            item.setText(view_name)
            item.setIcon(QIcon("icons/16/code"))
            tableModel.appendRow(item)
        self.tableList.setModel(tableModel)
        
    def changeSchema(self,idx):
        if idx < 0:
            return
        self.currentDictSchema = self.schemaList.currentText()
        self.getTables()
    
    def changeTable(self,mdlIdx):
        columnModel = QStandardItemModel()
        columnModel.setHorizontalHeaderLabels(('name', 'type', 'nullable', 'default', 'autoincrement'))
        for r,column in enumerate(self.inspector.get_columns(mdlIdx.data(),self.currentDictSchema)):
            columnRow = [ QStandardItem(str(column[fld])) for fld in ('name', 'type', 'nullable', 'default', 'autoincrement')]
            columnModel.appendRow(columnRow)
        self.rowList.setModel(columnModel)
    
class SesionTab(QWidget):
    def __init__(self,conn,confName,holder=None,parent=None):
        super(SesionTab,self).__init__(parent)
        self.conn = conn
        self.confName = confName
        self.holder = holder
        self.tabQueries = QTabWidget()
        self.tabQueries.setTabShape(QTabWidget.Triangular)
        meatLayout = QVBoxLayout()
        meatLayout.addWidget(self.tabQueries)
        self.setLayout(meatLayout)
        
        self.addQuery()
        
    def addQuery(self):
        self.tabQueries.addTab(QueryTab(self.conn,self.confName,holder=self.holder),"{}:{}".format(self.confName, self.tabQueries.count() +1))
        self.tabQueries.setCurrentIndex(self.tabQueries.count() -1)

    def openQuery(self):
        #self.tabQueries.addTab(QueryTab(self.conn,self.confName,holder=self.holder),"{}:{}".format(self.confName, #self.tabQueries.count() +1))
        #self.tabQueries.setCurrentIndex(self.tabQueries.count() -1)
        self.tabQueries.currentWidget().readQuery()
        
    def saveQuery(self):
        self.tabQueries.currentWidget().writeQuery()
    def saveAsQuery(self):
        self.tabQueries.currentWidget().writeQuery(True)
        
    def closeQuery(self):
        tabId = self.tabQueries.currentIndex()
        self.tabQueries.removeTab(tabId)

    def execute(self):
        self.tabQueries.currentWidget().execute()
    def reformat(self):
        self.tabQueries.currentWidget().reformat()
    
class QueryTab(QWidget):
    def __init__(self,conn,confName,holder=None,parent=None):
        super(QueryTab,self).__init__(parent)
        self.conn = conn
        self.holder = holder
        self.fileName = None
        self.browser = QTableView()
        self.browser.setSortingEnabled(True)  
        self.browser.setAlternatingRowColors(True)

        self.sqlEdit = QTextEdit()
        self.msgLine = QTextEdit()
        self.msgLine.setReadOnly(True)
        self.msgLine.setText("Bienvenido al query masta")
        
        split = QSplitter(Qt.Vertical)
        split.addWidget(self.sqlEdit)
        split.addWidget(self.browser)
        split.addWidget(self.msgLine)
        split.setSizes([50,250,25])
        #split.setRubberBand(1)
        
        meatLayout = QVBoxLayout()
        meatLayout.addWidget(split)
        self.setLayout(meatLayout)

    @waiting_effects
    def execute(self):
        sqlString = self.sqlEdit.document().toPlainText()
        if len(sqlString) == 0:
            return 
        cursor = None

        self.msgLine.hide()
        self.msgLine.setText('')
        try:
            #TODO opcion para poner un limit
            cursor = getCursorLim(self.conn,sqlString,LIMIT=1000)
        except Exception as e:
            if cursor is not None:
                cursor.close()
            self.msgLine.show()
            self.msgLine.setText(norm2String(e.orig.args))
            return
            
        self.baseModel = CursorItemModel()
        self.baseModel.setHorizontalHeaderLabels(cursor.keys())
        for row in cursor:
            modelRow = [ CursorItem(str(fld)) for fld in row ]
            self.baseModel.appendRow(modelRow)
        self.browser.setModel(self.baseModel)
        cursor.close() #INNECESARIO pero recomendable

    def readQuery(self):
        #TODO y el contenido actual del script ?
        if self.fileName is not None and self.sqlEdit.document().isModified():
            #dialogo de confirmar el salvado de los datos
             pass
        filename,filter = QFileDialog.getOpenFileName(self,
                                                  caption="Nombre del fichero de comandos a editar",
                                                  directory="script",
                                                  filter = "sql (*.sql);; All files (*)",
                                                  initialFilter="sql (*.sql)",
                                                  )
        if filename:
            with open(filename,"r") as file:
                self.sqlEdit.document().setPlainText(file.read())
                self.sqlEdit.document().setModified(False)
            self.fileName = filename
            #FIXME fugly
            pos = self.holder.tabSesiones.currentWidget().tabQueries.currentIndex()
            self.holder.tabSesiones.currentWidget().tabQueries.setTabText(pos,filename)
            
    def writeQuery(self,saveAs=False):
        if not self.sqlEdit.document().isModified():
            return
        if self.fileName is None:
            filename,filter = QFileDialog.getSaveFileName(self,
                                                    caption="Salvar el script como",
                                                    directory="script",
                                                    filter = "sql (*.sql);; All files (*)",
                                                    initialFilter="sql (*.sql)",
                                                    )
            if filename:
                pass
            else:
                return

        elif saveAs:
            filename,filter = QFileDialog.getSaveFileName(self,"Save as",self.fileName)
            if filename:
                pass
            else:
                return
        else:
            filename = self.fileName
        with open(self.fileName,"w") as file:
            file.write(self.sqlEdit.document().toPlainText())
            
        if self.fileName is None or saveAs is True:
            self.fileName = filename
            #FIXME fugly
            pos = self.holder.tabSesiones.currentWidget().tabQueries.currentIndex()
            self.holder.tabSesiones.currentWidget().tabQueries.setTabText(pos,filename)
    
        self.sqlEdit.document().setModified(False)
    def reformat(self):
        sqlString = self.sqlEdit.document().toPlainText()
        self.sqlEdit.setText(queryFormat(sqlString))
  
    def close(self):
        #TODO salvar si es fichero
        if self.fileName is not None:
            pass
        self.conn.close()
        super().close()
        
class EditWindow(QMainWindow):
    def __init__(self): #conn,confName):
        super(EditWindow,self).__init__()

        parser = generaArgParser()
        args = parser.parse_args()
        #Leeo la configuracion
        self.configFile = args.configFile
        #self.secure = args.secure
        #cubeFile = args.cubeFile
        self.sysExclude = args.sysExclude
        
        #self.conn = conn
        self.setWindowTitle("Consultas a bases de datos" )
        #self.setupEditWindow()
        self.setupMultiEdit()
        
    def setupMultiEdit(self):


        self.tabSesiones = QTabWidget()
        self.addSesion()
        firstconn = self.tabSesiones.currentWidget().conn
        self.setCentralWidget(self.tabSesiones)
        
        self.tabSesiones.currentChanged[int].connect(self.sesionChanges)
        self.addDockWidget(Qt.RightDockWidgetArea, self.createDictionaryDocket(firstconn))

        self.sesionMenu = self.menuBar().addMenu("Sesiones")
        self.sesionMenu.addAction("&Nueva Sesion",self.addSesion,"Ctrl+N")
        self.sesionMenu.addAction("&Cerrar Actual",self.closeSesion,"Ctrl+C")

        self.queryMenu = self.menuBar().addMenu("Queries")
        self.queryMenu.addAction("&Nueva consulta",self.addQuery,"Alt+N")
        self.queryMenu.addAction("&Abrir query guardada",self.openQuery,"Alt+O")
        self.queryMenu.addAction("Guardar query",self.saveQuery,"Alt+S")
        self.queryMenu.addAction("Guardar query como",self.saveAsQuery,"Alt+S")
        self.queryMenu.addAction("&Cerrar consulta",self.closeQuery,"Alt+C")
        self.queryMenu.addSeparator()
        self.queryMenu.addAction("&Ejecutar", self.queryExecute, "Alt+X")
        self.queryMenu.addAction("re&Format", self.queryReformat, "Alt+R")        
    
    def addSesion(self):
        conn,confName,confInfo = selector(self.configFile)
        if conn is None:
            return None
        self.tabSesiones.addTab(SesionTab(conn,confName,holder=self),confName)
        self.tabSesiones.setCurrentIndex(self.tabSesiones.count() -1)
    
    def closeSesion(self):
        tabId = self.tabSesiones.currentIndex()
        self.tabSesiones.currentWidget().conn.close()
        self.tabSesiones.removeTab(tabId)

    def addQuery(self):
        self.tabSesiones.currentWidget().addQuery()
    def openQuery(self):
        self.tabSesiones.currentWidget().openQuery()
    def saveQuery(self):
        self.tabSesiones.currentWidget().saveQuery()
    def saveAsQuery(self):
        self.tabSesiones.currentWidget().saveAsQuery()

    def closeQuery(self):
        self.tabSesiones.currentWidget().closeQuery()
    
    def queryExecute(self):
        self.tabSesiones.currentWidget().execute()
    def queryReformat(self):
        self.tabSesiones.currentWidget().reformat()

    def sesionChanges(self,idx):
        currentWidget = self.tabSesiones.currentWidget()   #.tree
        if currentWidget is None:
            return
        self.dictDock.widget().initializeDictDock(currentWidget.conn)
                
    def createDictionaryDocket(self,conn,area=Qt.RightDockWidgetArea):
        self.dictDock = QDockWidget()
        self.dictDock.setAllowedAreas(area)
        self.dictDock.setWidget(dictBand(conn,holder=self,exclude=self.sysExclude))
        return self.dictDock
            
def selector(configFile):
    configData = load_cubo(getConfigFileName(configFile))
    if configData is None or configData.get('Conexiones') is None:
        sys.exit()

    form = directConnectDlg(configData)
    form.show()
    if form.exec_():
        return form.conn,form.confName,form.confInfo
    else:
        return None,None,None
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    #conn,confName,confInfo = selector()
    #if conn is None:
        #sys.exit()
    window = EditWindow()#conn,confName)
    #window = multiEdit(conn,confName)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
