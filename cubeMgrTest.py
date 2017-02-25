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

   
def sql():
  pepe=dict()
  clause1=dict()
  pepe['tables']='votos_locales'
  pepe['fields']=['geo_rel.padre','partido',('votes_presential','sum')]
  pepe['group']=['partido',]
  pepe['join']={'table':'geo_rel',
                'join_filter':"geo_rel.tipo_padre = 'P'",
                'join_clause':(('padre','=','votos_locales.municipio'),),
               }

  #clause2=dict()
  #pepe['fields']=(""" case 
        #when partido in (3316,4688) then '1 derecha'
    #when partido in (1079,4475) then '2 centro'
        #when partido in (3484) then '3 izquierda'
    #when partido in (3736,5033,4850,5008,5041,2744,5026) then '4 extrema'
        #when partido in (5063,4991,1528) then '5 separatistas'
        #when partido in (1533,4744,4223) then '6 nacionalistas'
    #else
         #'otros'
    #end as categoria""" ,'partido',('seats','sum'))
  #pepe['tables']='votos_provincia'
  #pepe['group']=('categoria',)
  #pepe['lfile']='sempronio'
  #pepe['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
  #pepe['tables'] = 'paco'
  ##pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
  #pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
  ##pepe['tables'] = 'paco'
  ##pepe['select_modifier'] = 'DISTINCT'
  #pepe['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
                    #('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
                  #)
  ##pepe['where']=((clause1,'OR',clause2),)
  ##pepe['group']=('julia','claudia')
  ##pepe['having']=(('campo','=','345'),)
  #pepe['base_filter']=''
  #pepe['order']=(1,(2,'DESC'),3)
  #pprint(pepe)
  ##pepe['fields'] = '*'

  print(queryConstructor(**pepe))



#from datadict import *    
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

from datalayer.query_constructor import *


def traverse(root,base=None):
    if base is not None:
       yield base
       queue = base.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]             
    

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from util.tree import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.numeros import stats

from datalayer.datemgr import getDateIndex,getDateEntry
from pprint import *

from core import Cubo

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeCRUD import editaCombo
from dictmgmt.tableInfo import FQName2array

import cubebrowse as cb

import time

@keep_tree_layout()
def openContextMenu(cubeMgr,position):
    """
    """
    indexes = cubeMgr.view.selectedIndexes()
    if len(indexes) > 0:
        index = indexes[0]
        item = cubeMgr.baseModel.itemFromIndex(index)
    menu = QMenu()
    setMenuActions(menu,cubeMgr,item)
    action = menu.exec_(cubeMgr.view.viewport().mapToGlobal(position))
    #getContextMenu(item,action,self)

def setMenuActions(menu,context,item):      
    menuActions = []
    menuActions.append(menu.addAction("Manage",lambda:execAction(item,context,"manage")))

def execAction(item,context,action):
    if action == "manage" :
        context.model().beginResetModel()
        manage(item,context)
        context.model().endResetModel()

