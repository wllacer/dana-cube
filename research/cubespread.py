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
import datetime
import argparse
from decimal import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QDialog, QMenu, QGridLayout, \
     QTableWidget,QTableWidgetItem,QTableView
     #QDialog, QTreeView, QSplitter, QMenu, 
     # QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     # QAbstractItemView, 
from PyQt5.QtPrintSupport import *

from base.core import Cubo,Vista
from base.tree import GuideItem,GuideItemModel,_getHeadColumn
from support.util.decorators import stopwatch,model_change_control
from support.util.numeros import is_number
from support.gui.dialogs import propertySheetDlg

ASUCAR = [ ['Uno',1,2,3,4 ],
           ['Dos',5,6,7,8 ],
           ['Tres',8,7,6,5 ],
           ['Cuatro',4,3,2,1 ],
        ]
#def traverse(root,base=None):
    #if base is not None:
       #yield base
       #queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        #if expansion is None:
            #del queue[0]
        #else:
            #queue = expansion  + queue[1:]  
            
class guidePreview(QDialog):
    def __init__(self,cubo,pos=0,parent=None):
        super(guidePreview,self).__init__(parent)
        #self.tree = previewTree(cubo,guia=pos)
        self.tree = previewTableView(cubo,guia=pos)
        meatLayout=QGridLayout()
        meatLayout.addWidget(self.tree)
        self.setLayout(meatLayout)

