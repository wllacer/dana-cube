#!/usr/bin/python
# -*- coding: utf-8 -*-
## Copyright (c) 2012,2016 Werner Llacer. All rights reserved.. Under the terms of the LGPL 2
## numberFormatDlg inspired by Portions copyright (c) 2008 Qtrac Ltd. All rights reserved.. Under the terms of the GPL 2

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
#from future_builtins import *

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pprint import pprint

from support.gui.widgets import * 
from support.util.numeros import is_number
 
"""
  config.DEBUG DATA start
"""
cubo = None



class propertySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
    """
    def __init__(self,title,context,data,parent=None):   
        super(propertySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet(context,data)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)

        self.errorMsg = QLabel('')
        
        #formLayout = QHBoxLayout()
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        
       
        meatLayout.addWidget(InicioLabel)
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.errorMsg)
        
        #formLayout.addLayout(meatLayout)        
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(480,310))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

    def accept(self):
        self.resetError()
        datos = self.sheet.values()
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.data[k] = valor
        QDialog.accept(self)

    def inlineError(self,text,widget):
        """
        Funcion para presentar errores en propertySheetDlg
        
        """
        widget.setFocus()
        self.errorMsg.setText(text)
        self.errorMsg.setStyleSheet("background-color:yellow;")
        
    def resetError(self):
        self.errorMsg.setText('')
        self.errorMsg.setStyleSheet(None)


from support.util.fechas import *

class dateFilterDlg(QDialog):
    def __init__(self,parent=None,**kwparm):
    #def __init__(self,descriptores=None,datos=None,parent=None):   
        """
        """
        
        if kwparm and not kwparm.get('descriptores'):
            return 
        #else:
            #self.descriptores = descriptores
        self.descriptores = []
        self.data = []
        self.result = None
        
        super(dateFilterDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = [ ( None ,), #['\t {}'.format(k) for k in descriptores ],
                                (0,WComboBoxIdx,None,CLASES_INTERVALO),
                                (None,WComboBoxIdx,None,TIPOS_INTERVALO),
                                (1,QSpinBox,{"setRange":(1,366)},None),
                                (None,QLineEdit,{"setEnabled":False},None),
                                (None,QLineEdit,{"setEnabled":False},None),
                                ]
        rows = 5 #len(self.context[0])
        cols = 5 #len(self.context) -1
        self.sheet = WDataSheet(self.context,rows)
        self.sheet.itemChanged.connect(self.validateEntry)
        
        if kwparm:
            self.setData(kwparm)
            
        #for i in range(self.sheet.rowCount()):
            #for j in range(3,5):
                #self.sheet.item(i,j).setBackground(QColor(Qt.gray))

        #self.data = datos
        #for row,entry in enumerate(self.data):
            #for col,dato in enumerate(entry):
                #if col == 0 and dato is not None:
                    #self.sheet.setData(row,col,[dato,CLASES_INTERVALO[dato]],split=True)
                    #if dato == 0:
                        #break
                #elif col == 1 and dato is not None:
                    #self.sheet.setData(row,col,[dato,TIPOS_INTERVALO[dato]],split=True)
                #elif dato is not None:
                    #self.sheet.setData(row,col,dato)
                #elif col == 2 and not dato:
                    #self.sheet.setData(row,col,1)
            #self._validateEntry(row,0)
            

        
        cabeceras = ('Tipo','Periodo','Rango','desde','hasta')
        self.sheet.setHorizontalHeaderLabels(cabeceras)
        #
        InicioLabel1 = QLabel('Filtre el rango temporal que desea')

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)


        self.msgLine = QLabel("")
        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        

        meatLayout.addWidget(InicioLabel1)
        meatLayout.addWidget(self.sheet)
        meatLayout.addWidget(self.msgLine)
       
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(800,200))
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")

    def setData(self,kwparm):
        self.descriptores = kwparm.get('descriptores',[])
        self.data = kwparm.get('datos',[])
        if not self.descriptores:
            self.reject()

        self.sheet.itemChanged.disconnect()
        
        self.sheet.setRowCount(len(self.descriptores))
        self.sheet.setVerticalHeaderLabels([ nombre.split('.')[-1] for nombre in self.descriptores] )
        
        for i in range(self.sheet.rowCount()):
            for j in range(3,5):
                self.sheet.item(i,j).setBackground(QColor(Qt.gray))
        for row,entry in enumerate(self.data):
            for col,dato in enumerate(entry):
                if col == 0 and dato is not None:
                    self.sheet.setData(row,col,[dato,CLASES_INTERVALO[dato]],split=True)
                    if dato == 0:
                        break
                elif col == 1 and dato is not None:
                    #self.sheet.setData(row,col,dato)
                    self.sheet.setData(row,col,[dato,TIPOS_INTERVALO[dato]],split=True)
                elif dato is not None:
                    self.sheet.setData(row,col,dato)
                elif col == 2 and not dato:
                    self.sheet.setData(row,col,1)
            self._validateEntry(row,0)
    
        self.sheet.itemChanged.connect(self.validateEntry)
            
        
    def _validateEntry(self,row,col):
            dato = self.sheet.get(row,col)
            if col in (0,):
                self.flipFlop(row,dato)
                self.seleccionIntervalo(dato,row)
            elif col in (1,):
                self.seleccionIntervalo(dato,row)
            elif col in (2,):
                self.seleccionIntervalo(dato,row)
        
    #def validateEntry(self,row,col):
    def validateEntry(self,item):
        row = item.row()
        col =  item.column()
        self.sheet.itemChanged.disconnect()
        self.msgLine.setText("")
        self._validateEntry(row,col)
        self.sheet.itemChanged.connect(self.validateEntry)
        
            
    def flipFlop(self,line,value):
        # puede ser un poco repetitivo, pero no se si es mas costoso el enable/disable que comprobar cada
        # vez si lo esta. Por lo menos el codigo es menos complejo y todavia no veo una razon para modificarlo
        if not is_number(value):
            return
        if value == 0:
            self.sheet.setEnabled(line,1,False)
            self.sheet.setEnabled(line,2,False)
        elif value == 1: 
            self.sheet.setEnabled(line,1,True)
            self.sheet.setEnabled(line,2,False)
        else:
            self.sheet.setEnabled(line,1,True)
            self.sheet.setEnabled(line,2,True)
        # ponemos los valores ejemplo


    def seleccionIntervalo(self,value,idx):
        self.sheet.set(idx,3,None)
        self.sheet.set(idx,4,None)
        clase = self.sheet.getData(idx,0,USER)
        tipo = self.sheet.getData(idx,1,USER)
        numper = self.sheet.get(idx,2) 
        if clase: 
            if tipo is not None:
                if not numper:
                    self.sheet.set(idx,2,1)
                    if clase > 1:
                        self.sheet.setCurrentCell(idx,2)
                        self.msgLine.setText("Especifique el numero de intervalos que desea para {}".format(CLASES_INTERVALO[clase]))
                        self.sheet.setFocus()
                    numper = 1
                
                desde,hasta = dateRange(clase,tipo,periodo=numper)
                self.sheet.set(idx,3,str(desde))
                self.sheet.set(idx,4,str(hasta))
            else:
                self.sheet.setCurrentCell(idx,1)
                self.msgLine.setText("Debe especificar un intervalo para {}".format(CLASES_INTERVALO[clase]))
                self.sheet.setFocus()
   
    def accept(self):
        #self.data = self.sheet.values()
        if not self.validate():
            return
        self.result = {'datos':self._getData()}

        QDialog.accept(self)
    
    def reject(self):
        self.result = {'cancel':True }
        QDialog.reject(self)
        
    def getData(self,reject=False):
        if self.result:
            return self.result
        else:
            self.result = {'datos':self._getData()}
        
    def _getData(self):
        result = self.sheet.values()
        for k in range(len(result)):
            result[k].insert(0,self.descriptores[k])
        return result
        
    def validate(self):
        self.msgLine.setText("")
        for row,entrada in enumerate(self.sheet.values()):
            clase = entrada[0]
            tipo = entrada[1]
            numper = entrada[2]
            if clase: 
                if tipo is not None:
                    if not numper:
                        if clase > 1:
                            self.sheet.setCurrentCell(row,2)
                            self.msgLine.setText("Especifique el numero de intervalos que desea para {}".format(CLASES_INTERVALO[clase]))
                            self.sheet.setFocus()
                            return False
                else:
                    self.sheet.setCurrentCell(row,1)
                    self.msgLine.setText("Debe especificar un tipo de intervalo para {}".format(CLASES_INTERVALO[clase]))
                    self.sheet.setFocus()
                    return False
        return True

class dataEntrySheetDlg(QDialog):
    """
        NO consta que se use
       Genera (mas o menos) una hoja de entrada de datos
       
    """
    def __init__(self,title,context,numrows,data,parent=None):   
        super(dataEntrySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WDataSheet(context,numrows)
        self.sheet.fill(data)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)

        #formLayout = QHBoxLayout()
        self.meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        formLayout = QVBoxLayout()
       
        self.meatLayout.addWidget(InicioLabel)
        self.meatLayout.addWidget(self.sheet)
        
        buttonLayout.addWidget(buttonBox)
        
        formLayout.addLayout(self.meatLayout)        
        formLayout.addLayout(buttonLayout)
        
        self.setLayout(formLayout)
        self.setMinimumSize(QSize(480,480))
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        

    def accept(self):
        tmp_data = self.sheet.values()
        for x in range(self.sheet.rowCount()):
            for y in range(self.sheet.columnCount()):
                self.data[x][y] = tmp_data[x][y]
        QDialog.accept(self)

class CuboDlg(QDialog):
    def __init__(self, dict_cubos, parent=None):
        super(CuboDlg, self).__init__(parent)
        
        self.definiciones = dict_cubos
        InicioLabel = QLabel("Seleccione y conectese a un cubo")
        cuboLbl = QLabel("&Cubo")
        self.cuboCB = QComboBox()
        self.cuboCB.addItems(sorted(self.definiciones.keys()))
        cuboLbl.setBuddy(self.cuboCB)
 
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                                        QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(InicioLabel, 0, 0)
        grid.addWidget(cuboLbl, 1, 0)
        grid.addWidget(self.cuboCB, 1, 1)
        grid.addWidget(buttonBox, 4, 0, 1, 2)


        self.setLayout(grid)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
class GraphDlg(QDialog):
    def __init__(self, currValue, tipo='row',parent=None):
        super(GraphDlg, self).__init__(parent)
        self.tiposGraficos = ( (None,'Ninguno'),
                          ('scatter','Grafico de puntos'),
                          ('bar','Grafico de barras'),
                          ('barh',' idm. vertical'),
                          ('multibar',' idm. comparado a superiores en jerarquia'),
                          ('pie','Gráfico en forma de tarta'),
                          ('boxplot','Boxplot'),
                          )
        InicioLabel = QLabel("Seleccione el formato grafico que desea")
        cuboLbl = QLabel("&Cubo")
        self.cuboCB = QComboBox()
        self.cuboCB.addItems([item[1] for item in self.tiposGraficos])
        self.cuboCB.setCurrentIndex([item[0] for item in self.tiposGraficos].index(currValue))
        cuboLbl.setBuddy(self.cuboCB)

        self.elementoRB = QCheckBox('Sólo filas terminales (hojas)')
        
        self.elementoRB.setVisible(False)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|
                                                        QDialogButtonBox.Cancel)

        grid = QGridLayout()
        grid.addWidget(InicioLabel, 0, 0)
        grid.addWidget(cuboLbl, 1, 0)
        grid.addWidget(self.cuboCB, 1, 1)
        grid.addWidget(self.elementoRB,2,0)
        grid.addWidget(buttonBox, 4, 0, 1, 2)

        if tipo == 'col':
            self.elementoRB.setVisible(True)

        self.setLayout(grid)
        
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
    def accept(self):
        self.result = self.tiposGraficos[self.cuboCB.currentIndex()][0]
        self.hojas  = self.elementoRB.isChecked()
        
        QDialog.accept(self)
        
class VistaDlg(propertySheetDlg):
    def __init__(self, cubo,parametros,parent=None):
        title = 'Eliga los parametros de la vista'
        self.data = parametros
        self.context = []
        self.context.append(('Guia filas',WComboBoxIdx,None,cubo.getGuideNames()),)
        self.context.append(('Guia columnas',WComboBoxIdx,None,cubo.getGuideNames()),)
        self.context.append(('Función agregacion',WComboBox,None,cubo.getFunctions()),)
        self.context.append(('Campo de datos',WComboBox,None,cubo.getFields()),)
        self.context.append(('Con totales',QCheckBox,None),)
        self.context.append(('Con estadisticas',QCheckBox,None),)
        
        super(VistaDlg, self).__init__(title,self.context,parametros,parent)
        self.setWindowTitle(title)
        #self.sheet.resizeColumnsToContents()
        
    def accept(self):
        self.resetError()
        datos = self.sheet.values()
        if any (k is None for k in datos[0:4]):
        #if any(k < 0 for k in datos[0:4]):
            pos = datos[0:4].index(None)
            self.sheet.setCurrentCell(pos,0)
            self.inlineError('{} debe tener valor'.format(self.context[pos][0]),self.sheet)
            return
        for k,valor in enumerate(datos):
            if valor == '' and self.context[k][1] is None:
               continue
            self.data[k] = valor
        self.sheet.setCurrentCell(0,0)
        QDialog.accept(self)

        
        


class NumberFormatDlg(QDialog):
    def __init__(self, format, callback, parent=None):
        super(NumberFormatDlg, self).__init__(parent)

        punctuationRe = QRegExp(r"[ ,;:.']")
        
        self.context=[]
        """
           context[0] titulos de las filas
           context[1] widget a utilizar (defecto QLineEdit)
           context[2] llamadas de configuracion del widget
           context[3] signal,slots (me temo que a mano)
        """
        self.context = (
                        ("Thousands separator",
                            QLineEdit,
                            {'setMaxLength':1,'setValidator':QRegExpValidator(punctuationRe, self)},
                            None,
                        ),
                        ("Decimal marker",
                            QLineEdit,
                            {'setMaxLength':1,
                                'setValidator':QRegExpValidator(punctuationRe, self),
                                'setInputMask':"X"
                         },
                         None,
                        ),
                        ("Decimal places",
                            QSpinBox,
                            {"setRange":(0,6)},
                            None,
                        ),
                        ("Red negative numeros",
                            QCheckBox,
                            None,
                            None,
                        ),
                        ("&Yellow outliers",
                            QCheckBox,
                            None,
                            None,
                        )
                      )
        self.data = [format["thousandsseparator"],
                        format["decimalmarker"],
                        format["decimalplaces"],
                        format["rednegatives"],
                        format["yellowoutliers"],
                    ]
        
        self.format = format
        self.callback = callback

        
        grid = QGridLayout()
        self.sheet = WPropertySheet(self.context,self.data)
        grid.addWidget(self.sheet, 0, 0)
        self.setLayout(grid)
        self.setMinimumSize(QSize(300,220))
        self.sheet.cellChanged.connect(self.valida)
        
        self.setWindowTitle("Set Number Format (`Live')")


    def valida(self,row,col):
        if row > 1:
            self.apply()
        else:
            self.checkAndFix()
            
    def checkAndFix(self):
        thousands = self.sheet.get(0,0)
        decimal = self.sheet.get(1,0)
        if thousands == '':
            self.sheet.setCurrentCell(0,0)
            return
        if decimal == '':
            self.sheet.setCurrentCell(1,0)
            return

        if thousands == decimal:
            self.sheet.getItem(0,0).setText("")
            self.sheet.setCurrentCell(0,0)
        if len(decimal) == 0:
            self.sheet.set(1,0,".")
            self.sheet.getItem(1,0).selectAll()
            self.sheet.setCurrentCell(1,0)
    
        self.apply()


    def apply(self):
        self.format["thousandsseparator"] = (
                #unicode(self.thousandsEdit.text()))
                self.sheet.get(0,0))
        self.format["decimalmarker"] = (
                #unicode(self.decimalMarkerEdit.text()))
                self.sheet.get(1,0))
        self.format["decimalplaces"] = (
                self.sheet.get(2,0))
        self.format["rednegatives"] = (
                self.sheet.get(3,0))
        self.format["yellowoutilers"] = (
                self.sheet.get(3,0))

        self.callback()
  
class WNameValue(QDialog):
    """
    WIP
    Widget para editar libremente pares nombre/valor
    
    """
    def __init__(self,load=None,parent=None):
        super().__init__(parent)
        if load:
            self.sheet = WSheet(len(load) +2,2)
        else:
            self.sheet = WSheet(5,2)

        self.setMinimumSize(QSize(440,220))
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok| QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)        
        self.msgLine = QLabel()
        
        meatlayout = QGridLayout()
        meatlayout.addWidget(self.sheet,0,0)
        meatlayout.addWidget(self.msgLine,1,0)
        meatlayout.addWidget(buttonBox,2,0)
        
        self.setLayout(meatlayout)
        self.prepareData(load)
        
    def prepareData(self,load=None):
        self.sheet.setHorizontalHeaderLabels(('nombre','valor                                                    '))
        if load:
            inicial = load
        else:
            inicial = [[None, None ],]
        self.sheet.loadData(inicial)
        self.sheet.horizontalHeader().setStretchLastSection(True)
        self.sheet.resizeColumnsToContents()
        
    def accept(self):
        from support.util.record_functions import osSplit
        
        def __limpia(texto):
            return texto.replace("'",'')
        
        def __procesaEntrada(texto):
            cabeza = texto[0]
            if cabeza in ( '[','{'):
                if texto.strip()[-1] == cabeza:
                    texto = texto.strip()[1:-1]
                else:
                    texto = texto.strip()[1:]
                lista = osSplit(texto)
                if cabeza == '[':
                    resultado = []
                    for row in lista:
                        resultado.append(__procesaEntrada(row))
                elif cabeza == '{':
                    resultado = {}
                    for row in lista:
                        nombre,valor = row.split(':')
                        resultado[__limpia(nombre)] = __procesaEntrada(valor)
            else:
                resultado = texto
            return resultado

        self.result = {}
        k = 0
        for entrada in self.sheet.values():
            self.msgLine.setText('')
            self.msgLine.setStyleSheet(None)
            if entrada[0].strip() == '':
                continue
            try:
                self.result[entrada[0]] = __procesaEntrada(entrada[1])
            except ValueError as e:
                self.msgLine.setText(str(e))
                self.msgLine.setStyleSheet("background-color:yellow;")
                self.sheet.cellWidget(k,1).setFocus()
                return
            k += 1
        super().accept()


def mainNF():
    app = QApplication(sys.argv)

    format = dict(thousandsseparator=".",
                                    decimalmarker=",",
                                    decimalplaces=2,
                                    rednegatives=False,
                                    yellowoutliers=True)

     
    #title = 'Hoja de seleccion de propiedades'
    ctexts = (u"C's", u'EH Bildu', u'EAJ-PNV', u'PP', u'PSOE', u'PODEMOS', u'GBAI', u'CCa-PNC', u'IU-UPeC', u'M\xc9S', u'DL', u'PODEMOS-COMPROM\xcdS', u'N\xd3S', u'EN COM\xda', u'PODEMOS-En Marea-ANOVA-EU', u'ERC-CATSI')
    context=[[ctexts[k],None] for k in range(len(ctexts))]
    #context[3][1]='oleole'
    #context[4][1]=5
    #form = propertySheetDlg(context)
    
    form = NumberFormatDlg(format,None)
    form.show()
    if form.exec_():
        cdata = [context[k][1] for k in range(len(ctexts))]
        print('a la vuelta de publicidad',cdata)
        sys.exit()

#OJO requiere de una funcion que ya no existe camposDeTipo. Encontrar en backup/datalayer/directory.py
#from base.core import Cubo, Vista
#from support.util.jsonmgr import load_cubo
#from support.datalayer.directory import camposDeTipo

#def dateFilter():
    #from base.core import Cubo
    #from support.util.jsonmgr import load_cubo
    
    #app = QApplication(sys.argv)
    #parametros = [ 1, 0, 2,3, False, False ]
    #mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['film'])
    #vista=Vista(cubo,1,0,'sum','sakila.film.film_id')
    #descriptores = camposDeTipo("fecha",vista.cubo.db,vista.cubo.definition['table'])
    #form = datebase.filterDlg(descriptores)
    ##form.show()
    #if form.exec_():
        ##cdata = [form.context[k][1] for k in range(len(parametros))]
        ##print('a la vuelta de publicidad',cdata)
        #sqlGrp = []
        ##OJO form.result lleva los indices desplazados respecto de form.data
        #for entry in form.result:
            #if entry[1] != 0:
                #intervalo = dateRange(entry[1],entry[2],periodo=entry[3])
                #sqlGrp.append((entry[0],'BETWEEN',intervalo))
        #if len(sqlGrp) > 0:
            #print(searchConstructor('where',{'where':sqlGrp}))
        #sys.exit()


if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #app = QApplication(sys.argv)
    #dateFilter()
    mainNF()

