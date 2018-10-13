#!/usr/bin/python
# -*- coding: utf-8 -*-

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
navegacion por un modelo QAbstractItemModel

apis
    def traverse(tree,elem=None)
    def traverse(root,elem=None)
    def traverse(elem)
mode
    _DEPTH              Por profundidad (orden 0, 0.0, 0.0.0, 0.0.1, 0.0.2, 0.1, ...)
    _BREADTH         Por anchura (primero resolvemos cada uno de los niveles, i,e primero todas las de nivel 0, luego las de nivel 1, etc)

inspirado en un ejemplo de  [Brett Kromkamp](http://www.quesucede.com/page/show/id/python-3-tree-implementation)

"""
_DEPTH,_BREADTH = range(1,3)

from PyQt5.QtCore import QAbstractItemModel,QModelIndex
#from support.util.tree_abstract import TreeDict

#def traverseBasicOld(root,base=None,mode=_DEPTH):
    #if base is not None and base != root:
       #yield base
       #queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        #if expansion is None:
            #del queue[0]
        #else:
            #if mode == _DEPTH:
                #queue = expansion  + queue[1:]  
            #elif mode == _BREADTH:
                #queue = queue[1:] + expansion

def traverseBasic(root,base=None,mode=_DEPTH,filter=None):
    """
    ejemplo de uso de filter 
    ```
        for item in traverseBasicFiltered(vista.row_hdr_idx.invisibleRootItem(),
                                                            None,
                                                            filter=lambda x:not(x.data(Qt.CheckStateRole))
                                                            ):
            print(item.getFullKey(),item.text(),item.getPayload())
    ```
    """
    if base is not None and base != root:
       yield base
       queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        if (not filter) or filter(queue[0]):
            yield queue[0]
            expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        else:
            expansion = None
        if expansion is None:
            del queue[0]
        else:
            if mode == _DEPTH:
                queue = expansion  + queue[1:]  
            elif mode == _BREADTH:
                queue = queue[1:] + expansion
        
def traverseAndDrop(root,base=None,mode=_DEPTH,filter=None):
    """
    ejemplo de uso de filter 
    ```
        for item in traverseBasicFiltered(vista.row_hdr_idx.invisibleRootItem(),
                                                            None,
                                                            filter=lambda x:not(x.data(Qt.CheckStateRole))
                                                            ):
            print(item.getFullKey(),item.text(),item.getPayload())
    ```
    """
    if base is not None and base != root:
       yield base
       queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        if (not filter) or filter(queue[0]):
            yield queue[0]
            expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        else:
            pai = queue[0].parent()
            if not pai:
                pai = queue[0].inivisibleRootItem()
            row = queue[0].row()
            print('a borrar',queue[0].getFullKey())
            pai.removeRow(row)
            expansion = None
        if expansion is None:
            del queue[0]
        else:
            if mode == _DEPTH:
                queue = expansion  + queue[1:]  
            elif mode == _BREADTH:
                queue = queue[1:] + expansion
                
def traverse(*lparm,**kwparm):
    start = None
    #action = traverseBasic
    if isinstance(lparm[0],(QAbstractItemModel,)):
        tree = lparm[0]
        root = tree.invisibleRootItem() #es de QAIM ¿?
        if len(lparm) > 1:
            start= lparm[1]
        else:
            start = None
    else:
        tree = lparm[0].model()
        if len(lparm) == 1:
            start = lparm[0]
            root = tree.invisibleRootItem()
        else:
            root = lparm[0]
            start = lparm[1]
    mode = kwparm.get('mode',_DEPTH)
    filter =  kwparm.get('filter')
    return traverseBasic(root,start,mode,filter)

def _getRow(lineHdr):
    """
    """
    return [ col for col in rowTraverse(lineHdr) ]
   
def rowTraverse(self):
    pai =  self.parent() if self.parent() else self.model().invisibleRootItem()
    row = self.row()
    for k in range(pai.columCount()):
        yield pai.child(row,k)
            
def dumpTree(*lparm,**kwparm):
    model = None
    for line in traverse(*lparm,**kwparm):
        if not model:
            model = line.model()
        yield _getRow(line)
