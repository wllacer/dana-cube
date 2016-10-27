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


from dictmgmt.datadict import *    
#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import  QSortFilterProxyModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter, QMenu

from datalayer.query_constructor import *

from models import fmtNumber               

DEBUG = True

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
                            if DEBUG:
                                print ('error de formato en ',
                                self.model().recordStructure[index.column()],
                                super(CursorItem,self).data(role))
                            return '=>'+rawData
            #else:
                #return Qt.AlignLeft| Qt.AlignVCenter
        return super(CursorItem,self).data(role)
    
def getTable(dd,confName,schemaName,tableName,maxlevel=1):
    #OJO silent error
    con = dd.getConnByName(confName)
    if con is None:
        if DEBUG:
            print('Conexion {} no definida'.format(confName))
        return
    sch = con.getChildrenByName(schemaName)
    if sch is None:
        if DEBUG:
            print('Esquema {} no definido'.format(schemaName))
        return
    tab = sch.getChildrenByName(tableName)
    if tab is None:
        if DEBUG:
            print('Tabla {} no definida'.format(tableName))
        return
    if DEBUG:
        print('get Table ->',tab.getFullDesc())
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
    #print('namespace')
    #pprint(namespace)
    #print('prefix ',prefix)
    #print('\n')
    
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
            #print(fkname,entry['table'],fk_prefix)
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
    sqlContext['formats'] = [ item[1] for item in dataspace ]
    sqls = sqlContext['sqls'] = queryConstructor(**sqlContext)
    if DEBUG:
        print(queryFormat(sqls))
    return sqlContext

def localQuery(conn,info,iters=None):
    sqlContext = setLocalQuery(conn,info,iters=None)
    sqls = sqlContext['sqls'] #solo por compatibilidad
    return getCursor(conn,sqls,LIMIT=1000)


class SortProxy(QSortFilterProxyModel):
    def lessThan(self, left, right):
        leftData = left.data(Qt.EditRole)
        rightData = right.data(Qt.EditRole)
        try:
            return float(leftData) < float(rightData)
        except (ValueError, TypeError):
            pass
        return leftData < rightData
    
class TableBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None,iters=0):
        super(TableBrowserWin, self).__init__()
        self.view = TableBrowser(confName,schema,table,pdataDict,iters)
        if DEBUG:
            print('inicializacion completa')
        ##CHANGE here
    
        self.querySplitter = QSplitter(Qt.Horizontal)
        self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.view)
        self.setCentralWidget(self.querySplitter)
               
        self.setWindowTitle("Visualizador de base de datos")

class TableBrowser(QTableView):
    def __init__(self,confName=None,schema=None,table=None,pdataDict=None,iters=0):
        super(TableBrowser, self).__init__()
        self.view = self # sinomimo para no tener que tocar codigo mas abajo
        self.model = CursorItemModel()
        self.setupModel(confName,schema,table,pdataDict,iters)
        self.setupView()
    
    def setupModel(self,confName,schema,table,pdataDict,iters): 
        if isinstance(pdataDict,DataDict):
            dataDict = pdataDict
        else:
            dataDict=DataDict(conn=confName,schema=schema)
        if not confName or confName == '':
            return
        info = getTable(dataDict,confName,schema,table)
        sqlContext= setLocalQuery(dataDict.conn[confName],info,iters)
        self.model.recordStructure = []
        for  idx,fld in enumerate(sqlContext['fields']):
            self.model.recordStructure.append({'name':fld,'format':sqlContext['formats'][idx]})
        sqls = sqlContext['sqls'] 
        cabeceras = [ fld for fld in sqlContext['fields']]
        self.model.setHorizontalHeaderLabels(cabeceras)

        cursor = getCursor(dataDict.conn[confName],sqls)
        for row in cursor:
            modelRow = [ CursorItem(str(fld)) for fld in row ]
            self.model.appendRow(modelRow)
            
        cursor = [] #operacion de limpieza, por si las mac-flies
    def setupView(self):
        #        self.view = QTableView(self)
        # aqui por coherencia --es un tema de presentacion
        sortProxy = SortProxy()
        sortProxy.setSourceModel(self.model)
        self.view.setModel(sortProxy)
        
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.horizontalHeader().customContextMenuRequested.connect(self.openContextMenu)

        self.view.doubleClicked.connect(self.test)

        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.verticalHeader().hide()
        self.view.setSortingEnabled(True)  
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)
        self.areHidden = False
     
    def loadData(self,confName=None,schema=None,table=None,pdataDict=None,iters=0):
        self.model.beginResetModel()
        self.model.clear()
        self.setupModel(confName,schema,table,pdataDict,iters)
        self.model.endResetModel()
        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
    
    def openContextMenu(self,position):
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            columna = index.column()
        else:
            columna=self.view.horizontalHeader().logicalIndexAt(position)
        
        menu = QMenu()
        self.menuActions = []
        self.menuActions.append(menu.addAction("HideColumn",lambda a = columna:self.view.hideColumn(a)))
        if self.areHidden:
            self.menuActions.append(menu.addAction("Show hidden columns",self.view.unhideColumns))
        
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        
    def hideColumn(self,pos):
        self.view.setColumnHidden(pos,True)
        self.areHidden = True
        
    def unhideColumns(self):
        for k in range(self.model.columnCount()): #TableView no tiene colimn count, pero si el modelo)
            if self.view.isColumnHidden(k):
                self.view.showColumn(k)
        self.areHidden = False
        
    def test(self):
        return
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    window = TableBrowserWin('MariaBD Local','sakila','film',iters=1)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
