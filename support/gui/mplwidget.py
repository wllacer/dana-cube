"""
Qt 5 sample of matplotlib use.
    Taken from https://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html
    
TODO
   get an option to show it as an independent matplotlib window
   
"""
import sys
import random
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtCore import Qt,QModelIndex
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget,QGridLayout,QTabWidget

import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker  as ticker

class MultiChart(FigureCanvas):
    def __init__(self,*args,**kwargs):
        self.fig,self.ax = plt.subplots()
        self.color_list=('r','g','b','k')
        super(MultiChart,self).__init__(self.fig)

    def loadData(self,*args,**kwargs):
        self.ax.cla()
        tipo = args[0]
        self.x=args[1]
        self.y=args[2]
        self.ax.set_title(args[3])
        self.ax.set_xlabel(args[4])
        self.ax.set_ylabel(args[5])
        
        pos_list = np.arange(len(self.x))
        numBars = len(y)
        if numBars > 1:
            width   = 1/(numBars +1)
        else:
            width = 1
        rects = list()
        for k in range(numBars):
            ely = self.y[k]
            elco = self.color_list[k % len(self.color_list)]
            #rects.append(self.ax.bar(pos_list +width*k, self.y[k], width, color=self.color_list[k]))
            rects.append(self.ax.bar(pos_list +width*k, ely, width, color=elco))
        if numBars > 1:
            self.ax.set_xticks(pos_list + width)
        else:
            self.ax.set_xticks(pos_list)
        self.ax.set_xticklabels(self.x)
        self.ax.legend([item[0] for item in rects], args[6])

class SimpleChart(FigureCanvas):
    """Class to represent the FigureCanvas widget"""
    def __init__(self,*args,**kwargs):
        # Standard Matplotlib code to generate the plot
        #self.fig = Figure()
        #self.axes = self.fig.add_subplot(111)
        self.color_list=('r','g','b','k')
        self.fig,self.axes = plt.subplots()
        super(SimpleChart,self).__init__(self.fig)
        self.setMinimumHeight(200)
        
    def loadData(self,*args,**kwargs):
        """
        args:
            0 tipo de grafico
            1 datos x
            2 datos y
            3 titulo
        """
        self.axes.cla()
        tipo = args[0]
        self.x=args[1]
        self.y=args[2]
        self.axes.set_title(args[3])
        self.axes.set_xlabel(args[4])
        self.axes.set_ylabel(args[5])
        
        pos_list = np.arange(len(self.x))
        if tipo not in ('barh',):
            self.axes.xaxis.set_major_locator(ticker.FixedLocator((pos_list)))
            self.axes.xaxis.set_major_formatter(ticker.FixedFormatter((self.x)))            
        else:
            self.axes.yaxis.set_major_locator(ticker.FixedLocator((pos_list)))
            self.axes.yaxis.set_major_formatter(ticker.FixedFormatter((self.x)))            
        
        labels = self.axes.get_xticklabels()
        plt.setp(labels, rotation = 270.)
        #TODO un poquito de magia por favor
        if tipo == 'multibar' and  not isinstance(self.y[0],(list,tuple)):
            tipo = 'bar'            
        if tipo == 'bar':
            self.axes.bar(pos_list,self.y)
        elif tipo == 'multibar':
            numBars = len(self.y)
            rects = list()
            if numBars > 1:
                width   = 1/(numBars +1)
                for k in range(numBars):
                    rects.append(self.axes.bar(pos_list +width*k, self.y[k], width, color=self.color_list[k]))
                self.axes.set_xticks(pos_list + width)
            else:
                rects.append(self.axes.bar(pos_list, self.y[0],1, color=self.color_list[0]))
                self.axes.set_xticks(pos_list)
            self.axes.set_xticklabels(self.x)
            if len(args) >= 6:
                if len(args[6]) < numBars:
                    labels = ['Total',]+['' for k in range(len(args[6]) - numBars -1) ] + args[6]
                else:
                    labels = args[6]
                #self.axes.legend([item[0] for item in rects], labels)
        elif tipo == 'boxplot':
            b = self.axes.boxplot(self.y)
            for name, line_list in b.items():
                for line in line_list:
                    line.set_color('k')
        elif tipo == 'barh':
            self.axes.barh(pos_list,self.y)
        elif tipo in ('tarta','pie'):
            self.axes.pie(self.y,labels=self.x,autopct='%1.1f%%')
        else:
            ktipo = 'o'  #scatter es el defecto
            self.axes.plot(pos_list, self.y,ktipo)
        self.draw()

    def close(self):
        plt.close(self.fig)
        super().close()
