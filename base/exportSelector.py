#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


para validar contenido
definir una señal validate 
en el slot de validate
   validar el primero
        en la validacion invocar a la señal recursivamente
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os
from pprint import pprint

#import user as uf
from support.util.uf_manager import *
from support.util.jsonmgr import *

from support.gui.widgets import *
import base.config as config

from PyQt5.QtCore import Qt, QSize,QRegExp
from PyQt5.QtGui import QStandardItem, QRegExpValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog,QGridLayout,   \
     QLineEdit, QComboBox, QMessageBox, QSpinBox, QLabel, QCheckBox, QStatusBar, QDialogButtonBox

from support.util.treeEditorUtil import *
"""
Funciones para leer la configuracion de user functions. Reutilizadas, creo
"""



def isDictFromDef(item):
    """
    determina si el nodo es la cabeza de un diccionario viendo como son los hijos.
    Es demasiado simple para otra cosa que lo que tenemos
    
    FIXME depende de getItemContext()
    """
    if item.hasChildren():
        contexto = Context(item)
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
def setFileType(editor,*lparm):
    item = lparm[0]
    view = lparm[1]
    if len(lparm) > 2:   
        context = lparm[2] 
    else:
        context = Context(item)
    if not editor.selectedFiles():
        return     
    tipo = editor.getFileType()
    pai = item.parent()
    tipoItem = getChildByType(pai,'type')
    tipoDataItem = getRow(tipoItem)[1]
    tipoDataItem.setData(tipo,Qt.UserRole +1)
    tipoDataItem.setData(tipo,Qt.DisplayRole)
    
    
def setCharacters(editor,*lparm):
    item = lparm[0]
    view = lparm[1]
    if len(lparm) > 2:   
        context = lparm[2] 
    else:
        context = Context(item)
    tipActua = context.get('type')
    valActua  = getRow(item)[1].data()

    pai = item.parent()
    valores = dict()
    categorias = ('decChar','txtSep','fldSep')
    for cat in categorias:
        if cat == tipActua:
            continue
        valores[cat] = getRow(getChildByType(pai,cat))[1].data()

    for cat in valores:
        if valActua == valores[cat]:
            #aqui viene el mogollon
            print('Duplicado')
            view.msgLine.setText('Los valores para {} y {} son identicos y eso es imposible'.format(tipActua,cat))
            view.setCurrentIndex(getRow(getChildByType(pai,cat))[1].index())
        else:
            continue
   

#en orden alfafetico
FORMATOS = {
     "csv":"CSV (*.csv)",
     "xls":"Excel (*.xlsx)",
     "html":"HTML (*.html)",
     "json":"Json (*.json)",
     }
FILTROS = [ FORMATOS[tipo] for tipo in sorted(FORMATOS)]
TIPOS = [ tipo for tipo in sorted(FORMATOS)]
class MyFileDialog(QFileDialog):
    from pathlib import Path
    def __init__(self,parent,*lparm,**kwparm):
        super().__init__(parent)
        self.filename = None
        self.parms = {}
    #def getSaveFileName(self,*lparm,**kwparm):
        self.parms['caption']="Nombre del fichero"
        filters = FILTROS
        datadir = Path.cwd() / "datos"
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.setFileMode(QFileDialog.AnyFile)
        self.setDirectory(str(datadir))
        self.setNameFilters(filters)
        defaultFilter = FILTROS[0]
        self.selectNameFilter(defaultFilter)
        #suffix = defaultFilter.split(' ')[0].split('.')[-1]
        #self.setDefaultSuffix(suffix)
        
        #self.filterSelected.connect(self.selFilter)
  
    #def selFilter(self,filter):
        #suffix = filter.split(' ')[0].split('.')[-1]
        #self.setDefaultSuffix(suffix)
    
    def setData(self,dato):
        self.selectFile(dato)
    
    def getData(self):
        #print('getData',self.selectedFiles(),self.selectedNameFilter())
        if self.selectedFiles():
            return self.selectedFiles()[0]
        else:
            return None
        
    def getFileType(self):
        filtroActivo = self.selectedNameFilter()
        Pos = FILTROS.index(filtroActivo)
        if Pos is not None:
            return TIPOS[Pos]
        else:
            return filtroActivo.split(' ')[0]  #no se yo si es buena idea
        

"""

Nuevo mojo del arbol

no example of validators attribute 
elements list is (element name,mandatory,readonly,repeatable)
still no process for repeatable 
class & name are not to be edited (even shown) as derived DONE
"""
puntuacion = (' ',',',';',':','.','\/')
punctuationRe = QRegExp(r"[ ,;:.'\"\/]")
decimalRe = QRegExp(r"[,.]")

