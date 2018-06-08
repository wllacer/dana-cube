#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Todo list tras completar validators y setters
-> DONE no en add, pero pueden moverse los elementos
-> DONE Incluir llamada a la consulta de guia
-> Incluir llamada al grand total
-> DONE Las fechas artificiales (trimestres, cuatrimestres, ...) como opciones de menu aqui y no en info2*
-> Para sqlite que el selector de base de datos sea el selector de ficheros del sistema
-> DONE Copy to other place
-> DONE Restore

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from support.gui.treeEditor import *
from admin.cubemgmt.cubeTreeUtil import *
from base.datadict import DataDict

from admin.cubemgmt.cubeUI.lnkEditDlg import FKNetworkDialog,makeTableSize,addNetworkMenuItem, LinksDlg,getLinks,setLinks
from admin.cubemgmt.cubeUI.catEditDlg import catDelegate,catEditor,getCategories,setCategories
from admin.cubemgmt.cubeUI.datEditDlg import getDateFilter,setDateFilter,dateFilterDlg


"""

Nuevo mojo del arbol

no example of validators attribute 
elements list is (element name,mandatory,readonly,repeatable, subtype_selector)
still no process for repeatable 
class & name are not to be edited (even shown) as derived DONE
Problem in values list. Edition of element duplicates them

We have prepared treeEditor to be able to handle QDialogs with following details
    * Data should be collected via a getter
    * Dialog must implement  setData / getData methods to be able to set/retrieve data to the dialog
    * Data should be returned to model via a setter
    * As accept/reject doesn't seem to be honored, implementator shall guarantee that a cancel maintains the original values
    
Still only basic testing done
    
A note about callbacks: (getters,setters,....)
In subtypes the one which has precedence is the child
GETTERS
    executed at start of SetEditorData 
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist 
    input
            editor,
            item,
            view,
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)
    output
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)

SETTERS
    executed at the end of SetModelData
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist
        input  *lparm
            item = lparm[0]
            view = lparm[1]
            context = lparm[2]   Fundamentalmente para obtener el valor original context['data']
            ivalue / values = lparm[3]
            dvalue = lparm[4]
        output
            item, the edited item
"""

