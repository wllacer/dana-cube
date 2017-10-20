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
from PyQt5.QtGui import QStandardItemModel, QStandardItem
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

class WzConnect(QWizardPage):
    def __init__(self,parent=None):
        super(WzConnect,self).__init__(parent)
        
        self.setTitle("Definicion conexión")
        self.setSubTitle(""" Defina los parámetros de conexion con la base de datos """)

        nombre = None
        data = None
        self.midict = None
        self.context = (
                #('Nombre',QLineEdit,{'setReadOnly':True} if nombre is not None else None,None,),
                ## driver
                ("Driver ",QComboBox,None,DRIVERS,),
                ("DataBase Name",QLineEdit,None,None,),
                ("Host",QLineEdit,None,None,),
                ("User",QLineEdit,None,None,),
                ("Password",QLineEdit,{'setEchoMode':QLineEdit.Password},None,),
                ("Port",QLineEdit,None,None,),
                ("Debug",QCheckBox,None,None,)
            )
        self.sheet=WPropertySheet(self.context,data)
        
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
        for k,clave in enumerate(('driver','dbname','dbhost','dbuser','dbpass','port','debug')):
            if self.context[k][1] == QComboBox:
                self.sheet.set(k,0,self.context[k][3].index(self.midict.get(clave)))
            self.sheet.set(k,0,self.midict.get(clave))
        
    def validatePage(self):
        values = self.sheet.values()
        for k,clave in enumerate(('driver','dbname','dbhost','dbuser','dbpass','port','debug')):
            if self.context[k][1] == QComboBox:
                try:
                    self.midict[clave] = self.context[k][3][values[k]]
                except IndexError:
                    self.midict[clave] = self.sheet.cellWidget(k,0).getCurrentText()
            else:
                self.midict[clave] = values[k]
        return True
    
class WzBaseFilter(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzBaseFilter,self).__init__(parent)
        numrows = 5
        context=[]
        fieldList = ['','Uno','Dos','Tres']
        context.append(('campo','condicion','valores'))
        context.append((QComboBox,None,fieldList))
        context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        context.append((QLineEdit,None,None))

        self.setTitle("Filtro Base")
        self.setSubTitle(""" Introduzca la condicion SQL por el que filtrar la tabla base """)

        self.sheet = WDataSheet(context,numrows)
        self.editArea = QPlainTextEdit()
        #TODO una linea pura de codigo. O mejor alterar los tamaños
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)
        meatLayout.addWidget(self.editArea,5,0,8,0)
        
        self.setLayout(meatLayout)
        
    def initializePage(self):
        pass
    def validatePage(self):
        pass
class WzDateFilter(QWizardPage):
    #TODO falta validaciones cruzadas como en el dialogo
    #TODO falta aceptar un campo no fecha (para sqlite) ya definido
    def __init__(self,parent=None,cache=None):
        super(WzDateFilter,self).__init__(parent)
        baseTable = cache['tabla_ref']
        self.baseFieldList = cache['info'][baseTable]['Fields']
        fieldList = ['',] + [item['basename'] for item in self.baseFieldList if item['format'] in ('fecha','fechahora') ]
        self.fqnfields = ['',] + [ item['name'] for item in self.baseFieldList if item['format'] in ('fecha','fechahora') ]
        numrows = len(fieldList) -1
        context = []
        context.append(('campo','Clase','Rango','Numero','Desde','Hasta'))
        context.append((QComboBox,None,fieldList))
        context.append((QComboBox,None,CLASES_INTERVALO))
        context.append((QComboBox,None,TIPOS_INTERVALO))
        context.append((QSpinBox,{"setRange":(1,366)},None,1))
        context.append((QLineEdit,{"setEnabled":False},None))
        context.append((QLineEdit,{"setEnabled":False},None))

        self.setTitle("Filtro Fechas")
        self.setSubTitle(""" Introduzca los criterios dinámicos de fecha por los que filtrar la tabla base """)

        self.sheet=self.sheet = WDataSheet(context,numrows)

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.sheet,0,0,1,0)
        
        self.setLayout(meatLayout)
        self.midict = None
        
    def getFormat(self,fieldName):
        formato = 'fecha'
        for item in self.baseFieldList:
            if item['basename'] == fieldName:
                formato = item['formato']
                break
        return formato

    def initializePage(self):
        if 'date filter' in self.wizard().diccionario:
            self.midict = self.wizard().diccionario['date filter']
        else:
            self.midict = self.wizard().diccionario
        if len(self.midict) > 0:
            for k,entry in enumerate(self.midict):
                #'elem':entry[0],
                #'date class': CLASES_INTERVALO[entry[1]],
                #'date range': TIPOS_INTERVALO[entry[2]],
                #'date period': entry[3],
                #'date start': None,
                #'date end': None,
                #'date format': formato

                campo = self.fqnfields.index(entry['elem'])
                self.sheet.set(k,0,campo)
                self.sheet.set(k,1,CLASES_INTERVALO.index(entry['date class']))
                self.sheet.set(k,2,TIPOS_INTERVALO.index(entry['date range']))
                self.sheet.set(k,3,int(entry['date period']))
                formato = 'fechahora'
                if not entry.get('date format'):
                    formato = self.getFormat(entry['elem'])
                else:
                    formato = entry['date format']

                if not entry.get('date start'):
                    intervalo = dateRange(self.sheet.get(k,1),self.sheet.get(k,2),periodo=int(entry['date period']),fmt=entry['date format'])
                else:
                    intervalo = tuple([entry['date start'],entry['date end']] )
                self.sheet.set(k,4,str(intervalo[0]))
                self.sheet.set(k,5,str(intervalo[1]))
                    
    def validatePage(self):
        values = self.sheet.values()
        guiaCamposVal = [item[0] for item in values]
        guiaCamposDic = [item['elem'] for item in self.midict]
        self.midict.clear()
        for entrada in values:
            print(entrada)
            if entrada[0] == 0 or entrada[1] == 0:
                continue
            self.midict.append({'elem':self.fqnfields[entrada[0]],
                                'date class':CLASES_INTERVALO[entrada[1]],
                                'date range':TIPOS_INTERVALO[entrada[2]],
                                'date period':entrada[3],
                                'date format':self.getFormat(self.fqnfields[entrada[0]])
                               })
        return True
   
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


