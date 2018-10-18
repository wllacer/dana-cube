# -*- coding=utf -*-
"""
Part of  Global Common modules by Werner Llácer (c) 2012-2018

As an integral part of a project distributed under an Open Source Licence, the licence of the proyect
Used as  standalone module or outside the scope of  a project valid according to the  previous paragraph, or when  in doubt, distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
"""
non QT implentation of a tree. Not used @dana-cube. 
Should be upgraded to an support.util.tree compatible api

"""
from pprint import pprint

from support.util.numeros import stats

(_ROOT, _DEPTH, _BREADTH) = range(3)
(_KEY,_ITEM) = range(2)

import base.config as config

def traverse(tree, key=None, mode=1):
    return tree.traverse(key,mode,output = _ITEM)
    """
        variante de TreeDict.traverse().
        En lugar de las claves devuelve el item
        TODO deberia normalizar todos los traverses
        
    #"""
    #if key is not None:
        #yield tree.content[key]
        #queue = tree.content[key].childItems
    #else:
        #queue = tree.rootItem.childItems
        ##print(queue)
        ##print('')
    #while queue:
        #yield queue[0] 
        #expansion = queue[0].childItems
        #if mode == _DEPTH:
            #queue = expansion + queue[1:]  # depth-first
        #elif mode == _BREADTH:
            #queue = queue[1:] + expansion  # width-first

class TreeItem(object):
    def __init__(self, key, ord=None, desc=None, data=None, parent=None):
        self.key= key
        if desc is None:
            self.desc = key
        elif isinstance(desc,(list,tuple)):
            try:
                self.desc = ', '.join(desc)
            except TypeError:
                self.desc = ', '.join([str(item) for item in desc ])
        else:
            self.desc = desc
         
        self.parentItem = parent
        if ord is None:
            if parent is not None:
                self.ord = self.parent().childCount()
            else:
                self.ord = 0
        else:
            self.ord = ord
        self.itemData = data
        self.statsData = None
        self.origData = None
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None
        
    def getPayload(self):
        """ Devuelve una lista con el contenido (columnas) del item
        """
        if self.itemData is None or len(self.itemData) == 1:
            return None
        else:
            return self.itemData[1:]
    
    def getStatistics(self):
        return self.statsData
    
    def getLabel(self):
        if self.itemData is None:
            return None
        else:
            return self.itemData[0]
    
    def getKey(self):
        return self.key
    
    def hasChildren(self):
        if len(self.childItems) >0:
            return True
        else:
            return False
        
    def isTotal(self):
        if self.key == '//':
            return True
        else:
            return False
        
    def isBranch(self):
        if len(self.childItems) != 0 and not self.isTotal():
            return True
        else:
            return False
        
    def isLeaf(self):
        if len(self.childItems) == 0:
            return True
        else:
            return False

    def setData(self,data):
        self.itemData = data
        
    def setBackup(self):
        if self.origData is None :
            self.origData = self.itemData[:]

    def restoreBackup(self):
        if self.origData is not None :
            self.itemData = self.origData[:]
        else:
            self.itemData = None
      
    def lenPayload(self):
        return len(self.itemData) -1
    
    def setPayload(self,data):
        if self.itemData is None:
            self.itemData = [None,] + data
        else:
            self.itemData[1:] = data[:]
    
    def getPayloadItem(self,ind):
        try:
            return self.itemData[ind +1]
        except IndexError:
            return None      
    
    def gpi(self,ind):
        return self.getPayloadItem(ind)
    
    def setPayloadItem(self,ind,data):
        self.itemData[ind +1]=data
    
    def spi(self,ind,data):
        self.setPayloadItem(ind,data)
        
    def setLabel(self,label):
        if self.itemData is None:
            self.itemData = [label ,]
        else:
            self.itemData[0]=label
        
    def setStatistics(self):
        stat_dict = stats(self.getPayload())
        self.statsData=stat_dict

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0
    
    def depth(self):
        """
          la profundidad del arbol en ese punto. Empezando desde 1
        """
        ind = 0
        papi = self.parentItem
        while papi is not None:
            papi = papi.parentItem
            ind += 1
        return ind
    
    def getLevel(self):
        """
          el nivel actual. empieza en 0
        """
        return self.depth() -1
    
    def getFullDesc(self):
        fullDesc = [] #let the format be done outside
        fullDesc.append(self.desc)
        papi = self.parentItem
        while papi is not None:
            if papi.parentItem is None or papi.key == '//':  #FIXME esto es un chapu
                break
            fullDesc.insert(0,papi.desc) #Ojo insert, o sea al principio
            papi = papi.parentItem
        return fullDesc
    
    def getRoot(self):
        item = self
        while item.parentItem:
            item = item.parentItem
        return item

    def simplify(self):
        npay = list()
        ncab = list()
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            npay.append(value)
            ncab.append(k +1)
        return npay,ncab

    def simplifyHierarchical(self):
        profundidad = self.depth()
        tmppay = list()
        ncab = list()
        kitem = self
        while kitem.parent():
            tmppay.insert(0,kitem.getPayload())
            kitem = kitem.parent()
            
        npay = [list() for k in range(profundidad) ]    
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            for j in range(profundidad):
                npay[j].append(tmppay[j][k])
            ncab.append(k +1)
        return npay,ncab

    def model(self):
        rootItem = self.getRoot()
        return rootItem.modelID
    
    def __getitem__(self,campo):
        if campo == 'campo':
            return self.campo
        elif campo == 'desc':
            return self.desc
        elif campo == 'ord':
            return self.ord
        elif campo == 'key':
            return self.key
        elif isinstance(campo,int):
            return self.itemData[campo]
        else:
            return None
        
    def __str__(self): 
        return '{}->{}'.format(self.key,self.desc)
        
    def __repr__(self): 
        return 'TreeItem({},{},{})'.format(self.key,self.ord,self.desc)