TOP_LEVEL_ELEMS = ['base','default_base']
EDIT_TREE = {
    'base': {'objtype': 'dict',
                    'elements': [
                        ('base filter',False,False),
                        ('connect',True,False),
                        ('fields',True,False),
                        ('guides',True,False,True),
                        ('table',True,False), 
                        ('date filter',False,False,True),
                    ],
                    'getters':[],                   #antes de editar
                    'setters':[],      #despues de editar (por el momento tras add
                    'validators':[],                 #validacion de entrada
                    'text':'definción de cubo',
                    },
    'connect': { 'objtype':'dict',
                     'elements':[
                         ('driver',True,False),
                         ('dbname',True,False),
                         ('dbhost',False,False),
                         ('dbuser',True,False),
                         ('dbpass',False,False),
                         ('schema',False,False),
                        ],
                     'getters':[],
                     'setters':[],
                    'validators':[],
                    'menuActions':[ [addConnectionMenu,'Comprueba la conexión'],],
                    'text':'parámetros de conexion a la base de datos',
                    },
    'driver': {'editor':QComboBox, 'source':DRIVERS,
               'text':'gestor de base de datos a usar',
               'validators':[valConnect,],
               },
    'dbname':{ 'editor':QLineEdit,
              'text':'Nombre de la instancia de  base de datos',
              'validators':[valConnect,],},
    'dbhost':{'editor':QLineEdit,
              'text':'Servidor donde reside la base de datos',
              'validators':[valConnect,],},
    'dbuser':{'editor':QLineEdit, 'default':'',
              'text':'Usuario de la base de datos por defecto',
              'validators':[valConnect,],},
    'dbpass':{'editor':QLineEdit, 'hidden':True,
              'text':'clave del usuario en la B.D. (desaconsejado)'},   
    'schema':{'editor':QComboBox,'source':srcSchemas,'default':defaultSchema,
              'text':'Esquema de la B.D. a utilizar por defecto',
              },
    'table' : { 'editor':QComboBox, 'source':srcTables,'editable':True,'setters':['default',setTable,] },
    'base filter': {'editor':QTextEdit }, #QLineEdit},   #aceptaria un validator
    'date filter': {'objtype':'list'},
    'fields' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcNumFields,
                'children': 'field',
                },
    'field' : { 'editor' : QLineEdit},   #experimento a ver si funciona
    'guides':{'objtype':'dict',
                   'elements':[
                       ('name',True,True),
                       ('class',True,True),
                       ('fmt',False,False),
                       ('prod',True,False,True,'class'),                       
                       ],
                    'text':'Guia de agrupación',
                    'menuActions':[[addNetworkMenuItem,'Añada una regla remota'],],
                   },
    'name':{'editor':QLineEdit },
    'class' :{'editor':QComboBox,'source':GUIDE_CLASS,'default':'o'},
    'fmt' :{'editor':QComboBox,'source': ENUM_FORMAT ,'default':'txt' },
    'prod':{'objtype':'dict','subtypes':('prod_std','prod_cat','prod_case','prod_date','prod_ref'),
            'discriminator':discProd,
            'setters':[setClass,],
            'diggers':[digClass,],
            'elements':[
                    ('name',True,True),
                    ('class',False,True),         
                    ('fmt',False,False),
                ],
            'text':'Regla de produccion de guía',
            },
    'prod_std':{'objtype':'dict',
                'elements':[
                    ('elems',True,False),
                    ('domain',False,False),
                    ],
                'text':'Guía ordinaria',
                },
    'prod_cat':{'objtype':'dict',                 # es o categories o case sql tengo que ver como lo asocio
                    'elements':[
                        ('elems',True,False),
                        ('categories',True,False,True),
                        ('fmt_out',False,False),
                    ],
                'text':'Guía por tabla de categorias',
                },
    'prod_case':{'objtype':'dict',                 # es o categories o case sql tengo que ver como lo asocio
                    'elements':[
                        ('elems',True,False),
                        ('case_sql',True,False),
                        ('fmt_out',False,False),
                    ],
                'text':'Guía por sentencia directa',
                },
    'prod_date':{'objtype':'dict',
                    'elements':[
                        ('elems',True,False),
                        ('mask',True,False),
                    ],
                'text':'Guía por fecha',
                },
    'prod_ref': { 'objtype':'dict',
               'elements':[
                   ('reference',True,False),
                   ('link ref',False,False),
                    ('grouped by',False,False),
                   ],
               'text':'referencia a otra guia',
            },
    'elems':{'objtype':'group', 
            'elements':[
                ('elem',True,False),
                ('table',False,False),
                ('link via',False,False,True),
                ],
            },
    'domain': { 'objtype':'dict',
               'elements':[
                    ('table',True,False),
                    ('code',True,False),
                    ('desc',False,False),
                    ('filter',False,False),
                    ('grouped by',False,False),
                   ],
               },
    'elem' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    'code' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    'desc' : { 'objtype':'list', 'editor' : WMultiList, 'source': srcFields,
                'children': 'field',
                },
    #'grouped by': {'objtype':'list'},
    'grouped by' : { 'objtype':'list', 'editor' : WMultiList }, #, 'source': srcFields,   #source probably not
                #'children': 'field',
                #},
    'filter': {'editor':QTextEdit,'default':"" }, #QLineEdit,'default':''},   #aceptaria un validator
    #TODO como hacer que solo haya un default. ¿Necesito otro callback para los menus ?
    #'menuActions':[ [addConnection,'Comprueba la conexión'],],
    #'categories': { 'objtype':'dict','subtypes':['default','category item'],'discriminator':discCat, },
    #'default':{'editor':QLineEdit },
    'categories':{'objtype':'dict',    #FIXME nombre
                     'elements':[
                         ('result',True,False),
                         ('condition',False,False),
                         ('values',True,False),  #FIXME a ver si
                         ],
                         'menuActions':[ [addCategoryMenu,'Add default value'],],
                         'editor':catEditor,
                         'getters':[getCategories, ],
                         'setters':[setCategories, ],

                     },
    'case_sql' : { 'objtype':'list', 'editor' :QTextEdit, #'source': srcNumFields,
                'children': 'field',
                },
    'result':{'editor':QLineEdit }, #TODO necesita un setter
    'condition':{'editor':QComboBox,'source':LOGICAL_OPERATOR,'default':'='},
    'values' : { 'objtype':'list',
                'children':'field'},

    'fmt_out' :{'editor':QComboBox,'source': ENUM_FORMAT ,'default':'txt' },
    'link via': {'objtype':'dict',
                'elements':[
                    ('table',True,False),
                    ('clause',True,False,True), #FIXME presentacion
                    ('filter',False,False),
                    ],
                'getters':[ getLinks, ],
                'setters':[ setLinks, ],                
                'editor': LinksDlg,

                },
    'clause':{'objtype':'dict',
              'elements':[
                  ('base_elem',True,False),
                  ('condition',False,False),
                  ('rel_elem',True,False)
                  ],
              },
    'base_elem':{'editor':QComboBox,'editable':True,'source':srcFields},  #TODO source
    'rel_elem':{'editor':QComboBox,'editable':True,'source':srcFields},     #TODO source
    #TODO concretar cuando puede usarse date start,date end, date format. Es cuestion de teoria
    'date filter':{'objtype':'dict',
                   'elements': [
                       ('elem',True,False),
                       ('date class',True,False),
                       ('date range',False,False),
                       ('date period',False,False),
                       ('date start',False,True),
                       ('date end',False,True),
                       ('date format',False,True),
                    ],
                   'editor':dateFilterDlg,
                   'getters':[ getDateFilter, ],
                   'setters':[ setDateFilter, ],
                   },
    'date class':{'editor':QComboBoxIdx,'source':CLASES_INTERVALO},
    'date range':{'editor':QComboBoxIdx,'source':TIPOS_INTERVALO},
    'date period':{'editor':QSpinBox,'min':1},
    'date format':{'default':'fecha'},
    'reference':{'editor':QComboBox,'source':srcGuides },
    'link ref':{'editor':QLineEdit},
    'default base': { 'objtype':'dict',
                     'elements':[],
                     'getters':[],
                     'setters':[],
                    'validators':[],
                    },
}
"""
utility functions to read from DD

"""

