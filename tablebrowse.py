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
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter

from datalayer.query_constructor import *

                


def getTable(dd,confName,schemaName,tableName,maxlevel=1):
    con = dd.getConnByName(confName)
    if con is None:
        print('Conexion {} no definida'.format(confName))
        return
    sch = con.getChildrenByName(schemaName)
    if sch is None:
        print('Esquema {} no definido'.format(schemaName))
        return
    tab = sch.getChildrenByName(tableName)
    if tab is None:
        print('Tabla {} no definida'.format(tableName))
        return
    print(tab.getFullDesc())
    #return tab.getFullInfo()
    #pprint(tab.getBackRefInfo())
    return tab.getFullInfoRecursive(maxlevel)

def name_collisions(namespace):
    for key in namespace.keys():
        if len(namespace[key])>=3:
            continue  #ya ha sido evaluada y es un duplicado.
        else:
            #TODO seguro que puede pitonizarse
            matches=[]
            for clave in namespace:
                valor = namespace[clave][0]
                if valor == namespace[key][0]:
                    matches.append(clave)
            if len(matches) > 1:
                for idx,nombre in enumerate(matches):
                    if len(namespace[nombre]) == 2:
                        namespace[nombre].append('{}_{}'.format(namespace[nombre][1],str(idx)))
                    else:  #no deberia ir por este path
                        namespace[nombre][2] = '{}_{}'.format(namespace[nombre][1],str(idx))

def normRef(namespace,entry):
    if len(namespace[entry]) == 2:
        reference = namespace[entry][0]
        prefix = namespace[entry][1]
    else:
        prefix = namespace[entry][2]
        reference='{} AS {}'.format(namespace[entry][0],prefix)
    return reference,prefix

def queryPrint(sqlstring):
    STATEMENT=('SELECT ','FROM ','WHERE ','LEFT OUTER JOIN ','GROUP BY ','ORDER BY ','WHERE ')
    cadena = sqlstring
    for entry in STATEMENT:
        salida = '\n{}\n\t'.format(entry)
        cadena = cadena.replace(entry,salida)
    cadena = cadena.replace(',',',\n\t')
    print(cadena)
    

def setLocalQuery(conn,info,iters=None):
    """
    TODO limit generico
    TODO relaciones con mas de un campo como enlace
    __DONE__ comprobar que nombres de tablas no colisionan
    __DONE__ informacion de formatos para la tabla de visualizacion
        Mejorar el rendimiento de la solucion
    TODO generalizar :
        * __DONE__ sin FKs
        * con FKs recursivas
    """
    if not iters:
        iteraciones = 0
    else:
        iteraciones = iters
        
    sqlContext=dict()
    namespace = dict()    


    basetable = info['tableName']

    namespace['base'] = [basetable,basetable.split('.')[-1],]
    if 'FK' in info:
        for relation in info['FK']:
            namespace[relation['Name']] = [relation['ParentTable'],relation['ParentTable'].split('.')[-1],]        
        name_collisions(namespace)
    sqlContext['tables'],prefix = normRef(namespace,'base')
    print('namespace')
    pprint(namespace)
    print('prefix ',prefix)
    print('\n')
    
    dataspace = info['Fields'][:]
    for entry in dataspace:
        if prefix:
            entry[0]='{}.{}'.format(prefix,entry[0].split('.')[-1])
    

    if info.get('FK') and iteraciones > 0:
        sqlContext['join'] = []
        for relation in info['FK']:
            
            entry = dict()
            fkname = relation['Name']
            entry['table'],fk_prefix = normRef(namespace,fkname) #relation['ParentTable']
            print(fkname,entry['table'],fk_prefix)
            if prefix:
                leftclause = prefix+'.'+relation['Field'].split('.')[-1]
            else:
                leftclause = relation['Field']
            if fk_prefix:
                rightclause = fk_prefix +'.'+relation['ParentField'].split('.')[-1]
            else:
                rightclause = relation['ParentField']
                
            entry['join_clause'] = ((leftclause,'=',rightclause),)
            entry['join_modifier']='LEFT OUTER'
            sqlContext['join'].append(entry)

            campos = relation['CamposReferencia'][:]
            for item in campos:
                if fk_prefix:
                    item[0]='{}.{}'.format(fk_prefix,item[0].split('.')[-1])
            #FIXME horrible la sentencia de abajo y consume demasiados recursos. Debo buscar una alternativa
            idx = [ k[0] for k in dataspace].index(entry['join_clause'][0][0])
            dataspace[idx+1:idx+1] = campos
                
    sqlContext['fields'] = [ item[0] for item in dataspace ]
    pprint(sqlContext)
    sqls = sqlContext['sqls'] = queryConstructor(**sqlContext)
    queryPrint(sqls)
    return sqlContext

def localQuery(conn,info,iters=None):
    sqlContext = setLocalQuery(conn,info,iters=None)
    sqls = sqlContext['sqls'] #solo por compatibilidad
    return getCursor(conn,sqls,LIMIT=1000)

class TableBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None):
        super(TableBrowserWin, self).__init__()
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
        #confName = 'MariaBD Local'
        #schema = 'sakila'
        #table = 'film'
        if type(pdataDict) is DataDict:
            dataDict = pdataDict
        else:
            dataDict=DataDict(conn=confName,schema=schema)
        info = getTable(dataDict,confName,schema,table)
        sqlContext= setLocalQuery(dataDict.conn[confName],info,1)
        sqls = sqlContext['sqls'] 
        cabeceras = [ fld for fld in sqlContext['fields']]
        self.model.setHorizontalHeaderLabels(cabeceras)
        
        cursor = getCursor(dataDict.conn[confName],sqls)
        for row in cursor:
            modelRow = [ QStandardItem(str(fld)) for fld in row ]
            self.model.appendRow(modelRow)
            
    def setupView(self):
        self.view = QTableView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.verticalHeader().hide()
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
    window = TableBrowserWin('MariaBD Local','sakila','film')
    #window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
