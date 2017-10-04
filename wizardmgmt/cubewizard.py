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
        catResultDefaultLabel = QLabel("Resultado por &Defecto:")
        self.catResultDefaultLine = QLineEdit()
        catResultDefaultLabel.setBuddy(self.catResultDefaultLine)
    
        self.context=[]
        
        self.context.append(('categoria','condicion','valores'))
        self.context.append((QLineEdit,None,None))
        self.context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        self.context.append((QLineEdit,None,None))
        self.numrows=5
        self.data = None
        self.sheet = WDataSheet(self.context,self.numrows)
        #self.sheet.fill(self.data)
    
    
        meatLayout = QGridLayout()
        meatLayout.addWidget(catValueFormatLabel,0,0)
        meatLayout.addWidget(self.catValueFormatCombo,0,1)
        meatLayout.addWidget(catResultFormatLabel,1,0)
        meatLayout.addWidget(self.catResultFormatCombo,1,1)
        meatLayout.addWidget(self.sheet, 2, 0, 1, 2)
        meatLayout.addWidget(catResultDefaultLabel,8,0)
        meatLayout.addWidget(self.catResultDefaultLine,8,1)
        
        self.setLayout(meatLayout)
    
    def initializePage(self):
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario

        if self.midict.get('fmt'):
            self.catResultFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(self.midict['fmt']))
        if self.midict.get('enum_fmt'): #es el formato del campo origen
            self.catValueFormatCombo.setCurrentIndex( [ item[0] for item in ENUM_FORMAT ].index(self.midict['enum_fmt']))
        if self.midict.get('categorias'):
            self.data = [] #'categoria','condicion','valores'  || 'result','condition','values'
            for entry in self.midict['categorias']:
                if entry.get('default'):
                    self.catResultDefaultLine.setText(entry['default'])
                    continue
                tmp = []
                tmp[0] = entry['result']
                tmp[1] = LOGICAL_OPERATOR.index(entry['condition'])
                tmp[2] = norm2String(entry['values'])
                self.data.append(tmp)
            
            if len(self.data) > self.numrows:
                diff = len(self.data) - self.numrows
                self.addLines(diff)
        
            self.sheet.fill(self.data)

        self.wizard().setOptions(QWizard.HaveCustomButton1)
        self.setButtonText(QWizard.CustomButton1,'Mas entradas')
        self.wizard().customButtonClicked.connect(self.addEntry)

        
    def nextId(self):
        return -1
    def validatePage(self):        
        formato = ENUM_FORMAT[self.catResultFormatCombo.currentIndex()][0]
        enumFmt = ENUM_FORMAT[self.catValueFormatCombo.currentIndex()][0]
        print(formato,enumFmt)
        if self.midict.get('fmt') or formato != 'txt':
            self.midict['fmt'] = formato
        if self.midict.get('enum_fmt') or formato != enumFmt:
            self.midict['enum_fmt'] = enumFmt
        if self.midict.get('categorias'):      
            self.midict['categorias'].clear()
        else:
            self.midict['categorias'] = []
        resultado = self.sheet.values()
        for entry in resultado:
            if entry[0] == '':
                continue
            self.midict['categorias'].append({'result':entry[0],'condition':LOGICAL_OPERATOR[entry[1]],'values':norm2List(entry[2])})
        
        if self.catResultDefaultLine.text() != '':
            self.midict['categorias'].insert(0,{'default':self.catResultDefaultLine.text()})
            
        if self.isFinalPage() and  self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False

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
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        

        caseStmt = self.midict.get('case_sql')
        if isinstance(caseStmt,(list,tuple)):
            self.editArea.setPlainText('\n'.join(caseStmt))
        else:    
            self.editArea.setPlainText(caseStmt)
        pass
    def nextId(self):
        return -1
    def validatePage(self):
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        
        texto = self.editArea.document().toPlainText()
        
        if texto and texto.strip() != '':
            self.midict['case_sql'] = texto.split('\n')
        elif self.midict.get('case_sql'):
            del self.midict['case_sql']
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
        self.targetCodeList = QListWidget()
        targetCodeLabel.setBuddy(self.targetCodeList)
        self.targetCodeList.setStyleSheet("background-color:khaki;")
        self.targetCodeList.setSelectionMode(QListWidget.ExtendedSelection)

        targetDescLabel = QLabel("&Textos desciptivos:")
        self.targetDescList = QListWidget()
        targetDescLabel.setBuddy(self.targetDescList)
        self.targetDescList.setSelectionMode(QListWidget.ExtendedSelection)

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
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        #TODO no inicializa si no esta en la regla de produccion
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario
        print('inicializando',self.midict)
        if self.midict.get('domain'):
            domain = self.midict['domain']
            print('y aqui el dominio',domain)
            if domain.get('table'):
                try:
                    idx = self.listOfTablesCode.index(domain['table'])
                except ValueError:
                    idx = self.listOfTables.index(domain['table'])
                print(domain['table'],idx)
                self.targetTableCombo.setCurrentIndex(idx)
            if domain.get('code'):
                ct = norm2List(domain['code'])
                for item in ct:
                    try:
                        idx = self.listOfFieldsCode.index(item)
                        entry = self.targetCodeList.model().itemFromIndex(idx)
                    except ValueError:
                        try:
                            idx = self.listOfFields.index(item)
                        except ValueError:
                            self.targetCodeList.addItem(item)
                            idx= self.targetCodeList.count() -1
                            #select item
                            self.listOfFields.append(item)
                            self.listOfFieldsCode.append(item)
                    #entry = self.targetCodeList.model().itemFromIndex(idx)
                    selItem = self.targetCodeList.item(idx)
                    selItem.setSelected(True)
                    
            if domain.get('desc'):
                ct = norm2List(domain['desc'])
                for item in ct:
                    try:
                        idx = self.listOfFieldsCode.index(item)
                        entry = self.targetDescList.model().itemFromIndex(idx)
                    except ValueError:
                        try:
                            idx = self.listOfFields.index(item)
                        except ValueError:
                            self.targetDescList.addItem(item)
                            idx= self.targetDescList.count() -1
                            #select item
                            self.listOfFields.append(item)
                            self.listOfFieldsCode.append(item)
                    selItem = self.targetDescList.item(idx)
                    selItem.setSelected(True)
                    
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
            self.midict['domain']={}
        domain = self.midict['domain']
        
        tabidx =self.targetTableCombo.currentIndex()
        domain['table'] = self.listOfTablesCode[tabidx]
        
        domain['code'] = []
        for entry in self.targetCodeList.selectedItems():
            nombre = entry.text()
            idx = self.listOfFields.index(nombre)
            domain['code'].append(self.listOfFieldsCode[idx])
        
        domain['desc'] = []
        for entry in self.targetDescList.selectedItems():
            nombre = entry.text()
            idx = self.listOfFields.index(nombre)
            domain['desc'].append(self.listOfFieldsCode[idx])
         
        domain['filter'] = self.targetFilterLineEdit.text()
         
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
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
        self.targetCodeList.clear()
        self.targetDescList.clear()
        self.targetCodeList.addItems(self.listOfFields)
        self.targetDescList.addItems(self.listOfFields) 

