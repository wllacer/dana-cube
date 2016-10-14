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
     QDialog, QInputDialog, QLineEdit

from datadict import *    
from datalayer.query_constructor import *
from datalayer.access_layer import DRIVERS, AGR_LIST, dbDict2Url
from tablebrowse import *
from datemgr import genTrimestreCode
from util.jsonmgr import *
from util.fivenumbers import is_number

(_ROOT, _DEPTH, _BREADTH) = range(3)

ITEM_TYPE = set([
     u'agregado',
     u'base',
     u'base filter',
     u'base_elem',
     u'case_sql',
     u'categories',
     u'class',
     u'clause',
     u'code',
     u'col',
     u'condition',
     u'connect',
     u'cubo',
     u'dbhost',
     u'dbname',
     u'dbpass',
     u'dbuser',
     u'default',
     u'desc',
     u'driver',
     u'elem',
     u'elemento',
     u'enum_fmt',
     u'fields',
     u'filter',
     u'fmt',
     u'grouped by',
     u'guides',
     u'name',
     u'pos',
     u'prod',
     u'rel_elem',
     u'related via',
     u'result',
     u'row',
     u'source',
     u'table',
     u'type',
     u'values',
     u'vista'])

TYPE_DICT = set([u'base',
     'connect',
     u'default_start',
     'source',
     'vista'])

TYPE_LIST = set(['case_sql',
     'fields',
     'values'])

TYPE_LIST_DICT = set([
     'categories',
     'clause',
     'guides',
     'prod',
     'related via'])

COMPLEX_TYPES = TYPE_DICT | TYPE_LIST | TYPE_LIST_DICT

GUIDE_CLASS = ( 
    ('o','normal',),
    ('c','categorias',),
    ('h','jerarquia',),
    ('d','fecha',),
    );
LOGICAL_OPERATOR = ('in','not in','between','not between','=','!=','<','>','>=','<=')
ENUM_FORMAT = ( ('t','texto'),('n','numerico'),('d','fecha'))
TIPO_FECHA = ('Ymd', 'Ym','Ymw','YWw') 

EDITED_ITEMS = set([
     u'agregado',  # AGR_LIST
     u'base_elem', #             field of  Reference  table
     u'base filter', # free text
     u'class',     # GUIDE_CLASS *
     u'code',      #             field of FK table (key)
     u'col',       # number (a guide of base)
     u'condition', # LOGICAL_OPERATOR
     u'cubo',      # uno de los cubos del fichero
     u'dbhost',    # free text
     u'dbname',    # free text 
     u'dbpass',    # free text (ver como ocultar)
     u'dbuser',    # free text
     u'default',   # free text
     u'desc',       #             field of FK table (values)
     u'driver',   # DRIVERS
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'enum_fmt',  # ENUM_FORMAT
     u'filter',    # free text
     u'fmt',       # en prod = FORMATO, en categories ENUM_FORMAT
     u'grouped by',#              field of FK table or derived value ??
     u'name',      # free text
     u'rel_elem',  #              field of FK table
     u'result',    # free text
     u'row',       # number (a guide of base)
     u'table',     # table ...
     u'type'])     # TIPO_FECHA

FREE_FORM_ITEMS = set([
     u'base filter',
     u'case_sql',
     u'dbhost',    # free text
     u'dbname',    # free text 
     u'dbpass',    # free text (ver como ocultar)
     u'dbuser',    # free text
     u'default',   # free text
     u'filter',    # free text
     #u'name',      # free text
     u'result',    # free text
     u'values',
    ])
STATIC_COMBO_ITEMS = dict({
     u'agregado': AGR_LIST,
     u'class': GUIDE_CLASS ,
     u'condition': LOGICAL_OPERATOR,
     u'driver': DRIVERS,
     u'enum_fmt': ENUM_FORMAT,
     u'fmt': ENUM_FORMAT,
     u'type': TIPO_FECHA,
    })

DYNAMIC_COMBO_ITEMS = set([
     u'base_elem', #             field of  Reference  table
     u'code',      #             field of FK table (key)
     u'col',       # number (a guide of base)
     u'cubo',      # uno de los cubos del fichero
     u'desc',       #             field of FK table (values)
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'fields',
     u'grouped by',#              field of FK table or derived value ??
     u'rel_elem',  #              field of FK table
     u'row',       # uno de los cubos del fichero
     u'table',
    ])