def _exists(dd,id):
    """
    comprueba si una determinada conexion ya existe. id puede ser el texto ya procesado o un diccionario connect
    
    """
    if isinstance(id,dict):
        nombre = toConfName(id)
    else:
        nombre = id
    lista = list(dd.configData['Conexiones'].keys())
    if nombre in lista:
        return True
    else:
        return False
    
def _hName(item):
    """
    para un arbol como el diccionario (ver que tiene  metodo .text()) la jerarquia de claves
    
    """
    fullName = []
    fullName.append(item.text())
    pai = item.parent()
    while pai:
        fullName.insert(0,pai.text())
        pai = pai.parent()
    return fullName

"""
Funciones para gestionar el diccionario de datos

"""
def datadict2dict(head):
    """
    convierte el QStandardItemModel de un DataDict en un diccionario. 
    La estructura de un DD puede ser buena para danabrowse, pero es un petardo autentico para programar

    head es el elemento raiz
    """
    resultado = {}
    for entry in traverse(head):
        fName = _hName(entry)
        # la linea de conexiones se trata por separado
        if len(fName) == 1:
            if fName[0] not in resultado:   #probablemente overkill
                resultado[fName[0]] = {'@tipo':entry.getTypeText(),'@engine':entry.getRow()[1]}
            continue
        
        if entry.text() in ('FIELDS','FK','FK_REFERENCE') and not entry.hasChildren():
            continue
        
        padre = resultado
        for nombre in fName[0:-1]:
            try:
                padre = padre[nombre]
            except KeyError:
                print('Horror',nombre,' de ',fName,' en ',padre)
                exit()
        if entry.getTypeText() in ('Schema','Table','View','FIELDS','FK','FK_REFERENCE'):
            padre[entry.text()] = {'@tipo':entry.getTypeText()}
            
        else:
            if len(fName) >2 and fName[-2] == 'FIELDS':
                padre[entry.text()] = {'@tipo':'Field','@fmt':entry.getRow()[1]}
            elif len(fName) >2  and fName[-2] in ( 'FK_REFERENCE','FK'):
                #TODO discriminar cual es cual
                agay = entry.getRow()
                name = agay[0]
                fields = agay[1:]
                padre[entry.text()] = {'@tipo':'FK_reference','@name':name,'@fields':fields}
            else: 
                padre[entry.text()] = {'@tipo':entry.text() }

    return resultado

