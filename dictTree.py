#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import os

#from PyQt5.QtCore import Qt,QSortFilterProxyModel, QCoreApplication, QSize
#from PyQt5.QtGui import QCursor, QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMessageBox
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QAbstractItemView, QMenu,\
          #QDialog, QLineEdit,QLabel,QDialogButtonBox, QVBoxLayout, QHBoxLayout, QComboBox, QCheckBox,\
          #QPushButton, QMessageBox, \
          #QTableView

from datalayer.access_layer import *
from util.record_functions import norm2String,dict2row, row2dict
#from util.jsonmgr import *
#from widgets import WPropertySheet

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError
#from  sqlalchemy.sql import text




def showConnectionError(context,detailed_error):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Error en la conexion con {}".format(context))
    #msg.setInformativeText(detailed_error)
    msg.setWindowTitle("Error de Conexion")
    msg.setDetailedText(detailed_error)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()

class BaseTreeItem(QStandardItem):
    def __init__(self, name):
        QStandardItem.__init__(self, name)
        self.setEditable(False)
        self.setColumnCount(1)
        #self.setData(self)
        self.gpi = self.getRow        
        
    def deleteChildren(self):
        if self.hasChildren():
            while self.rowCount() > 0:
                self.removeRow(self.rowCount() -1)
 
    def isAuxiliar(self):
        if self.text() in ('FIELDS','FK','FK_REFERENCE') and self.depth() == 3:
            return True
        else:
            return False
   
    def getBrotherByName(self,name): 
        # getSibling esta cogido para los elementos de la fila, asi que tengo que inventar esto para obtener
        # un 'hermano' por nomnbre
        padre = self.parent()
        for item in padre.listChildren():
            if item.text() != name:
                continue
            else:
                return item
        return None

    def getChildrenByName(self,name): 
        for item in self.listChildren():
            if item.text() != name:
                continue
            else:
                return item
        return None

    def getFullDesc(self):
        fullDesc = [] #let the format be done outside
        if not self.isAuxiliar():
            fullDesc.append(self.text())
        papi = self.parent()
        while papi is not None:
            if not papi.isAuxiliar():
                fullDesc.insert(0,papi.text()) #Ojo insert, o sea al principio
            papi = papi.parent()
        return '.'.join(fullDesc)
 
    def depth(self):
        item = self
        depth = -1 #hay que recordar que todo cuelga de un hiddenRoot
        while item is not None:
            item = item.parent()
            depth +=1
        return depth

    def lastChild(self):
        if self.hasChildren():
            return self.child(self.rowCount() -1)
        else:
            return None
        
    def listChildren(self):
        lista = []
        if self.hasChildren():
            for k in range(self.rowCount()):
                lista.append(self.child(k))
        return lista
     
    def getRow(self,role=None):
        """
          falta el rol
        """
        lista=[]
        indice = self.index() #self.model().indexFromItem(field)
        k = 0
        colind = indice.sibling(indice.row(),k)
        while colind.isValid():
            if role is None:
                lista.append(colind.data()) #print(colind.data())
            else:
                lista.append(colind.data(role))
            k +=1
            colind = indice.sibling(indice.row(),k)
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

    def getTypeText(self):
        if type(self) == ConnectionTreeItem :
            return 'Conn'
        elif type(self) == SchemaTreeItem:
            return 'Schema'
        elif type(self) == TableTreeItem :
            return 'Table'
        else:
            return ''
        
    
    def type(self):
        return self.__class__
     
    def getModel(self):
        """
        probablemente innecesario
        """
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

    #def setContextMenu(self,menu):
        #setContextMenu(self,menu)
    #def getContextMenu(self,action,exec_obj=None):
        #getContextMenu(self,action,exec_obj)

    def __repr__(self):
        return "<" + self.getTypeText() + " " + self.text() + ">"

    
class ConnectionTreeItem(BaseTreeItem):
    def __init__(self, name,connection=None):
        BaseTreeItem.__init__(self, name)
        #FIXME no podemos poner el icono de momento
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
        ##TODO cambiar la columna 
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
            #FIXME no podemos poner el icono de momento
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
        
          

class SchemaTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        #FIXME no podemos poner el icono de momento
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
       

class TableTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        #FIXME no podemos poner el icono de momento
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
                    print('Columna sin tipo',schema,' ',table_name,' ',name)
                    if name and name != '':
                        tipo = BaseTreeItem(typeHandler('TEXT'))
                        curTableFields.appendRow((name,tipo))
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
        
    def getFields(self,simple=False):
        lista = []
        for item in self.listChildren():
            if item.text() != 'FIELDS':
                continue
            else:
                for field in item.listChildren():
                    if simple:
                        lista.append(field.text())
                    else:
                        lista.append(field.getRow())
                break
        return lista

    def getFK(self,simple=False):
        lista = []
        for item in self.listChildren():
            if item.text() != 'FK':
                continue
            else:
                for field in item.listChildren():
                    if simple:
                        lista.append(field.text())
                    else:
                        lista.append(field.getRow())
                break
        return lista

    def getFKref(self,simple=False):
        lista = []
        for item in self.listChildren():
            if item.text() != 'FK_REFERENCE':
                continue
            else:
                for field in item.listChildren():
                    if simple:
                        lista.append(field.text())
                    else:
                        lista.append(field.getRow())
                break
        return lista
       
    def getFullInfo(self):
        """
           De momento no incluyo FKr -- no tengo claro necesitarla
        """
        TableInfo = dict()
        esquema = self.getSchema()
        TableInfo['schemaName'] = nomEsquema = esquema.text()
        TableInfo['tableName'] = self.text()
        TableInfo['Fields']= self.getFields()
        FKs = self.getFK(False)
        if len(FKs) > 0:
            TableInfo['FK']= []
            for idx,asociacion in enumerate(FKs):
                RefInfo = dict()
                RefInfo['Name'] = asociacion[0]
                RefInfo['ParentTable']=asociacion[1]
                RefInfo['Field'] = asociacion[2] # campo en la tabla que nos ocupa
                RefInfo['ParentField'] = asociacion[3]
                esqReferred = esquema
                qualName = asociacion[1].split('.')
                if len(qualName) == 1 :
                    padre = self.getBrotherByName(qualName[0])
                elif qualName[0] == nomEsquema:
                    padre = self.getBrotherByName(qualName[1])
                else:
                    esqReferred = esquema.getBrotherByName(qualName[0])
                    if esqReferred is not None:
                        padre = esqReferred.getChildByName(qualName[1])
                    else:
                        print('Error horroroso en ',self.text(),asociacion)
                        exit()
                camposPadre = padre.getFields()
                for i in range(0,len(camposPadre)):
                    if camposPadre[i][0] == asociacion[3]:
                        del camposPadre[i]
                        break
                RefInfo['CamposReferencia'] = camposPadre
                TableInfo['FK'].append(RefInfo)   
                
        FKRs = self.getFKref(False)
        if len(FKRs) > 0:
            TableInfo['FKR']= []
            for idx,asociacion in enumerate(FKRs):
                RefInfo = dict()
                RefInfo['ChildTable']=asociacion[1]
                RefInfo['Field'] = asociacion[2] # campo en la tabla que nos ocupa
                RefInfo['ChildField'] = asociacion[3]
                esqReferred = esquema
                qualName = asociacion[1].split('.')
                if len(qualName) == 1 :
                    padre = self.getBrotherByName(qualName[0])
                elif qualName[0] == nomEsquema:
                    padre = self.getBrotherByName(qualName[1])
                else:
                    esqReferred = esquema.getBrotherByName(qualName[0])
                    if esqReferred is not None:
                        padre = esqReferred.getChildByName(qualName[1])
                    else:
                        print('Error horroroso en ',self.text(),asociacion)
                        exit()
                camposPadre = padre.getFields()
                for i in range(0,len(camposPadre)):
                    if camposPadre[i][0] == asociacion[3]:
                        del camposPadre[i]
                        break
                RefInfo['CamposReferencia'] = camposPadre
                TableInfo['FKR'].append(RefInfo)

        return TableInfo
                

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

    #def __repr__(self):
        #return "<" + self.__class__.__name__ + " " + self.getName() + ">"

