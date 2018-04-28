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
from support.gui.widgets import WMultiCombo,WPowerTable, WMultiList, WNameValue
from support.util.record_functions import norm2List,norm2String
import base.config as config

from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QTreeView, QSplitter, QMenu, \
     QDialog, QInputDialog, QLineEdit, QComboBox, QMessageBox,QGridLayout, \
     QAbstractItemView, QTableView, QStyledItemDelegate, QSpinBox, QListWidget, QPushButton, QVBoxLayout,QLabel, QWidget, QCheckBox

from research.ufTreeUtil import *
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

def isDictFromDef(item):
    """
    determina si el nodo es la cabeza de un diccionario viendo como son los hijos.
    Es demasiado simple para otra cosa que lo que tenemos
    
    FIXME depende de getItemContext()
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
    
"""
Callbacks del editor
"""
def funclist(*lparm):
    return list(readUM(uf).keys())
def modlist(*lparm):
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
from research.treeEditor import *


class ufTreeMgrWindow(QMainWindow):
    """
    """
    def __init__(self,parent=None):
        super(ufTreeMgrWindow,self).__init__(parent)
        self.cubeFile = 'danacube.json'
        self.tree = TreeMgr(editAsTree(self.cubeFile),
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            getItemContext)
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
        self.cubeFile = 'danacube.json'
        self.tree = TreeMgr(editAsTree(self.cubeFile),
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            getItemContext)
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