"""
   cubo --> lista de cubos
   col,row
"""
class CubeItem(QStandardItem):
    """
    TODO unificar con BaseTreeItem en dictTree
    """
    def __init__(self, name):
        QStandardItem.__init__(self, name)
        self.setEditable(False)
        self.setColumnCount(1)
        #self.setData(self)
        self.gpi = self.getRow        
        
    def suicide(self):
        """
           Mas bien suicida
        """
        indice = self.index()
        padre=self.parent()
        padre.removeRow(indice.row())
        
    def deleteChildren(self):
        if self.hasChildren():
            while self.rowCount() > 0:
                self.removeRow(self.rowCount() -1)
 
    def isAuxiliar(self):
        if self.text() in ('FIELDS','FK','FK_REFERENCE') and self.depth() == 3:
            return True
        else:
            return False
        
    def setDescriptive(self):
        if self.isAuxiliar():
            return
        else:
            indice = self.index() 
            colind = indice.sibling(indice.row(),2)
            if colind:
                colind.setData(True)
                
    def getBrotherByName(self,name): 
        # getSibling esta cogido para los elementos de la fila, asi que tengo que inventar esto para obtener
        # un 'hermano' por nomnbre
        padre = self.parent()
        for item in padre.listChildren():
            if item.text() != name:
                continue
            else:
                return item
        return None

    def getChildrenByName(self,name): 
        for item in self.listChildren():
            if item.text() != name:
                continue
            else:
                return item
        return None

    def getFullDesc(self):
        fullDesc = [] #let the format be done outside
        if not self.isAuxiliar():
            fullDesc.append(self.text())
        papi = self.parent()
        while papi is not None:
            if not papi.isAuxiliar():
                fullDesc.insert(0,papi.text()) #Ojo insert, o sea al principio
            papi = papi.parent()
        return '.'.join(fullDesc)
 
    def depth(self):
        item = self
        depth = -1 #hay que recordar que todo cuelga de un hiddenRoot
        while item is not None:
            item = item.parent()
            depth +=1
        return depth

    def lastChild(self):
        if self.hasChildren():
            return self.child(self.rowCount() -1)
        else:
            return None
        
    def listChildren(self):
        lista = []
        if self.hasChildren():
            for k in range(self.rowCount()):
                lista.append(self.child(k))
        return lista
     
    def getRow(self,role=None):
        """
          falta el rol
        """
        lista=[]
        indice = self.index() #self.model().indexFromItem(field)
        k = 0
        colind = indice.sibling(indice.row(),k)
        while colind.isValid():
            if role is None:
                lista.append(colind.data()) #print(colind.data())
            else:
                lista.append(colind.data(role))
            k +=1
            colind = indice.sibling(indice.row(),k)
        return lista
     
    def getColumnData(self,column,role=None):
        indice = self.index() #self.model().indexFromItem(field)
        colind = indice.sibling(indice.row(),column)
        if colind.isValid():
            return colind.data(role) if role else colind.data()
        else:
            return None
    
    def setColumnData(self,column,data,role=None):
        indice = self.index() #self.model().indexFromItem(field)
        colind = indice.sibling(indice.row(),column)
        if colind.isValid():
            colitem = self.model().itemFromIndex(colind)
            if role:
                colitem.setData(data,role)
            else:
                colitem.setData(data)

    
    def takeChildren(self):
        if self.hasChildren():
            lista = []
            for k in range(self.rowCount()):
                lista.append(self.takeItem(k))
        else:
            lista = None
        return lista
    
    def getTypeName(self):
        return self.__class__.__name__ 

    def type(self):
        if not self.getColumnData(2) :
            return self.parent().type()
        return self.getColumnData(2)
    
    def extendedType(self):
        if self.type():
            return self.type()
        else:
            padre = self.parent()
            while padre:
                if padre.type():
                    return padre.type()
                else:
                    padre = padre.parent()

    def typeHierarchy(self):
        tipos = []
        tipos.append(self.type())
        padre = self.parent()
        while padre:
            tipos.append(padre.type())
            padre = padre.parent()
        return tipos  #.reverse() #no se si sera esto lo que quiero        
     
    def getModel(self):
        """
        probablemente innecesario
        """
        item = self
        while item is not None and type(item) is not TreeModel:
            item = item.parent()
        return item


    def __repr__(self):
        return "<" + self.text() + ">"
    
def lastChild(item):
    if item.hasChildren():
        return item.child(item.rowCount() -1)
    else:
        return None

