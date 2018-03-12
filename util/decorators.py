#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
EXPERIMENTAL

Plans are to lift some of them from https://wiki.python.org/moin/PythonDecoratorLibrary
Now only those used in danacube are in the library
Documentation, License etc.

@package estimaciones
'''
import sys
from PyQt5.QtCore import Qt, QSortFilterProxyModel
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QMessageBox

from pprint import *
from functools import wraps

import config

def stopwatch(function):
    """
        decorator que devuelve el elapsed time por una operacion en 10-6 segs (la precison real no puede ser tanta)
    """
    from datetime import datetime
    @wraps(function)
    def timed_func(*args,**kwargs):
        ahora = datetime.now()
        results = function(*args,**kwargs)
        print(function.__name__,'lapsed',datetime.now() - ahora)
        return results
    return timed_func

def waiting_effects(function):
    """
      decorator from http://stackoverflow.com/questions/8218900/how-can-i-change-the-cursor-shape-with-pyqt
      para poner el cursor en busy/libre al ejectuar una funcion que va a tardar
            
    """
    @wraps(function)
    def cursor_busy(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        try:
            return function(*args, **kwargs)
        except Exception as e:
            QMessageBox.warning(QApplication.activeWindow(),
                            "Warning",
                            "Error {}".format(e.args[0]))
            if config.DEBUG:
                print("Error {}".format(e.args[0]))
            raise e
        finally:
            QApplication.restoreOverrideCursor()
    return cursor_busy

def model_change_control(clas_pos=0):
    """ 
    FIXME . si hay una interaccion por pantalla por medio (un dialogo) la vista va a blanco. Es un error detectado varias veces.
        decorator para incluir el par beginResetModel/endResetModel para todos los derivados de QAbstractItemModel
        Espera que el primer argumento tenga una funcion model() para acceder a el (normalmente una instasncia de QAbstractViewModel o incluso un elemento de modelo)
        La posición del argumento que contiene referencias al modelo es nuestra variable
    """
    def reset_model_dec(function):
        @wraps(function)
        def reset_model(*args, **kwargs):
            cls = args[clas_pos]
            model = cls.model()
            if isinstance(model,QSortFilterProxyModel):
                model = model.sourceModel()
            try:
                model.beginResetModel()
                return function(*args, **kwargs)
            except Exception as e:
                QMessageBox.warning(QApplication.activeWindow(),
                                "Warning",
                                "Error {}".format(e.args[0]))
                if config.DEBUG:
                    print("Error {}".format(e.args[0]))
                raise e
            finally:
                model.endResetModel()
        return reset_model
    return reset_model_dec

def keep_tree_layout(clas_pos=0):
    """
        Para vistas en arbol derivadas de QAbstractViewModel para mantener el estado en pantalla tras actualizaciones del modelo.
        Espera que el argumento 0 incluya la referencia a la vista. El parametro sriver para enviarlo a otra direccion
    """
    from util.treestate import saveExpandedState,restoreExpandedState
    def keep_position_dec(function):
        @wraps(function)
        def keep_position(*args, **kwargs):
            cls = args[clas_pos]
            try:
                expList = saveExpandedState(cls)
                return function(*args, **kwargs)
            except Exception as e:
                QMessageBox.warning(QApplication.activeWindow(),
                                "Warning",
                                "Error {}".format(e.args[0]))
                if config.DEBUG:
                    print("Error {}".format(e.args[0]))
                raise e
            finally:
                restoreExpandedState(expList,cls)
        return keep_position
    return keep_position_dec
    
def model_update_dec(function):
    """
        DEPRECADO
        Decorator que realiza las funciones de waiting_effects, keep_tree_layout y model_change_control en uno solo
        Prefiero usar los otros uno a uno
    """
    from util.treestate import saveExpandedState,restoreExpandedState
    @wraps(function)
    def model_update_keep_position(*args, **kwargs):
        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        cls = args[0]
        model = cls.model()
        if isinstance(model,QSortFilterProxyModel):
            model = model.sourceModel()
        try:
            expList = saveExpandedState(cls)
            cls.model.beginResetModel()
            return function(*args, **kwargs)
        except Exception as e:
            QMessageBox.warning(QApplication.activeWindow(),
                            "Warning",
                            "Error {}".format(e.args[0]))
            if config.DEBUG:
                print("Error {}".format(e.args[0]))
            raise e
        finally:
            cls.model.endResetModel()
            restoreExpandedState(expList,cls)
            QApplication.restoreOverrideCursor()
    return model_update_keep_position

@stopwatch
def carrera():
    m = list()
    for k in range(1000):
        m.append(k)
    return m
        
if __name__ == '__main__':
    
    print(carrera())
    #app = QApplication(sys.argv)
    #window = QMainWindow()
    #window.show()
    #tarugo()
    #sys.exit(app.exec_())
    
    
