#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

import user as uf
from support.util.uf_manager import *
from support.util.decorators import keep_tree_layout,model_change_control,waiting_effects

class Uf_handler():
    
    def __init__(self,menu=None,cubo=None,slot=None):
        self.plugins = dict()
        self.ufMenu = menu      #menu principal
        self.specUfMenu = None  #menu para subsistema particular
        self.baseSlot = slot
        
        #uf_discover(uf,self.plugins)
        uf_discover_file(uf,self.plugins)
        
        if menu and slot:
            self.setupPluginMenu(self.ufMenu,cubo,self.baseSlot)
    
    """
    Funciones para rellenar el menu
    """
    def setupPluginMenu(self,pmenu=None,cubo=None,pslot=None):
        """
        funcion para (re)inicializar el menu.
        Se incluyen las funciones comunes y si se especifica cubo las del menu especial
        si se cambia el slot se cambia el defecto a partir de ese momento
        """
        if not pmenu:
            menu = self.ufMenu
        else:
            menu = pmenu
        
        slot = self.baseSlot
        if pslot:
            slot = self.baseSlot = pslot 
            

        if cubo:
            self.fillUserFunctionMenu('',slot,menu) #las comunes
            menu.addSeparator()
            self.specUfMenu = menu.addMenu("Especificas")
            self.fillUserFunctionMenu(cubo.nombre,slot,self.specUfMenu) #las especificas del cubo
        else:
            self.fillUserFunctionMenu('',menu) #las comunes
            
        return self.specUfMenu

    def fillUserFunctionMenu(self,db='',pslot=None,pmenu=None,):
        if not pmenu:
            if self.specUfMenu:
                menu = self.specUfMenu
            else:
                menu = self.specUfMenu = self.ufMenu.addMenu('Especificas')
        else:
            menu = pmenu
            
        if db != '':
            menu.clear()
            menu.setTitle('Funciones especificas para '+ db)
            subset = { k:self.plugins[k] for k in self.plugins if db in self.plugins[k].get('db','') }
        else:
            subset = { k:self.plugins[k] for k in self.plugins if self.plugins[k].get('db','') == '' }
        if len(subset) == 0:
            return
        
        if not pslot:
            slot = self.baseSlot
        else:
            slot = pslot
            
        for k in sorted(subset,
                    key=lambda x:self.plugins[x].get('seqnr', float('inf'))):
            entry = self.plugins[k]
            if entry.get('hidden',False):
                continue
            menu.addAction(entry['text'],lambda  idx=k: slot(idx))
            if entry.get('sep',False):
                menu.addSeparator()
            
    """
    funciones para ejecutar las acciones
    necesito de arriba
        pre_function
        filter_item
        pre_item
        pos_item
        post_function
    """
    @waiting_effects    
    def dispatch(self,target,fcnName,**callbacks):
        pre = callbacks.get('pre',None)
        pre_exec = callbacks.get('pre exec',preExec)
        pos = callbacks.get('pos',basePos)
        pos_exec = callbacks.get('pos exec',posExec)
        if pre:
            pre(target,fcnName)
        for elem in self.plugins[fcnName]['exec']:
            if pre_exec:
                pre_exec(target,fcnName,elem)
                
            plugin = elem[0]
            tipo_plugin = elem[1]
            lparm,kparm = self.getExecParms(target,plugin,tipo_plugin,elem,**callbacks)
            self.efectiveDispatch(target,plugin,tipo_plugin,lparm,kparm,**callbacks)

            if pos_exec:
                pos_exec(target,fcnName,elem)

        if pos:
            pos(target,fcnName)

    #@keep_tree_layout(1) 
    #@model_change_control(1)    
    def efectiveDispatch(self,model,plugin,tipo_plugin,lparm,kparm,**callbacks):
        """
        separado para evitar efectos secundarios de model_change_control
        """
        #pre = callbacks.get('pre',None)
        #pre_exec = callbacks.get('pre exec',preExec)
        filter_item = callbacks.get('filter item',filterItem)
        pre_item = callbacks.get('pre item',preItem)
        pos_item = callbacks.get('pos item',posItem)
        #pos_exec = callbacks.get('pos exec',posExec)
        #pos = callbacks.get('pos',basePos)

        for item in model.traverse():
            if filter_item and filter_item(item,tipo_plugin,lparm,kparm):
                    continue
            if pre_item:
                pre_item(item,tipo_plugin,lparm,kparm)

            lparm[0] = item 
            plugin(*lparm,**kparm)
            if pos_item:
                pos_item(item,tipo_plugin,lparm,kparm)
 
 
    def getExecParms(self,model,plugin,tipo_plugin,entry,**callbacks):
        from support.util.record_functions import norm2String
        
        index = callbacks.get('index',model2index)
        initial_Data = callbacks.get('index',initialDataVoid)
        data_capture = callbacks.get('data capture',presenta)

        lparm = [None for k in range(4)]
        kparm = dict()

        if entry[2]:
            for key in entry[2]:
                kparm[key] = entry[2][key]

        if 'colparm' in tipo_plugin:
            datosBase = initial_Data(model,'col')
            lparm[1] = [ (dato[0],dato[1]) for dato in datosBase ]
        if 'rowparm' in tipo_plugin:
            datosBase = initial_Data(model,'row')
            lparm[1] = [ (dato[0],dato[1]) for dato in datosBase ]
            
        if 'colkey' in tipo_plugin and not lparm[1]:
            lparm[1] = index(model,'col')
        if 'rowkey' in tipo_plugin and not lparm[1]:
            lparm[1] = index(model,'row')
            
        if 'colparm' in tipo_plugin:  # or 'rowparm' in tipo_plugin:
            # presenta parametros
            a_table = data_capture(datosBase)
            # convierte en parms
            lparm[3] = a_table
        if 'rowparm' in tipo_plugin:
            # presenta parametros
            a_table = data_capture(datosBase)
            # convierte en parms
            lparm[2] = a_table
            
        
        if 'kwparm' in tipo_plugin:
            a_table = [ [key,key,norm2String(kparm[key])] for key in kparm]
            m_datos = data_capture(a_table) #,[norm2String(kparm[key[0]]) for key in a_table])
            for i,key in enumerate(a_table):
                kparm[key[0]] = m_datos[i][2]
        
        return lparm,kparm


