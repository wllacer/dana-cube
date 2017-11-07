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

  
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

#def traverse(root,base=None):
    #if base is not None:
       #yield base
       #queue = base.listChildren() 
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = queue[0].listChildren() 
        #if expansion is None:
            #del queue[0]
        #else:
            #queue = expansion  + queue[1:]             
    

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
#from util.tree import *

#from datalayer.access_layer import *
#from datalayer.query_constructor import *

#from util.numeros import stats

#from datalayer.datemgr import getDateIndex,getDateEntry
#from pprint import *

#from core import Cubo

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *
#from cubemgmt.cubeCRUD import insertInList
#from dictmgmt.tableInfo import FQName2array,TableInfo

#from dialogs import propertySheetDlg

#import cubebrowse as cb

#import time

from wizardmgmt.guihelper import *

from widgets import *    
from util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

class WzConnect(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzConnect,self).__init__(parent)
        
        self.setTitle("Definicion conexión")
        self.setSubTitle(""" Defina los parámetros de conexion con la base de datos """)

        self.cache = cache
        self.cube = cube
        nombre = None
        data = None
        self.midict = None
        self.context = [
                #['Nombre',QLineEdit,{'setReadOnly':True} if nombre is not None else None,None,],
                ## driver
                ["Driver ",QComboBox,None,DRIVERS,],
                ["DataBase Name",QLineEdit,None,None,],
                #["Schema",QComboBox,None,None],
                ["Schema",QLineEdit,None,None],
                ["Host",QLineEdit,None,None,],
                ["User",QLineEdit,None,None,],
                ["Password",QLineEdit,{'setEchoMode':QLineEdit.Password},None,],
                ["Port",QLineEdit,None,None,],
                ["Debug",QCheckBox,None,None,]
            ]
        self.sheet=WPropertySheet(self.context,data)
        self.sheet.cellWidget(0,0).currentIndexChanged[int].connect(self.driverChanged)
        self.sheet.cellWidget(1,0).textChanged.connect(self.dbChanged)
        self.msgLine = QLabel('')
        self.msgLine.setWordWrap(True)

        meatLayout = QVBoxLayout()
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
        
        self.setLayout(meatLayout)

    def initializePage(self):
        if 'connect' in self.wizard().diccionario:
            self.midict = self.wizard().diccionario['connect']
        else:
            self.midict = self.wizard().diccionario
        for k,clave in enumerate(('driver','dbname','schema','dbhost','dbuser','dbpass','port','debug')):
            if clave == 'schema':
                self.sheet.set(2,0,self.cache['schema'])
                #self.sheet.cellWidget(2,0).clear()
                #confName = self.cache['confName']
                #conn = self.cube.dataDict.getConnByName(confName)
                #esquemas = [ item.text() for item in conn.listChildren() ]
                #self.context[2][3] = esquemas
                #self.sheet.cellWidget(2,0).addItems(esquemas)
                #try:
                    #self.sheet.set(2,0,self.context[2][3].index(self.cache['schema']))
                #except ValueError:
                    #esquemas.append(self.cache['schema'])
                    #self.sheet.cellWidget(2,0).addItem(self.cache['esquema'])
                    #self.sheet.set(2,0,esquemas.rowCount() -1)
                    #self.sheet.cellWidget(2,0).setStyleSheet("background-color:yellow;")
                #continue
            elif self.context[k][1] == QComboBox:
                self.sheet.set(k,0,self.context[k][3].index(self.midict.get(clave)))
            else:
                self.sheet.set(k,0,self.midict.get(clave))
        
    def validatePage(self):
        values = self.sheet.values()
        for k,clave in enumerate(('driver','dbname','schema','dbhost','dbuser','dbpass','port','debug')):
            if self.context[k][1] == QComboBox:
                try:
                    self.midict[clave] = self.context[k][3][values[k]]
                except IndexError:
                    self.midict[clave] = self.sheet.cellWidget(k,0).getCurrentText()
            else:
                self.midict[clave] = values[k]
        return True
    
    def driverChanged(self,idx):
        if DRIVERS[idx] == 'sqlite':
            self.sheet.set(2,0,None)
            for k in range(2,6):
                self.sheet.hideRow(k)
        else: #de momento no alterno nada
            for k in range(2,6):
                self.sheet.showRow(k)

    def dbChanged(self,idx):
        pass
class WzDateFilter(QWizardPage):
    """
    codigo robado absolutamente de dialogs.dateFilterDialog()
    FIXME como reutilizar ambos  
    """
    
    def __init__(self,parent=None,cache=None):
        super(WzDateFilter,self).__init__(parent)
        baseTable = cache['tabla_ref']
        self.baseFieldList = getFieldsFromTable(baseTable)
        self.fieldList = [ item['basename'] for item in self.baseFieldList if item['format'] in ('fecha','fechahora') ]
        self.fieldListCore = [ item['name'] for item in self.baseFieldList if item['format'] in ('fecha','fechahora') ]
        
            
        numrows = len(self.fieldList) 

        self.cache = cache
        
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

        nombresBase =[ item['basename'] for item in self.baseFieldList ]
        nombres     =[ item['name'] for item in self.baseFieldList ]
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
            if item['basename'] == fieldName:
                formato = item['format']
                break
        if formato not in ('fecha','fechahora'):
            formato = 'fecha'
        return formato
    
   
class WzFieldList(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzFieldList,self).__init__(parent)
        fieldList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in fieldList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass
    def validatePage(self):
        return True
   
class WzGuideList(QWizardPage):
    def __init__(self,parent=None):
        super(WzGuideList,self).__init__(parent)
        guideList = ['uno','dos','tres']
        context = [ [argumento,QCheckBox,None] for argumento in guideList]
        data = [ None for k in range(len(context))]

        self.sheet=WPropertySheet(context,data)

        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        pass
    def validatePage(self):
        return True
def toCodeDescList(origin,codeId,descId,withBlank=False):
    code = [ item[codeId] for item in origin ]
    desc = [ item[descId] for item in origin ]
    if withBlank:
        code.insert(0,'')
        desc.insert(0,'')
    return code,desc

def catAddLines(wP,numLines):
    count = wP.catSheet.rowCount()
    for k in range(numLines):
        wP.catSheet.insertRow(count+k)
        wP.catSheet.addRow(count+k)
    wP.catSheet.setCurrentCell(count,0)

def categoriesForm(wP):
    Formatos = [ item[1] for item in ENUM_FORMAT ]

    catResultFormatLabel = QLabel("Formato del &Resultado:")
    wP.catResultFormatCombo = QComboBox()
    wP.catResultFormatCombo.addItems(Formatos)
    wP.catResultFormatCombo.setCurrentIndex(0)
    catResultFormatLabel.setBuddy(wP.catResultFormatCombo)

    catValueFormatLabel = QLabel("Formato de los &Valores:")
    wP.catValueFormatCombo = QComboBox()
    wP.catValueFormatCombo.addItems(Formatos)
    catValueFormatLabel.setBuddy(wP.catValueFormatCombo)
    
    #OJO notar que su posicion es posterior, pero lo necesito para cargar valor
    wP.catResultDefaultLabel = QLabel("Resultado por &Defecto:")
    wP.catResultDefaultLine = QLineEdit()
    wP.catResultDefaultLabel.setBuddy(wP.catResultDefaultLine)

    wP.catContext=[]
    wP.catContext.append(('categoria','condicion','valores'))
    wP.catContext.append((QLineEdit,None,None))
    wP.catContext.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
    wP.catContext.append((QLineEdit,None,None))
    wP.catNumRows=5
    wP.catData = None
    wP.catSheet = WDataSheet(wP.catContext,wP.catNumRows)
    #wP.catSheet.fill(wP.catData)
    wP.simpleContext=(
        ('categoria',QLineEdit,None,None),
        ('condicion',QComboBox,None,tuple(LOGICAL_OPERATOR)),
        ('valores',QLineEdit,None,None),
        )
    wP.catSimpleSheet = WPropertySheet(wP.simpleContext,wP.catData)
    wP.catSimpleSheet.hide()


    meatLayout = QGridLayout()
    meatLayout.addWidget(catValueFormatLabel,0,0)
    meatLayout.addWidget(wP.catValueFormatCombo,0,1)
    meatLayout.addWidget(catResultFormatLabel,1,0)
    meatLayout.addWidget(wP.catResultFormatCombo,1,1)
    meatLayout.addWidget(wP.catSheet, 2, 0, 1, 2)
    meatLayout.addWidget(wP.catSimpleSheet, 2, 0, 1, 3)
    meatLayout.addWidget(wP.catResultDefaultLabel,8,0)
    meatLayout.addWidget(wP.catResultDefaultLine,8,1)    
    
    return meatLayout

