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
from core import Cubo,Vista
#from datalayer.query_constructor import *
#from operator import attrgetter,methodcaller

from pprint import pprint

from  PyQt5.QtWidgets import QApplication


#import exportWizard as eW
#from util.numeros import fmtNumber
#from util.jsonmgr import dump_structure
from util.mplwidget import SimpleChart
  
#import math
#import matplotlib.pyplot as plt
#import numpy as np
 
from PyQt5 import QtCore
#from PyQt5.QtGui import QSizePolicy
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QGridLayout, QSizePolicy, QWidget, QTreeView, QHBoxLayout

from dictmgmt.datadict import DataDict

(_ROOT, _DEPTH, _BREADTH) = range(3)

def traverse(root,base=None):
    if base is not None:
       yield base
       queue = base.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]      
def prueba():
    dd = DataDict()
    # defFile
    # conName
    # schema
    # table
    # iters
    # confData (connexion Data)
    # pos
    # dd= DataDict(conn=confName,schema=schema)
    # dd= DataDict(conn=confName,schema=schema,table=table,iters=iters,confData=confData) 
    pprint(dd.configData)
    #print(dd.baseModel)
    pprint(dd.conn)
    #print(dd.hiddenRoot)
    #for entry in traverse(dd.hiddenRoot):
        #tabs = '\t'*entry.depth()
        #if not entry.isAuxiliar():
            #print(tabs,entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())

    #print(dd.isEmpty)
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    #aw = ApplicationWindow()
    #aw.show()
    prueba()
