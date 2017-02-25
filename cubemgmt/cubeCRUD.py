#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from cubemgmt.cubetree  import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeutil  import *
from cubemgmt.guideWizard import *

from util.decorators import *

from widgets import WDataSheet
from dialogs import propertySheetDlg
from PyQt5.QtWidgets import QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox, QSpinBox
    
    
def editTableElem(exec_object,obj,valor,refTable=None):
    lista = getFldTable(exec_object,obj,refTable)
    if lista:
        array = [ (item[0],item[1],)  for item in lista ]
        result = editaCombo(obj,array,valor)
        return result
    else:
       return None
    ##TODO determinar que es lo que necesito hacer cuando no esta disponible
    ##TODO  Unificar con la de abajo
    ##TODO base elem probablemente trasciende esta definicion
    ##TODO calcular dos veces FQ ... es un exceso. simplificar
    #FQtablaArray,connURL = getCubeTarget(obj)
    #if refTable:
        #FQtablaArray = FQName2array(refTable.getColumnData(1))
    ##print(FQtablaArray,connURL)
    #actConn = connMatch(exec_object.dataDict,connURL)
    #if actConn:
        #tableItem = actConn.findElement(FQtablaArray[1],FQtablaArray[2])
        #if tableItem:
            #fieldIdx = childByName(tableItem,'FIELDS')
            ##array = getDataList(fieldIdx,0)
            #array = [ (item.fqn(),item.text(),)  for item in fieldIdx.listChildren() ]
            #result = editaCombo(obj,array,valor)
            #return result
        #else:
            #print(connURL,'ESTA DISPONIBLE y el fichero NOOOOOR')
    #else:
        #print(connURL,'NO ESTA A MANO')
    #return None

def editaCombo(obj,valueTable,valorActual):
    # No es exactamente así
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
    #if descriptivo and valorActual:
        #try:
            #values = [ claveList.index(valorActual), ]
        #except ValueError:
            #comboList.append(valorActual)
            #claveList.append(valorActual)
            #values = [ len(claveList) -1 ]
    #elif descriptivo:
        #values = [ None , ]
    #else:
        #values = [ claveList.index(valorActual), ]

    spec = []
    spec.append(('Seleccione',QComboBox,{'setEditable':True},comboList))

    parmDialog = propertySheetDlg('Defina '+obj.text(),spec,values)
    if parmDialog.exec_():
        #print(values[0],parmDialog.sheet.cellWidget(0,0).currentText())
        if descriptivo:
            if parmDialog.sheet.cellWidget(0,0).currentText() != comboList[values[0]]:
                return parmDialog.sheet.cellWidget(0,0).currentText()
            else:
                return claveList[values[0]] 
        else:
            return parmDialog.sheet.cellWidget(0,0).currentText()  #pues no lo tengo tan claro
    
