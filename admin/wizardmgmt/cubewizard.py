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
    

import base.config as config

from support.util.record_functions import *

from admin.cubemgmt.cubeutil import info2cube,isDictionaryEntry,action_class,getCubeList,getCubeItemList
from base.cubetree import *
from admin.cubemgmt.cubeTypes import *

from admin.wizardmgmt.guihelper import *

import support.gui.widgets import *    
from support.util.fechas import dateRange


(ixWzConnect,ixWzDateFilter,ixWzFieldList,ixWzBaseFilter,ixWzGuideList,ixWzProdBase,ixWzCategory,ixWzRowEditor,ixWzTime,ixWzDomain, ixWzLink) = range(11) 
ixWzGuideBase = ixWzProdBase

from admin.wizardmgmt.pages.wzcategory import WzCategory
from admin.wizardmgmt.pages.wzconnect  import WzConnect
from admin.wizardmgmt.pages.wzdatefilter import WzDateFilter
from admin.wizardmgmt.pages.wzdomain import WzDomain
from admin.wizardmgmt.pages.wzlink import WzLink
from admin.wizardmgmt.pages.wzother import WzFieldList,WzGuideList,uno,dos
from admin.wizardmgmt.pages.wzperiod import WzTime
from admin.wizardmgmt.pages.wzrowedit import WzRowEditor
from admin.wizardmgmt.pages.wzprodbase import WzProdBase



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
            
            #self.setPage(ixWzProdBase, uno(cube=cubeMgr,cache=cache_data))
            #self.setPage(ixWzLink, dos(cube=cubeMgr,cache=cache_data))

            self.setPage(ixWzLink, WzLink(cube=cubeMgr,cache=cache_data))
            self.setPage(ixWzProdBase, WzProdBase(cube=cubeMgr,cache=cache_data))
        texto_pantalla = obj.text() if obj.text() != tipo else obj.parent().text()
        self.setWindowTitle('Mantenimiento de ' + tipo + ' ' + texto_pantalla.split('.')[-1])
        self.show()
