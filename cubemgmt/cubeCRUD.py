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
    
    
def editTableElem(exec_object,obj,valor,refTable=None):
    lista = getFldTable(exec_object,obj,refTable)
    if lista:
        array = [ (item[0],item[1],)  for item in lista ]
        result = editaCombo(obj,array,valor)
        return result
    else:
       return None
    ##TODO determinar que es lo que necesito hacer cuando no esta disponible
    ##TODO  Unificar con la de abajo
    ##TODO base elem probablemente trasciende esta definicion
    ##TODO calcular dos veces FQ ... es un exceso. simplificar
    #FQtablaArray,connURL = getCubeTarget(obj)
    #if refTable:
        #FQtablaArray = FQName2array(refTable.getColumnData(1))
    ##print(FQtablaArray,connURL)
    #actConn = connMatch(exec_object.dataDict,connURL)
    #if actConn:
        #tableItem = actConn.findElement(FQtablaArray[1],FQtablaArray[2])
        #if tableItem:
            #fieldIdx = childByName(tableItem,'FIELDS')
            ##array = getDataList(fieldIdx,0)
            #array = [ (item.fqn(),item.text(),)  for item in fieldIdx.listChildren() ]
            #result = editaCombo(obj,array,valor)
            #return result
        #else:
            #print(connURL,'ESTA DISPONIBLE y el fichero NOOOOOR')
    #else:
        #print(connURL,'NO ESTA A MANO')
    #return None

def editaCombo(obj,valueTable,valorActual):
    descriptivo = False
    if isinstance(valueTable[0],(list,tuple,set)):
        descriptivo = True
        comboList = [ item[1] for item in valueTable ]
        claveList = [ str(item[0]) for item in valueTable ]
    else:
        claveList = comboList = tuple(valueTable)
    if descriptivo and valorActual:
        try:
            values = [ claveList.index(valorActual), ]
        except ValueError:
            comboList.append(valorActual)
            claveList.append(valorActual)
            values = [ len(claveList) -1 ]
    elif descriptivo:
        values = [ None , ]
    else:
        values = [ valorActual, ]

    spec = []
    spec.append(('Seleccione',QComboBox,{'setEditable':True},comboList))

    parmDialog = propertySheetDlg('Defina '+obj.text(),spec,values)
    if parmDialog.exec_():
        #print(values[0],parmDialog.sheet.cellWidget(0,0).currentText())
        if descriptivo:
            if parmDialog.sheet.cellWidget(0,0).currentText() != comboList[values[0]]:
                return parmDialog.sheet.cellWidget(0,0).currentText()
            else:
                return claveList[values[0]] 
        else:
            return parmDialog.sheet.cellWidget(0,0).currentText()  #pues no lo tengo tan claro
    