def addDefault(obj,exec_object):
    #TODO cuando existe default cargar valores como defecto
    #print('Procesar Default')
    spec_d = []
    parray=[]
    listCubes=['', ]+getCubeList(exec_object.hiddenRoot) 
    def getContext(idx):
        """
            La funcion esta embebida para poder mantener el contexto (exec_object en concreto)
        """
        cubo = childByName(exec_object.hiddenRoot,listCubes[idx])
        guias,campos = getCubeInfo(cubo)
        for k in range(1,5):
            parmDialog_d.sheet.cellWidget(k,0).setEnabled(True)
            if k == 1:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(guias)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
            elif k == 2:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(guias)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
            elif k == 4:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(campos)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
                
    spec_d.append(('Seleccione el cubo a utilizar',QComboBox,None,tuple(listCubes)))
    spec_d.append(('Guia filas',QComboBox,{'setEnabled':False},tuple(parray)),)
    spec_d.append(('Guia columnas',QComboBox,{'setEnabled':False},tuple(parray)),)
    spec_d.append(('Función agregacion',QComboBox,{'setEnabled':False},tuple(AGR_LIST)),)
    spec_d.append(('Campo de datos',QComboBox,{'setEnabled':False},tuple(parray)),)
    values_d = [ None for k in range(len(spec_d))]
    parmDialog_d = propertySheetDlg('Defina el cubo a generar',spec_d,values_d,exec_object)
    parmDialog_d.sheet.cellWidget(0,0).currentIndexChanged[int].connect(getContext)
    
    if parmDialog_d.exec_():
        defaultBase = childByName(exec_object.hiddenRoot,'default')
        if defaultBase:
            defaultBase.suicide()
        defaultBase = exec_object.hiddenRoot
        defaultBase.insertRow(0,(CubeItem(str('default')),CubeItem(str('')),CubeItem(str('default_base')),))
        padre = defaultBase.child(0)
        dato =parmDialog_d.sheet.cellWidget(0,0).currentText()
        padre.appendRow((CubeItem(str('cubo')),CubeItem(str(dato)),CubeItem(str('cubo')),))
        padre.appendRow((CubeItem(str('vista')),CubeItem(str('')),CubeItem(str('vista')),))
        vista = padre.lastChild()
        vista.appendRow((CubeItem(str('col')),CubeItem(str(values_d[1])),CubeItem(str('col')),))
        vista.appendRow((CubeItem(str('row')),CubeItem(str(values_d[2])),CubeItem(str('row')),))
        dato =parmDialog_d.sheet.cellWidget(3,0).currentText()
        vista.appendRow((CubeItem(str('agregado')),CubeItem(str(dato)),CubeItem(str('agregado')),))
        dato =parmDialog_d.sheet.cellWidget(4,0).currentText()
        vista.appendRow((CubeItem(str('elemento')),CubeItem(str(dato)),CubeItem(str('elemento')),))
    
def addBase(obj,exec_object):
    spec = []
    spec.append(('Intruduzca el nombre del nuevo cubo',None,None,))
    array=getListAvailableTables(obj,exec_object)
    spec.append(('Seleccione la tabla a utilizar',QComboBox,None,tuple(array)))
    spec.append(('Profundidad de enlaces',QSpinBox,{"setRange":(1,5)}),)
    values = [ None for k in range(len(spec))]
    values[2] = 2 #para los niveles de profundidad
    parmDialog = propertySheetDlg('Defina el cubo a generar',spec,values,exec_object)
    if parmDialog.exec_():
        if values[0] :
            print('Proceso de alta')
            #FIXME todo este proceso para obtener el nombre de la conexion es un poco tremebundo
            FQtablaArray,connURL = getCubeTarget(obj)
            actConn = connMatch(exec_object.dataDict,connURL)
            connName = actConn.text()
            tabla = array[values[1]].split('.')
            schemaName= tabla[0] if len(tabla) > 1 else ''
            tableName = tabla[1] if len(tabla) > 1 else tabla[0]
            info = info2cube(exec_object.dataDict,connName,schemaName,tableName,values[2])
            for key in info:
                clave = key
                break
            dict2tree(exec_object.hiddenRoot,values[0],info[clave],'base')

    pass
    
