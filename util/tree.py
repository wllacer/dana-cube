# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from util.numbers import stats

(_ROOT, _DEPTH, _BREADTH) = range(3)
(_KEY,_ITEM) = range(2)

DELIMITER=':'

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
    
    def hasChildren(self):
        if len(self.childItems) >0:
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
            if papi.parentItem is None:  #FIXME esto es un chapu
                break
            fullDesc.insert(0,papi.desc) #Ojo insert, o sea al principio
            papi = papi.parentItem
        return fullDesc
    
    def __getitem__(self,key):
        if key == 'key':
            return self.key
        elif key == 'desc':
            return self.desc
        elif key == 'ord':
            return self.ord
        else:
            return self.itemData[key]
        
    def __str__(self): 
        return '{}->{}'.format(self.key,self.desc)
        
    def __repr__(self): 
        return 'TreeItem({},{},{})'.format(self.key,self.ord,self.desc)

class TreeDict(object):
    
    def __init__(self):
        self.content={}
        self.rootItemKey="/"
        self.rootItem=TreeItem(self.rootItemKey,-1,"RootNode")


    def rebaseTree(self):
        if not self.exists('//'):
            self.content['//']=self.rootItem
            self.content['//'].key = '//'
            self.content['//'].desc= "Grand Total"
            newRoot=TreeItem(self.rootItemKey,-1,"RootNode")
            newRoot.appendChild(self.rootItem)
            self.rootItem.parentItem = newRoot
            self.rootItem = newRoot
       
        
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
            node.parentItem = self.content[parentKey]
            self.__append(node)
        
    def searchNode(self,key):
        try:
            return self.content[key]
        except KeyError:
            return None
     
    def count(self):
        return len(self.content)
    
    def queryAdd(self,node):
        if node.parentItem != None :
            pass
        else:
           node.parentItem = self.searchNode(key)
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

if __name__ == '__main__':
     item=TreeItem('alfa')
     #item.setLabel('omega')
     datos = [1,2,3,4,5]
     item.setPayload(datos)
     print(item,item.itemData)
