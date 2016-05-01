# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

(_ROOT, _DEPTH, _BREADTH) = range(3)
DELIMITER=':'

class TreeItem(object):
    
    def __init__(self, key, ord=None, desc=None, data=None, parent=None):
        self.key= key
        if desc is None:
            self.desc = key
        elif isinstance(desc,(list,tuple)):
            self.desc = ', '.join(desc)
        else:
            self.desc = desc
         
        self.parentItem = parent
        if ord is None:
            self.ord = self.parent().childCount()
        else:
            self.ord = ord
        self.itemData = data
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

    def setData(self,data):
        self.itemData = data
        
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
    
    def __str__(self): 
        return '{}->{}'.format(self.key,self.desc)
        
    def __repr__(self): 
        return 'TreeItem({},{},{})'.format(self.key,self.ord,self.desc)

class TreeDict(object):
    def __init__(self):
        self.content={}
        self.rootItemKey="/"
        self.rootItem=TreeItem(self.rootItemKey,-1,"RootNode")
        
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
        
    def __getitem__(self, key):
        return self.content[key]
    

    def display(self, key=None, depth=_ROOT):
        # Obtenido de
        # Brett Kromkamp (brett@perfectlearn.com)
        # You Programming (http://www.youprogramming.com)
        # May 03, 2014, que afirma
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

    def traverse(self, key=None, mode=_DEPTH):
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
            yield key
            queue = self.content[key].childItems
        else:
            queue = self.rootItem.childItems
        while queue:
            yield queue[0].key
            expansion = queue[0].childItems
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first


if __name__ == '__main__':
    # Copyright (C) by Brett Kromkamp 2011-2014 (brett@perfectlearn.com)
    # You Programming (http://www.youprogramming.com)
    # May 03, 2014


    (_ROOT, _DEPTH, _BREADTH) = range(3)

    tree = TreeDict()

    tree.add(TreeItem("Harry"))  # 
    tree.add(TreeItem("Jane"), "Harry")
    tree.add(TreeItem("Bill"), "Harry")
    tree.add(TreeItem("Joe"), "Jane")
    tree.add(TreeItem("Diane"), "Jane")
    tree.add(TreeItem("George"), "Diane")
    tree.add(TreeItem("Mary"), "Diane")
    tree.add(TreeItem("Jill"), "George")
    tree.add(TreeItem("Carol"), "Jill")
    tree.add(TreeItem("Grace"), "Bill")
    tree.add(TreeItem("Mark"), "Jane")
    print(tree.content)
    tree.display("Harry")
    print("***** DEPTH-FIRST ITERATION *****")
    for node in tree.traverse("Harry"):
        print(node)
    print("***** BREADTH-FIRST ITERATION *****")
    for node in tree.traverse("Harry", mode=_BREADTH):
        print(node)