class WzLink(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzLink,self).__init__(parent)
        self.setFinalPage(True)
        
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        
        self.setTitle("Definición del enlace entre tablas")
        self.setSubTitle(""" Introduzca la definición del enlace entre la tabla base y la guía  """)

        joinTableLabel = QLabel("&Tabla de enlace")
        self.joinTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.joinTableCombo.addItems(self.listOfTables)
        self.joinTableCombo.setCurrentIndex(0)
        joinTableLabel.setBuddy(self.joinTableCombo)
        self.joinTableCombo.currentIndexChanged[int].connect(self.tablaElegida)

        joinFilterLabel = QLabel("&Filtro:")
        self.joinFilterLineEdit = QLineEdit()
        joinFilterLabel.setBuddy(self.joinFilterLineEdit)
        
        #TODO esto quedaria mejor con un WDataSheet 
        
        context=[]
        
        context.append(('c. base','condicion','c. enlace'))
        context.append((QComboBox,None,('',)+tuple(self.listOfFields)))
        context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        context.append((QComboBox,None,None))
        
        numrows=3
        
        self.joinClauseArray = WDataSheet(context,numrows)
        
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        self.joinClauseArray.resizeColumnToContents(0)
            
        meatLayout = QGridLayout()
        meatLayout.addWidget(joinTableLabel,0,0)
        meatLayout.addWidget(self.joinTableCombo,0,1)
        meatLayout.addWidget(joinFilterLabel,1,0)
        meatLayout.addWidget(self.joinFilterLineEdit,1,1)
        meatLayout.addWidget(self.joinClauseArray,2,0,1,2)
        self.setLayout(meatLayout)

        

    
    def initializePage(self):
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        #TODO no inicializa si no esta en la regla de produccion
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
        
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

    def tablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTablesCode[idx]
        self.listOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.listOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.targetCodeList.clear()
        self.targetDescList.clear()
        self.targetCodeList.addItems(self.listOfFields)
        self.targetDescList.addItems(self.listOfFields) 


