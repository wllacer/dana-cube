#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Acciones pendientes
Necesarias
    create group boxes for optical effect
Mejoras
    manual link
        #DONE posibilidad de boton de vuelta atras (sencillamente revertir self.structure)    
        #DONE cuando es un automatico fustrado reenviar la structure generada a manual
        #DONE Integrar como opcion de edicion
    auto link
    Comunes
        #FIXME me parece que aparecen mas relaciones de la cuenta
        #FIXME falta comprobar el caso con varios campos en la foreign key en automatico
        #unificar codigo
        #TODO simplificar de Link via a  domain + link_via ¿o no?
        #TODO ¿Convertir self.sheet a WDelegateSheet? ON HOLD hasta que ataque los widgets
        #TODO  filter de QLineEdit a QPlainTextEdit ¿?

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from support.gui.widgets import *
from support.util.record_functions import norm2List,norm2String

from PyQt5.QtCore import Qt,QSize,pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, \
      QCheckBox,QPushButton,QLineEdit,QVBoxLayout,QHBoxLayout

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QMenu, QComboBox, QStyledItemDelegate, QLabel, QDialogButtonBox, QLineEdit,QSizePolicy,QHeaderView,QPlainTextEdit

from support.gui.treeEditor import *
from admin.cubemgmt.cubeTreeUtil import *


"""

Ahora vienen funciones para gestionar la creacion semi automatica de guias con relaciones con otras tablas

"""
def addNetworkMenuItem(*lparms):
    """
    aqui incluyo las opciones de menu para las guias. ¿Deberia separarlo?
    """
    item = lparms[0]
    view = lparms[1]
    menuStruct = lparms[2]
    menu = lparms[3]
    text = lparms[4]
    n,i,t=getRow(item)
    print('ANMI',n.data())
    if n.data() == 'guides':
        menuStruct.append(menu.addAction(text,lambda i=item,j=view:addNetworkPath(i,j)))
    else:
        menuStruct.append(menu.addAction('Ver conjunto de prueba',lambda i=lparms:sampleData(*lparms)))
        classItem = getChildByType(item,'class')
        if classItem:
            clase = getRow(classItem)[1].data()
        else:
            clase = 'o'
        if clase == 'd':
            menuStruct.append(menu.addAction('Añadir agrupaciones especiales por fecha',lambda i=lparms:addDateGroups(*lparms)))




def addNetworkPath(*lparm):
    """
    Accion de menu para la creacion de guias con relaciones.
    Deriva a manual o FK internas
    
    """
    item = lparm[0]
    view = lparm[1]
    # me fascina como obtener los datos
    baseTableItm = getChildByType(getParentByType(item,'base'),'table')
    baseTable = baseTableItm.parent().child(baseTableItm.row(),1).data()
    
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    schema = getSchema(item,baseTable)
    fqtable = schema + '.' + baseTable.split('.')[-1]  #solo por ir seguro
    
    relHandler = relCatcher(item,view,confName,schema)
    arbolNavegacion  = relHandler.get(baseTable)
    #tableDdItem = _getDictTable(view.dataDict,confName,schema,baseTable)
    #arbolNavegacion = getFKLinks(tableDdItem)
    
    if not arbolNavegacion:
        #gparm = lparm[:]
        manualNetwork(*lparm,confName=confName,schema=schema,fqtable=fqtable,rel=relHandler)
    else:
        FKNetwork(*lparm,confName=confName,schema=schema,fqtable=fqtable,rel=relHandler)
      

def manualNetwork(*lparm,**kwparm):
    """
    
    Gestiona el dialogo para crear relaciones manualmente
    
    """
    item = lparm[0]
    view = lparm[1]
    fqtable = kwparm.get('fqtable')
    tables = srcTables(*lparm)
    gparm = list(lparm)
    if len(gparm) > 2:
        gparm[3] = tables
    else:
        gparm.append(tables)
    fieldGetter = fieldCatcher(*gparm)
    
    if 'rel' in kwparm:
        relGetter = kwparm['rel']
    else:
        confName = kwparm.get('confName')
        schema = kwparm.get('schema')
        relGetter = relCatcher(item,view,confName,schema)
        
    selDlg = LinksDlg(pfile=fqtable.split('.')[-1],tablas=tables,fields=fieldGetter,rel=relGetter)
    selDlg.show
    if selDlg.exec_():
        prod = selDlg.result.get('structure')
        guia = {'name':prod.get('name'),'class':'o','prod':[prod,] }
        dict2tree(item,None,guia,'guides')
        uch = item.child(item.rowCount() -1)
        uch.setData(prod['name'],Qt.EditRole)
        uch.setData(prod['name'],Qt.UserRole +1)

