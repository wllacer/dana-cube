#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2019

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

Vamos a probar el uso de rollup para generar la vista
"""
import sys
sys.path.append('/home/werner/projects/dana-cube.git')

from base.tree import *
from support.util import decorators
from base.core import *
from PyQt5.QtWidgets import QApplication,QDialog,QDialogButtonBox,QComboBox,QLabel,QVBoxLayout
from pprint import pprint
import  base.config

from total_core import *

def test_genera_comp():
    """
    probar todas las combinaciones posibles y las diferencias de implementacion
    
    """
    from support.util.jsonmgr import load_cubo
    from support.util.numeros import avg
    from random import randint
    mis_cubos = load_cubo('testcubo.json')
    cubo = Cubo(mis_cubos['datos locales pg'])
    for guia in cubo.lista_guias:
        for guia2 in cubo.lista_guias:
            if guia['name'] == 'geo-detail' or guia2['name'] == 'geo-detail':
               continue
            print ('procesando ',guia['name'],guia2['name'])
            test_comp(cubo,guia['name'],'partido')
        #test_comp(cubo,'partido',guia['name'])     
 
@stopwatch
def with_rollup(cubo,row,col):
    vista = Vista(cubo,row,col,'sum','votes_presential',totalizado=False)
    vista.toNewTree2D()
    return vista 

@stopwatch
def with_clone(cubo,row,col):
    vista = Vista2(cubo,row,col,'sum','votes_presential',totalizado=False)
    vista.toNewTree2D()
    return vista 


def test_comp(cubo,rowname,colname,show=False):
    """
    Comprobar el comportamiento del rollup
    FIXME  ¿Como distingue el rollup de los nulos de cabecera con los nulos de uso practico ?
    """
    vista = with_clone(cubo,rowname,colname) 
    wisout = []
    for row in vista.row_hdr_idx.traverse():
        wisout.append((row.text(),row.getPayload()))

    vista2 = with_rollup(cubo,rowname,colname) 
    wisin = []
    for row in vista2.row_hdr_idx.traverse():
        wisin.append((row.text(),row.getPayload()))
    
    if wisout != wisin:
        print('NO coinciden las ejecuciones para fila {} y columna {}'.format(rowname,colname))
    if show:
        print('sin ',len(wisout),'con',len(wisin))
        for k in range(min(len(wisout),len(wisin))):
                print(wisout[k])
                print(wisin[k])
                print()
    return

def short_test_sim():
    """
    Comprobar el comportamiento del rollup
    FIXME  ¿Como distingue el rollup de los nulos de cabecera con los nulos de uso practico ?
    """
    from support.util.jsonmgr import load_cubo
    from support.util.numeros import avg
    from random import randint
    mis_cubos = load_cubo('../testcubo.json')
    cubo = Cubo(mis_cubos['datos locales'])
    row = 'partido'
    col = 'geo'
    vista = Vista2(cubo,row,col,'sum','votes_presential',totalizado=True)
    #pprint(vista.array)
    #for item in vista.col_hdr_idx.traverse():
        #print(item.text(),item.getFullHeadInfo(content='key',format='array'))
    for line in vista.toList():
        print(line)
    print()
    for line in vista.toList(rowHdrContent='key',rowFilter=lambda x:x.type() == TOTAL):
        print(line)

    #vista.toNewTree2D()
    #for fila in vista.row_hdr_idx.traverse():
        #print(fila.text(),fila.getPayload())
    #return vista 
    #return
  


if __name__ == '__main__':    
    app = QApplication(sys.argv)
    config.DEBUG = False
    function = short_test_sim
    parms = []
    if len(sys.argv) > 1:
        function = locals()[sys.argv[1]]
        if len(sys.argv) > 2:
            parms = sys.argv[2:]
    function(*parms)
