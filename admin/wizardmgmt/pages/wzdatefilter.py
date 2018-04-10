##!/usr/bin/python
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

  
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox
    
import base.config as config

from support.util.record_functions import *

from admin.cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from base.cubetree import *
from admin.cubemgmt.cubeTypes import *

from admin.wizardmgmt.guihelper import *

from support.gui.widgets import *    
from support.util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

class WzDateFilter(QWizardPage):
    """
    codigo robado absolutamente de dialogs.dateFilterDialog()
    FIXME como reutilizar ambos  
    """
    
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzDateFilter,self).__init__(parent)
        baseTable = cache['tabla_ref']
        self.cache = cache
        self.cube  = cube
        self.baseFieldList = getFieldsFromTable(baseTable,cache_data=self.cache,cube=self.cube,tipo_destino='fmt')
        self.fieldList = [ item[1] for item in self.baseFieldList if item[2] in ('fecha','fechahora') ]
        self.fieldListCore = [ item[0] for item in self.baseFieldList if item[2] in ('fecha','fechahora') ]
        
            
        numrows = len(self.fieldList) 


        
        self.single = False
            
        # cargando parametros de defecto
        self.context = []

        for k in self.fieldList:
            self.context.append(('\t {}'.format(k),
                                  (QComboBox,None,CLASES_INTERVALO),
                                  (QComboBox,None,TIPOS_INTERVALO),
                                  (QSpinBox,{"setRange":(1,366)},None,1),
                                  (QLineEdit,{"setEnabled":False},None),
                                  (QLineEdit,{"setEnabled":False},None),
                                  )
                        )
        rows = len(self.context)
        cols = 5 #max( [len(item) -1 for item in self.context ])  #FIXME
        self.sheet1=WPowerTable(rows,cols)

        for i,linea in enumerate(self.context):
            for j in range(1,len(linea)):
                self.sheet1.addCell(i,j -1,linea[j])
                #self.sheet1.set(i,j -1,self.data[i][j-1])
            self.sheet1.cellWidget(i,0).currentIndexChanged[int].connect(lambda j,idx=i:self.seleccionCriterio(j,idx))
            self.sheet1.cellWidget(i,1).currentIndexChanged[int].connect(lambda j,idx=i:self.seleccionIntervalo(j,idx))
            self.sheet1.cellWidget(i,2).valueChanged[int].connect(lambda j,idx=i:self.seleccionIntervalo(j,idx))
            self.flipFlop(i,self.sheet1.get(i,0))

       #FIXME valor inicial        
        campos = [ k[0] for k in self.context ]
        self.sheet1.setVerticalHeaderLabels(campos)
        self.sheet1.resizeColumnsToContents()
        cabeceras = ('Tipo Intervalo','Periodo intervalo','Numero Intervalos','F. inicio Inter. ','F. final Inter.')
        self.sheet1.setHorizontalHeaderLabels(cabeceras)
        self.sheet1.resizeColumnsToContents()
        #
        InicioLabel1 = QLabel('Filtre el rango temporal que desea')


        meatLayout = QVBoxLayout()
        
        meatLayout.addWidget(InicioLabel1)
        meatLayout.addWidget(self.sheet1)
       
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(800,200))

        self.setWindowTitle("Date Filter editor")
        
    def initializePage(self):
        # TODO tablas sin fecha explicita (en sqlite)
        if len(self.fieldList) == 0:
            self.wizard().back()

        if 'date filter' in self.wizard().diccionario:
            self.midict = self.wizard().diccionario['date filter']
        else:
            self.midict = self.wizard().diccionario
        if isinstance(self.midict,dict):
            self.single = True
            datos = [self.midict,]
        else:
            datos = self.midict
            
        for entrada in datos:
            campo = entrada.get('elem')
            # TODO cuando hay un campo NO fecha
            row = self.name2row(campo)
                    
            self.sheet1.set(row,0,CLASES_INTERVALO.index(entrada.get('date class'))) # date class
            self.sheet1.set(row,1,TIPOS_INTERVALO.index(entrada.get('date range'))) # date range
            self.sheet1.set(row,2,int(entrada.get('date period'))) # date period
            self.sheet1.set(row,3,entrada.get('date start')) # date start11
            self.sheet1.set(row,4,entrada.get('date end')) # date end
            if self.single:
                for k in range(self.sheet1.rowCount()):
                    if k == row:
                        continue
                    for j in range(self.sheet1.columnCount()):
                        self.sheet1.cellWidget(k,j).setEnabled(False)
            
    def name2row(self,campo):
        try:
            row = self.fieldListCore.index(campo)
            return row
        except ValueError:
            pass
        try:
            row = self.fieldList.index(campo)
            return row
        except ValueError:
            pass

        nombresBase =[ item[1] for item in self.baseFieldList ]
        nombres     =[ item[0] for item in self.baseFieldList ]
        idx = None
        try:
            idx = nombresBase.index(campo)
        except ValueError:
            pass
        if not idx:
            idx = nombres.index(campo)
            # aqui dejo cascar el proceso. Es un fallo lo suficiente
        self.context.append(('\t {}'.format(nombres[idx]),
                        (QComboBox,None,CLASES_INTERVALO),
                        (QComboBox,None,TIPOS_INTERVALO),
                        (QSpinBox,{"setRange":(1,366)},None,1),
                        (QLineEdit,{"setEnabled":False},None),
                        (QLineEdit,{"setEnabled":False},None),
                        )
                        )
        self.fieldListCore.append(campo)
        self.fieldList.append(campo)
        row = self.sheet1.rowCount()
        self.sheet1.insertRow(row)
        linea = self.context[-1]
        self.sheet1.setVerticalHeaderItem(row,QTableWidgetItem(nombres[idx]))
        for j in range(1,len(linea)):
            self.sheet1.addCell(row,j -1,linea[j])
        self.sheet1.cellWidget(row,0).currentIndexChanged[int].connect(lambda j,idx=row:self.seleccionCriterio(j,idx))
        self.sheet1.cellWidget(row,1).currentIndexChanged[int].connect(lambda j,idx=row:self.seleccionIntervalo(j,idx))
        self.sheet1.cellWidget(row,2).valueChanged[int].connect(lambda j,idx=row:self.seleccionIntervalo(j,idx))
        self.flipFlop(row,self.sheet1.get(row,0))
        
        return row
        
    def flipFlop(self,line,value):
        # puede ser un poco repetitivo, pero no se si es mas costoso el enable/disable que comprobar cada
        # vez si lo esta. Por lo menos el codigo es menos complejo y todavia no veo una razon para modificarlo
        if value == 0:
            self.sheet1.cellWidget(line,1).setEnabled(False)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        elif value == 1: 
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        else:
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(True)
        # ponemos los valores ejemplo

    def seleccionCriterio(self,value,idx):
        self.flipFlop(idx,value)
        self.seleccionIntervalo(value,idx)
            
    def seleccionIntervalo(self,value,idx):
        if self.sheet1.get(idx,0)  == 0:
            self.sheet1.set(idx,3,None)
            self.sheet1.set(idx,4,None)
        else:
            desde,hasta = dateRange(self.sheet1.get(idx,0),self.sheet1.get(idx,1),periodo=self.sheet1.get(idx,2))
            self.sheet1.set(idx,3,str(desde))
            self.sheet1.set(idx,4,str(hasta))

    def validatePage(self):
        data = self.sheet1.values()
        if self.single:
            campo = self.midict.get('elem')
            # TODO cuando hay un campo NO fecha
            row = self.name2row(campo)
            entrada = data[row]
            self.midict['date class'] = CLASES_INTERVALO[entrada[0]]
            self.midict['date range'] = TIPOS_INTERVALO[entrada[1]]
            self.midict['date period'] = entrada[2]
        else:
            self.midict.clear()
            for row,entrada in enumerate(data):
                if entrada[0] <= 0:
                    continue
                self.midict.append({'elem':self.fieldListCore[row],
                                    'date class':CLASES_INTERVALO[entrada[0]],
                                    'date range':TIPOS_INTERVALO[entrada[1]],
                                    'date period':entrada[2],
                                    'date format':self.getFormat(self.fieldListCore[row])
                                })
        return True
        
    def getFormat(self,fieldName):
        formato = 'fecha'
        for item in self.baseFieldList:
            """
              item 0 full name2
              item 1 basename
              item 2 format
            """  
            #if item['basename'] == fieldName:
                #formato = item['format']
                #break
            if item[1] == fieldName:
                formato = item[2]
                break
        if formato not in ('fecha','fechahora'):
            formato = 'fecha'
        return formato
    
   