def atomicEditAction(obj,valor,exec_object):
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()

    result = None
    if tipo in FREE_FORM_ITEMS:
        text = QInputDialog.getText(None, "Editar:"+obj.text(),obj.text(), QLineEdit.Normal,obj.getColumnData(1))
        result = text[0]

    elif tipo in STATIC_COMBO_ITEMS:
        array = STATIC_COMBO_ITEMS[tipo]
        result = editaCombo(obj,array,valor)

    elif tipo in DYNAMIC_COMBO_ITEMS:
        print('Edit dynamic',obj,tipo,valor)
        array = []
        if tipo == 'cubo':
            array = getCubeList(exec_object.hiddenRoot)
            result = editaCombo(obj,array,valor)
        #TODO adaptar a  getCubeInfo
        elif tipo in ('row','col'):
            pai = obj.parent()
            if pai.type() == 'vista':
                cubeItem = pai.getBrotherByName('cubo')
                #print (pai.text(),cubeItem.text(),cubeItem.getColumnData(1))
                cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                guidemaster = childByName(cubo,'guides')
                nombres = getItemList(guidemaster,'guides')
                
                array = [ (k,nombres[k]) for k in range(len(nombres)) ]
                result = editaCombo(obj,array,valor)

            #TODO el else deberia dar un error y no ignorarse
        elif tipo in ('elemento',):
            pai = obj.parent()
            if pai.type() == 'vista':
                cubeItem = pai.getBrotherByName('cubo')
                cubo = childByName(exec_object.hiddenRoot,cubeItem.getColumnData(1))
                guidemaster = childByName(cubo,'fields')
                
                array = getDataList(guidemaster,1) 
                result = editaCombo(obj,array,valor)

        elif tipo in ('table',):
            #TODO modificar esto lo destroza todo en teoría.
            #Acepto cualquier tabla en la conexion actual, no necesariamente el esquema
            array = getListAvailableTables(obj,exec_object)
            result = editaCombo(obj,array,valor)
            #print('El resultado de andar por el combo es',result)
                
        elif tipo in ('elem','base_elem','fields'):
            #TODO base_elem no tiene esta base, ojala
            result = editTableElem(exec_object,obj,valor,None)
                
        elif tipo in ('code','desc','grouped_by'):
            refTable = obj.getBrotherByName('table')
            
            result = editTableElem(exec_object,obj,valor,refTable)

        elif tipo in ('rel_elem'):
            pai = obj.parent()
            while pai.type() and pai.type() != 'link via':
                pai = pai.parent()
            refTable  = childByName(pai,'table')
            
            result = editTableElem(exec_object,obj,valor,refTable)

        else:
            print('Edit dynamic sin regla',obj,tipo,valor)
    else:
        print('Edit sin regla',obj,tipo,valor)
    return result

def addDefault(obj,exec_object):
    #TODO cuando existe default cargar valores como defecto
    #print('Procesar Default')
    spec_d = []
    parray=[]
    listCubes=['', ]+getCubeList(exec_object.hiddenRoot) 
    def getContext(idx):
        """
            La funcion esta embebida para poder mantener el contexto (exec_object en concreto)
        """
        cubo = childByName(exec_object.hiddenRoot,listCubes[idx])
        guias,campos = getCubeInfo(cubo)
        for k in range(1,5):
            parmDialog_d.sheet.cellWidget(k,0).setEnabled(True)
            if k == 1:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(guias)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
            elif k == 2:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(guias)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
            elif k == 4:
                parmDialog_d.sheet.cellWidget(k,0).clear()
                items = tuple(campos)
                parmDialog_d.sheet.cellWidget(k,0).addItems(items)
                
    spec_d.append(('Seleccione el cubo a utilizar',QComboBox,None,tuple(listCubes)))
    spec_d.append(('Guia filas',QComboBox,{'setEnabled':False},tuple(parray)),)
    spec_d.append(('Guia columnas',QComboBox,{'setEnabled':False},tuple(parray)),)
    spec_d.append(('Función agregacion',QComboBox,{'setEnabled':False},tuple(AGR_LIST)),)
    spec_d.append(('Campo de datos',QComboBox,{'setEnabled':False},tuple(parray)),)
    values_d = [ None for k in range(len(spec_d))]
    parmDialog_d = propertySheetDlg('Defina el cubo a generar',spec_d,values_d,exec_object)
    parmDialog_d.sheet.cellWidget(0,0).currentIndexChanged[int].connect(getContext)
    
    if parmDialog_d.exec_():
        defaultBase = childByName(exec_object.hiddenRoot,'default')
        if defaultBase:
            defaultBase.suicide()
        defaultBase = exec_object.hiddenRoot
        defaultBase.insertRow(0,(CubeItem(str('default')),CubeItem(str('')),CubeItem(str('default_base')),))
        padre = defaultBase.child(0)
        dato =parmDialog_d.sheet.cellWidget(0,0).currentText()
        padre.appendRow((CubeItem(str('cubo')),CubeItem(str(dato)),CubeItem(str('cubo')),))
        padre.appendRow((CubeItem(str('vista')),CubeItem(str('')),CubeItem(str('vista')),))
        vista = padre.lastChild()
        vista.appendRow((CubeItem(str('col')),CubeItem(str(values_d[1])),CubeItem(str('col')),))
        vista.appendRow((CubeItem(str('row')),CubeItem(str(values_d[2])),CubeItem(str('row')),))
        dato =parmDialog_d.sheet.cellWidget(3,0).currentText()
        vista.appendRow((CubeItem(str('agregado')),CubeItem(str(dato)),CubeItem(str('agregado')),))
        dato =parmDialog_d.sheet.cellWidget(4,0).currentText()
        vista.appendRow((CubeItem(str('elemento')),CubeItem(str(dato)),CubeItem(str('elemento')),))
    
