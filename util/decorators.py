#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
EXPERIMENTAL

Documentation, License etc.

@package estimaciones
'''
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView



from pprint import *

def waiting_effects(function):
    """
      decorator from http://stackoverflow.com/questions/8218900/how-can-i-change-the-cursor-shape-with-pyqt
      para poner el cursor en busy/libre al ejectuar una funcion que va a tardar
      
      TODO unificar en un solo sitio
      
    """
    def new_function(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            raise e
            QMessageBox.warning(self,
                            "Warning",
                            "Error {}".format(e.args[0]))
            if DEBUG:
                print("Error {}".format(e.args[0]))
        finally:
            QApplication.restoreOverrideCursor()
    return new_function

#def cursor_busy(f):
    #QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    #salida = f(*args,**kwargs)
    #QApplication.restoreOverrideCursor()
    #return salida

#@cursor_busy
#def tarugo():
    #for k in range(1000):
        #paco = sum([m for m in range(k-1)])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()
    tarugo()
    sys.exit(app.exec_())
    
    
