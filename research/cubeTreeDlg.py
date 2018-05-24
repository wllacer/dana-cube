#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
manual link
    #TODO posibilidad de boton de vuelta atras
    #TODO formato de cabecera mas chillon
    #TODO falta nombre
    #TODO recoger informacion cuando viene de un automatico fustrado
    #TODO ¿Convertir self.sheet a WDelegateSheet ¿?
auto link

Comunes
    #FIXME me parece que aparecen mas relaciones de la cuenta
    #FIXME falta comprobar el caso con varios campos en la foreign key en automatico
    #unificar codigo

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from support.gui.widgets import WMultiCombo,WPowerTable,WMultiList
from support.util.record_functions import norm2List,norm2String

from PyQt5.QtCore import Qt,QSize,pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QGridLayout, \
      QCheckBox,QPushButton,QLineEdit

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem, QMenu, QComboBox, QStyledItemDelegate, QLabel, QDialogButtonBox, QLineEdit,QSizePolicy

def makeTableSize(widget):
    widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    #self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    #self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    #self.resizeColumnsToContents()
    widget.setFixedSize(widget.horizontalHeader().length()+widget.verticalHeader().width(), 
                                widget.verticalHeader().length()+widget.horizontalHeader().height())

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
        print('CE',self.sheet)
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

        pprint(self.tempTables)
        editor = QComboBox(parent)
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
        self.tables = self.parent().tables #TODO adecuar a la estructura de datos
        
    def createEditor(self,parent,option,index):
        if index.row() == 0:
            return super().createEditor(parent,option,index)
        return QComboBox(parent)
        
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
    
class WDelegateSheet(QTableWidget):
    """
    """
    contextChange = pyqtSignal()
    rowAdded = pyqtSignal(int)
    rowRemoved =pyqtSignal(int)

    def __init__(self,row,col,delegate=None,parent=None):
        super().__init__(row,col,parent)
        makeTableSize(self)
        self.initialize()
        if delegate:
            sheetDelegate = delegate(self)
            self.setItemDelegate(sheetDelegate)
       
        #FIXME no funciona
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        self.context = {}
        # en esta posicion para que las señales se activen tras la inicializacion
        #self.currentItemChanged.connect(self.moveSheetSel)
        #self.itemChanged.connect(self.itemChanged)

    def initialize(self):
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                self.initializeCell(i,j)
        self.setItemPrototype(QTableWidgetItem(''))
    
    def initializeCell(self,x,y):
        self.setItem(x,y,QTableWidgetItem(None))

    def openContextMenu(self,position):
        print('voy a context menu',position)
        item = self.itemAt(position)
        row = item.row()
        menu = QMenu()
        menu.addAction("Insert row before",lambda i=row:self.addRow(i))
        menu.addAction("Insert row after",lambda i=row:self.addRow(i +1))
        menu.addAction("Append row",self.addRow)
        menu.addSeparator()
        menu.addAction("Remove",lambda i=row:self.removeRow(i))
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
                
    def addRow(self,idx=None,emit=True):
        if not idx:
            idx = self.rowCount()
        self.insertRow(idx)
        for j in range(self.columnCount()):
                self.initializeCell(idx,j)
        if emit:
            self.rowAdded.emit(idx)
        item = self.item(idx,0)
        self.setCurrentItem(item)
        self.setFocus()
        
    def removeRow(self,idx=None,emit=True):
        if not idx:
            return
        self.removeRow(idx)
        if emit:
            self.rowRemoved.emit(idx)
        self.setCurrentItem(self.sheet.item(idx -1,0))
        self.setFocus()

    def setContext(self,data=None,**kwparm):
        changed = False
        for dato in kwparm:
            if self.context.get(dato) != kwparm.get(dato):
                changed = True
                break
        if changed:
            self.contextChange.emit()
            self.initialize()
        for dato in kwparm:
            self.context[dato] = kwparm[dato]
            
        if data:
            self.loadData(data)
        #self.resizeColumnsToContents()

    def loadData(self,data):
        """
        before use it might be of interest to disconnect the rowAdded pyqtSignal
        """
        for ind,entry in enumerate(data):
            if ind >= self.rowCount():
                self.addRow(emit=False)
            for col,dato in enumerate(entry):
                if col >= self.columnCount():
                    break
                self.setData(ind,col,dato)
    
    def unloadData(self):
        result = [ [ None for k in range(self.columnCount()) ] for j in range (self.rowCount()) ]
        for row  in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.item(row,col):
                    result[row][col] = self.item(row,col).text()
                else:
                    result[row][col] = None
        return result
    