def requestFunctionParms(spec,values):
    from PyQt5.QtCore import Qt #,QSortFilterProxyModel
    from PyQt5.QtGui import QCursor
    from PyQt5.QtWidgets import QApplication
    from support.gui.dialogs import propertySheetDlg
    
    QApplication.restoreOverrideCursor()
    parmDialog = propertySheetDlg('Introduzca los valores a simular',spec,values)
    if parmDialog.exec_():
        retorno = parmDialog.data
    else:
        retorno = values
        #print([a_spec[k][1] for k in range(len(a_spec))])
    QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
    return retorno
#    return parmDialog.data

def basePos(model,fcnName):
    vista = model.vista
    vista.isModified = True
    #vista.parent.restorator.setEnabled(True)
            
def preExec(model,fcnName,elem):
    if elem[1] is None: #defino un defecto para esta aplicacion
        elem[1] = 'item'
        
def posExec(model,fcnName,elem):
    if 'leaf' in elem[1]:                
        model.vista.recalcGrandTotal()
            
def filterItem(item,tipo_plugin,lparm,kparm):
    if 'leaf' in tipo_plugin and not item.isLeaf():
        return True
    else:
        return False
    
def preItem(item,tipo_plugin,lparm,kparm):
    item.setBackup()
    
def posItem(item,tipo_plugin,lparm,kparm):
    if  item.model().vista.stats :
        item.setStatistics()

def model2index(model,direction):
    """
    funcioncilla para obtener las tablas para parmetrizar y presentar de las cabeceras de fila o columna
    """
    if direction == 'row':
        guia = model.vista.row_hdr_idx
    elif direction == 'col':
        guia = model.vista.col_hdr_idx
        
    m_tabla = []
    for item in guia.traverse():
        m_tabla.append((item.getKey(),item.getLabel()))
    return m_tabla

def initialDataVoid(model,direction):
    operador = model.vista.agregado
    if operador == 'count':
        operador = 'sum'
    funcion = functionFromName(operador)
    if not funcion:
        return None
    return model.vista.sinAgregado(direction)

def initialData(model,direction):
    operador = model.vista.agregado
    if operador == 'count':
        operador = 'sum'
    funcion = functionFromName(operador)
    if not funcion:
        return None
    return model.vista.agrega(direction,funcion)

def initialDataPct(model,direction):
    operador = model.vista.agregado
    if operador == 'count':
        operador = 'sum'
    funcion = functionFromName(operador)
    if not funcion:
        return None
    return model.vista.agregaPct(direction)

def presenta(baseData):
    """
    funcioncilla para presentar los datos
    """
    a_data = [ dato[2] for dato in baseData]
    a_gui_def = [ [dato[0],None,None] for dato in baseData]
    b_data = requestFunctionParms(a_gui_def,a_data)
    return [ [baseData[k][1],baseData[k][0],b_data[k]] for k in range(len(baseData))]

def functionFromName(operador,context=None):
    import builtins
    
    if context:
        try:
            return getattr(context,operador)
        except AttributeError :
            pass
    
    try:
        return locals()[operador]
    except KeyError  :
        pass
    try:
        return getattr(builtins,operador)
    except AttributeError :
        pass
    print('ERROR: operador {} no encontrado en la ejecucion dinamica'.format(operador))
    return None