def categoriesFormLoad(wP,dataContext):
    obj = wP.wizard().obj
    if obj.type() == 'prod':
        if dataContext.get('fmt'):
            wP.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(dataContext['fmt']))
        if dataContext.get('enum_fmt'): #es el formato del campo origen
            wP.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(dataContext['enum_fmt']))

    elif obj.type() == 'categories':
        if obj.text() == obj.type() :  #las categorias al completo
            pai = wP.wizard().obj.parent()
        else:
            pai = wP.wizard().obj.parent().parent()  
            wP.catSheet.hide()
            if dataContext.get('default'):
                pass
            else:
                wP.catSimpleSheet.show()
                wP.catResultDefaultLabel.hide()
                wP.catResultDefaultLine.hide()
                
        fmtObj = pai.getChildrenByName('fmt')
        if not fmtObj:
            fmt = 'txt'
        else:
            fmt = fmtObj.getColumnData(1)
        enum_fmtObj = pai.getChildrenByName('enum_fmt')
        if not enum_fmtObj:
            enum_fmt = 'txt'
        else:
            enum_fmt = enum_fmtObj.getColumnData(1)
            
        wP.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(fmt))
        wP.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(enum_fmt))
        wP.catResultFormatCombo.setEnabled(False)
        wP.catValueFormatCombo.setEnabled(False)

    wP.catData = [] #'categoria','condicion','valores'  || 'result','condition','values'
    if dataContext.get('categories'): #usa sheet
        lista = dataContext['categories']
        for entry in lista:
            if entry.get('default'):
                wP.catResultDefaultLine.setText(entry['default'])
                continue
            tmp = [ None for i in range(3) ]
            tmp[0] = entry['result']
            tmp[1] = LOGICAL_OPERATOR.index(entry['condition'])
            tmp[2] = norm2String(entry['values'])
            wP.catData.append(tmp)
        
        if len(wP.catData) > wP.catNumRows:
            diff = len(wP.catData) - wP.catNumRows
            catAddLines(wP,diff)
    
        wP.catSheet.fill(wP.catData)

    else:
        entry = dataContext
        if entry.get('default'):
            wP.catResultDefaultLine.setText(entry['default'])
        else:
            for k,clave in enumerate(('result','condition','values')):
                if wP.simpleContext[k][1] == QComboBox:
                    wP.catSimpleSheet.set(k,0,wP.simpleContext[k][3].index(dataContext.get(clave,'in')))
                wP.catSimpleSheet.set(k,0,norm2String(dataContext.get(clave)))
    
    #if dataContext.get('categories'):
        #wP.wizard().setOptions(QWizard.HaveCustomButton1)
        #wP.setButtonText(QWizard.CustomButton1,'Mas entradas')
        #wP.wizard().customButtonClicked.connect(addCatEntry)
        
def categoriesFormValidate(wP,dataContext):
        resultado = wP.catSheet.values()
        obj = wP.wizard().obj
        if obj.type() in ('prod','guides'): # cuando la llamada es indirecta
            formato = ENUM_FORMAT[wP.catResultFormatCombo.currentIndex()][0]
            enumFmt = ENUM_FORMAT[wP.catValueFormatCombo.currentIndex()][0]
            
            if dataContext.get('fmt') or formato != 'txt':
                dataContext['fmt'] = formato
            if dataContext.get('enum_fmt') or formato != enumFmt:
                dataContext['enum_fmt'] = enumFmt
            if dataContext.get('categories'):      
                dataContext['categories'].clear()
            else:
                dataContext['categories'] = []
            resultado = wP.catSheet.values()
            for entry in resultado:
                if entry[0] == '' or entry[2] == '':
                    continue
                dataContext['categories'].append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
            
            if wP.catResultDefaultLine.text() != '':
                dataContext['categories'].insert(0,{'default':wP.catResultDefaultLine.text()})

        elif obj.type() == 'categories':
            if obj.text() == obj.type():  #las categorias al completo
                lista_categ = wP.wizard().diccionario
                lista_categ.clear()
                for entry in resultado:
                    if entry[0] == '':
                        continue
                    lista_categ.append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
                
                if wP.catResultDefaultLine.text() != '':
                    lista_categ.insert(0,{'default':wP.catResultDefaultLine.text()})

            else:
                # FIXME no procesa bien el default
                dataContext.clear()
                if wP.catResultDefaultLine.text() != '':
                    dataContext = {'default':wP.catResultDefaultLine.text()}
                    return True
                values = wP.catSimpleSheet.values()
                for k,clave in enumerate(('result','condition','values')):
                    if wP.catContext[k][1] == QComboBox:
                        try:
                            dataContext[clave] = wP.catContext[k][3][values[k]]
                        except IndexError:
                            dataContext[clave] = wP.catSheet.cellWidget(k,0).getCurrentText()
                    else:
                        dataContext[clave] = values[k]
                        print(dataContext,wP.wizard().diccionario)


        return True

def rowEditorForm(wP):
    #FIXME no admite mandatory
    wP.editArea = QPlainTextEdit()
    meatLayout = QGridLayout()
    meatLayout.addWidget(wP.editArea,0,0,1,0)
    return meatLayout

def rowEditorFormLoad(wP,dataContext):
    if wP.wizard().obj.type() not in TYPE_EDIT :
        caseStmt = dataContext.get('case_sql')
    else:
        caseStmt = dataContext
        
    if isinstance(caseStmt,(list,tuple)):
        wP.editArea.setPlainText('\n'.join(caseStmt))
    else:    
        wP.editArea.setPlainText(caseStmt)
    pass

def rowEditorFormValidate(wP,dataContext):
    texto = wP.editArea.document().toPlainText()
    if isinstance(dataContext,dict):
        area = dataContext.get('case_sql')
    else:
        area = dataContext
        
    if texto and texto.strip() != '':
        area.clear()
        area += texto.split('\n')
    elif area is not None: #dataContext is not None: 
        area.clear()
        
    return True

def defTimeItemComboBox(wP,k):
    # para que coja valores distintos de k en cada ejecucion !!???
    wP.formFechaLabel[k] = QLabel("Formato del {}er nivel:".format(k))
    wP.formFechaCombo[k] = QComboBox()
    if k == 0:
        wP.formFechaCombo[k].addItems(wP.fmtFecha[k:])
    else:
        wP.formFechaCombo[k].addItems(['',] + wP.fmtFecha[k:])
    wP.formFechaCombo[k].setCurrentIndex(0)
    wP.formFechaLabel[k].setBuddy(wP.formFechaCombo[k])
    wP.formFechaCombo[k].currentIndexChanged.connect(lambda:timeSeleccion(wP,k))

def timeSeleccion(wP,idx):
    #TODO sería mas interesante pasar tambien el valor, pero sigo sin acertar
    if idx < 0:
        return 
    # que hemos cambiado ?
    valor = wP.formFechaCombo[idx].currentText()
    if valor == '':
        if idx != 0:
            posActual = wP.fmtFecha.index(wP.formFechaCombo[idx -1].currentText())+1
        else:
            posActual = 0
    else:
        posActual = wP.fmtFecha.index(valor)
    
    for k in range(idx +1,wP.maxTImeLevel):
        j = k - idx
        #if posActual >= (wP.formFechaCombo[idx].count() -1):
        if len(wP.fmtFecha[posActual + j:]) == 0:
            wP.formFechaLabel[k].hide()
            wP.formFechaCombo[k].hide()
        else:
            wP.formFechaCombo[k].blockSignals(True)  #no veas el loop en el que entra si no
            if not wP.formFechaCombo[k].isVisible():
                wP.formFechaLabel[k].show() #por lo de arriba
                wP.formFechaCombo[k].show()
            wP.formFechaCombo[k].clear()
            wP.formFechaCombo[k].addItems(['',] + wP.fmtFecha[posActual + j :])
            wP.formFechaCombo[k].blockSignals(False)  

def timeForm(wP):
    wP.fmtFecha = [ item[1] for item in FECHADOR ]
    wP.fmtFechaCode = [ item[0] for item in FECHADOR ]
    wP.maxTImeLevel = 4  
    wP.formFechaLabel = [None for k in range(wP.maxTImeLevel)]
    wP.formFechaCombo = [None for k in range(wP.maxTImeLevel)]
    
    for k in range(wP.maxTImeLevel):
        defTimeItemComboBox(wP,k)

    meatLayout = QGridLayout()
    for k in range(wP.maxTImeLevel):
        meatLayout.addWidget(wP.formFechaLabel[k],k,0)
        meatLayout.addWidget(wP.formFechaCombo[k],k,1)
    
    return meatLayout
    