def FKNetwork(*lparm,**kwparm):
    """
    
    Gestiona el dialogo para crear relaciones exclusivamente con FKs existentes.
    Opcionalmente permite derivar a la forma manual
    
    """
    item = lparm[0]
    view = lparm[1]
    fqtable = kwparm.get('fqtable')
    relHandler = kwparm.get('rel')

    gparm = list(lparm)
    tables = srcTables(*lparm)
    if len(gparm) > 2:
        gparm[3] = tables
    else:
        gparm.append(tables)
    fieldGetter = fieldCatcher(*gparm)

    selDlg = FKNetworkDialog(fqtable,fieldGetter,relHandler)
    selDlg.show()
    if selDlg.exec_():
        if not selDlg.manual:
            dict2tree(item,None,selDlg.result,'guides')
            uch = item.child(item.rowCount() -1)
            uch.setData(selDlg.result['name'],Qt.EditRole)
            uch.setData(selDlg.result['name'],Qt.UserRole +1)
        else:
            confName = kwparm.get('confName')
            schema = kwparm.get('schema')
            manualNetwork(*lparm,confName=confName,schema=schema,fqtable=fqtable)

"""    
GETTERS
    executed at start of SetEditorData 
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist 
    input
            editor,
            item,
            view,
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)
    output
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)

SETTERS
    executed at the end of SetModelData
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist
        input  *lparm
            item = lparm[0]
            view = lparm[1]
            context = lparm[2]   Fundamentalmente para obtener el valor original context['data']
            ivalue / values = lparm[3]
            dvalue = lparm[4]
        output
            item, the edited item
"""
def getLinks(*lparm):
    editor = lparm[0]
    item = lparm[1]
    view = lparm[2]
    dato = lparm[3]
    display = lparm[4]
    
    # determino el tipo de informacion que voy a pasar como estructura
    context = Context(item)
    item = item.parent().child(item.row(),0)  #normalizo la posicion del item
    tipo = context['editType']
    head = context['repeteable']
    instance = context['repeatInstance']
    if tipo == 'link via':
        headItem = getParentByType(item,'prod')
        structure = tree2dict(headItem,isDictFromDef)
        #pprint(structure)
        #exit()
    else:
        print('Se disparo aqui',tipo)
    #determino la informacion contextual para el dialogo
    baseTableItm = getChildByType(getParentByType(item,'base'),'table')
    baseTable = baseTableItm.parent().child(baseTableItm.row(),1).data()
    
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    schema = getSchema(item,baseTable)

    #Instancio los getters 
    relGetter = relCatcher(item,view,confName,schema)
    gparm = [item,view,None]
    tables = srcTables(*gparm)
    gparm[2] = tables
    fieldGetter = fieldCatcher(*gparm)

    environ = {'pfile':baseTable.split('.')[-1],'tablas':tables,'fields':fieldGetter,'rel':relGetter,'tipo':tipo,'headItem':headItem,
                        'structure':structure }
    
    return environ,display

def setLinks(*lparm):
    item = lparm[0]
    view = lparm[1]
    context = lparm[2]  
    values = lparm[3]
    if not values:
        return item
    if 'cancel' in values:
            return item
    head = values['headItem']
    for k in range(head.rowCount()):
        head.model().removeRow(0,head.index())

    dict2tree(head,None,values['structure'],'prod',direct=True)
    head.setData(values['structure'].get('name',head.data(Qt.DisplayRole)),Qt.DisplayRole)
    return item
    


class fieldDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.tableFrom = None
        self.tableTo = None
        self.tempTables = []
        self.fields = None
        self.sheet = self.parent()#.clauseSheet
        
        
    def createEditor(self,parent,option,index):
        """
        A parte de crear las listas, realmente estoy creando un cache para poder ahorrarme construcciones de lista
        
        """
        # al inicializarlo en el dialogo tengo este problema
        
        if not self.tempTables:
            self.tempTables = [None,('=','>','<','>=','<=','!='),None]
        if self.sheet.context.get('fieldCatcher') and self.fields != self.sheet.context.get('fieldCatcher'):
            self.tempTables[0] = None
            self.tempTables[2] = None
            self.fields = self.sheet.context.get('fieldCatcher')
       
        if self.tableFrom != self.sheet.context.get('tableFrom') or not self.tempTables[0]:
            self.tableFrom = self.sheet.context.get('tableFrom')
            self.tempTables[0] = self.fields.get(self.tableFrom)
        if self.tableTo != self.sheet.context.get('tableTo') or not self.tempTables[2]:
            self.tableTo = self.sheet.context.get('tableTo')
            self.tempTables[2] = self.fields.get(self.tableTo)

        editor = QComboBox(parent)
        editor.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        
        if index.column() == 0:
            editor.addItems(self.tempTables[0])
        elif index.column() == 1:
            editor.addItems(self.tempTables[1])
        elif index.column() == 2:
            editor.addItems(self.tempTables[2])
       
        return editor
    
    def setEditorData(self, editor, index):
        if index.data():
            pos = self.tempTables[index.column()].index(index.data())
            editor.setCurrentIndex(pos)
        else:
            if index.column() == 1:
                editor.setCurrentIndex(0)
            else:
                editor.setCurrentIndex(-1)
        
    def setModelData(self,editor,model,index):
            idx = editor.currentIndex()
            if idx < 0:
                model.setData(index,None)
            else:
                model.setData(index,self.tempTables[index.column()][idx])
    
class tablesDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.tables = None
        
    def createEditor(self,parent,option,index):
        self.tables = self.parent().tables #TODO adecuar a la estructura de datos
        if index.row() == 0:
            return super().createEditor(parent,option,index)
        editor = QComboBox(parent)
        editor.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        return editor
    def setEditorData(self, editor, index):
        if index.row() == 0:
            return super().setEditorData(editor,index)
        editor.addItems(self.tables)   #TODO adecuar a la estructura de datos
        if index.data():
            pos = self.tables.index(index.data())
            editor.setCurrentIndex(pos)
        else:
            editor.setCurrentIndex(-1)
            
    def setModelData(self,editor,model,index):
        #TODO con la estructura real debe ser mas complejo
        if index.row() == 0:
            return super().setModelData(editor,model,index)
        if editor.currentIndex() == -1:
            return
        nuevo = editor.currentText()
        if nuevo == index.data():
            return 
        model.setData(index,nuevo)
    
            

