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

  
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QColor
from  PyQt5.QtWidgets import QApplication, QMainWindow, QWizard,QWizardPage,QLabel,QComboBox,QGridLayout,QGroupBox,QRadioButton,QVBoxLayout,QGridLayout,QPlainTextEdit,QListWidget,QCheckBox
    

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *

from cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from cubemgmt.cubetree import *
from cubemgmt.cubeTypes import *

from wizardmgmt.guihelper import *

from widgets import *    
from util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

from wizardmgmt.pages.wzcategory import WzCategory
from wizardmgmt.pages.wzconnect  import WzConnect
from wizardmgmt.pages.wzdatefilter import WzDateFilter
from wizardmgmt.pages.wzdomain import WzDomain
from wizardmgmt.pages.wzlink import WzLink
from wizardmgmt.pages.wzother import WzFieldList,WzGuideList
from wizardmgmt.pages.wzperiod import WzTime
from wizardmgmt.pages.wzrowedit import WzRowEditor
from wizardmgmt.pages.wzprodbase import WzProdBase

class CubeWizard(QWizard):
    def __init__(self,obj,cubeMgr,action,cube_root,cube_ref,cache_data):
        super(CubeWizard,self).__init__()
        """
           convierto los parametros en atributos para poder usarlos en las paginas 
        """
        self.obj = obj
        self.cubeMgr = cubeMgr
        self.action = action
        self.cube_root = cube_root
        self.cache_data = cache_data

        tipo = obj.type()
        if action == 'add date filter':
            self.diccionario = {'date filter':[]}
        else:
            self.diccionario = tree2dict(obj,isDictionaryEntry)
            
        if not tipo or tipo == 'connect':
            self.setPage(ixWzConnect, WzConnect(cube=cubeMgr,cache=cache_data))
        # TODO no son estrictamente complejos pero la interfaz es mejor como complejos
        #if not tipo:
            #self.setPage(ixWzFieldList, WzFieldList(cache=cache_data))
            #self.setPage(ixWzBaseFilter, WzBaseFilter(cache=cache_data))
        if not tipo or tipo == 'date filter' or action == 'add date filter':
            self.setPage(ixWzDateFilter, WzDateFilter(cube=cubeMgr,cache=cache_data))
        
        if tipo in ('categories'):
            self.setPage(ixWzCategory, WzCategory(cache=cache_data))
        elif tipo in ('domain'):
            self.setPage(ixWzDomain, WzDomain(cube=cubeMgr,cache=cache_data))
        elif tipo in ('case_sql'):
            self.setPage(ixWzRowEditor, WzRowEditor(cache=cache_data))
        elif tipo in ('link via'):
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            
        elif tipo in ('prod','guides'): #== 'prod':
            self.prodIters = 1
            if obj.text() != 'prod':  # entrada individual
                if action in ('add','insert after','insert before'):
                    self.diccionario = {}
                elif action == 'edit':
                    pass
            else:  # la entrada de produccion
                if action in ('add','insert first'):
                    self.diccionario = {}
                elif action == 'edit':
                    self.prodIters = len(self.diccionario)
                    pass
            
            self.setPage(ixWzProdBase, WzProdBase(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            
        texto_pantalla = obj.text() if obj.text() != tipo else obj.parent().text()
        self.setWindowTitle('Mantenimiento de ' + tipo + ' ' + texto_pantalla.split('.')[-1])
        self.show()