def timeFormLoad(wP,dataContext):
    mascara = ''
    if dataContext.get('mask'):
        mascara = dataContext['mask']
    elif dataContext.get('type'):
        mascara = dataContext['type']
    for k,letra in enumerate(mascara):
        wP.formFechaCombo[k].setCurrentIndex(wP.fmtFechaCode.index(letra))
        timeSeleccion(wP,k)
    wP.iterator = wP.wizard().page(ixWzProdBase).iterations
    if isinstance(wP.wizard().diccionario,(list,tuple)):
        #varias entradas
        dataContext = wP.wizard().diccionario[wP.iterator -1]
    else:
        dataContext = wP.wizard().diccionario
    pass

def timeFormValidate(wP,dataContext):
    mask = ''
    for k in range(wP.maxTImeLevel):
        if wP.formFechaCombo[k].currentText() != '':
            idx = wP.fmtFecha.index(wP.formFechaCombo[k].currentText())
            mask += wP.fmtFechaCode[idx]
        else:
            break
    if mask != '':
        dataContext['mask'] = mask
    if dataContext.get('type'):
        del dataContext['type']
            
    return True

def setBaseFK(wP,entry,fromTable,toTable):
    claves = wP.cache['info'][fromTable].get('FK')
    if not claves:
        return 
    for fkey in claves:
        #FIXME si hay varias solo coge la primera
        if fkey.get('parent table') == toTable:
            base = norm2List(fkey.get('ref field'))
            dest = norm2List(fkey.get('parent field'))
            entry['clause'] = []
            for i in len(base):  #mas vale que coincidan
                entry['clause'].append({'base_elem':base[i],'ref elem':dest[i]})
                break
            
def short2FullName(wP,file):
    if file not in wP.listOfTablesCode:
        try:
            idx = wP.listOfTables.index(file)
            return wP.listOfTablesCode(idx)
        except ValueError:
            return None
    else:
        return file
    pass
    
def prodBaseForm(wP):
    prodNameLabel = QLabel("&Nombre:")
    wP.prodIterator  = QLabel("")
    wP.prodName = QLineEdit()
    prodNameLabel.setBuddy(wP.prodName)
    wP.prodName.setStyleSheet("background-color:khaki;")

    domainTableLabel = QLabel("&Tabla de definición de valores")
    wP.domainTableCombo = QComboBox()
    wP.domainTableCombo.addItems(wP.listOfTables)
    wP.domainTableCombo.setCurrentIndex(0)
    domainTableLabel.setBuddy(wP.domainTableCombo)
    wP.domainTableCombo.currentIndexChanged[int].connect(lambda i,w='domain' : wP.tablaElegida(i,w))

    #
    domainGuideLabel = QLabel("Campo &guia:")
    wP.domainFieldCombo = WMultiCombo()
    #wP.guidFldCombo.addItems(wP.listOfFields)
    wP.domainFieldCombo.setEditable(True)
    domainGuideLabel.setBuddy(wP.domainFieldCombo)
    wP.domainFieldCombo.currentIndexChanged[int].connect(wP.campoElegido)
    wP.domainFieldCombo.setStyleSheet("background-color:khaki;")

    #
    domainDescLabel = QLabel("&Campo &Descriptivo:")
    wP.domainDescCombo = WMultiCombo()
    #wP.guideDescCombo.addItems(wP.listOfFields)
    wP.domainDescCombo.setEditable(True)
    domainDescLabel.setBuddy(wP.domainDescCombo)
    #wP.domainDescCombo.currentIndexChanged[int].connect(wP.campoElegido)

    #TODO algo para poder construir links complejos. Es necesario en la interfaz
    
    guideDataTableLabel = QLabel("&Tabla de datos")
    wP.guideDataTableCombo = QComboBox()
    #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
    #                     Use a null value in combos if mandatory
    wP.guideDataTableCombo.addItems(wP.listOfTables)
    wP.guideDataTableCombo.setCurrentIndex(wP.listOfTablesCode.index(wP.cache['tabla_ref']))
    guideDataTableLabel.setBuddy(wP.guideDataTableCombo)
    wP.guideDataTableCombo.currentIndexChanged[int].connect(lambda i,w='data' : wP.tablaElegida(i,w))

    #
    guideDataGuideLabel = QLabel("Campo &guia:")
    wP.guideDataFieldCombo = WMultiCombo()
    wP.guideDataFieldCombo.load(wP.listOfLinkFieldsCode,wP.listOfLinkFields)
    #wP.guidFldCombo.addItems(wP.listOfFields)
    wP.guideDataFieldCombo.setEditable(True)
    guideDataGuideLabel.setBuddy(wP.guideDataFieldCombo)
    wP.guideDataFieldCombo.currentIndexChanged[int].connect(wP.campoElegido)
    wP.guideDataFieldCombo.setStyleSheet("background-color:khaki;")
    
    wP.linkCTorRB = QRadioButton("Con tablas intermedias")
    wP.linkCTorRB.hide()
    #
    #sp_retain = wP.guideLinkCombo.sizePolicy()
    #sp_retain.setRetainSizeWhenHidden(True)
    #wP.guideLinkCombo.setSizePolicy(sp_retain)
    
    wP.catCtorRB = QRadioButton("Agrupado en Categorias")
    wP.caseCtorRB = QRadioButton("Directamente via código SQL")
    wP.dateCtorRB = QRadioButton("Agrupaciones de fechas")
    
    
    groupBox = QGroupBox("Criterios de agrupacion manuales ")
    groupBoxLayout = QHBoxLayout()
    groupBoxLayout.addWidget(wP.catCtorRB)
    groupBoxLayout.addWidget(wP.caseCtorRB)
    groupBoxLayout.addWidget(wP.dateCtorRB)
    groupBox.setLayout(groupBoxLayout)

    meatLayout = QGridLayout()
    meatLayout.addWidget(wP.prodIterator,0,0)
    meatLayout.addWidget(prodNameLabel,0,1)
    meatLayout.addWidget(wP.prodName,0,2,1,2)
    meatLayout.addWidget(domainTableLabel,1,0)
    meatLayout.addWidget(wP.domainTableCombo,1,1)
    meatLayout.addWidget(domainGuideLabel,1,2)
    meatLayout.addWidget(wP.domainFieldCombo,1,3)
    meatLayout.addWidget(domainDescLabel,2,2)
    meatLayout.addWidget(wP.domainDescCombo,2,3)
    meatLayout.addWidget(guideDataTableLabel,3,0)
    meatLayout.addWidget(wP.guideDataTableCombo,3,1)
    meatLayout.addWidget(guideDataGuideLabel,3,2)
    meatLayout.addWidget(wP.guideDataFieldCombo,3,3)
    meatLayout.addWidget(wP.linkCTorRB,4,3)
    meatLayout.addWidget(groupBox, 5, 0, 1, 4)
    
    return meatLayout

def formatoInterno2Enum(format):
    if format in ('texto',):
        return 'txt'
    elif format in ('fecha','fechahora','hora'):
        return 'date'
    else:
        return 'num'
    
def prodBaseFormLoad(wP,dataContext):
    if isinstance(wP.wizard().diccionario,(list,tuple)):
        #varias entradas
        wP.prodIterator.setText("entrada {}/{}".format(wP.iterations +1,wP.wizard().prodIters))
    else:
        wP.prodIterator.setText("")
    #limipiamos todo

    wP.domainTableCombo.setCurrentIndex(-1)
    wP.domainFieldCombo.setCurrentIndex(-1)
    wP.domainDescCombo.setCurrentIndex(-1)
    wP.guideDataTableCombo.setCurrentIndex(-1)
    wP.guideDataFieldCombo.setCurrentIndex(-1)
    wP.linkCTorRB.setChecked(False)


    #vamos ahora al proceso de add
    #TODO si no esta en la lista
    wP.prodName.setText(dataContext.get('name',str(wP.iterations)))
        
    if dataContext.get('domain'):
        #TODO elementos multiples
        setAddComboElem(dataContext['domain'].get('table'),
                        wP.domainTableCombo,
                        wP.listOfTablesCode,wP.listOfTables)
        #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
        wP.domainFieldCombo.set(norm2String(dataContext['domain'].get('code')))
        wP.domainDescCombo.set(norm2String(dataContext['domain'].get('desc')))
        if dataContext.get('link via'):
            wP.linkCTorRB.setChecked(True)
            wP.linkCTorRB.show()
            #TODO multiples criterios 
            setAddComboElem(dataContext['link via'][-1].get('table'),
                            wP.guideDataTableCombo,
                        wP.listOfTablesCode,wP.listOfTables)
        wP.guideDataFieldCombo.set(norm2String(dataContext.get('elem')))
        wP.guideDataFieldCombo.show()
        wP.guideDataTableCombo.show()
    else:    
        setAddComboElem(wP.cache['tabla_ref'],
                        wP.domainTableCombo,
                        wP.listOfTablesCode,wP.listOfTables)
        #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
        if dataContext.get('elem'):
            wP.domainFieldCombo.set(norm2String(dataContext.get('elem')))
        else:
            wP.domainFieldCombo.setCurrentIndex(0)  #FIXME
        wP.domainDescCombo.setCurrentIndex(0)  #FIXME
        #wP.guideDataFieldCombo.hide()
        #wP.guideDataTableCombo.hide()
        
    clase=dataContext.get('class','o')
    if clase == 'd' or dataContext.get('fmt','txt') == 'date':
        wP.dateCtorRB.setChecked(True)
    
    if dataContext.get('categories'):
        wP.catCtorRB.setChecked(True)
    elif dataContext.get('case_sql'):
        wP.caseCtorRB.setChecked(True)