def file2datadict(fileName,secure=True,exclude=True):
    #from base.datadict import DataDict
    """
    de cubo a DataDictionary
    
    """
    mis_cubos = load_cubo(fileName)
    dd = None
    for cubo in mis_cubos:
        if cubo == 'default':
            continue
        confData = mis_cubos[cubo]['connect']
        #el driver tambien forma parte de la identificacion
        confName = toConfName(confData)
        if not dd:
            dd = DataDict(conName = confName,confData=confData,secure=secure,sysExclude=exclude)
        elif _exists(dd,confName):
            print('conexion <',confName,'> ya existe')
            continue
        else:
            dd.appendConnection(confName=confName,confData=confData,secure=secure,sysExclude=exclude)
    return dd

def editAsTree(file=None,rawCube=None):
    if not file and not rawCube:
        raise NameError('Para editAsTree no se especificaron los parametros necesarios')
    
    if not rawCube:
        definiciones = load_cubo(file)
        mis_cubos = definiciones
    else:
        mis_cubos = rawCube

    #cubo = Cubo(mis_cubos['experimento'])
    model = displayTree() #QStandardItemModel()
    model.setItemPrototype(QStandardItem())
    hiddenRoot = model.invisibleRootItem()
    parent = hiddenRoot
    for entrada in mis_cubos:
        if entrada == 'default':
            tipo = 'default_base'
        else:
            tipo = 'base'
        dict2tree(parent,entrada,mis_cubos[entrada],tipo)
    return model