def setContextMenu(obj,menu,exec_object=None):
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()

    obj.menuActions = []
    obj.menuActions.append(menu.addAction("Add ",lambda:execAction(exec_object,obj,"add")))
    obj.menuActions.append(menu.addAction("Edit ",lambda :execAction(exec_object,obj,"edit")))
    obj.menuActions.append(menu.addAction("Delete ",lambda: execAction(exec_object,obj,"delete")))
    obj.menuActions.append(menu.addAction("Copy ",lambda: execAction(exec_object,obj,"copy")))
    obj.menuActions.append(menu.addAction("Rename ",lambda: execAction(exec_object,obj,"rename")))
    obj.menuActions.append(menu.addAction("Refresh ",lambda: execAction(exec_object,obj,"refresh")))
    
    separador = False

    def setSeparador(separador):
        if not separador:
            obj.menuActions.append(menu.addSeparator())
            separador = True
    # tipos especiales    
    if tipo in ('base'): 
        obj.menuActions.append(menu.addSeparator())
        obj.menuActions.append(menu.addAction("Add another Cube",lambda: execAction(exec_object,obj,"add")))
        if 'default' not in getCubeList(exec_object.hiddenRoot,False):
            obj.menuActions.append(menu.addAction("Add Default View",lambda: execAction(exec_object,obj,"default_base")))
        
        if not obj.getChildrenByName('date filter'):
            setSeparador(separador)
            obj.menuActions.append(menu.addAction("Add date filter",lambda: execAction(exec_object,obj,"date filter")))
            obj.menuActions[-1].setEnabled(False) #hasta que no lo implemente
            
    
    if tipo in ('prod') and obj.text() != 'prod' and not obj.getChildrenByName('domain'):
            setSeparador(separador)
            obj.menuActions.append(menu.addAction("Add Domain Definition",lambda: execAction(exec_object,obj,"domain")))
    # acciones
    # add
    if tipo in NO_ADD_LIST:
        obj.menuActions[0].setEnabled(False)
    #edit
    if tipo in NO_EDIT_LIST :  
        obj.menuActions[1].setEnabled(False)

    if tipo not in  TYPE_LEAF :  #provisional
        obj.menuActions[1].setEnabled(False)

    if tipo in ('fields','case_sql') and obj.text() == tipo and obj.hasChildren():
        obj.menuActions[1].setEnabled(False)
    # delete    
    if tipo in NO_ADD_LIST:
        obj.menuActions[2].setEnabled(False)
    elif obj.text() in ITEM_TYPE :
        obj.menuActions[2].setEnabled(False)
    if obj.type() in ('default_base','domain','link_via','categories'):
        obj.menuActions[2].setEnabled(True)
    # copy
    obj.menuActions[3].setEnabled(False)
    # rename
    if obj.text() in ITEM_TYPE or obj.text() == "":
        obj.menuActions[4].setEnabled(False)
    # refresh
    if tipo in COMPLEX_TYPES :
        obj.menuActions[5].setEnabled(True)
    else:
        obj.menuActions[5].setEnabled(False)


        """
        FREE_FORM_ITEMS = set([
            -'base filter'# on base add
            *'case_sql',
            -'dbhost',    # on base add
            -'dbname',    # on base add
            -'dbpass',    # on base add
            -'dbuser',    # on base add
            -'default',   # created on default/ base add
            u'filter',    # free text
            #u'name',      # free text
            u'result',    # free text
            *'values',
            ])
        STATIC_COMBO_ITEMS = dict({
            - 'agregado': created on default
            u'class': GUIDE_CLASS ,
            u'condition': LOGICAL_OPERATOR,
            u'driver': DRIVERS,
            u'enum_fmt': ENUM_FORMAT,
            u'fmt': ENUM_FORMAT,
            u'type': TIPO_FECHA,
            })

        DYNAMIC_COMBO_ITEMS = set([
            *'base_elem', #             field of  Reference  table
            *'code',      #             field of FK table (key)
            -'col',       # created on default
            -'cubo',      # created on default
            *'desc',       #             field of FK table (values)
            *'elem',      #              field of table, or derived value 
            -'elemento',  # created on default
            *'fields',
            *'grouped by',#              field of FK table or derived value ??
            *'rel_elem',  #              field of FK table
            -'row',       # created on default
            u-'table',    #on base add
            ])

        """
        

def getDynamicArray(tipo,obj,exec_object):
    # los campos
    if tipo in ('elem','base_elem','fields','code','desc','grouped by','rel_elem'):
        # determinamos la tabla a consultar
        if tipo in ('code','desc','grouped by') :
            refTable = obj.getBrotherByName('table')
            nomTabla = refTable.getColumnData(1)
        elif tipo in ('rel_elem',):
            pai = obj.parent()
            while pai.type() and pai.type() != 'link via':
                pai = pai.parent()
            refTable  = childByName(pai,'table')
        else:
            refTable = None
        # obtenemos los campos
        lista = getFldTable(exec_object,obj,refTable)
        if lista:
            array = [ (item[0],item[1],)  for item in lista ]
        else:
            return None
    # las referencias en el default
    elif tipo in ('row','col','elemento'): 
        # identificamos el cubo de defecto
        pai = obj.parent()
        if pai.type() != 'vista':
            return None
        cubeItem = pai.getBrotherByName('cubo')
        cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
        if tipo == 'elemento':
            guidemaster = childByName(cubo,'fields')
            array = getDataList(guidemaster,1) 
        else:
            guidemaster = childByName(cubo,'guides')
            nombres = getItemList(guidemaster,'guides')
            array = [ (k,nombres) for k,nombres in enumerate(nombres) ]
            
    elif tipo == 'cubo':
        array = getCubeList(exec_object.hiddenRoot)
    else:
        print('Edit dynamic sin regla',obj,tipo)
    return array

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
    