def info2cube(dataDict,confName,schema,table,maxlevel=1):
    """
       de monento solo sustituyo
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

#def constructFKsheet(elemento,path, path_array,routier):
def constructFKsheet(elemento, path_array,routier):    
    path_array_local = path_array[:]
    path_array_local.append(elemento)
    routier.append(path_array_local)
    for fkr in elemento.get('FK',list()):
        constructFKsheet(fkr,path_array_local,routier)

def getDescList(fk):
    desc_fld = []
    for fld in fk['CamposReferencia']:
        if fld[1] == 'texto':
            desc_fld.append(fld[0])
    if len(desc_fld) == 0:
        print('No proceso correctamente por falta de texto',fk)
        desc_fld = fk['ParentField']
    return desc_fld


def recTreeLoader(parent,key,data,tipo=None):
    """
        Los valores de elementos atomicos son atributos del nodo en arbol
    """
    #parent.appendRow((QStandardItem(str(key)),QStandardItem(str(data)),))
    if not tipo:
        tipo=str(key)
    if not isinstance(data,(list,tuple,set,dict)): #
        parent.appendRow((CubeItem(str(key)),CubeItem(str(data)),CubeItem(tipo),))
    else:
        parent.appendRow((CubeItem(str(key)),None,CubeItem(tipo),))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in data:
            recTreeLoader(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                #continue
                newparent.appendRow((CubeItem(None),CubeItem(str(elem)),))
            elif isinstance(elem,dict) and elem.get('name'):
                clave = elem.get('name')
                datos = elem
                #datos['pos'] = idx
                recTreeLoader(newparent,clave,datos,tipo)
            else:                
                clave = str(idx)
                datos = elem
                recTreeLoader(newparent,clave,datos,tipo)
    #else:
        #newparent.appendRow(CubeItem(str(data)))
        
def recTreeLoaderAtomic(parent,key,data,tipo=None):
    """
    version con los valores de elementos atomicos son nodos en el arbol
    """
    #parent.appendRow((QStandardItem(str(key)),QStandardItem(str(data)),))
    if not tipo:
        tipo=str(key)
    parent.appendRow((CubeItem(str(key)),CubeItem(tipo),))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in data:
            recTreeLoader(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                clave = elem
                newparent.appendRow((CubeItem(str(clave)),))
            elif isinstance(elem,dict) and elem.get('name'):
                clave = elem.get('name')
                datos = elem
                #datos['pos'] = idx
                recTreeLoader(newparent,clave,datos,tipo)
            else:                
                clave = str(idx)
                datos = elem
                recTreeLoader(newparent,clave,datos,tipo)
    else:
        newparent.appendRow(CubeItem(str(data)))

def traverseTree(key,mode=_DEPTH):
    if key is not None:
        yield key
        queue = childItems(key)
        
    while queue:
        yield queue[0]
        expansion = childItems(queue[0])
        if not expansion:
            expansion = []
            
        if mode == _DEPTH:
            queue = expansion + queue[1:]  # depth-first
        elif mode == _BREADTH:
            queue = queue[1:] + expansion  # width-first
    
def childItems(treeItem):
    if not treeItem:
        return None
    datos = []
    if isinstance(treeItem,CubeItem):
        datos = treeItem.listChildren()
    else:
        for ind in range(treeItem.rowCount()):
            datos.append(treeItem.child(ind))
    return datos
 
def childByName(treeItem,name):
    if isinstance(treeItem,CubeItem):
        return treeItem.getChildrenByName(name)
    else:
        for k in range(treeItem.rowCount()):
            if treeItem.child(k).text() == name:
                return treeItem.child(k)
    return None        
def rowData(treeItem):
    datos = []
    if not treeItem:
        return None
    
    if isinstance(treeItem,CubeItem):
        datos = treeItem.getRow()
    else:
        indice = treeItem.index()
        datos = []
        k=0
        while True:
            columna = indice.sibling(indice.row(),k)
            if columna.isValid():
                datos.append(columna.data())
                k += 1
            else:
                break
    return datos


def navigateTree(parent):
    editor = set()
    for node in traverseTree(parent):
        if isinstance(node,CubeItem):
            #print(node,node.getColumnData(1),'<-',node.typeHierarchy())
            if node.getColumnData(1):
                editor.add(node.text())
        #else:
            #print(node)
    print('EDITED_ITEMS =')
    pprint(editor)

def editaCombo(obj,valueTable,valorActual):
    # primero determino el indice del valor actual
    act_valor_idx = 0
    for k,value in enumerate(valueTable):
        if isinstance(value,(list,tuple,set)):
            kval =value[0]
        else:
            kval = value
        if str(kval) == str(valorActual):  #FIXME sto es un poco asi así
            act_valor_idx = k
            break
    print(valueTable,valorActual,act_valor_idx)
    #normalizo la tabla de valores para que presente solo las descripciones (si las hay)
    hasDescriptions = False
    if isinstance(valueTable[0],(list,tuple,set)) and len(valueTable[0]) > 1:
        hasDescriptions = True
        combo = [ item[1] for item in valueTable]
    else:
        combo = list(valueTable)
        
    result,controlvar = QInputDialog.getItem(None,"Editar:"+obj.text(),obj.text(),combo,current=act_valor_idx) 
    
    # si tiene descripciones tengo que averiguar a que elemento pertenecen
    if hasDescriptions:
        idx = None
        for k,value in enumerate(combo):
            if value == result:
                #idx = k
                result = valueTable[k][0]
                break
    #    obj.setColumnData(1,valueTable[idx][0],Qt.EditRole) 
    #else:
        #obj.setColumnData(1,result,Qt.EditRole) 
    if result != valorActual:
        obj.setColumnData(1,result,Qt.EditRole) 
    #if  isinstance(array[idx],(list,tuple,set)) and len(array[idx]) > 2 and array[idx][2]:
        #obj.suicide() # un poco fuerte
    #elif  isinstance(array[idx],(list,tuple,set)):
        #obj.setColumnData(1,array[idx][0],Qt.EditRole)
    #else:
        #obj.setColumnData(1,array[idx],Qt.EditRole)
    
def getCubeList(rootElem):
    entradas_especiales = ('default',)
    lista = [ item.text() for item in childItems(rootElem) if item.text() not in entradas_especiales ]
    return lista

def getItemList(rootElem,tipo = None):
    if tipo:
        lista = [ item.text() for item in childItems(rootElem) if item.type() == tipo ]
    else:
        lista = [ item.text() for item in childItems(rootElem) ]
    print(lista)
    return lista

def getDataList(rootElem,column,tipo = None):
    if tipo:
        lista = [ item.getColumnData(column) for item in childItems(rootElem) if item.type() == tipo ]
    else:
        lista = [ item.getColumnData(column) for item in childItems(rootElem) ]
    print(lista)
    return lista

def FQName2array(fqname):
    dbmanager = '' #no deberia existir pero por si acaso
    schema = ' '
    filename = ''
    splitdata = fqname.split('.')
    if len(splitdata) == 3:
        dbmanager,schema,filename = splitdata
    elif len(splitdata) == 2:
        schema,filename = splitdata
    elif len(splitdata) == 1:
       filename = fqname
    return dbmanager,schema,filename

        
def tree2dict(rootItem): #FIXIT como manejar los numeros un poco raros
                         #Compactar el codigo
    elementos=childItems(rootItem)
    #una de las variables es innecesaria de momento
    toList = False
    toDict = False
    #if rootItem.type() in TYPE_LIST or (rootItem.type() in TYPE_LIST_DICT and rootItem.text() == rootItem.type()):
    if (( not isinstance(rootItem,CubeItem) ) or   #la raiz siempre genera directorio
         rootItem.type() in TYPE_DICT or          # es obvio
       ( rootItem.type() in TYPE_LIST_DICT and rootItem.text() != rootItem.type() )):
       toDictionary = True
    else:
       toList = True
       
    if toList:
        result_l = list()
        for item in elementos:
            if item.hasChildren():
                result_l.append(tree2dict(item))
            else:
                dato = item.getColumnData(1)
                if dato == 'None':
                   result_l.append(None)
                #elif is_number(dato):
                   #result_l.append(Decimal(dato))
                else:
                    result_l.append(dato)
        return result_l
    else:
        result_d = dict()
        for item in elementos:
            if item.hasChildren():
                result_d[item.text()] = tree2dict(item)
            else:
                dato = item.getColumnData(1)
                if dato == 'None':
                   result_d[item.text()]=None
                #elif is_number(dato):
                   #result_d[item.text()] = Decimal(dato)
                else:
                    result_d[item.text()]= dato

        return result_d
 
def getCubeTarget(obj):
    pai = obj.parent()
    while pai and pai.type() != 'base' :
        pai = pai.parent()
    if pai: #o sea hay padre
        tablaItem = childByName(pai,'table')
        FQtablaArray = FQName2array(tablaItem.getColumnData(1))
        connItem = childByName(pai,'connect')
        conn_data = tree2dict(connItem)
    return FQtablaArray,dbDict2Url(conn_data)

def dbUrlSplit(url):
    agay= url.split('://')
    if len(agay) == 2:
        fullinterface = agay[0]
        resto  = agay[1]
    elif len(agay) == 1:
        fullinterface = None
        resto = agay[0]

    if fullinterface is not None:
        agay = fullinterface.split('+')
        dialect = agay[0]
        if len(agay) == 2:
            driver = agay[1]
        else:
            driver = None
    else:
        dialect = None
        driver  = None
            

    agay = resto.split('@')
    if len(agay) == 2:
        login = agay[0]
        reference  = agay[1]
    elif len(agay) == 1:
        login = None
        reference = agay[0]
    
    if not reference:
        host= None
        dbref = None
    elif reference[0] == '/':
        host = None
        dbref = reference
    else:
        agay = reference.split('/',1)
        if len(agay) >2:
            host = agay[0]
            dbref = '/'.join(agay[1:])
        elif len(agay) == 2:
            host = agay[0]
            dbref = agay[1]
        else:
            host= None
            dbref = reference
    #print('{:20}{:20} {:20} {:20} {}'.format(dialect,driver,login,host,dbref)
    return dialect,driver,login,host,dbref

def getOpenConnections(dataDict):
    conns = childItems(dataDict.hiddenRoot)
    for conn in conns:
        print(conn.getConnection().data().engine.url)
    return

def connMatch(dataDict,pUrl):
    conns = childItems(dataDict.hiddenRoot)
    available = False
    for conn in conns:
        if str(conn.getConnection().data().engine.url) == pUrl:  #¿? el str
            available = True
            break
    if available:
        return conn  #ConnectionTreeObject
    else:
        return None
    

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
        #FIXME es un chapu brutal
        #if actConn.data().engine.driver == 'pysqlite':
            ##CHECK creo que el primer parche es inncesario
            #tableItem = actConn.findElement('main',FQtablaArray[2])
        #else:
        tableItem = actConn.findElement(FQtablaArray[1],FQtablaArray[2])
        if tableItem:
            fieldIdx = childByName(tableItem,'FIELDS')
            array = getDataList(fieldIdx,0)
            editaCombo(obj,array,valor)
        else:
            print(connURL,'ESTA DISPONIBLE y el fichero NOOOOOR')
    else:
        print(connURL,'NO ESTA A MANO')

def setContextMenu(obj,menu):
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()

    obj.menuActions = []
    obj.menuActions.append(menu.addAction("Add ..."))
    obj.menuActions.append(menu.addAction("Edit ..."))
    if tipo not in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) and tipo not in STATIC_COMBO_ITEMS  :
        obj.menuActions[-1].setEnabled(False)
    if tipo in ('fields','case_sql') and obj.text() == tipo and obj.hasChildren():
        obj.menuActions[-1].setEnabled(False)
        
    obj.menuActions.append(menu.addAction("Delete"))
    obj.menuActions.append(menu.addAction("Copy ..."))
    obj.menuActions.append(menu.addAction("Rename"))
    if obj.text() in ITEM_TYPE or obj.text() == "":
        obj.menuActions[-1].setEnabled(False)
    obj.menuActions.append(menu.addAction("Refresh"))    
    
    if tipo in COMPLEX_TYPES :
        obj.menuActions[-1].setEnabled(True)
    else:
        obj.menuActions[-1].setEnabled(False)
        
def getContextMenu(obj,action,exec_object=None):
    if action is None:
        return
    
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    
    ind = obj.menuActions.index(action)
    modelo.beginResetModel()
    if ind == 0:
        print('Add by',obj)
        if tipo in ('fields','elem','code','desc','base_elem','grouped_by','case_sql','values'):
            if not obj.text():
                #ya es un array; solo hay que añadir elementos
                pass
            elif not obj.getColumnData(1):
                #hablamos del padre. Solo hay que añadir un hijo
                pass
            else: # <code> : <valor>
                #creo un elemento array hijo copiado del actual
                #borro el contenido del original
                #creo un nuevo registro
                pass
        pass
    elif ind == 1 :
        valor = obj.getColumnData(1)
        if tipo in FREE_FORM_ITEMS:
            text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,obj.getColumnData(1))
            obj.setColumnData(1,text[0],Qt.EditRole)
        elif tipo in STATIC_COMBO_ITEMS:
            array = STATIC_COMBO_ITEMS[tipo]

            editaCombo(obj,array,valor)
        elif tipo in DYNAMIC_COMBO_ITEMS:
            print('Edit dynamic',obj,tipo,valor)
            array = []
            if tipo == 'cubo':
                array = getCubeList(exec_object.hiddenRoot)
                editaCombo(obj,array,valor)
            elif tipo in ('row','col'):
                pai = obj.parent()
                if pai.type() == 'vista':
                    cubeItem = pai.getBrotherByName('cubo')
                    print (pai.text(),cubeItem.text(),cubeItem.getColumnData(1))
                    cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                    guidemaster = childByName(cubo,'guides')
                    nombres = getItemList(guidemaster,'guides')
                    array = [ (k,nombres[k]) for k in range(len(nombres)) ]
                    editaCombo(obj,array,valor)
                #TODO el else deberia dar un error y no ignorarse
            elif tipo in ('elemento',):
                pai = obj.parent()
                if pai.type() == 'vista':
                    cubeItem = pai.getBrotherByName('cubo')
                    print (pai.text(),cubeItem.text(),cubeItem.getColumnData(1))
                    cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                    guidemaster = childByName(cubo,'fields')
                    array = getDataList(guidemaster,1) 
                    editaCombo(obj,array,valor)
            elif tipo in ('table',):
                #TODO modificar esto lo destroza todo en teoría.
                #Acepto cualquier tabla en la conexion actual, no necesariamente el esquema
                FQtablaArray,connURL = getCubeTarget(obj)
                actConn = connMatch(exec_object.dataDict,connURL)
                if actConn.data().engine.driver == 'pysqlite':
                    templateTxt = '{1}'
                else:
                    templateTxt = '{0}.{1}'
                if actConn:
                    array = []
                    for sch in childItems(actConn):
                        schema = sch.text()
                        for tab in childItems(sch):
                            array.append(templateTxt.format(schema,tab.text()))
                            
                    editaCombo(obj,array,valor)        
                else:
                    print(connURL,'NO ESTA A MANO')
                    
            elif tipo in ('elem','base_elem','fields'):
                editTableElem(exec_object,obj,valor,None)

            elif tipo in ('code','desc','grouped_by'):
                refTable = obj.getBrotherByName('table')
                editTableElem(exec_object,obj,valor,refTable)

            elif tipo in ('rel_elem'):
                pai = obj.parent()
                while pai.type() and pai.type() != 'related via':
                    pai = pai.parent()
                refTable  = childByName(pai,'table')
                editTableElem(exec_object,obj,valor,refTable)

            else:
                print('Edit',obj,tipo,valor)
            """
     u'base_elem', #<>             field of  Reference  table
     u'code',      #<>             field of FK table (key)
     u'col',       #<> number (a guide of base)
     u'cubo',      #<>uno de los cubos del fichero
     u'desc',      #<>             field of FK table (values)
     u'elem',      #<>              field of table, or derived value 
     u'elemento',  #<> FIELD of cube
     u'grouped by',#<>              field of FK table or derived value ??
     u'rel_elem',  #<>              field of FK table
     u'row',       #<> uno de los cubos del fichero
     u'table'      #<>,
        a) Lista de cubos activos
        b) Lista de guias en un cubo
        c) Lista de tablas en una B.D.
        d) Lista de campos en una tabla
        a1) determinar que tabla me corresode
        """
        else:
            print('Se escapa',obj,tipo,valor)
        pass  # edit item, save config, refresh tree
    elif ind == 2:
        obj.suicide()
        pass  # close connection, delete tree, delete config
    elif ind == 3:
        print('copy ',obj)
        pass
    elif ind == 4:
        print('rename',obj)
        text = QInputDialog.getText(None, "Renombrar el nodo :"+obj.text(),"Nodo", QLineEdit.Normal,obj.text())
        obj.setData(text[0],Qt.EditRole)
        for item in obj.listChildren():
            if item.text() == 'name':
                print('procedo')
                item.setColumnData(1,text[0],Qt.EditRole)
                break
                
    elif ind == 5:
        print('refresh',obj)
        pass
    modelo.endResetModel()
    
 

class CubeBrowserWin(QMainWindow):
    def __init__(self,confName,schema,table,pdataDict=None):
        super(CubeBrowserWin, self).__init__()
        self.configFile = 'experimento.json'
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
            self.dataDict=DataDict(conn=confName,schema=schema)
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
        newcubeStruct = tree2dict(self.hiddenRoot)
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