def setContextMenu(obj,menu,exec_object=None):
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()

    obj.menuActions = []
    obj.menuActions.append(menu.addAction("Add ",lambda:execAction(exec_object,obj,"add")))
    obj.menuActions.append(menu.addAction("Edit ",lambda :execAction(exec_object,obj,"edit")))
    obj.menuActions.append(menu.addAction("Delete ",lambda: execAction(exec_object,obj,"delete")))
    obj.menuActions.append(menu.addAction("Copy ",lambda: execAction(exec_object,obj,"copy")))
    obj.menuActions.append(menu.addAction("Rename ",lambda: execAction(exec_object,obj,"rename")))
    obj.menuActions.append(menu.addAction("Refresh ",lambda: execAction(exec_object,obj,"refresh")))
    
    if tipo in NO_ADD_LIST:
        obj.menuActions[0].setEnabled(False)


    if tipo not in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) and tipo not in STATIC_COMBO_ITEMS  :
        obj.menuActions[1].setEnabled(False)
    if tipo in ('fields','case_sql') and obj.text() == tipo and obj.hasChildren():
        obj.menuActions[1].setEnabled(False)
        
    if tipo in NO_ADD_LIST:
        obj.menuActions[2].setEnabled(False)
    #elif tipo in TYPE_LIST_DICT and obj.text() == tipo:
        #obj.menuActions[-1].setEnabled(False)

    obj.menuActions[3].setEnabled(False)

    if obj.text() in ITEM_TYPE or obj.text() == "":
        obj.menuActions[4].setEnabled(False)

    if tipo in COMPLEX_TYPES :
        obj.menuActions[5].setEnabled(True)
    else:
        obj.menuActions[-1].setEnabled(False)


        """
        FREE_FORM_ITEMS = set([
            -'base filter'# on base add
            *'case_sql',
            -'dbhost',    # on base add
            -'dbname',    # on base add
            -'dbpass',    # on base add
            -'dbuser',    # on base add
            -'default',   # created on default/ base add
            u'filter',    # free text
            #u'name',      # free text
            u'result',    # free text
            *'values',
            ])
        STATIC_COMBO_ITEMS = dict({
            - 'agregado': created on default
            u'class': GUIDE_CLASS ,
            u'condition': LOGICAL_OPERATOR,
            u'driver': DRIVERS,
            u'enum_fmt': ENUM_FORMAT,
            u'fmt': ENUM_FORMAT,
            u'type': TIPO_FECHA,
            })

        DYNAMIC_COMBO_ITEMS = set([
            *'base_elem', #             field of  Reference  table
            *'code',      #             field of FK table (key)
            -'col',       # created on default
            -'cubo',      # created on default
            *'desc',       #             field of FK table (values)
            *'elem',      #              field of table, or derived value 
            -'elemento',  # created on default
            *'fields',
            *'grouped by',#              field of FK table or derived value ??
            *'rel_elem',  #              field of FK table
            -'row',       # created on default
            u-'table',    #on base add
            ])

        """
        
def guideWizard(exec_object,obj):
    """
    """
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    if not tipo:
        print('NO tiene tipo',obj.getDataList())
    
    (ixWzBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzLink, ixWzJoin) = range(6) 


    class WzBase(QWizardPage):
        #FIXME no se si todo el bloqueo de fechas tenia sentido. Me temo que en SQLITE no
        def __init__(self,parent=None):
            super(WzBase,self).__init__(parent)
            #super().__init__(self,parent)
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
            self.fieldArray = getFldTable(exec_object,obj)
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
            # control parcial de tipo y cosas que se pueden hacer.
            # el tipo se normalizara al generar el arbol
            if   ind in (0,1,3): # nomral y jerarquia
