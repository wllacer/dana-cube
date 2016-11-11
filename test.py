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
from operator import attrgetter,methodcaller

from pprint import pprint

from  PyQt5.QtWidgets import QApplication


import exportWizard as eW
from util.numbers import fmtNumber
from util.jsonmgr import dump_structure
    
(_ROOT, _DEPTH, _BREADTH) = range(3)

def presentaIndice(cubo,num):
    guia=cubo.lista_guias[num]['dir_row']
    ind = 0
    for key in traverse(guia,mode=1):
        elem = guia[key]
        print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
        ind += 1




def experimental():
    from util.jsonmgr import load_cubo
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['datos light'])
    #for ind,guia in enumerate(cubo.lista_guias):
        #print(ind,guia['name'])

    ind=2
    #pprint(cubo.lista_guias[4])
    #cubo.fillGuia(ind)

    parms = eW.exportWizard()
    if not parms.get('file'):
        exit()
    print(parms)
    
    vista=Vista(cubo,5,1,'sum','votes_presential',totalizado=True)
    k=vista.toTree2D()
    #pprint(vista.toTable())
    #pprint(vista.toTable())
    #resultado=toCsvOrig(vista,col_sparse=True)
    parms['filter']['scope'] = 'test'
    resultado = vista.export(parms)
    #for entrada in resultado:
        #print(entrada)
    #for elem in (sorted(guia.content,key=methodcaller('childCount'),reverse=True)):
        #print(elem,sorted(guia[elem].childItems,key=attrgetter('desc')))
        #print(elem,sorted(guia[elem].childItems,key=methodcaller('childCount'),reverse=True))
        #print(elem)
def traverse(tree, key=None, mode=1):
    # Obtenido de
    # Brett Kromkamp (brett@perfectlearn.com)
    # You Programming (http://www.youprogramming.com)
    # May 03, 2014, que afirma
    # Python generator. Loosly based on an algorithm from 
    # 'Essential LISP' by John R. Anderson, Albert T. Corbett, 
    # and Brian J. Reiser, page 239-241
    if key is not None:
        yield key
        queue = tree.content[key].childItems
    else:
        queue = tree.rootItem.childItems
        print(queue)
        print('')
    while queue:
        yield queue[0].key
        expansion = queue[0].childItems
        if mode == _DEPTH:
            queue = expansion + queue[1:]  # depth-first
        elif mode == _BREADTH:
            queue = queue[1:] + expansion  # width-first
   
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    numero = -232145.1234567890123
    #print(fmtNumber(numero))
    #print(fmtNumber(numero,{'decimalmarker':','}))
    experimental()
