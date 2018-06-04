#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

#from support.util.uf_manager import *
#from support.util.jsonmgr import *

from PyQt5.QtCore import Qt,QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from support.util.record_functions import norm2List

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
        doublet = [None,None]
        if isinstance(parms[k],(list,tuple)):
            doublet[0] = parms[k][0]
            doublet[1] = str(parms[k][1]) if len(parms[k] > 1) or parms[k][1] is not None else None
        else:
            doublet[0] = parms[k]
            doublet[1] = str(parms[k]) if parms[k] is not None else None
        
        elem = QStandardItem(doublet[1])
        elem.setData(doublet[0],Qt.UserRole +1)
        retorno.append(elem)
    return retorno

def dict2tree(parent,key,data,tipo=None,direct=False):
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
        return
    if direct:
        newparent = parent
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
                for texto in ('name','result','default'):
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
    toList = False
    toDict = False

    if rootItem == rootItem.model().invisibleRootItem() :
            toDict = True #la raiz siempre genera directorio
    elif esdiccionario and esdiccionario(rootItem):   
        toDict = True
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

def traverse(*lparms):
    if len(lparms) >=2:
        model = lparms[0]
        key = lparms[1]
    elif len(lparms) == 1:
        if isinstance(lparms[0],QStandardItemModel):
            model = lparms[0]
            key = model.invisibleRootItem()
        else:
            key = lparms[0]
            model = lparms[0].model()
            
    if key == model.invisibleRootItem():
        queue = childItems(model.invisibleRootItem())
    elif key is not None:
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
        
def getItemTopDown(parent,namearr):
    name = namearr[0]
    hijo  = getChildByName(parent,name)
    if not hijo:
        print('no encontre nada para',name)
        return None
    else:
        del namearr[0]
        if len(namearr) > 0:
            return getItemTopDown(hijo,namearr)
        else:
            return hijo
                
def getChildByName(parent,name):
    for entry in childItems(parent):
        if entry.data() == name:
            return entry
    return None

def getParentByName(item,name):
    pai = item #por si acaso
    while pai:  #evitamos 
        if pai.data() == name:
            return pai
        pai = pai.parent()
    return None

def getChildByType(parent,type):
    for entry in childItems(parent):
        n,i,typeItem = getRow(entry)
        if typeItem and typeItem.data() == type:
            return entry
    return None

def getChildByTypeH(parent,typeList):
    base = parent
    for tipo in norm2List(typeList):
        res = getChildByType(base,tipo)
        if not res:
            return None
        base = res
    return base

def getParentByType(item,type):
    pai = item #por si acaso
    while pai:  #evitamos 
        n,i,typeItem = getRow(pai)
        if typeItem and typeItem.data() == type:
            return pai
        pai = pai.parent()
    return None


def mergeEditData(parentData,childData):
    """
    
    TODO hacerlo de modo que utilice ambos sin saber cuales son
    
    """
    #attr =('objtype','subtypes','discriminator','elements','getters','setters','diggers','validator','text','menuActions')
    fromChild = ('objtype','subtypes','discriminator')
    fromParent = ()
    priorityCommon = ('editor','getters','setters','diggers','validator','menuActions','text','hint')  #from both sources child has priority
    mergeCommon =('elements',) #accumulated
    new_edit = {}
    for entry in fromParent:
        if parentData.get(entry):
            new_edit[entry] = parentData.get(entry)
    for entry in fromChild:
        if childData.get(entry):
            new_edit[entry] = childData.get(entry)
    for entry in priorityCommon:
        if parentData.get(entry):
            new_edit[entry] = parentData.get(entry)
        if childData.get(entry):
            new_edit[entry] = childData.get(entry)
    for entry in mergeCommon:
        lista = []
        if parentData.get(entry):
            lista += parentData.get(entry)
        if childData.get(entry):
            lista += childData.get(entry)
        if len(lista) > 0:  
            new_edit[entry] = lista
            
    return new_edit
        
