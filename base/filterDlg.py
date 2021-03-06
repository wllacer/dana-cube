#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
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


#from admin.dictmgmt.datadict import *    
#from PyQt5.QtGui import QGuiApplication

from PyQt5.QtCore import  Qt, QSortFilterProxyModel, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QComboBox, QLabel, QPlainTextEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout

#from support.datalayer.query_constructor import *
#from support.gui.dialogs import dataEntrySheetDlg
from support.gui.widgets import *
#from support.util.numeros import fmtNumber               
from admin.cubemgmt.cubeTypes import LOGICAL_OPERATOR
from support.util.numeros import is_number
from support.util.fechas import isDate

from support.datalayer.query_constructor import *

from support.util.cadenas import mergeStrings

        
        
        
class filterDialog(QDialog):
    """
        FIXME existe duda si en guias jerarquicas filtra con toda la amplitud
    """
    def __init__(self,recordStructure,currentData,title,parent=None,driver=None):
        super().__init__(parent)
        # cargando parametros de defecto
        self.record = recordStructure
        self.campos = [ elem['name'] for elem in recordStructure ]
        self.formatos =[ elem['format'] for elem in recordStructure ]
        self.driver = driver
        self.context = []
        self.context.append(('campo','formato','condicion','valores'))
        self.context.append((None,WComboBox,None,self.campos))
        self.context.append((None,QLineEdit,{'setEnabled':False},None))
        self.context.append(('=',WComboBox,None,tuple(LOGICAL_OPERATOR)))
        self.context.append((None,QLineEdit,None,None))
        self.data = []
        
        self.sheet = WDataSheet(self.context,len(recordStructure))
        cabeceras = [ item  for item in self.context[0] ]
        self.sheet.verticalHeader().hide()
        self.sheet.setHorizontalHeaderLabels(cabeceras)
                
        self.sheet.initialize()
        self.load(currentData)
        for i in range(self.sheet.rowCount()):
            #for j in range(2):
            self.sheet.item(i,1).setBackground(QColor(Qt.gray))
        #for k in range(len(self.record)):
            #self.addRow(k)
        self.sheet.resizeRowsToContents()
        self.sheet.horizontalHeader().setStretchLastSection(True)
        
        self.origMsg = 'Recuerde: en SQL el separador decimal es el punto "."'
        # super(filterDialog,self).__init__('Defina el filtro',self.context,len(self.data),self.data,parent=parent) 

        InicioLabel = QLabel(title)
        #
        
        self.mensaje = QLineEdit('')
        self.mensaje.setReadOnly(True)
        
        freeSqlLbl = QLabel('Texto Libre')
        self.freeSql  = QLineEdit() #QPlainTextEdit()

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)

        #formLayout = QHBoxLayout()
        #self.meatLayout = QVBoxLayout()
        self.meatLayout = QVBoxLayout() #QGridLayout()
        buttonLayout = QHBoxLayout()
        formLayout = QVBoxLayout()
       
        self.meatLayout.addWidget(InicioLabel) #,0,0)
        self.meatLayout.addWidget(self.sheet) #,1,0,6,5)
        self.meatLayout.addWidget(freeSqlLbl) #,8,0)
        self.meatLayout.addWidget(self.freeSql) #,8,1,1,4)
        self.meatLayout.addWidget(self.mensaje) #,10,0,1,4)
        
        buttonLayout.addWidget(buttonBox)
        
        formLayout.addLayout(self.meatLayout)        
        formLayout.addLayout(buttonLayout)
        
        self.setLayout(formLayout)
        self.setMinimumSize(QSize(480,480))
        
        self.sheet.itemChanged.connect(self.cambioCampo)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle(title)
        

 
 
        #--- end super
        self.setMinimumSize(QSize(800,480))
        
        self.mensaje.setText(self.origMsg)
        self.defaultBackground = self.mensaje.backgroundRole()
        
        #for k in range(4):
            #self.sheet.resizeColumnToContents(k)
        
    def load(self,currentData):
        data = []
        if not currentData:
            return
        for item in currentData:
            if item[0]:
                #FIXME y si el campo no existe porque es calculado ¿? editable, etc ...
                linea = item[:]
                if not linea[1]:
                    linea[1] = self.formatos[self.campos.index(item[0])]
                if not linea[2]:
                    linea[2] = '='
                data.append(linea)
            else:
                continue
        self.sheet.loadData(data)
        
    def cambioCampo(self,item):
        if item.column() != 0:
            return 
        if item.text() == '':
            return
        pos = self.campos.index(item.text())
        self.sheet.setData(item.row(),1,self.formatos[pos])
        
    def accept(self):
        self.mensaje.setText(self.origMsg)
        fallo = False
        errorTxt = ''
        self.queryArray = []
        values = self.sheet.unloadData()
        for pos,item in enumerate(values):
            opcode = item[2]
            values = item[3]
            if opcode in ('is null','is not null'): #TODO, esto no es así
                self.queryArray.append((item[0],
                                    opcode.upper(),
                                    None,None))
                continue
            if not values: # or item[3] == '':  #Existe  de datos
                continue
            aslist = norm2List(values)
            #primero comprobamos la cardinalidad. Ojo en sentencias separadas o el elif no funciona bien
            if opcode in ('between','not between'): 
                if len(aslist) != 2:
                    errorTxt = 'La operacion between exige exactamente dos valores'
                    fallo = True
            elif opcode not in ('in','not in') :
                if len(aslist) != 1:
                    errorTxt = ' La operacion elegida exige un único valor'
                    fallo = True
            
            if not fallo:
                testElem = aslist[0].lower().strip()
                formato = item[1]
                if formato in ('numerico','entero') and not is_number(testElem):
                    # vago. no distingo entre ambos tipos numericos FIXME
                    errorTxt = 'No contiene un valor numerico aceptable'
                    fallo = True
                #elif formato in ('texto','binario'):
                    #pass
                elif formato in ('booleano',) and testElem not in ('true','false'):
                    errorTxt = 'Solo admitimos como booleanos: True y False'
                    fallo = True
                elif formato in ('fecha','fechahora','hora') and not isDate(testElem):
                    errorTxt = 'Formato o fecha incorrecta. Verifique que es del tipo AAAA-MM-DD HH:mm:SS'
                    fallo = True
                else:
                    pass

            if fallo:
                self.mensaje.setText('ERROR @{}: {}'.format(item[0],errorTxt))
                #self.sheet.cellWidget(pos,3).selectAll()  FIXME ¿que hay para combos ?
                self.sheet.setCurrentCell(pos,3)
                self.sheet.setFocus()
                return
            qfmt = 't'     
            if formato in ('entero','numerico'):
                qfmt = 'n'
            elif formato in ('fecha','fechahora','hora'):
                qfmt = 'f'
            elif formato in ('booleano'):
                qfmt = 'n' #me parece 
                
            self.queryArray.append((item[0],
                                opcode.upper(),
                                aslist[0] if len(aslist) == 1 else aslist,
                                qfmt))

        self.result = mergeStrings('AND',
                                    searchConstructor('where',where=self.queryArray,driver=self.driver),
                                    self.freeSql.text(),
                                    spaced=True)
        self.data = self.sheet.values()
        QDialog.accept(self)
        
        