class manualLinkDlg(QDialog):
    def __init__(self,pfile,tablas,fields,rel,structure=None,parent=None,):
        super().__init__(parent)
        
        self.fullTables = tablas
        self.tables = [ elem[1] for elem in tablas ]
        
        iidx = self.tables.index(pfile)
        self.baseTable = self.fullTables[iidx][0]
        self.fields = fields
        self.rel = rel
        if not structure:
            self.structure = {}
        else:
            self.structure = structure
        self.array = [ elem for elem in self.structure.get('link via',[])] 
        file =  [pfile, ] + [ elem.get('table') for elem in self.array ]
        for k in range(len(self.array)):
            line = self.array[k]
            line['internalLink'] = None
            del line['table']
        if self.array:
            self.targetTable = self.structure.get('link via',[])[-1].get('table')
            self.targetFields = norm2List(self.structure.get('link via',[])[-1].get('elem'))
        else:
            self.targetTable= None
            self.targetFields = []
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        self.msgLine = QLabel()
        self.sheet = QTableWidget(5,1)
        self.sheet.horizontalHeader().hide()
        self.sheet.verticalHeader().hide()
        makeTableSize(self.sheet)

        self.internalLink = QComboBox()
        self.clauseWgt = WDelegateSheet(5,3,fieldDelegate)
        self.setClauseWgtSize()
        self.fieldsTarget = WMultiList(format='c',cabeceras=('De ','Campos de agrupacion'))
        
        self.filter = QLineEdit()
        
        detail = QGridLayout()
        k=2
        detail.addWidget(self.clauseWgt,k,0,1,2)
        k = 1
        internalLbl=QLabel('Eliga una relacion interna')
        internalLbl.setAlignment(Qt.AlignRight)
        detail.addWidget(internalLbl,k,0)
        detail.addWidget(self.internalLink,k,1,1,2)
        k=3
        filterLbl = QLabel('Escriba un filtro adicional')
        filterLbl.setAlignment(Qt.AlignRight)
        detail.addWidget(filterLbl,k,0)
        detail.addWidget(self.filter,k,1,1,2)
        
        meatlayout = QGridLayout()
        meatlayout.addWidget(self.sheet,1,0)
        meatlayout.addLayout(detail,1,1)
        
        meatlayout.addWidget(self.fieldsTarget,2,1)
        meatlayout.addWidget(self.msgLine)
        meatlayout.addWidget(buttonBox)
        
        self.setLayout(meatlayout)
        

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        self.internalLink.currentIndexChanged.connect(self.linkUpdated)
        self.sheet.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sheet.customContextMenuRequested.connect(self.openContextMenu)
        
        delegate = tablesDelegate(self)
        self.sheet.setItemDelegate(delegate)
        
        self.initialize(file)
        self.disableDetail()
        # en esta posicion para que las señales se activen tras la inicializacion
        self.sheet.currentItemChanged.connect(self.moveSheetSel)
        self.sheet.itemChanged.connect(self.itemChanged)
        
    def initializeCell(self,x,y):
        self.sheet.setItem(x,y,QTableWidgetItem(None))
 
    def initialize(self,file):
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
        if self.actualSize() > 1:
            self.loadTarget()
            self.fieldsTarget.show()
            
        else:
            self.fieldsTarget.hide()
    """
        sheet status change
    """
    def moveSheetSel(self,current,previous):
        if not previous:
            return
        print('Item de ({},{}) a ({},{})'.format(previous.row(),previous.column(),current.row(),current.column()))
        self.unloadDetail(previous.row())
        #esto es para que cuando en entra en linea nueva no haga cargas inutiles
        if self.sheet.item(current.row(),0).text() == "":
            return
        self.loadDetail(current.row())
        
        
    def itemChanged(self,item):
        print('item changed  ({}/{}) : {}'.format(item.row(),item.column(),item.text()))
        self.changeDetail(item)
        self.updateTarget(item)
        
    def updateTarget(self,item):    
        if item.row() == self.actualSize():
            if item.text() != self.targetTable:
                self.targetTable =  item.text()
                self.loadTarget()
                self.fieldsTarget.show()
        
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
            initialData.append(elem['base_elem'],elem.get('condition','='),elem['rel_elem'])
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
        print('change detail',idx)
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
        print('Link cic',idx)
        if idx < 1:  #no elegí
            self.clauseWgt.setEnabled(True)
        else:
            self.clauseWgt.setEnabled(False)
     
    def validateArray(self):
        self.msgLine.setText("")
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
        #TODO verificar los datos
        if not self.validateArray():
            return
        stablas = [ self.sheet.item(k,0).text() for k in range(1,self.sheet.rowCount()) ]
        tablasFQ = []
        for entrada in stablas:
            if entrada == "":
                break
            tablasFQ.append(self.short2long(entrada))

        #TODO expandir los internalLinks
        links = []
        pprint(tablasFQ)
        pprint(self.array)
        for k in range(len(tablasFQ)):
            print('y ahora entrada',k)
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
        name = self.targetTable #FIXME
        #resultado = { 'link via':links,'elem':self.fieldsTarget.seleList,'name':self.targetTable,'table':self.targetTable}
        self.result = {'name':name,
                                    'class':'o',
                                    'prod':[{'name':name,
                                                    'elem':[ self.fields.tr(self.targetTable,value) for value in self.fieldsTarget.seleList ],
                                                    'table':self.short2long(self.targetTable),
                                                    'link via':links
                                                    }
                                                ,]
                        }
        pprint(self.result)
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
        #resultados = []
        #clausulaAut = self.rel.detailPretty(tablaOrig,tablaDest,entrada['internalLink'])
        #for ind,arc in enumerate(clausulaAut):
            ##FIXME falta el caso con varios campos en la foreign key
            #arcInfo = arc['ref'].getRow()
            #bases = norm2List(arcInfo[2])
            #rels = norm2List(arcInfo[3])
            #clause = []
            #for k in range(min(len(bases),len(rels))):
                    #base =  self.fields.tr(arc['child'],bases[k])
                    #rel    =  self.fields.tr(arc['parent'],rels[k])
                    #clause.append({'base_elem':base,'rel_elem':rel})
            #arcDict = {'table':self.short2long(arcInfo[1]),
                             #'filter':'',
                             #'clause':clause}
            #resultados.append(arcDict)
        #return resultados

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
        pprint(resultado)
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
#from research.cubeTree  import srcFields,srcTables

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
        self.destField = WMultiCombo()
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
        x,y = zip(*self.FieldsFullList)
        self.fieldsCurrentList = list(y)
        self.destField.clear()
        self.destField.load([ entry[0] for entry in self.FieldsFullList],self.fieldsCurrentList)
        
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
