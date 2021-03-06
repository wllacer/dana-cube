#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
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

from support.datalayer.access_layer import *
from support.datalayer.query_constructor import queryFormat
#from admin.cubebrowse import *
from support.util.record_functions import norm2String,dict2row, row2dict
from support.util.decorators import *
#from support.util.jsonmgr import *
#from support.gui.widgets import WPropertySheet

from  sqlalchemy import create_engine,inspect,MetaData, types
from  sqlalchemy.exc import CompileError, OperationalError, ProgrammingError, InterfaceError
#from  sqlalchemy.sql import text

import base.config as config


def showConnectionError(context,detailed_error,title="Error de Conexion"):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Error en {}".format(context))
    #msg.setInformativeText(detailed_error)
    msg.setWindowTitle(title)
    msg.setDetailedText(detailed_error)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()

def arbol(fileSet,inspector, schema,table,maxiters,parentIter):
    """
        funcion recursiva utilizada para obtener el set (fileSet) de tablas que deben formar parte 
        del diccionario en el caso que lo pidamos centrado en una sola tabla
    """
    try:
        fks =  inspector.get_foreign_keys(table,schema)
    except:
        print('Tabla {}.{} no puede ser consultada'.format(schema,table))
        return
    fileSet.add('{}.{}'.format(schema,table) )
    # el control de iteracion se hace aqui porque maxiters 0 es sin referencias y en otro sitio 
    # es demasiado 
    actIter = parentIter  + 1
    if maxiters < actIter:
        return  
    for entry in fks:
        #TODO de momento solo en el esquema de la tabla original 99% de los casos
        #if entry['referred_schema'] is not None:
            #table = entry['referred_schema']+'.'+entry['referred_table']
        #else:
            #table = entry['referred_table']
        arbol (fileSet,inspector,entry.get('referred_schema',schema),entry['referred_table'],maxiters,actIter)
    return 

