#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012,2016 Werner Llacer. All rights reserved.. Under the terms of the LGPL 2


from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pprint import pprint
from util.record_functions import norm2List
 

class WPowerTable(QTableWidget):
    # TODO mas tipos
    # TODO un defecto razonable

    def __init__(self,rows=0,cols=0,parent=None):
        super(WPowerTable,self).__init__(rows,cols,parent)
        self.horizontalHeader().setStretchLastSection(True)
        #self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum);
        #self.resizeRowsToContents()
        #self.resizeColumnsToContents()
        
    def addCell(self,x,y,colDef,defVal=None):
        item = defVal
        type = colDef[0]
        typeSpec = colDef[1]
        if len(colDef) > 2:
            listVals = colDef[2]
        else:
            listVals = None
        editItem = None
        if type is None or type == QLineEdit:
            editItem = QLineEdit()
            editItem.setText(str(item) if item is not None else '')
        elif type == QCheckBox:
            editItem = QCheckBox()
            if item is None:
                editItem.setChecked(False)
            else:
                editItem.setChecked(item)
        elif type == QSpinBox:
            editItem = QSpinBox()
            if item is None:    
                editItem.setValue(0)
            else:
                editItem.setValue(item)
        elif type == QComboBox:
            editItem = QComboBox()
            if listVals is not None:
                editItem.addItems(listVals)
            if item is None:
                pass
            else:
                if isinstance(item,int):
                    editItem.setCurrentIndex(item)
                else:  #esto es para el caso en que no existe en origen (prefijos, por ejemplo)
                    editItem.addItem(item)
                    editItem.setCurrentIndex(editItem.count() -1)
              
        else:
            print('Noooop',x)
        if typeSpec is not None:
            #TODO ejecuto los metodos dinamicamente. por ahora solo admite parametros en lista  
            #TODO vale como funcion utilitaria
            for func in typeSpec:
                try:
                    shoot = getattr(editItem,func)
                except AttributeError:
                    print(typeSpec,item)
                    exit()
                if isinstance(typeSpec[func],(list,tuple)):
                    parms = typeSpec[func]
                else:
                    parms = (typeSpec[func],)
                shoot(*parms)

        self.setCellWidget(x,y,editItem)

    def values(self):
        valores=[]
        for x in range(self.rowCount()):
            linea=[]
            for y in range(self.columnCount()):
                linea.append(self.get(x,y))
            valores.append(linea)
        return valores

    def set(self,x,y,value):
        if isinstance(self.cellWidget(x,y),QLineEdit):
            self.cellWidget(x,y).setText(value)
        elif isinstance(self.cellWidget(x,y),QCheckBox):
            if value is None:
                self.cellWidget(x,y).setChecked(False)
            else:
                self.cellWidget(x,y).setChecked(value)
        elif isinstance(self.cellWidget(x,y),QSpinBox):
            self.cellWidget(x,y).setValue(value)
        elif isinstance(self.cellWidget(x,y),QComboBox):
            if value is None:
                pass
            elif isinstance(value,int):
                self.cellWidget(x,y).setCurrentIndex(value)
            else:
                self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).findText(value,Qt.MatchExactly))
                #FIXME no se si no debe sustituirse por esta de abajo
                #TODO comprobar matches parciales
                #try:
                    #self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).findText(value))
                #except IndexError :
                    #self.cellWidget(x,y).addItem(value)
                    #self.cellWidget(x,y).setCurrentIndex(self.cellWidget(x,y).count() -1)

        else:
            self.cellWidget(x,y).setText(value)
            print('Noooop',x,y)

        
    def get(self,x,y):
        if isinstance(self.cellWidget(x,y),QLineEdit):
            return self.cellWidget(x,y).text()
        elif isinstance(self.cellWidget(x,y),QCheckBox):
            return self.cellWidget(x,y).isChecked()
        elif isinstance(self.cellWidget(x,y),QSpinBox):
            return self.cellWidget(x,y).value()
        elif isinstance(self.cellWidget(x,y),QComboBox):
            return self.cellWidget(x,y).currentIndex()
        else:
            print('Noooop',x,y)
            return self.cellWidget(x,y).text()
        
   

class WDataSheet(WPowerTable):
    """
        Version del TableWidget para simular hojas de entrada de datos
        se inicializa con el context
           context[0] titulos de las filas
           context[1 -n] columnas
                (??)context[k][0] valores iniciales (si es comun)
                context[k][1] widget a utilizar (defecto QLineEdit)
                context[k][2] parametrizacion del widget (metodo:valor)
                context[k][3] lista adicinal de valores (para QComboBox y similares)
           ...
           m numero de filas a generar
          
    """
    def __init__(self,context,rows,parent=None): 
        
        cols=len(context) -1

        super(WDataSheet, self).__init__(rows,cols,parent)
        # cargando parametros de defecto
        self.context = context
        
        #FIXME es un desastre
        cabeceras = [ item  for item in self.context[0] ]
        for k in range(rows):
            self.addRow(k)

        self.setHorizontalHeaderLabels(cabeceras)
        

        self.resizeRowsToContents()

    def addRow(self,line):
        for y,colDef in enumerate(self.context[1:]):
            self.addCell(line,y,colDef)
            
    def fill(self,data):
        if len(data) == 0:
            return
        rows=min(self.rowCount(),len(data))
        cols=min(self.columnCount(),len(data[0]))
        for x in range(rows):
            for y in range(cols):
                self.set(x,y,data[x][y])
            
    def values(self):
        valores=[]
        for x in range(self.rowCount()):
            linea=[]
            for y in range(self.columnCount()):
                linea.append(self.get(x,y))
            valores.append(linea)
        return valores
     
    def valueCol(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            #if self.sheet.cellWidget(k,0) is None:
                #print('elemento {} vacio'.format(k))
                #continue
            valores.append(self.get(k,col))
        return valores
 
 
class WPropertySheet(WPowerTable):
    """
        Version del TableWidget para simular hojas de propiedades
        se inicializa con el array context
           context[0] titulos de las filas
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] parametrizacion del widget (metodo:valor)
           ...
       FIXME que pasa cuando context != data
       
    """
    def __init__(self,context,data,parent=None): 
        
        rows=len(context)
        cols=1
        super(WPropertySheet, self).__init__(rows,cols,parent)
        # cargando parametros de defecto
        self.context = context
        cabeceras = [ k[0] for k in self.context ]
        for k in range(len(self.context)):
                self.addCell(k,0,context[k][1:],None)
                if data:
                    self.set(k,0,data[k])
        self.setVerticalHeaderLabels(cabeceras)
        #no necesito cabeceras horizontales en este caso
        self.horizontalHeader().hide()


        self.resizeRowsToContents()
        self.horizontalHeader().setStretchLastSection(True)
    def values(self,col=0):
        """
           devuelve los valores actuales para la columna
        """
        valores =[]
        for k in range(self.rowCount()):     
            valores.append(self.get(k,0))
        return valores

        
        
