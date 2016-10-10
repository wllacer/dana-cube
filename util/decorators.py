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

from pprint import *

def cursor_busy(f):
    app.setOverrideCursor(QCursor(Qt.WaitCursor))
    salida = f(*args,**kwargs)
    app.restoreOverrideCursor()
    return salida

@cursor_busy
def tarugo():
    for k in range(1000):
        paco = sum([m for m in range(k-1)])

if __name__ == '__main__':
    import sys
    from PyQt5.QtGui import QCursor
    from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView

    app = QApplication(sys.argv)
    window = QMainWindow()
    window.show()
    tarugo()
    sys.exit(app.exec_())
    
    