class BaseTreeItem(QStandardItem):
    def __init__(self, name):
        QStandardItem.__init__(self, name)
        self.setEditable(False)
        self.setColumnCount(4)
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
     
    def setDescriptive(self):
        if self.isAuxiliar():
            return
        else:
            indice = self.index() 
            colind = indice.sibling(indice.row(),2)
            if colind:
                colind.setData(True)
                
    @waiting_effects
    def getValueSpread(self):
        if self.type() == BaseTreeItem and not self.isAuxiliar() and self.parent().text() == 'FIELDS':
            conn = self.getConnection().data().engine
            schema = self.getSchema().text()
            table = self.getTable().text()
            #sqlq = 'select count(*) from (select distinct {} from {}.{}) as base'.format(self.text(),schema,table)
            # el cambio de sentencia mejora el rendimiento
            sqlq = 'select count(distinct {}) from {}.{}'.format(self.text(),schema,table)
            result = getCursor(conn,sqlq)
            self.setColumnData(2,result[0][0],Qt.EditRole)
        else:
            return  
    

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
        if isinstance(self,ConnectionTreeItem) :
            return 'Conn'
        elif isinstance(self,SchemaTreeItem):
            return 'Schema'
        elif isinstance(self,ViewTreeItem) : # con isinstance las especializaciones por delante
            return 'View'
        elif isinstance(self,TableTreeItem) :
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
        while item is not None: 
            item = item.parent()
        return item

    def fqnArray(self):
        if isinstance(self,BaseTreeItem):
            result = [self.getConnection().text(),self.getSchema().text(),self.getTable(),self.text()]
        elif isinstance(self,TableTreeItem):
            result = [self.getConnection().text(),self.getSchema().text(),self.text()]
        elif isinstance(self,SchemaTreeItem):
            result = [self.getConnection().text(),self.text()]
        elif isinstance(self,ConnectionTreeItem):
            result = [self.text(),]
            
    def fqn(self):
        if isinstance(self,TableTreeItem):
            # aparentemente sqlite funciona con main como esquema o sin
            schema = self.getSchema().text()
            return '.'.join((schema,self.text(),))
        elif isinstance(self,BaseTreeItem):
            tabfqn = self.getTable()
            if tabfqn:
                return '.'.join((tabfqn.fqn(),self.text(),))
            else:
                return self.text()
        else:
            return self.text()

            
    def getColumnData(self,column,role=None):
        indice = self.index() #self.model().indexFromItem(field)
        colind = indice.sibling(indice.row(),column)
        if colind.isValid():
            return colind.data(role) if role else colind.data()
        else:
            return None
    
    def setColumnData(self,column,data,role=None):
        indice = self.index() #self.model().indexFromItem(field)
        colind = indice.sibling(indice.row(),column)
        if colind.isValid():
            colitem = self.model().itemFromIndex(colind)
            if role:
                colitem.setData(data,role)
            else:
                colitem.setData(data)

    def getConnection(self):
        item = self
        while item is not None and not isinstance(item,ConnectionTreeItem):
            item = item.parent()
        return item

    def getSchema(self):
        item = self
        while item is not None and not isinstance(item,SchemaTreeItem):
            item = item.parent()
        return item

    def getTable(self):
        item = self
        while item is not None and not isinstance(item,TableTreeItem):
            item = item.parent()
        return item

    #def setContextMenu(self,menu):
        #setContextMenu(self,menu)
    #def getContextMenu(self,action,exec_obj=None):
        #getContextMenu(self,action,exec_obj)

    def __repr__(self):
        return "<" + self.getTypeText() + " " + self.text() + ">"

    def setMenuActions(self,menu,context):  
        if self.isAuxiliar():
            return
        else:
            pai = self.parent() # que debe ser auxiliar
        self.menuActions = []
        if pai.text() in  ('FK','FK_REFERENCE'):
            self.menuActions.append(menu.addAction("Go to reverse FK",lambda:self.execAction(context,"reverse")))
            self.menuActions[-1].setEnabled(False)
            self.menuActions.append(menu.addAction("Set descriptive fields",lambda:self.execAction(context,"descset")))
            self.menuActions[-1].setEnabled(False)
        elif pai.text() == 'FIELDS':
            self.menuActions.append(menu.addAction("Set as descriptive field",lambda:self.execAction(context,"desc")))
            self.menuActions[-1].setEnabled(False)
            self.menuActions.append(menu.addAction("Get number of values",lambda:self.execAction(context,"histogram")))

        #for entrada in self.menuActions:
            #entrada.setEnabled(False)
        
    def execAction(self,context,action):
        
        if action in ('histogram',):
            self.getValueSpread()
        elif action in ('reverse','descset'):
            pass
        else:
            self.setDescriptive()

    
