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

from models import *

(_ROOT, _DEPTH, _BREADTH) = range(3)




def simplify(payload,cabeceras):
    npay = list()
    ncab = list()
    for k,item in enumerate(payload):
        if not item:
            continue
        npay.append(item)
        ncab.append(cabeceras[k +1])
    return npay,ncab

def msimplify(payload,cabeceras):
    if not isinstance(payload[0],(list,tuple)):
        return simplify(payload,cabeceras)
    profundidad = len(payload)
    npay = [ list() for k in range(profundidad)]
    ncab = list()
    for k,item in enumerate(payload[-1]):
        if not item:
            continue
        for j in range(profundidad):
            npay[j].append(payload[j][k])
        ncab.append(cabeceras[k +1])
    return npay,ncab


def processTree(grid,xtree,ytree):
    textos_col = ytree.getHeader('col')
    textos_row = xtree.getHeader('row')
    line = 0
    col  = 0
    chart = dict()
    for item in xtree.traverse(mode=1,output=1):
        chart[item.key] = SimpleChart()
        datos,cabeceras = simplify(item.getPayload(),textos_col)
        if len(datos) == 0:
            continue
        chart[item.key].loadData('tarta',cabeceras,datos,xtree.name+'>'+item.getFullDesc()[-1],ytree.name,'sum(votes_presential)')  
        grid.addWidget(chart[item.key],line,0)
        chart[item.key].draw()
        line +=1
   
    
def experimental():
    from util.jsonmgr import load_cubo
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['datos light'])
    #for ind,guia in enumerate(cubo.lista_guias):
        #print(ind,guia['name'])

    ind=2
    pprint(cubo.definition)
    vista=Vista(cubo,5,1,'sum','votes_presential',totalizado=True)
    model = TreeModel(vista)
    return model
    #k=vista.toTree2D()
    #return(vista.row_hdr_idx,vista.col_hdr_idx)

class ApplicationWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")
        #self.showMaximized()
        #self.main_widget = QWidget(self)
        
        #defwidget = QWidget()
        #self.grid = QGridLayout()
        #defwidget.setLayout(self.grid)
        #xtree,ytree = experimental()
        self.tree = QTreeView()
        self.tree.clicked.connect(self.drawChart)
        self.modelo = experimental()
        
        self.modelo.datos.format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)
        self.textos_col = self.modelo.datos.col_hdr_idx.getHeader('col')
        self.textos_row = self.modelo.datos.row_hdr_idx.getHeader('row')
        
        self.tree.setModel(self.modelo)
        self.tree.setSizePolicy(QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Expanding))
        for k in range(self.modelo.datos.col_hdr_idx.count()):  
            self.tree.hideColumn(k+1)
            
        self.chart = SimpleChart()
        self.chart.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        self.chartType = 'multibar'
        if self.modelo.datos.totalizado:
            self.processChartItem(tipo=self.chartType)
        mainWidget = QWidget()
        lay = QGridLayout()
        mainWidget.setLayout(lay)
        
        lay.addWidget(self.tree,0,0,1,1)
        lay.addWidget(self.chart,0,1,1,4)

        self.setCentralWidget(mainWidget)
        
        
    def drawChart(self,index):
        self.processChartItem(index,tipo=self.chartType)

    def processChartItem(self,index=None,tipo='bar'):
        if index:
            item = self.modelo.item(index)
        else:
            item = self.modelo.item('//')
            
        #textos_col = ytree.getHeader('col')
        #textos_row = xtree.getHeader('row')
        #line = 0
        #col  = 0
        titulo = self.modelo.datos.row_hdr_idx.name+'> '+item.getFullDesc()[-1] +  '\n' + \
            '{}({})'.format(self.modelo.datos.agregado,self.modelo.datos.campo) 
        x_text = self.modelo.datos.col_hdr_idx.name
        y_text = ''
        
        if tipo == 'multibar' and item.depth() > 1:
            mdatos = list()
            k = 0
            limite = item.depth()
            kitem = item
            while k < limite:
                mdatos.insert(0,kitem.getPayload())
                kitem = kitem.parent()
                k += 1
            datos,cabeceras = msimplify(mdatos,self.textos_col)
        else:
            datos,cabeceras = simplify(item.getPayload(),self.textos_col)

        if len(datos) == 0:
            self.chart.axes.cla()
        else:
            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,item.getFullDesc())  
        self.chart.draw()
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.show()
    app.exec_()
    exit()
    numero = -232145.1234567890123
    #print(fmtNumber(numero))
    #print(fmtNumber(numero,{'decimalmarker':','}))
    #experimental(aw)