def info_cache(cubeMgr,cube_root):
    """
        esto realmente debe ser un metodo de cubeMgr.
        Debe añadirse uno si cambian datos claves del cubo (conexion y/o tabla)
    """
    cube_ref = cube_root.text()
    #
    # A partir de aqui podria guardarse como un cache
    #
    if not cubeMgr.cache.get(cube_ref):
        print('Nuevo en la plaza')
        tabla_ref = cube_root.getChildrenByName('table').getColumnData(1)
        conn_root = cube_root.getChildrenByName('connect')
        conn_dict = {'dbhost':conn_root.getChildrenByName('dbhost').getColumnData(1),
                    'dbname':conn_root.getChildrenByName('dbname').getColumnData(1),
                    'driver':conn_root.getChildrenByName('driver').getColumnData(1)
                    }

        dd=cubeMgr.dataDict
        
        confName,schema,tabla = FQName2array(tabla_ref)
        if confName == '':
            for conexion in dd.configData['Conexiones']:
                entrada = dd.configData['Conexiones'][conexion]
                match = True
                for entry in ('dbhost','dbname','driver'):
                    match = match and (entrada[entry] == conn_dict [entry])
                if match:
                    confName = conexion
                    confData = entrada
                    break
        else:
            confData = dd.configData['Conexiones'][confName]
        
        #TODO algo como esto deberia ser generico
        if schema == '':
            if confData['driver'] == 'sqlite':
                schema = 'main'
            elif confData['driver'] == 'mysql':
                schema = confData['dbname']
            elif confData['driver'] == 'postgresql':
                schema = 'public'
            elif confData['driver'] == 'oracle':
                schema = confData['dbuser']
        
        tabInfo = TableInfo(dd,confName,schema,tabla,2)
        info = tabInfo.lista
        cubeMgr.cache[cube_ref] = {'confName':confName,
                                   'confData':confData,
                                   'schema':schema,
                                   'tabla':tabla,
                                   'tabla_ref':tabla_ref,
                                   'info':info }
    # fin del proceso de cache
    return cubeMgr.cache[cube_ref]

def manage(item,cubeMgr):
    '''
       item    -> cubeTree item
       cubeMgr -> cubeMgr actual
    '''

    tipo = item.type()
    texto = item.text()
    valor = item.getColumnData(1)

    cube_root = item
    while cube_root.type() not in ('base','default_base'):
        cube_root = cube_root.parent()
    if cube_root.type() == 'default base':
        return

    cube_ref = cube_root.text()
    cache_data = info_cache(cubeMgr,cube_root)
    #confName =cache_data['confName']
    #confData =cache_data['confData']
    #schema = cache_data['schema']
    #tabla  = cache_data['tabla']
    #tabla_ref = cache_data['tabla_ref']
    #info = cache_data['info']
    
    if tipo in TYPE_LEAF:
        resultado = leaf_management(item,cubeMgr,cube_root,cube_ref,cache_data)
    else:
        print(tipo,item.text(),item.getColumnData(1))
        resultado = block_management(item,cubeMgr,cube_root,cube_ref,cache_data)

    #if tipo in COMPLEX_TYPES:
        #pprint(tree2dict(item,isDictionaryEntry))
    #else:
        #print('\t{}:{} ({})'.format(item.type(),item.text(),item.getColumnData(1)))
    ##pprint(tree2dict(item,isDictionaryEntry))
    #pprint(item.typeHierarchy())

def block_management(obj,cubeMgr,cube_root,cube_ref,cache_data):
    pass
def preparaCombo(obj,valueTable,valorActual):
    descriptivo = False
    if isinstance(valueTable[0],(list,tuple,set)):
        descriptivo = True
        comboList = [ item[1] for item in valueTable ]
        claveList = [ str(item[0]) for item in valueTable ]
    else:
        claveList = comboList = tuple(valueTable)

    if valorActual:
        try:
            values = [ claveList.index(valorActual), ]
        except ValueError:
            if descriptivo:
                comboList.append(valorActual)
            claveList.append(valorActual)
            values = [ len(claveList) -1 ]
    else:
        values = [ 0 , ]
    return comboList,claveList,values