#                self.directCtorRB.setDisabled(False)
                self.directCtorRB.setChecked(True)
                #self.catCtorRB.setDisabled(False)
                #self.catCtorRB.setChecked(False)
                #self.caseCtorRB.setDisabled(False)
                #self.caseCtorRB.setChecked(False)
                #self.dateCtorRB.setDisabled(True)
                #self.dateCtorRB.setChecked(False)
                #self.linkCtorRB.setDisabled(False)
                #self.linkCtorRB.setChecked(True)
            elif ind == 2: # categorias
                #self.directCtorRB.setDisabled(True)
                #self.directCtorRB.setChecked(False)
                #self.catCtorRB.setDisabled(False)
                self.catCtorRB.setChecked(True)
                #self.caseCtorRB.setDisabled(False)
                #self.caseCtorRB.setChecked(False)
                #self.dateCtorRB.setDisabled(True)
                #self.dateCtorRB.setChecked(False)
                #self.linkCtorRB.setDisabled(True) #de momento
                #self.linkCtorRB.setChecked(False)
            elif ind == 4: #fecha
                #self.directCtorRB.setDisabled(True)
                #self.directCtorRB.setChecked(False)
                #self.catCtorRB.setDisabled(True)
                #self.catCtorRB.setChecked(False)
                #self.caseCtorRB.setDisabled(False)
                #self.caseCtorRB.setChecked(False)
                #self.dateCtorRB.setDisabled(False)
                self.dateCtorRB.setChecked(True)
                #self.linkCtorRB.setDisabled(True) #de momento
                #self.linkCtorRB.setChecked(False)
                
                
        def campoElegido(self,ind):
            formato = self.fieldArray[ind - 1][2]
            print(self.fieldArray[ind -1][1],formato)
            if formato == 'fecha':
