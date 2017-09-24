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
import datetime
import argparse
from decimal import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox
 
from dictmgmt.datadict import *    
from datalayer.query_constructor import *
from datalayer.access_layer import dbDict2Url
from tablebrowse import *
from datalayer.datemgr import genTrimestreCode
from util.jsonmgr import *
from util.numeros import is_number
from util.decorators import *

from dialogs import propertySheetDlg

from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeutil  import *
from cubemgmt.cubeCRUD  import *

from wizardmgmt.dispatcher import *

(_ROOT, _DEPTH, _BREADTH) = range(3)


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

class CubeBrowserWin(QMainWindow):
    def __init__(self,confName=None,schema=None,table=None,pdataDict=None,parent=None):
        super(CubeBrowserWin, self).__init__(parent)
        
        parser = generaArgParser()
        args = parser.parse_args()

        self.cubeFile = args.cubeFile #'cubo.json'   #DEVELOP
        self.configFile = args.configFile
        self.secure = args.secure
        self.sysExclude = args.sysExclude
        #Leeo la configuracion

        #TODO variables asociadas del diccionario. Reevaluar al limpiar
        # para notificar si estoy editando el fichero de configuracion completo o solo para una tabla
        # desactivado porque aparentemente no es necesario
        #self.fullConfig = True
        #self.setupModel(confName,schema,table,pdataDict)
        #self.setupView()
        #print('inicializacion completa')
        ##CHANGE here
        self.cubeMgr = CubeMgr(self,confName,schema,table,pdataDict,self.cubeFile,configFile=self.configFile,secure=self.secure,sysExclude=self.sysExclude)
        #self.querySplitter = QSplitter(Qt.Horizontal)
        #self.querySplitter.addWidget(self.view)
        #self.querySplitter.addWidget(self.view)
        #self.setCentralWidget(self.querySplitter)
        self.fileMenu = self.menuBar().addMenu("&General")
        self.fileMenu.addAction("&Salvar", self.cubeMgr.saveCubeFile, "Ctrl+S")
        self.fileMenu.addAction("&Restaurar", self.cubeMgr.restoreCubeFile, "Ctrl+M")
        self.fileMenu.addAction("S&alir", self.close, "Ctrl+D")

        self.setCentralWidget(self.cubeMgr)
        
        self.setWindowTitle("Visualizador del fichero de definición")
     
    
    def closeEvent(self, event):
        self.close()
        
    def close(self):
        import sys
        #
        connDict = self.cubeMgr.dataDict.conn
        for conid in connDict:
            if connDict[conid] is None:
                continue
            if not connDict[conid].closed :
                connDict[conid].close()
        self.cubeMgr.saveCubeFile()
        sys.exit()
    
    

class CubeMgr(QTreeView):
    def __init__(self,parent=None,confName=None,schema=None,table=None,pdataDict=None,cubeFile=None,rawCube=None,configFile=None,secure=True,sysExclude=True):
        super(CubeMgr, self).__init__(parent)
        self.parentWindow = parent
        if not cubeFile:
            self.cubeFile = 'cubo.json' #DEVELOP
        else:
            self.cubeFile = cubeFile
        
        self.cache = dict() #para la gestion del wizard
        
        if isinstance(pdataDict,DataDict):
            self.dataDict = pdataDict
        else:
            if configFile:
                self.dataDict = DataDict(defFile=configFile,secure=secure,sysExclude=sysExclude)
            else:
                self.dataDict = DataDict()


        self.baseModel = QStandardItemModel()
        self.hiddenRoot = self.baseModel.invisibleRootItem()
        self.particular = False #variable auxiliar para saber que tipo de uso hago
        self.setupModel(confName,schema,table,rawCube)
        
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.setupView()

        print('inicializacion completa')

    def setupModel(self,confName=None,schema=None,table=None,rawCube=None):
            #self.dataDict=DataDict(conn=confName,schema=schema)
        if confName and schema and table and rawCube:
            self.particular = True
            self.particularContext=(confName,schema,table,rawCube)
            info = rawCube
        elif confName and schema and table :
            info = info2cube(self.dataDict,confName,schema,table)
            self.particular = True
            self.particularContext=(confName,schema,table)
            #self.fullConfig = False
        else:
            info = load_cubo(self.cubeFile)
            #infox = None
        ##TODO convertir eso en una variable
        #info = load_cubo(self.cubeFile)
        #if infox:
            #for nuevo in infox:
                #info[nuevo] = infox[nuevo]

        #

        parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        if not info:
            print('Algo ha fallado espectacularmente',self.particular,self.particularContext)
        for entrada in sorted(info):  #quiero que el orden sea constante
            if entrada == 'default':
                tipo = 'default_base'
            elif entrada in ITEM_TYPE:
                tipo = entrada
            else:
                tipo = 'base'
            dict2tree(parent,entrada,info[entrada],tipo)
            print(entrada,'procesada')
        #navigateTree(self.hiddenRoot)
        #pprint(tree2dict(self.hiddenRoot))
        #getOpenConnections(self.dataDict)
        
    def setupView(self):
        #self.view = QTreeView(self)
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.openContextMenu)
        self.view.doubleClicked.connect(self.test)
        self.view.setModel(self.baseModel)
        #self.view.hideColumn(2) # eso no interesa al usuario final
        self.view.expandAll() # es necesario para el resize
        for m in range(self.baseModel.columnCount()):
            self.view.resizeColumnToContents(m)
        #self.view.collapseAll()
        #self.view.expandToDepth(1)     
        #self.view.verticalHeader().hide()
        #self.view.setHeaderHidden(True)
        #self.view.setSortingEnabled(True)
        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)
    

    def openContextMenu(self,position):
        """
        """
        openContextMenu(self,position)
        #indexes = self.view.selectedIndexes()
        #if len(indexes) > 0:
            #index = indexes[0]
            #item = self.baseModel.itemFromIndex(index)
        #else:
            #return
        #menu = QMenu()
        #setContextMenu(item,menu,self)        
        #action = menu.exec_(self.view.viewport().mapToGlobal(position))
        ## getContextMenu(item,action,self)
 
    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False


    def saveCubeFile(self):
        if self.saveDialog():
            print('Voy a salvar el fichero')
            newcubeStruct = tree2dict(self.hiddenRoot,isDictionaryEntry,Qt.EditRole)
            if isinstance(self.parentWindow,CubeBrowserWin):
                total=True
            else:
                total = False
            dump_structure(newcubeStruct,self.cubeFile,total=total)
            

    @waiting_effects
    @model_change_control()
    def restoreCubeFile(self):
        #self.baseModel.beginResetModel()
        self.baseModel.clear()
        if self.particular:
            self.setupModel(*self.particularContext)
        else:
            self.setupModel()
        self.setupView()
        #self.baseModel.endResetModel()
    
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
    window = CubeBrowserWin()#'MariaBD Local','sakila','film')
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
