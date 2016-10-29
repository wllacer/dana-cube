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

   
from dictmgmt.dictTree import *
from dictmgmt.datadict import *
from tablebrowse import getTable

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter


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


if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    confName = 'MariaBD Local'
    schema   = 'sakila'
    table    = 'payment'
    iters    = 2
    dataDict=DataDict(conn=confName,schema=schema,table=table,iters=iters)
    for entry in traverse(dataDict.hiddenRoot):
        tabs = '\t'*entry.depth()
        if entry.type() != BaseTreeItem : #not entry.isAuxiliar():
            print(entry.getTypeText(),tabs,entry.text(),entry.fqn(),entry.getFullDesc()) # entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    info = getTable(dataDict,confName,schema,table)    
    pprint(info)
