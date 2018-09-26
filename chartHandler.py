#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3

Usos SimpleChart
base/danacube.py:631:        self.chart = SimpleChart()
100:from support.gui.mplwidget import SimpleChart
631:        self.chart = SimpleChart()
632:        self.chartType = None #'barh'
634:        self.tree.clicked.connect(self.drawChart)
637:        split.addWidget(self.chart)
641:        self.drawChart(None)
644:        dialog = GraphDlg(self.chartType, parent=self)
646:            self.chartType = dialog.result
647:        self.drawChart()
654:        self.drawChart()
656:    def drawChart(self,index=None):
657:        if self.chartType:
658:            self.processChartItem(index,tipo=self.chartType)
660:            self.chart.hide()
662:    def processChartItem(self,index=None,tipo='bar',visibleOnly=True):
711:            self.chart.axes.cla()
713:            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,rowid.getFullDesc())  
714:        self.chart.draw()
715:        self.chart.show()
1213:        dialog = GraphDlg(self.parent.tabulatura.currentWidget().chartType, source, self)
1215:            chart = self.parent.tabulatura.currentWidget().chart
1258:                    chart.axes.cla()
1261:                    chart.loadData(dialog.result,etiquetas,datos,titulo,x_text,y_text)  
1262:                chart.draw()
1263:                chart.show()
1265:                chart.hide()
loadData
draw
show
hide