class WzProdBase(QWizardPage):
    def __init__(self,parent=None,cube=None,cache=None):
        super(WzProdBase,self).__init__(parent)
        self.setFinalPage(True)
        
        self.iterations = 0
        self.cube = cube
        self.cache = cache
        
        tableArray = getAvailableTables(self.cube,self.cache)
        
        
        self.listOfTables = ['',] + [ item[1] for item in tableArray]
        self.listOfTablesCode = ['',] + [ item[0] for item in tableArray]
        self.listOfFields = []
        self.listOfFieldsCode = []
        self.listOfLinkFields = ['',] + [ item[1] for item in getFieldsFromTable(cache['tabla_ref'],self.cache,self.cube) ]
        self.listOfLinkFieldsCode = ['',] +  [ item[1] for item in getFieldsFromTable(cache['tabla_ref'],self.cache,self.cube) ]

        
        self.setTitle("Definición del dominio de la guía")
        self.setSubTitle(""" Introduzca la localización donde estan los valores por los que vamos a agrupar """)

        prodNameLabel = QLabel("&Nombre:")
        self.prodName = QLineEdit()
        prodNameLabel.setBuddy(self.prodName)
        self.prodName.setStyleSheet("background-color:khaki;")
 
        joinTableLabel = QLabel("&Tabla")
        self.joinTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.joinTableCombo.addItems(self.listOfTables)
        self.joinTableCombo.setCurrentIndex(0)
        joinTableLabel.setBuddy(self.joinTableCombo)
        self.joinTableCombo.currentIndexChanged[int].connect(self.tablaElegida)

        #
        guideFldLabel = QLabel("&Campo guia:")
        self.guidFldCombo = QComboBox()
        self.guidFldCombo.addItems(self.listOfFieldsCode)
        self.guidFldCombo.setEditable(True)
        guideFldLabel.setBuddy(self.guidFldCombo)
        self.guidFldCombo.currentIndexChanged[int].connect(self.campoElegido)
        self.guidFldCombo.setStyleSheet("background-color:khaki;")
 
        #
        guideDescLabel = QLabel("&Campo Descriptivo:")
        self.guideDescCombo = QComboBox()
        self.guideDescCombo.addItems(self.listOfFieldsCode)
        self.guideDescCombo.setEditable(True)
        guideDescLabel.setBuddy(self.guideDescCombo)
        self.guideDescCombo.currentIndexChanged[int].connect(self.campoElegido)

        #TODO algo para poder construir links complejos. Es necesario en la interfaz
        self.guideLinkLabel = QLabel("&Campo de enlace en \n" + cache['tabla_ref'].split('.')[-1])
        self.guideLinkLabel.setAlignment(Qt.AlignRight)
        self.guideLinkLabel.setWordWrap(True)  
        self.guideLinkCombo = QComboBox()
        self.guideLinkCombo.addItems(self.listOfLinkFieldsCode)
        self.guideLinkCombo.setEditable(True)
        self.guideLinkLabel.setBuddy(self.guideLinkCombo)
        self.guideLinkCombo.currentIndexChanged[int].connect(self.campoElegido)
        self.guideLinkCombo.setStyleSheet("background-color:khaki;")
        self.linkRB = QRadioButton("Con tablas intermedias")
        self.guideLinkLabel.hide()
        self.guideLinkCombo.hide()
        self.linkRB.hide()
        #
        sp_retain = self.guideLinkCombo.sizePolicy()
        sp_retain.setRetainSizeWhenHidden(True)
        self.guideLinkCombo.setSizePolicy(sp_retain)
        
        self.catCtorRB = QRadioButton("Agrupado en Categorias")
        self.caseCtorRB = QRadioButton("Directamente via código SQL")
        self.dateCtorRB = QRadioButton("Agrupaciones de fechas")
        
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
        meatLayout.addWidget(joinTableLabel,1,0)
        meatLayout.addWidget(self.joinTableCombo,1,1)
        meatLayout.addWidget(guideFldLabel,1,2)
        meatLayout.addWidget(self.guidFldCombo,1,3)
        meatLayout.addWidget(guideDescLabel,2,2)
        meatLayout.addWidget(self.guideDescCombo,2,3)
        meatLayout.addWidget(self.guideLinkLabel,3,0,1,2)
        meatLayout.addWidget(self.guideLinkCombo,3,2)
        meatLayout.addWidget(self.linkRB,3,3)
        meatLayout.addWidget(groupBox, 4, 0, 1, 4)

        #meatLayout.addWidget(self.joinClauseArray,2,0,1,2)
        self.setLayout(meatLayout)

        

    
    def initializePage(self):
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        #TODO no inicializa si no esta en la regla de produccion
        self.iterator = self.wizard().page(ixWzProdBase).iterations
        if isinstance(self.wizard().diccionario,(list,tuple)):
            #varias entradas
            self.midict = self.wizard().diccionario[self.iterator -1]
        else:
            self.midict = self.wizard().diccionario

        #vamos ahora al proceso de add
        #TODO si no esta en la lista
        pos = self.listOfTablesCode.index(self.cache['tabla_ref'])
        self.joinTableCombo.setCurrentIndex(pos)

    def nextId(self):
        return -1

    def validatePage(self):
        
        if self.isFinalPage() and self.iterator < self.wizard().prodIters:
            self.wizard().setStartId(ixWzProdBase);
            self.wizard().restart()        
            return False
        return True

    def tablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTablesCode[idx]
        self.listOfFields = [ item[1] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.listOfFieldsCode = [ item[0] for item in getFieldsFromTable(tabname,self.cache,self.cube) ]
        self.guidFldCombo.clear()
        self.guidFldCombo.addItems(self.listOfFields)
        self.guideDescCombo.clear()
        self.guideDescCombo.addItems(['',] + self.listOfFields)

        if tabname != self.cache['tabla_ref']:
            self.guideLinkLabel.show()
            self.guideLinkCombo.show()
            self.linkRB.show()
        #self.targetCodeList.clear()
        #self.targetDescList.clear()
        #self.targetCodeList.addItems(self.listOfFields)
        #self.targetDescList.addItems(self.listOfFields) 

    def campoElegido(self,idx):
        return 
    
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
        
        if tipo in ('guides','prod'): #== 'prod':
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
            self.setPage(ixWzDomain, WzDomain(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            
        texto_pantalla = obj.text() if obj.text() != tipo else obj.parent().text()
        self.setWindowTitle('Mantenimiento de ' + tipo + ' ' + texto_pantalla.split('.')[-1])
        self.show()