class TreeDict(object):
    def __init__(self):
        self.content={}
        self.rootItemKey="/"
        self.rootItem=TreeItem(self.rootItemKey,-1,"RootNode")
        self.rootItem.modelID = self
        self.name = None

    def rebaseTree(self):
        if not self.exists('//'):
            self.content['//']=self.rootItem
            self.content['//'].key = '//'
            self.content['//'].desc= "Grand Total"
            newRoot=TreeItem(self.rootItemKey,-1,"RootNode")
            newRoot.appendChild(self.rootItem)
            self.rootItem.parentItem = newRoot
            self.rootItem = newRoot
            self.rootItem.modelID = self

       
    def __append(self,node):
        if node.parentItem == None:
            node.parentItem = self.rootItem
        self.content[node.key]=node
        node.parentItem.appendChild(node)
    
    def append(self,node,parentKey=None):
        if parentKey is None:
            self.__append(node)
        else:
        # este lo dejo fallar
        # tengo dos opciones
        # 1) try e ignorar las claves inexistentes y
        # 2) construir las claves sobre la marcha. De momento voy a ignorarla, puede capturar mas casos generales
            try:
                node.parentItem = self.content[parentKey]
            except KeyError :
                node.parentItem = None

            self.__append(node)

        
    def searchNode(self,key):
        try:
            return self.content[key]
        except KeyError:
            return None
     
    def count(self):
        return len(self.content)
    
    def __lenIter(self,elem):

        has = elem.childCount()
        if has != 0:
            for item in elem.childItems:
                has += self.__lenIter(item)
        return has
        
    def len(self):
        return self.__lenIter(self.rootItem)

    def queryAdd(self,node):
        if node.parentItem != None :
            pass
        else:
           node.parentItem = self.searchNode(node.key) #FIXME no tengo claro que esto sea lo que quiero
           if node.parentItem == None:
               node.parentItem = self.rootItem
        self.__add(node)
        
    def item(self,key):
        return self.__getitem__(key)
    
    def __getitem__(self, key):
        return self.content[key]
    
    def exists(self,key):
        item = self.content.get(key,None)
        if item:
            return True
        else:
            return False
    def display(self, key=None, depth=_ROOT):
        if key is None:
            children = self.rootItem.childItems
        else:
            children = self.content[key].childItems
        if depth == _ROOT:
            print("{0}".format(key))
        else:
            print("\t"*depth, "{0}".format(key))

        depth += 1
        for child in children:
            self.display(child.key, depth)  # recursive call



    def traverse(self, key=None, mode=_DEPTH, output = _KEY):
        # Obtenido de
        # Brett Kromkamp (brett@perfectlearn.com)
        # You Programming (http://www.youprogramming.com)
        # May 03, 2014, que afirma
        # Python generator. Loosly based on an algorithm from 
        # 'Essential LISP' by John R. Anderson, Albert T. Corbett, 
        # and Brian J. Reiser, page 239-241
        #if key is None:
            #yield self.rootItem.childItems[0].key
            #queue = self.rootItem.childItems[1:]
        #else:
            
        if key is not None:
            yield self.item(key) if output == _ITEM else key
            queue = self.item(key).childItems
        else:
            queue = self.rootItem.childItems
        while queue:
            yield queue[0] if output == _ITEM else queue[0].key
            expansion = queue[0].childItems
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def restrictedTraverse(self, key=None, mode=_DEPTH):
        # 
        # Basado en el anterior
        # FIXME solo valido para arboles equilibrados
        #
        if key is not None:
            yield key
            queue = self.content[key].childItems
        else:
            queue = self.rootItem.childItems
        while queue:
            if queue[0].childCount() > 0:
                yield queue[0].key
                expansion = queue[0].childItems   
            else:
                expansion = []
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def setHeader(self):
        header = [None for k in range(self.count())] 
        for item in self.traverse(output = _ITEM):
            clave = item.getFullDesc()
            try:
                header[item.ord] = clave
            except IndexError:
                print('Canturriazo',self.count(),item,item.ord,item.model().name)
                exit()
        return header

    def getHeader(self,tipo='row',separador='\n',sparse=True):
        if sparse:
            cabecera = [ item[-1].replace(config.DELIMITER,'-') for item in self.setHeader() ]
        else:
            cabecera = [ separador.join([ entry.replace(config.DELIMITER,'-') for entry in item]) for item in self.setHeader()]
        if tipo == 'row':
            return cabecera
        else:
            return ['',] + cabecera

    def filterCumHeader(self,total=True,branch=True,leaf=True,separador='\n',sparse=True):
        lista = []
        for item in self.traverse(output = _ITEM):
            if total and item.isTotal():
                pass
            elif branch and item.isBranch():
                pass
            elif leaf and item.isLeaf():
                pass
            else:
                continue
            
            clave = item.getFullDesc()
            if sparse:
                for k in range(len(clave) -1):
                    clave[k]=''
            lista.append((item,clave,))
        return lista
        
    
if __name__ == '__main__':
     item=TreeItem('alfa')
     #item.setLabel('omega')
     datos = [1,2,3,4,5]
     item.setPayload(datos)
     print(item,item.itemData)