class LinksDlg(QDialog):
    def __init__(self,parent=None,**kwparm): #pfile,tablas,fields,rel,structure=None,parent=None,):
        super().__init__(parent)
        self.defaultData = kwparm
        self.name = QLineEdit()  #lo necesito antes de los valores iniciales :-(    
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.msgLine = QLabel()
        nameLbl = QLabel('Nombre de la guia')

        
        sheetLbl = QLabel('Camino de enlace')
        self.sheet = QTableWidget(5,1)        
        makeTableSize(self.sheet)
        self.sheet.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sheet.customContextMenuRequested.connect(self.openContextMenu)
        delegate = tablesDelegate(self)
        self.sheet.setItemDelegate(delegate)

        internalLbl=QLabel('O Eliga una relacion interna')
        self.internalLink = QComboBox()
        clauseLbl = QLabel('Eliga la condicion de enlace entre las tablas')
        self.clauseWgt = WSheet(5,3,fieldDelegate)
        #self.setClauseWgtSize()
        fieldsTargetLbl = QLabel('Escoga los campos por los que desee agrupar')
        self.fieldsTarget = WMultiList(format='c',cabeceras=('De ','Campos de agrupacion'))
        
        filterLbl = QLabel('Escriba un filtro SQL adicional')
        self.filter = QLineEdit()
        
        detail = QVBoxLayout()

        detail.addWidget(nameLbl)
        detail.addWidget(self.name)
        detail.addWidget(clauseLbl)
        detail.addWidget(self.clauseWgt)
        detail.addWidget(internalLbl)
        detail.addWidget(self.internalLink)
        detail.addWidget(filterLbl)
        detail.addWidget(self.filter)
        detail.addWidget(fieldsTargetLbl)
        detail.addWidget(self.fieldsTarget)

        
        meatlayout =QGridLayout()

        meatlayout.addWidget(self.sheet,1,0)
        meatlayout.addLayout(detail,0,1,8,1)
        meatlayout.addWidget(self.msgLine,9,0,1,2)
        meatlayout.addWidget(buttonBox,10,1)
        
        self.setLayout(meatlayout)
        
        #self.initialValues(**kwparm)
        #self.initializeSheet(self.fileStack)
        #self.disableDetail()
        # en esta posicion para que las señales se activen tras la inicializacion
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        self.internalLink.currentIndexChanged.connect(self.linkUpdated)
        self.sheet.currentItemChanged.connect(self.moveSheetSel)
        self.sheet.itemChanged.connect(self.itemChanged)
        self.initialValues(**kwparm)        
        
    def initialValues(self,**kwparm): #file,tablas,fields,rel,structure):pfile,tablas,fields,rel,structure=None,parent=None,):
        if not kwparm:
            return 
        else:
            self.sheet.currentItemChanged.disconnect()
            self.sheet.itemChanged.disconnect()
            self.disableDetail()            
            file = kwparm.get('pfile')
            tablas = kwparm.get('tablas',[])
            fields = kwparm.get('fields')
            rel = kwparm.get('rel')
            structure = kwparm.get('structure',{})

            self.fullTables = tablas
            self.tables = [ elem[1] for elem in tablas ]
            
            iidx = self.tables.index(file)
            self.baseTable = self.fullTables[iidx][0]
            self.fields = fields
            self.rel = rel
            if not structure:
                self.structure = {}
            else:
                if 'prod' in structure:
                    self.structure = structure['prod'][0]
                else:
                    self.structure = structure
            
            self.name.setText(self.structure.get('name',""))
            self.array = self.denorm([ elem for elem in self.structure.get('link via',[])])
            #self.fileStack =  [file, ] + [ elem.get('table') for elem in self.array ]
            self.fileStack =  [file, ] + [ elem.get('table').split('.')[-1] for elem in self.array if elem.get('table')]
            for k in range(len(self.array)):
                line = self.array[k]
                line['internalLink'] = None
                if 'table' in line:
                    del line['table']
            if self.array:
                self.targetTable = self.fileStack[-1]
                self.targetFields = self.denorm(norm2List(self.structure.get('elem')))
            else:
                self.targetTable= None
                self.targetFields = []

        self.initializeSheet(self.fileStack)
        if len(self.array) >= 1:
            pos = len(self.fileStack) -1
            self.sheet.setCurrentCell(pos,0)
            self.loadDetail(pos)
            #self.loadTarget()
            self.enableDetail()    

        self.setClauseWgtSize()
        self.sheet.currentItemChanged.connect(self.moveSheetSel)
        self.sheet.itemChanged.connect(self.itemChanged)

    
    def initializeCell(self,x,y):
        self.sheet.setItem(x,y,QTableWidgetItem(""))
 
    def initializeSheet(self,file):
        for i in range(self.sheet.rowCount()):
            for j in range(self.sheet.columnCount()):
                self.initializeCell(i,j)
        self.sheet.setItemPrototype(QTableWidgetItem(''))
        if file:
            for idx,elem in enumerate(norm2List(file)):
                #self.sheet.setItem(idx,0,QTableWidgetItem(None))
                self.sheet.item(idx,0).setText(elem)
                if idx == 0:
                    self.sheet.item(idx,0).setFlags( Qt.ItemIsEnabled )
                    self.sheet.item(idx,0).setBackground(QColor(Qt.gray))
        if self.actualSize() >= 1:
            self.loadTarget()
            self.fieldsTarget.setEnabled(True)
            
        else:
            self.fieldsTarget.setEnabled(False)
    """
        sheet status change
    """
    def moveSheetSel(self,current,previous):
        if not previous:
            return
        self.unloadDetail(previous.row())
        #esto es para que cuando en entra en linea nueva no haga cargas inutiles
        if self.sheet.item(current.row(),0).text() == "":
            return
        self.loadDetail(current.row())
        
        
    def itemChanged(self,item):
        self.changeDetail(item)
        self.updateTarget(item)
        
    def updateTarget(self,item):    
        if item.row() == self.actualSize():
            if item.text() != self.targetTable:
                self.targetTable =  item.text()
                self.loadTarget()
                self.fieldsTarget.setEnabled(True)
        
        #pass
    """
        context menu actions
    """
    def openContextMenu(self,position):
        item = self.sheet.itemAt(position)
        row = item.row()
        if row == 0:
            return
        
        menu = QMenu()
        menu.addAction("Insert row before",lambda i=row:self.addRow(i))
        menu.addAction("Insert row after",lambda i=row:self.addRow(i +1))
        menu.addAction("Append row",self.addRow)
        menu.addSeparator()
        menu.addAction("Remove",lambda i=row:self.removeRow(i))
        
        action = menu.exec_(self.sheet.viewport().mapToGlobal(position))
                
    def addRow(self,idx=None):
        if not idx:
            idx =self.actualSize() +1
        self.sheet.insertRow(idx)
        for j in range(self.sheet.columnCount()):
                self.initializeCell(idx,j)
        ind = idx -1
        self.array.insert(ind,{'clause':[],'internalLink':None,'filter':""})
        self.resetVecinos(ind)
        
        item = self.sheet.item(idx,0)
        self.sheet.setCurrentItem(item)
        self.updateTarget(self.sheet.item(self.actualSize(),0))
        self.sheet.setFocus()

        
    def removeRow(self,idx=None):
        if not idx:
            return
        self.sheet.removeRow(idx)
        ind = idx -1
        self.resetVecinos(ind)
        del self.array[ind]
        self.sheet.setCurrentItem(self.sheet.item(idx -1,0))
        self.updateTarget(self.sheet.item(self.actualSize(),0))
        self.sheet.setFocus()
        
    def resetVecinos(self,ind):
        anterior = ind -1
        if anterior >= 0:
            self.resetArrayEntry(anterior)
        posterior = ind +1
        if posterior <= self.actualSize():
            self.resetArrayEntry(posterior)
        
    def clearDetail(self):
            self.internalLink.clear()
            self.clauseWgt.clear()
            self.filter.setText("")

    def disableDetail(self):
            self.internalLink.setEnabled(False)
            self.clauseWgt.setEnabled(False)
            self.filter.setEnabled(False)
            
    def enableDetail(self):
            self.internalLink.setEnabled(True)
            self.clauseWgt.setEnabled(True)
            self.filter.setEnabled(True)

    def actualSize(self):
        maxpos = -1
        for  k in range(self.sheet.rowCount()):
            if self.sheet.item(k,0).text() != '':
                maxpos = k
        return maxpos
    
    def resetArrayEntry(self,ind):
        if ind >= len(self.array):
            for j in range(len(self.array),ind +1):
                self.array.append({})
        self.array[ind]['clause']=[]
        self.array[ind]['internalLink'] = None
        self.array[ind]['filter'] = ""
    
    def loadDetail(self,idx):
        self.clearDetail()
        if idx == 0:
            self.disableDetail()
            return 
        self.enableDetail()
        ind = idx -1
        if ind >= len(self.array):
            for j in range(len(self.array),ind +1):
                self.array.append({})
                
        tableFrom = self.sheet.item(ind,0).text()
        tableTo = self.sheet.item(idx,0).text()
        
        if not tableFrom or not tableTo:
            return
        initialData = []
        for elem in self.array[ind].get('clause',[]):
            initialData.append((elem['base_elem'],elem.get('condition','='),elem['rel_elem']))
        if initialData:
            self.internalLink.setEnabled(False)
        self.clauseWgt.setContext(initialData,tableFrom=tableFrom,tableTo=tableTo,fieldCatcher=self.fields)
        self.clauseWgt.setHorizontalHeaderLabels(('Desde  {:25}'.format(tableFrom),
                                                            'op',
                                                           'Hacia   {:25}'.format(tableTo)
                                                           ))
        relList = self.rel.prettyList(tableFrom,tableTo)

        if relList == []:
            self.internalLink.setEnabled(False)
        else:
            self.internalLink.setEnabled(True)
        relList = ['Manual',]+relList
        self.internalLink.currentIndexChanged.disconnect()   #no quiero que la carga moleste 
        self.internalLink.addItems(relList)
        initialLink = self.array[ind].get('internalLink')
        if initialLink:
            self.internalLink.setCurrentIndex(relList.index(initialLink))
            self.fieldsFrom.setEnabled(False)
            self.fieldsTo.setEnabled(False)
        else:
            self.internalLink.setCurrentIndex(-1)
        self.internalLink.currentIndexChanged.connect(self.linkUpdated)    
        
        self.filter.setText(self.array[ind].get('filter',''))
     
    def loadTarget(self):
        if self.targetTable:
            fieldsTarget = self.fields.get(self.targetTable)
            self.fieldsTarget.load(self.fields.get(self.targetTable,[]),self.targetFields)
            self.fieldsTarget.origenCabecera.setText('De '+self.targetTable)
        
    def changeDetail(self,item):
        idx = item.row()
        if idx == 0:
            return
        ind = idx -1
        self.resetArrayEntry(ind)
        self.loadDetail(idx)
        
    def unloadDetail(self,idx):
        #FIXME puede ser un buen momento para restaurar los prefijos (o no)
        if idx == 0:
            return
        ind = idx -1
        if ind >= len(self.array):
            return
        iLink = self.internalLink.currentIndex()
        if iLink < 1: #no hay link
            self.array[ind]['internalLink'] = None
            data = self.clauseWgt.unloadData()
            clause = []
            for linea in data:
                if not linea[0] or not linea[2]:
                    continue
                if not linea[1] or linea[1] == '=':
                    clause.append({'base_elem':linea[0],'rel_elem':linea[2]})
                else:
                    clause.append({'base_elem':linea[0],'condition':linea[1],'rel_elem':linea[2]})
            self.array[ind]['clause'] = clause
        else:
            self.array[ind]['internalLink'] = self.internalLink.currentText()
            self.array[ind]['clause'] = []
        self.array[ind]['filter'] = self.filter.text()
            
    def linkUpdated(self,idx):
        if idx < 1:  #no elegí
            self.clauseWgt.setEnabled(True)
        else:
            self.clauseWgt.setEnabled(False)
     
    def validateArray(self):
        self.msgLine.setText("")
        if not self.name.text():
            self.msgLine.setText('El nombre es obligatorio')
            self.name.setFocus()
            return False
        numfiles = self.actualSize()
        for ind in range(numfiles):
            entrada = self.array[ind]
            if not entrada.get('clause') and not entrada.get('internalLink'):
                self.msgLine.setText('Esta entrada esta incompleta')
                self.sheet.setCurrentItem(self.sheet.item(ind +1,0))
                self.loadDetail(ind +1)
                self.clauseWgt.setFocus()
                return False
            elif entrada.get('clause'):
                for clausula in entrada.get('clause'):
                    if not clausula.get('base_elem') or not clausula.get('rel_elem'):
                        self.msgLine.setText('Desde y A deben tener el mismo número de campos)')
                        self.loadDetail(ind +1)
                        self.clauseWgt.setFocus()
                        return False
            elif len(self.fieldsTarget.seleList) == 0:
                self.msgLine.setText('Debe especificar al menos un campo para agrupar')
                self.fieldsTarget.setFocus()
                return False
        return True
            
    def accept(self):
        #descargo lo ultimo editado
        cItem = self.sheet.currentItem().row()
        self.unloadDetail(cItem)
        datos = self.getData()
        if not datos:
            return 
        else:
            self.result = datos
        super().accept()
      
    def short2long(self,tabla):
        if '.' in tabla:
            return tabla
        intIdx = self.tables.index(tabla)
        return self.fullTables[intIdx][0]
    
    def linkTransform(self,ind,tablas):
        entrada = self.array[ind]
        tablaOrig = tablas[ind -1] if ind > 0 else self.baseTable
        tablaDest = tablas[ind]
        return dictLinkDef2dict(self.rel,entrada['internalLink'],tablaOrig,tablaDest,self.fields,self.short2long)
    
    def clauseTransform(self,ind,tablas):
        entrada = self.array[ind]
        tablaOrig = tablas[ind -1] if ind > 0 else self.baseTable
        tablaDest = tablas[ind]
        resultado = {}
        resultado['table'] = tablaDest
        clausulas = []
        #else:
        for clausula in entrada.get('clause'):
            clausulas.append({'base_elem':self.fields.tr(tablaOrig,clausula.get('base_elem'))
                                        ,'rel_elem':self.fields.tr(tablaDest,clausula.get('rel_elem'))
                                        }
                                        )
            if clausula.get('condition'):
                clausulas[-1]['condition'] = clausula.get('condition')
        resultado['clause']=clausulas
        resultado['filter'] = entrada.get('filter')
        return resultado
            
    def setClauseWgtSize(self):
        self.clauseWgt.setHorizontalHeaderLabels((' Desde  {:25}'.format(self.baseTable),
                                                    'op',
                                                    ' Hacia   {:25}<'.format(self.targetTable if self.targetTable else "")
                                                    ))
        size = self.clauseWgt.size()
        totalwidth = size.width()
        self.clauseWgt.setColumnWidth(0,totalwidth * 38 // 100)
        self.clauseWgt.setColumnWidth(1,totalwidth * 10 // 100)
        self.clauseWgt.setColumnWidth(2,totalwidth * 38 // 100)

    """
    para convertirlo en aceptable para embeberlo
    """
    def setData(self,dato):
        self.defaultData = dato
        self.initialValues(**dato)
        
    def getData(self):
        #TODO verificar los datos
        if self.defaultData.get('cancel',False):
            return self.defaultData
        stablas = [ self.sheet.item(k,0).text()  for k in range(1,self.sheet.rowCount())  if self.sheet.item(k,0).text() ]
        if len(stablas) == 0:
            self.msgLine.setText('Debe definir al menos una tabla de enlace')
            self.sheet.setFocus()
            return
        if not self.validateArray():
            return
        
        tablasFQ = []
        for entrada in stablas:
            if entrada == "":
                break
            tablasFQ.append(self.short2long(entrada))

        #TODO expandir los internalLinks
        links = []
        for k in range(len(tablasFQ)):
            if tablasFQ[k] == '':
                continue
            if  self.array[k].get('internalLink'):
                arcos = self.linkTransform(k,tablasFQ)
                for arco in arcos:
                    links.append(arco)
            elif self.array[k].get('clause'):
                arco = self.clauseTransform(k,tablasFQ)
                arco['table'] = tablasFQ[k]
                links.append(arco)
        name = self.name.text()
        #resultado = { 'link via':links,'elem':self.fieldsTarget.seleList,'name':self.targetTable,'table':self.targetTable}
        dato = self.defaultData.copy()
        if 'structure' not in dato:
            dato['structure'] = {}
        dato['structure']['name'] = name
        dato['structure']['elem'] = [ self.fields.tr(self.targetTable,value) for value in self.fieldsTarget.seleList ]
        dato['structure']['table'] = self.short2long(self.targetTable)
        dato['structure']['link via'] = links
        return dato


    def reject(self):
        #FIXME esto creo que no es tan simple en este caso
        if self.defaultData:
            self.defaultData['cancel']=True
            #self.initialValues(**self.defaultData)
        super().reject()


    def denorm(self,struct):
        if isinstance(struct,(list,tuple)):
            for ind,linea in enumerate(struct):
                struct[ind] = self.denorm(linea)
        elif isinstance(struct,dict):
            for key in struct:
                struct[key] = self.denorm(struct[key])
        elif isinstance(struct,str):
            if ' ' in struct or '(' in struct:
                pass
            else:
                return struct.split('.')[-1]

        return struct
    
class FKNetworkDialog(QDialog):
    def __init__(self,cubeTable,fields,routeHandler,parent=None):

        super().__init__(parent)
        self.setMinimumSize(QSize(640,330))
        
        self.manualBB = QPushButton('Ir a manual')
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonBox.addButton(self.manualBB, QDialogButtonBox.ActionRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        buttonBox.clicked.connect(self.procBotones)
        
        self.msgLine = QLabel()
        titleLabel = QLabel('Nombre de la guia')
        destLabel =QLabel('Tabla por la que queremos agrupar')
        destFLabel    =QLabel('Campos por los que queremos agrupar')
        routeLabel  = QLabel('Ruta para acceder a al tabla destino')
        
        self.titleText = QLineEdit()
        self.titleText.setStyleSheet("background-color:yellow;")

        
        self.destTable = QComboBox()
        self.destField = WComboMulti()
        self.destRoutes = QComboBox()
        
        meatlayout = QGridLayout()
        x = 0
        meatlayout.addWidget(titleLabel,x,0)
        meatlayout.addWidget(self.titleText,x,1)
        x +=1
        meatlayout.addWidget(destLabel,x,0)
        meatlayout.addWidget(self.destTable,x,1)
        x +=1
        meatlayout.addWidget(destFLabel,x,0)
        meatlayout.addWidget(self.destField,x,1)
        x += 1
        meatlayout.addWidget(routeLabel,x,0)
        meatlayout.addWidget(self.destRoutes,x,1,1,2)
        x += 2
        meatlayout.addWidget(self.msgLine,x,0)
        x += 1
        meatlayout.addWidget(buttonBox,x,1)
        
        self.setLayout(meatlayout)
        self.prepareData(cubeTable,fields,routeHandler)

        self.manual = False

    def prepareData(self,cubeTable,fields,routeHandler):
        
        self.rel = routeHandler
        #self.routeData = self.rel.get(cubeTable)
        self.cubeTable = cubeTable
        self.fields = fields
        # load destTable. TODO ¿todas las tablas o solo las que tienen conexion FK?
        self.tablesCurrentList = list(self.rel.get(self.cubeTable).keys())
        self.destTable.addItems(self.tablesCurrentList)
        self.destTable.setCurrentIndex(-1)
        self.destTable.currentIndexChanged[int].connect(self.seleccionTabla)
 
    def seleccionTabla(self,idx):
        #FIXME y si no hay rutas .... ¿?
        # preparamos la lista de campos
        #self.FieldsFullList = srcFields(self.item,self.view,file=self.tablesCurrentList[idx])
        self.FieldsFullList = self.fields.getFull(self.tablesCurrentList[idx])
        #x,y = zip(*self.FieldsFullList)
        #self.fieldsCurrentList = list(y)
        self.destField.clear()
        self.destField.addItems(self.FieldsFullList)
        #self.destField.load([ entry[0] for entry in self.FieldsFullList],self.fieldsCurrentList)
        
        # preparamos la lista de rutas
        rutasTabla = self.rel.prettyList(self.cubeTable,self.tablesCurrentList[idx])
        ##FIXME esto tiene que ser un map
        #for k in range(len(rutasTabla)):
            #entrada = rutasTabla[k][2:]
            #rutasTabla[k] = entrada.replace('->','\n\t')
        self.destRoutes.clear()
        self.destRoutes.addItems(rutasTabla)
        self.destRoutes.setCurrentIndex(-1)
       
    def short2long(self,file):
        if '.' in file:
            return file
        schema = self.cubeTable.split('.')[0] # se supone que viene cargado
        return '{}.{}'.format(schema,file)
    def accept(self):
        #TODO validaciones
        name = self.titleText.text()
        schema = self.cubeTable.split('.')[0] # se supone que viene cargado
        baseTable = self.tablesCurrentList[self.destTable.currentIndex()]
        table = '{}.{}'.format(schema, baseTable)
        values = norm2List(self.destField.get())

        # ahora el link link_via
        electedPath = self.destRoutes.currentText() #que valiente
        path = dictLinkDef2dict(self.rel,electedPath,self.cubeTable,baseTable,self.fields,self.short2long)
        
        #electedPath = '->' + electedPath.replace('\n\t','->')
        #electedPathDatos = self.routeData[baseTable][electedPath]
        #path = []
        #for arc in electedPathDatos:
            #arcInfo = arc['ref'].getRow()
            #arcDict = {'table':arcInfo[1],'filter':'','clause':[{'base_elem':arcInfo[2],'rel_elem':arcInfo[3]},]}
            #path.append(arcDict)
            
        self.result = {'name':name,
                                            'class':'o',
                                            'prod':[{'name':name,
                                                            'elem':values,
                                                            'table':table,
                                                            'link via':path
                                                          }
                                                        ,]
                                }
        super().accept()


        
    def procBotones(self,button):
        if button == self.manualBB:
            self.manual = True
            super().accept()
      
def dictLinkDef2dict(routeData,route,tablaOrig,tablaDest,fieldDef,fqnget):
    resultados = []
    clausulaAut = routeData.detailPretty(tablaOrig,tablaDest,route)
    for ind,arc in enumerate(clausulaAut):
        #FIXME falta el caso con varios campos en la foreign key
        arcInfo = arc['ref'].getRow()
        bases = norm2List(arcInfo[2])
        rels = norm2List(arcInfo[3])
        clause = []
        for k in range(min(len(bases),len(rels))):
                base =  fieldDef.tr(arc['child'],bases[k])
                rel    =  fieldDef.tr(arc['parent'],rels[k])
                clause.append({'base_elem':base,'rel_elem':rel})
        arcDict = {'table':fqnget(arcInfo[1]),
                            'filter':'',
                            'clause':clause}
        resultados.append(arcDict)
    return resultados
