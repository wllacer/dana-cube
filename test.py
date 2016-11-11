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
try:
    import xlsxwriter
    XLSOUTPUT = True
except ImportError:
    XLSOUTPUT = False
    
(_ROOT, _DEPTH, _BREADTH) = range(3)

def presentaIndice(cubo,num):
    guia=cubo.lista_guias[num]['dir_row']
    ind = 0
    for key in traverse(guia,mode=1):
        elem = guia[key]
        print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
        ind += 1

def export(vista,parms,selArea=None):
    file = parms['file']
    type = parms['type']
    if type == 'xls' and not XLSOUTPUT:
        type = 'csv'
        print('Xls writer no disponible, pasamos a csv')
    fldSep  = parms['csvProp']['fldSep']
    txtSep = parms['csvProp']['txtSep'] 

    def csvFormatString(cadena):
        if fldSep in cadena:
            if txtSep in cadena:
                cadena = cadena.replace(txtSep,txtSep+txtSep)
            return '{0}{1}{0}'.format(txtSep,cadena)
        else:
            return cadena

    ctable,dim_row,dim_col = vista.getExportData(parms,selArea=None)
    if type == 'csv':
        with open(parms['file'],'w') as f:
            for row in ctable:
                csvrow = [ csvFormatString(item) for item in row ]
                f.write(fldSep.join(csvrow) + '\n')
        f.closed
    elif type == 'json':
        dump_structure(ctable,parms['file'])
    elif type == 'html':
        fldSep = '</td><td>'
        hdrSep = '</th><th>'
        with open(parms['file'],'w') as f:
            f.write('<table>\n')
            f.write('<head>\n')
            cont = 0
            for row in ctable:
                htmrow = [item.strip() for item in row ]
                if cont < dim_col:
                    f.write('<tr><th>'+hdrSep.join(htmrow) + '</th></tr>\n')
                    cont +=1
                elif cont == dim_col:
                    f.write('</thead>\n')
                    f.write('<tr><td>'+fldSep.join(htmrow) + '</td></tr>\n')
                    cont += 1
                else:
                    f.write('<tr><td>'+fldSep.join(htmrow) + '</td></tr>\n')
            f.write('</body>\n')
            f.write('</table>\n')
        f.closed

    elif type == 'xls':
        workbook = xlsxwriter.Workbook(parms['file'])
        worksheet = workbook.add_worksheet()
        for i,entry in enumerate(ctable):
            for j,item in enumerate(entry):
                worksheet.write(i, j,item.strip())
        workbook.close()
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

    #parms = eW.exportWizard()
    #if not parms.get('file'):
        #exit()
    #print(parms)
    
    vista=Vista(cubo,5,1,'sum','votes_presential',totalizado=True)
    pprint(vista.toTable())
    #pprint(vista.toTable())
    #resultado=toCsvOrig(vista,col_sparse=True)
    #resultado = export(vista,parms)
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