#def isVisible(item,treeView,direccion):
    #if direccion == 'col':
        #pos = treeView.vista.col_hdr_idx.item2pos(item)
        #if treeView.isColumnHidden(pos +1):
            #return False
        #else:
            #return True
    #elif direccion == 'row':
        #entry = item
        #hidden = False
        #while entry:
            #row = entry.row()
            #pai = entry.parent().index() if entry.parent() else QModelIndex()
            #if treeView.isRowHidden(row,pai):
                #hidden = True
                #break
            #entry = entry.parent()
        #if hidden:
            #return False
        #else:
            #return True
    #return True
        
def getGraphTexts(vista,head,xlevel,dir='row'):
    
    if dir == 'row':
        fmodel = vista.row_hdr_idx
        xmodel = vista.col_hdr_idx
        fidx = vista.row_id
        xidx = vista.col_id
        fdim = vista.dim_row
        xdim  = vista.dim_col
    else:
        fmodel = vista.col_hdr_idx
        xmodel = vista.row_hdr_idx
        fidx = vista.col_id
        xidx = vista.row_id
        fdim = vista.dim_col
        xdim  = vista.dim_row
        
    fixedParm = fmodel.name
    if fdim > 1:
        j = head.depth() -1 if (dir == 'row' and vista.totalizado) else head.depth()
        if j == -1:
            pass
        else:
            fixedParm = vista.cubo.lista_guias[fidx]['contexto'][j]['name']
            
    ejeX  = xmodel.name
    if xdim > 1:
        if dir == 'col' and vista.totalizado:
            ejeX = vista.cubo.lista_guias[xidx]['contexto'][xlevel -1]['name']
        else:
            ejeX = vista.cubo.lista_guias[xidx]['contexto'][xlevel]['name']
        
    titulo = '{}:  {} \n por {} '.format(fixedParm,head.getFullHeadInfo(),ejeX)
    
    ejeY = '{}({})'.format(vista.agregado,vista.campo)  #TODO depende de las funciones ejecutadas
    
    return titulo,ejeX,ejeY