class WzProdBaseOld(QWizardPage):
    def __init__(self,parent=None,cache=None):
        #TODO campos obligatorios fondo amarillo, por convencion
        #TODO class y fmt. eliminar si no aparecen en el origen
        super(WzProdBaseOld,self).__init__(parent)
    
        self.iterations = 0
        
        baseTable = cache['tabla_ref']
        self.baseFieldList = cache['info'][baseTable]['Fields']
        formatArray = [None , ] + [elem[1] for elem in ENUM_FORMAT ]
        self.formatArrayCode = [None , ] + [elem[0] for elem in ENUM_FORMAT ]
        fieldArray = [None , ] + [ '{}  ({})'.format(item['basename'],item['format']) for item in self.baseFieldList]
        self.fieldArrayCode = [None , ] + [ item['name'] for item in self.baseFieldList]
        
        self.setTitle("Definicion basica de la guía")
        self.setSubTitle(""" Introduzca el campo por el que desea agrupar los resultados y como determinar el texto  """)

        valueFormatLabel = QLabel("&Formato:")
        self.valueFormatCombo = QComboBox()
        self.valueFormatCombo.addItems(formatArray)
        self.valueFormatCombo.setCurrentIndex(1)
        valueFormatLabel.setBuddy(self.valueFormatCombo)
        #desactivo las jerarquias por defecto, de momento
        #self.valueFormatCombo.model().item(3).setEnabled(False)
        #self.valueFormatCombo.currentIndexChanged[int].connect(self.tipoElegido)

        prodNameLabel = QLabel("&Nombre:")
        self.prodName = QLineEdit()
        prodNameLabel.setBuddy(self.prodName)
        
        #TODO el campo debe de ser editable. Como actuar ver en editaCombo
        guideFldLabel = QLabel("&Campo guia:")
        self.guidFldCombo = QComboBox()
        self.guidFldCombo.addItems(fieldArray)
        self.guidFldCombo.setEditable(True)
        guideFldLabel.setBuddy(self.guidFldCombo)
        self.guidFldCombo.currentIndexChanged[int].connect(self.campoElegido)
        self.guidFldCombo.setStyleSheet("background-color:khaki;")
        
        groupBox = QGroupBox("C&onstructor de textos ")

        self.directCtorRB = QRadioButton("&Directa")
        self.catCtorRB = QRadioButton("Agrupado en Categorias, enunciando &valores")
        self.caseCtorRB = QRadioButton("Directamente via código SQL")
        self.dateCtorRB = QRadioButton("Agrupaciones de intervalos de fecha")
        #self.dateCtorRB.setDisabled(True)
        self.linkCtorRB = QRadioButton("A traves de otra tabla")            

        self.directCtorRB.setChecked(True)
        self.directCtorRB.toggled.connect(self.setFinalPage)

        groupBoxLayout = QVBoxLayout()
        groupBoxLayout.addWidget(self.directCtorRB)
        groupBoxLayout.addWidget(self.catCtorRB)
        groupBoxLayout.addWidget(self.caseCtorRB)
        groupBoxLayout.addWidget(self.dateCtorRB)
        groupBoxLayout.addWidget(self.linkCtorRB)

        groupBox.setLayout(groupBoxLayout)
        
        meatLayout = QGridLayout()
        meatLayout.addWidget(valueFormatLabel, 0, 0)
        meatLayout.addWidget(self.valueFormatCombo, 0, 1)
        meatLayout.addWidget(prodNameLabel, 1, 0)
        meatLayout.addWidget(self.prodName, 1, 1)
        meatLayout.addWidget(guideFldLabel, 2, 0)
        meatLayout.addWidget(self.guidFldCombo, 2, 1)
        meatLayout.addWidget(groupBox, 3, 0, 1, 2)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        #TODO maxima longitud del diccionario actual como indice en add
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterations]
        else:
            self.midict = self.wizard().diccionario

        self.fmtEnum = 'txt'
        if self.midict.get('elem'):
            try:
                indice = self.fieldArrayCode.index(self.midict['elem'])
                self.guidFldCombo.setCurrentIndex(indice)
                self.fmtEnum = self.formatoInterno2Enum(self.baseFieldList[indice -1]['format'])
            except ValueError :
                self.guidFldCombo.addItem(self.midict['elem'])
                self.formatArrayCode.append(self.midict['elem'])
                self.guidFldCombo.setCurrentIndex(self.guidFldCombo.count() -1)
            

        #TODO valor de defecto en funcion del formato del campo
        self.valueFormatCombo.setCurrentIndex(self.formatArrayCode.index(self.midict.get('fmt',self.fmtEnum)))
        self.prodName.setText(self.midict.get('name',str(self.iterations)))
        
            
        if self.midict.get('domain') or self.midict.get('link_via'):
            self.linkCtorRB.setChecked(True)
        elif self.midict.get('categorias'):
            self.catCtorRB.setChecked(True)
        elif self.midict.get('case_sql'):
            self.caseCtorRB.setChecked(True)
            
        self.iterator = self.iterations
        self.iterations += 1  #OJO 
        
    def nextId(self):
        print('invocamos nextId')
        nextPage = -1
        if self.directCtorRB.isChecked():
            # Fin de todo
            nextPage =  -1 #ixWzLink
        elif self.catCtorRB.isChecked():
            nextPage =  ixWzCategory
        elif self.caseCtorRB.isChecked():
            nextPage =  ixWzRowEditor
        elif self.dateCtorRB.isChecked():
            nextPage =  ixWzTime
        elif self.linkCtorRB.isChecked():
            nextPage =  ixWzDomain
        else:
            nextPage =  -1
        return nextPage
    
    def validatePage(self):
        print('invocamos validatePage')
        #TODO ¿como devuelvo el cursor al campo correspondiente'
        #if self.resultDefaultLineEdit.text() == '':
            #self.resultDefaultLineEdit.setFocus()
            #return False
        if self.guidFldCombo.currentIndex() == 0:
            self.guidFldCombo.setFocus()
            return False
        
        #Hago los arreglos que son necesarios en la entrada
        
        formato = self.formatArrayCode[self.valueFormatCombo.currentIndex()]
        if self.midict.get('fmt') or formato != 'txt':
            self.midict['fmt'] = formato
        if self.prodName.text() != str(self.iterator):
            self.midict['name'] = self.prodName.text()
        try:
            self.midict['elem'] = self.fieldArrayCode[self.guidFldCombo.currentIndex()]
        except IndexError: 
            self.midict['elem'] = self.guidFldCombo.currentText()

        if self.directCtorRB.isChecked():
            if self.midict.get('class'):
                self.midict['class'] = 'o'
            for key in ('domain','categorias','case_sql','link_via','mask'):
                if self.midict.get(key):
                    del self.midict[key]
        elif self.catCtorRB.isChecked():
            self.midict['class'] = 'c'
            self.midict['enum_fmt'] = self.fmtEnum
            for key in ('domain','case_sql','link_via','mask'):
                if self.midict.get(key):
                    del self.midict[key]
        elif self.caseCtorRB.isChecked():
            for key in ('domain','categorias','link_via','mask'):
                if self.midict.get(key):
                    del self.midict[key]
        elif self.dateCtorRB.isChecked():
            self.midict['class'] = 'd'
            for key in ('domain','categorias','case_sql','link_via'):
                if self.midict.get(key):
                    del self.midict[key]
        elif self.linkCtorRB.isChecked():
            for key in ('categorias','case_sql','mask'):
                if self.midict.get(key):
                    del self.midict[key]
        
        
        if self.isFinalPage() and self.iterations < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True
    
    def tipoElegido(self,ind):
                # control parcial tipo y cosas que se pueden hacer.
        # el tipo se normalizara al generar el arbol
        if   ind in (0,1,3): # nomral jerarquia
            self.directCtorRB.setChecked(True)
        elif ind == 2: # categorias
            self.catCtorRB.setChecked(True)
        elif ind == 4: #fecha
            self.dateCtorRB.setChecked(True)

    def formatoInterno2Enum(self,format):
        if format in ('texto',):
            return 'txt'
        elif format in ('fecha','fechahora','hora'):
            return 'date'
        else:
            return 'num'
        
    def campoElegido(self,ind):
        try:
            self.fmtEnum = self.formatoInterno2Enum(self.baseFieldList[ind -1]['format'])
        except IndexError:
            self.fmtEnum = 'txt'
        if self.fmtEnum in ('date',):
            self.dateCtorRB.setChecked(True)
        ##else:
            ##self.tipoElegido(self.valueFormatCombo.currentIndex()) 

    
