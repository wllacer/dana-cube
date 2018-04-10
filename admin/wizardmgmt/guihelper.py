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

  
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

#def traverse(root,base=None):
    #if base is not None:
       #yield base
       #queue = base.listChildren() 
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = queue[0].listChildren() 
        #if expansion is None:
            #del queue[0]
        #else:
            #queue = expansion  + queue[1:]             
    
import base.config as config

#from support.util.record_functions import *
#from base.tree import *

#from support.datalayer.access_layer import *
#from support.datalayer.query_constructor import *

#from support.util.numeros import stats

#from support.datalayer.datemgr import getDateIndex,getDateEntry
#from pprint import *

#from base.core import Cubo

from admin.cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from base.cubetree import CubeItem
from admin.cubemgmt.cubeTypes import *
#from admin.cubemgmt.cubeCRUD import insertInList
from admin.dictmgmt.tableInfo import FQName2array,TableInfo

from support.gui.dialogs import propertySheetDlg
import support.gui.widgets import WMultiCombo
#import cubebrowse as cb

#import time

def insertInList(obj,tipo,value):
    if not obj.text():
        #ya es un array; solo hay que añadir elementos
        idx = obj.index()
        pai = obj.parent()
        pai.insertRow(idx.row()+1,(CubeItem(None),CubeItem(str(value)),CubeItem(tipo)))
    elif not obj.getColumnData(1):
        #hablamos del padre. Solo hay que añadir un hijo
        obj.appendRow((CubeItem(None),CubeItem(str(value)),CubeItem(tipo)))
        pass
    else: # <code> : <valor>
        #creo un elemento array hijo copiado del actual
        #borro el contenido del original
        #creo un nuevo registro
        #oldRecord = [ CubeItem(obj.getColumnData[k]) for k in range(1,obj.columnCount()) ]
        #oldRecord.insert(0,CubeItem(None))
        #pprint(oldRecord)
        obj.appendRow((CubeItem(None),CubeItem(obj.getColumnData(1)),CubeItem(obj.getColumnData(2))))
        #obj.appendRow(oldRecord)
        obj.appendRow((CubeItem(None),CubeItem(str(value)),CubeItem(tipo)))
        obj.setColumnData(1,None,Qt.EditRole)
        pass

def preparaCombo(obj,valueTable,valorActual):
    descriptivo = False
    if isinstance(valueTable[0],(list,tuple,set)):
        descriptivo = True
        comboList = [ item[1] for item in valueTable ]
        claveList = [ str(item[0]) for item in valueTable ]
    else:
        claveList = comboList = list(valueTable)

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
    data = []
    if  modo == 'input':
        texto = 'Edite '+obj.text()
        widget = QLineEdit
        options = None
        data = [ value , ]
        #text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,value)
        #result = text[0]
    elif modo == 'static combo':
        texto = 'Seleccione '+obj.text()
        widget = QComboBox
        options = None
        array = STATIC_COMBO_ITEMS[tipo]
        descriptivo = True if isinstance(array[0],(list,tuple,set)) else False
        comboList,claveList,data= preparaCombo(obj,array,value)
    elif modo == 'dynamic combo':
        texto = 'Seleccione '+obj.text()
        widget = QComboBox
        options = {'setEditable':True}
        array = prepareDynamicArray(obj,cubeMgr,cube_root,cube_ref,cache_data)
        descriptivo = True if isinstance(array[0],(list,tuple,set)) else False
        if array:
           comboList,claveList,data= preparaCombo(obj,array,value)
    specs = (texto,widget,options,comboList,claveList,descriptivo)
    return specs,data


def getAvailableTables(cubeMgr,cache_data):
    #restringimos a las del mismo esquema
    dd=cubeMgr.dataDict
    conn = dd.getConnByName(cache_data['confName'])
    schema = conn.getChildrenByName(cache_data['schema'])
    if schema is None: #Puede ocurrir en algunos casos de manipulacion
        return ['',]
    hijos = schema.listChildren()
    array = [ (item.fqn(),item.text()) for item in hijos ]
    return array
    