def getInputWidget(obj,cubeMgr,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    modo = action_class(obj)
    value = obj.getColumnData(1)
    comboList = None
    claveList = None
    descriptivo = False
    
    if  modo == 'input':
        texto = 'Edite '+obj.text()
        widget = QLineEdit
        options = None
        values = [ value , ]
        #text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,value)
        #result = text[0]
    elif modo == 'static combo':
        texto = 'Seleccione '+obj.text()
        widget = QComboBox
        options = None
        array = STATIC_COMBO_ITEMS[tipo]
        descriptivo = True if isinstance(array[0],(list,tuple,set)) else False
        comboList,claveList,defValue= preparaCombo(obj,array,value)
    elif modo == 'dynamic combo':
        texto = 'Seleccione '+obj.text()
        widget = QComboBox
        options = {'setEditable':True}
        array = prepareDynamicArray(obj,cubeMgr,cube_root,cube_ref,cache_data)
        descriptivo = True if isinstance(array[0],(list,tuple,set)) else False
        if array:
           comboList,claveList,values= preparaCombo(obj,array,value)
    specs = (texto,widget,options,comboList,claveList,descriptivo)
    return specs,values

def leaf_management(obj,cubeMgr,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    modo = action_class(obj)
    value = obj.getColumnData(1)
    specs,values = getInputWidget(obj,cubeMgr,cube_root,cube_ref,cache_data)
    
    result = None
    context = []
    context.append(specs[0:3])

    parmDialog = propertySheetDlg('Edite '+obj.text(),context,values)
    if parmDialog.exec_():
        retorno = parmDialog.sheet.values()[0]
        if specs[0][1] == QLineEdit :
            result = retorno
        elif specs[0][5]: #descriptivo
            comboList = specs[0][3]
            claveList = specs[0][4]
            if parmDialog.sheet.cellWidget(0,0).currentText() != comboList[retorno]:
                result = parmDialog.sheet.cellWidget(0,0).currentText()
            else:
                result = claveList[retorno] 
        else:
           result = parmDialog.sheet.cellWidget(0,0).currentText()  #pues no lo tengo tan claro
    print(result)

    #if result:    
        #if tipo in TYPE_LIST and action == 'add':
            #insertInList(obj,tipo,result)
        #else:
            #if result and result != value:
                #obj.setColumnData(1,result,Qt.EditRole) 
    
def leaf_management_old(obj,cubeMgr,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    modo = action_class(obj)
    value = obj.getColumnData(1)

    if  modo == 'input':
        text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,value)
        result = text[0]
    elif modo == 'static combo':
        array = STATIC_COMBO_ITEMS[tipo]
        result = editaCombo(obj,array,value)
    elif modo == 'dynamic combo':
        array = prepareDynamicArray(obj,cubeMgr,cube_root,cube_ref,cache_data)
        if array:
            result = editaCombo(obj,array,value)
    print(result)
    #if result:    
        #if tipo in TYPE_LIST and action == 'add':
            #insertInList(obj,tipo,result)
        #else:
            #if result and result != value:
                #obj.setColumnData(1,result,Qt.EditRole) 

def prepareDynamicArray(obj,cubeMgr,cube_root,cube_ref,cache_data):
    
    #los campos
    tipo = obj.type()
    if tipo == 'table':
        #restringimos a las del mismo esquema
        dd=cubeMgr.dataDict
        conn = dd.getConnByName(cache_data['confName'])
        schema = conn.getChildrenByName(cache_data['schema'])
        hijos = schema.listChildren()
        array = [ (item.fqn(),item.text()) for item in hijos ]
        #TODO normalizar el valor actual
    elif tipo in ('elem','base_elem','fields','code','desc','grouped by','base_elem','rel_elem'):
        # primero determinamos de que tabla hay que extraer los datos
        if tipo in ('elem','fields'):
            tabla_campos = cache_data['tabla_ref']
        elif tipo in ('code','desc','grouped by'):
            pai = obj
            while pai.type() != 'domain':
                pai = pai.parent()
            tabla_campos = pai.getChildrenByName('table').getColumnData(1)
            pass
        elif tipo in ('base_elem',):
            pai = obj
            while pai.type() != 'link via':
                pai = pai.parent()
            indice = int(pai.text())
            if indice == 0:
                tabla_campos = cache_data['tabla_ref']
            else:
                indice -= 1
                siguiente = pai.getBrotherByName(str(indice))
                tabla_campos = siguiente.getChildrenByName('table').getColumnData(1)
        elif tipo in ('rel_elem',):
            pai = obj
            while not (pai.type() == 'clause' and pai.text() == 'clause' ):
                pai = pai.parent()
                if not pai:
                    return None
            tabla_campos = pai.getBrotherByName('table').getColumnData(1)
        # normalizamos el nombre de la tabla (añadiendo el esquema si es necesario).
        # es un pequeño fastido pero no hay manera de garantizar que los datos esten bien en origen
        print(tabla_campos)
        conexion,esquema,tabName = FQName2array(tabla_campos)
        if esquema == '':
            esquema = cache_data['schema']
        tabla_campos = '{}.{}'.format(esquema,tabName)
        # obtenemos la lista de campos
        #TODO falta por evaluar que ocurre si el fichero no esta en el cache de datos
        if tipo != 'fields':
            array = [ (item['name'],item['basename']) for item in cache_data['info'][tabla_campos]['Fields'] ]
        else:
            array = [ (item['name'],item['basename']) 
                     for item in cache_data['info'][tabla_campos]['Fields'] 
                     if item['format'] in ('entero','numerico')
                     ]
        #TODO normalizar el valor actual
    # las referencias en el default
    elif tipo in ('row','col','elemento'): 
        # identificamos el cubo de defecto
        pai = obj.parent()
        if pai.type() != 'vista': #no deberia ocurrir
            return None
        refCubeName = pai.getBrotherByName('cubo')
        refCube = None
        for cubo in getCubeItemList(cubeMgr.hidden_root):
            if cubo.text() == refCubeName:
                refCube = cubo
                break
        if refCube:
            if tipo == 'elemento':
                guidemaster = childByName(refCube,'fields')
                array = getDataList(guidemaster,1) 
            else:
                guidemaster = childByName(refCube,'guides')
                nombres = getItemList(guidemaster,'guides')
        else:
            return None
    elif tipo == 'cubo':
        array = getCubeList(cubeMgr.hiddenRoot)
    else:
        print('Edit dynamic sin regla',obj,tipo)
    return array

def miniCube():

    app = QApplication(sys.argv)
    win = QMainWindow()
    confName = 'Pagila'
    schema = 'public'
    table = 'rental'
    dataDict=DataDict(conName=confName,schema=schema)
    cubo = info2cube(dataDict,confName,schema,table,3)   
    cubeMgr = cb.CubeMgr(win,confName,schema,table,dataDict,rawCube=cubo)
    cubeMgr.cache = dict()  #OJO OJO OJO
    cubeMgr.view.setContextMenuPolicy(Qt.CustomContextMenu)
    cubeMgr.view.customContextMenuRequested.disconnect()
    #print('desconectada')
    cubeMgr.view.customContextMenuRequested.connect(lambda i,j=cubeMgr:openContextMenu(j,i))

    cubeMgr.expandToDepth(1)        
    #if self.configSplitter.count() == 1:  #de momento parece un modo sencillo de no multiplicar en exceso
    win.setCentralWidget(cubeMgr)
    win.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    win.show()
    app.exec_()
    exit()


from widgets import *    
            
class WzConnect(QWizardPage):
    def __init__(self,parent=None):
        super(WzConnect,self).__init__(parent)
        nombre = None
        data = None
        context = (
                ('Nombre',QLineEdit,{'setReadOnly':True} if nombre is not None else None,None,),
                # driver
                ("Driver ",QComboBox,None,DRIVERS,),
                ("DataBase Name",QLineEdit,None,None,),
                ("Host",QLineEdit,None,None,),
                ("User",QLineEdit,None,None,),
                ("Password",QLineEdit,{'setEchoMode':QLineEdit.Password},None,),
                ("Port",QLineEdit,None,None,),
                ("Debug",QCheckBox,None,None,)
            )
        self.sheet=WPropertySheet(context,data)
        
        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)

        meatLayout = QVBoxLayout()
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
        
        self.setLayout(meatLayout)

    def initializePage(self):
        pass

class WzBaseFilter(QWizardPage):
    def __init__(self,parent=None):
        super(WzBaseFilter,self).__init__(parent)
        numrows = 5
        context=[]
        fieldList = ['','Uno','Dos','Tres']
        context.append(('campo','condicion','valores'))
        context.append((QComboBox,None,fieldList))
        context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        context.append((QLineEdit,None,None))

        self.sheet = WDataSheet(context,numrows)
        self.editArea = QPlainTextEdit()
        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)
        meatLayout.addWidget(self.editArea,5,0,8,0)
        
        self.setLayout(meatLayout)
        
    def initializePage(self):
        pass