class WzCategory(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzCategory,self).__init__(parent)
        
        self.setFinalPage(True)
        
        Formatos = [ item[1] for item in ENUM_FORMAT ]
        
        self.setTitle("Definicion por categorias")
        self.setSubTitle(""" Introduzca la agrupación de valores que constityen cada categoria  """)

        catResultFormatLabel = QLabel("Formato del &Resultado:")
        self.catResultFormatCombo = QComboBox()
        self.catResultFormatCombo.addItems(Formatos)
        self.catResultFormatCombo.setCurrentIndex(0)
        catResultFormatLabel.setBuddy(self.catResultFormatCombo)

        catValueFormatLabel = QLabel("Formato de los &Valores:")
        self.catValueFormatCombo = QComboBox()
        self.catValueFormatCombo.addItems(Formatos)
        catValueFormatLabel.setBuddy(self.catValueFormatCombo)
        
        #OJO notar que su posicion es posterior, pero lo necesito para cargar valor
        self.catResultDefaultLabel = QLabel("Resultado por &Defecto:")
        self.catResultDefaultLine = QLineEdit()
        self.catResultDefaultLabel.setBuddy(self.catResultDefaultLine)
    
        self.context=[]
        self.context.append(('categoria','condicion','valores'))
        self.context.append((QLineEdit,None,None))
        self.context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        self.context.append((QLineEdit,None,None))
        self.numrows=5
        self.data = None
        self.sheet = WDataSheet(self.context,self.numrows)
        #self.sheet.fill(self.data)
        self.simpleContext=(
            ('categoria',QLineEdit,None,None),
            ('condicion',QComboBox,None,tuple(LOGICAL_OPERATOR)),
            ('valores',QLineEdit,None,None),
            )
        self.simpleSheet = WPropertySheet(self.simpleContext,self.data)
        self.simpleSheet.hide()
    
    
        meatLayout = QGridLayout()
        meatLayout.addWidget(catValueFormatLabel,0,0)
        meatLayout.addWidget(self.catValueFormatCombo,0,1)
        meatLayout.addWidget(catResultFormatLabel,1,0)
        meatLayout.addWidget(self.catResultFormatCombo,1,1)
        meatLayout.addWidget(self.sheet, 2, 0, 1, 2)
        meatLayout.addWidget(self.simpleSheet, 2, 0, 1, 3)
        meatLayout.addWidget(self.catResultDefaultLabel,8,0)
        meatLayout.addWidget(self.catResultDefaultLine,8,1)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        base = self.wizard().page(ixWzProdBase) 
        if not base:
            self.iterator = -1
        else:
            self.iterator = self.wizard().page(ixWzProdBase).iterations

        obj = self.wizard().obj
        if obj.type() == 'prod': # cuando la llamada es indirecta
            self.midict = self.wizard().diccionario
            if self.midict.get('fmt'):
                self.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(self.midict['fmt']))
            if self.midict.get('enum_fmt'): #es el formato del campo origen
                self.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(self.midict['enum_fmt']))

        elif obj.type() == 'categories':
            if obj.text() == obj.type() :  #las categorias al completo
                self.midict = {'categories':self.wizard().diccionario}
                pai = self.wizard().obj.parent()
            else:
                self.midict = self.wizard().diccionario
                pai = self.wizard().obj.parent().parent()  
                self.sheet.hide()
                if self.midict.get('default'):
                    pass
                else:
                    self.simpleSheet.show()
                    self.catResultDefaultLabel.hide()
                    self.catResultDefaultLine.hide()
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
                
            self.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(fmt))
            self.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(enum_fmt))
            self.catResultFormatCombo.setEnabled(False)
            self.catValueFormatCombo.setEnabled(False)


        
    #def validatePage(self):
        #values = self.sheet.values()
        #for k,clave in enumerate(('driver','dbname','dbhost','dbuser','dbpass','port','debug')):
            #if self.context[k][1] == QComboBox:
                #try:
                    #self.midict[clave] = self.context[k][3][values[k]]
                #except IndexError:
                    #self.midict[clave] = self.sheet.cellWidget(k,0).getCurrentText()
            #else:
                #self.midict[clave] = values[k]
        #return True

        self.data = [] #'categoria','condicion','valores'  || 'result','condition','values'
        if self.midict.get('categories'): #usa sheet
            lista = self.midict['categories']
            for entry in lista:
                if entry.get('default'):
                    self.catResultDefaultLine.setText(entry['default'])
                    continue
                tmp = [ None for i in range(3) ]
                tmp[0] = entry['result']
                tmp[1] = LOGICAL_OPERATOR.index(entry['condition'])
                tmp[2] = norm2String(entry['values'])
                self.data.append(tmp)
            
            if len(self.data) > self.numrows:
                diff = len(self.data) - self.numrows
                self.addLines(diff)
        
            self.sheet.fill(self.data)

        else:
            entry = self.midict
            if entry.get('default'):
                self.catResultDefaultLine.setText(entry['default'])
            else:
                for k,clave in enumerate(('result','condition','values')):
                    if self.simpleContext[k][1] == QComboBox:
                        self.simpleSheet.set(k,0,self.simpleContext[k][3].index(self.midict.get(clave,'in')))
                    self.simpleSheet.set(k,0,norm2String(self.midict.get(clave)))
            

        if self.midict.get('categories'):
            self.wizard().setOptions(QWizard.HaveCustomButton1)
            self.setButtonText(QWizard.CustomButton1,'Mas entradas')
            self.wizard().customButtonClicked.connect(self.addEntry)

        
    def nextId(self):
        return -1
    
    def validatePage(self):        

        resultado = self.sheet.values()
        obj = self.wizard().obj
        if obj.type() == 'prod': # cuando la llamada es indirecta
            formato = ENUM_FORMAT[self.catResultFormatCombo.currentIndex()][0]
            enumFmt = ENUM_FORMAT[self.catValueFormatCombo.currentIndex()][0]
            
            if self.midict.get('fmt') or formato != 'txt':
                self.midict['fmt'] = formato
            if self.midict.get('enum_fmt') or formato != enumFmt:
                self.midict['enum_fmt'] = enumFmt
            if self.midict.get('categories'):      
                self.midict['categories'].clear()
            else:
                self.midict['categories'] = []
            resultado = self.sheet.values()
            for entry in resultado:
                if entry[0] == '':
                    continue
                self.midict['categories'].append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
            
            if self.catResultDefaultLine.text() != '':
                self.midict['categories'].insert(0,{'default':self.catResultDefaultLine.text()})

        elif obj.type() == 'categories':
            if obj.text() == obj.type():  #las categorias al completo
                lista_categ = self.wizard().diccionario
                lista_categ.clear()
                for entry in resultado:
                    if entry[0] == '':
                        continue
                    lista_categ.append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
                
                if self.catResultDefaultLine.text() != '':
                    lista_categ.insert(0,{'default':self.catResultDefaultLine.text()})

            else:
                # FIXME no procesa bien el default
                self.midict.clear()
                if self.catResultDefaultLine.text() != '':
                    self.midict = {'default':self.catResultDefaultLine.text()}
                    return True
                values = self.simpleSheet.values()
                for k,clave in enumerate(('result','condition','values')):
                    if self.context[k][1] == QComboBox:
                        try:
                            self.midict[clave] = self.context[k][3][values[k]]
                        except IndexError:
                            self.midict[clave] = self.sheet.cellWidget(k,0).getCurrentText()
                    else:
                        self.midict[clave] = values[k]
                        print(self.midict,self.wizard().diccionario)


                
        
            
        #if self.isFinalPage() and  (self.iterator == -1 or self.iterator < self.wizard().prodIters ):
            #self.wizard().setStartId(ixWzProdBase);
            #self.wizard().restart()        
            #return False

        return True
    
    def addEntry(self,buttonId):
        #FIXME da algunos problemas de presentacion ¿Bug upstream?
        if buttonId == QWizard.CustomButton1:
            self.addLines(3)
            
    def addLines(self,numLines):
        count = self.sheet.rowCount()
        for k in range(numLines):
            self.sheet.insertRow(count+k)
            self.sheet.addRow(count+k)
        self.sheet.setCurrentCell(count,0)
            