class ConnectionTreeItem(BaseTreeItem):
    def __init__(self, name,connection=None):
        BaseTreeItem.__init__(self, name)
        #FIXME no podemos poner el icono de momento
        self.setIcon(QIcon("icons/16/database_server"))
        self.inspector = None
        if connection is not None:
            self.setData(connection)
        #else:
            #self.setData(None)

    def findElement(self,schemaName,tableName):
        sch = self.getChildrenByName(schemaName)
        if sch is None:
            if config.DEBUG:
                print('Esquema >{}< no definido'.format(schemaName))
            return
        tab = sch.getChildrenByName(tableName)
        if tab is None:
            if config.DEBUG:
                print('Tabla {} no definida'.format(tableName))
            return
        return tab

    
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
                        
                except ( OperationalError, ProgrammingError) as e:
                    # showConnectionError('Error en {}.{}'.format(schema,table_name),norm2String(e.orig.args),'Error en el diccionario')
                    if config.DEBUG:
                        print('error operativo en ',schema,table_name,norm2String(e.orig.args))
                    continue
                except AttributeError as e:
                    # showConnectionError('Error en {}.{}, >{}'.format(schema,table_name,fk['referred_table']),norm2String(e.orig.args),'Error en el diccionario')
                    if config.DEBUG:
                        print(schema,table_name,fk['referred_table'],'casca',norm2String(e.orig.args))
                    continue
                
    def refresh(self,**kwargs):
        """
           Refesca los datos de la conexion
           Probablemente no se usa ahora mismo.
           El problema es que no acaba de cuadran para el caso que la base este caida
        """
        pSchema = kwargs.get('schema')
        sysExcluded =kwargs.get('sysExclude',True)
        self.deleteChildren()
        if self.isOpen():
            engine = self.getConnection().data().engine
            self.inspector = inspect(engine)
            
            if len(self.inspector.get_schema_names()) is 0:
                schemata =[None,]
            elif pSchema is not None:
                schemata = [pSchema,]
            else:
                driver = self.data().dialect.name
                if sysExcluded and driver in SYSTEM_SCHEMAS:                    
                    schemata = [schema for schema in self.inspector.get_schema_names() if schema not in SYSTEM_SCHEMAS[driver] ]
                else:
                    schemata=self.inspector.get_schema_names()  #behaviour with default
            for schema in schemata:
                self.appendRow(SchemaTreeItem(schema))
                curSchema = self.lastChild()
                curSchema.refresh(**kwargs)
            # en el caso de pedir una tabla en concreto NO se calculan la FK hierarchy
            if not kwargs.get('table'):    
                self.FK_hierarchy(self.inspector,schemata)
            
        else:
            self.setIcon(QIcon('icons/16/database_lightning.png'))
            self.setData(None)


    def isOpen(self):
        if isinstance(self.data(),ConnectionTreeItem):
            return False
        if self.data() is None:
            return False
        if self.data().closed:
            return False
        else:
            #No esta garantizado que realmente este arriba el servidor
            return True
        
    def setMenuActions(self,menu,context):      
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh",lambda:self.execAction(context,"refresh")))
        self.menuActions.append(menu.addAction("Edit ...",lambda:self.execAction(context,"edit")))
        self.menuActions.append(menu.addAction("Delete",lambda:self.execAction(context,"delete")))
        if self.isOpen():
            self.menuActions.append(menu.addAction("Disconnect",lambda:self.execAction(context,"switch")))
        else:
            self.menuActions.append(menu.addAction("Connect",lambda:self.execAction(context,"switch")))

    
    def execAction(self,context,action):
        if action == "refresh" :
            modelo = self.model()
            modelo.beginResetModel()
            #if self.isOpen():
                #self.refresh()
            #else:
                #context.updateModel(self.text())
            context.updateModel(self.text())
            modelo.endResetModel()
        if action == "edit" :
            context.modConnection(self.text())
            pass  # edit item, save config, refresh tree
        elif action == "delete":
            context.delConnection(self.text())
            pass  # close connection, delete tree, delete config
        elif action == "switch":
            if self.isOpen():
                self.model().beginResetModel()
                self.data().close()
                self.deleteChildren()
                self.setIcon(QIcon('icons/16/database_lightning.png'))
                self.setData(None)
                self.model().endResetModel()
            else:
                context.updateModel(self.text())
                #self.model().updateModel(self.text())
        