'''

from pprint import pprint
import sys
import datetime
import argparse
from decimal import *
from random import randint

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView,QTabWidget
 
from PyQt5.QtPrintSupport import *
from base.core import Cubo,Vista,printArray
from base.tree import * #GuideItem,GuideItemModel,_getHeadColumn
from support.util.decorators import stopwatch,model_change_control
from support.util.jsonmgr import load_cubo
from support.util.record_functions import norm2List

from support.gui.mplwidget import *
from support.gui.dialogs import GraphDlg
import sys

#class pepe(QDialog):
    #def __init__(self,parent=None):
        #super().__init__(parent)
        #hugo = WComboBox()
        #hugo.addItems(puntuacion)
        #meat = QVBoxLayout()
        #meat.addWidget(hugo)
        #self.setLayout(meat)
        
#def processChartItem(TabMgr,index=None,tipo='bar',visibleOnly=True):
    #if index:
        #if index.isValid():
            #item = TabMgr.tree.model().itemFromIndex(index)
            #rowid = item.getHead()
        #else:
            #return
        
    #elif len(TabMgr.tree.selectedIndexes()) > 0:
        #indice = TabMgr.tree.selectedIndexes()[0]
        #item = TabMgr.tree.model().itemFromIndex(indice)
        #rowid = item.getHead()

    #elif TabMgr.lastItemUsed is not None:
        #item = TabMgr.lastItemUsed
        #rowid = item

    #else:
        #item = TabMgr.tree.model().invisibleRootItem().child(0)
        #rowid = item
    #TabMgr.lastItemUsed = rowid

    #x_text = TabMgr.tree.vista.col_hdr_idx.name
    #y_text = ''
    #titleParms = {}
    #if tipo == 'multibar': 
        #datos,kcabeceras = rowid.simplifyHierarchical() #msimplify(mdatos,self.textos_col)
        #titleParms = {'format':'string', 'delimiter':' > '}
    #else:
        #datos,kcabeceras = rowid.simplify() #item.getPayload(),self.textos_col)
    
    ##suprimo las columnas ocultas
    #if visibleOnly:
        #for k in range(len(kcabeceras)-1,-1,-1):
            #pos = kcabeceras[k]
            #if TabMgr.tree.isColumnHidden(pos +1):
                #del kcabeceras[k]
                #if tipo == 'multibar':
                    #for j in range(len(datos)):
                        #del datos[j][k]
                #else:
                    #del datos[k]
        
    #titulo = TabMgr.tree.vista.row_hdr_idx.name+'> '+rowid.getFullHeadInfo(**titleParms) +  '\n' + \
            #'{}({})'.format(TabMgr.tree.vista.agregado,TabMgr.tree.vista.campo) 
        
    #cabeceras = [ TabMgr.tree.colHdr[k] for k in kcabeceras ] 

    #if len(datos) == 0:
        #TabMgr.chart.axes.cla()
    #else:
        #TabMgr.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,rowid.getFullDesc())  
    #TabMgr.chart.draw()
    #TabMgr.chart.show()
        
#def drawGraph(danaCube,source,id,visibleOnly=True):
    #dialog = GraphDlg(danaCube.parent.tabulatura.currentWidget().chartType, source, danaCube)
    #if dialog.exec_():
        #chart = danaCube.parent.tabulatura.currentWidget().chart
        #if dialog.result:
            #if source == 'row':
                #item = danaCube.model().itemFromIndex(id)
                #titulo = item['value']
                #datos = []
                #etiquetas = []
                #for k,entrada in enumerate(item.getPayload()):
                    #if entrada is None:
                        #continue
                    #elif visibleOnly and danaCube.isColumnHidden(k+1):
                        #continue
                    #else:
                        #datos.append(entrada)
                        #etiquetas.append(danaCube.colHdr[k])
            #elif source == 'col':
                #titulo = danaCube.colHdr[id - 1]
                #datos = []
                #etiquetas = []
                #for entrada in danaCube.model().traverse():
                    #if dialog.hojas and not entrada.isLeaf():
                        #continue
                    #if entrada.gpi(id -1) is None:
                        #continue
                    #if visibleOnly:
                        #entry = entrada
                        #hidden = False
                        #while entry:
                            #row = entry.row()
                            #pai = entry.parent().index() if entry.parent() else QModelIndex()
                            #if danaCube.isRowHidden(row,pai):
                                #hidden = True
                                #break
                            #entry = entry.parent()
                        #if hidden:
                            #continue
                    #datos.append(entrada.gpi(id -1))
                    #etiquetas.append(entrada.getFullHeadInfo())
                    
            
            #x_text = danaCube.model().name
            #y_text = ''
            #if len(datos) == 0:
                #chart.axes.cla()
            #else:
                ##print(dialog.result,etiquetas,datos,titulo,x_text,y_text)
                #chart.loadData(dialog.result,etiquetas,datos,titulo,x_text,y_text)  
            #chart.draw()
            #chart.show()
        #else:
            #chart.hide()

def getGraphTexts(vista,head,xlevel,dir='row'):
    
    if dir == 'row':
        fmodel = vista.row_hdr_idx
        xmodel = vista.col_hdr_idx
        fidx = vista.row_id
        xidx = vista.col_id
        fdim = vista.dim_row
        xdim  = vista.dim_col
    else:
        fmodel = vista.col_hdr_idx
        xmodel = vista.row_hdr_idx
        fidx = vista.col_id
        xidx = vista.row_id
        fdim = vista.dim_col
        xdim  = vista.dim_row
        
    fixedParm = fmodel.name
    if fdim > 1:
        j = head.depth() -1 if (dir == 'row' and vista.totalizado) else head.depth()
        if j == -1:
            pass
        else:
            fixedParm = vista.cubo.lista_guias[fidx]['contexto'][j]['name']
            
    ejeX  = xmodel.name
    if xdim > 1:
        if dir == 'col' and vista.totalizado:
            ejeX = vista.cubo.lista_guias[xidx]['contexto'][xlevel -1]['name']
        else:
            ejeX = vista.cubo.lista_guias[xidx]['contexto'][xlevel]['name']
        
    titulo = '{}:  {} \n por {} '.format(fixedParm,head.getFullHeadInfo(),ejeX)
    
    ejeY = '{}({})'.format(vista.agregado,vista.campo)  #TODO depende de las funciones ejecutadas
    
    return titulo,ejeX,ejeY
                
#def getData():
    #mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['datos locales'])
    #lista = cubo.getGuideNames()
    ##print(lista)
    ##exit()
    #xdesc = 'fecha'
    #ydesc  = 'geo'
    #vista = Vista(cubo,xdesc,ydesc,'sum','votes_presential',totalizado=True,cartesian=False)
    #vista.toTree2D()
    ##printArray(vista)
    #xrecs = vista.row_hdr_idx.numRecords()
    #yrecs = vista.col_hdr_idx.numRecords()
    #dlg = charter()
    ##obtengo una fila al azar
    ##xrow = 0 #randint(0,xrecs -1)
    ##xhead = vista.row_hdr_idx.pos2item(xrow)
    ##resultado = vista.getVector(xhead,dir='row') #,keyfmt='sparse')
    ##print(xhead)
    
    
        
    ##for k in range(len(resultado)):
        ##texto = resultado[k][0] 
        ##valores = [ elem.data(Qt.UserRole +1) for elem in resultado[k][1] ]
        ##titulo,ejeX,ejeY = getGraphTexts(vista,xhead,k,dir='row')
        ##dlg.chart.loadData('bar',texto,valores,titulo,ejeX,ejeY)
        ##dlg.chart.draw()
        ##dlg.show()
        ##if dlg.exec_():
            ##pass
        
    #yrow = randint(0,yrecs -1)
    #yhead = vista.col_hdr_idx.pos2item(yrow)
    #resultado = vista.getVector(yhead,dir='col')
    #print(yhead)
    #for k in range(len(resultado)):
        #if k == 0 and vista.totalizado:
            #continue
        #texto = resultado[k][0] 
        #valores = [ elem.data(Qt.UserRole +1) for elem in resultado[k][1] ]
        #titulo,ejeX,ejeY = getGraphTexts(vista,yhead,k,dir='col')
        #dlg.chart.loadData('bar',texto,valores,titulo,ejeX,ejeY)
        #dlg.chart.draw()
        #dlg.show()
        #if dlg.exec_():
            #pass
        
    ##x_text = vista.col_hdr_idx.name
    ##y_text = ''
    ##titleParms = {'format':'array'}
    ##datos,kcabeceras = head.simplify() #Hierarchical() #msimplify(mdatos,self.textos_col)
    ##print(head,datos,kcabeceras)
    
#Usos SimpleChart
#base/danacube.py:631:        self.chart = SimpleChart()
#100:from support.gui.mplwidget import SimpleChart
#631:        self.chart = SimpleChart()
#632:        self.chartType = None #'barh'
#634:        self.tree.clicked.connect(self.drawChart)
#637:        split.addWidget(self.chart)
#641:        self.drawChart(None)
#644:        dialog = GraphDlg(self.chartType, parent=self)
#646:            self.chartType = dialog.result
#647:        self.drawChart()
#654:        self.drawChart()
#656:    def drawChart(self,index=None):
#657:        if self.chartType:
#658:            self.processChartItem(index,tipo=self.chartType)
#660:            self.chart.hide()
#662:    def processChartItem(self,index=None,tipo='bar',visibleOnly=True):
#711:            self.chart.axes.cla()
#713:            self.chart.loadData(tipo,cabeceras,datos,titulo,x_text,y_text,rowid.getFullDesc())  
#714:        self.chart.draw()
#715:        self.chart.show()
#1213:        dialog = GraphDlg(self.parent.tabulatura.currentWidget().chartType, source, self)
#1215:            chart = self.parent.tabulatura.currentWidget().chart
#1258:                    chart.axes.cla()
#1261:                    chart.loadData(dialog.result,etiquetas,datos,titulo,x_text,y_text)  
#1262:                chart.draw()
#1263:                chart.show()
#1265:                chart.hide()
#loadData
#draw
#show
#hide
#class ChartTab(QTabWidget):
    #def __init__(self,parent=None):
        #super().__init__(parent)
        
    #def loadData(self,vista,head,graphType='bar',dir='row',filter=None):
        ##borro los tabs
        #for k in range(self.count()-1,-1,-1):
            #self.removeTab(k)
        #if graphType is None:
            #self.hide()
        
        #resultado = vista.getVector(head,dir=dir,filter=filter)
        #for k in range(len(resultado)):
            #if k == 0 and dir=='col' and vista.totalizado:
                #continue
            #texto = resultado[k][0] 
            #valores = [ elem.data(Qt.UserRole +1) for elem in resultado[k][1] ]
            #titulo,ejeX,ejeY = getGraphTexts(vista,head,k,dir=dir)
            #self.addTab(SimpleChart(),ejeY)
            #self.setCurrentIndex(self.count() -1)
            #self.currentWidget().loadData(graphType,texto,valores,titulo,ejeX,ejeY)
            #self.currentWidget().draw()        
        #self.setCurrentIndex(0)
    #def draw(self):
        #for k in range(self.count()):
            #self.setCurrentIndex(k)
            #self.currentWidget().draw()
            
class charter(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.chart =ChartTab()
        self.meat = QGridLayout()
        self.meat.addWidget(self.chart,0,0)
        self.setLayout(self.meat)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dlg = charter()
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['datos locales'])
    xdesc = 'partidos importantes'
    ydesc  = 'geo'
    vista = Vista(cubo,xdesc,ydesc,'sum','votes_presential',totalizado=True,cartesian=False)
    vista.toTree2D()
    #printArray(vista)
    xrecs = vista.row_hdr_idx.numRecords()
    xrow = randint(0,xrecs -1)
    xhead = vista.row_hdr_idx.pos2item(xrow)
    dlg.chart.loadData(vista,xhead,dir='row')
    dlg.show()
    if dlg.exec_():
        pass
    sys.exit()