class WzRowEditor(QWizardPage):
    def __init__(self,parent=None,cache=None):
        #TODO hay que buscar/sustituir nombres de campos
        # o como alternativa presentar como pares when / then
        super(WzRowEditor,self).__init__(parent)
        
        self.setFinalPage(True)

        self.setTitle("Definicion de texto libre")
        self.setSubTitle(""" Introduzca el codigo SQL que desea utilizar para agrupar.
        Recuerde sustituir el nombre del campo guia por $$1 """)

        #FIXME no admite mandatory
        self.editArea = QPlainTextEdit()

        meatLayout = QGridLayout()
        meatLayout.addWidget(self.editArea,0,0,1,0)

        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        self.iterator = -1
        if self.wizard().obj.type() not in TYPE_EDIT :
            self.iterator = self.wizard().page(ixWzProdBase).iterations
            if isinstance(self.wizard().diccionario,(list,tuple)):
                #varias entradas
                self.midict = self.wizard().diccionario[self.iterator -1]
            else:
                self.midict = self.wizard().diccionario
            caseStmt = self.midict.get('case_sql')
        else:
            self.midict = self.wizard().diccionario
            caseStmt = self.midict
            
        if isinstance(caseStmt,(list,tuple)):
            self.editArea.setPlainText('\n'.join(caseStmt))
        else:    
            self.editArea.setPlainText(caseStmt)
        pass
    def nextId(self):
        return -1
    def validatePage(self):
        #if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            #self.wizard().setStartId(ixWzProdBase);
            #self.wizard().restart()        
            #return False
        
        texto = self.editArea.document().toPlainText()
        if isinstance(self.midict,dict):
            area = self.midict.get('case_sql')
        else:
            area = self.midict
            
        if texto and texto.strip() != '':
            area.clear()
            area += texto.split('\n')
        elif self.midict is not None: 
            area.clear()
        return True