@keep_tree_layout(0)
@model_change_control(1)
def execAction(exec_object,obj,action):
    #TODO listas editables en casi todos los elementos
    if action is None:
        return
    
    #modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    if not tipo:
        print('NO tiene tipo',obj.getDataList())
        
    #modelo.beginResetModel()
    if action in ('add','edit'):
        result = None
        if tipo in TYPE_LEAF:
            modo = action_class(obj)
        
            if action == 'edit':
                value = obj.getColumnData(1)
            else:
                value = None
                
            if  modo == 'input':
                text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,value)
                result = text[0]
            elif modo == 'static combo':
                array = STATIC_COMBO_ITEMS[tipo]
                result = editaCombo(obj,array,value)
            elif modo == 'dynamic combo':
                array = getDynamicArray(tipo,obj,exec_object)
                if array:
                    result = editaCombo(obj,array,value)
            if result:    
                if tipo in TYPE_LIST and action == 'add':
                    insertInList(obj,tipo,result)
                else:
                    if result and result != value:
                        obj.setColumnData(1,result,Qt.EditRole) 

        else:
            #
            if tipo == 'domain':  #  
                result = guideWizard(exec_object,obj)
                if result:
                    pass
            if tipo == 'date filter':
                pass
            elif tipo == 'default_base':
                addDefault(obj,exec_object)
            elif tipo == 'base':  #No admite edit directamente (lo logico)
                if action == 'add':
                    addBase(obj,exec_object)
            elif tipo in ('prod','guides'):
                # siempre añade la regla de produccion al final
                #TODO quizas en domain deba subir un elemento
                if action == 'add':
                    result = guideWizard(exec_object,obj)
                    if result:
                        if obj.text() != tipo:
                            #add a new array entry
                            idx = obj.index()
                            pai = obj.parent()
                        else:
                            pai = obj
                        nombre = result.get('name',pai.rowCount())
                        dict2tree(pai,nombre,result,tipo)
            elif tipo == 'categories':
                result = guideWizard(exec_object,obj)
                del result['class']  #no lo necesito, de momento
                if result:
                    pai = obj.parent()
                    while not pai.type() == 'prod':
                        pai = pai.parent()
                    for entry in result:
                        item = pai.getChildrenByName(entry)
                        if item:
                            item.suicide()
                        dict2tree(pai,entry,result[entry],entry)
                pass
            elif tipo == 'connect':  # will not be honored
                pass
            elif tipo == 'link via':
                pass
            elif tipo == 'clause':
                pass
            elif tipo == 'vista': # will not be honored
                pass

            print ('no implementado todavia')

    elif action == 'delete' :
        if obj.type() == 'base': #no puedo borrarlo pero si vaciarlo, es un probleam de logica. ver cubebrowewin.close()
            indice = obj.index()
            while obj.hasChildren():
                obj.model().item(indice.row()).removeRow(0)
            obj.setEnabled(False)
        else:
            obj.suicide()
        pass  # close connection, delete tree, delete config
    elif action == 'copy':
        pass
    elif action == 'rename':
        text = QInputDialog.getText(None, "Renombrar el nodo :"+obj.text(),"Nodo", QLineEdit.Normal,obj.text())
        obj.setData(text[0],Qt.EditRole)
        nombre = obj.getChildrenByName('name')
        if nombre:
            obj.setColumnData(1,text[0],Qt.EditRole)
        else:
            obj.appendRow((CubeItem('name'),CubeItem(text[0],)))
    elif action == 'refresh':
        pass
    elif action == 'date filter':
        pass
    else:
        pass
    #modelo.endResetModel()
 
