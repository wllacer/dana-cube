#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''

from pprint import pprint

   

from dictmgmt.dictTree import *

#from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize

#from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtGui import QStandardItemModel, QStandardItem
#from PyQt5.QtWidgets import QApplication
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          #QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,\
          #QPushButton, QMessageBox, \
          #QTableView

#from datalayer.access_layer import *
#from util.record_functions import norm2String,dict2row, row2dict
from util.jsonmgr import *
from util.decorators import *
#from widgets import WPropertySheet

#from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError, InterfaceError
#from  sqlalchemy.sql import text


class DataDict():
    """
    Argumentos opcionales que recibe DataDict
    defFile. Nombre del fichero de configuracion
    conName  Nombre de la conexion
    confData (connexion Data, como en cubo.connect
    schema
    table
    iters profundidad de navegacion en claves extranjeras
    pos   posicion donde se añade la conexión
    conn  -> conexion viva (nuevo)
    secure conexion obliga a login
    """
    def __init__(self,**kwargs):
        #FIXME eliminar parametros espureos
        defFile= kwargs.get('defFile')
        self.baseModel = None
        self.hiddenRoot  = None  #self.hiddenRoot
        self.configData = None
        self.conn = dict()
        self.isEmpty = False
        
        self._setupModel()
        if 'confData' in kwargs or self._readConfigData(defFile):
            self._cargaModelo(**kwargs)
        else:
            self.isEmpty = True
        
    def model(self):
        return self.baseModel
    
    def close(self):
        for entry in self.conn:
            self.dropConnection(entry)
            
    def getConnByName(self,name):
        for k in range(self.hiddenRoot.rowCount()):
            item = self.hiddenRoot.child(k)
            if item.text() != name:
                continue
            if not isinstance(item,ConnectionTreeItem):
                continue
            return item
            break
        return None
    
    def getConnNr(self,name):
        for k in range(self.hiddenRoot.rowCount()):
            item = self.hiddenRoot.child(k)
            if item.text() != name:
                continue
            if not isinstance(item,ConnectionTreeItem):
                continue
            return k
            break
        return None

    def _setupModel(self):
        """
        definimos el modelo.  
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(5)
        self.hiddenRoot = newModel.invisibleRootItem()
        self.baseModel = newModel #proxyModel
        
    def _readConfigData(self,fileName=None):
        self.configData = load_cubo(getConfigFileName(fileName))
        if self.configData is None or self.configData.get('Conexiones') is None:
            return False
        else:
            return True
        
    def _cargaModelo(self,**kwargs):
        if 'conn' in kwargs:
            self.appendConnection(kwargs.get('conName','$$TEMP'),**kwargs)
            return
        if 'confData' not in kwargs:
            definition = self.configData.get('Conexiones')
        if 'conName' in kwargs:
            self.appendConnection(kwargs.get('conName'),**kwargs)
            return
        for confName in sorted(definition):
            self.appendConnection(confName,**kwargs)  # aqui no tiene sentido filtrar

    def appendConnection(self,confName,**kwargs):

        padre = self.hiddenRoot
        if 'confData' in kwargs:
            conf = kwargs['confData']
            # asi tengo acceso a esos datos aunque sea dinamica
            if not self.configData:
                self.configData = {'Conexiones':{confName:conf}}
            elif 'Conexiones' not in self.confiData:
                self.configData['Conexiones']: {confName:conf}
            else:
                self.configData['Conexiones'][confName] = conf
        else:
            conf = self.configData['Conexiones'].get(confName)
            
        if not conf:
            self.conn[confName] = None
            showConnectionError(confName,'No es posible determinar la configuracion')             
            return 
        
        if kwargs.get('pos') is None:
#        if pos is None:
            pos = padre.rowCount()
        else:
            pos = kwargs.get('pos')
            
        try:
            if 'conn' in kwargs:
                self.conn[confName] = kwargs['conn']
            else:
                if kwargs.get('secure',False) and conf['driver'] not in ('sqlite','QSQLITE'):
                    kconf = {'connect':conf}
                    self.editConnection(kconf,confName)
                    conf = kconf['connect']
                self.conn[confName] = dbConnectAlch(conf)
            conexion = self.conn[confName]
            engine=conexion.engine 
            padre.insertRow(pos,(ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
            curConnection = padre.child(pos)

        #except ( OperationalError, ProgrammingError, InterfaceError,  ) as e:
        except Exception as e:
            self.conn[confName] = None
            informacion = [ str(item) for item in e.orig.args ]
            print(informacion)
            showConnectionError(confName,norm2String(informacion))             
            padre.insertRow(pos,(ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
            curConnection = padre.child(pos)
        
        #if kwargs.get('schema') is not None:
        #curConnection.refresh(kwargs.get('schema')) #ENFRIAR
        curConnection.refresh(**kwargs)
        #else: #probablemente innecesario
            #curConnection.refresh()
    
    @model_change_control()
    def dropConnection(self,confName):
    
        #self.baseModel.beginResetModel()
        # limpio el arbol (podia usar findItem, pero no se, no se ...)
    
        k = self.getConnNr(confName)
        if not k:
            if DEBUG:
                print(confName,' conexion inexistente')
            return
        else:
            self.conn[confName].close()
            self.hiddenRoot.removeRow(k)
        del self.configData['Conexiones'][confName]
        del self.conn[confName]
        #self.baseModel.endResetModel()
        
    def changeConnection(self,padre,confName,conf):
        self.configData['Conexiones'][confName] = conf
        self.updateModel(self,confName)
    
    @model_change_control()
    def updateModel(self,confName=None):
        """
        """
        #self.baseModel.beginResetModel()       
        if confName is None:
            self.baseModel.clear()
            self.hiddenRoot = self.baseModel.invisibleRootItem()
            self._cargaModelo(self.baseModel)
        else:
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
                if not isinstance(item,ConnectionTreeItem):
                    continue
                self.hiddenRoot.removeRow(k)
                pos = k
                break
                    # es un elemento que no estaba en el modelo
            
            self.appendConnection(confName,pos=k)

        #self.baseModel.endResetModel()
    def editConnection(self,configData,nombre=None): 
        
        from PyQt5.QtWidgets import QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox, QPushButton, QMessageBox, QTextEdit

        from util.record_functions import dict2row, row2dict
        from datalayer.conn_dialogs import ConnectionSheetDlg
        
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
        parmDialog = ConnectionSheetDlg('Edite la conexion',context,datos, None)
        if parmDialog.exec_():
            #TODO deberia verificar que se han cambiado los datos
            configData['connect'] = row2dict(datos[1:],attr_list)
            return datos[0]
     
