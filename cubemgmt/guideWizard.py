#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from cubemgmt.cubetree  import *
from cubemgmt.cubeTypes import *
from cubemgmt.cubeutil  import *

from widgets import WDataSheet
from dialogs import propertySheetDlg
from PyQt5.QtWidgets import QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox

    
(ixWzBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzLink, ixWzJoin) = range(6) 

def guideWizard(exec_object,obj):
    """
    """
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    if not tipo:
        print('NO tiene tipo',obj.getDataList())
    
    isDirect = False
    isCategory = False
    isCase = False
    isDate = False
    isLink = False
    hasJoin = False
    wizard = CubeWizard(exec_object,obj)        
    if wizard.exec_() :
        guide = dict()
        if tipo == 'guides':
            guide['name']= wizard.field('resultDefault')
            guide['class']= GUIDE_CLASS[wizard.field('valueFormat') -1][0]
            guide['prod']=list()
            guide['prod'].append(dict())
            produccion = guide['prod'][-1]
            produccion['elem'] = wizard.page(ixWzBase).fieldArray[wizard.field('guideFld') - 1][0]        
        else:
            produccion = guide
        
        if tipo in ('guides','prod','domain'):
            isDirect = wizard.field('ctorDirect')
            isCategory = wizard.field('ctorCat')
            isCase = wizard.field('ctorCase')
            isDate = wizard.field('ctorDate')
            isLink = wizard.field('ctorLink')
        elif tipo in ('categories'):
            isCategory = True
            isDirect = isCase = isDate = isLink = False
            
        if isDirect :
            guide['class'] = 'o' 
        elif isCategory:
            prod = categoryClause(wizard)
            for item in prod :
                produccion[item] = prod[item]
            guide['class'] = 'c' 
            pass
        elif isCase:
            prod = getCaseStmt(wizard)
            for item in prod :
                produccion[item] = prod[item]
            pass
        elif isDate:
            guide['class']='d'
            produccion['fmt'] = 'date' #FIXME puede provocar probleas con otros formatos
            produccion['type']=getDateClause(wizard)
            
        elif isLink:
            prod = getLinkClause(wizard)
            for entry in prod:
                produccion[entry] = prod[entry]
        
        elif hasJoin:
            print('join')
            produccion['link via']=getJoinClause(wizard)
        else :
            return None
        pprint(guide)
        return guide
    else:
        return None


