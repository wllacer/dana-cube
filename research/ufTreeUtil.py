#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from support.util.uf_manager import *
from support.util.jsonmgr import *

from PyQt5.QtCore import Qt,QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem


"""
Utildades
"""
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1", "si", "sí", "ok")

 
def lastChild(item):
    if item.hasChildren():
        return item.child(item.rowCount() -1)
    else:
        return None
    
def childItems(treeItem):
    if not treeItem:
        return None
    datos = []
    for ind in range(treeItem.rowCount()):
        datos.append(treeItem.child(ind))
    return datos

def makeRow(*parms):
    retorno = []
    for k in range(len(parms)):
        elem = QStandardItem(str(parms[k]) if parms[k] is not None else None)
        elem.setData(parms[k],Qt.UserRole +1)
        retorno.append(elem)
    return retorno

def dict2tree(parent,key,data,tipo=None):
    """
        Funcion que carga de estructura de cubo python a nodo QStandardItem del arbol (recursiva)
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
        parent.appendRow(makeRow(key,data,tipo))
    else:
        parent.appendRow(makeRow(key,None,tipo))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in sorted(data):
            dict2tree(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                #continue
                newparent.appendRow(makeRow(None,elem))

            elif isinstance(elem,dict): #and elem.get('name'):
                for texto in ('name','result'):
                    if elem.get(texto):
                        clave = elem.get(texto)
                        break
                else:
                    clave = str(idx)
                datos = elem
                #datos['pos'] = idx
                dict2tree(newparent,clave,datos,tipo)
            else:                
                clave = str(idx)
                datos = elem
                dict2tree(newparent,clave,datos,tipo)  
     
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
    if rootItem == rootItem.model().invisibleRootItem() :
            toDictionary = True #la raiz siempre genera directorio
    elif esdiccionario and esdiccionario(rootItem):   
        toDictionary = True
    else:
       toList = True
       
    if toList:
        result_l = list()
        for item in elementos:
            nombre = item.data()
            dato = item.model().itemFromIndex(item.index().sibling(item.row(),1)).data()
            #tipo = item.model().itemFromIndex(item.index().sibling(item.row(),2)).data()
            if item.hasChildren():
                result_l.append(tree2dict(item,esdiccionario,role))
            else:
                #dato = item.getColumnData(1,role)
                if dato is None or dato == 'None': #FIXME deberia ser continue ¿?
                   result_l.append(None)
                else:
                    result_l.append(dato)
        return result_l
    else:
        result_d = dict()
        for item in elementos:
            nombre = item.data()
            dato = item.model().itemFromIndex(item.index().sibling(item.row(),1)).data()
            #tipo = item.model().itemFromIndex(item.index().sibling(item.row(),2)).data()
            if item.hasChildren():
                result_d[nombre] = tree2dict(item,esdiccionario,role)
            else:
                #dato = item.getColumnData(1,role)
                if dato is None or dato == 'None':
                    #FIXME deberia ser continue
                   result_d[nombre]=None
                # para los valores booleanos. Bug sutil 
                #if dato in ('True','False'):
                    #result_d[item.text()] = True if dato == 'True' else False
                #elif is_number(dato):
                   #result_d[item.text()] = Decimal(dato)
                else:
                    result_d[nombre]= dato

        return result_d

def cloneSubTree(entryPoint): #,filter=None,payload=False):
    """
    TODO add to doc
    Generate a new tree from entryPoint and its children
    
    * Input parms
        *
        * __entryPoint__ a GuideItem as hierachical head of what to export
        * __filter__ a function which does some filtering at the tree (default is no filter)
        * __payload__ boolean. If True copies the payload
        
    * returns
        a tree
    
    """
    #for k in range(modelo.rowCount()):
        #item = modelo.item(k)
        #first = True
        #print(item.data())
        #for chip in traverse(modelo,item):
            #if first:
                #hier = hierTree(chip)
                #last = chip.data()
                #first = False
                #continue
            #ohier = hierTree(chip)
            #if len(ohier) == len(hier):
                #pass
            #elif len(ohier) > len(hier):
                #hier.append(last)
            #elif len(ohier) < len(hier):
                #del hier[len(ohier):]
            #if ohier != hier:
                #print('scheisse',ohier,hier)
            #last = chip.data()

    def hierTree(entry):
        mihier = []
        pai = entry.parent()
        while pai is not None:
                mihier.insert(0,pai)
                pai = pai.parent()
        return mihier
    isFirst = True
    hierarchy = []
    model = entryPoint.model()
    for item in traverse(model,entryPoint):
        n,i,t = getRow(item)
        if isFirst:
            newRow = makeRow(t.data(),i.data(),t.data())
            if entryPoint.parent() is None:
                newRow = makeRow(t.data(),i.data(),t.data())
                model.appendRow(newRow)
            else:
                entryPoint.parent().appendRow(newRow)
                pai = entryPoint.parent()
                while pai is not None:
                    hierarchy.insert(0,[pai,pai])
                    pai = pai.parent()
            hierarchy.append([item,newRow[0]])
            newHead = newRow[0]
            isFirst = False
        else:
            newRow = makeRow(n.data(),i.data(),t.data() if t else None)
            ohier = hierTree(item)
            if len(ohier) == len(hierarchy):
                pass
            elif len(ohier) < len(hierarchy):
               del hierarchy[len(ohier):]
            else: #mas
                hierarchy.append(last)
            hierarchy[-1][1].appendRow(newRow)
        last = [n,newRow[0]]            
    return newHead

def traverse(model, key=None):
    if key is not None:
        yield key
        queue = childItems(key)
    else:
        queue = childItems(model.invisibleRootItem())
    while queue:
        yield queue[0] 
        expansion = childItems(queue[0])
        queue = expansion + queue[1:]  # depth-first

def getRow(item_ref,conTipo=False):
    """
    con tipo devuelve datos diferentes
    """
    if isinstance(item_ref,QModelIndex):
        index = item_ref 
    else:
        index = item_ref.index()
    model = index.model()  

    if index is None or not index.isValid():
        print('indice dañado seriamente')
        raise()
    nomidx = index.sibling(index.row(),0)
    itmidx = index.sibling(index.row(),1)
    tipidx = index.sibling(index.row(),2)
    nomItem= model.itemFromIndex(nomidx)
    item = model.itemFromIndex(itmidx)
    tipoItem = model.itemFromIndex(tipidx)
    headitem = item
    #if tipoItem.data() not in EDIT_TREE:
        #print('empiexa',nomItem.data(),item.data(),tipoItem.data())
    if conTipo:
        pai = index.parent()
        while not tipoItem: # or tipoItem.data() not in EDIT_TREE:
            tipoItem =model.itemFromIndex(pai.sibling(pai.row(),2))
            headitem = model.itemFromIndex(pai)
            pai = pai.parent()
        objtype = tipoItem.data()
        #print('termina',nomItem.data(),headitem.data(),tipoItem.data())
    if conTipo:
        return nomItem,item,tipoItem,headitem,objtype
    else:
        return nomItem,item,tipoItem

def branch2text(headItem):                    
    if not headItem.hasChildren():
        if headItem.column() == 1:
            return str(headItem.data())
        else:
            datosEnIdx = headItem.index().sibling(headItem.row(),1)
            datos = headItem.model().itemFromIndex(datosEnIdx).data()
            return str(datos)
    text = None
    clase = None
    for x in range(headItem.rowCount()):
        n,i,t = getRow(headItem.index().child(x,0))
        if x == 0:
            if n.data() is None:
                clase = 'L'
                text = branch2text(n)
            else:
                clase = 'D'
                text = "'{}':{}".format(n.data(),branch2text(n))
        else:
            if clase == 'L':
                text = ','.join((text,branch2text(n)))
            else:
                text = ','.join((text,"'{}':{}".format(n.data(),branch2text(n))))
    if clase == 'D':
        text = '{'+text+'}'
    else:
        text ='['+text+']'
    return text
        
 
if __name__ == '__main__':
    #readConfig()
    #testSelector()
    #editAsTree()
    #tools = {}
    #pprint(readUM(uf))
    #pprint(tools)
    #print(readUM(uf))
    exit()
    pruebaGeneral()
    #modelo =editAsTree()
            
            
    
        #print(getItemContext(item))