class WzTime(QWizardPage):
    def __init__(self,parent=None,cache=None):
        super(WzTime,self).__init__(parent)
        
        self.setFinalPage(True)
        
        self.setTitle("Guía tipo fecha")
        self.setSubTitle(""" Introduzca la jerarquía de criteros temporales que desea  """)

        self.Formatos = [ item[1] for item in FECHADOR ]
        self.formatosCode = [ item[0] for item in FECHADOR ]
        self.maxLevel = 4  
        self.formFechaLabel = [None for k in range(self.maxLevel)]
        self.formFechaCombo = [None for k in range(self.maxLevel)]
        
        for k in range(self.maxLevel):
            self.defItemComboBox(k)

        meatLayout = QGridLayout()
        for k in range(self.maxLevel):
            meatLayout.addWidget(self.formFechaLabel[k],k,0)
            meatLayout.addWidget(self.formFechaCombo[k],k,1)
        self.setLayout(meatLayout)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        #TODO no inicializa si no esta en la regla de produccion
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        

        mascara = ''
        if self.midict.get('mask'):
            mascara = self.midict['mask']
        elif self.midict.get('type'):
            mascara = self.midict['type']
        for k,letra in enumerate(mascara):
            self.formFechaCombo[k].setCurrentIndex(self.formatosCode.index(letra))
            self.seleccion(k)
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        pass
    
    def nextId(self):
        return -1

    def validatePage(self):
        mask = ''
        for k in range(self.maxLevel):
            if self.formFechaCombo[k].currentText() != '':
                idx = self.Formatos.index(self.formFechaCombo[k].currentText())
                mask += self.formatosCode[idx]
            else:
                break
        if mask != '':
            self.midict['mask'] = mask
        if self.midict.get('type'):
            del self.midict['type']
            
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

    def defItemComboBox(self,k):
        # para que coja valores distintos de k en cada ejecucion !!???
        self.formFechaLabel[k] = QLabel("Formato del {}er nivel:".format(k))
        self.formFechaCombo[k] = QComboBox()
        if k == 0:
            self.formFechaCombo[k].addItems(self.Formatos[k:])
        else:
            self.formFechaCombo[k].addItems(['',] + self.Formatos[k:])
        self.formFechaCombo[k].setCurrentIndex(0)
        self.formFechaLabel[k].setBuddy(self.formFechaCombo[k])
        self.formFechaCombo[k].currentIndexChanged.connect(lambda: self.seleccion(k))

        
        
    def seleccion(self,idx):
        #TODO sería mas interesante pasar tambien el valor, pero sigo sin acertar
        if idx < 0:
            return 
        # que hemos cambiado ?
        valor = self.formFechaCombo[idx].currentText()
        if valor == '':
            if idx != 0:
                posActual = self.Formatos.index(self.formFechaCombo[idx -1].currentText())+1
            else:
                posActual = 0
        else:
            posActual = self.Formatos.index(valor)
        
        for k in range(idx +1,self.maxLevel):
            j = k - idx
            #if posActual >= (self.formFechaCombo[idx].count() -1):
            if len(self.Formatos[posActual + j:]) == 0:
                self.formFechaLabel[k].hide()
                self.formFechaCombo[k].hide()
            else:
                self.formFechaCombo[k].blockSignals(True)  #no veas el loop en el que entra si no
                if not self.formFechaCombo[k].isVisible():
                    self.formFechaLabel[k].show() #por lo de arriba
                    self.formFechaCombo[k].show()
                self.formFechaCombo[k].clear()
                self.formFechaCombo[k].addItems(['',] + self.Formatos[posActual + j :])
                self.formFechaCombo[k].blockSignals(False)  

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
         
        #if self.isFinalPage() and (self.iterator == -1 or self.iterator < self.wizard().prodIters):
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


        #para la lista
        
        self.context=[]
        
        self.context.append(['Tabla Desde','campos desde','Tabla hasta','Campos Hasta'])
        self.context.append([QComboBox,None,self.listOfTables])
        self.context.append([WMultiCombo,None,['',]])
        self.context.append([QComboBox,None,self.listOfTables])
        self.context.append([WMultiCombo,None,['',]])
        
        numrows=4
        
        self.joinListArray = WDataSheet(self.context,numrows)
        
        for row in range(numrows):
            self.defineSlots(row)
        
        
        # ahora para el detalle

        self.baseLabel = QLabel('Desde ')
        self.baseTableCombo = QComboBox()
        self.baseTableCombo.addItems(self.listOfTables)
        self.baseTableCombo.setCurrentIndex(0)

        
        self.destLabel = QLabel('Hacia ')
        self.destTableCombo = QComboBox()
        self.destTableCombo.addItems(self.listOfTables)
        self.destTableCombo.setCurrentIndex(0)
        
        self.clauseContext=[]
        
        self.clauseContext.append(['c. base','condicion','c. enlace'])
        self.clauseContext.append([QComboBox,None,['',]+list(self.listOfFields)])
        self.clauseContext.append([QComboBox,None,tuple(LOGICAL_OPERATOR)])
        self.clauseContext.append([QComboBox,None,None])
        
        numrows=3
        
        self.joinClauseArray = WDataSheet(self.clauseContext,numrows)
        
        #self.destTableCombo.currentIndexChanged[int].connect(lambda i,w='target' : self.tablaElegida(i,w))
        #self.baseTableCombo.currentIndexChanged[int].connect(lambda i,w='base' : self.tablaElegida(i,w))
        
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        self.joinClauseArray.resizeColumnToContents(0)

        self.joinFilterLabel = QLabel("&Filtro:")
        self.joinFilterLineEdit = QLineEdit()
        self.joinFilterLabel.setBuddy(self.joinFilterLineEdit)
            
        meatLayout = QGridLayout()

        meatLayout.addWidget(self.joinListArray,0,0,3,4)
        #
        meatLayout.addWidget(self.baseLabel,0,0)
        meatLayout.addWidget(self.baseTableCombo,0,1)
        meatLayout.addWidget(self.destLabel,1,0)
        meatLayout.addWidget(self.destTableCombo,1,1)
        meatLayout.addWidget(self.joinClauseArray,2,0,3,4)
        meatLayout.addWidget(self.joinFilterLabel,6,0)
        meatLayout.addWidget(self.joinFilterLineEdit,6,1)

        self.setLayout(meatLayout)

        self.joinListArray.hide()
        self.baseLabel.hide()
        self.baseTableCombo.hide()
        self.destLabel.hide()
        self.destTableCombo.hide()
        self.joinClauseArray.hide()
        self.joinFilterLabel.hide()
        self.joinFilterLineEdit.hide()

    def initializePage(self):

        obj = self.wizard().obj
        self.iterator = None
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
        elif self.tipo == 'LinkEntry':
            self.baseLabel.show()
            self.baseTableCombo.show()
            self.destLabel.show()
            self.destTableCombo.show()
            self.joinClauseArray.show()
            self.joinFilterLabel.show()
            self.joinFilterLineEdit.show()


    def nextId(self):
        return -1

    def validatePage(self):
        if self.tipo == 'LinkList':
            return self.validatePageLinkList()
        elif self.tipo == 'LinkEntry':
            return self.validatePageLinkEntry()
    
      
    def initializePageLinkEntry(self):
        obj = self.wizard().obj
        pos = obj.getPos()
        auxobj = obj.getPrevious()
        if auxobj is not None:
            origTable = auxobj.getChildrenByName('table')
        else:
            origTable = self.cache['tabla_ref']
        destTable = self.midict.get('table')
        #self.baseTableCombo.show()
        baseField = [ item.get('base_elem') for item in self.midict.get('clause') ]
        relField = [ item.get('rel_elem') for item in self.midict.get('clause') ]
        
       
        pos = setAddComboElem(origTable,self.baseTableCombo,self.listOfTablesCode,self.listOfTables)
        self.baseTableCombo.setEnabled(False)
        self.sourceFields = [ item[1] for item in getFieldsFromTable(origTable,self.cache,self.cube) ]
        self.sourceFieldsBase= [ item[0] for item in getFieldsFromTable(origTable,self.cache,self.cube) ]
        column = 1
        self.clauseContext[column][2] = ['',] + list(self.sourceFields)
        self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
        
        pos = setAddComboElem(destTable,self.destTableCombo,self.listOfTablesCode,self.listOfTables)
        self.destTableCombo.setEnabled(False)
        self.targetFields = [ item[1] for item in getFieldsFromTable(destTable,self.cache,self.cube) ]
        self.targetFieldsBase= [ item[0] for item in getFieldsFromTable(destTable,self.cache,self.cube) ]
        column = 3
        self.clauseContext[column][2] = ['',] + list(self.targetFields)
        self.joinClauseArray.changeContextColumn(self.clauseContext[column],column)
 
        #self.joinClauseArray.resizeColumnsToContents()
            
        if self.midict.get('clause'):
            for i,clausula in enumerate(self.midict.get('clause')):
                setAddComboElem(clausula.get('condition','='),
                                self.joinClauseArray.cellWidget(i,1),
                                LOGICAL_OPERATOR,LOGICAL_OPERATOR)
                setAddComboElem(clausula.get('base_elem',''),
                                self.joinClauseArray.cellWidget(i,0),
                                self.sourceFieldsBase,self.sourceFields,1)

                setAddComboElem(clausula.get('rel_elem',''),
                                self.joinClauseArray.cellWidget(i,2),
                                self.targetFieldsBase,self.targetFields,1)
        
        

        self.joinFilterLineEdit.setText(self.midict.get('filter',''))
    
    def initializePageLinkList(self):
        for i in range(len(self.midict)):
            #TODO  que pasa si tengo mas de cinco ocurrencias
            setAddComboElem(self.midict[i -1].get('table') if i != 0 else self.cache['tabla_ref'],
                            self.joinListArray.cellWidget(i,0),
                            self.listOfTablesCode,self.listOfTables)
            setAddComboElem(self.midict[i].get('table'),
                            self.joinListArray.cellWidget(i,2),
                            self.listOfTablesCode,self.listOfTables)
            
            # ahora los campos ya modificado el combos
            base_elems = [ item.get('base_elem') for item in self.midict[i].get('clause') ]
            self.joinListArray.cellWidget(i,1).set(base_elems)
            tgt_elems = [ item.get('rel_elem') for item in self.midict[i].get('clause') ]
            self.joinListArray.cellWidget(i,3).set(tgt_elems)
            self.joinListArray.resizeColumnsToContents()

    def validatePageLinkEntry(self):
        resultado = self.joinClauseArray.values()
        # ser pestiño pero primero tengo que eliminar los huecos
        resultado = self.joinClauseArray.values()
        lastNonEmpty = len(resultado) -1
        for k in range(len(resultado) -1,-1,-1):
            if resultado[k][0] != 0:
                lastNonEmpty = k
                break
        try:
            pos = [ linea[0] for linea in resultado[0:lastNonEmpty +1]].index(0)
            self.joinClauseArray.removeRow(pos)
            return False
        except ValueError:
            pass

        baseFlds = [ linea[0] for linea in resultado if linea[0] != 0]
        tgtFlds = [ linea[2] for linea in resultado if linea[2] != 0]
        if len(baseFlds) != len(tgtFlds) :
            return False
        
            
        self.midict['table'] = self.listOfTablesCode[self.destTableCombo.currentIndex()]
        self.midict['filter'] = self.joinFilterLineEdit.text()
        self.midict['clause'].clear()
        for linea in resultado:
            if linea[0] == 0:
                continue  #deberia ser break, pero por si acaso no funciona lo de arriba
            entry = {}
            entry['base_elem'] = self.sourceFieldsBase[linea[0] -1]
            entry['rel_elem'] = self.targetFieldsBase[linea[2] -1]
            if linea[1] != 3:
                entry['condition'] = LOGICAL_OPERATOR[linea[1]]
            self.midict['clause'].append(entry)
        return True
    
    def validatePageLinkList(self):
        #TODO eliminar lineas en blanco
        # ser pestiño pero primero tengo que eliminar los huecos
        resultado = self.joinListArray.values()
        lastNonEmpty = len(resultado) -1
        for k in range(len(resultado) -1,-1,-1):
            if resultado[k][0] != 0:
                lastNonEmpty = k
                break
        try:
            pos = [ linea[0] for linea in resultado[0:lastNonEmpty +1]].index(0)
            self.joinListArray.removeRow(pos)
            return False
        except ValueError:
            pass
            
        #ahora verifico que los ficheros estan correctamente enlazados    
        #ahora las validaciones complicadas
        # si i != 0 si base != target(-1) insert row  target[-1] -> base
        # si i == 0 si base != referencia insert row  referencia -> base
            #self.joinClauseArray.addRow(0)
            #fillrow
        # si i != -1 si target != base[+1] append row

        baseIdx = self.listOfTablesCode.index(self.cache['tabla_ref'])
        for row,linea in enumerate(resultado):
            #if linea[0] == 0:
                #continue
            ##print(linea)
            if row == 0:
                if linea[0] != baseIdx:
                    #inserta linea
                    self.joinListArray.appendRow(row )
                    self.defineSlots(row)
                    self.joinListArray.cellWidget(row ,0).setCurrentIndex(baseIdx)
                    self.joinListArray.cellWidget(row ,2).setCurrentIndex(linea[0])
                    #self.tablaElegidaLinkList(baseIdx,row,'base')
                    self.setBaseFK(row,baseIdx,linea[0])
                    return False
            else:
                if linea[0] != resultado[row -1][2]:
                    #inserta linea
                    self.joinListArray.appendRow(row )
                    self.defineSlots(row)
                    self.joinListArray.cellWidget(row ,0).setCurrentIndex(resultado[row -1][2])
                    self.joinListArray.cellWidget(row ,2).setCurrentIndex(linea[0])
                    self.setBaseFK(row,resultado[row -1][2],linea[0])
                    return False

            if row == lastNonEmpty:
                pass
            elif linea[2] != resultado[row +1][0]:
                #inserta linea
                self.joinListArray.appendRow(row +1)
                self.defineSlots(row + 1)
                self.joinListArray.cellWidget(row +1 ,0).setCurrentIndex(linea[2])
                self.joinListArray.cellWidget(row +1,2).setCurrentIndex(resultado[row +1][0])
                self.setBaseFK(row +1,linea[2],resultado[row +1][0])
                return False
            
        # ahora compruebo los campos de enlace
        for row,linea in enumerate(resultado):
            if linea[1] == '' or linea[2] == '':
                #FIXME posicionar el cursor en esa posicion
                return False
            if len(norm2List(linea[1])) != len(norm2List(linea[3])):
                return False
                                                                            
            self.midict.clear() #esto es muy valiente
            for row,linea in enumerate(resultado):
                entry = {}
                entry['table'] = self.listOfTablesCode[linea[2]]
                entry['filter'] = ''
                entry['clause'] = []
                base = norm2List(linea[1])
                ref  = norm2List(linea[3])
                for k in range(len(base)):
                    entry['clause'].append({'base_elem':base[k],
                                            'rel_elem':ref[k]})
                self.midict.append(entry)
                
        #if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            #self.wizard().setStartId(ixWzProdBase);
            #self.wizard().restart()        
            #return False
        return True

        return True

    def defineSlots(self,row):
        self.joinListArray.cellWidget(row,0).currentIndexChanged[int].connect(
            lambda p,i=row,w='base' : self.tablaElegidaLinkList(p,i,w))
        self.joinListArray.cellWidget(row,2).currentIndexChanged[int].connect(
            lambda p,i=row,w='tgt' : self.tablaElegidaLinkList(p,i,w))
        
    def setBaseFK(self,row,fromTableIdx,toTableIdx):
        fromTable = self.listOfTablesCode[fromTableIdx]
        toTable = self.listOfTablesCode[toTableIdx]
        claves = self.cache['info'][fromTable].get('FK')
        if not claves:
            return 
        for fkey in claves:
            #FIXME si hay varias solo coge la primera
            if fkey.get('parent table') == toTable:
                setAddComboElem(fkey.get('ref field'),
                                self.joinListArray.cellWidget(row,1),
                                ['',]+[ entry['name'] for entry in self.cache['info'][fromTable]['Fields']],
                                ['',]+[ entry['basename'] for entry in self.cache['info'][fromTable]['Fields']])
                setAddComboElem(fkey.get('parent field'),
                                self.joinListArray.cellWidget(row,3),
                                ['',]+[ entry['name'] for entry in self.cache['info'][toTable]['Fields']],
                                ['',]+[ entry['basename'] for entry in self.cache['info'][toTable]['Fields']])

    def tablaElegidaLinkList(self,idx,row,status):
        #if status == 'base' and idx == 0:
            #self.joinClauseArray.removeRow(row)
            #return 
        tabname = self.listOfTablesCode[idx]
        listOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        listOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        numrows = self.joinListArray.rowCount()
        numcols = self.joinListArray.columnCount()
        
        if status == 'base':
            column = 1
        elif status == 'tgt':
            column = 3
        self.joinListArray.cellWidget(row,column).load(listOfFieldsCode,listOfFields)    
        
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
        self.listOfLinkFields = [ item[1] for item in getFieldsFromTable(cache['tabla_ref'],self.cache,self.cube) ]
        self.listOfLinkFieldsCode = [ item[0] for item in getFieldsFromTable(cache['tabla_ref'],self.cache,self.cube) ]

        
        self.setTitle("Definición del dominio de la guía")
        self.setSubTitle(""" Introduzca la localización donde estan los valores por los que vamos a agrupar """)

        prodNameLabel = QLabel("&Nombre:")
        self.prodName = QLineEdit()
        prodNameLabel.setBuddy(self.prodName)
        self.prodName.setStyleSheet("background-color:khaki;")
 
        domainTableLabel = QLabel("&Tabla de definición de valores")
        self.domainTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.domainTableCombo.addItems(self.listOfTables)
        self.domainTableCombo.setCurrentIndex(0)
        domainTableLabel.setBuddy(self.domainTableCombo)
        self.domainTableCombo.currentIndexChanged[int].connect(lambda i,w='domain' : self.tablaElegida(i,w))

        #
        domainGuideLabel = QLabel("Campo &guia:")
        self.domainFieldCombo = WMultiCombo()
        #self.guidFldCombo.addItems(self.listOfFields)
        self.domainFieldCombo.setEditable(True)
        domainGuideLabel.setBuddy(self.domainFieldCombo)
        self.domainFieldCombo.currentIndexChanged[int].connect(self.campoElegido)
        self.domainFieldCombo.setStyleSheet("background-color:khaki;")
 
        #
        domainDescLabel = QLabel("&Campo &Descriptivo:")
        self.domainDescCombo = WMultiCombo()
        #self.guideDescCombo.addItems(self.listOfFields)
        self.domainDescCombo.setEditable(True)
        domainDescLabel.setBuddy(self.domainDescCombo)
        #self.domainDescCombo.currentIndexChanged[int].connect(self.campoElegido)

        #TODO algo para poder construir links complejos. Es necesario en la interfaz
        
        guideDataTableLabel = QLabel("&Tabla de datos")
        self.guideDataTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.guideDataTableCombo.addItems(self.listOfTables)
        self.guideDataTableCombo.setCurrentIndex(self.listOfTablesCode.index(cache['tabla_ref']))
        guideDataTableLabel.setBuddy(self.guideDataTableCombo)
        self.guideDataTableCombo.currentIndexChanged[int].connect(lambda i,w='data' : self.tablaElegida(i,w))

        #
        guideDataGuideLabel = QLabel("Campo &guia:")
        self.guideDataFieldCombo = WMultiCombo()
        self.guideDataFieldCombo.load(self.listOfLinkFieldsCode,self.listOfLinkFields)
        #self.guidFldCombo.addItems(self.listOfFields)
        self.guideDataFieldCombo.setEditable(True)
        guideDataGuideLabel.setBuddy(self.guideDataFieldCombo)
        self.guideDataFieldCombo.currentIndexChanged[int].connect(self.campoElegido)
        self.guideDataFieldCombo.setStyleSheet("background-color:khaki;")
        
        self.linkCTorRB = QRadioButton("Con tablas intermedias")
        self.linkCTorRB.hide()
        #
        #sp_retain = self.guideLinkCombo.sizePolicy()
        #sp_retain.setRetainSizeWhenHidden(True)
        #self.guideLinkCombo.setSizePolicy(sp_retain)
        
        self.catCtorRB = QRadioButton("Agrupado en Categorias")
        self.caseCtorRB = QRadioButton("Directamente via código SQL")
        self.dateCtorRB = QRadioButton("Agrupaciones de fechas")
        
        self.catCtorRB.clicked.connect(self.setFinal)
        self.caseCtorRB.clicked.connect(self.setFinal)
        self.dateCtorRB.clicked.connect(self.setFinal)
        self.linkCTorRB.clicked.connect(self.setFinal)
        
        groupBox = QGroupBox("Criterios de agrupacion manuales ")
        groupBoxLayout = QHBoxLayout()
        groupBoxLayout.addWidget(self.catCtorRB)
        groupBoxLayout.addWidget(self.caseCtorRB)
        groupBoxLayout.addWidget(self.dateCtorRB)
        groupBox.setLayout(groupBoxLayout)
        
        #context.append(('c. base','condicion','c. enlace'))
        #context.append((QComboBox,None,('',)+tuple(self.listOfFields)))
        #context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        #context.append((QComboBox,None,None))
        
        #numrows=3
        
        #self.joinClauseArray = WDataSheet(context,numrows)
        
        #for k in range(self.joinClauseArray.rowCount()):
            #self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        #self.joinClauseArray.resizeColumnToContents(0)
            
        meatLayout = QGridLayout()
        meatLayout.addWidget(prodNameLabel,0,0)
        meatLayout.addWidget(self.prodName,0,1,1,3)
        meatLayout.addWidget(domainTableLabel,1,0)
        meatLayout.addWidget(self.domainTableCombo,1,1)
        meatLayout.addWidget(domainGuideLabel,1,2)
        meatLayout.addWidget(self.domainFieldCombo,1,3)
        meatLayout.addWidget(domainDescLabel,2,2)
        meatLayout.addWidget(self.domainDescCombo,2,3)
        meatLayout.addWidget(guideDataTableLabel,3,0)
        meatLayout.addWidget(self.guideDataTableCombo,3,1)
        meatLayout.addWidget(guideDataGuideLabel,3,2)
        meatLayout.addWidget(self.guideDataFieldCombo,3,3)
        meatLayout.addWidget(self.linkCTorRB,4,3)
        meatLayout.addWidget(groupBox, 5, 0, 1, 4)

        #meatLayout.addWidget(self.joinClauseArray,2,0,1,2)
        self.setLayout(meatLayout)

        

    
    def initializePage(self):
        #TODO no inicializa si no esta en la regla de produccion
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterations]
        else:
            self.midict = self.wizard().diccionario
        
            
            
        #vamos ahora al proceso de add
        #TODO si no esta en la lista
        self.prodName.setText(self.midict.get('name',str(self.iterations)))
            
        if self.midict.get('domain'):
            #TODO elementos multiples
            setAddComboElem(self.midict['domain'].get('table'),
                            self.domainTableCombo,
                            self.listOfTablesCode,self.listOfTables)
            #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
            self.domainFieldCombo.set(norm2String(self.midict['domain'].get('code')))
            self.domainDescCombo.set(norm2String(self.midict['domain'].get('desc')))
            if self.midict.get('link via'):
                self.linkCTorRB.setChecked(True)
                self.linkCTorRB.show()
                #TODO multiples criterios 
                setAddComboElem(self.midict['link via'][-1].get('table'),
                                self.guideDataTableCombo,
                            self.listOfTablesCode,self.listOfTables)
            self.guideDataFieldCombo.set(norm2String(self.midict.get('elem')))
            self.guideDataFieldCombo.show()
            self.guideDataTableCombo.show()
        else:    
            setAddComboElem(self.cache['tabla_ref'],
                            self.domainTableCombo,
                            self.listOfTablesCode,self.listOfTables)
            #es valido porque la señal de cambio de tabla se dispara internamente con el setCurrentIndex
            if self.midict.get('elem'):
                self.domainFieldCombo.set(norm2String(self.midict.get('elem')))
            else:
                self.domainFieldCombo.setCurrentIndex(0)  #FIXME
            self.domainDescCombo.setCurrentIndex(0)  #FIXME
            self.guideDataFieldCombo.hide()
            self.guideDataTableCombo.hide()
            
        clase=self.midict.get('class','o')
        if clase == 'd' or self.midict.get('fmt','txt') == 'date':
            self.dateCtorRB.setChecked(True)
        
        if self.midict.get('categories'):
            self.catCtorRB.setChecked(True)
        elif self.midict.get('case_sql'):
            self.caseCtorRB.setChecked(True)
     
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


    def formatoInterno2Enum(self,format):
        if format in ('texto',):
            return 'txt'
        elif format in ('fecha','fechahora','hora'):
            return 'date'
        else:
            return 'num'
        
    def campoElegido(self,ind):
        try:
            self.fmtEnum = self.formatoInterno2Enum(self.baseFieldList[ind][2])
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
        #
        tipo = obj.type()
        if action == 'add date filter':
            self.diccionario = {'date filter':[]}
        else:
            self.diccionario = tree2dict(obj,isDictionaryEntry)
            
        if not tipo or tipo == 'connect':
            self.setPage(ixWzConnect, WzConnect())
        # TODO no son estrictamente complejos pero la interfaz es mejor como complejos
        if not tipo:
            self.setPage(ixWzFieldList, WzFieldList(cache=cache_data))
            self.setPage(ixWzBaseFilter, WzBaseFilter(cache=cache_data))
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
        elif tipo in ('guides','prod'): #== 'prod':
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