TOP_LEVEL_ELEMS = []
EDIT_TREE = {
    'type':{'editor':WComboBox,'source':TIPOS,'text':'Formato de datos' },
    'file':{'editor':MyFileDialog,'setters':('default',setFileType),'text':'Fichero de descarga'},
    'csvProp': {'objtype':'dict','text':'Caracteres especiales',
                'elements': [
                    ('fldSep',False,False),
                    ('decChar',False,False),
                    ('txtSep',False,False),
                ] },
    'fldSep': {'editor':WComboBox,'source':puntuacion,'options':{'setEditable':True},
                    #'edit':QLineEdit,'options':{'setMaxLength':1,'setValidator':QRegExpValidator(punctuationRe) },
                    'default':';','text':'Delimitador de campos',
                    'setters':('default',setCharacters),
                  },
                       #self.separadorCampos.setMaxLength(1)
        #self.separadorCampos.setValidator(QRegExpValidator(punctuationRe,self))
        #self.separadorCampos.setText(';')

    'decChar':{'editor':WComboBox,'source':('.',','),'default':'.','text':'Carácter decimal',
                    'setters':('default',setCharacters),},
    'txtSep': {'editor':WComboBox,'source':puntuacion,'options':{'setEditable':True},
                #'editor':QLineEdit,'options':{'setMaxLength':1,'setValidator':QRegExpValidator(punctuationRe) },
               'default':'"','text':'Separador de textos',
                'setters':('default',setCharacters),},
    'filter':{'objtype':'dict','text':'Datos a descargar','elements':[
            ('scope',True,False),
            ('row',True,False),
            ('col',True,False),
        ]},
    'row':{'objtype':'dict','text':'Filas','elements':[
            ('content',True,False),
            ('totals',True,False),
            ('Sparse',True,False)
        ]},
    'col':{'objtype':'dict','text':'Columnas','elements':[
            ('content',True,False),
            ('totals',True,False),
            ('Sparse',True,False)
        ]},
    'content':{'editor':WComboBox,'source':('full','branch','leaf') },
    'totals':{'editor':QCheckBox,'text':'Con totalizadores' },
    'Sparse':{'editor':QCheckBox,'text':'Cabeceras sin repeticiones' },
    'scope':{'editor':WComboBox,'source':('all','visible'),'text':'Ambito de descarga' ,'default':'visible'},
    'NumFormat':{'editor':QCheckBox,'text':'Formateo de números' }
    
}
    
def editAsTree(dataDict):
    #
    # Como no hay datos prealmacenados, es una manera de definir los defectos y la estructura de presentacion
    #
    deffile = Path.cwd() / "datos" / "download.csv"
    if not dataDict:
        dataDict = {'file': str(deffile),
                            'type': 'csv',
                            'filter': {'scope': 'visible',
                                        'row': {'Sparse': True, 'content': 'leaf', 'totals': False},
                                        'col': {'Sparse': True, 'content': 'leaf', 'totals': False},
                                        },
                            'csvProp': {'decChar': ',', 'fldSep': ';', 'txtSep': '"'},
                            'NumFormat': False,


                            }
    
    model = displayTree()
    model.setItemPrototype(QStandardItem())
    model.setHorizontalHeaderLabels(['Nombre','Contenido','Tipo'])
    hiddenRoot = model.invisibleRootItem()
    parent = hiddenRoot
    entrada = 'Parametros de exportacion'
    tipo=None
    dict2tree(parent,entrada,dataDict,tipo,ordenado=False)
    return model

            
        
        
    #return {
            #'rowHead':n,
            #'name':n.data(),
            #'data':d.data(),
            #'type':t.data() if t else None,
            #'dtype':dataType,
            #'topLevel':isTopLevel,
            #'listMember':isListMember,
            #'editPos': editPosition,
            #'editType':editType,
            #'mandatory':isMandatory,
            #'readonly':isReadOnly,
            #'edit_tree':EDIT_TREE.get(t.data() if t else tp.data(),{})
            #}
    ##print('datos ->{}:{} ({})  tipo:{} TopLevel:{}, ListMember:{} edit type {} and edit position {}'.format(
            ##n.data(),d.data(),t.data() if t else None,
            ##dataType,isTopLevel,isListMember,
            ##editType.data(), editPosition.data()
          ##))
    
    
"""
Funciones GUI principales 
"""
from support.gui.treeEditor import *




class exportDialog(QDialog):
    """
    """
    def __init__(self,data=None,parent=None):
        super().__init__(parent)

        Context.EDIT_TREE = EDIT_TREE
        
        self.msgLine = QLabel()
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        self.data = data
        self.tree = TreeMgr(editAsTree(self.data),
                                            EDIT_TREE,
                                            TOP_LEVEL_ELEMS,
                                            Context,
                                            msgLine=self.msgLine)
        meatLayout = QGridLayout()
        self.tree.expandAll()
        self.tree.hideColumn(2)
        meatLayout.addWidget(self.tree,0,0)
        meatLayout.addWidget(self.msgLine,1,0)
        meatLayout.addWidget(buttonBox)
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(640,570))
        
        
    def accept(self):
        """
        cuando salgo por ok, no pregunto, salvo directamente
        
        """
        if self.saveDialog():
            definiciones = tree2dict(self.tree.model().invisibleRootItem(),isDictFromDef)
            self.resultado = definiciones['Parametros de exportacion']
            super().accept()
        else:
            self.resultado = None
            super().reject()
            
    def closeEvent(self,event):
        self.close()
        
    def close(self):

        return True
 

    def saveDialog(self):
        if (QMessageBox.question(self,
                "Salvar",
                "Desea salvar los cambios de configuracion ?",
                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes):
            return True
        else:
            return False
 


import sys
def pruebaGeneral():
    app = QApplication(sys.argv)
    config.DEBUG = True
    form = exportDialog()
    form.show()
    if form.exec_():
        pass
        sys.exit()
    sys.exit()
    #sys.exit(app.exec_())

    
 
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