class SchemaTreeItem(BaseTreeItem):
    def __init__(self, name):
        BaseTreeItem.__init__(self, name)
        #FIXME no podemos poner el icono de momento
        self.setIcon(QIcon("icons/16/database"))
        
    def refresh(self,**kwargs):
        self.deleteChildren()
        pFile = kwargs.get('table')
        
        #engine = self.getConnection().data().engine
        inspector = self.getConnection().inspector #inspect(engine)
        schema = self.text() if self.text() != '' else None
        #no parece funcionar muy bien con el resto del codigo.
        #TODO ver como funciona con los sinonimos en oracle
        #if schema == inspector.default_schema_name:
            #schema = None

        if pFile: 
            maxIter = kwargs.get('iters',1) # el defecto es un nivel de anidacion
            list_of_files = set()
            arbol(list_of_files,inspector,schema,pFile,maxIter,0)
            for entry in list_of_files:
                (kschema,ktable) = entry.split('.')
                if kschema and kschema  == '':
                    kschema = None
                if (kschema and schema) and kschema == schema:  #?? como se comportara eso con los nones 
                    self.appendRow(TableTreeItem(ktable))
                    curTable = self.lastChild()
                    curTable.refresh()
                else:
                    hermano = self.getBrotherByName(kschema)
                    if hermano:
                        hermano.appendRow(TableTreeItem(ktable))
                        curTable = hermano.lastChild()
                        curTable.refresh()
                    else:
                        conexion = self.parent() #self.getParent()
                        conexion.appendRow(SchemaTreeItem(kschema))  
                        curSchema = conexion.lastChild()
                        curSchema.refresh(table=ktable,iters=0)

            return
        
        """
          el codigo a partir de ahora no se ve afectado por lo que necesito hacer
        """
        list_of_files = inspector.get_table_names(schema)
        for table_name in list_of_files:
            self.appendRow(TableTreeItem(table_name))
            curTable = self.lastChild()
            curTable.refresh()

        list_of_views = inspector.get_view_names(schema)
        for view_name in list_of_views:
            self.appendRow(ViewTreeItem(view_name))
            curTable = self.lastChild()
            curTable.refresh()
       
    def setMenuActions(self,menu,context):      
        self.menuActions = []
        self.menuActions.append(menu.addAction("Refresh",lambda:self.execAction(context,"refresh")))

    
    def execAction(self,context,action):
        if action == "refresh" :
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
        #engine = self.getConnection().data().engine
        #inspector = inspect(engine)
        inspector = self.getConnection().inspector
        
        table_name = self.text()
        schema = self.getSchema().text()
        if schema == '':
            schema = None
            
        try:
            #FIXME self.getRecordCount()
            for column in inspector.get_columns(table_name,schema):
                try:
                    name = BaseTreeItem(column['name'])
                    tipo = BaseTreeItem(typeHandler(column.get('type',types.Text())))
                    curTableFields.appendRow((name,tipo))
                    #FIXME el rendimiento es intolerable para poer hacerlo para todas las columnas
                    #curTableFields.lastChild().getValueSpread()
                except CompileError: 
                #except CompileError:
                    if config.DEBUG:
                        print('Columna sin tipo',schema,' ',table_name,' ',name)
                    if name and name != '':
                        tipo = BaseTreeItem(typeHandler(types.Text()))
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
        except (OperationalError, ProgrammingError) as e:
            if config.DEBUG:
                #showConnectionError('Error en {}.{}'.format(schema,table_name),norm2String(e.orig.args))
                print('Error en {}.{}'.format(schema,table_name),norm2String(e.orig.args))
                
    def getFields(self,simple=False):
        """
        if simple returns fqn
        else returns:
           array of
              fqn
              format (my style)
              if available value_spread
              None
              basename
        """
        lista = []
        for item in self.listChildren():
            if item.text() != 'FIELDS':
                continue
            else:
                for field in item.listChildren():
                    if simple:
                        lista.append(field.fqn())
                    else:
                        struct = field.getRow()
                        struct[0] = field.fqn()
                        baseName = field.text()
                        struct.append(baseName)
                        lista.append(struct)
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
       

    
    def getTableInfo(self):
        TableInfo = dict()
        esquema = self.getSchema()
        TableInfo['schemaName'] = nomEsquema = esquema.text()
        TableInfo['tableName'] = self.fqn()
        Fields = self.getFields()
        if Fields and len(Fields) != 0:
            TableInfo['Fields'] = []
            for entrada in Fields:
                TableInfo['Fields'].append({'name':entrada[0],'format':entrada[1],'basename':entrada[-1]})
                
        FKs = self.getFK(False)
            
        if FKs and len(FKs) > 0:
            TableInfo['FK']= []
            for entrada in FKs:
                TableInfo['FK'].append({'name':entrada[0],'parent table':entrada[1],'parent field':entrada[3],'ref field':entrada[2]})   
        
        return TableInfo
        

    def setMenuActions(self,menu,context):      
        self.menuActions = []
        
        self.menuActions.append(menu.addAction("Refresh",lambda:self.execAction(context,"refresh")))
        self.menuActions.append(menu.addAction("Properties",lambda:self.execAction(context,"properties")))
        self.menuActions[-1].setEnabled(False)
        self.menuActions.append(menu.addAction("Count rows",lambda:self.execAction(context,"rowcount")))
        self.menuActions.append(menu.addAction("Field statisticts",lambda:self.execAction(context,"fieldstats")))
        menu.addSeparator()
        self.menuActions.append(menu.addAction("Browse Data",lambda:self.execAction(context,"browse")))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key",lambda:self.execAction(context,"browseFK")))
        self.menuActions.append(menu.addAction("Browse Data with Foreign Key recursive",lambda:self.execAction(context,"browseFKR")))
        self.menuActions[-1].setEnabled(False)
        menu.addSeparator()
        self.menuActions.append(menu.addAction("Generate Cube",lambda:self.execAction(context,"generate")))
        
        
    def execAction(self,context,action):
        
        if action == 'refresh' :
            self.model().beginResetModel()
            self.refresh()
            self.model().endResetModel()
        # show properties sheet
        elif action == 'properties':
            pass
        elif action == 'rowcount':
            self.getRecordCount()
        elif action == 'fieldstats':
            self.getFieldStats()
        elif 'browse' in action:
            conn,schema,table=self.getFullDesc().split('.')
            if action == 'browse':
                niters = 0 #de momento NO
            elif action == 'browseFK':
                niters = 1
            elif action == 'browseFKR':
                niters = 2 #de momento NO
            context.databrowse(conn,schema,table,iters=niters)
            
        elif action == 'generate':
            conn,schema,table=self.getFullDesc().split('.')
            context.cubebrowse(conn,schema,table)
            #cubemgr = CubeBrowserWin(conn,schema,table,pdataDict=self.model())
            pass # generate cube
    
    @waiting_effects
    def getRecordCount(self):
        if isinstance(self,TableTreeItem) :   #Recordar que especializamos Table.. con View luego el type no va
            conn = self.getConnection().data().engine
            schema = self.getSchema().text()
            table = self.text()
            if schema is  None or schema == '' or schema == 'None' : #cubriendo todas las bases
                sqlq = 'select count(*) from {} '.format(table)
            else:
                 sqlq = 'select count(*) from {}.{} '.format(schema,table)
            result = getCursor(conn,sqlq)
            self.setColumnData(1,result[0][0],Qt.EditRole)
        else:
            return None

    @waiting_effects
    def getFieldStats(self):
        if isinstance(self,TableTreeItem) :   #Recordar que especializamos Table.. con View luego el type no va
            listaCampos = self.getChildrenByName('FIELDS')
            for item in listaCampos.listChildren():
                item.getValueSpread()
        else:
            return None

class ViewTreeItem(TableTreeItem):
    def __init__(self, name):
        TableTreeItem.__init__(self, name)
        self.setIcon(QIcon("icons/16/code"))

    def setMenuActions(self,menu,context):      
        TableTreeItem.setMenuActions(self,menu,context)
        self.menuActions[1].setEnabled(True)  #FIXME buscar una manera mas segura de invocar el indice
                
                    
    def execAction(self,context,action):
        TableTreeItem.execAction(self,context,action)
        if action == 'properties' :
            #engine = self.getConnection().data().engine
            #inspector = inspect(engine)
            inspector = self.getConnection().inspector
            table_name = self.text()
            schema = self.getSchema().text()
            cadena = queryFormat(inspector.get_view_definition(table_name,schema))
            QMessageBox.information(context,
                                "Información de la vista",
                                cadena)

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