def subTypeDiscover(item,edit_data):
        rowHead,i,t = getRow(item)
        subtipo = None
        discriminador = edit_data.get('discriminator','subtype')
        if discriminador and callable(discriminador):
            subtipo = discriminador(rowHead,None)
        else:
            subItem = getChildByType(discriminador)
            if subItem:
                nh,ni,nj = getRow(subItem)
                subtipo = ni.data()
        return subtipo

def getFullElementList(treeDef,orlist):
    """
    devuelve una lista de elementos con los grupos resueltos
    parametros:
        treeDef -> la definicion del arbol
        orlist -> la lista original
    """
    elementos = orlist  #una copia o puedo organizar un guirigay
    # voy ahora a cargar los grupos en la lista de elementos 
    # este bucle a la antigua es para evitar problemas porqu estoy expandiendo dinamicamente la lista de elementos
    k = 0
    grupos = set()
    while k < len(elementos):
        elemento = elementos[k]
        tipo = treeDef.get(elemento[0],{}).get('objtype','atom')
        if tipo == 'group': 
            grupos.add(elemento[0])
            # si no me casca el for es lo mas interesante, porque permite recursividad
            for entrada in treeDef.get(elemento[0],{}).get('elements',[]):
                elementos.append(entrada)
        k += 1
    # ahora elimino de la lista los grupos, porque ya no los necesito
    for grupo in grupos:
        idx = [ entry[0] for entry in elementos].index(grupo)
        del elementos[idx]
    return elementos

def getRealType(item,treeDef,editType):
    definicion = treeDef.get(editType,{})
    if len(definicion.get('subtypes',[])) > 0:
        retorno = subTypeDiscover(item,definicion)
        if retorno:
            return retorno
    return editType

def getRealEditDefinition(item,treeDef,original):   
    tipo = original
    definicion = treeDef.get(original,{})
    if len(definicion.get('subtypes',[])) > 0:
        retorno = subTypeDiscover(item,definicion)
        if retorno:
            tipo = retorno
            definicion = mergeEditData(treeDef.get(original),treeDef.get(retorno))
    #TODO incluir los elementos desplegados. Desactivado de momento
    if 'elements' in definicion:
            definicion['elements'] = getFullElementList(treeDef,definicion.get('elements',[]))
    return original,definicion


def numEntries(tree):
    k = 0
    k = 0
    for item in traverse(tree):
        k +=1
    print('hay ',k, ' entradas')
    return k

def padd(lista,num,default=None,pos='after',truncate=True):
    """
    devuelve una copia con el relleno que indico
    """
    original = len(lista)
    if original >= num:
        if not truncate:
            return lista[:]
        else:
            return lista[:num]
    resultado = lista[:]
    for k in range(num - len(lista)):
        if pos == 'after':
            resultado.append(default)
        elif pos == 'before':
            resultado.insert(0,default)
    return resultado

def fullKey(item):
    result = []
    n,i,t = getRow(item)
    result.append(n.data())
    pai = n.parent()
    while pai:
        result.insert(0,str(pai.data()))
        pai = pai.parent()
    return result

def getNorm(diccionario,parametro,default=''):
    """
    normaliza el valor nulo a '' para un determinado elemento de un diccionario
    recordar que is not es verdadero para nulos y estructuras vacias, p.e. '' o numericos 0
    c.f
    prins = ( None,"None","none",'','uno','dos',[],{},0,-1,+1)
    for cosa in prins:
        if not cosa:
            print(cosa,' is not')
        else:
            print(cosa,'is')

    """
    result = diccionario.get(parametro,default)
    
    if not result or str(result).lower() == "none":
        result = default
    return result


if __name__ == '__main__':
    #readConfig()
    #testSelector()
    #editAsTree()
    #tools = {}
    #pprint(readUM(uf))
    #pprint(tools)
    #print(readUM(uf))
    exit()
    #modelo =editAsTree()
            
            
    
        #print(getItemContext(item))



