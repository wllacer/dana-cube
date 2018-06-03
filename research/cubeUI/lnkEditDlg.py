#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Todo list tras completar validators y setters
-> en repeatable add debe dividirse en (insert after, insert before, append). General de editTree
-> DONE Incluir llamada a la consulta de guia
-> Incluir llamada al grand total
-> DONE Las fechas artificiales (trimestres, cuatrimestres, ...) como opciones de menu aqui y no en info2*
-> Para sqlite que el selector de base de datos sea el selector de ficheros del sistema
-> Copy to other place
-> Restore

"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse


from support.gui.treeEditor import *
from research.cubebrowse import *
from research.cubeTree import *
from base.datadict import DataDict

from PyQt5.QtWidgets import QFrame

"""
GETTERS
    executed at start of SetEditorData 
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist 
    input
            editor,
            item,
            view,
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)
    output
            dato  (Qt.UserRole + 1 value)
            display (Qt.DisplayRole)

SETTERS
    executed at the end of SetModelData
    admits one "default" as text, to position where the basic model update will perform. 
    If no "default" is specified ... ya know, by hand ...
    parmlist
        input  *lparm
            item = lparm[0]
            view = lparm[1]
            context = lparm[2]   Fundamentalmente para obtener el valor original context['data']
            ivalue / values = lparm[3]
            dvalue = lparm[4]
        output
            item, the edited item
"""
def getLinks(*lparm):
    editor = lparm[0]
    item = lparm[1]
    view = lparm[2]
    dato = lparm[3]
    display = lparm[4]
    
    # determino el tipo de informacion que voy a pasar como estructura
    context = Context(item)
    item = item.parent().child(item.row(),0)  #normalizo la posicion del item
    tipo = context['editType']
    head = context['repeteable']
    instance = context['repeatInstance']
    if tipo == 'link via':
        headItem = getParentByType(item,'prod')
        structure = tree2dict(headItem,isDictFromDef)
        #pprint(structure)
        #exit()
    else:
        print('Se disparo aqui',tipo)
    #determino la informacion contextual para el dialogo
    baseTableItm = getChildByType(getParentByType(item,'base'),'table')
    baseTable = baseTableItm.parent().child(baseTableItm.row(),1).data()
    
    confName,confData = getConnection(item,name=True,dict=view.dataDict)
    schema = getSchema(item,baseTable)

    #Instancio los getters 
    relGetter = relCatcher(item,view,confName,schema)
    gparm = [item,view,None]
    tables = srcTables(*gparm)
    gparm[2] = tables
    fieldGetter = fieldCatcher(*gparm)

    environ = {'pfile':baseTable.split('.')[-1],'tablas':tables,'fields':fieldGetter,'rel':relGetter,'tipo':tipo,'headItem':headItem,
                        'structure':structure }
    
    return environ,display

def setLinks(*lparm):
    item = lparm[0]
    view = lparm[1]
    context = lparm[2]  
    values = lparm[3]
    head = values['headItem']
    for k in range(head.rowCount()):
        head.model().removeRow(0,head.index())

    dict2tree(head,None,values['structure'],'prod',direct=True)
    head.setData(values['structure'].get('name',head.data(Qt.DisplayRole)),Qt.DisplayRole)
    return item