class WzDateFilter(QWizardPage):
    def __init__(self,parent=None):
        super(WzDateFilter,self).__init__(parent)
        numrows = 5
        context = []
        fieldList = ['','Uno','Dos','Tres']
        context.append(('campo','Clase','Rango','Numero','Desde','Hasta'))
        context.append((QComboBox,None,fieldList))
        context.append((QComboBox,None,CLASES_INTERVALO))
        context.append((QComboBox,None,TIPOS_INTERVALO))
        context.append((QSpinBox,{"setRange":(1,366)},None,1))
        context.append((QLineEdit,{"setEnabled":False},None))
        context.append((QLineEdit,{"setEnabled":False},None))
        self.sheet=self.sheet = WDataSheet(context,numrows)

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)
        
        self.setLayout(meatLayout)

    def initializePage(self):
        pass
   
class WzFieldList(QWizardPage):
    def __init__(self,parent=None):
        super(WzFieldList,self).__init__(parent)
        fieldList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in fieldList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass
   
class WzGuideList(QWizardPage):
    def __init__(self,parent=None):
        super(WzGuideList,self).__init__(parent)
        guideList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in guideList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass


class MiniWizard(QWizard):
    def __init__(self):
        super(MiniWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.diccionario = {'alfa':'omega'}
        self.setPage(1, WzConnect())
        self.setPage(2, WzBaseFilter())
        self.setPage(3, WzDateFilter())
        self.setPage(4, WzFieldList())
        self.setWindowTitle('Tachan')
        self.show()

class Wz1(QWizardPage):
    def __init__(self,parent=None):
        super(Wz1,self).__init__(parent)
        self.contador = 0
        label =QLabel('alfa')
        self.value = QLineEdit()
        self.value.editingFinished.connect(self.modificaValue)
        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.value, 0, 1)
        self.setLayout(layout)
        self.registerField('alfa', self.value)

    def initializePage(self):
        self.value.setText(self.wizard().diccionario['alfa'])
        self.contador += 1

    def modificaValue(self):
        if self.value.isModified():
            self.wizard().diccionario['alfa']=self.value.text()
        
    
