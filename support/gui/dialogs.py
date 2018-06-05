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
 
"""
  config.DEBUG DATA start
"""
cubo = None



class propertySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de propiedades
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
    """
    def __init__(self,title,context,data,parent=None):   
        super(propertySheetDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = context
        self.data = data
        #
        InicioLabel = QLabel(title)
        #
        self.sheet=WPropertySheet2(context,data)
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
    def __init__(self,descriptores=None,datos=None,parent=None):   
        """
        """
        if descriptores is None:
            return 
        else:
            self.descriptores = descriptores

        if datos is None:
            self.data = []
        else:
            self.data = datos
            
        super(dateFilterDlg, self).__init__(parent)
        # cargando parametros de defecto
        self.context = []

        for k in self.descriptores:
            self.context.append(('\t {}'.format(k),
                                  (QComboBox,None,CLASES_INTERVALO),
                                  (QComboBox,None,TIPOS_INTERVALO),
                                  (QSpinBox,{"setRange":(1,366)},None,1),
                                  (QLineEdit,{"setEnabled":False},None),
                                  (QLineEdit,{"setEnabled":False},None),
                                  )
                        )
        rows = len(self.context)
        cols = max( [len(item) -1 for item in self.context ])  #FIXME
        self.sheet1=WPowerTable(rows,cols)

        for i,linea in enumerate(self.context):
            for j in range(1,len(linea)):
                self.sheet1.addCell(i,j -1,linea[j])
                self.sheet1.set(i,j -1,self.data[i][j-1])
            self.sheet1.cellWidget(i,0).currentIndexChanged[int].connect(lambda j,idx=i:self.seleccionCriterio(j,idx))
            self.sheet1.cellWidget(i,1).currentIndexChanged[int].connect(lambda j,idx=i:self.seleccionIntervalo(j,idx))
            self.sheet1.cellWidget(i,2).valueChanged[int].connect(lambda j,idx=i:self.seleccionIntervalo(j,idx))
            self.flipFlop(i,self.sheet1.get(i,0))

       #FIXME valor inicial        
        campos = [ k[0] for k in self.context ]
        self.sheet1.setVerticalHeaderLabels(campos)
        self.sheet1.resizeColumnsToContents()
        cabeceras = ('Tipo','Periodo','Rango','desde','hasta')
        self.sheet1.setHorizontalHeaderLabels(cabeceras)
        #
        InicioLabel1 = QLabel('Filtre el rango temporal que desea')

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel,
                                     Qt.Horizontal)



        meatLayout = QVBoxLayout()
        buttonLayout = QHBoxLayout()
        

        meatLayout.addWidget(InicioLabel1)
        meatLayout.addWidget(self.sheet1)
       
        buttonLayout.addWidget(buttonBox)
        meatLayout.addLayout(buttonLayout)
        
        self.setLayout(meatLayout)
        self.setMinimumSize(QSize(800,200))
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.setWindowTitle("Item editor")
        
    def flipFlop(self,line,value):
        # puede ser un poco repetitivo, pero no se si es mas costoso el enable/disable que comprobar cada
        # vez si lo esta. Por lo menos el codigo es menos complejo y todavia no veo una razon para modificarlo
        if value == 0:
            self.sheet1.cellWidget(line,1).setEnabled(False)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        elif value == 1: 
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(False)
        else:
            self.sheet1.cellWidget(line,1).setEnabled(True)
            self.sheet1.cellWidget(line,2).setEnabled(True)
        # ponemos los valores ejemplo

    def seleccionCriterio(self,value,idx):
        self.flipFlop(idx,value)
        self.seleccionIntervalo(value,idx)
            
    def seleccionIntervalo(self,value,idx):
        if self.sheet1.get(idx,0)  == 0:
            self.sheet1.set(idx,3,None)
            self.sheet1.set(idx,4,None)
        else:
            desde,hasta = dateRange(self.sheet1.get(idx,0),self.sheet1.get(idx,1),periodo=self.sheet1.get(idx,2))
            self.sheet1.set(idx,3,str(desde))
            self.sheet1.set(idx,4,str(hasta))

   
    def accept(self):
        self.data = self.sheet1.values()
        self.result = []
        self.result = []
        for k,valor in enumerate(self.data):
            if valor[0] == 0:
                continue
            else:
                self.result.append((self.descriptores[k],valor[0],valor[1],valor[2]))
        QDialog.accept(self)
    
class dataEntrySheetDlg(QDialog):
    """
       Genera (mas o menos) una hoja de entrada de datos
       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
       FIXME los botones estan fatal colocados
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
        self.context = []
        self.context.append(('Guia filas',QComboBox,None,cubo.getGuideNames()),)
        self.context.append(('Guia columnas',QComboBox,None,cubo.getGuideNames()),)
        self.context.append(('Función agregacion',QComboBox,None,cubo.getFunctions()),)
        self.context.append(('Campo de datos',QComboBox,None,cubo.getFields()),)
        self.context.append(('Con totales',QCheckBox,None),)
        self.context.append(('Con estadisticas',QCheckBox,None),)
        
        super(VistaDlg, self).__init__(title,self.context,parametros,parent)
        
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
        self.sheet = WPropertySheet2(self.context,self.data)
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
            self.sheet = WPowerTable(len(load) +2,2)
        else:
            self.sheet = WPowerTable(5,2)

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
        context = []
        context.append((QLineEdit,{'setEnabled':True},None))
        context.append((QLineEdit,{'setEnabled':True},None))
        self.sheet.setRowModelDef(context)
        if load:
            inicial = load
        else:
            inicial = [[None, None ],]
        for x in range(self.sheet.rowCount()):
            for y,colDef in enumerate(context):
                if x < len(inicial):
                    self.sheet.addCell(x,y,colDef,defVal=inicial[x][y])
                else:
                    self.sheet.addCell(x,y,colDef,defVal=None)
            self.sheet.resizeRowsToContents()
        self.sheet.resizeColumnsToContents()
        
    def accept(self):
        from support.util.record_functions import osSplit
        
        def __limpia(texto):
            return texto.replace("'",'')
        
        def __procesaEntrada(texto):
            cabeza = texto[0]
            if cabeza in ( '[','{'):
                texto = texto.strip()[1:-1]
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
                resultado = texto[0]
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

