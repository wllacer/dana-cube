# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

(_ROOT, _DEPTH, _BREADTH) = range(3)


class TreeItem(object):
    
    def __init__(self, key, ord=None, desc=None, data=None, parent=None):
        self.key= key
        if desc is None:
            self.desc = key
        else:
            self.desc = desc
        self.ord = ord
        self.parentItem = parent
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

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0
    
    def getLevel(self):
        ind = 0
        papi = self.parentItem
        while papi is not Null:
            papi = papi.parentItem
            ind += 1
   
    def getFullDesc(self):
        fullDesc = [] #let the format be done outside
        fullDesc.append(self.desc)
        papi = self.parentItem
        while papi is not Null:
            fullDesc.insert(0,papi.desc) #Ojo insert, o sea al principio
            papi = papi.parentItem


class TreeDict(object):
    def __init__(self):
        self.content={}
        self.rootItemKey="/"
        self.rootItem=TreeItem(self.rootItemKey,-1,"RootNode")
        
    def __add(self,node):
        if node.parentItem == None:
            node.parentItem = self.rootItem
        self.content[node.key]=node
        node.parentItem.appendChild(node)
    
    def add(self,node,parentKey=None):
        if parentKey is None:
            self.__add(node)
        else:
        # este lo dejo fallar
            node.parentItem = self.content[parentKey]
            self.__add(node)
        
    def searchNode(self,key):
        try:
            return self.content[key]
        except KeyError:
            return None
     
    def queryAdd(self,node):
        if node.parentItem != None :
            pass
        else:
           node.parentItem = self.searchNode(key)
           if node.parentItem == None:
               node.parentItem = self.rootItem
        self.__add(node)

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
        if key is None:
            yield '/'
            queue = self.rootItem.childItems
        else:
            yield key
            queue = self.content[key].childItems
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