class CubeWizard(QWizard):
    def __init__(self,exec_object,obj):
        super(CubeWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.exec_object = exec_object
        self.obj = obj
        self.modelo = obj.model() # es necesario para que el delete no pierda la localizacion
        self.tipo = obj.type()
        self.jerarquia = obj.typeHierarchy()
        self.base = tree2dict(self.obj,isDictionaryEntry)
        
        if not self.tipo:   
            print('NO tiene tipo',obj.getDataList())

    
        if self.tipo in ('guides','prod','domain'):
            self.setPage(ixWzBase, WzBase(exec_object,obj))
            self.setPage(ixWzCategory, WzCategory(exec_object,obj))
            self.setPage(ixWzRowEditor, WzRowEditor(exec_object,obj))
            self.setPage(ixWzTime, WzTime(exec_object,obj))
            self.setPage(ixWzLink, WzLink(exec_object,obj))
            self.setPage(ixWzJoin, WzJoin(exec_object,obj))
        elif self.tipo in ('categories'):
            self.setPage(ixWzCategory, WzCategory(exec_object,obj))
            pass
        
        # TODO if domain elem should be gotten from actual value
        #      in categories, it should be loaded with existing categories
        self.setWindowTitle("Definición de guias")
        self.show()

class WzBase(QWizardPage):
    #FIXME no se si todo el bloqueo de fechas tenia sentido. Me temo que en SQLITE no
    def __init__(self,exec_object,obj,parent=None):
        super(WzBase,self).__init__(parent)
        #super().__init__(self,parent)
        self.exec_object = exec_object
        self.obj = obj
        
        self.setTitle("Definicion basica de la guía")
        self.setSubTitle(""" Introduzca el campo por el que desea agrupar los resultados y como determinar el texto asociado a los valores de estos campos""")
        valueFormatLabel = QLabel("&Tipo de guia:")
        self.valueFormatCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.valueFormatCombo.addItems([None , ] + [elem[1] for elem in GUIDE_CLASS ])
        self.valueFormatCombo.setCurrentIndex(1)
        valueFormatLabel.setBuddy(self.valueFormatCombo)
        
        #desactivo las jerarquias por defecto, de momento
        self.valueFormatCombo.model().item(3).setEnabled(False)
        self.valueFormatCombo.currentIndexChanged[int].connect(self.tipoElegido)

        resultDefaultLabel = QLabel("&Nombre:")
        self.resultDefaultLineEdit = QLineEdit()
        resultDefaultLabel.setBuddy(self.resultDefaultLineEdit)
        #TODO el campo debe de ser editable. Como actuar ver en editaCombo
        guideFldLabel = QLabel("&Campo guia:")
        self.guidFldCombo = QComboBox()
        self.fieldArray = getFldTable(self.exec_object,self.obj)
        comboArray = [None , ] + [ '{}  ({})'.format(item[1],item[2]) for item in self.fieldArray]
        self.guidFldCombo.addItems(comboArray)
        guideFldLabel.setBuddy(self.guidFldCombo)
        
        self.guidFldCombo.currentIndexChanged[int].connect(self.campoElegido)

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

        self.registerField('valueFormat', self.valueFormatCombo)
        self.registerField('resultDefault*', self.resultDefaultLineEdit)
        self.registerField('guideFld*', self.guidFldCombo)
        self.registerField('ctorDirect',self.directCtorRB)
        self.registerField('ctorCat',self.catCtorRB)
        self.registerField('ctorCase',self.caseCtorRB)
        self.registerField('ctorDate',self.dateCtorRB)
        self.registerField('ctorLink',self.linkCtorRB)
        
        layout = QGridLayout()
        layout.addWidget(valueFormatLabel, 0, 0)
        layout.addWidget(self.valueFormatCombo, 0, 1)
        layout.addWidget(resultDefaultLabel, 1, 0)
        layout.addWidget(self.resultDefaultLineEdit, 1, 1)
        layout.addWidget(guideFldLabel, 2, 0)
        layout.addWidget(self.guidFldCombo, 2, 1)
        layout.addWidget(groupBox, 3, 0, 1, 2)
        self.setLayout(layout)

    def nextId(self):

        if self.directCtorRB.isChecked():
            # Fin de todo
            return -1 #ixWzJoin
        elif self.catCtorRB.isChecked():
            return ixWzCategory
        elif self.caseCtorRB.isChecked():
            return ixWzRowEditor
        elif self.dateCtorRB.isChecked():
            return ixWzTime
        elif self.linkCtorRB.isChecked():
            return ixWzLink
        else:
            return -1
        
    def tipoElegido(self,ind):
        # control parcial tipo y cosas que se pueden hacer.
        # el tipo se normalizara al generar el arbol
        if   ind in (0,1,3): # nomral jerarquia
            self.directCtorRB.setChecked(True)
        elif ind == 2: # categorias
            self.catCtorRB.setChecked(True)
        elif ind == 4: #fecha
            self.dateCtorRB.setChecked(True)
            
    def campoElegido(self,ind):
        formato = self.fieldArray[ind - 1][2]
        print(self.fieldArray[ind -1][1],formato)
        if formato in ('fecha','fechahora'):
#                self.dateCtorRB.setDisabled(False)
            self.dateCtorRB.setChecked(True)
        else:
            self.tipoElegido(self.valueFormatCombo.currentIndex()) 
            
class WzCategory(QWizardPage):
    #TODO con esta sintaxis puede incluirse el critero de LIKE. Falta en core
    def __init__(self,exec_object,obj,parent=None):
        super(WzCategory,self).__init__(parent)
        self.exec_object = exec_object
        self.obj = obj
        
        self.setFinalPage(True)
        
        self.setTitle("Definicion de categorias")
        self.setSubTitle("Utilice la tabla para determinar los valores\n"
            "<RESULTADO> <operacion (por defecto IN> <lista de valores, separada por comas>")
        

        Formatos = [ item[1] for item in ENUM_FORMAT ]
        
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
    
        context=[]
        
        context.append(('categoria','condicion','valores'))
        context.append((QLineEdit,None,None))
        context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        context.append((QLineEdit,None,None))
        numrows,self.data = self.loadData()
        self.catArray = WDataSheet(context,numrows)
        self.catArray.fill(self.data)
    
    
        layout = QGridLayout()
        layout.addWidget(catValueFormatLabel,0,0)
        layout.addWidget(self.catValueFormatCombo,0,1)
        layout.addWidget(catResultFormatLabel,1,0)
        layout.addWidget(self.catResultFormatCombo,1,1)
        layout.addWidget(self.catArray, 2, 0, 1, 2)
        layout.addWidget(catResultDefaultLabel,8,0)
        layout.addWidget(self.catResultDefaultLine,8,1)
        self.setLayout(layout)
        #FIXME ¿de verdad no se pueden usar?
        #self.setCentralWidget(self.editArea)
        self.registerField('catResultFormat', self.catResultFormatCombo)
        self.registerField('catValueFormat', self.catValueFormatCombo)
        self.registerField('catResultDefault', self.catResultDefaultLine)
        self.registerField('catArray',self.catArray)
        
        self.loadData()

    def initializePage(self): 
        print('paso por aqui')
        self.wizard().setOptions(QWizard.HaveCustomButton1)
        self.setButtonText(QWizard.CustomButton1,'Mas entradas')
        self.wizard().customButtonClicked.connect(self.addEntry)

        if self.obj.type() == 'categories':
            # necesito hacer este horror
            formatDict = dict()
            for k,item in enumerate(ENUM_FORMAT):
                formatDict[item[0]] = k
            
            pai = self.obj
            while pai.type() != 'prod':
                pai = pai.parent()
            formV = pai.getChildrenByName('fmt')
            if formV:
                formato = formV.getColumnData(1)
                self.catValueFormatCombo.setCurrentIndex(formatDict.get(formato,0))
            formR = pai.getChildrenByName('enum_fmt')
            if formR:
                formato = formR.getColumnData(1)
                self.catResultFormatCombo.setCurrentIndex(formatDict.get(formato,0))
        else: 
            campo=self.wizard().field('guideFld')            
            datosCampo = getFldTable(self.exec_object,self.obj)[campo -1]
            formato = datosCampo[2]
            print(campo,'==>',datosCampo)
            if formato in ('numerico','entero'):
                self.catValueFormatCombo.setCurrentIndex(1) 
            elif formato in ('fecha','fechahora'):
                self.catValueFormatCombo.setCurrentIndex(2)
            else:
                self.catValueFormatCombo.setCurrentIndex(0)
    
    def loadData(self):         
        data = None
        additionalRecords = 3
        if self.obj.type() == 'categories': # es un update
            if self.obj.text() == self.obj.type(): # estamos en la cabecera
                pos = self.obj
            else:
                pos =self.obj.parent()
            numrows = pos.rowCount() + additionalRecords 
            data = []
            for k in range(pos.rowCount()):
                tuple = []
                item = pos.child(k)
                if item.getChildrenByName('default'):
                    additionalRecords += 1
                    self.catResultDefaultLine.setText(item.getChildrenByName('default').getColumnData(1))
                    continue
                tuple.append(item.getChildrenByName('result').getColumnData(1))
                tuple.append(LOGICAL_OPERATOR.index(item.getChildrenByName('condition').getColumnData(1)))
                tuple.append(norm2String(item.getChildrenByName('values').getChildrenValuesAsList(1)))
                data.append(tuple)
            for k in range(additionalRecords ):
                data.append([None,0,None])
        else:
            numrows=5
            data = [ [None,0,None] for k in range(numrows) ]
            
        return numrows,data 
    def nextId(self):
        return -1

    def addEntry(self,buttonId):
        #FIXME da algunos problemas de presentacion ¿Bug upstream?
        if buttonId == QWizard.CustomButton1:
            count = self.catArray.rowCount()
            self.catArray.insertRow(count)
            self.catArray.addRow(count)
            self.catArray.setCurrentCell(count,0)

class WzRowEditor(QWizardPage):
    def __init__(self,exec_object,obj, parent=None):
        super(WzRowEditor,self).__init__(parent)
        self.exec_object = exec_object
        self.obj = obj
        

        self.setFinalPage(True)
        #super().__init__(self,parent)
        self.setTitle("Definicion de sentencias")
        self.setSubTitle(""" Utilice el espacio para escribir la sentencias SQL que deseee """)
        
        #FIXME no admite mandatory
        self.editArea = QPlainTextEdit()
        #self.editArea.textChanged.connect(self.validatePage)
        self.registerField('sqlEdit',self.editArea)
        
        layout = QGridLayout()
        layout.addWidget(self.editArea, 0, 0, 1, 2)
        self.setLayout(layout)
        #FIXME ¿de verdad no se pueden usar?
        #self.setCentralWidget(self.editArea)

    def nextId(self):
        return -1

class WzTime(QWizardPage):
    #TODO no se si core admite una sintaxis tan sofistica
    # ¿Sólo presentar si la variable es fecha, o dejar a eleccion del usuario -con SQLITE no queda mas remedio-
    def __init__(self, exec_object,obj ,parent=None):
        super(WzTime,self).__init__(parent)
        self.exec_object = exec_object
        self.obj = obj
        

        self.setFinalPage(True)
        #super().__init__(self,parent)
        self.setTitle("Definicion por fechas")
        self.setSubTitle("Defina una jerarquía de intervalos temporales por los que romper")

        self.Formatos = [ item[1] for item in FECHADOR ]

        self.MaxLevel = 4  
        self.formFechaLabel = [None for k in range(self.MaxLevel)]
        self.formFechaCombo = [None for k in range(self.MaxLevel)]
        
        for k in range(self.MaxLevel):
            self.defItemComboBox(k)

        layout = QGridLayout()
        for k in range(self.MaxLevel):
            layout.addWidget(self.formFechaLabel[k],k,0)
            layout.addWidget(self.formFechaCombo[k],k,1)
        self.setLayout(layout)
        #FIXME ¿de verdad no se pueden usar?
        #self.setCentralWidget(self.editArea)

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

        self.registerField('formFecha{}'.format(k), self.formFechaCombo[k])
        
        
    def seleccion(self,idx):
        #TODO sería mas interesante pasar tambien el valor, pero sigo sin acertar
        if idx < 0:
            return 
        captura = self.formFechaCombo[idx].currentIndex()
        for k in range(idx +1,self.MaxLevel):
            
            if captura >= (self.formFechaCombo[idx].count() -1 ):
                self.formFechaLabel[k].hide()
                self.formFechaCombo[k].hide()
            else:
                self.formFechaCombo[k].blockSignals(True)  #no veas el loop en el que entra si no
                if not self.formFechaCombo[k].isVisible():
                    self.formFechaLabel[k].show() #por lo de arriba
                    self.formFechaCombo[k].show()
                self.formFechaCombo[k].clear()
                self.formFechaCombo[k].addItems(['',] + self.Formatos[captura + k :])
                self.formFechaCombo[k].blockSignals(False)  
    def nextId(self):
        return -1

class WzLink(QWizardPage):
    """
        table    QComboBox 
        filter   QListItem
        code 1+  QListWidget
        desc 1+  idm
        *
        a checkbox to send to link
        *link via
            table
            filter
            clause +1
            rel_elem
            base_elem
            condition
        *grouped_by (que ya no me acuerdo ni que significa
    """
    def __init__(self, exec_object,obj ,parent=None):
        super(WzLink,self).__init__(parent)
        self.exec_object = exec_object
        self.obj = obj
        

        self.setFinalPage(True)
        #super().__init__(self,parent)
        self.setTitle("Definicion de tabla relacionada")
        self.setSubTitle("Defina la tabla y atributos a traves de la cual obtendra los valores de la guía")
        
        self.listOfTables = ['',] + getListAvailableTables(self.obj,self.exec_object)
        self.listOfFields = []
        
        targetTableLabel = QLabel("&Tabla origen:")
        self.targetTableCombo = QComboBox()
        #MARK VERY CAREFULLY. If has default value, DON'T make it mandatory in wizard
        #                     Use a null value in combos if mandatory
        self.targetTableCombo.addItems(self.listOfTables)
        self.targetTableCombo.setCurrentIndex(0)
        targetTableLabel.setBuddy(self.targetTableCombo)
        self.targetTableCombo.currentIndexChanged[int].connect(self.tablaElegida)

        targetFilterLabel = QLabel("&Filtro:")
        self.targetFilterLineEdit = QLineEdit()
        targetFilterLabel.setBuddy(self.targetFilterLineEdit)
        

        targetCodeLabel = QLabel("&Clave de enlace:")
        self.targetCodeList = QListWidget()
        targetCodeLabel.setBuddy(self.targetCodeList)
        self.targetCodeList.setSelectionMode(QListWidget.ExtendedSelection)

        targetDescLabel = QLabel("&Textos desciptivos:")
        self.targetDescList = QListWidget()
        targetDescLabel.setBuddy(self.targetDescList)
        self.targetDescList.setSelectionMode(QListWidget.ExtendedSelection)

        linkLabel = QLabel("¿Requiere de un enlace externo?")
        self.linkCheck = QCheckBox()
        linkLabel.setBuddy(self.linkCheck)
        self.linkCheck.stateChanged.connect(self.estadoLink)
        
        layout = QGridLayout()
        layout.addWidget(targetTableLabel,0,0)
        layout.addWidget(self.targetTableCombo,0,1)
        layout.addWidget(targetFilterLabel,1,0)
        layout.addWidget(self.targetFilterLineEdit,1,1)
        layout.addWidget(targetCodeLabel,2,0)
        layout.addWidget(self.targetCodeList,2,1)
        layout.addWidget(targetDescLabel,3,0)
        layout.addWidget(self.targetDescList,3,1)
        layout.addWidget(linkLabel,4,0)
        layout.addWidget(self.linkCheck,4,1)
        self.setLayout(layout)
        #FIXME ¿de verdad no se pueden usar?
        #self.setCentralWidget(self.editArea)
        self.registerField('targetTable', self.targetTableCombo)
        self.registerField('targetFilter', self.targetFilterLineEdit)
        self.registerField('targetCode',self.targetCodeList)
        self.registerField('targetDesc',self.targetDescList)

    def nextId(self):
        #if not self.linkCheck.isChecked():
            #return -1 
        #else:
            return ixWzJoin
        
    def estadoLink(self,idx):
        if self.linkCheck.isChecked():
            self.setFinalPage(False)
        else:
            self.setFinalPage(True)
            
    def tablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTables[idx]
        self.listOfFields = [ item[0] for item in getFldTable(self.exec_object,self.obj,tabname) ]
        self.targetCodeList.clear()
        self.targetDescList.clear()
        self.targetCodeList.addItems(self.listOfFields)
        self.targetDescList.addItems(self.listOfFields) 
    
    def initializePage(self): 
        print('paso por aqui')
        
class WzJoin(QWizardPage):
    """
        *link via
            table
            filter
            clause +1
            rel_elem
            base_elem
            condition
        *grouped_by (que ya no me acuerdo ni que significa
    """
    #FIXME nombres de los campos 
    def __init__(self, exec_object,obj ,parent=None):
        super(WzJoin,self).__init__(parent)
        self.exec_object = exec_object
        self.obj = obj
        

        self.setFinalPage(True)
        #super().__init__(self,parent)
        self.setTitle("Definicion del enlace")
        self.setSubTitle("Definimos la tabla de enlace entre datos y guia \n. Si su .modeo requiere mas de un enlace, por favor edite a mano a partir del segundo")
        
        self.listOfTables = ['',] + getListAvailableTables(self.obj,self.exec_object)
        
        pai = self.obj.parent()
        while pai and pai.type() != 'base':
            pai = pai.parent()
        baseItem = childByName(pai,'table')
        self.listOfFieldsBase = [ item[0] for item in getFldTable(self.exec_object,baseItem) ]
        
        self.listOfFieldsRel = []
        
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
        context.append((QComboBox,None,('',)+tuple(self.listOfFieldsBase)))
        context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        context.append((QComboBox,None,None))
        
        numrows=3
        
        self.joinClauseArray = WDataSheet(context,numrows)
        
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,1).setCurrentIndex(3) #la condicion de igualdad
        self.joinClauseArray.resizeColumnToContents(0)
            
        layout = QGridLayout()
        layout.addWidget(joinTableLabel,0,0)
        layout.addWidget(self.joinTableCombo,0,1)
        layout.addWidget(joinFilterLabel,1,0)
        layout.addWidget(self.joinFilterLineEdit,1,1)
        layout.addWidget(self.joinClauseArray,2,0,1,2)
        self.setLayout(layout)
        #FIXME ¿de verdad no se pueden usar?
        #self.setCentralWidget(self.editArea)
        self.registerField('joinTable', self.joinTableCombo)
        self.registerField('joinFilter', self.joinFilterLineEdit)
        self.registerField('joinClauseArray',self.joinClauseArray)

    def nextId(self):
        return -1 
        
            
    def tablaElegida(self,idx):
        print('Algo encuentra',idx)
        tabname = self.listOfTables[idx]
        self.listOfFieldsRel = [ item[0] for item in getFldTable(self.exec_object,self.obj,tabname) ]
        for k in range(self.joinClauseArray.rowCount()):
            self.joinClauseArray.cellWidget(k,2).clear()
            self.joinClauseArray.cellWidget(k,2).addItems(['',]+self.listOfFieldsRel)
        #self.joinDescList.clear()
        #self.joinDescList.addItems(self.listOfFieldsRel)





