#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

import user as uf
import math 

from support.util.uf_manager import *
from base.ufhandler import functionFromName
from support.util.jsonmgr import *
from support.gui.widgets import WMultiCombo,WPowerTable
from support.util.record_functions import norm2List,norm2String
import base.config as config

from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView, QStyledItemDelegate, QSpinBox, QListWidget, QPushButton, QVBoxLayout,QLabel, QWidget, QCheckBox

"""
Utildades
"""
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1", "si", "sí", "ok")

"""
from PyQt5.QtWidgets import QWidget,QListWidget,QPushButton,QVBoxLayout,QLabel,QGridLayout

Widgets
"""
class WMultiList(QWidget):
    def __init__(self,lista=None,initial=None,parent=None):
        super().__init__(parent)
        self.disponible = QListWidget()
        self.selecto = QListWidget()
        self.anyade = QPushButton('Añadir')
        self.elimina = QPushButton('Eliminar')
        
        origenlayout=QVBoxLayout()
        self.origenCabecera = QLabel('Elementos disponibles')
        origenlayout.addWidget(self.origenCabecera)
        origenlayout.addWidget(self.disponible)
        
        destinolayout=QVBoxLayout()
        self.destinoCabecera = QLabel('Elementos seleccionados')
        destinolayout.addWidget(self.destinoCabecera)
        destinolayout.addWidget(self.selecto)

        boxlayout = QGridLayout()
        boxlayout.addWidget(self.anyade,2,0)
        boxlayout.addWidget(self.elimina,3,0)

        meatlayout = QGridLayout()
        meatlayout.addLayout(origenlayout,0,0)
        meatlayout.addLayout(boxlayout,0,2)
        meatlayout.addLayout(destinolayout,0,3)
        
        self.setLayout(meatlayout)

        self.anyade.clicked.connect(self.selectItem)
        self.elimina.clicked.connect(self.removeItem)
        
        self.origList = []
        self.freeList = []
        self.seleList = []
        
        self.load(lista,initial)
        
    def load(self,lista,initial):
        self.disponible.clear()
        if lista is not None:
            self.origList = [ entry for entry in lista ]
        self.freeList = [ entry for entry in self.origList]
        self.disponible.addItems(self.freeList)
        self.selecto.clear()
        self.seleList = []
        if initial is not None:
            self.setSelectedEntries(initial)
    
    # slots
    def selectItem(self,checked):
        """
        checked is not used
        """
        lista = self.disponible.selectedItems()
        for item in lista:
            valor = item.data(0)
            idx = self.freeList.index(valor)
            del self.freeList[idx]
            self.seleList.append(valor)
            mitem = self.disponible.takeItem(idx)
            self.selecto.addItem(mitem)

    def removeItem(self,checked):
        """
        checked is not used
        #TODO devolver a la posicion original
        """
        lista = self.selecto.selectedItems()
        for item in lista:
            valor = item.data(0)
            idx = self.seleList.index(valor)
            del self.seleList[idx]
            self.freeList.append(valor)
            mitem = self.selecto.takeItem(idx)
            self.disponible.addItem(mitem)


    def selectEntry(self,entrada):
        if entrada not in self.seleList:
            self.seleList.append(entrada)
            self.selecto.addItem(entrada)
        ande = self.freeList.index(entrada)
        self.disponible.takeItem(ande)
        del self.freeList[ande]

    def removeEntry(self,entrada):
        if entrada not in self.freeList:
            self.freeList.append(entrada)  #TODO devolver a la posicion original
            self.disponible.addItem(entrada)
        ande = self.seleList.index(entrada)
        self.selecto.takeItem(ande)
        del self.seleList[ande]

    def setSelectedEntries(self,lista):
        conjunto = norm2List(lista)
        for entrada in conjunto:
            self.selectEntry(entrada)

    ## signals
    #def itemSelected(self,item): #signal
        #pass
    #def itemRemoved(self,item):  #signal
        #pass
    ## methods
    
    #def getAvailableItems(self):
        #pass
    #def setAvailableItems(self,lista):
        #pass
    #def getAvailableItemsLabel(self):
        #pass
    #def setAvailableItemsLabel(self,label):
        #pass
    #def getSelectedItems(self):
        #pass
    #def setSelectedItems(self,lista):
        #pass
    #def getSelectedItemsLabel(self):
        #pass    
    #def setSelectedItemsLabel(self,label):
        #pass
    ## protected member
    #def addSelectedItem(self):
        #pass
    #def removeSelectedItem(self):
        #pass