def prodBaseFormValidate(wP,dataContext):
    #TODO realmente no hacemos ninguna validaciones
    #FIXME hacemos wP.iterations es la entrada en guide y entrada +1 en prod
    if not wP.prodName.text().strip().isnumeric():
        dataContext['name'] = wP.prodName.text()
    #wP.domainTableCombo
    if wP.listOfTablesCode[wP.domainTableCombo.currentIndex()] == wP.cache['tabla_ref']:
        # no requiere dominio
        if dataContext.get('domain'):
            del dataContext['domain']
            dataContext['elem'] = norm2List(wP.domainFieldCombo.get())
    else:
        if dataContext.get('domain') is None:
            dataContext['domain'] = {}
        dataContext['domain']['code'] = norm2List(wP.domainFieldCombo.get())
        dataContext['domain']['desc'] = norm2List(wP.domainDescCombo.get())
        dataContext['domain']['table'] = wP.listOfTablesCode[wP.domainTableCombo.currentIndex()]
        dataContext['elem'] = norm2List(wP.guideDataFieldCombo.get())
        # dataContext['domain']['filter'] 
        pass
    tablaDatos = wP.listOfTablesCode[wP.guideDataTableCombo.currentIndex()]
    #FIXME probablemente no sea necesario. Hay que ver la integracion con el wizard de Link
    if ( wP.guideDataTableCombo.currentIndex() > 0 and tablaDatos != wP.cache['tabla_ref'] ):
        #necesitamos un data link
        if not dataContext.get('link via'):
            dataContext['link via'] = []
            entry = {}
            entry['table'] = tablaDatos
            entry['filter'] = ''
            setBaseFK(wP,entry,wP.cache['tabla_ref'],tablaDatos)
            wP.linkCTorRB.setChecked(True)
            dataContext['link via'].append(entry)
        else:
            ultimaTabla = short2FullName(wP,dataContext['link via'][-1]['table'])
            if tablaDatos == ultimaTabla :
                pass
            else:
                try:
                    pos = [ short2FullName(wP,entry['table']) for entry in dataContext['link via']].index(tablaDatos)
                    del dataContext['link via'][pos +1:]
                except ValueError:
                    entry = {}
                    entry['table'] = tablaDatos
                    entry['filter'] = ''
                    setBaseFK(wP,entry,ultimaTabla,tablaDatos)
                    dataContext['link via'].append(entry)
                    wP.linkCTorRB.setChecked(True)
    #class
    #TODO falta modificar la regla de produccion de acuerdo con ello    
    if wP.dateCtorRB.isChecked():
        dataContext['class'] = 'd'
        dataContext['fmt'] = 'date'
    elif wP.catCtorRB.isChecked() or wP.caseCtorRB.isChecked():
        dataContext['class'] = 'c'    
        
    return True

class WzCategory(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzCategory,self).__init__(parent)
        
        self.setFinalPage(True)
                
        self.setTitle("Definicion por categorias")
        self.setSubTitle(""" Introduzca la agrupación de valores que constityen cada categoria  """)

        meatLayout = categoriesForm(self)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        base = self.wizard().page(ixWzProdBase) 
        if not base:
            self.iterator = -1
        else:
            self.iterator = self.wizard().page(ixWzProdBase).iterations
        
        obj = self.wizard().obj
        if obj.type() == 'prod': # cuando la llamada es indirecta
            if obj.text() == obj.type():
                self.midict = self.wizard().diccionario[self.iterator - 1]
            else:
                self.midict = self.wizard().diccionario
        elif obj.type() == 'categories':
            if obj.text() == obj.type() :  #las categorias al completo
                self.midict = {'categories':self.wizard().diccionario}
            else:
                self.midict = self.wizard().diccionario
    
        categoriesFormLoad(self,self.midict)
        
    def nextId(self):
        return -1
    
    def validatePage(self):        

        if not categoriesFormValidate(self,self.midict):
            return False
        if self.iterator == -1:
            return True
            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False

        return True
    
def addCatEntry(wP,buttonId):
    #FIXME da algunos problemas de presentacion ¿Bug upstream?
    if buttonId == QWizard.CustomButton1:
        catAddLines(self,3)
                        
class WzRowEditor(QWizardPage):
    def __init__(self,parent=None,cache=None):
        #TODO hay que buscar/sustituir nombres de campos
        # o como alternativa presentar como pares when / then
        super(WzRowEditor,self).__init__(parent)
        
        self.setFinalPage(True)

        self.setTitle("Definicion de texto libre")
        self.setSubTitle(""" Introduzca el codigo SQL que desea utilizar para agrupar.
        Recuerde sustituir el nombre del campo guia por $$1 """)
        
        self.setLayout(rowEditorForm(self))
    
    def initializePage(self):
        self.iterator = -1
        if self.wizard().obj.type() not in TYPE_EDIT :
            self.iterator = self.wizard().page(ixWzProdBase).iterations
            if isinstance(self.wizard().diccionario,(list,tuple)):
                #varias entradas
                self.midict = self.wizard().diccionario[self.iterator -1]
            else:
                self.midict = self.wizard().diccionario
        else:
            self.midict = self.wizard().diccionario
            
        rowEditorFormLoad(self,self.midict)
        
    def nextId(self):
        return -1
    def validatePage(self):
        
        if not rowEditorFormValidate(self,self.midict):
            return False
        
        if self.iterator == -1:
            return True
            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False

class WzTime(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzTime,self).__init__(parent)
        
        self.setFinalPage(True)
        
        self.setTitle("Guía tipo fecha")
        self.setSubTitle(""" Introduzca la jerarquía de criteros temporales que desea  """)

        
        self.setLayout(timeForm(self))
    
    def initializePage(self):
        #TODO no inicializa si no esta en la regla de produccion
        base = self.wizard().page(ixWzProdBase) 
        if not base:
            self.iterator = -1
        else:
            self.iterator = self.wizard().page(ixWzProdBase).iterations

        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        
        timeFormLoad(self,self.midict)
    
    def nextId(self):
        return -1

    def validatePage(self):
        if not timeFormValidate(self,self.midict):
            return False

            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True


