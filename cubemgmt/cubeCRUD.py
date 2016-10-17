#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from cubemgmt.cubetree  import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeutil  import *


    
def editTableElem(exec_object,obj,valor,refTable=None):
    #TODO determinar que es lo que necesito hacer cuando no esta disponible
    #TODO  Unificar con la de abajo
    #TODO base elem probablemente trasciende esta definicion
    #TODO calcular dos veces FQ ... es un exceso. simplificar
    FQtablaArray,connURL = getCubeTarget(obj)
    if refTable:
        FQtablaArray = FQName2array(refTable.getColumnData(1))
    #print(FQtablaArray,connURL)
    actConn = connMatch(exec_object.dataDict,connURL)
    if actConn:
        tableItem = actConn.findElement(FQtablaArray[1],FQtablaArray[2])
        if tableItem:
            fieldIdx = childByName(tableItem,'FIELDS')
            #array = getDataList(fieldIdx,0)
            array = [ (item.fqn(),item.text(),)  for item in fieldIdx.listChildren() ]
            result = editaCombo(obj,array,valor)
            return result
        else:
            print(connURL,'ESTA DISPONIBLE y el fichero NOOOOOR')
    else:
        print(connURL,'NO ESTA A MANO')
    return None

def editaCombo(obj,valueTable,valorActual):
    descriptivo = False
    if isinstance(valueTable[0],(list,tuple,set)):
        descriptivo = True
        comboList = [ item[1] for item in valueTable ]
        claveList = [ str(item[0]) for item in valueTable ]
    else:
        claveList = comboList = tuple(valueTable)
    spec = []
    spec.append(('Seleccione',QComboBox,None,comboList))
    if descriptivo and valorActual:
        values = [ claveList.index(valorActual) ]
    elif descriptivo:
        values = [ None , ]
    else:
        values = [ valorActual, ]

    parmDialog = propertySheetDlg('Defina '+obj.text(),spec,values)
    if parmDialog.exec_():
        print(values[0],parmDialog.sheet.cellWidget(0,0).currentText)
        if descriptivo:
            return claveList[values[0]]
        else:
            return parmDialog.sheet.cellWidget(0,0).currentText  #pues no lo tengo tan claro
    


def atomicEditAction(obj,valor,exec_object):
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()

    result = None
    if tipo in FREE_FORM_ITEMS:
        text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,obj.getColumnData(1))
        result = text[0]

    elif tipo in STATIC_COMBO_ITEMS:
        array = STATIC_COMBO_ITEMS[tipo]
        result = editaCombo(obj,array,valor)

    elif tipo in DYNAMIC_COMBO_ITEMS:
        print('Edit dynamic',obj,tipo,valor)
        array = []
        if tipo == 'cubo':
            array = getCubeList(exec_object.hiddenRoot)
            result = editaCombo(obj,array,valor)
        #TODO adaptar a  getCubeInfo
        elif tipo in ('row','col'):
            pai = obj.parent()
            if pai.type() == 'vista':
                cubeItem = pai.getBrotherByName('cubo')
                print (pai.text(),cubeItem.text(),cubeItem.getColumnData(1))
                cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                guidemaster = childByName(cubo,'guides')
                nombres = getItemList(guidemaster,'guides')
                
                array = [ (k,nombres[k]) for k in range(len(nombres)) ]
                result = editaCombo(obj,array,valor)

            #TODO el else deberia dar un error y no ignorarse
        elif tipo in ('elemento',):
            pai = obj.parent()
            if pai.type() == 'vista':
                cubeItem = pai.getBrotherByName('cubo')
                cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                guidemaster = childByName(cubo,'fields')
                
                array = getDataList(guidemaster,1) 
                result = editaCombo(obj,array,valor)

        elif tipo in ('table',):
            #TODO modificar esto lo destroza todo en teoría.
            #Acepto cualquier tabla en la conexion actual, no necesariamente el esquema
            array = getListAvailableTables(obj,exec_object)
            result = editaCombo(obj,array,valor)
                
        elif tipo in ('elem','base_elem','fields'):
            #TODO base_elem no tiene esta base, ojala
            result = editTableElem(exec_object,obj,valor,None)
                
        elif tipo in ('code','desc','grouped_by'):
            refTable = obj.getBrotherByName('table')
            
            result = editTableElem(exec_object,obj,valor,refTable)

        elif tipo in ('rel_elem'):
            pai = obj.parent()
            while pai.type() and pai.type() != 'related via':
                pai = pai.parent()
            refTable  = childByName(pai,'table')
            
            result = editTableElem(exec_object,obj,valor,refTable)

        else:
            print('Edit dynamic sin regla',obj,tipo,valor)
    else:
        print('Edit sin regla',obj,tipo,valor)
    return result

