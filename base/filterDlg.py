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


#from admin.dictmgmt.datadict import *    
#from PyQt5.QtGui import QGuiApplication

from PyQt5.QtCore import  Qt, QSortFilterProxyModel, QModelIndex, QSize
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QComboBox, QLabel, QPlainTextEdit, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout

#from support.datalayer.query_constructor import *
#from support.gui.dialogs import dataEntrySheetDlg
from support.gui.widgets import WDataSheet, WPowerTable
#from support.util.numeros import fmtNumber               
from admin.cubemgmt.cubeTypes import LOGICAL_OPERATOR
from support.util.numeros import is_number
from support.util.fechas import isDate

from support.datalayer.query_constructor import *

from support.util.cadenas import mergeStrings

        
class filterDialog(QDialog):
    """
       Esta clase NO tiene valores de entrada. Deben incluirse en la celda (x,3) dentro del llamador
       TODO en el caso de tener una guia, no podemos, de momento, aceptar valores multiples, y si es una jerarquia sólo = o !=
       #TODO permitir formatos distintos para las entradas jerarquicas
    """
    def __init__(self,recordStructure,title,parent=None,driver=None):
        super(filterDialog, self).__init__(parent)
        # cargando parametros de defecto
        self.record = recordStructure
        self.driver = driver
        self.context = []
        self.context.append(('campo','formato','condicion','valores'))
        self.context.append((QLineEdit,{'setEnabled':False},None))
        self.context.append((QLineEdit,{'setEnabled':False},None))
        self.context.append((QComboBox,None,tuple(LOGICAL_OPERATOR)))
        self.context.append((QLineEdit,None,None))
        self.data = []
        
        self.sheet=WPowerTable(len(recordStructure),4)

        cabeceras = [ item  for item in self.context[0] ]
        self.sheet.setHorizontalHeaderLabels(cabeceras)
        
        for k in range(len(self.record)):
            self.addRow(k)
        self.sheet.resizeRowsToContents()

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
        self.meatLayout = QGridLayout()
        buttonLayout = QHBoxLayout()
        formLayout = QVBoxLayout()
       
        self.meatLayout.addWidget(InicioLabel,0,0)
        self.meatLayout.addWidget(self.sheet,1,0,6,5)
        self.meatLayout.addWidget(freeSqlLbl,8,0)
        self.meatLayout.addWidget(self.freeSql,8,1,1,4)
        self.meatLayout.addWidget(self.mensaje,10,0,1,4)
        
        buttonLayout.addWidget(buttonBox)
        
        formLayout.addLayout(self.meatLayout)        
        formLayout.addLayout(buttonLayout)
        
        self.setLayout(formLayout)
        self.setMinimumSize(QSize(480,480))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

 
 
        #--- end super
        self.setMinimumSize(QSize(800,480))
        
        self.mensaje.setText(self.origMsg)
        self.defaultBackground = self.mensaje.backgroundRole()
        
        for k in range(4):
            self.sheet.resizeColumnToContents(k)
        
        #for k in range(self.sheet.rowCount()):
            #self.sheet.cellWidget(k,2).textChanged['QString'].connect(lambda b,a=k:self.checkData(b,a))
            
    #def checkData(self,content,pos):
    def addRow(self,line):
        data = dict2row(self.record[line],('name','format'))
        data.append(3)
        data.append(None)
        definicion = self.context[1:]
        if 'values' in self.record[line]:
            definicion[3] = (QComboBox,None,tuple([''] + [entry[1] for entry in self.record[line]['values']]))
        for y,colDef in enumerate(definicion):
            self.sheet.addCell(line,y,colDef,defVal=data[y])
        #FIXME esto deberia ir fuera del dialogo
        if self.record[line].get('class','o') == 'h':
            for k in range(len(LOGICAL_OPERATOR)):
                if k in (3,4):
                    continue
                else:
                    self.sheet.cellWidget(line,2).model().item(k).setEnabled(False)
        if 'values' in self.record[line]:
            self.sheet.cellWidget(line,2).model().item(0).setEnabled(False)
            self.sheet.cellWidget(line,2).model().item(1).setEnabled(False)
            self.sheet.cellWidget(line,2).model().item(9).setEnabled(False)
            self.sheet.cellWidget(line,2).model().item(10).setEnabled(False)

                    
    def accept(self):
        self.mensaje.setText(self.origMsg)
        fallo = False
        errorTxt = ''
        self.queryArray = []
        for pos in range(self.sheet.rowCount()):
            item = [self.sheet.get(pos,k) for k in range(4) ]
            item[0]= norm2List(self.record[pos].get('source',item[0]))
            opcode = LOGICAL_OPERATOR[item[2]].lower()
            if opcode in ('is null','is not null'): #TODO, esto no es así
                self.queryArray.append((item[0],
                                    opcode.upper(),
                                    None,None))
                continue
            if not item[3] or item[3] == '':  #Se nota que vengo de Oracle. Aparte del null no se que casos no necesitan parametro de datos
                continue
            if 'values' in self.record[pos]:  # viene de un combobox
                if item[3] == 0: # sin valor
                    continue
                else:
                    aslist = self.record[pos]['values'][item[3] -1][0]
            else:
                aslist = item[3].split(',')
            aslist = norm2List(aslist)
            #primero comprobamos la cardinalidad. Ojo en sentencias separadas o el elif no funciona bien
            if opcode in ('between','not between'): 
                if len(aslist) != 2:
                    errorTxt = 'La operacion between exige exactamente dos valores'
                    fallo = True
            elif opcode not in ('in','not in') :
                if len(aslist) != 1:
                    errorTxt = ' La operacion elegida exige un único valor'
                    fallo = True
            # chequeamos los formatos. Por comodidad solo el primer elemento de la lista. Los no reconocidos no chequeados
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
                self.sheet.cellWidget(pos,3).setFocus()
                return

            qfmt = 't'     
            if formato in ('entero','numerico'):
                qfmt = 'n'
            elif formato in ('fecha','fechahora','hora'):
                qfmt = 'f'
            elif formato in ('booleano'):
                qfmt = 'n' #me parece 
                
            if len(item[0]) > 1:
                datos = aslist[0].split(':')
                for k,campo in enumerate(item[0]):
                    if k >= len(datos):
                        break 
                    self.queryArray.append((campo,
                                        opcode.upper(),
                                        datos[k],
                                        qfmt))
            else:
                self.queryArray.append((norm2String(item[0]),
                                    opcode.upper(),
                                    aslist[0] if len(aslist) == 1 else aslist,
                                    qfmt))

        self.result = mergeStrings('AND',
                                    searchConstructor('where',where=self.queryArray,driver=self.driver),
                                    self.freeSql.text(),
                                    spaced=True)
        print(self.result)
        self.data = self.sheet.values()
                
        QDialog.accept(self)
        
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
