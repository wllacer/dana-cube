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
    

DEBUG = True
TRACE=True
DELIMITER=':'

#from util.record_functions import *
#from util.tree import *

#from datalayer.access_layer import *
#from datalayer.query_constructor import *

#from util.numeros import stats

#from datalayer.datemgr import getDateIndex,getDateEntry
#from pprint import *

#from core import Cubo

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
#from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeCRUD import insertInList
from dictmgmt.tableInfo import FQName2array,TableInfo

from dialogs import propertySheetDlg

#import cubebrowse as cb

#import time

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

def leaf_management(obj,cubeMgr,action,cube_root,cube_ref,cache_data):
    tipo = obj.type()
    modo = action_class(obj)
    if action == 'edit':
        value = obj.getColumnData(1)
    else:
        value = None
        
    specs,values = getInputWidget(obj,cubeMgr,cube_root,cube_ref,cache_data)
    
    result = None
    context = []
    context.append(specs[0:4])

    parmDialog = propertySheetDlg('Edite '+obj.text(),context,values)
    if parmDialog.exec_():
        retorno = parmDialog.sheet.values()[0]
        
        if specs[1] == QLineEdit :
            result = retorno
        elif specs[5]: #descriptivo
            comboList = specs[3]
            claveList = specs[4]
            #print(retorno,comboList,claveList)
            # en un combo tengo que tener cuidado que no se hayan añadido/modificado
            # entradas durante la ejecucion (p.e de campo a funcion(campo)
            if retorno >= len(comboList):  #nueva entrada dinamica en el combo
                result = parmDialog.sheet.cellWidget(0,0).currentText() 
            elif parmDialog.sheet.cellWidget(0,0).currentText() != comboList[retorno]:
                result = parmDialog.sheet.cellWidget(0,0).currentText()
            else:
                result = claveList[retorno] 
        else:
           result = parmDialog.sheet.cellWidget(0,0).currentText()  #pues no lo tengo tan claro
   

    if result:    
        if tipo in TYPE_LIST and action == 'add':
            insertInList(obj,tipo,result)
        else:
            if result and result != value:
                obj.setColumnData(1,result,Qt.EditRole) 
    # efectos secundarios
    # 1) referencia en conexion
    # 2) table name
    #

def getAvailableTables(cubeMgr,cache_data):
    #restringimos a las del mismo esquema
    dd=cubeMgr.dataDict
    conn = dd.getConnByName(cache_data['confName'])
    schema = conn.getChildrenByName(cache_data['schema'])
    hijos = schema.listChildren()
    array = [ (item.fqn(),item.text()) for item in hijos ]
    return array
    
def getFieldsFromTable(fqn_table_name,cache_data,cube,tipo_destino=None):
    # obtenemos la lista de campos
    #TODO falta por evaluar que ocurre si el fichero no esta en el cache de datos
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
