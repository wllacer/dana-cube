#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from PyQt5.QtCore import QAbstractItemModel
#from support.util.tree_abstract import TreeDict

def traverseBasic(root,base=None,mode=_DEPTH):
    if base is not None and base != root:
       yield base
       queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
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
    return traverseBasic(root,start,mode)