"""
Clase principal

"""
class cubeTree(TreeMgr):
    # señal para controlar el cambio de la conexion. Realmente solo la usa en el check. Overkill ¿?
    connChanged = pyqtSignal(str,str)
    resized = pyqtSignal()
    
    def __init__(self,treeDef,firstLevelDef,ctxFactory,file,msgLine,**kwparms):
        Context.EDIT_TREE = treeDef
        if 'dataDict' in kwparms:
            self.dataDict = kwparms['dataDict']
        else:
            secure = kwparms.get('secure',True)
            sysEx =   kwparms.get('sysExclude',True)
            self.dataDict  = file2datadict(file,secure,sysEx)
            
        self.diccionario = datadict2dict(self.dataDict.hiddenRoot)
        
        self.defaultEntry = {'file':file,'rawCube':kwparms.get('rawCube',{})}
        if 'rawCube' in kwparms:
            self.tree = editAsTree(rawCube = kwparms['rawCube'])
        else:
            self.tree = editAsTree(file=file)
        self.cubeFile = file
        super().__init__(self.tree,treeDef,firstLevelDef,ctxFactory,msgLine)
        
        #self.sortByColumn(0, Qt.AscendingOrder)
        
        self.connChanged.connect(self.checkConexion)
        self.resized.connect(self.resizeTree)
    """
    slots
    """
    def checkConexion(self,cubeName,itemName):
        """
        slot para procesar el añade conexion. Quizas se ejecute demasiadas veces
        """
        #FIXME como hago que solo se ejecute si cambia
        # el principio podria sustituirse por getConnection()
        namehier = [cubeName,'connect']
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        confData = {}
        for entrada in childItems(item):
            n, i, t = getRow(entrada)
            confData[n.data()] = i.data()
        confName = toConfName(confData)
        dd = self.dataDict
        if _exists(dd,confName):
            print('conexion <',confName,'> ya existe')
            return
        else:
            print('conexion <',confName,'> no existe. Voy a crearla')
            dd.appendConnection(confName=confName,confData=confData,secure=True)
        #FIXME esto es caro de recursos
            self.diccionario = datadict2dict(self.dataDict.hiddenRoot)
        pass
    """
    data access methods
    
    """
    def _getTopLevel(self,item):
        pai = item
        nombre = None
        while pai:
            n,i,t = getRow(pai)
            nom = n.data()
            tipo = t.data() if t else None
            if t and t.data() == 'base':
                nombre = n.data()
                break
            elif t and t.data() == 'default_base':
                #TODO
                pass
            pai = n.parent()
        return nombre

    def getHierarchy(self,item,hierarchy):
        """
        obtener un elemento del arbol conociendo la jerarquia
        
        """
        namehier = hierarchy[:]
        toplevel = self._getTopLevel(item)
        namehier.insert(0,toplevel)
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        n,i,t = getRow(item)
        return n.data(),i.data(),t.data() if t else None
    
    def getConnection(self,item):
        nombre = self._getTopLevel(item)
        if not nombre:
            return None
        namehier = [nombre,'connect']
        item = getItemTopDown(self.tree.invisibleRootItem(),namehier)
        confData = {}
        for entrada in childItems(item):
            n, i, t = getRow(entrada)
            confData[n.data()] = i.data()
        confName = toConfName(confData)
        return confName,confData

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
            self.prune(exec=True)
            newcubeStruct = tree2dict(self.model().invisibleRootItem(),isDictFromDef)
            if isinstance(self.parentWindow,(cubeMgrWindow,cubeMgrDialog)):
                total=True
            else:
                total = False
            dump_structure(newcubeStruct,self.cubeFile,total=total)
            

    

    #
    def pruneExcludeList(self):
        return ['connect',]

    def domainPrune(self,item,ctx):
        super().domainPrune(item,ctx)
            
    #@waiting_effects
    #@model_change_control()
    def restoreCubeFile(self):

        if 'rawCube' in self.defaultEntry and self.defaultEntry['rawCube']:
            self.tree = editAsTree(rawCube=self.defaultEntry['rawCube'])
        else:
            self.tree = editAsTree(file=self.defaultEntry['file'])
        self.baseModel = self.tree
        self.hiddenRoot = self.baseModel.invisibleRootItem()
        self.view.setModel(self.baseModel)
    

    def resizeEvent(self, event):
        self.resized.emit()
        return super().resizeEvent(event)

    def resizeTree(self):
        totalwidth = self.size().width()
        if not config.DEBUG:
            firstCol = totalwidth * 2 // 10
            self.setColumnWidth(0,totalwidth * 2 // 10)
            self.setColumnWidth(1,totalwidth * 8 //10)
        else:
            self.setColumnWidth(0,totalwidth * 2 // 10)
            self.setColumnWidth(1,totalwidth * 7 //10)
            self.setColumnWidth(2,totalwidth * 1 //10)

    def dumpStructure(self):
        import re
        match = r'([}\]]+)'
        repl = r'\1\n'
        result = tree2dict(self.tree.invisibleRootItem(),isDictFromDef)
        resultado = repr(result)
        res = re.sub(match,repl,resultado)
        QMessageBox.information(self,"Estructura",res)
 
    def actionPaste(self,item):
        #TODO cambiar los ficheros principales
        otableItm = getChildByType(getParentByType(self.copyContext[0],'base'),'table')
        otable = getRow(otableItm)[1].data()
        nitem = super().actionPaste(item)[0]
        if not nitem:
            return
        ntableItm =getChildByType(getParentByType(nitem,'base'),'table')
        ntable = getRow(ntableItm)[1].data()
        for elem in traverse(nitem):
            propagateTableName(elem,self,otable,ntable)
        self.setCurrentIndex(nitem.index())

            
    def test(self):
        return

"""

Interfaz de usuario

"""


def generaArgParser():
    parser = argparse.ArgumentParser(description='Cubo de datos')
    parser.add_argument('--cubeFile','--cubefile','-c',
                        nargs='?',
                        default='cubo.json',
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

class cubeMgrWindow(QMainWindow):
    """
    """
    
    def __init__(self,file=None,parent=None):
        super(cubeMgrWindow,self).__init__(parent)

        #self.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
        parser = generaArgParser()
        args = parser.parse_args()
        self.cubeFile = args.cubeFile #'cubo.json'   #DEVELOP
        if file:
            self.cubeFile = file
        self.secure = args.secure
        self.sysExclude = args.sysExclude

        Context.EDIT_TREE = EDIT_TREE
        
        self.statusBar = QStatusBar()
        self.msgLine = QLabel()
        self.statusBar.addWidget(self.msgLine)
        self.tree = cubeTree(
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            self.cubeFile,
                                            msgLine = self.msgLine,
                                            secure = self.secure,
                                            sysExclude = self.sysExclude)
        
        self.fileMenu = self.menuBar().addMenu("&General")
        self.fileMenu.addAction("Verificar",lambda k=False:self.tree.prune(exec=k))
        self.fileMenu.addAction("&Salvar", self.tree.saveCubeFile, "Ctrl+S")
        self.fileMenu.addAction("&Restaurar", self.tree.restoreCubeFile, "Ctrl+M")
        self.fileMenu.addAction("S&alir", self.close, "Ctrl+D")

        self.setCentralWidget(self.tree)
        self.setStatusBar(self.statusBar)
  
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.tree.saveCubeFile()
        return True
 

class cubeMgrDialog(QDialog):
    """
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.cubeFile = 'testcubo.json'
        self.msgLine = QLabel()
        
        self.tree = cubeTree(
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            self.cubeFile,
                                            msgLine = self.msgLine)

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.tree,0,0)
        meatLayout.addWidget(self.msgLine,1,1)
        self.setLayout(meatLayout)
        
    def closeEvent(self,event):
        self.close()
        
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.tree.saveCubeFile()
        return True
 

class CubeMgr(cubeTree):
    """
    confName,schema,table son puramente por compatibilidad
    self.cubeMgr = CubeMgr(self,confName,
                                                schema,
                                                table,
                                                self.dictionary,rawCube=infox,
                                                cubeFile=self.cubeFile)
    """
    def __init__(self,parent=None,
                 confName=None,
                 schema=None,
                 table=None,
                 pdataDict=None,
                 cubeFile=None,
                 rawCube=None,
                 msgLine = None
                ):
        config.DEBUG =True
        self.cubeFile = cubeFile if cubeFile else 'testcubo.json'
        if not msgLine:
            self.msgLine = QLabel()
        else:
            self.msgLine = msgLine
        
        super().__init__(EDIT_TREE,
                                TOP_LEVEL_ELEMS,
                                Context,
                                self.cubeFile,
                                msgLine = self.msgLine,
                                dataDict = pdataDict,
                                rawCube=rawCube,
                                confName = confName,
                                schema = schema,
                                table = table,
                                )
        


import sys
def pruebaGeneral():
    app = QApplication(sys.argv)
    config.DEBUG = True
    form = cubeMgrWindow()
    form.show()
    #if form.exec_():
        #pass
        #sys.exit()
    sys.exit(app.exec_())

    
 
if __name__ == '__main__':
    #readConfig()
    #testSelector()
    #editAsTree()
    #tools = {}
    #pprint(readUM(uf))
    #pprint(tools)
    #print(readUM(uf))
    pruebaGeneral()
    #modelo =editAsTree()
            
            
    
        #print(getItemContext(item))