class ChartTab(QTabWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.datos = []
        self.item =None
        self.vista=None
        self.graph=None
        self.dir=None
        self.filter=None

    def forSimple(self,vista):
        resultado = vista.getVector(self.item,dir=self.dir,filter=self.filter)
        for k in range(len(resultado)):
            if len(resultado[k]['text']) == 0:
                continue
            if k == 0 and self.dir=='col' and vista.totalizado:
                continue
            texto = resultado[k]['text'] 
            valores = [ elem.data(Qt.UserRole +1) for elem in resultado[k]['elems'] ]
            titulo,ejeX,ejeY = getGraphTexts(vista,self.item,k,dir=self.dir)
            self.datos.append({'texto':texto,'valores':valores,'titulo':titulo,'ejeX':ejeX,'ejeY':ejeY })
            
            self.addTab(SimpleChart(),ejeX)
            self.setCurrentIndex(self.count() -1)
            self.currentWidget().loadData(self.graph,texto,valores,titulo,ejeX,ejeY)
            self.currentWidget().draw()   
        else:
            self.setCurrentIndex(0)
            self.currentWidget().setFocus()  #FIXME
        
    def loadData(self,vista,head,graphType='bar',dir='row',filter=None):
        #borro los tabs
        self.limpia()
        self.item = head
        self.vista=vista
        self.graph=graphType
        self.dir=dir
        self.filter=filter
        for k in range(self.count()-1,-1,-1):
            self.removeTab(k)
        if graphType is None:
            self.hide()
        
        if self.graph.startswith('multi') and  self.item.depth() > 0:
            pos = self.item
            while pos:
                print(pos)
                pos = pos.parent()
            
        self.forSimple(vista)
    
    def reLoad(self,item=None):
        if not item:
            self.loadData(self.vista,self.item,self.graph,self.dir,self.filter)
        else:
            self.loadData(self.vista,item,self.graph,self.dir,self.filter)
        
    def draw(self):
        for k in range(self.count()):
            self.setCurrentIndex(k)
            self.currentWidget().draw()
            
    def limpia(self):
        for k in range(self.count()):
            self.setCurrentIndex(k)
            #plt.close(self.currentWidget().fig)
            self.currentWidget().close()
        self.datos.clear()    
        
    def hide(self):
        self.limpia()
        self.vista=None
        self.graph=None
        self.dir=None
        self.filter=None
        super().hide()

"""
    Prueba
"""
class ApplicationWindow(QMainWindow):
    def __init__(self,*args,**kwargs):
        QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        #self.main_widget = QWidget(self)

        #self.main_widget = SimpleChart(*args,**kwargs) #self.main_widget, width=5, height=4, dpi=200)
        self.main_widget = SimpleChart(*args,**kwargs)
        #self.main_widget = MultiChart(*args,**kwargs)
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        #self.statusBar().showMessage("All hail matplotlib!", 2000)

if __name__ == '__main__':
    
    #y=[1038, 172, 16, 11, 15, 18, 15, 12, 10, 16, 17, 10, 17, 15, 171, 14, 18, 20, 8, 17, 14, 10, 10, 13, 14, 15, 18, 178, 12, 23, 17, 10, 18, 18, 6, 23, 9, 10, 15, 17, 164, 23, 18, 7, 16, 9, 13, 14, 6, 16, 12, 14, 16, 176, 13, 12, 19, 7, 15, 12, 16, 19, 15, 17, 18, 13, 177, 16, 13, 12, 14, 12, 13, 14, 16, 16, 13, 20, 18]
    #x=['2010', '2010:01', '2010:02', '2010:03', '2010:04', '2010:05', '2010:06', '2010:07', '2010:08', '2010:09', '2010:10', '2010:11', '2010:12', '2011', '2011:01', '2011:02', '2011:03', '2011:04', '2011:05', '2011:06', '2011:07', '2011:08', '2011:09', '2011:10', '2011:11', '2011:12', '2012', '2012:01', '2012:02', '2012:03', '2012:04', '2012:05', '2012:06', '2012:07', '2012:08', '2012:09', '2012:10', '2012:11', '2012:12', '2013', '2013:01', '2013:02', '2013:03', '2013:04', '2013:05', '2013:06', '2013:07', '2013:08', '2013:09', '2013:10', '2013:11', '2013:12', '2014', '2014:01', '2014:02', '2014:03', '2014:04', '2014:05', '2014:06', '2014:07', '2014:08', '2014:09', '2014:10', '2014:11', '2014:12', '2015', '2015:01', '2015:02', '2015:03', '2015:04', '2015:05', '2015:06', '2015:07', '2015:08', '2015:09', '2015:10', '2015:11', '2015:12', None]
    y = [3500541, 7215752, 5530779, 3182082, 923133]
        #[611772, 1292652, 1400399, 749081, 256080],
        #[142301, 275335, 371103, 207826, 62152]]
    x = ["C's", 'PP', 'PSOE', 'PODEMOS', 'IU-UPeC']
    titulo = 'geo> Cordoba'
    x_text = 'sum(votes_presential)' 
    y_text = 'partidos importantes '

    app = QApplication(sys.argv)
    tipo = 'bar' #'bar' #'scatter'
    aw = ApplicationWindow()#tipo,x,y,'Fresquito de la Base de Datos','Una dimension','La otra')
    aw.setWindowTitle("PyQt5 Matplot Example")
    aw.main_widget.loadData(tipo,x,y,titulo,x_text,y_text,('Ejemplo',))
    aw.show()
    #sys.exit(qApp.exec_())
    app.exec_()