class fullFilterDialog(filterDialog):
    """
    clase inactiva. Mantenida por si en algun momento merece la pena reutilizarla en otro contexto
    TODO adaptarla a la sintaxis de la siguiente
    
    """
    def __init__(self,recordStructure,currentData,title,parent=None,driver=None):
        super().__init__(recordStructure,currentData,title,parent,driver)
        self.context[1] = (None,QComboBox,{'setEnabled':False},self.campos)
        
    def load(self,currentData):
        #TODO y si el campo aparece mas de una vez ¿?
        data = []
        if currentData:
            campos = [ elem[0] for elem in currentData ]
        for item in self.record:
            linea = [ None for k in range(self.sheet.columnCount()) ]
            linea[0] = item['name']
            linea[1] = item['format']
            if currentData:
                pos = campos.index(item['name'])
                linea[2:] = currentData[pos][2:]
                
            data.append(linea)
        self.sheet.loadData(data)
        for i in range(self.sheet.rowCount()):
            self.sheet.item(i,0).setFlags(Qt.ItemIsSelectable )

                

def main():
    app = QApplication(sys.argv)
    record = [  {'format': 'entero', 'name': 'film.film_id'},
                {'format': 'texto', 'name': 'film.title'},
                {'format': 'texto', 'name': 'film.description'},
                {'format': 'YEAR(4)', 'name': 'film.release_year'},
                {'format': 'entero', 'name': 'film.language_id'},
                #{'format': 'entero', 'name': 'language_0.language_id'},
                #{'format': 'texto', 'name': 'language_0.name'},
                #{'format': 'fecha', 'name': 'language_0.last_update'},
                {'format': 'entero', 'name': 'film.original_language_id'},
                #{'format': 'entero', 'name': 'language_1.language_id'},
                #{'format': 'texto', 'name': 'language_1.name'},
                #{'format': 'fecha', 'name': 'language_1.last_update'},
                {'format': 'entero', 'name': 'film.rental_duration'},
                {'format': 'numerico', 'name': 'film.rental_rate'},
                {'format': 'entero', 'name': 'film.length'},
                {'format': 'numerico', 'name': 'film.replacement_cost'},
                {'format': 'texto', 'name': 'film.rating'},
                {'format': 'texto', 'name': 'film.special_features'},
                {'format': 'fecha', 'name': 'film.last_update'}]

    form = filterDialog(record,'Version experimental',driver='oracle')
    form.show()
    if form.exec_():
        pprint(form.result)
        #pepe = dict()
        #pepe['tables'] = 'sakila.film'
        #pepe['fields'] = [ item['name'] for item in record ]
        #pepe['where'] = form.result['where']
        #pepe['filter'] = form.result.get('filter')
        #print(queryConstructor(**pepe))
        #cdata = [form.context[k][1] for k in range(len(parametros))]
        #print('a la vuelta de publicidad',cdata)
        sys.exit()

if __name__ == '__main__':
        # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    main()