class WzDomain(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzDomain,self).__init__(parent)

        #self.setFinalPage(True)
        
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        
        self.setTitle("Dominio de definición")
        self.setSubTitle(""" Defina el dominio con el que creará la guía  """)

        targetTableLabel = QLabel("&Tabla origen:")
        self.targetTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.targetTableCombo.addItems(self.listOfTables)
        self.targetTableCombo.setCurrentIndex(0)
        targetTableLabel.setBuddy(self.targetTableCombo)
        self.targetTableCombo.setStyleSheet("background-color:khaki;")
        self.targetTableCombo.currentIndexChanged[int].connect(self.tablaElegida)

        targetFilterLabel = QLabel("&Filtro:")
        self.targetFilterLineEdit = QLineEdit()
        targetFilterLabel.setBuddy(self.targetFilterLineEdit)
        

        targetCodeLabel = QLabel("&Clave de enlace:")
        self.targetCodeList = WMultiCombo()
        targetCodeLabel.setBuddy(self.targetCodeList)
        self.targetCodeList.setStyleSheet("background-color:khaki;")

        targetDescLabel = QLabel("&Textos desciptivos:")
        self.targetDescList = WMultiCombo()
        targetDescLabel.setBuddy(self.targetDescList)


        linkLabel = QLabel("¿Requiere de un enlace externo?")
        self.linkCheck = QCheckBox()
        linkLabel.setBuddy(self.linkCheck)
        self.linkCheck.stateChanged.connect(self.estadoLink)
        
        meatLayout = QGridLayout()
        meatLayout.addWidget(targetTableLabel,0,0)
        meatLayout.addWidget(self.targetTableCombo,0,1)
        meatLayout.addWidget(targetCodeLabel,1,0)
        meatLayout.addWidget(self.targetCodeList,1,1)
        meatLayout.addWidget(targetDescLabel,2,0)
        meatLayout.addWidget(self.targetDescList,2,1)
        meatLayout.addWidget(targetFilterLabel,3,0)
        meatLayout.addWidget(self.targetFilterLineEdit,3,1)
        meatLayout.addWidget(linkLabel,4,0)
        meatLayout.addWidget(self.linkCheck,4,1)
        
        self.setLayout(meatLayout)


        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        #base = self.wizard().page(ixWzProdBase) 
        #if not base:
            #self.iterator = -1
        #else:
            #self.iterator = self.wizard().page(ixWzProdBase).iterations

        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
            
        print('inicializando',self.midict)
        if self.midict.get('domain'):
            domain = self.midict['domain']
        else:
            domain = self.midict
        print('y aqui el dominio',domain)
        if domain.get('table'):
            try:
                idx = self.listOfTablesCode.index(domain['table'])
            except ValueError:
                idx = self.listOfTables.index(domain['table'])
            print(domain['table'],idx)
            self.targetTableCombo.setCurrentIndex(idx)
            
        if domain.get('code'):
            self.targetCodeList.set(norm2String(domain.get('code')))
        if domain.get('desc'):
            self.targetDescList.set(norm2String(domain.get('desc')))
        if domain.get('filter'):
            self.targetFilterLineEdit.setText(domain['filter'])
        if domain.get('grouped by'):
            #TODO TODO
            pass
        if self.midict.get('link via'):
            self.linkCheck.setChecked(True)
            self.setFinalPage(False)
        else:
            self.linkCheck.setChecked(False)
            self.setFinalPage(True)
        pass

    def nextId(self):
        if self.linkCheck.isChecked():
            return ixWzLink
        else:
            return -1

    def validatePage(self):
        # verificar que los campos obligatorios estan rellenos
        if self.targetTableCombo.currentText() == '':
            self.targetTableCombo.setFocus()
            return False
        #TODO aqui deberia verificarse que el numero corresponde al numero de elementos de la regla de prod.
        if len(self.targetCodeList.selectedItems()) == 0:
            self.targetCodeList.setFocus()
            return False
            
        if not self.midict.get('domain'):
            domain = self.midict
        else:
            domain = self.midict['domain']
        
        tabidx =self.targetTableCombo.currentIndex()
        domain['table'] = self.listOfTablesCode[tabidx]
        
        domain['code'] = norm2List(self.targetCodeList.get())
        
        domain['desc'] = norm2List(self.targetDescList.get())
         
        domain['filter'] = self.targetFilterLineEdit.text()
         
        #if self.isFinalPage() and (self.iterator != -1 or self.iterator < self.wizard().prodIters):
            #self.wizard().setStartId(ixWzProdBase);
            #self.wizard().restart()        
            #return False
        return True

    def estadoLink(self,idx):
        if self.linkCheck.isChecked():
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)
            
    def tablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTablesCode[idx]
        self.listOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.listOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.targetCodeList.load(self.listOfFieldsCode,self.listOfFields)
        self.targetDescList.load(self.listOfFieldsCode,self.listOfFields)