#                self.dateCtorRB.setDisabled(False)
                self.dateCtorRB.setChecked(True)
            else:
               self.tipoElegido(self.valueFormatCombo.currentIndex()) 
                
    class WzCategory(QWizardPage):
        #TODO con esta sintaxis puede incluirse el critero de LIKE. Falta en core
        def __init__(self, parent=None):
            super(WzCategory,self).__init__(parent)
            self.setFinalPage(True)
            #super().__init__(self,parent)
            self.setTitle("Definicion de categorias")
            self.setSubTitle("Utilice la tabla para determinar los valores\n"
                "<RESULTADO> <operacion (por defecto IN> <lista de valores, separada por comas>")
            
            
            #wizard.setOptions(QWizard.HaveCustomButton1)
            #self.setButtonText(QWizard.CustomButton1,'Mas entradas')
            #wizard.customButtonClicked.connect(self.addEntry)
            #FIXME no admite mandatory

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
    
        
            context=[]
            
            context.append(('categoria','condicion','valores'))
            context.append((QLineEdit,None,None))
            context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
            context.append((QLineEdit,None,None))
            
            numrows=5
            self.catArray = WDataSheet(context,numrows)

     
            catResultDefaultLabel = QLabel("Resultado por &Defecto:")
            self.catResultDefaultLine = QLineEdit()
            catResultDefaultLabel.setBuddy(self.catResultDefaultLine)
     
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

        def initializePage(self):            
            self.wizard().setOptions(QWizard.HaveCustomButton1)
            self.setButtonText(QWizard.CustomButton1,'Mas entradas')
            self.wizard().customButtonClicked.connect(self.addEntry)


            campo=self.wizard().field('guideFld')
            datosCampo = getFldTable(exec_object,obj)[campo -1]
            pprint(getFldTable(exec_object,obj))
            print(campo,'==>',datosCampo)
            if datosCampo[2] in ('numerico','entero'):
                self.catValueFormatCombo.setCurrentIndex(1) 
            elif datosCampo[2] == 'fecha':
                self.catValueFormatCombo.setCurrentIndex(2)
            else:
                self.catValueFormatCombo.setCurrentIndex(0)

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
        def __init__(self, parent=None):
            super(WzRowEditor,self).__init__(parent)
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
        def __init__(self, parent=None):
            super(WzTime,self).__init__(parent)
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
        def __init__(self, parent=None):
            super(WzLink,self).__init__(parent)
            self.setFinalPage(True)
            #super().__init__(self,parent)
            self.setTitle("Definicion de tabla relacionada")
            self.setSubTitle("Defina la tabla y atributos a traves de la cual obtendra los valores de la guía")
            
            self.listOfTables = getListAvailableTables(obj,exec_object)
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
            self.listOfFields = [ item[0] for item in getFldTable(exec_object,obj,tabname) ]
            self.targetCodeList.clear()
            self.targetDescList.clear()
            self.targetCodeList.addItems(self.listOfFields)
            self.targetDescList.addItems(self.listOfFields)
            
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
        def __init__(self, parent=None):
            super(WzJoin,self).__init__(parent)
            self.setFinalPage(True)
            #super().__init__(self,parent)
            self.setTitle("Definicion del enlace")
            self.setSubTitle("Definimos la tabla de enlace entre datos y guia \n. Si su modelo requiere mas de un enlace, por favor edite a mano a partir del segundo")
            
            self.listOfTables = getListAvailableTables(obj,exec_object)
            
            pai = obj.parent()
            while pai and pai.type() != 'base':
                pai = pai.parent()
            baseItem = childByName(pai,'table')
            self.listOfFieldsBase = [ item[0] for item in getFldTable(exec_object,baseItem) ]
            
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
            self.listOfFieldsRel = [ item[0] for item in getFldTable(exec_object,obj,tabname) ]
            for k in range(self.joinClauseArray.rowCount()):
                self.joinClauseArray.cellWidget(k,2).clear()
                self.joinClauseArray.cellWidget(k,2).addItems(['',]+self.listOfFieldsRel)
            #self.joinDescList.clear()
            #self.joinDescList.addItems(self.listOfFieldsRel)
            

    wizard = QWizard(exec_object)
    wizard.setPage(ixWzBase, WzBase())
    wizard.setPage(ixWzCategory, WzCategory())
    wizard.setPage(ixWzRowEditor, WzRowEditor())
    wizard.setPage(ixWzTime, WzTime())
    wizard.setPage(ixWzLink, WzLink())
    wizard.setPage(ixWzJoin, WzJoin())
    
    wizard.setWindowTitle("Definición de guias")
    wizard.show()

    if wizard.exec_() :
        guide = dict()
        guide['name']= wizard.field('resultDefault')
        guide['class']= GUIDE_CLASS[wizard.field('valueFormat') -1][0]
        guide['prod']=list()
        guide['prod'].append(dict())
        produccion = guide['prod'][-1]
        produccion['elem'] = wizard.page(ixWzBase).fieldArray[wizard.field('guideFld') - 1][0]        
        if wizard.field('ctorDirect') :
            guide['class'] = 'o'
        elif wizard.field('ctorCat'):
            print('categorias')
            guide['class'] = 'c'
            produccion['fmt']=ENUM_FORMAT[wizard.field('catValueFormat')] [0]
            produccion['enum_fmt']=ENUM_FORMAT[wizard.field('catResultFormat')] [0]
            produccion['categories']=list()
            if wizard.field('catResultDefault') != '':
                produccion['categories'].append({"default":wizard.field('catResultDefault') })
            tabla = wizard.page(ixWzCategory).catArray
            for i in range(tabla.rowCount()):
                if tabla.get(i,0) == '' and tabla.get(i,2) == '':
                    break
                result = tabla.get(i,0)
                condition = LOGICAL_OPERATOR[tabla.get(i,1)]
                values = tabla.get(i,2).split(',')
                #TODO comprobar que no son necesarios formateos
                #FIXM que hago con los decimales
                produccion['categories'].append({"result":result,"condition":condition,"values":values})
            pass
        elif wizard.field('ctorCase'):
            produccion['case_sql']=wizard.page(ixWzRowEditor).editArea.document().toPlainText()
            produccion['class'] = 'c'
            pass
        elif wizard.field('ctorDate'):
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
            guide['class']='d'
            produccion['fmt'] = 'date' #FIXME puede provocar probleas con otros formatos
            guide['type']=secuencia
            
            pass
            
        elif wizard.field('ctorLink'):
            print('link')
            produccion['domain']=dict()
            #self.registerField('targetTable', self.targetTableCombo)
            produccion['domain']['table'] = wizard.page(ixWzLink).targetTableCombo.currentText()
            produccion['domain']['filter'] = wizard.field('targetFilter')
            produccion['domain']['code'] = [ item.text() for item in wizard.page(ixWzLink).targetCodeList.selectedItems() ]
            produccion['domain']['desc'] = [ item.text() for item in wizard.page(ixWzLink).targetDescList.selectedItems() ]
            #self.registerField('targetFilter', self.targetFilterLineEdit)
            #self.registerField('targetCode',self.targetCodeList)
            #self.registerField('targetDesc',self.targetDescList)
            if wizard.page(ixWzLink).linkCheck.isChecked():
                print('join')
                produccion['link via']=list()
                tabla = wizard.page(ixWzJoin).joinTableCombo.currentText()
                filter = wizard.field('joinFilter') 
                array = wizard.page(ixWzJoin).joinClauseArray
                clausulas = list()
                for i in range(array.rowCount()):
                    if array.get(i,0) == '' and array.get(i,2) == '':
                        break
                    base = array.get(i,0)
                    condition = LOGICAL_OPERATOR[array.get(i,1)]
                    related = array.get(i,2)
                    if condition == '=':
                        clausulas.append({"base_elem":base,"rel_elem":related,})
                    else:
                        clausulas.append({"base_elem":base,"rel_elem":related,"condition":condition})
                produccion['link via'].append({"table":tabla,"clause":clausulas,"filter":filter})
                #self.registerField('joinTable', self.joinTableCombo)
                #self.registerField('joinFilter', self.joinFilterLineEdit)
                #self.registerField('joinClauseArray',self.joinClauseArray)

            pass
        else :
            return None
        pprint(guide)
        return guide
    else:
        return None