def categoryClause(wizard):
    result = dict()
    result['fmt']=ENUM_FORMAT[wizard.field('catValueFormat')] [0]
    result['enum_fmt']=ENUM_FORMAT[wizard.field('catResultFormat')] [0]
    result['categories']=list()
    if wizard.field('catResultDefault') != '':
        result['categories'].append({"default":wizard.field('catResultDefault') })
    tabla = wizard.page(ixWzCategory).catArray
    for i in range(tabla.rowCount()):
        if tabla.get(i,0) == '' and tabla.get(i,2) == '':
            continue
        resultValue = tabla.get(i,0)
        condition = LOGICAL_OPERATOR[tabla.get(i,1)]
        values = tabla.get(i,2).split(',')
        #TODO comprobar que no son necesarios formateos
        #FIXM que hago con los decimales
        result['categories'].append({"result":resultValue,"condition":condition,"values":values})
    return result

def getCaseStmt(wizard):
    result = dict()
    result['case_sql']=wizard.page(ixWzRowEditor).editArea.document().toPlainText()
    result['class'] = 'c'
    return result

def getDateClause(wizard):
    print('fecha')
    #TODO no todas las opciones son posibles ahora mismo con este codigo (no cuatrimestres, no trimestres, no quincenas)
    #es solo cuestion de tirar codigo
    secuencia = ''
    for k,entry in enumerate(wizard.page(ixWzTime).formFechaCombo):
        if entry.isHidden():
            break
        if k == 0:
            print(FECHADOR[entry.currentIndex()])
            secuencia = FECHADOR[entry.currentIndex()][0]
        else:
            print(FECHADOR[entry.currentIndex() -1])
            secuencia += FECHADOR[entry.currentIndex() -1][0]
    return secuencia
    
