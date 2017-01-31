"""
Qt 5 sample of matplotlib use.
    Taken from https://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html
"""
import sys
import random
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget,QGridLayout

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
            rects.append(self.ax.bar(pos_list +width*k, self.y[k], width, color=self.color_list[k]))
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
        plt.setp(labels, rotation = 60.)
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
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

#        self.statusBar().showMessage("All hail matplotlib!", 2000)

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