class Wz2(QWizardPage):
    def __init__(self,parent=None):
        super(Wz2,self).__init__(parent)
        self.contador = 0
    def initializePage(self):
        self.contador += 1
        self.wizard().diccionario[self.contador] = 'iteracion' + str(self.contador)

class Wz3(QWizardPage):
    def __init__(self,parent=None):
        super(Wz3,self).__init__(parent)

        linkLabel = QLabel("¿Quiere volver a empezar?")
        self.linkCheck = QCheckBox()
        linkLabel.setBuddy(self.linkCheck)
        self.linkCheck.stateChanged.connect(self.estadoLink)
        

        layout = QGridLayout()
        layout.addWidget(linkLabel,0,0)
        layout.addWidget(self.linkCheck,0,1)
        self.setLayout(layout)

        self.contador = 0
    
    def estadoLink(self):
        if self.linkCheck.isChecked():
            self.wizard().setStartId(2);
            self.wizard().restart()        
    def initializePage(self):
        self.contador += 1

class Wz4(QWizardPage):
    def __init__(self,parent=None):
        super(Wz4,self).__init__(parent)
        self.contador = 0
    def initializePage(self):
        self.contador += 1
        


def miniWizard():
    
    app = QApplication(sys.argv)
    wizard = MiniWizard()        
    if wizard.exec_() :
        print(wizard.page(1).value.text())
        #print('Milagro',wizard.page(1).contador,wizard.page(2).contador,wizard.page(3).contador)
        print(wizard.diccionario)
        exit()

if __name__ == '__main__':
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    #app = QApplication(sys.argv)
    miniCube()
    #miniWizard()
