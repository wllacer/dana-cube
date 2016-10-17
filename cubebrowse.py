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

from decimal import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox

from datadict import *    
from datalayer.query_constructor import *
from datalayer.access_layer import dbDict2Url
from tablebrowse import *
from datemgr import genTrimestreCode
from util.jsonmgr import *
from util.fivenumbers import is_number
from dialogs import propertySheetDlg

from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeutil  import *
from cubemgmt.cubeCRUD  import *

(_ROOT, _DEPTH, _BREADTH) = range(3)

from cubeTypes import *
"""
   cubo --> lista de cubos
   col,row
"""
def info2cube(dataDict,confName,schema,table,maxlevel=1):
    """
       de la informacion de la tabla en DANACUBE crea un cubo por defecto

    """
    #TODO strftime no vale para todos los gestores de base de datos
    #pprint(dataDict)
    info = getTable(dataDict,confName,schema,table,maxlevel)                
    #pprint(info)
    
    #cubo = load_cubo()
    cubo = dict()
    cubo[table]=dict() # si hubiera algo ... requiescat in pace
    entrada = cubo[table]
    #entrada = dict()
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
    if maxlevel == 0:
        pass
    elif maxlevel == 1:
        for fk in info.get('FK',list()):
            desc_fld = getDescList(fk)
                
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
    else:
        routier = []
        #path = ''
        path_array = []
        for fk in info.get('FK',list()):
            constructFKsheet(fk,path_array,routier)
        
        for elem in routier:
            nombres = [ item['Name'] for item in elem]
            nombres.reverse()
            nombre = '@'.join(nombres)
            activo = elem[-1]
            base   = elem[0]
            rule =   {'source': {
                                    "filter":"",
                                    "table":activo['ParentTable'],
                                    "code":activo['ParentField'],
                                    "desc":getDescList(activo)
                                },
                         'elem':activo['Field']}   #?no lo tengo claro
            if len(elem) > 1:
                rule['related via']=list()
                for idx in range(len(elem)-1):
                    actor = elem[idx]
                    join_clause = { "table":actor['ParentTable'],
                                    "clause":[{"rel_elem":actor["ParentField"],"base_elem":actor['Field']},],
                                    "filter":"" }
                    rule['related via'].append(join_clause)
                
            entrada['guides'].append({'name':nombre,
                                        'class':'o',
                                        'prod':[rule ,]
                                            })  #no es completo
    return cubo


class CubeBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None):
        super(CubeBrowserWin, self).__init__()
        self.configFile = 'cuboSqliteOrig.json'
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
        if type(pdataDict) is DataDict:
            self.dataDict = pself.dataDict
        else:
            self.dataDict = DataDict()
            #self.dataDict=DataDict(conn=confName,schema=schema)
        infox = info2cube(self.dataDict,confName,schema,table)
        #TODO convertir eso en una variable
        info = load_cubo(self.configFile)
        for nuevo in infox:
            info[nuevo] = infox[nuevo]
        #pprint(info)
        #
        parent = self.hiddenRoot
        for entrada in info:
            if entrada == 'default':
                tipo = 'default_start'
            elif entrada in ITEM_TYPE:
                tipo = entrada
            else:
                tipo = 'base'
            recTreeLoader(parent,entrada,info[entrada],tipo)
        #navigateTree(self.hiddenRoot)
        #pprint(tree2dict(self.hiddenRoot))
        getOpenConnections(self.dataDict)
        
    def setupView(self):
        self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.model)
        #self.view.hideColumn(2) # eso no interesa al usuario final
        self.view.expandAll() # es necesario para el resize
        for m in range(self.model.columnCount()):
            self.view.resizeColumnToContents(m)
        #self.view.collapseAll()
        #self.view.verticalHeader().hide()
        #self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)
    

    def openContextMenu(self,position):
        """
        """
        indexes = self.view.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
            item = self.model.itemFromIndex(index)
        menu = QMenu()
        setContextMenu(item,menu)        
        action = menu.exec_(self.view.viewport().mapToGlobal(position))
        getContextMenu(item,action,self)
        
    def test(self):
        return
    
    def saveConfigFile(self):
        baseCubo=load_cubo(self.configFile)
        newcubeStruct = tree2dict(self.hiddenRoot,isDictionaryEntry)
        for entrada in newcubeStruct:
            baseCubo[entrada] = newcubeStruct[entrada]
        #TODO salvar la version anterior
        dump_structure(baseCubo,self.configFile)
    
    def closeEvent(self, event):
        self.close()
        
    def close(self):
        #TODO  deberia cerrar los recursos de base de datos
        #for conid in self.conn:
            #if self.conn[conid] is None:
                #continue
            #if self.conn[conid].closed :
                #self.conn[conid].close()
        self.saveConfigFile()

        sys.exit()

if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    window = CubeBrowserWin('MariaBD Local','sakila','film')
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