def addDefault(obj,exec_object):
    #TODO cuando existe default cargar valores como defecto
    print('Procesar Default')
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
    
    if tipo in NO_ADD_LIST:
        obj.menuActions[0].setEnabled(False)


    if tipo not in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) and tipo not in STATIC_COMBO_ITEMS  :
        obj.menuActions[1].setEnabled(False)
    if tipo in ('fields','case_sql') and obj.text() == tipo and obj.hasChildren():
        obj.menuActions[1].setEnabled(False)
        
    if tipo in NO_ADD_LIST:
        obj.menuActions[2].setEnabled(False)
    #elif tipo in TYPE_LIST_DICT and obj.text() == tipo:
        #obj.menuActions[-1].setEnabled(False)

    obj.menuActions[3].setEnabled(False)

    if obj.text() in ITEM_TYPE or obj.text() == "":
        obj.menuActions[4].setEnabled(False)

    if tipo in COMPLEX_TYPES :
        obj.menuActions[5].setEnabled(True)
    else:
        obj.menuActions[-1].setEnabled(False)


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
    
def execAction(exec_object,obj,action):
    #TODO listas editables en casi todos los elementos
    if action is None:
        return
    
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    if not tipo:
        print('NO tiene tipo',obj.getDataList())
    modelo.beginResetModel()
    if action ==  'add' :
        print('Add by',obj)
        #TODO deberia capturarse duplicados en la lista existente
        #FIXME no entiendo el porque los valors de un listbox tienen que venir en forma de tuple()
        if tipo in ('base','default_start'):
            #TODO la lista de ficheros deberia obviar los esquemas del sistema
            spec = []
            spec.append(('Intruduzca el nombre del nuevo cubo',None,None,))
            array=getListAvailableTables(obj,exec_object)
            spec.append(('Seleccione la tabla a utilizar',QComboBox,None,tuple(array)))
            values = [ None for k in range(len(spec))]
            parmDialog = propertySheetDlg('Defina el cubo a generar',spec,values,exec_object)
            if parmDialog.exec_():
                if values[0] :
                    if values[0].lower() == 'default':
                        addDefault(obj,exec_object)
                    else:
                        print('Proceso de alta')
                        #FIXME todo este proceso para obtener el nombre de la conexion es un poco tremebundo
                        FQtablaArray,connURL = getCubeTarget(obj)
                        actConn = connMatch(exec_object.dataDict,connURL)
                        connName = actConn.text()
                        tabla = array[values[1]].split('.')
                        schemaName= tabla[0] if len(tabla) > 1 else ''
                        tableName = tabla[1] if len(tabla) > 1 else tabla[0]
                        info = info2cube(exec_object.dataDict,connName,schemaName,tableName)
                        for key in info:
                            clave = key
                            break
                        recTreeLoader(exec_object.hiddenRoot,values[0],info[clave],'base')

            pass
        #elif tipo == 'fields'  no porque lo definimos como elemento libre
        elif tipo == 'guides':
            print(tipo,obj.text(),obj.getRow())
            # aqui el proceso del objeto
            if obj.text() != tipo:
                #add a new array entry
                idx = obj.index()
                pai = obj.parent()
             else:
                pai = obj
            #pai.insertRow(idx.row()+1,(CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))            
        elif tipo in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) or tipo in STATIC_COMBO_ITEMS  :
            result = atomicEditAction(obj,None,exec_object)
            #TODO repasar el grouped_by
            if tipo in ('fields','elem','code','desc','base_elem','rel_elem','grouped_by','case_sql','values'):
                if not obj.text():
                    #ya es un array; solo hay que añadir elementos
                    idx = obj.index()
                    pai = obj.parent()
                    pai.insertRow(idx.row()+1,(CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                elif not obj.getColumnData(1):
                    #hablamos del padre. Solo hay que añadir un hijo
                    obj.appendRow((CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                    pass
                else: # <code> : <valor>
                    #creo un elemento array hijo copiado del actual
                    #borro el contenido del original
                    #creo un nuevo registro
                    #FIXME esto deberia hacerse con takeRow
                    oldRecord = [ CubeItem(obj.getColumnData[k]) for k in range(1,obj.columnCount()) ]
                    print(obj.columnCount())
                    pprint(oldRecord)
                    oldRecord.insert(0,CubeItem(None))
                    pprint(oldRecord)
                    obj.appendRow((CubeItem(None),CubeItem(obj.getColumnData(1)),CubeItem(obj.getColumnData(2))))
                    obj.appendRow((CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                    obj.setColumnData(1,None,Qt.EditRole)
                    pass
            pass

        else:
            print('Se escapa',obj,tipo)
        pass  # edit item, save config, refresh tree
    elif action == 'edit':
        if tipo in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) or tipo in STATIC_COMBO_ITEMS  :
            valor = obj.getColumnData(1)
            result = atomicEditAction(obj,valor,exec_object)
            if result and result != valor:
                obj.setColumnData(1,result,Qt.EditRole) 
        else:
            print('Se escapa',obj,tipo)
        pass  # edit item, save config, refresh tree
    elif action == 'delete' :
        obj.suicide()
        pass  # close connection, delete tree, delete config
    elif action == 'copy':
        print('copy ',obj)
        pass
    elif action == 'rename':
        print('rename',obj)
        text = QInputDialog.getText(None, "Renombrar el nodo :"+obj.text(),"Nodo", QLineEdit.Normal,obj.text())
        obj.setData(text[0],Qt.EditRole)
        for item in obj.listChildren():
            if item.text() == 'name':
                print('procedo')
                item.setColumnData(1,text[0],Qt.EditRole)
                break
                
    elif action == 'refresh':
        print('refresh',obj)
        pass
    else:
        print('Action ',action,' desconocida')
        pass
    modelo.endResetModel()
 


