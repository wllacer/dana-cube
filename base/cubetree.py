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

#from decimal import *

##from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
#from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QSplitter, QMenu, \
     #QDialog, QInputDialog, QLineEdit, QComboBox

#from datadict import *    
#from support.datalayer.query_constructor import *
#from support.datalayer.access_layer import DRIVERS, AGR_LIST, dbDict2Url
#from admin.tablebrowse import *
#from support.datalayer.datemgr import genTrimestreCode
#from support.util.jsonmgr import *
#from support.util.numeros import is_number
#from support.gui.dialogs import propertySheetDlg

(_ROOT, _DEPTH, _BREADTH) = range(3)

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
        if padre:
            padre.removeRow(indice.row())
        else:
            self.model().removeRow(indice.row())
            
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
    
    def getChildrenValuesAsList(self,column):
        lista = self.listChildren()
        if len(lista) == 0:
            return lista
        array = []
        for item in lista:
            array.append(item.getColumnData(column))
        return array
    
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
    #FIXME desactivado por el momento, no acaba de salir como yo quiero y no tengo tiempo
    def data(self,role=Qt.UserRole +1):
        indice = self.index() #self.model().indexFromItem(field)
        tipo = None
        if indice.column() == 1:
            tipoInd = indice.sibling(indice.row(),2)
            if tipoInd.isValid():
                tipo = tipoInd.data(role)
            if tipo and tipo == 'dbpass' and role == Qt.DisplayRole :
                return '********'
        return super(CubeItem,self).data(role)
 
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
        probablemente innecesario. No se usa de hecho
        """
        item = self
        while item is not None: 
            item = item.parent()
        return item

    def getPos(self):
        pai = self.parent()
        pos = None
        for k,item in enumerate(pai.listChildren()):
            if item == self:
                pos = k 
                break
        return pos
    
    def getPrevious(self):
        pos = self.getPos()
        if pos == 0:
            return None
        else:
            return self.parent().getChildByPos(pos -1)
        
    def getNext(self):
        pos = self.getPos()
        if pos == self.parent().rowCount() -1:
            return None
        else:
            return self.parent().getChildByPos(pos +1)
        
    def getChildByPos(self,pos):
        return self.child(pos)
                
    def __repr__(self):
        return "<" + self.text() + ">"
    
def lastChild(item):
    if item.hasChildren():
        return item.child(item.rowCount() -1)
    else:
        return None

def recTreeLoader(parent,key,data,tipo=None):
    """
        Funcion que carga de estructura de cubo python a nodo CubeItem del arbol (recursiva)
        parent -> nodo del arbol a partir del cual incluir
        key > clave del nodo
        data > valor del nodo
        tipo > clase del nodo
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
        for elem in sorted(data):
            recTreeLoader(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                #continue
                newparent.appendRow((CubeItem(None),CubeItem(str(elem)),))
            elif isinstance(elem,dict): #and elem.get('name'):
                for texto in ('name','result'):
                    if elem.get(texto):
                        clave = elem.get(texto)
                        break
                else:
                    clave = str(idx)
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
    Funcion que carga de estructura de cubo python a arbol. NO USADA
    
    version con los valores de elementos atomicos son nodos en el arbol
    """
    #parent.appendRow((QStandardItem(str(key)),QStandardItem(str(data)),))
    if not tipo:
        tipo=str(key)
    parent.appendRow((CubeItem(str(key)),CubeItem(tipo),))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in data:
            recTreeLoaderAtomic(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                clave = elem
                newparent.appendRow((CubeItem(str(clave)),))
            elif isinstance(elem,dict) and elem.get('name'):
                clave = elem.get('name')
                datos = elem
                #datos['pos'] = idx
                recTreeLoaderAtomic(newparent,clave,datos,tipo)
            else:                
                clave = str(idx)
                datos = elem
                recTreeLoaderAtomic(newparent,clave,datos,tipo)
    else:
        newparent.appendRow(CubeItem(str(data)))

dict2tree = recTreeLoader    #un sinonimo asi puedo elegir la rutina que mas me interese

def tree2dict(rootItem,esdiccionario=None,role=None):
    """
       convertir un nodo de  estructura arbol en una entrada de cubo en memoria (diccionario) -recursiva-
       deberia ir a cubetree
       esdiccionario es una funcion para determinar si la entrada es o no un diccionario.
       TODO convertir la funcion en multiple valor elem,dict,tree,Not Defined
    """
    #FIXIT como manejar los numeros un poco raros
                         #Compactar el codigo
    elementos=childItems(rootItem)
    #una de las variables es innecesaria de momento
    toList = False
    toDict = False

    if not isinstance(rootItem,CubeItem) :
            toDictionary = True #la raiz siempre genera directorio
    elif esdiccionario and esdiccionario(rootItem):   
        toDictionary = True
    else:
       toList = True
       
    if toList:
        result_l = list()
        for item in elementos:
            if item.hasChildren():
                result_l.append(tree2dict(item,esdiccionario,role))
            else:
                dato = item.getColumnData(1,role)
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
                result_d[item.text()] = tree2dict(item,esdiccionario,role)
            else:
                dato = item.getColumnData(1,role)
                if dato == 'None':
                   result_d[item.text()]=None
                # para los valores booleanos. Bug sutil 
                if dato in ('True','False'):
                    result_d[item.text()] = True if dato == 'True' else False
                #elif is_number(dato):
                   #result_d[item.text()] = Decimal(dato)
                else:
                    result_d[item.text()]= dato

        return result_d

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

def getItemList(rootElem,tipo = None):
    if tipo:
        lista = [ item.text() for item in childItems(rootElem) if item.type() == tipo ]
    else:
        lista = [ item.text() for item in childItems(rootElem) ]
    return lista

def getDataList(rootElem,column,tipo = None):
    if tipo:
        lista = [ item.getColumnData(column) for item in childItems(rootElem) if item.type() == tipo ]
    else:
        lista = [ item.getColumnData(column) for item in childItems(rootElem) ]
    #print(lista)
    return lista

def main():
    import sys
    from base.core import Cubo
    from support.util.jsonmgr import load_cubo
    from PyQt5.QtWidgets import QApplication
    
    
    types = set([
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
        u'default_base',
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
        u'link via',
        u'result',
        u'row',
        u'domain',
        u'table',
        u'type',
        u'values',
        u'vista'])

    
    app = QApplication(sys.argv)
    mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['experimento'])
    model = QStandardItemModel()
    hiddenRoot = model.invisibleRootItem()
    parent = hiddenRoot
    for entrada in mis_cubos:
        if entrada == 'default':
            tipo = 'default_base'
        elif entrada in types:
            tipo = entrada
        else:
            tipo = 'base'
        recTreeLoader(parent,entrada,mis_cubos[entrada],tipo)
        for node in traverseTree(hiddenRoot):
            if isinstance(node,CubeItem):
                padd = '\t'*node.depth()
                print(padd,node.text(),node.getColumnData(1),node.type())
            else:
                print(node.text())
        
    #vista=Vista(cubo,1,0,'sum','votes_presential')
    #form = datebase.filterDlg(vista)
    #form.show()
    #if form.exec_():
        ##cdata = [form.context[k][1] for k in range(len(parametros))]
        ##print('a la vuelta de publicidad',cdata)
        #sys.exit()

if __name__ == '__main__':
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    main()