def execAction(exec_object,obj,action):
    #TODO listas editables en casi todos los elementos
    if action is None:
        return
    
    modelo = obj.model() # es necesario para que el delete no pierda la localizacion
    tipo = obj.type()
    jerarquia = obj.typeHierarchy()
    if not tipo:
        print('NO tiene tipo',obj.getDataList())
    modelo.beginResetModel()
    if action ==  'add' :
        print('Add by',obj)
        #TODO deberia capturarse duplicados en la lista existente
        #FIXME no entiendo el porque los valors de un listbox tienen que venir en forma de tuple()
        if tipo in ('base','default_start'):
            #TODO la lista de ficheros deberia obviar los esquemas del sistema
            spec = []
            spec.append(('Intruduzca el nombre del nuevo cubo',None,None,))
            array=getListAvailableTables(obj,exec_object)
            spec.append(('Seleccione la tabla a utilizar',QComboBox,None,tuple(array)))
            values = [ None for k in range(len(spec))]
            parmDialog = propertySheetDlg('Defina el cubo a generar',spec,values,exec_object)
            if parmDialog.exec_():
                if values[0] :
                    if values[0].lower() == 'default':
                        addDefault(obj,exec_object)
                    else:
                        print('Proceso de alta')
                        #FIXME todo este proceso para obtener el nombre de la conexion es un poco tremebundo
                        FQtablaArray,connURL = getCubeTarget(obj)
                        actConn = connMatch(exec_object.dataDict,connURL)
                        connName = actConn.text()
                        tabla = array[values[1]].split('.')
                        schemaName= tabla[0] if len(tabla) > 1 else ''
                        tableName = tabla[1] if len(tabla) > 1 else tabla[0]
                        info = info2cube(exec_object.dataDict,connName,schemaName,tableName)
                        for key in info:
                            clave = key
                            break
                        recTreeLoader(exec_object.hiddenRoot,values[0],info[clave],'base')

            pass
        #elif tipo == 'fields'  no porque lo definimos como elemento libre
        elif tipo in ('guides',):
            #print(tipo,obj.text(),obj.getRow())
            # aqui el proceso del objeto
            result = guideWizard(exec_object,obj)
            if not result:
                return
            #TODO lo de abajo es lo que deberia ejecutar
            
            if obj.text() != tipo:
                #add a new array entry
                idx = obj.index()
                pai = obj.parent()
            else:
                pai = obj
            nombre = result.get('name',pai.rowCount())
            recTreeLoader(pai,nombre,result,tipo)
            
        elif tipo in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) or tipo in STATIC_COMBO_ITEMS  :
            result = atomicEditAction(obj,None,exec_object)
            #TODO repasar el grouped_by
            if tipo in ('fields','elem','code','desc','base_elem','rel_elem','grouped_by','case_sql','values'):
                if not obj.text():
                    #ya es un array; solo hay que añadir elementos
                    idx = obj.index()
                    pai = obj.parent()
                    pai.insertRow(idx.row()+1,(CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                elif not obj.getColumnData(1):
                    #hablamos del padre. Solo hay que añadir un hijo
                    obj.appendRow((CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                    pass
                else: # <code> : <valor>
                    #creo un elemento array hijo copiado del actual
                    #borro el contenido del original
                    #creo un nuevo registro
                    #FIXME esto deberia hacerse con takeRow
                    oldRecord = [ CubeItem(obj.getColumnData[k]) for k in range(1,obj.columnCount()) ]
                    #print(obj.columnCount())
                    #pprint(oldRecord)
                    oldRecord.insert(0,CubeItem(None))
                    #pprint(oldRecord)
                    obj.appendRow((CubeItem(None),CubeItem(obj.getColumnData(1)),CubeItem(obj.getColumnData(2))))
                    obj.appendRow((CubeItem(None),CubeItem(str(result)),CubeItem(tipo)))
                    obj.setColumnData(1,None,Qt.EditRole)
                    pass
            pass

        else:
            print('Se escapa',obj,tipo)
        pass  # edit item, save config, refresh tree
    elif action == 'edit':
        if tipo in   ( FREE_FORM_ITEMS | DYNAMIC_COMBO_ITEMS ) or tipo in STATIC_COMBO_ITEMS  :
            valor = obj.getColumnData(1)
            result = atomicEditAction(obj,valor,exec_object)
            if result and result != valor:
                obj.setColumnData(1,result,Qt.EditRole) 
        else:
            print('Se escapa',obj,tipo)
        pass  # edit item, save config, refresh tree
    elif action == 'delete' :
        if obj.type() == 'base': #no puedo borrarlo pero si vaciarlo, es un probleam de logica. ver cubebrowewin.close()
            indice = obj.index()
            while obj.hasChildren():
                obj.model().item(indice.row()).removeRow(0)
            obj.setEnabled(False)
        else:
            obj.suicide()
        pass  # close connection, delete tree, delete config
    elif action == 'copy':
        print('copy ',obj)
        pass
    elif action == 'rename':
        print('rename',obj)
        text = QInputDialog.getText(None, "Renombrar el nodo :"+obj.text(),"Nodo", QLineEdit.Normal,obj.text())
        obj.setData(text[0],Qt.EditRole)
        for item in obj.listChildren():
            if item.text() == 'name':
                print('procedo')
                item.setColumnData(1,text[0],Qt.EditRole)
                break
                
    elif action == 'refresh':
        print('refresh',obj)
        pass
    else:
        print('Action ',action,' desconocida')
        pass
    modelo.endResetModel()
 


