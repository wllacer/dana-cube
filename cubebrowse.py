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


from datadict import *    
#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter

from datalayer.query_constructor import *
from tablebrowse import *
from datemgr import genTrimestreCode
from util.jsonmgr import *

class CubeItem(QStandardItem):
    """
    TODO unificar con BaseTreeItem en dictTree
    """
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
        
    def setDescriptive(self):
        if self.isAuxiliar():
            return
        else:
            indice = self.index() 
            colind = indice.sibling(indice.row(),2)
            if colind:
                colind.setData(True)
                
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


    def __repr__(self):
        return "<" + self.getTypeText() + " " + self.text() + ">"
    
def lastChild(item):
    if item.hasChildren():
        return item.child(item.rowCount() -1)
    else:
        return None

def info2cube(dataDict,confName,schema,table):
    """
       de monento solo sustituyo
    """
    #TODO strftime no vale para todos los gestores de base de datos
    #pprint(dataDict)
    info = getTable(dataDict,confName,schema,table)                
    #pprint(info)
    
    #cubo = load_cubo()
    #cubo[table]=dict() # si hubiera algo ... requiescat in pace
    #entrada = cubo[table]
    entrada = dict()
    entrada['base filter']=""
    entrada['table'] = '{}.{}'.format(schema,table) if schema != "" else table
    
    entrada['connect']=dict()
    conn = dataDict.getConnByName(confName).data().engine
    
    print('Conexion ',conn.url,conn.driver)
    entrada['connect']["dbuser"] = None 
    entrada['connect']["dbhost"] =  None
    entrada['connect']["driver"] =  conn.driver
    entrada['connect']["dbname"] =  str(conn.url) #"/home/werner/projects/dana-cube.git/ejemplo_dana.db"
    entrada['connect']["dbpass"] =  None
    
    entrada['guides']=[]
    entrada['fields']=[]
    for fld in info['Fields']:
        if fld[1] in ('numerico'):
            entrada['fields'].append(fld[0])
        elif fld[1] in ('fecha'):
            entrada['guides'].append({'name':fld[0],
                                      'class':'d',
                                      'type':'Ymd',
                                      'prod':[{'fmt':'date','elem':fld[0]},]
                                      })  #no es completo
            #TODO cambiar strftime por la funcion correspondiente en otro gestor 
            entrada['guides'].append( genTrimestreCode(fld[0],conn.driver))

        else:
            entrada['guides'].append({'name':fld[0],
                                      'class':'o',
                                      'prod':[{'elem':fld[0],},]})  #no es completo
        """
                "prod": [
                    {   "source": {
                            "filter": "code in (select distinct partido from votos_provincia where votes_percent >= 3)", 
                            "table": "partidos", 
                            "code": "code", 
                            "desc": "acronym"
                        }, 

                        "elem": "partido"
                    }
        """
    for fk in info.get('FK',list()):
        desc_fld = []
        for fld in fk['CamposReferencia']:
            if fld[1] == 'texto':
                desc_fld.append(fld[0])
        if len(desc_fld) == 0:
            print('No proceso por falta de texto',fk)
            continue
            
        entrada['guides'].append({'name':fk['Name'],
                                    'class':'o',
                                    'prod':[{'source': {
                                            "filter":"",
                                            "table":fk['ParentTable'],
                                            "code":fk['ParentField'],
                                            "desc":desc_fld
                                        },
                                        'elem':fk['Field']},]
                                    })  #no es completo
    
    return entrada

def recTreeLoader(parent,key,data):
    parent.appendRow((QStandardItem(str(key)),QStandardItem(str(data)),))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in data:
            recTreeLoader(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                clave = elem
                datos = idx
            elif isinstance(elem,dict) and elem.get('name'):
                clave = elem.get('name')
                datos = elem
                datos['pos'] = idx
            else:                
                clave = str(idx)
                datos = elem
            recTreeLoader(newparent,clave,datos)
    #else:
        #newparent.appendRow(QStandardItem(str(data)))

class CubeBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None):
        super(CubeBrowserWin, self).__init__()
        #Leeo la configuracion
        #TODO variables asociadas del diccionario. Reevaluar al limpiar

        self.setupModel(confName,schema,table,pdataDict)
        self.setupView()
        print('inicializacion completa')
        ##CHANGE here
    
        self.querySplitter = QSplitter(Qt.Horizontal)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.view)
        self.setCentralWidget(self.querySplitter)
               
        self.setWindowTitle("Visualizador de base de datos")
     
            
    def setupModel(self,confName,schema,table,pdataDict): 
        self.model = QStandardItemModel()
        self.hiddenRoot = self.model.invisibleRootItem()
        #confName = 'MariaBD Local'
        #schema = 'sakila'
        #table = 'film'
        if type(pdataDict) is DataDict:
            dataDict = pdataDict
        else:
            dataDict=DataDict(conn=confName,schema=schema)
        info = info2cube(dataDict,confName,schema,table)
        #
        info = load_cubo('cuboSqlite.json')
        #
        parent = self.hiddenRoot
        for entrada in info:
            recTreeLoader(parent,entrada,info[entrada])
        #sqlContext= setLocalQuery(dataDict.conn[confName],info,1)
        #sqls = sqlContext['sqls'] 
        #cabeceras = [ fld for fld in sqlContext['fields']]
        #self.model.setHorizontalHeaderLabels(cabeceras)
        
        #cursor = getCursor(dataDict.conn[confName],sqls)
        #for row in cursor:
            #modelRow = [ QStandardItem(str(fld)) for fld in row ]
            #self.model.appendRow(modelRow)
            
    def setupView(self):
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
        #self.view.verticalHeader().hide()
        #self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)
        
    def test(self):
        return
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    window = CubeBrowserWin('MariaBD Local','sakila','rental')
    #window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