def getFieldsFromTable(fqn_table_name,cache_data,cube,tipo_destino=None):
    # obtenemos la lista de campos
    if fqn_table_name not in cache_data['info']:
        basename = fqn_table_name.split('.')[-1]
        tmpTabInfo = TableInfo(cube.dataDict,cache_data['confName'],cache_data['schema'],basename,maxlevel=0)
        for key in tmpTabInfo.lista:
            cache_data['info'][key] = tmpTabInfo.lista[key] #FIXME no seria mas rentable un deepcopy ?
        
    if tipo_destino == 'fields':
        array = [ (item['name'],item['basename']) 
                    for item in cache_data['info'][fqn_table_name]['Fields'] 
                    if item['format'] in ('entero','numerico')
                    ]
    elif tipo_destino == 'fmt':
        array = [ (item['name'],item['basename'],item['format']) 
                    for item in cache_data['info'][fqn_table_name]['Fields'] 
                    ]
    else:
        array = [ (item['name'],item['basename']) for item in cache_data['info'][fqn_table_name]['Fields'] ]    
    return array

def prepareDynamicArray(obj,cubeMgr,cube_root,cube_ref,cache_data):
    #los campos
    tipo = obj.type()
    if tipo == 'table':
        #restringimos a las del mismo esquema
        array = getAvailableTables(cubeMgr,cache_data)
        
        #TODO normalizar el valor actual
    elif tipo in ('elem','base_elem','fields','code','desc','grouped by','base_elem','rel_elem'):
        # primero determinamos de que tabla hay que extraer los datos
        if tipo in ('elem',):
            join = obj.getBrotherByName('link via')
            if join:
                joinelem = join.listChildren()[-1] #eso obliga a una disciplina
                tabla_campos  = joinelem.getChildrenByName('table').getColumnData(1)
            else:
                tabla_campos = cache_data['tabla_ref']
        if tipo in ('fields'):
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
            #indice = int(pai.text())
            indice = pai.getPos()
            if indice == 0:
                tabla_campos = cache_data['tabla_ref']
            else:
                indice -= 1
                #siguiente = pai.getBrotherByName(str(indice))
                siguiente = pai.parent().getChildByPos(indice)
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
        conexion,esquema,tabName = FQName2array(tabla_campos)
        if esquema == '':
            esquema = cache_data['schema']
        tabla_campos = '{}.{}'.format(esquema,tabName)
        array = getFieldsFromTable(tabla_campos,cache_data,cubeMgr,tipo)

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
    elif tipo == 'mask':  #dinamico para que sea editable
        return TIPO_FECHA
    else:
        print('Edit dynamic sin regla',obj,tipo)
    return array

def setAddComboElem(dataValue,widget,codeArray,descArray,offset=0):
    """ Añadir elementos a un combo editabe con dos arrays (uno para el codigo y otro el texto
    fieldValue  la entrada
    widget      al combo que vamos a tratar
    codeArray   valores internos
    descArray   valores presentacion
    offset      por si es necesario para los espacios en blanco
    """
    #FIXME codigo trapacer para evitar problemas con arrays
    if not dataValue:
        return None
    fieldValue = norm2String(dataValue)
    if isinstance(widget,WMultiCombo):
        widget.set(fieldValue)
        return
    try:
        if '.' in fieldValue:
            pos = codeArray.index(fieldValue)
        else:
            pos = descArray.index(fieldValue)
        widget.setCurrentIndex(pos +offset)  #FIXME
        widget.setStyleSheet("")
    except ValueError:
        widget.addItem(fieldValue)
        codeArray.append(fieldValue)
        descArray.append(fieldValue)
        widget.setCurrentIndex(widget.count() -1)
        widget.setStyleSheet("background-color:yellow;")
        pos = -1
    return pos + offset

def setAddQListElem(fieldValue,widget,codeArray,descArray,offset=0):
    """ Añadir elementos a un QListWidget editabe con dos arrays (uno para el codigo y otro el texto
    fieldValue  la entrada
    widget      al QListWidget que vamos a tratar
    codeArray   valores internos
    descArray   valores presentacion
    offset      por si es necesario para los espacios en blanco
    """
    
    try:
        idx = codeArray.index(fieldValue)
        #entry = widget.model().itemFromIndex(idx)
    except ValueError:
        try:
            idx = descArray.index(fieldValue)
        except ValueError:
            widget.addItem(fieldValue)
            idx= widget.count() -1
            #select fieldValue
            descArray.append(fieldValue)
            codeArray.append(fieldValue)
            #entry = widget.model().itemFromIndex(idx)
    selfieldValue = widget.item(idx)
    selfieldValue.setSelected(True)
