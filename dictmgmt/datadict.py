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
#from widgets import WPropertySheet

#from  sqlalchemy import create_engine,inspect,MetaData, types
#from  sqlalchemy.exc import CompileError, OperationalError
#from  sqlalchemy.sql import text


class DataDict():
    def __init__(self,**kwargs):
        #FIXME eliminar parametros espureos
        defFile= kwargs.get('defFile')
        print('Def File is',defFile)
        self.model = None
        self.hiddenRoot  = None  #self.hiddenRoot
        self.configData = None
        self.conn = dict()
        self.isEmpty = False
        
        self._setupModel()
        if self._readConfigData(defFile):
            self._cargaModelo(**kwargs)
        else:
            self.isEmpty = True
        
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
        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
        """
        newModel = QStandardItemModel()
        newModel.setColumnCount(5)
        self.hiddenRoot = newModel.invisibleRootItem()
        #self.multischema(newModel)        
        #proxyModel = QSortFilterProxyModel()
        #proxyModel.setSourceModel(newModel)
        #proxyModel.setSortRole(33)
        self.model = newModel #proxyModel
        
    def _readConfigData(self,fileName=None):
        self.configData = load_cubo(getConfigFileName(fileName))
        if self.configData is None or self.configData.get('Conexiones') is None:
            return False
        else:
            return True
        
    def _cargaModelo(self,**kwargs):
        definition = self.configData.get('Conexiones')
        if 'conn' in kwargs:
            self.appendConnection(kwargs.get('conn'),**kwargs)
            return
        for confName in sorted(definition):
            self.appendConnection(confName)  # aqui no tiene sentido filtrar

    #TODO probablemente padre sea un parametro inncecesario
    #def appendConnection(self,confName,pos=None):
    def appendConnection(self,confName,**kwargs):
        padre = self.hiddenRoot
        conf = self.configData['Conexiones'].get(confName)
        if kwargs.get('pos') is None:
#        if pos is None:
            pos = padre.rowCount()
        else:
            pos = kwargs.get('pos')
            
        try:
            self.conn[confName] = dbConnectAlch(conf)
            conexion = self.conn[confName]
            engine=conexion.engine 
            padre.insertRow(pos,(ConnectionTreeItem(confName,conexion),QStandardItem(str(engine))))
            curConnection = padre.child(pos)

        except ( OperationalError, ProgrammingError ) as e:
            #TODO deberia ampliar la informacion de no conexion
            self.conn[confName] = None
            showConnectionError(confName,norm2String(e.orig.args))             
            padre.insertRow(pos,(ConnectionTreeItem(confName,None),QStandardItem('Disconnected')))
            curConnection = padre.child(pos)
        
        #if kwargs.get('schema') is not None:
        curConnection.refresh(kwargs.get('schema'))
        #else: #probablemente innecesario
            #curConnection.refresh()
    
    def dropConnection(self,confName):
    
        self.model.beginResetModel()
        # limpio el arbol (podia usar findItem, pero no se, no se ...)
        k = self.getConnNr(confName)
        if not k:
            print(confName,' conexion inexistente')
        else:
            self.hiddenRoot.removeRow(k)
        del self.configData['Conexiones'][confName]
        del self.conn[confName]
        self.model.endResetModel()
        
    def changeConnection(self,padre,confName,conf):
        self.configData['Conexiones'][confName] = conf
        self.updateModel(self,confName)
    
    def updateModel(self,confName=None):
        """
        """
        self.model.beginResetModel()       
        if confName is None:
            self.model.clear()
            self.hiddenRoot = self.model.invisibleRootItem()
            self._cargaModelo(self.model)
        else:
            # codigo nuevo. no funciona por alguna razon misteriosa en los datos
            #conexion = self.getConnByName(confName)
            ##del self.conn[confName]
            #conf = self.configData['Conexiones'][confName]
            #self.conn[confName] = dbConnectAlch(conf)
            #engine=self.conn[confName].engine 
            
            ##conexion.setData(QStandardItem(str(engine)))

            #if not conexion:
                ##TODO gestionar error de conexion no existente
                #print(confName,' conexion inexistente')
                #return
            #conexion.refresh()
            # codigo antiguo, probablemente innecesario
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
                if not isinstance(item,ConnectionTreeItem):
                    continue
                self.hiddenRoot.removeRow(k)
                pos = k
                break
                    # es un elemento que no estaba en el modelo
            
            #conf =self.configData['Conexiones'][confName]
            #aqui la broam era mantener la posicion del elemento y no mandarlo el último
            self.appendConnection(confName,pos=k)

        self.model.endResetModel()