class WzLink(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzLink,self).__init__(parent)
        self.setFinalPage(True)        
        self.cube = cube
        self.cache = cache

        self.setTitle("Definición del enlace entre tablas")
        self.setSubTitle(""" Introduzca la definición del enlace entre la tabla base y la guía  """)

        self.tipo = None
        
        tableArray = getAvailableTables(self.cube,self.cache)
        self.baseTable = None
        self.targetTable = None
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []

        numrows=5
        
        #self.joinListArray = WDataSheet(self.context,numrows)
        self.joinListArray = QTableWidget(numrows,2)
        self.joinListArray.setHorizontalHeaderLabels(('Tabla Origen ','Tabla Destino'))
        self.joinListArray.resizeColumnsToContents()
        #
        self.joinListArray.setContextMenuPolicy(Qt.CustomContextMenu)
        self.joinListArray.customContextMenuRequested.connect(self.openContextMenu)

        # ahora para el detalle

        self.baseLabel = QLabel('Desde ')
        self.baseTableCombo = QComboBox()
        self.baseTableCombo.addItems(self.listOfTables)
        self.baseTableCombo.setCurrentIndex(0)
        self.baseTableCombo.currentIndexChanged[int].connect(lambda i,w='source':self.tableChanged(i,w))
                                                             
        self.destLabel = QLabel('Hacia ')
        self.destTableCombo = QComboBox()
        self.destTableCombo.addItems(self.listOfTables)
        self.destTableCombo.setCurrentIndex(0)
        self.destTableCombo.currentIndexChanged[int].connect(lambda i,w='dest':self.tableChanged(i,w))
        
        self.clauseContext=[]
        
        self.clauseContext.append(['campo tabla base','condicion','campo tabla destino'])
        self.clauseContext.append([QComboBox,None,['',]+list(self.listOfFields)])
        self.clauseContext.append([QComboBox,None,tuple(LOGICAL_OPERATOR)])
        self.clauseContext.append([QComboBox,None,None])
        
        numrows=3
        
        self.joinClauseArray = WDataSheet(self.clauseContext,numrows)
        self.joinClauseArray.resizeColumnsToContents()
        
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        self.joinClauseArray.resizeColumnToContents(0)
        self.joinListArray.currentCellChanged[int,int,int,int].connect(self.currentCellChanged)

        self.joinFilterLabel = QLabel("&Filtro:")
        self.joinFilterLineEdit = QLineEdit()
        self.joinFilterLabel.setBuddy(self.joinFilterLineEdit)
            
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.joinListArray,0,0,7,2)
        meatLayout.addWidget(self.baseLabel,0,3)
        meatLayout.addWidget(self.baseTableCombo,0,4)
        meatLayout.addWidget(self.destLabel,1,3)
        meatLayout.addWidget(self.destTableCombo,1,4)
        meatLayout.addWidget(self.joinClauseArray,2,3,3,4)
        meatLayout.addWidget(self.joinFilterLabel,6,3)
        meatLayout.addWidget(self.joinFilterLineEdit,6,3)

        #fullLayout = QHBoxLayout()
        #fullLayout.addWidget(self.joinListArray)
        #fullLayout.addLayout(meatLayout)
        
        self.setLayout(meatLayout)
        #self.setLayout(fullLayout)


        self.joinListArray.hide()

    def initializePage(self):
        obj = self.wizard().obj
        self.iterator = -1
        if obj.type() == 'prod':
            self.tipo = 'LinkList'
            base = self.wizard().page(ixWzProdBase) 
            if not base:
                self.iterator = 0
            else:
                self.iterator = base.iterations
            self.iterator +1
            if obj.text() == obj.type():
                self.midict = self.wizard().diccionario[self.iterator -1].get('link via',[])
            else:
                self.midict = self.wizard().diccionario.get('link via',[])
            self.initializePageLinkList()
            
        elif obj.type() == 'link via':
            if obj.text() == obj.type():
                self.tipo = 'LinkList'
                self.midict = self.wizard().diccionario 
                self.initializePageLinkList()
            else:
                # aqui viene el proceso de una sola entrada. De momento lo dejo
                self.tipo = 'LinkEntry'
                self.midict = self.wizard().diccionario 
                self.initializePageLinkEntry()
            
        if len(self.midict) == 0:
            # no hay elementos. No deberia ocurrir (si es nueva creacion debe hacerse uno con los datos del prod)
            pass
        
        if self.tipo == 'LinkList':
            self.joinListArray.show()
            self.joinListArray.cellChanged[int,int].connect(self.checkList)
        #elif self.tipo == 'LinkEntry':
            #self.baseLabel.show()
            #self.baseTableCombo.show()
            #self.destLabel.show()
            #self.destTableCombo.show()
            #self.joinClauseArray.show()
            #self.joinFilterLabel.show()
            #self.joinFilterLineEdit.show()


    def nextId(self):
        return -1

    def validatePage(self):
        if self.tipo == 'LinkList':
            return self.validatePageLinkList()
        elif self.tipo == 'LinkEntry':
            return self.validatePageLinkEntry(self.midict)
    
      
    def initializePageLinkEntry(self):
        obj = self.wizard().obj
        pos = obj.getPos()
        auxobj = obj.getPrevious()
        if auxobj is not None:
            origTable = auxobj.getChildrenByName('table').getColumnData(1)
        else:
            origTable = self.cache['tabla_ref']
        destTable = self.midict.get('table')
        self.loadPageLinkEntry(origTable,destTable,self.midict)
        self.baseTableCombo.setEnabled(False)
        self.destTableCombo.setEnabled(False)
        
    def loadPageLinkEntry(self,origTable,destTable,entry_data):    
        #self.baseTableCombo.show()
        baseField = [ item.get('base_elem') for item in entry_data.get('clause',[]) ]
        relField = [ item.get('rel_elem') for item in entry_data.get('clause',[]) ]
        
       
        pos = setAddComboElem(origTable,self.baseTableCombo,self.listOfTablesCode,self.listOfTables)
        self.tablaElegida(pos,'source')
        pos = setAddComboElem(destTable,self.destTableCombo,self.listOfTablesCode,self.listOfTables)
        self.tablaElegida(pos,'dest')
        #self.baseTableCombo.setEnabled(False)
        #self.destTableCombo.setEnabled(False)
 
        #self.joinClauseArray.resizeColumnsToContents()
            
        if entry_data.get('clause'):
            while len(entry_data.get('clause',[])) > self.joinClauseArray.rowCount():
                self.joinClauseArray.addRow(self.joinClauseArray.rowCount())   
            for i,clausula in enumerate(entry_data.get('clause')):
                setAddComboElem(clausula.get('condition','='),
                                self.joinClauseArray.cellWidget(i,1),
                                LOGICAL_OPERATOR,LOGICAL_OPERATOR)
                setAddComboElem(clausula.get('base_elem',''),
                                self.joinClauseArray.cellWidget(i,0),
                                self.sourceFieldsBase,self.sourceFields,1)

                setAddComboElem(clausula.get('rel_elem',''),
                                self.joinClauseArray.cellWidget(i,2),
                                self.targetFieldsBase,self.targetFields,1)
        
        

        self.joinFilterLineEdit.setText(entry_data.get('filter',''))
    

    def validatePageLinkEntry(self,entry_data):
        resultado = self.joinClauseArray.values()
        # ser pestiño pero primero tengo que eliminar los huecos
        resultado = self.joinClauseArray.values()
        lastNonEmpty = len(resultado) -1
        for k in range(len(resultado) -1,-1,-1):
            if resultado[k][0] > 0:
                lastNonEmpty = k
                break
        try:
            pos = [ linea[0] for linea in resultado[0:lastNonEmpty +1]].index(0)
            self.joinClauseArray.removeRow(pos)
            return False
        except ValueError:
            pass

        for row,entrada in enumerate(resultado):
            if entrada[0] <= 0 and entrada[2] <= 0:
                continue #linea vacia
            elif entrada[0] > 0 and entrada[2] <= 0:
                self.joinClauseArray.cellWidget(row,2).setFocus()
                return False #uno no especificado
            
        entry_data['table'] = self.listOfTablesCode[self.destTableCombo.currentIndex()]
        entry_data['filter'] = self.joinFilterLineEdit.text()
        if entry_data.get('clause'):
            entry_data['clause'].clear()
        else:
            entry_data['clause'] = []
        for linea in resultado:
            if linea[0] <= 0:
                continue  #deberia ser break, pero por si acaso no funciona lo de arriba
            entry = {}
            entry['base_elem'] = self.sourceFieldsBase[linea[0] -1]
            entry['rel_elem'] = self.targetFieldsBase[linea[2] -1]
            if linea[1] != 3:
                entry['condition'] = LOGICAL_OPERATOR[linea[1]]
            entry_data['clause'].append(entry)
            
        if self.tipo == 'LinkList':
            self.checkList(0,0)
        return True
    
    def validatePageLinkList(self):
        #TODO eliminar lineas en blanco
        # ser pestiño pero primero tengo que eliminar los huecos
        
        # valido la ultima linea procesada
        row = self.joinListArray.currentRow()
        if not self.validatePageLinkEntry(self.midict[row]):
            return False
        
    
        if self.iterator == -1:
           return True
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

        return True

        
    def setBaseFK(self,fromTableIdx,toTableIdx):
        fromTable = self.listOfTablesCode[fromTableIdx]
        toTable = self.listOfTablesCode[toTableIdx]
        claves = self.cache['info'][fromTable].get('FK')
        if not claves:
            return 
        #FIXME solo tengo sitio para una primaria
        for fkey in claves:
            #FIXME si hay varias solo coge la primera
            if fkey.get('parent table') == toTable:
                setAddComboElem(fkey.get('ref field'),
                                self.joinClauseArray.cellWidget(0,0),
                                ['',]+[ entry['name'] for entry in getFieldsFromTable(fromTable)],
                                ['',]+[ entry['basename'] for entry in getFieldsFromTable(fromTable)])
                setAddComboElem(fkey.get('parent field'),
                                self.joinClauseArray.cellWidget(0,2),
                                ['',]+[ entry['name'] for entry in getFieldsFromTable(toTable)],
                                ['',]+[ entry['basename'] for entry in getFieldsFromTable(toTable)])
        for row in range(1,self.joinClauseArray.rowCount()):
            self.joinClauseArray.set(row,0,None)
            self.joinClauseArray.set(row,2,None)
                
    def initializePageLinkList(self):
        for i in range(self.joinListArray.rowCount()):
            if ( i != 0 and i >= len(self.midict) ):
                break
            if i == 0:
                sourceItem = QTableWidgetItem(self.cache['tabla_ref'])
            else:
                sourceItem = QTableWidgetItem(self.midict[i -1]['table'])
            sourceItem.setFlags(Qt.ItemIsEnabled)
            targetItem = QTableWidgetItem(self.midict[i]['table'])
            targetItem.setFlags(Qt.ItemIsEnabled)
            self.joinListArray.setItem(i,0,sourceItem)
            self.joinListArray.setItem(i,1,targetItem)

    def currentCellChanged ( self, currentRow, currentColumn, previousRow, previousColumn): 
        if currentRow == previousRow:
            return 
        try:
            datos = self.joinListArray.item(currentRow,0).data(0)
        except AttributeError:
            return
 
        #if self.validatePageLinkEntry(self.midict[previousRow]):
        if self.dumpDetailSheet(previousRow):
            self.initializeDetailSheet(currentRow)
        else:
            self.joinListArray.scrollToItem(self.joinListArray.item(previousRow,previousColumn))

    def initializeDetailSheet(self,row):
        origTable = self.joinListArray.item(row,0).data(0)
        destTable = self.joinListArray.item(row,1).data(0)
        if row == 0:
            self.baseTableCombo.setEnabled(False)
        else:    
            self.baseTableCombo.setEnabled(True)
        self.loadPageLinkEntry(origTable,destTable,self.midict[row])


    def dumpDetailSheet(self,row):
        if row != -1:
            pass
            return self.validatePageLinkEntry(self.midict[row]  )
        else:
            return True

    def tableChanged(self,idx,status):
        if status == 'source':
            origTable = idx
            destTable = self.destTableCombo.currentIndex()
        elif status == 'dest':
            origTable = self.baseTableCombo.currentIndex()
            destTable = idx
        self.tablaElegida(idx,status)
        #FIXME al iniciarse que pasa con los datos que vienen (nada en teoría)
        self.setBaseFK(origTable,destTable)
        #
        if self.tipo == 'LinkList':
            row = self.joinListArray.currentRow()
            if status == 'source':
                self.joinListArray.item(row,0).setData(0,self.listOfTablesCode[idx])
            elif status == 'dest':
                self.joinListArray.item(row,1).setData(0,self.listOfTablesCode[idx])
                if row < len(self.midict) -1:
                    self.joinListArray.item(row +1,0).setData(0,self.listOfTablesCode[idx])
        
    def tablaElegida(self,idx,status):
        if idx == -1:
            return
        tabname = self.listOfTablesCode[idx]
        print('Current Index Changed',status,tabname)
        if status == 'source':
            self.sourceFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            self.sourceFieldsBase= [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            column = 1
            self.clauseContext[column][2] = ['',] + list(self.sourceFields)
            self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
        elif status == 'dest':
        
            self.targetFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            self.targetFieldsBase= [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
            column = 3
            self.clauseContext[column][2] = ['',] + list(self.targetFields)
            self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
 
    
    def openContextMenu(self,position):
        """
        """
        row = self.joinListArray.currentRow()
        menuActions = []
        menu = QMenu()
        menuActions.append(menu.addAction("Append",lambda item=row:self.execAction(item,"append")))
        if row != len(self.midict) -1:
            menuActions.append(menu.addAction("Insert After",lambda item=row:self.execAction(item,"after")))
        if row != 0:
            menuActions.append(menu.addAction("Insert Before",lambda item=row:self.execAction(item,"before")))
        menu.addSeparator()
        menuActions.append(menu.addAction("Delete",lambda item=row:self.execAction(item,"delete")))
        action = menu.exec_(self.joinListArray.viewport().mapToGlobal(position))
    
    def execAction(self,row,action):
        if row >= len(self.midict):
            return
        if action == 'delete':
            del self.midict[row]
            curPos = row -1 if row != 0 else 0
            #FIXME la 0
        elif action == 'append':
            entry = {'table':self.midict[-1]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.append(entry)
            curPos = len(self.midict) -1
            self.destTableCombo.setFocus()
        elif action == 'after':
            entry = {'table':self.midict[row]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.insert(row + 1,entry)
            curPos = row +1
            self.destTableCombo.setFocus()
        elif action == 'before':
            entry = {'table':self.midict[row -1]['table'],'filter':'','clause':[]}  #peligrosillo
            self.midict.insert(row,entry)
            curPos = row +1
            self.destTableCombo.setFocus()
            
        self.joinListArray.blockSignals(True)
        self.joinListArray.clear()
        self.initializePageLinkList()
        self.joinListArray.blockSignals(False)
        self.joinListArray.setCurrentCell(curPos,0)
 
    def checkList(self,row,colum):
        for row,entry in enumerate(self.midict):
            destList = self.joinListArray.item(row,1).data(0)
            baseList = self.joinListArray.item(row,0).data(0)
            dest = entry.get('table')
            correcta = True
            if row == 0:
                base = self.cache['tabla_ref']
            else:
                base = self.midict[row -1]['table']
                if not dest or dest == base : #no es un error pero debe dar warning
                    correcta = False
            if destList != dest or baseList != base:
                correcta = False
            if correcta:
                if len(entry.get('clause',[])) == 0:
                    correcta = False
            
            if correcta:
                baseFields = [ item['name'] for item in getFieldsFromTable(base)]  #solo FQN si no puede haber diplicidades
                destFields = [ item['name'] for item in getFieldsFromTable(dest)]  #solo FQN si no puede haber
                
                for clausula in entry.get('clause'):
                    if clausula['base_elem'] not in baseFields:
                        correcta = False
                        break
                    if clausula['rel_elem'] not in destFields:
                        correcta = False
                        break
            
            if not correcta:
                self.joinListArray.item(row,0).setBackground(Qt.yellow)
                self.joinListArray.item(row,1).setBackground(Qt.yellow)
            else:
                self.joinListArray.item(row,0).setBackground(Qt.white)
                self.joinListArray.item(row,1).setBackground(Qt.white)

class WzGuideBase(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzGuideBase,self).__init__(parent)

        self.cube = cube
        self.cache = cache

        tableArray = getAvailableTables(self.cube,self.cache)
        self.baseFieldList = []
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        self.listOfFieldsCode = []
        self.listOfLinkFields = [ item[1] for item in getFieldsFromTable(self.cache['tabla_ref'],self.cache,self.cube) ]
        self.listOfLinkFieldsCode = [ item[0] for item in getFieldsFromTable(self.cache['tabla_ref'],self.cache,self.cube) ]



        self.setTitle("Definición de la guía")
        self.setSubTitle(""" Introduzca la localización donde estan los valores por los que vamos a agrupar """)
        
        nombre = QLabel("&Nombre:")
        self.nombreLE = QLineEdit()
        nombre.setBuddy(self.nombreLE)
        
        clase = QLabel("&Clase")
        self.claseCB = QComboBox()
        self.claseCB.addItems([ elem[1] for elem in GUIDE_CLASS])
        self.claseCB.setCurrentIndex(0)
        clase.setBuddy(self.claseCB)

        self.prodTB = QTableWidget(5,1)
        self.prodTB.horizontalHeader().setStretchLastSection(True)  
        self.prodTB.setContextMenuPolicy(Qt.CustomContextMenu)
        self.prodTB.customContextMenuRequested.connect(self.openContextMenu)

        detailLayout = prodBaseForm(self)
        
        self.catCtorRB.clicked.connect(self.setDetail)
        self.caseCtorRB.clicked.connect(self.setDetail)
        self.dateCtorRB.clicked.connect(self.setDetail)
        self.linkCTorRB.clicked.connect(self.setDetail)
        self.prodTB.currentCellChanged[int,int,int,int].connect(self.currentCellChanged)

        self.rowEditor = QWidget()
        self.rowEditor.setLayout(rowEditorForm(self))
        self.timeEditor = QWidget()
        self.timeEditor.setLayout(timeForm(self))
        self.categoryEditor = QWidget()
        self.categoryEditor.setLayout(categoriesForm(self))
        
                    
        self.Stack = QStackedWidget (self)
        self.Stack.addWidget(self.categoryEditor)
        self.Stack.addWidget (self.rowEditor)
        self.Stack.addWidget(self.timeEditor)

        
        #self.Stack.addWidget (self.stack2)
        #self.Stack.addWidget (self.stack3)

        meatLayout = QGridLayout()
        meatLayout.addWidget(nombre,0,0)
        meatLayout.addWidget(self.nombreLE,0,1,1,2)
        meatLayout.addWidget(clase,0,3)
        meatLayout.addWidget(self.claseCB,0,4)
        
        meatLayout.addWidget(self.prodTB,2,0,5,1)
        meatLayout.addLayout(detailLayout,2,1,5,4)
        meatLayout.addWidget(self.Stack,2,5,5,2)

        self.setLayout(meatLayout)
       
        self.Stack.hide()
    

    def initializePage(self):
        self.iterations = 1
        pprint(self.wizard().diccionario)
        if self.wizard().obj.type() == 'guides':
            self.midict = self.wizard().diccionario
            
            self.nombreLE.setText(self.midict.get('name',''))
            
            clase = self.midict.get('class','o')
            self.claseCB.setCurrentIndex([ elem[0] for elem in GUIDE_CLASS].index(clase))
            if clase == 'c':
                if self.midict.get('prod',[])[-1].get('categories'):
                    self.catCtorRB.setChecked(True)
                elif self.midict.get('prod',[])[-1].get('case_sql'):
                    self.caseCtorRB.setChecked(True)
                else:
                    self.catCtorRB.setChecked(True)
            elif clase == 'd':
                self.dateCtorRB.setChecked(True)
            self.setDetail()         

            if self.midict.get('prod'):
                for k,entrada in enumerate(self.midict['prod']):
                    self.prodTB.setItem(k,0,QTableWidgetItem(entrada.get('name',str(k))))
            else:
                self.midict['prod']=[{},]
            idx = 0
            self.loadSingleEntry(idx)
                    
        elif self.wizard().obj.type() == 'prod':
            self.nombreLE.hide()
            self.claseCB.hide()
            
    def loadSingleEntry(self,idx):
        self.iterations = idx
        entrada = self.midict['prod'][idx]
        prodBaseFormLoad(self,entrada)
        self.setDetail()
        if self.catCtorRB.isChecked():
            categoriesFormLoad(self,entrada)
        elif self.caseCtorRB.isChecked():
            rowEditorFormLoad(self,entrada)
        elif self.dateCtorRB.isChecked():
            timeFormLoad(self,entrada)
        
        
    def validatePage(self):
        idx = self.iterations
        if not self.dumpSingleEntry(idx):
            return False
        else:
            return True
 
    def dumpSingleEntry(self,idx):
        self.iterations = idx
        entrada = self.midict['prod'][idx]
        if not prodBaseFormValidate(self,entrada):
            return False
        if self.catCtorRB.isChecked():
            if not categoriesFormValidate(self,entrada):
                return False
        elif self.caseCtorRB.isChecked():
            if  not rowEditorFormValidate(self,entrada):
                return False
        elif self.dateCtorRB.isChecked():
            if not timeFormValidate(self,entrada):
                return False
            
        return True
    
    def setFinal(self):
        if self.linkCTorRB :
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)    
        
         
    def nextId(self):
        print('invocamos nextId')
        nextPage = -1
        if self.linkCTorRB.isChecked(): #and nextPage == -1:
            nextPage =  ixWzLink

        return nextPage

    def setDetail(self):
        self.Stack.hide()
        if  self.catCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(0)
        elif self.caseCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(1)            
        elif self.dateCtorRB.isChecked():
            self.Stack.show()
            self.Stack.setCurrentIndex(2)
            
    def tablaElegida(self,idx,tipo):
        tabname = self.listOfTablesCode[idx]
        self.baseFieldList = getFieldsFromTable(tabname,self.cache,self.cube,'fmt')
        self.listOfFields = [ item[1] for item in self.baseFieldList ]
        self.listOfFieldsCode = [ item[0] for item in self.baseFieldList ]
        if tipo == 'domain':
            self.domainFieldCombo.load(self.listOfFieldsCode,self.listOfFields)
            self.domainDescCombo.load(self.listOfFieldsCode,self.listOfFields)
        elif tipo == 'data':
            self.guideDataFieldCombo.load(self.listOfFieldsCode,self.listOfFields)
            if tabname != self.cache['tabla_ref']:
                self.linkCTorRB.show()
    #def formatoInterno2Enum(self,format):
        #if format in ('texto',):
            #return 'txt'
        #elif format in ('fecha','fechahora','hora'):
            #return 'date'
        #else:
            #return 'num'
        
    def campoElegido(self,ind):
        try:
            self.fmtEnum = formatoInterno2Enum(self.baseFieldList[ind][2])
        except IndexError:
            self.fmtEnum = 'txt'
        if self.fmtEnum in ('date',):
            self.dateCtorRB.setChecked(True)
 
    def openContextMenu(self,position):
        """
        """
        row = self.prodTB.currentRow()
        menuActions = []
        menu = QMenu()
        menuActions.append(menu.addAction("Append",lambda item=row:self.execAction(item,"append")))
        if row != len(self.midict.get('prod',[])) -1:
            menuActions.append(menu.addAction("Insert After",lambda item=row:self.execAction(item,"after")))
        if row != 0:
            menuActions.append(menu.addAction("Insert Before",lambda item=row:self.execAction(item,"before")))
        menu.addSeparator()
        menuActions.append(menu.addAction("Delete",lambda item=row:self.execAction(item,"delete")))
        action = menu.exec_(self.prodTB.viewport().mapToGlobal(position))
    
    def execAction(self,row,action):

        if row >= len(self.midict['prod']):
            return
        
        if action == 'delete':
            del self.midict['prod'][row]
        else:
            if not self.dumpSingleEntry(row):
                return False
            if action == 'append':
                self.midict['prod'].append({})
                pos = self.prodTB.rowCount()
            elif action == 'after':
                pos = row +1
                self.midict['prod'].insert(pos,{})
            elif action == 'before':
                pos = row
                self.midict['prod'].insert(pos,{})
            
        self.prodTB.blockSignals(True)
        self.prodTB.clear()
        for k,entrada in enumerate(self.midict['prod']):
            self.prodTB.setItem(k,0,QTableWidgetItem(entrada.get('name',str(k))))
        self.prodTB.blockSignals(False)
        self.prodTB.setCurrentCell(row,0)
 
    def currentCellChanged ( self, currentRow, currentColumn, previousRow, previousColumn): 
        if currentRow == previousRow:
            return 
        try:
            datos = self.prodTB.item(currentRow,0).data(0)
        except AttributeError:
            return
 
        #if self.validatePageLinkEntry(self.midict[previousRow]):
        if previousRow != -1:
            estadoAnterior =  self.dumpSingleEntry(previousRow)
        else:
            estadoAnterior = True
            
        if estadoAnterior:       
            self.loadSingleEntry(currentRow)
        else:
            self.prodTB.scrollToItem(self.prodTB.item(previousRow,previousColumn))
            
class WzProdBase(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzProdBase,self).__init__(parent)
        self.setFinalPage(True)
        
        self.iterations = 0
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        self.baseFieldList = []
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        self.listOfFieldsCode = []
        self.listOfLinkFields = [ item[1] for item in getFieldsFromTable(self.cache['tabla_ref'],self.cache,self.cube) ]
        self.listOfLinkFieldsCode = [ item[0] for item in getFieldsFromTable(self.cache['tabla_ref'],self.cache,self.cube) ]

        
        self.setTitle("Definición del dominio de la guía")
        self.setSubTitle(""" Introduzca la localización donde estan los valores por los que vamos a agrupar """)


        self.setLayout(prodBaseForm(self))

        self.catCtorRB.clicked.connect(self.setFinal)
        self.caseCtorRB.clicked.connect(self.setFinal)
        self.dateCtorRB.clicked.connect(self.setFinal)
        self.linkCTorRB.clicked.connect(self.setFinal)


    
    def initializePage(self):
        #TODO no inicializa si no esta en la regla de produccion

        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterations]
            self.prodIterator.setText("entrada {}/{}".format(self.iterations +1,self.wizard().prodIters))
        else:
            self.midict = self.wizard().diccionario

        prodBaseFormLoad(self,self.midict)
        self.iterations += 1
     
    def setFinal(self):
        if ( self.catCtorRB  or
            self.caseCtorRB or
            self.dateCtorRB or
            self.linkCTorRB ):
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)    
        
         
    def nextId(self):
        print('invocamos nextId')
        nextPage = -1
        
        if self.catCtorRB.isChecked():
            nextPage =  ixWzCategory
        elif self.caseCtorRB.isChecked():
            nextPage =  ixWzRowEditor
        elif self.dateCtorRB.isChecked():
            nextPage =  ixWzTime
            
        if self.linkCTorRB.isChecked(): #and nextPage == -1:
            nextPage =  ixWzLink

        return nextPage


    def validatePage(self):

        if not prodBaseFormValidate(self,self.midict):
            return False
        
        if self.isFinalPage() and self.iterations < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

    def tablaElegida(self,idx,tipo):
        tabname = self.listOfTablesCode[idx]
        self.baseFieldList = getFieldsFromTable(tabname,self.cache,self.cube,'fmt')
        self.listOfFields = [ item[1] for item in self.baseFieldList ]
        self.listOfFieldsCode = [ item[0] for item in self.baseFieldList ]
        if tipo == 'domain':
            self.domainFieldCombo.load(self.listOfFieldsCode,self.listOfFields)
            self.domainDescCombo.load(self.listOfFieldsCode,self.listOfFields)
        elif tipo == 'data':
            self.guideDataFieldCombo.load(self.listOfFieldsCode,self.listOfFields)
            if tabname != self.cache['tabla_ref']:
                self.linkCTorRB.show()



        
    def campoElegido(self,ind):
        try:
            self.fmtEnum = formatoInterno2Enum(self.baseFieldList[ind][2])
        except IndexError:
            self.fmtEnum = 'txt'
        if self.fmtEnum in ('date',):
            self.dateCtorRB.setChecked(True)
            
class CubeWizard(QWizard):
    def __init__(self,obj,cubeMgr,action,cube_root,cube_ref,cache_data):
        super(CubeWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.obj = obj
        self.cubeMgr = cubeMgr
        self.action = action
        self.cube_root = cube_root
        self.cache_data = cache_data

        tipo = obj.type()
        if action == 'add date filter':
            self.diccionario = {'date filter':[]}
        else:
            self.diccionario = tree2dict(obj,isDictionaryEntry)
            
        if not tipo or tipo == 'connect':
            self.setPage(ixWzConnect, WzConnect(cube=cubeMgr,cache=cache_data))
        # TODO no son estrictamente complejos pero la interfaz es mejor como complejos
        #if not tipo:
            #self.setPage(ixWzFieldList, WzFieldList(cache=cache_data))
            #self.setPage(ixWzBaseFilter, WzBaseFilter(cache=cache_data))
        if not tipo or tipo == 'date filter' or action == 'add date filter':
            self.setPage(ixWzDateFilter, WzDateFilter(cache=cache_data))
        
        if tipo in ('categories'):
            self.setPage(ixWzCategory, WzCategory(cache=cache_data))
        elif tipo in ('domain'):
            self.setPage(ixWzDomain, WzDomain(cube=cubeMgr,cache=cache_data))
        elif tipo in ('case_sql'):
            self.setPage(ixWzRowEditor, WzRowEditor(cache=cache_data))
        elif tipo in ('link via'):
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
        elif tipo in ('guides'):
            if action in ('add','insert after','insert before'):
                    self.diccionario = {}
            self.setPage(ixWzGuideBase, WzGuideBase(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            
        elif tipo in ('prod'): #== 'prod':
            self.prodIters = 1
            if obj.text() != 'prod':  # entrada individual
                if action in ('add','insert after','insert before'):
                    self.diccionario = {}
                elif action == 'edit':
                    pass
            else:  # la entrada de produccion
                if action in ('add','insert first'):
                    self.diccionario = {}
                elif action == 'edit':
                    self.prodIters = len(self.diccionario)
                    pass
            print(self.prodIters,self.diccionario)
            
            
            self.setPage(ixWzProdBase, WzProdBase(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzCategory, WzCategory(cache=cache_data))
            self.setPage(ixWzRowEditor, WzRowEditor(cache=cache_data))
            self.setPage(ixWzTime, WzTime(cache=cache_data))
            #self.setPage(ixWzDomain, WzDomain(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            
        texto_pantalla = obj.text() if obj.text() != tipo else obj.parent().text()
        self.setWindowTitle('Mantenimiento de ' + tipo + ' ' + texto_pantalla.split('.')[-1])
        self.show()