class WNameValue(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.sheet = WPowerTable(5,2)
        self.ok = QPushButton('ok')
        
        self.ok.clicked.connect(self.accept)
        
        meatlayout = QGridLayout()
        meatlayout.addWidget(self.sheet,0,0)
        meatlayout.addWidget(self.ok,1,0)
        self.setLayout(meatlayout)
        self.prepareData()
        
    def prepareData(self):
        self.sheet.setHorizontalHeaderLabels(('nombre','valor                                                    '))
        context = []
        context.append((QLineEdit,{'setEnabled':True},None))
        context.append((QLineEdit,{'setEnabled':True},None))
        for x in range(self.sheet.rowCount()):
            for y,colDef in enumerate(context):
                self.sheet.addCell(x,y,colDef,defVal=None)
            self.sheet.resizeRowsToContents()

        
"""
Funciones para leer la configuracion de user functions. Reutilizadas, creo
"""

def readUM(context,toollist= None):
    withReturn = False
    if not toollist:
        withReturn = True
        toollist = {}
    import inspect as ins
    for entrada in context.__all__:
        source = getattr(context,entrada)
        for func in ins.getmembers(source,ins.isfunction):
            if func[0] in toollist:
                continue
            toollist[func[0]] = func[1]
        
        for clase in ins.getmembers(source,ins.isclass):
            if clase[0] in toollist:
                continue
            toollist[clase[0]] = clase[1]
    if withReturn:
        return toollist


 
def lastChild(item):
    if item.hasChildren():
        return item.child(item.rowCount() -1)
    else:
        return None
    
def childItems(treeItem):
    if not treeItem:
        return None
    datos = []
    for ind in range(treeItem.rowCount()):
        datos.append(treeItem.child(ind))
    return datos

def makeRow(*parms):
    retorno = []
    for k in range(len(parms)):
        elem = QStandardItem(str(parms[k]) if parms[k] is not None else None)
        elem.setData(parms[k],Qt.UserRole +1)
        retorno.append(elem)
    return retorno

def dict2tree(parent,key,data,tipo=None):
    """
        Funcion que carga de estructura de cubo python a nodo QStandardItem del arbol (recursiva)
        parent -> nodo del arbol a partir del cual incluir
        key > clave del nodo
        data > valor del nodo
        tipo > clase del nodo
        Los valores de elementos atomicos son atributos del nodo en arbol
    """
    #parent.appendRow((QStandardItem(str(key)),QStandardItem(str(data)),))
    if not tipo:
        tipo=str(key)
    if not isinstance(data,(list,tuple,set,dict)): #
        parent.appendRow(makeRow(key,data,tipo))
    else:
        parent.appendRow(makeRow(key,None,tipo))
    newparent = lastChild(parent)
    if isinstance(data,dict):
        for elem in sorted(data):
            dict2tree(newparent,elem,data[elem])
    elif isinstance(data,(list,tuple)):
        for idx,elem in enumerate(data):
            if not isinstance(elem,(list,tuple,dict)):
                #continue
                newparent.appendRow(makeRow(None,elem))

            elif isinstance(elem,dict): #and elem.get('name'):
                for texto in ('name','result'):
                    if elem.get(texto):
                        clave = elem.get(texto)
                        break
                else:
                    clave = str(idx)
                datos = elem
                #datos['pos'] = idx
                dict2tree(newparent,clave,datos,tipo)
            else:                
                clave = str(idx)
                datos = elem
                dict2tree(newparent,clave,datos,tipo)  
 
def isDictFromDef(item):
    """
    determina si el nodo es la cabeza de un diccionario viendo como son los hijos.
    Es demasiado simple para otra cosa que lo que tenemos
    
    """
    if item.hasChildren():
        contexto = getItemContext(item)
        type_context =  contexto.get('edit_tree',{}).get('objtype')
        if type_context == 'dict':
            return True
        elif type_context is not None:
            return False
        
        firstChild = item.child(0,0)
        firstChildTipo = item.child(0,2)
        if not firstChildTipo:                             #los elementos de una lista pura no tienen tipo y no deberian tener ese elemento
            return False
        elif firstChildTipo.data() is None:
            return False
        elif firstChild.data() is None:                 #los elementos de una lista no tienen nombre
            return False
        else:
            return True
    else:
        return False
    
def tree2dict(rootItem,esdiccionario=None,role=None):
    """
       convertir un nodo de  estructura arbol en una entrada de cubo en memoria (diccionario) -recursiva-
       deberia ir a cubetree
       esdiccionario es una funcion para determinar si la entrada es o no un diccionario.
       TODO convertir la funcion en multiple valor elem,dict,tree,Not Defined
    """
    #FIXIT como manejar los numeros un poco raros
                         #Compactar el codigo
    elementos=childItems(rootItem)
    #una de las variables es innecesaria de momento
    toList = False
    toDict = False
    if rootItem == rootItem.model().invisibleRootItem() :
            toDictionary = True #la raiz siempre genera directorio
    elif esdiccionario and esdiccionario(rootItem):   
        toDictionary = True
    else:
       toList = True
       
    if toList:
        result_l = list()
        for item in elementos:
            nombre = item.data()
            dato = item.model().itemFromIndex(item.index().sibling(item.row(),1)).data()
            #tipo = item.model().itemFromIndex(item.index().sibling(item.row(),2)).data()
            if item.hasChildren():
                result_l.append(tree2dict(item,esdiccionario,role))
            else:
                #dato = item.getColumnData(1,role)
                if dato is None or dato == 'None': #FIXME deberia ser continue ¿?
                   result_l.append(None)
                else:
                    result_l.append(dato)
        return result_l
    else:
        result_d = dict()
        for item in elementos:
            nombre = item.data()
            dato = item.model().itemFromIndex(item.index().sibling(item.row(),1)).data()
            #tipo = item.model().itemFromIndex(item.index().sibling(item.row(),2)).data()
            if item.hasChildren():
                result_d[nombre] = tree2dict(item,esdiccionario,role)
            else:
                #dato = item.getColumnData(1,role)
                if dato is None or dato == 'None':
                    #FIXME deberia ser continue
                   result_d[nombre]=None
                # para los valores booleanos. Bug sutil 
                #if dato in ('True','False'):
                    #result_d[item.text()] = True if dato == 'True' else False
                #elif is_number(dato):
                   #result_d[item.text()] = Decimal(dato)
                else:
                    result_d[nombre]= dato

        return result_d

def cloneSubTree(entryPoint): #,filter=None,payload=False):
    """
    TODO add to doc
    Generate a new tree from entryPoint and its children
    
    * Input parms
        *
        * __entryPoint__ a GuideItem as hierachical head of what to export
        * __filter__ a function which does some filtering at the tree (default is no filter)
        * __payload__ boolean. If True copies the payload
        
    * returns
        a tree
    
    """
    #for k in range(modelo.rowCount()):
        #item = modelo.item(k)
        #first = True
        #print(item.data())
        #for chip in traverse(modelo,item):
            #if first:
                #hier = hierTree(chip)
                #last = chip.data()
                #first = False
                #continue
            #ohier = hierTree(chip)
            #if len(ohier) == len(hier):
                #pass
            #elif len(ohier) > len(hier):
                #hier.append(last)
            #elif len(ohier) < len(hier):
                #del hier[len(ohier):]
            #if ohier != hier:
                #print('scheisse',ohier,hier)
            #last = chip.data()

    def hierTree(entry):
        mihier = []
        pai = entry.parent()
        while pai is not None:
                mihier.insert(0,pai)
                pai = pai.parent()
        return mihier
    isFirst = True
    hierarchy = []
    model = entryPoint.model()
    for item in traverse(model,entryPoint):
        n,i,t = getRow(item)
        if isFirst:
            newRow = makeRow(t.data(),i.data(),t.data())
            if entryPoint.parent() is None:
                newRow = makeRow(t.data(),i.data(),t.data())
                model.appendRow(newRow)
            else:
                entryPoint.parent().appendRow(newRow)
                pai = entryPoint.parent()
                while pai is not None:
                    hierarchy.insert(0,[pai,pai])
                    pai = pai.parent()
            hierarchy.append([item,newRow[0]])
            newHead = newRow[0]
            isFirst = False
        else:
            newRow = makeRow(n.data(),i.data(),t.data() if t else None)
            ohier = hierTree(item)
            if len(ohier) == len(hierarchy):
                pass
            elif len(ohier) < len(hierarchy):
               del hierarchy[len(ohier):]
            else: #mas
                hierarchy.append(last)
            hierarchy[-1][1].appendRow(newRow)
        last = [n,newRow[0]]            
    return newHead

def traverse(model, key=None):
    if key is not None:
        yield key
        queue = childItems(key)
    else:
        queue = childItems(model.invisibleRootItem())
    while queue:
        yield queue[0] 
        expansion = childItems(queue[0])
        queue = expansion + queue[1:]  # depth-first

def getRow(item_ref,conTipo=False):
    """
    con tipo devuelve datos diferentes
    """
    if isinstance(item_ref,QModelIndex):
        index = item_ref 
    else:
        index = item_ref.index()
    model = index.model()  

    if index is None or not index.isValid():
        print('indice dañado seriamente')
        raise()
    nomidx = index.sibling(index.row(),0)
    itmidx = index.sibling(index.row(),1)
    tipidx = index.sibling(index.row(),2)
    nomItem= model.itemFromIndex(nomidx)
    item = model.itemFromIndex(itmidx)
    tipoItem = model.itemFromIndex(tipidx)
    headitem = item
    #if tipoItem.data() not in EDIT_TREE:
        #print('empiexa',nomItem.data(),item.data(),tipoItem.data())
    if conTipo:
        pai = index.parent()
        while not tipoItem: # or tipoItem.data() not in EDIT_TREE:
            tipoItem =model.itemFromIndex(pai.sibling(pai.row(),2))
            headitem = model.itemFromIndex(pai)
            pai = pai.parent()
        objtype = tipoItem.data()
        #print('termina',nomItem.data(),headitem.data(),tipoItem.data())
    if conTipo:
        return nomItem,item,tipoItem,headitem,objtype
    else:
        return nomItem,item,tipoItem

def branch2text(headItem):                    
    if not headItem.hasChildren():
        if headItem.column() == 1:
            return str(headItem.data())
        else:
            datosEnIdx = headItem.index().sibling(headItem.row(),1)
            datos = headItem.model().itemFromIndex(datosEnIdx).data()
            return str(datos)
    text = None
    clase = None
    for x in range(headItem.rowCount()):
        n,i,t = getRow(headItem.index().child(x,0))
        if x == 0:
            if n.data() is None:
                clase = 'L'
                text = branch2text(n)
            else:
                clase = 'D'
                text = "'{}':{}".format(n.data(),branch2text(n))
        else:
            if clase == 'L':
                text = ','.join((text,branch2text(n)))
            else:
                text = ','.join((text,"'{}':{}".format(n.data(),branch2text(n))))
    if clase == 'D':
        text = '{'+text+'}'
    else:
        text ='['+text+']'
    return text
    
"""
Callbacks del editor
"""
def funclist(item):
    return list(readUM(uf).keys())
def modlist(item):
    definiciones = load_cubo('danacube.json')
    return list(definiciones['user functions'].keys())


def qualifyClass(*lparms):
    item = lparms[0]
    n,i,t = getRow(item)
    clase = t.data()
    for k in range(n.rowCount()):
        hijo = n.child(k,0)
        if hijo.data() == 'class':
            porta = n.child(k,1)
            porta.setData(t.data(),Qt.DisplayRole)
            porta.setData(t.data(),Qt.UserRole +1)
    
def checkMandatory(*lparms):
    item = lparms[0]
    view = lparms[1]
    n,i,t = getRow(item)
    for k in range(n.rowCount()):
        context = getItemContext(n.child(k,0))
        if context.get('mandatory',False) and ( context['data'] is None or context['data'] == '' ):
            editIndex = n.child(k,1).index()
            view.setCurrentIndex(editIndex)
            #view.edit(editIndex)
            view.edit(editIndex)
        
        
    
"""

Nuevo mojo del arbol

no example of validators attribute 
elements list is (element name,mandatory,readonly,repeatable)
still no process for repeatable 
class & name are not to be edited (even shown) as derived DONE
"""

TOP_LEVEL_ELEMS = ['function','sequence']
EDIT_TREE = {
    'function': {'objtype': 'dict',
                    'elements': [
                        ('entry',True,False),
                        ('type',True,False),
                        ('text',True,False),
                        ('class',True,True),
                        ('aux_parm',False,False), #o no ? TODO
                        ('db',True,False), #o no ?
                        ('seqnr',False,False),
                        ('sep',False,False),
                        ('hidden',False,False),
                        ('api',False,False)
                        ],
                    'getter':[],                   #antes de editar
                    'setter':[qualifyClass, checkMandatory],      #despues de editar (por el momento tras add
                    'validator':[]                 #validacion de entrada
                    },
    'sequence': {'objtype': 'dict',
                    'elements': [
                        ('list',True,False),
                        ('type',True,False),
                        ('text',True,False),
                        ('class',True,True),
                        ('db',False,False), #o no ?
                        ('seqnr',False,False),
                        ('sep',False,False),
                        ('hidden',False,False),
                        ],
                    'getter':[],
                    'setter':[qualifyClass,],
                    'validator':[]
                    },
    'name': {'editor':QLineEdit},
    'entry':{'editor':QComboBox,'source':funclist},
    'type': {'editor':WMultiCombo,
                'source':['item','leaf','colparm','rowparm','colkey','rowkey','kwparm'],
                'default':'item'
            },
    'text':{'editor':QLineEdit},
    'aux_parm':{'objtype':'dict'},  #TODO mejorable
    'db': {'editor':QLineEdit},
    'seqnr': {'editor':QSpinBox},
    'sep': {'editor':QComboBox,'source':['True','False'],'default':False},
    'hidden':{'editor':QComboBox,'source':['True','False'],'default':False},
    'sep': {'editor':QCheckBox,'default':False},
    'hidden':{'editor':QCheckBox,'default':False},
    'list' : {'editor':WMultiList,'source':modlist},
    'api': {'editor':QSpinBox,'default':1,'max':1,'min':1},
    'class':{'editor':QComboBox,'source':('function','sequence')}
    
}
    
def editAsTree(fichero):
    from base.core import Cubo
    from support.util.jsonmgr import load_cubo
    definiciones = load_cubo(fichero)
    mis_cubos = definiciones['user functions']

    #cubo = Cubo(mis_cubos['experimento'])
    model = QStandardItemModel()
    model.setItemPrototype(QStandardItem())
    hiddenRoot = model.invisibleRootItem()
    parent = hiddenRoot
    for entrada in mis_cubos:
        if mis_cubos[entrada]['class'] == 'function':
            tipo = 'function'
        elif mis_cubos[entrada]['class'] == 'sequence':
            tipo = 'sequence'
        dict2tree(parent,entrada,mis_cubos[entrada],tipo)
    return model

def getItemContext(item_ref):
    # sobrecargo tanto para item como indice
    if isinstance(item_ref,QModelIndex):
        item = item_ref.model().itemFromIndex(item_ref)
    else:
        item = item_ref
    model = item.model()  
    if item == model.invisibleRootItem():
        print('Cabecera de cartel, nada que hacer de momento')
        return
    # obtengo la fila entera
    n,d,t = getRow(item.index())
    # obtengo el padre
    if n.parent() is None:
        isTopLevel = True
        np = dp = tp = None
    else:
        np,dp,tp = getRow(n.parent().index())
        isTopLevel = False
    
    if not t or ( not isTopLevel and t.data() == tp.data()):
        isListMember = True
    else:
        isListMember = True
    #obtengo el primer hijo
    if n.hasChildren():
        nh,dh,th = getRow(n.child(0,0).index())
        if nh.data() is None:
            dataType = 'list'
        else:
            dataType = 'dict'
    else:
        dataType = 'atom'
    # datos de edicion
    if not t or t.data() is None:
        editPosition = dp
        editType = tp.data()
    else:
        editPosition = d
        editType = t.data()
    
    isMandatory = False
    isReadOnly = False
    if tp:
        elementosPadre = EDIT_TREE.get(tp.data(),{}).get('elements',[[None,None,None]])
        if t.data():
            try:
                idx  = [ dato[0] for dato in elementosPadre ].index(t.data())
                isMandatory = elementosPadre[idx][1]
                isReadOnly = elementosPadre[idx][2]
            except ValueError:
                pass
            
        
        
    return {
            'rowHead':n,
            'name':n.data(),
            'data':d.data(),
            'type':t.data() if t else None,
            'dtype':dataType,
            'topLevel':isTopLevel,
            'listMember':isListMember,
            'editPos': editPosition,
            'editType':editType,
            'mandatory':isMandatory,
            'readonly':isReadOnly,
            'edit_tree':EDIT_TREE.get(t.data() if t else tp.data(),{})
            }
    #print('datos ->{}:{} ({})  tipo:{} TopLevel:{}, ListMember:{} edit type {} and edit position {}'.format(
            #n.data(),d.data(),t.data() if t else None,
            #dataType,isTopLevel,isListMember,
            #editType.data(), editPosition.data()
          #))
    
    
"""
Funciones GUI principales 
"""



class ufTreeMgrWindow(QMainWindow):
    """
    """
    def __init__(self,parent=None):
        super(ufTreeMgrWindow,self).__init__(parent)
        self.cubeFile = 'danacube.json'
        self.tree = ufTreeMgr()
        self.setCentralWidget(self.tree)
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.saveFile()
        return True
 
    def saveFile(self):
        if self.saveDialog():
            definiciones = load_cubo(self.cubeFile)
            definiciones['user functions'] = tree2dict(self.tree.model().invisibleRootItem(),isDictFromDef)
            dump_config(definiciones, self.cubeFile,total=True,secure=False)

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False

class ufTreeMgrDialog(QDialog):
    """
    """
    def __init__(self,parent=None):
        super().__init__(parent)
        self.cubeFile = 'danacube.json'
        self.tree = ufTreeMgr()
        self.msgLine = QLabel()
        meatLayout = QGridLayout()
        meatLayout.addWidget(self.tree,0,0)
        meatLayout.addWidget(self.msgLine,1,1)
        self.setLayout(meatLayout)
        
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        self.saveFile()
        return True
 
    def saveFile(self):
        if self.saveDialog():
            definiciones = load_cubo(self.cubeFile)
            definiciones['user functions'] = tree2dict(self.tree.model().invisibleRootItem(),isDictFromDef)
            dump_json(definiciones,self.cubeFile)

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios del fichero de configuracion {}?".format(self.cubeFile),
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False
 
class ufTreeMgr(QTreeView):
    """
    """
    def __init__(self,fichero='danacube.json',parent=None):
        super(ufTreeMgr, self).__init__(parent)
        self.parentWindow = parent
        self.cubeFile = fichero
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.view.setAlternatingRowColors(True)
        #self.view.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        
        self.baseModel  = editAsTree(self.cubeFile)
        parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        self.view.setModel(self.baseModel)
        
        if not config.DEBUG:
            self.view.hideColumn(2) # eso no interesa al usuario final        

        self.view.expandAll() # es necesario para el resize
        for m in range(self.baseModel.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.collapseAll()

        delegate = ufTreeDelegate(self)
        self.setItemDelegate(delegate)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)


        print('inicializacion completa')
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def openContextMenu(self,position):
        menu = QMenu()
        self.ctxMenu = []
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        context = getItemContext(index)
        n = context.get('rowHead')
        
        edit_data = EDIT_TREE.get(context.get('editType'),{})
        if context.get('topLevel',False):
            for entrada in TOP_LEVEL_ELEMS:
                self.ctxMenu.append(menu.addAction("Add new {}".format(entrada),
                                    lambda i=self.model().invisibleRootItem(),j=entrada:self.actionAddTop(i,j))) 
            self.ctxMenu.append(menu.addAction("Copy",lambda i=n:self.actionCopy(i)))
            self.ctxMenu.append(menu.addAction("Rename",lambda i=n:self.actionRename(i))) 
            menu.addSeparator()
        if 'elements' in edit_data:
            # creo que es lo mas sensible hacer. Localizo los elementos que ya existen
            existentes = set()
            for k in range(n.rowCount()):
                child = n.child(k,0)
                ns,js,ts = getRow(child.index())
                if ts.data():
                    existentes.add(ts.data())
            for elemento in edit_data['elements']:
                if elemento[0] in existentes:
                    pass
                else:
                    self.ctxMenu.append(menu.addAction("Add {}".format(elemento[0]),
                                                   lambda i=n,j=elemento[0]:self.actionAdd(i,j)))
            menu.addSeparator()

        if edit_data.get('objtype','atom') == 'dict' and edit_data.get('elements',None) is None:
            self.ctxMenu.append(menu.addAction("Add name/value pair",lambda i=n:self.actionNameValue(n)))

        if context.get('topLevel',False) or ( not context.get('mandatory',False)):
            self.ctxMenu.append(menu.addAction("Borrar",lambda i=n:self.actionRemove(i)))
        else:
            pass
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def actionRemove(self,item):
        rownr = item.row()
        pai = item.parent()
        if pai is None: #topLevel
            item.model().removeRow(rownr)
        else:
            item.model().removeRow(rownr,pai.index())
    
    def actionAdd(self,item,newItemType):
        edit_data = EDIT_TREE.get(newItemType,{})
        if item.column() == 0:
            parent = item
        else:
            parent = item.model().itemFromIndex(item.index().sibling(item.row(),0))
        newRow = makeRow(newItemType,edit_data.get('default',None),newItemType)
        if parent is None:
            self.model().appendRow(newRow)
        else:
            parent.appendRow(newRow)
        if edit_data.get('elements'):
            for entrada in edit_data.get('elements'):
                self.actionAdd(newRow[0],entrada[0])
        #TODO falta colocar el foco y validar obligatorios
        for funcion in edit_data.get('setter',[]):
            funcion(newRow[0],self)
        return newRow[0]
    
    def actionAddTop(self,item,newItemType):
        pos = self.actionAdd(item,newItemType)
        self.actionRename(pos)
       
    def actionRename(self,item):
        text = QInputDialog.getText(None, "Nuevo nombre para el nodo: "+item.data(),"Nodo", QLineEdit.Normal,item.data())
        if text[0] and text[0] != '':
            item.setData(text[0],Qt.EditRole)
            item.setData(text[0],Qt.UserRole +1)
       
    def actionCopy(self,item):
        newHead = cloneSubTree(item)
        self.actionRename(newHead)
        
    def actionNameValue(self,item):

        context = getItemContext(item)
        form = WNameValue()
        form.show()
        form.raise_()
        if form.exec():
            values = form.sheet.values()
            for funcion in context.get('edit_tree',{}).get('validators',[]):
                if not funcion(item,values):
                    print('validacion fallida')  #TODO a mensaje o similar
                    #form.sheet.cellWidget(0,0).setFocus()
                    return
            for entrada in values:
                item.appendRow(makeRow(entrada[0],entrada[1],entrada[0]))
            for funcion in context.get('edit_tree',{}).get('setters',[]):
                funcion(item,values)
            
          
class ufTreeDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.context = None 

    def createEditor(self,parent,option,index):
        """
        
        une las funciones de createEditor and setEditorData al mismo tiempo. Simplemente la logica es demasiado enlazada en este caso para separarlo
        
        """
        if index.column() != 1:
            return 
        self.context = getItemContext(index)
        #nomItem, item, tipoItem, headItem, objtype = getRow(index,True)
        #item = headItem
        
        if self.context.get('topLevel',False):
            return 
        if self.context.get('readonly',False):
            return
        #edit_format = EDIT_TREE.get(self.context.get('editType'),{})
        edit_format = self.context.get('edit_tree',{})

        item = self.context.get('editPos')
        display = item.data(Qt.DisplayRole)
        dato = item.data(Qt.UserRole +1)
        tipo = type(dato)
        defeditor = edit_format.get('editor',QLineEdit)
        
 
        if tipo == bool or defeditor ==  QCheckBox:
            #TODO hay que ponerle un nombre
            editor = QCheckBox(self.context.get('name'))
            if dato is not None:
                editor.setCheckState(dato)
            else:
                editor.setChecked(edit_format.get('default',False))
        elif defeditor ==  QSpinBox:
            editor = QSpinBox()
            editor.setMaximum(edit_format.get('max',99))
            editor.setMinimum(edit_format.get('min',0))
            if dato is not None:
                editor.setValue(dato)
            else:
                editor.setValue(edit_format.get('default',0))
        elif defeditor in (QComboBox,WMultiCombo,WMultiList):
            editor = defeditor()
            orlist = edit_format.get('source',[])
            if callable(orlist):
                lista = sorted(orlist(item))
            else:
                lista = orlist
            if defeditor ==  QComboBox:
                editor.addItems(lista)
                if dato is not None:
                    editor.setCurrentIndex(lista.index(dato))
                elif edit_format.get('default') is not None:
                    editor.setCurrentIndex(lista.index(edit_format.get('default')))

            elif defeditor in (WMultiCombo,) :
                editor.load(lista)
                aceptados = norm2List(dato)
                for entrada in aceptados:
                    editor.set(entrada)
            elif defeditor in (WMultiList,):
                inicial = []
                if item.column() != 0:
                    item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
                if item.hasChildren():
                    for x in range(item.rowCount()):
                        hijo = item.child(x)
                        valor = index.model().itemFromIndex(hijo.index().sibling(hijo.row(),1))
                        inicial.append(valor.data())
                editor.load(lista,inicial)
        elif defeditor == WPowerTable :
            if item.column() != 0:
                item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            editor = defeditor(item.rowCount() +2,2)
            editor.setHorizontalHeaderLabels(('nombre','valor'))
            context = []
            context.append((QLineEdit,{'setEnabled':False},None))
            context.append((QLineEdit,{'setEnabled':True},None))
            data = []
            for x in range(item.rowCount()):
                childIdx = item.index().child(x,0)
                nomItem,sitem,typeItem = getRow(childIdx)
                datos = [nomItem.data(),branch2text(nomItem)]
                for y,colDef in enumerate(context):
                    editor.addCell(x,y,colDef,defVal=datos[y])


            editor.resizeRowsToContents()
        else:
            if self.context.get('rowHead').hasChildren():
                return
            editor = defeditor()
            editor.setText(dato)
        return editor
            
    def setModelData(self,editor,model,index):

        model = index.model()
        if isinstance(editor, WMultiList):
            values = editor.seleList

            if not self.validator(editor,values):
                print('Rechazada la validacion')
                return
            item = self.context.get('editPos')
            # aqui el proceso de borrado y carga
            if item.column() != 0:
                item = item.model().itemFromIndex(item.index().sibling(item.row(),0))
            contador = item.rowCount()
            for k in range(contador):
                model.removeRow(0,item.index())
            for entrada in values:
                item.appendRow(makeRow(None,entrada))
        else:
            if isinstance(editor, QComboBox):
                dvalue = ivalue = editor.currentText() #Un poco valiente
                if dvalue in ('True','False'):
                    ivalue = str2bool(dvalue)            
            elif isinstance(editor, QSpinBox):
                ivalue = editor.value()
                dvalue = str(ivalue)
            elif isinstance(editor, QCheckBox):
                ivalue = editor.isChecked()
                dvalue = str(ivalue)
            elif isinstance(editor, WMultiCombo):
                dvalue = ivalue = editor.get()
            elif isinstance(editor,WPowerTable):
                return
            else:
                dvalue = ivalue = editor.text()
    
            if not self.validator(editor,dvalue,ivalue):
                print('Rechazada la validacion')
                return
            
            if not dvalue:
                model.setData(index,str(index.data(Qt.UserRole +1)),Qt.EditRole)
            else:
                model.setData(index,dvalue, Qt.EditRole)                
            model.setData(index,ivalue, Qt.UserRole +1)
            item = model.itemFromIndex(index.sibling(index.row(),0))
        
        setters = self.context.get('edit_tree',{}).get('setters',[])
        for funcion in setters:
            funcion(item,self.parent())

    def validator(self,editor,*lparms,**kwparms):
        if isinstance(editor,(WMultiList,)):
            values = lparms[0]
            if self.context.get('mandatory') and len(values) == 0:
                print('No hay entradas')
                return False
        else:
            dvalue,ivalue = lparms[0:2]
            if self.context.get('mandatory') and (ivalue is None or dvalue == ''):
                print('sin valor')
                return False
        validators = self.context.get('edit_tree',{}).get('validators',[])
        if len(validators) == 0:
            return True
        else:
            for entry in validators:
                if not validators(self.context.get('editPos'),editor,*lparms,**kwparms):
                    return False
        return True
                

import sys
def pruebaGeneral():
    app = QApplication(sys.argv)
    config.DEBUG = True
    form = ufTreeMgrWindow()
    form.show()
    #if form.exec_():
        #pass
        #sys.exit()
    sys.exit(app.exec_())

    
 
if __name__ == '__main__':
    #readConfig()
    #testSelector()
    #editAsTree()
    #tools = {}
    #pprint(readUM(uf))
    #pprint(tools)
    #print(readUM(uf))
    pruebaGeneral()
    #modelo =editAsTree()
            
            
    
        #print(getItemContext(item))