def getLinkClause(wizard): 
    print('link')
    result=dict()
    result['domain']=dict()
    #self.registerField('targetTable', self.targetTableCombo)
    result['domain']['table'] = wizard.page(ixWzLink).targetTableCombo.currentText()
    result['domain']['filter'] = wizard.field('targetFilter')
    result['domain']['code'] = [ item.text() for item in wizard.page(ixWzLink).targetCodeList.selectedItems() ]
    result['domain']['desc'] = [ item.text() for item in wizard.page(ixWzLink).targetDescList.selectedItems() ]
    if wizard.page(ixWzLink).linkCheck.isChecked():
        print('join')
        result['link via']=getJoinClause(wizard)
    return result

def getJoinClause(wizard):
    result=list()
    tabla = wizard.page(ixWzJoin).joinTableCombo.currentText()
    filter = wizard.field('joinFilter') 
    array = wizard.page(ixWzJoin).joinClauseArray
    clausulas = list()
    for i in range(array.rowCount()):
        if array.get(i,0) == 0 and array.get(i,2) == 0:
            break
        base = array.cellWidget(i,0).currentText() #array.get(i,0)
        condition = LOGICAL_OPERATOR[array.get(i,1)]
        related = array.cellWidget(i,0).currentText() #array.get(i,2)
        if condition == '=':
            clausulas.append({"base_elem":base,"rel_elem":related,})
        else:
            clausulas.append({"base_elem":base,"rel_elem":related,"condition":condition})
    result.append({"table":tabla,"clause":clausulas,"filter":filter})
    return result
