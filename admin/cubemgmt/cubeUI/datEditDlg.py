#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from support.gui.treeEditor import *
from admin.cubemgmt.cubeTreeUtil import *
from support.gui.widgets import *
from base.datadict import DataDict

from PyQt5.QtWidgets import QFrame
from support.gui.dialogs import dateFilterDlg

"""
GETTERS
    executed at start of SetEditorData 
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist 
    input
            editor,
            item,
            view,
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)
    output
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)

SETTERS
    executed at the end of SetModelData
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist
        input  *lparm
            item = lparm[0]
            view = lparm[1]
            context = lparm[2]   Fundamentalmente para obtener el valor original context['data']
            ivalue / values = lparm[3]
            dvalue = lparm[4]
        output
            item, the edited item
"""
def _getDetailLine(hijo): #,elems):
    linea = [ None for m in range(5) ]
    campo = None
    numele = hijo.rowCount()
    for l in range(hijo.rowCount()):
        base = hijo.child(l,0).data()
        valor = hijo.child(l,1).data()
        if base == 'elem':
            #valores = []
            #for m in range(hijo.child(l,0).rowCount()):
                #valores.append(hijo.child(l,0).child(m,1).data())
            #elems.append(norm2String(valores))
            #elems.append(valor)
            campo = valor
        elif base == 'date class':
            linea[0] = valor
        elif base == 'date range':
            linea[1] = valor
        elif base == 'date period':
            linea[2] = valor
        linea[3] = None
        linea[4]= None
    return campo,linea 

def getDateFilter(*lparm):
    editor = lparm[0]
    item = lparm[1]
    view = lparm[2]
    dato = lparm[3]
    display = lparm[4]
    
    n,i,t = getRow(item)
    dato = []
    elems = []
    if n.data() ==  'date filter':
        for k in range(n.rowCount()):
            hijo = n.child(k,0)
            campo,linea = _getDetailLine(hijo)
            #dato.append(_getDetailLine(hijo,elems))
            if campo:
                elems.append(campo)
                dato.append(linea)
            
    elif t.data() == 'date filter':
        #dato.append(_getDetailLine(n,elems))
        campo,linea = _getDetailLine(n)
        if campo:
            elems.append(campo)
            dato.append(linea)
        
    gparm = list(lparm[1:3])
    gparm.insert(2,'@fmt') #formato
    gparm.insert(3,lambda i:i in ('fecha', 'fechahora'))
    datefields = srcFields(*gparm)
    
    for item in datefields:
        if item[0] in elems:
            continue
        else:
            elems.append(item[0])
            dato.append([0,0,1,None,None])

    environ = {'descriptores':elems,'datos':dato}
    return environ,display
                
def setDateFilter(editor,*lparm):
    item = lparm[0]
    view = lparm[1]
    context = lparm[2]  
    values = lparm[3]
    if not values or 'cancel' in values:
        return
    definicion = []
    fieldCtx = srcFields(item,view,extended=True)
    for k,entry in enumerate(values.get('datos',[])):
        if entry[1] != 0:
            formato = fieldCtx[entry[0].split('.')[-1]]['@fmt']
            if formato not in ('fecha','fechahora'):
                formato = 'fecha'
            definicion.append({
                                        'elem':entry[0],
                                        'date class': entry[1],
                                        'date range': entry[2],
                                        'date period': entry[3],
                                        'date start': None,
                                        'date end': None,
                                        'date format': formato
                                        })
    n,i,t = getRow(item)
    if definicion:
        if n.data() == 'date filter':
            for k in range(n.rowCount()):
                n.removeRow(k)
            dict2tree(n,None,definicion,'date filter',direct=True)
        elif t.data() == 'date filter':
            for k in range(n.rowCount()):
                n.removeRow(k)
                dict2tree(n,None,definicion[0],'date filter',direct=True)
    else:
        pai = n.parent()
        row = n.row()
        pai.removeRow(row)
        item = pai
    return item



def validateDateFilter():
    pass

 