class previewTableWidget(QTableWidget):
    @stopwatch
    def __init__(self,cubo,guia=0,parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.cubo = Cubo(cubo)
        self.vista = Vista(self.cubo,'geo','partidos importantes','sum',self.cubo.lista_campos[0],totalizado=False)
        #self.vista = Vista(self.cubo,'partidos importantes','geo','sum',self.cubo.lista_campos[0],totalizado=False)
        self.setupModel() 
        #self.setupPureModel()
        #self.setupMixedModel()
        #self.setupHModelFail()
        #self.setupHModel()
        
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.setupView()
        print('inicializacion completa')
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setupModel(self):
        self.vista.toNewTree2D()
        array = self.vista.toExpandedArray(self.vista)
        self.setRowCount(len(array))
        self.setColumnCount(len(array[0]))
        for i,linea in enumerate(array):
            for j,columna in enumerate(linea):
                item = QTableWidgetItem(str(columna) if columna else '')
                if i < self.vista.dim_col:
                    item.setBackground(QColor(Qt.lightGray))
                if j < self.vista.dim_row:
                    item.setBackground(QColor(Qt.lightGray))
                if is_number(columna):
                    item.setTextAlignment(Qt.AlignRight)
                else:
                    item.setTextAlignment(Qt.AlignLeft)
                self.setItem(i,j,item)
        #self.baseModel  = self.vista.row_hdr_idx
        #self.hiddenRoot = self.baseModel.invisibleRootItem()       
        #parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        #self.baseModel.setStats(True)

class previewTableView(QTableView):
    @stopwatch
    def __init__(self,cubo,guia=0,parent=None):
        super().__init__(parent)
        self.parentWindow = parent
        self.cubo = Cubo(cubo)
        self.vista = Vista(self.cubo,'geo','partidos importantes','sum',self.cubo.lista_campos[0],totalizado=False)
        self.setupModel() 
        
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.setupView()
        print('inicializacion completa')
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def setupModel(self):
        self.vista.toNewTree()
        array = self.toExpandedArray(self.vista)
        self.sheet = SsModel(self.vista) #QStandardItemModel()
        for i,linea in enumerate(array):
            nlinea = []
            for j,columna in enumerate(linea):
                item = QStandardItem()
                item.setData(str(columna) if columna else '',Qt.UserRole +1)
                if i < self.vista.dim_col:
                    item.setBackground(QColor(Qt.lightGray))
                if j < self.vista.dim_row:
                    item.setBackground(QColor(Qt.lightGray))
                #if is_number(columna):
                    #item.setTextAlignment(Qt.AlignRight)
                #else:
                    #item.setTextAlignment(Qt.AlignLeft)
                nlinea.append(item)
            self.sheet.appendRow(nlinea)
        self.setModel(self.sheet)
        #self.setModel(self.vista.row_hdr_idx)

    def setupView(self):
        #self.view.setModel(self.baseModel)
        #self.colHdr = self.vista.col_hdr_idx.asHdr()
        self.model().setHorizontalHeaderLabels([colNr2Key(x) for x in range(self.model().columnCount())])
        #self.vista.row_hdr_idx.setHorizontalHeaderLabels(
            #[self.vista.row_hdr_idx.name,]+ 
            #self.colHdr )

        self.view.setAlternatingRowColors(True)
        #self.view.sortByColumn(0, Qt.AscendingOrder)
        #self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.view.customContextMenuRequested.connect(self.openContextMenu)

        #self.view.header().setContextMenuPolicy(Qt.CustomContextMenu)
        #self.view.header().customContextMenuRequested.connect(self.openHeaderContextMenu)

    #def hola(self,topLeft,bottomRight):
        #print('bingo',topLeft,bottomRight)
      

        
    def openContextMenu(self,position):
        pass
        #menu = QMenu()
        #self.ctxMenu = []
        #self.ctxMenu.append(menu.addAction("Insertar fila",lambda :self.execAction("add",position)))
        #self.ctxMenu.append(menu.addAction("Imprimir",lambda :self.execAction("print",position)))
        #action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def execAction(self,function,position):
        pass
        #print(position)
        #indexes = self.selectedIndexes()
        #if len(indexes) > 0:
            #index = indexes[0]
        #if function == 'add':
            #self.insertElement(index,tipo='row')
            ##self.drawGraph('row',index)
        #if function == 'print':
            #self.print_()
            
    def Tree2Array(self,vista):
        """
        TODO document
        """
        maxCols = vista.col_hdr_idx.numRecords()
        result= []
        for row in vista.row_hdr_idx.traverse():
            pl = row.getPayload()
            if len(pl) < maxCols:
                pl += [ None for k in range(maxCols - len(pl)) ]
            result.append(pl)
        return result

    def toExpandedArray(self,vista,*parms,**kwparms):
        """
        Converts the view results in a list of texts
        * Input parameters. All optional
            * __colHdr__  boolean if a column header will be shown. default True
            * __rowHdr__  boolean if a row header will be shown. default True
            * __numFmt__ python format for the numeric values. Default = '      {:9,d}'
            * __colFmt__    python format for the column headers. Default = ' {:>n.ns}', where n is the len of the numeric format minus 1
            * __rowFmt__   python format for the row headers. Default = ' {:20.20s}', 
            * __hMarker__  hierachical marker (for row header). Default _'  '_
            * __rowHdrContent__ one of ('key','value'). Default 'value'
            * __colHdrContent__ one of ('key','value'). Default 'value'
            * __rowFilter__ a filtering function
            * __colFilter__ a filtering function
        Returns
            a tuple of formatted lines
        """
        #colHdr=kwparms.get('colHdr',True)
        #rowHdr=kwparms.get('rowHdr',True)
        #numFormat = kwparms.get('numFmt','      {:9,d}')
        #numLen = len(numFormat.format(0))
        #colFormat = kwparms.get('colFmt',' {{:>{0}.{0}s}}'.format(numLen -1))
        #rowFormat = kwparms.get('rowFmt','{:20.20s}')
        #rowLen = len(rowFormat.format(''))
        hMarker = kwparms.get('hMarker','  ')
        #rowContent = kwparms.get('rowHdrContent','value')
        #colContent = kwparms.get('colHdrContent','value')
        #rowFilter = kwparms.get('rowFilter',lambda x:True)
        #colFilter = kwparms.get('colFilter',lambda x:True)
        
 
        tmpArray = self.Tree2Array(vista)
        
        rowHeaders = vista.row_hdr_idx.asHdr(format='array',delimiter=hMarker,sparse=True)
        for entry in rowHeaders:
            if len(entry) < vista.dim_row:
                entry.extend(['' for k in range(vista.dim_row - len(entry))])
                
        colHeaders = vista.col_hdr_idx.asHdr(format='array',sparse=True)
        
        resultado = []
        for k in range(vista.dim_col):
            resultado.append(['' for k in range(vista.dim_row)] + [elem[k] if k < len(elem) else '' for elem in colHeaders ])
            
        for idx,item in enumerate(tmpArray):
            resultado.append(rowHeaders[idx] + item)
            
        return resultado
                
    def dataChanged(self, *args,**kwargs):
        topLeft = args[0]
        bottomRight = args[1]
        roles = args[2]
        if topLeft == bottomRight:
            ## debo desactivar las señales porque en caso contrario, el limpiado provoca un recursivo
            self.model().blockSignals(True)
            item = self.model().itemFromIndex(topLeft)
            nuevoDato = item.data(Qt.DisplayRole)
            viejoDato = item.data(Qt.UserRole +1)
            item.setData(None,Qt.DisplayRole) # ahora reseto. La aplicacion no espera DR en general
            if nuevoDato != viejoDato:  #ha cambiado
                if nuevoDato == '':  #revierto los cambios
                    pass
                else:
                    item.setData(nuevoDato,Qt.UserRole +1)
                    item.setData(None,Qt.DisplayRole)
            self.model().blockSignals(False)
        super().dataChanged(*args,**kwargs)

    def print_(self):
        printer = QPrinter(QPrinter.ScreenResolution)
        dlg = QPrintPreviewDialog(printer)
        view = PrintView()
        view.setModel(self.model())
        dlg.paintRequested.connect(view.print_)
        dlg.exec_()

def colNr2Key(x):
    if x < 26:
        key=chr(65+x)
    else:
        key=chr(65+int(x/26))+chr(65+x%26)
    return key
    
class PrintView(QTableWidget):
    def __init__(self):
        super(PrintView, self).__init__()
        self.expandToDepth(2)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def print_(self, printer):
        self.resize(printer.width(), printer.height())
        self.render(printer)


    
def main():
    from support.util.jsonmgr import load_cubo
    app = QApplication(sys.argv)
    mis_cubos = load_cubo()
    cubo = mis_cubos['datos light']
    form = guidePreview(cubo)
    form.show()
    if form.exec_():
        pass
        sys.exit()

from base.tree import TOTAL,BRANCH,LEAF,TreeFormat
from support.util.numeros import s2n,fmtNumber

class SsModel(QStandardItemModel):
    def __init__(self,*parms,**kwparms):
        if parms:
            self.vista = parms[0]
            parent = parms[1] if 1 < len(parms) else None
        else:
            self.vista = None
            parent = None
        super().__init__(parent)
        self.datos = TreeFormat()
        self.ss = SpreadSheet(self)
    def traverse(self,base=None):
        """
        Generator to navigate the tree. It only reads the head items of each rows

        * Input parameter
            * __base__ initial item to process. default is .invisibleRootItem, but this element is not yielded
        * returns
            * next item in sequence
        
        __TODO__
        
        It would be nice to put it functionally on par to util.treebasic.TreeModel
        """
        if base is not None:
            yield base
            queue = [ base.child(i) for i in range(0,base.rowCount()) ]
        else:
            root = self.invisibleRootItem()
            queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        while queue :
            yield queue[0]
            expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
            if expansion is None:
                del queue[0]
            else:
                queue = expansion  + queue[1:]            

    def data(self,index,role):
        """
        Reimplementation of QStandardItemModel.data for the needs of danacube. It will be invoked when a view associated with the model is redrawn
        
        * Input parameters
            * __index__ a QIndexModel which identifies the item
            * __role__ which Qt.Role are we handling
            
        * Programming notes
        We define special actions for following cases
            * Qt.BackgroundRole. Color if the conditions in TreeFormat are met 
            * Qt.DisplayRole. Formats the numeric vector
        """
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        retorno = item.data(role)
        displayData = baseData = item.data(Qt.UserRole +1)
        
        if  role not in (Qt.DisplayRole, Qt.UserRole +2) and baseData and isinstance(baseData,str) and baseData[0] == '=':
            displayData = self.data(index,Qt.UserRole + 2)
            
        if role == Qt.TextAlignmentRole:
            if not baseData:
                return retorno
            if is_number(displayData):
                return Qt.AlignRight | Qt.AlignVCenter
            else:
                return Qt.AlignLeft | Qt.AlignVCenter
            
        if role == Qt.BackgroundRole:
            if baseData is None:
                return retorno
            else:
                datos = baseData
                if datos is None or datos == '':
                    return  retorno
                if is_number(displayData):
                    datos = float(displayData)
                    if self.datos.format['rednegatives'] and datos < 0 :
                        retorno = QColor(Qt.red)
                    else:
                        return retorno
                else:
                    return retorno
            return retorno   
         
        elif role == Qt.DisplayRole:
            if not baseData or baseData == '':
                return None
            if isinstance(baseData,str) and len(baseData) > 0 and baseData[0] == '=':
                baseData =  self.ss[baseData]
            if is_number(baseData):
                text, sign = fmtNumber(s2n(baseData),self.datos.format)
                return '{}{}'.format(sign if sign == '-' else '',text)               
            else:
                return baseData
            
        elif role == Qt.UserRole + 2:  #es como el display pero sin formatos numericos            
            if not baseData or baseData == '':
                return None
            if isinstance(baseData,str) and len(baseData) > 0 and baseData[0] == '=':
                baseData =  self.ss[baseData]
                return baseData
            else:
                return baseData
        else:
            return item.data(role)
        
        
import math
class SpreadSheet:
    
    _cells = {}
    tools = {}
    for entry in dir(math):
        if entry[0] == '_':
            continue
        if entry not in tools:
            tools[entry]=getattr(math,entry)

    
    def __init__(self,model):
        self.model = model
        #pprint(SpreadSheet.tools)
        #print(eval('sin(pi/2)',SpreadSheet.tools))

    def __setitem__(self, key, formula):
        #if isinstance(formula, str) and formula[0] == '=':
            #formula = formula[1:]
        #else:
            #formula = (formula,)
        self._cells[key] = formula
    
    def getformula(self, key):
        c = self._cells[key]
        if isinstance(c, str):
            return '=' + c
        return c[0]
    
    def __getitem__(self, key ):
        
        x,y = keyCoord(key)
        if x and y:
            item = self.model.item(y,x)
            c = item.data(Qt.UserRole +1)
            if is_number(c):
                c = s2n(c)
        else:
            item = None
            c = key
        if isinstance(c, str) and c[0] == '=':
            while True:
                try:
                    resultado = eval(c[1:], SpreadSheet.tools,self._cells)
                    self._cells.clear()
                    return resultado
                except NameError as ne:
                    dato = ne.args[0][6:-16]
                    self._cells[dato] = self[dato]
                    
        else:
            return c
        return c

def isKey(key):
    if (key[0].isalpha() and key[1:].isdigit()) or (key[0:1].isalpha() and key[2:].isdigit()):
        return True
    return False

def keyCoord(key):
    if not isKey(key):
        return None,None
    if key[1].isalpha():
        x=(ord(key[0].lower())-97)*26+ord(key[1].lower())-97
        y=int(key[2:])-1
    else:
        x=ord(key[0].lower())-97
        y=int(key[1:])-1
    return x,y

if __name__ == '__main__':
        # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    main()
    #cloneTest()
    #ordered()