class LinksDlg(manualLinkDlg):
    """
    especializacion de manualLinkDlg para simplificar su uso cuando es dialogo directo sobre elemento de linkvia
    TODO unificarlo en un solo dialogo. NO lo he hecho para poder seguir trabajando
    
    """
    def setData(self,dato):
        self.defaultData = dato
        self.initialValues(**dato)
        
    def initialValues(self,**kwparm): #file,tablas,fields,rel,structure):pfile,tablas,fields,rel,structure=None,parent=None,):
        if not kwparm:
            return 
        else:
            self.sheet.currentItemChanged.disconnect()
            self.sheet.itemChanged.disconnect()
            self.disableDetail()            
            file = kwparm.get('pfile')
            tablas = kwparm.get('tablas',[])
            fields = kwparm.get('fields')
            rel = kwparm.get('rel')
            structure = kwparm.get('structure',{})

            self.fullTables = tablas
            self.tables = [ elem[1] for elem in tablas ]
            
            iidx = self.tables.index(file)
            self.baseTable = self.fullTables[iidx][0]
            self.fields = fields
            self.rel = rel
            if not structure:
                self.structure = {}
            else:
                if 'prod' in structure:
                    self.structure = structure['prod'][0]
                else:
                    self.structure = structure
                    
            self.name.setText(self.structure.get('name',""))
            self.array = self.denorm([ elem for elem in self.structure.get('link via',[])])
            #self.fileStack =  [file, ] + [ elem.get('table') for elem in self.array ]
            self.fileStack =  [file, ] + [ elem.get('table').split('.')[-1] for elem in self.array ]
            for k in range(len(self.array)):
                line = self.array[k]
                line['internalLink'] = None
                del line['table']
            if self.array:
                self.targetTable = self.fileStack[-1]
                self.targetFields = self.denorm(norm2List(self.structure.get('elem')))
            else:
                self.targetTable= None
                self.targetFields = []

        self.initializeSheet(self.fileStack)
        if len(self.array) >= 1:
            pos = len(self.fileStack) -1
            self.sheet.setCurrentCell(pos,0)
            self.loadDetail(pos)
            #self.loadTarget()
            self.enableDetail()    

        self.setClauseWgtSize()
        self.sheet.currentItemChanged.connect(self.moveSheetSel)
        self.sheet.itemChanged.connect(self.itemChanged)
   
    def denorm(self,struct):
        if isinstance(struct,(list,tuple)):
            for ind,linea in enumerate(struct):
                struct[ind] = self.denorm(linea)
        elif isinstance(struct,dict):
            for key in struct:
                struct[key] = self.denorm(struct[key])
        elif isinstance(struct,str):
            if ' ' in struct or '(' in struct:
                pass
            else:
                return struct.split('.')[-1]

        return struct
        
    #def getData(self):
        #dato = None
        #print('LinksDlg set Data')
        #return dato
    def getData(self):
        #TODO verificar los datos
        print('GET DATA')
        stablas = [ self.sheet.item(k,0).text()  for k in range(1,self.sheet.rowCount())  if self.sheet.item(k,0).text() ]
        if len(stablas) == 0:
            self.msgLine.setText('Debe definir al menos una tabla de enlace')
            self.sheet.setFocus()
            return
        if not self.validateArray():
            return
        
        tablasFQ = []
        for entrada in stablas:
            if entrada == "":
                break
            tablasFQ.append(self.short2long(entrada))

        #TODO expandir los internalLinks
        links = []
        for k in range(len(tablasFQ)):
            if tablasFQ[k] == '':
                continue
            if  self.array[k].get('internalLink'):
                arcos = self.linkTransform(k,tablasFQ)
                for arco in arcos:
                    links.append(arco)
            elif self.array[k].get('clause'):
                arco = self.clauseTransform(k,tablasFQ)
                arco['table'] = tablasFQ[k]
                links.append(arco)
        name = self.name.text()
        #resultado = { 'link via':links,'elem':self.fieldsTarget.seleList,'name':self.targetTable,'table':self.targetTable}
        dato = self.defaultData.copy()
        dato['structure']['name'] = name
        dato['structure']['elem'] = [ self.fields.tr(self.targetTable,value) for value in self.fieldsTarget.seleList ]
        dato['structure']['table'] = self.short2long(self.targetTable)
        dato['structure']['link via'] = links
        return dato


    def reject(self):
        #FIXME esto creo que no es tan simple en este caso
        if self.defaultData:
            self.initialValues(**self.defaultData)
        super().reject()

#EDIT_TREE['link via'] = {'objtype':'dict',
                #'elements':[
                    #('table',True,False),
                    #('clause',True,False,True), #FIXME presentacion
                    #('filter',False,False),
                    #],
                #'getters':[ getLinks, ],
                #'setters':[ setLinks, ],                
                #'editor': LinksDlg,
                #}
                
