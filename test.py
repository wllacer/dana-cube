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
from exportWizard import miniWizard
from util.numbers import fmtNumber

(_ROOT, _DEPTH, _BREADTH) = range(3)

def presentaIndice(cubo,num):
    guia=cubo.lista_guias[num]['dir_row']
    ind = 0
    for key in traverse(guia,mode=1):
        elem = guia[key]
        print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
        ind += 1

def __getHeader(header_tree,dim,sparse,content):
    tabla = list()
    for key in header_tree.traverse(mode=1):
        entry = ['' for k in range(dim) ]
        elem = header_tree[key]
        if content == 'branch' and elem.isLeaf() and dim > 1:
            continue
        if content == 'leaf' and not elem.isLeaf():
            continue
        
        desc = elem.getFullDesc() 
        if sparse:
            entry[elem.depth() -1] = desc[-1]
        else:
            for k in range(desc):
                entry[k] = desc[k]
                
        if content == 'branch' and dim > 1:
            del entry[dim -1 ]
        elif content == 'leaf' :
            while len(entry) > 1:
                del entry[0]
                
        entry.append(elem.ord)
        tabla.append(entry)
    return tabla  

def export(vista,parms,selArea=None):
    """
        parms['file']
        parms['type'] = ('csv','xls','json','html')
        *parms['csvProp']['fldSep'] 
        *parms['csvProp']['decChar']
        *parms['csvProp']['txtSep'] 
        *parms['NumFormat'] 
        parms['filter']['scope'] = ('all','visible,'select') 
        *parms['filter']['content'] = ('full','branch','leaf')
        parms['filter']['totals'] 
        *parms['filter']['horSparse'] 
        *parms['filter']['verSparse']

    """
    contentFilter = parms['filter']['content']
    row_sparse = parms['filter']['horSparse']
    col_sparse = parms['filter']['verSparse']
    translated = parms['NumFormat']
    fldSep  = parms['csvProp']['fldSep']
    txtSep = parms['csvProp']['txtSep']                       
    numFmt = parms['NumFormat']
    decChar = parms['csvProp']['decChar']
    
    ind = 1
    
    def csvFormatString(cadena):
        if fldSep in cadena:
            if txtSep in cadena:
                cadena = cadena.replace(txtSep,txtSep+txtSep)
            return '{0}{1}{0}'.format(txtSep,cadena)
        else:
            return cadena

    def num2text(number):
        if numFmt:
            return fmtNumber(number,{'decimalmarker':decChar})[0]
        elif decChar != '.':
            return '{}'.format(number).replace('.',decChar)
        else:
            return str(number)
    
    dim_row = vista.dim_row
    dim_col = vista.dim_col
        
    row_hdr = __getHeader(vista.row_hdr_idx,dim_row,row_sparse,contentFilter)
    col_hdr = __getHeader(vista.col_hdr_idx,dim_col,col_sparse,contentFilter)
    
    num_rows = len(row_hdr)
    num_cols = len(col_hdr)
    
    dim_row = len(row_hdr[0]) -1
    dim_col = len(col_hdr[0]) -1
    
    ctable = [ ['' for k in range(num_cols + dim_row)] 
                            for j in range(num_rows +dim_col) ]

    for i in range(num_cols):
        for j,colItem in enumerate(col_hdr[i]):
            if j >= dim_col:
                break
            ctable[j][i + dim_row]=colItem
            
    for i in range(num_rows):
        for j,rowItem in enumerate(row_hdr[i]):
            if j >= dim_row:
                break
            ctable[i + dim_col][j]=rowItem
    table = vista.toTable()
    
    for i in range(num_rows):
        x = row_hdr[i][-1]
        for j in range(num_cols):
            y = col_hdr[j][-1]
            ctable[i + dim_col][j + dim_row] = num2text(table[x][y]) if table[x][y] else ''  #TODO aqui es el sito de formatear numeros
            
    with open(parms['file'],'w') as f:
        for row in ctable:
            f.write(fldSep.join(row) + '\n')
    f.closed
    #return lineas


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
    vista=Vista(cubo,5,1,'sum','votes_percent')
    convertParms = miniWizard()
    print(convertParms)
    #resultado=toCsvOrig(vista,col_sparse=True)
    resultado = export(vista,convertParms)
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
