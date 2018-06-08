#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from support.gui.widgets import * 
from support.gui.dialogs import WNameValue
from support.util.record_functions import norm2List,osSplit
import base.config as config

from PyQt5.QtCore import Qt,QModelIndex,  QPersistentModelIndex
from PyQt5.QtGui import QStandardItemModel,QColor
from PyQt5.QtWidgets import QTreeView, QMenu, QStyledItemDelegate, QInputDialog, QMessageBox,\
    QSpinBox, QListWidget, QPushButton,QLabel, QCheckBox , QLineEdit, QComboBox, QTextEdit, QDialog,QListWidget,QDialog,\
    QVBoxLayout

from support.util.treeEditorUtil import *
"""
Funciones para leer la configuracion de user functions. Reutilizadas, creo
"""
class displayTree(QStandardItemModel):
    """
    Overloaded QStandardITemModel
    Just for domain specific changes at the EDIT_TREE
    
    Quizas me he pasado de colorines
    """
    def data(self,index,role=Qt.UserRole +1):
        if index.column() == 1:
            if role in (Qt.DisplayRole, ):
                context = Context(index)
                rowHead = context.get('rowHead')
                if role == Qt.DisplayRole and context.get('edit_tree',{}).get('hidden',False):
                    return '****'
                if ( context.get('edit_tree',{}).get('objtype','atom') != 'atom' and
                    context.get('edit_tree',{}).get('editor',None) is not None):
                    # algunas veces la cabecera tiene ya los datos
                    if not rowHead.hasChildren() and super().data(index,role) is None:
                            return 'pulse aquí para editar la lista'
                    else:
                            return branch2text(rowHead)
            elif role in (Qt.BackgroundRole,):
                # la sintaxis es para que el data sea del item y no del arbol
                # si la celda tiene algun tipo de color se lo mantenemos
                orig = self.itemFromIndex(index).data(role)
                if orig is not None:
                    return orig
                context = Context(index)
                rowHead = context.get('rowHead')
                if ( context.get('edit_tree',{}).get('objtype','atom') != 'atom' and
                    context.get('edit_tree',{}).get('editor',None) is not None):
                    if context.get('mandatory',False) and not rowHead.hasChildren():
                        return QColor(Qt.yellow)
                    else:
                        return QColor(Qt.cyan)
                if context.get('readonly',False):
                    return QColor(Qt.gray)
                if context.get('mandatory',False) and not rowHead.hasChildren():
                    return QColor(Qt.yellow)
            elif role == Qt.ToolTipRole:
                context = Context(index)
                if context.get('edit_tree',{}).get('hint'):
                    return context.get('edit_tree',{}).get('hint')
                elif context.get('edit_tree',{}).get('text'):
                    return context.get('edit_tree',{}).get('text')
                    
        return super().data(index,role)

class Context():
    """
    Esta clase es la interfaz en tiempo de ejecucion del contexto dentro del arbol en que se encuentra el item.
    El contexto como tal se almacena en el diccionario self.content, con los siguientes contenidos
         self.content = {
                'rowHead': el elemento 0 de la fila, es por el que se navega
                'name': el nombre del elemento
                'data': el valor del elemento (fila) 
                'type': el tipo en el dominio del problema de elemento si lo tiene
                'dtype': tipo de entrada (atom ica, list una lista ordenada dict una coleccion de nombres:valores
                'topLevel': si es el elemento de mas alta jerarquia 
                'listMember': si la entrada forma parte de una lista
                'editPos': donde va el cursor de edición (al mismo elemento o en bloque por su padre
                'editType': el tipo, dentro del dominio de edicion, del elemento
                'mandatory': si es obligatorio en ese contexto
                'readonly': si es solo lectura
                'repeteable': si es un elemento repetible (en cabecera), p.e. una lista de reglas de produccion
                'repeatInstance': si este elemento es una instancia indidual de un elemento repetibke
                'edit_tree': los detalles de edicion para este tipo de elemento
                'hasname': si tiene un atributo nombre
            
        La forma actual se debe que comenzo su vida como un diccioario simple, y hemos decidido mantener una sintaxis
        compatible
        Cada instanciacion -en nuestro ordenador- tarda sobre 10-4 s, con lo que, en un entorno interactivo no parece miy costoso.
        Por comparar, como llamada a una funcion que creara el diccionario la instanciacion era un 20% mas rápido, pero a largo plazo como objeto parece mas sensible (la posibilidad de determinar entrdas en tiempo real), y el margen parece seguro
        
        Importante que antes de usarlo se defina el atributo de clase EDIT_TREE para rellenar con las definiciones del dominio problema, bien con
        ```
           Context.EDIT_TREE = arbol_local
           ...
           var = Context(item)
        ```
        para toda la sesion del programa
        o al inicializar el contexto individual
        ```
            var = Context(item,arbol_local)
        ```
    
    Existe un problema con el contexto,y es que esta preparado para la estructura trina que utilizo en los arboles (nombre,valor,tipo) y puede no reflejar otras situaciones tipo arbol
    
    """
    EDIT_TREE = None
    def __init__(self,item_ref,Tree = None):
        if isinstance(item_ref,QModelIndex):
            item = item_ref.model().itemFromIndex(item_ref)
        else:
            item = item_ref
        model = item.model()  
        if item == model.invisibleRootItem():
            print('Cabecera de cartel, nada que hacer de momento')
            return
        
        if Tree is None:
            self.tree = Context.EDIT_TREE
        else:
            self.tree = Tree
        #obtengo la fila entera y cargo los defectos
        n,d,t = getRow(item.index())
        # obtengo el padre
        if n.parent() is None:
            isTopLevel = True
            np = dp = tp = None
        else:
            np,dp,tp = getRow(n.parent().index())
            isTopLevel = False
        editPosition = d
        if t:
            editType,edit_data = getRealEditDefinition(item,self.tree,t.data())
        else:
            editType = None
            edit_data = {}
        
        if editType:
            dataType = self.tree.get(editType,{}).get('objtype','atom')
        else:
            dataType = 'atom'
    # corrigo para listas implicitas
        if n.hasChildren() and dataType == 'atom':
            nh,dh,th = getRow(n.child(0,0).index())
            if nh.data() is None:
                dataType = 'list'
            else:
                dataType = 'dict'

        # ahora determino los atributos que dependen del padre
        isMandatory = False
        isReadOnly = False
        isRepeteable = False
        isRepeatInstance = False
        isListMember = False

        if tp:
            tpType,tpEdit_data = getRealEditDefinition(np,self.tree,tp.data())
            tipoPadre =  tpEdit_data.get('objtype')
            if tipoPadre == 'dict':
                elementosPadre = tpEdit_data.get('elements',[]) #ya esta expandido
                if t and t.data():
                    try:
                        idx  = [ dato[0] for dato in elementosPadre ].index(t.data())
                        isMandatory = elementosPadre[idx][1]
                        isReadOnly = elementosPadre[idx][2]
                        if len(elementosPadre[idx]) > 3:
                            isRepeteable = elementosPadre[idx][3]
                    except ValueError:
                        pass
                #de momento desactivado
                #if edit_data.get('editor') is None:
                    #editPosition = dp
                    #editType,edit_data = getRealEditDefinition(np,self.tree,tpType)
                    #dataType = 'dict'
                    #if tpEdit_data.get('editor') is None:
                        #edit_data['editor'] = WNameValue
            elif tipoPadre == 'list':
                isListMember = True
                hijosPadre = tpEdit_data.get('children')
                edit_ctx_hijo = self.tree.get(hijosPadre)
                #cuando es una lista sin tipos hijo, solo dejamos editar en la cabeza
                if edit_ctx_hijo:
                    if not t:
                        editType,edit_data = getRealEditDefinition(np,self.tree,hijosPadre)
                else:
                    editPosition = dp
                    editType,edit_data = getRealEditDefinition(np,self.tree,edit_ctx_hijo)
                    dataType = 'list'
                    
            else: #es hijo de un atom
                isListMember = True
                if not t or t.data() is None:
                    editPosition = dp
                    editType,edit_data = getRealEditDefinition(np,self.tree,tpType) if tp else [None,{}]
                    dataType = 'list'
            
            if t and t.data() and t.data() == tpType:  #es un elemento repetible
                isRepeatInstance = True
        
            
        #TODO puede ser interesante para name vlaue paisrs
        hasName = False if not isTopLevel else True
        if edit_data and  'elements' in edit_data:
            elementos = [ elements[0] for elements in getFullElementList(self.tree,edit_data['elements']) ]
            #if editType == 'category item':
                #print(elementos)
            if 'name' in elementos or 'result' in elementos:
                hasName = True
    
        self.content = {
                'rowHead':n,
                'name':n.data() if n else None,
                'data':d.data() if d else None,
                'type':t.data() if t else None,
                'dtype':dataType,
                'topLevel':isTopLevel,
                'listMember':isListMember,
                'editPos': editPosition,
                'editType':editType,
                'mandatory':isMandatory,
                'readonly':isReadOnly,
                'repeteable':isRepeteable,
                'repeatInstance':isRepeatInstance,
                'edit_tree':edit_data,
                'hasname':hasName,
                }
    def get(self,entrada,default=None):
        return self.content.get(entrada,default)
    def __getitem__(self,entrada):
        return self.content[entrada]
    def __setitem__(self,entrada,valor):
        self.content[entrada] = valor

 
class TreeMgr(QTreeView):
    """
    """
    def __init__(self,model,treeDef,firstLevelDef,ctxFactory,msgLine=None,parent=None):
        """
        parametros model .-> modelo a procesar
                           treeDef -> Definicion del arbol
                           firstLevelDef -> List of first level elements
                           ctxFactory -> generador de contexto
        """
        super(TreeMgr, self).__init__(parent)
        self.parentWindow = parent
        self.view = self  #truco para no tener demasiados problemas de migracion
        self.treeDef = treeDef
        self.firstLevelDef = firstLevelDef
        self.ctxFactory = ctxFactory
        self.view.setAlternatingRowColors(True)
        #self.view.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.SelectedClicked)
        if msgLine:
            self.msgLine = msgLine
        else:
            self.msgLine = QLabel()  #nunca va a funcionar pero asi no debe darme errores 
        self.baseModel  = model
        parent = self.hiddenRoot = self.baseModel.invisibleRootItem()
        self.view.setModel(self.baseModel)
      
        self.view.expandAll() # es necesario para el resize
        for m in range(self.baseModel.columnCount()):
            self.view.resizeColumnToContents(m)
        self.view.collapseAll()

        delegate = TreeDelegate(self)
        self.setItemDelegate(delegate)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.openContextMenu)

        self.copyContext = None
        
        #print('inicializacion completa')
        #self.setEditTriggers(QAbstractItemView.NoEditTriggers)
    
    def openContextMenu(self,position):
        menu = QMenu()
        self.ctxMenu = []
        indexes = self.selectedIndexes()
        if len(indexes) > 0:
            index = indexes[0]
        else:
            return
        context = self.ctxFactory(index)
        n = context.get('rowHead')
        edit_data = self.treeDef.get(context.get('editType'),{})
        if context.get('topLevel',False):
            for entrada in self.firstLevelDef:
                texto = context.get('edit_tree',{}).get('text',entrada)
                self.ctxMenu.append(menu.addAction("Add new {}".format(texto),
                                    lambda i=self.model().invisibleRootItem(),j=entrada:self.actionAddTop(i,j))) 
            self.ctxMenu.append(menu.addAction("Duplicate",lambda i=n:self.actionDuplicate(i)))
            self.ctxMenu.append(menu.addAction("Rename",lambda i=n:self.actionRename(i))) 
            menu.addSeparator()
            
        for linea in edit_data.get('menuActions',[]):
            linea[0](n,self,self.ctxMenu,menu,linea[1])
            #self.ctxMenu.append(menu.addAction(linea[1],lambda i=n:linea[0](i,self)))
        self.ctxMenu.append(menu.addAction("Copy",lambda i=n:self.actionCopy(i),"Ctrl+C"))
        if self.copyContext and context.get('type') == self.copyContext[1]:

            self.ctxMenu.append(menu.addAction("Paste",lambda i=n:self.actionPaste(i),"Ctrl+V"))
            
        if context.get('topLevel',False) or ( not context.get('mandatory',False)):
            self.ctxMenu.append(menu.addAction("Remove",lambda i=n:self.actionRemove(i)))
            
        if context.get('edit_tree',{}).get('editor',None) is None:
            if context.get('dtype','atom') == 'list':
                if not context.get('listMember',False):  # cabeza
                    self.ctxMenu.append(menu.addAction("Clear list",lambda i=n:self.clearList(i)))
                    self.ctxMenu.append(menu.addAction("Add entry",lambda i=n:self.addEntry(i)))
                datos = n.model().itemFromIndex(n.index().sibling(n.row(),1) )        
                if datos.data():
                    self.ctxMenu.append(menu.addAction("entry to list ",lambda i=n:self.convertToList(i)))
            elif edit_data.get('objtype','atom') == 'dict' and edit_data.get('elements',None) is None:
                self.ctxMenu.append(menu.addAction("Edit as name/value pairs",lambda i=n:self.actionNameValue(n)))
    
        menu.addSeparator()
        
        self.getMenuOptionsDetail(menu,n,context)
        
        action = menu.exec_(self.viewport().mapToGlobal(position))
        
    def getMenuOptionsDetail(self,menu,rowHead,context):
        """
        parameters:
        menu
        n -> rowHead
        context
        
        aqui pongo las funciones que dependen del tipo de objeto
        """
        edit_data = self.treeDef.get(context.get('editType'),{})
        
        if context.get('repeteable',False):
            tipoAEditar = context.get('editType')    
            texto = context.get('edit_tree',{}).get('text',tipoAEditar)
            self.ctxMenu.append(menu.addAction("Add {}".format(texto),
                                                   lambda i=rowHead,j=tipoAEditar:self.actionAdd(i,j)))
        
        else:
            if context.get('repeatInstance',False) or context.get('listMember',False):
                self.ctxMenu.append(menu.addAction("Move first",lambda i=rowHead:moveInList(i,'first')))
                self.ctxMenu.append(menu.addAction("Up",lambda i=rowHead:moveInList(i,'-1')))
                self.ctxMenu.append(menu.addAction("Down",lambda i=rowHead:moveInList(i,'+1')))
                self.ctxMenu.append(menu.addAction("Move last",lambda i=rowHead:moveInList(i,'last')))
            if context.get('repeatInstance',False):
                self.ctxMenu.append(menu.addAction("Duplicate",lambda i=rowHead:self.actionDuplicate(i)))
                self.ctxMenu.append(menu.addAction("Rename",lambda i=rowHead:self.actionRename(i))) 
            menu.addSeparator()
            if 'subtypes' in edit_data:
                subtipo = subTypeDiscover(rowHead,edit_data)
                if subtipo :
                    context['editType'] = subtipo
                    edit_data = mergeEditData(edit_data,self.treeDef.get(subtipo,{}))
                
            if 'elements' in edit_data:
            # creo que es lo mas sensible hacer. Localizo los elementos que ya existen
                existentes = set()
                for k in range(rowHead.rowCount()):
                    child = rowHead.child(k,0)
                    ns,js,ts = getRow(child.index())
                    if ts.data():
                        existentes.add(ts.data())
                        
                elementos = getFullElementList(self.treeDef,edit_data.get('elements',[]))                    
                for elemento in elementos:
                    if elemento[0] in existentes:
                        pass
                    else:
                        texto = self.treeDef.get(elemento[0],{}).get('text',elemento[0])
                        self.ctxMenu.append(menu.addAction("Add {}".format(texto),
                                                    lambda i=rowHead,j=elemento[0]:self.actionAdd(i,j)))
            menu.addSeparator()
        

    def actionRemove(self,item):
        rownr = item.row()
        diggers= self.ctxFactory(item).get('edit_tree',{}).get('diggers',[])
        pai = item.parent()
        if pai is None: #topLevel
            item.model().removeRow(rownr)
        else:
            item.model().removeRow(rownr,pai.index())
        
        if len(diggers) >0:
            for dig in diggers:
                dig(pai,self)
    
    def actionAdd(self,item,newItemType):
        """
        """
        def __getParentRepeatStatus(itm):
            """
            Determino cual es el elemento padre de este elemento
            determino si el elemento forma parte de un repeat group. Si lo es cambia el parent (parece que aqui no ha funcionado lo
            del objeto como parametro es referencia, por eso lo hago explicitamente
            Si es un repeat group y no hay cabecera, la da de alta al paso ...
            """
            if itm.column() == 0:
                parent = itm
            else:
                parent = itm.model().itemFromIndex(itm.index().sibling(itm.row(),0))
            if not parent:
                return None,False
        #correccion para el caso de que sean elementos repetibles y sea el primero
            ctxParent = self.ctxFactory(parent)
            if ctxParent.get('editType') == newItemType:
                return parent,True
            else:
                elementosPadre = ctxParent.get('edit_tree',{}).get('elements',[])
                try:
                    idx = [elemento[0] for elemento in elementosPadre].index(newItemType)
                except ValueError:
                    # FIXME esto es un parche, no una solucion coherente
                    # en un alta es posible que no conozcamos todavia que subtipo 
                    # por tanto tenemos que forzar un pastiche incluyendo todos los subtipos
                    if ctxParent.get('edit_tree',{}).get('subtypes'):
                        for subtipo in ctxParent.get('edit_tree',{}).get('subtypes'):
                            elementosPadre += getFullElementList(self.treeDef,self.treeDef[subtipo].get('elements'))
                        idx = [elemento[0] for elemento in elementosPadre].index(newItemType)
                    else:
                        raise
                if len(elementosPadre[idx]) > 3 and elementosPadre[idx][3]:  #repetible, con esto ya deberia valer pero aseguro la situacion
                    cabeceraCartel = getChildByType(parent,newItemType)
                    if not cabeceraCartel:
                        newHeader = makeRow(newItemType,None,newItemType)
                        parent.appendRow(newHeader)
                    return newHeader[0],True
            return parent,False
                
        edit_data = self.treeDef.get(newItemType,{})

        parent, repeatInstance= __getParentRepeatStatus(item)
                
        def_val = edit_data.get('default',None)
        valor_defecto = None
        if def_val and callable(def_val):
            valor_defecto = def_val(item,self)
        else:
            valor_defecto = def_val
        
        if edit_data.get('objtype','atom') != 'group':
            newRow = makeRow(newItemType,valor_defecto,newItemType)
            if parent is None:
                self.model().appendRow(newRow)
            else:
                parent.appendRow(newRow)
                
            self.addChildren(newRow[0],edit_data,newItemType)
            
            self.setCurrentIndex(newRow[0].index())
        # este es el sitio para realizar el cambio de nombre
            ftype,fedit_data = getRealEditDefinition(newRow[0],self.treeDef,newItemType)
            #print('action rename',newRow[0].data(),ftype,fedit_data)
            if 'elements' in fedit_data:
                campos = [elem[0] for elem in fedit_data['elements'] ]
                for nombre in ('name','result','default'):
                    if nombre in campos:
                        self.actionRename(newRow[0],nombre)
                        break
                else:
                    if repeatInstance:
                        newRow[0].setData(newRow[0].row(),Qt.UserRole +1)
                        newRow[0].setData(str(newRow[0].row()),Qt.EditRole)
                for funcion in edit_data.get('setters',[]):
                    funcion(newRow[0],self,self.ctxFactory(newRow[0]),None)
        
            return newRow[0]
        else:
            self.addChildren(item,edit_data,newItemType)
            self.setCurrentIndex(item.index())
            return item
            
        

    def addChildren(self,newHead,edit_data,tipo):
        """
        separada 
        """
        if edit_data.get('subtypes'):
            ok = False
            lista = []
            ilista = []
            for entrada in edit_data.get('subtypes'):
                lista.append(self.treeDef.get(entrada,{}).get('text','{} de tipo {}'.format(tipo,entrada)))
                ilista.append(entrada)
            text,ok = QInputDialog.getItem(None,'Seleccione el tipo de {} a añadir'.format(tipo),'tipo',lista,0,False)
            if ok and text:
                subtipo =ilista[lista.index(text)]
            else:
                return

            edit_data = mergeEditData(edit_data,self.treeDef.get(subtipo,{}))
            self.addChildren(newHead,edit_data,subtipo)
        else:
            if edit_data.get('elements'):
                for entrada in getFullElementList(self.treeDef,edit_data['elements']) :
                    #FIXME solo los obligatorios:
                    if len(entrada) > 3 and entrada[3]: # es solo un repeat
                        newHead.appendRow(makeRow(entrada[0],None,entrada[0]))
                    #elif entrada[1]:
                    else:
                        self.actionAdd(newHead,entrada[0])
        #TODO falta colocar el foco y validar obligatorios
    
    def actionAddTop(self,item,newItemType):
        pos = self.actionAdd(item,newItemType)
        self.actionRename(pos)
       
    def actionRename(self,item,campo=None):
        #TODO necesita un alta ¿?
        text = QInputDialog.getText(None, "Nuevo nombre para el nodo: "+item.data(),"Nodo", QLineEdit.Normal,item.data())
        if text[0] and text[0] != '':
            item.setData(text[0],Qt.EditRole)
            item.setData(text[0],Qt.UserRole +1)
        #propago
        n,i,t = getRow(item)
        if n.hasChildren():
            for k in range(n.rowCount()):
                nh,ih,th = getRow(n.child(k))
                if nh.data() in ('name','result','default'):
                    ih.setData(text[0],Qt.EditRole)
                    ih.setData(text[0],Qt.UserRole +1)
                    break
       
    def actionDuplicate(self,item):
        newHead = duplicateSubTree(item)
        self.actionRename(newHead)
        
    def actionCopy(self,item):
        tipoPadre = 'root'
        if item.parent():
            np,ip,tp = getRow(item.parent())
            tipoPadre = tp.data()
            if not tipoPadre:
                self.msgLine.setText("Problemas en la especificacion del tipo a copiar, cancelando")
                return
        self.copyContext=(item,tipoPadre)
    
    def actionPaste(self,item):
        """
        TODO comprobar que sean iguales
        """
        oitem = self.copyContext[0]
        otype = self.copyContext[1]
        ocontext = self.ctxFactory(oitem)
        n,i,t = getRow(item)
        if t.data() != otype:
                self.msgLine.setText("Destino inadecuado para el objeto copiado, cancelando")
                return None
        sub = cloneSubTree(oitem)
        if ocontext.get('repeteable'):
            nitem = getChildByType(item,ocontext.get('type'))
            if nitem:
                head = sub.item(0)
                for k in range(head.rowCount()):
                    row = head.takeRow(k)
                    nitem.appendRow(row)
            else:
                row = sub.takeRow(0)
                item.appendRow(row)
        elif ocontext.get('repeatInstance',False):
            row = sub.takeRow(0)
            item.appendRow(row)
        else:
            # substituyo 
            nitem = getChildByType(item,ocontext.get('type'))
            if nitem:
                item.removeRow(nitem.row())
            row = sub.takeRow(0)
            item.appendRow(row)
        self.copyContext = None
        
        return row
        
    def actionNameValue(self,item):
        """
        """
        context = self.ctxFactory(item)
        cab = context.get('rowHead')
        datos = []
        for k in range(cab.rowCount()):
            nombre = cab.child(k,0).data()
            valor = branch2text(cab.child(k,0))
            datos.append([nombre,valor])
        form = WNameValue(datos)
        form.setWindowTitle('Edicion de {}'.format(nombre))
        form.show()
        form.raise_()
        if form.exec():
            resultado = form.result
            #self.msgLine.setText('Validacion para {} realizada'.format(nombre))
        else:
            return 
        # eliminado, aqui no parece apropiado
        #for funcion in context.get('edit_tree',{}).get('validators',[]):
            #if not funcion(item,resultado):
                #self.msgLine.setText('Validacion para {} fallida'.format(nombre))
                #print('validacion fallida')  #TODO a mensaje o similar
                #self.setCurrentIndex()
                #return
        
        pai = cab.parent()
        rownr = cab.row()
        nombre = cab.data()
        texto = context.get('data')
        tipo = context.get('type')
        if pai is None: #topLevel
            pai = item.model().invisibleRootItem()
            item.model().removeRow(rownr)
        else:
            item.model().removeRow(rownr,pai.index())

        dict2tree(pai,nombre,resultado,tipo=tipo)

        for funcion in context.get('edit_tree',{}).get('setters',[]):
            funcion(item,self,context,resultado)

        #form = WNameValue(datos)
        #form.show()
        #form.raise_()
        #if form.exec():
            #values = form.sheet.values()
            #for entrada in values:
                #item.appendRow(makeRow(entrada[0],entrada[1],entrada[0]))
 
    def clearList(self,item):
        nitem = item.model().itemFromIndex(item.index().sibling(item.row(),0) )                    
        while nitem.rowCount() > 0:
            item.removeRow(0)

    def addEntry(self,item):
        nitem = item.model().itemFromIndex(item.index().sibling(item.row(),0) )       
        text,ok = QInputDialog.getText(None, "Nueva entrada para: "+nitem.data(),"Valor", QLineEdit.Normal,'')
        if ok and text:
            nRow = makeRow(None,text,None)
            nitem.appendRow(nRow)

    def convertToList(self,item):
        n,i,t = getRow(item)
        if not i.data():
            return 
        for entrada in norm2List(i.data()):
            nRow = makeRow(None,entrada,None)
            n.appendRow(nRow)
        i.setData(None,Qt.EditRole)
        i.setData(None,Qt.UserRole +1)
 
    def prune(self,exec=False):
        def localiza(model,head,to_remove,to_check):
            for k in range(head.rowCount()):
                item = head.child(k)
                ctx = Context(item)
                nombre = item.data() if item.data() else '<>'
                dato = getNorm(ctx,'data')
                tipo = ctx['type'] 
                mand = ctx['mandatory']
                nchild = item.rowCount()
                if tipo in EXCLUDE_LIST:
                    continue
                msg = self.domainPrune(item,ctx)
                if msg:
                    to_check.append(msg +'/'.join(fullKey(item)))
                if mand and not dato and nchild == 0:
                    to_check.append('Obligatorio sin valor : '+'/'.join(fullKey(item)))
                elif not mand and not dato and nchild == 0:
                    if exec:
                        pmi =QPersistentModelIndex(item.index())
                        print(fullKey(item),'Opcional y vacio',pmi)
                        to_remove.append(pmi)
                    else:
                        to_check.append('Opcional sin valor : ' + '/'.join(fullKey(item)))
                else:
                    localiza(model,item,to_remove,to_check)
        model = self.model()
        EXCLUDE_LIST = self.pruneExcludeList() #['connect',]
        to_remove = []
        to_check = []
        localiza(model,model.invisibleRootItem(),to_remove,to_check)
        if exec:
            for  index in to_remove:
                model.removeRow(index.row(),index.parent())
        if to_check:
            self.showTroubledEntries('Existen entradas con anomalias',to_check)

    def showTroubledEntries(self,title,data):
        dlg = TroubledEntriesDlg(title,data)
        dlg.show()
        dlg.exec_()
    """
        ¿virtual? methods
    """
    def pruneExcludeList(self):
        return []
    
    def domainPrune(self,item,ctx):
        msg = None
        return msg
    
class TreeDelegate(QStyledItemDelegate):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.context = None 
        #para los objetos con lista
        self.isDouble = False
        self.fullList = None
        self.currentList = None 
        
    def createEditor(self,parent,option,index):
        """

        """
        if index.column() != 1:
            return 
        self.context = self.parent().ctxFactory(index)
        #pprint(self.context.content)
        if self.context.get('topLevel',False):
            return 
        if self.context.get('readonly',False):
            return
        edit_format = self.context.get('edit_tree',{})
        item = self.context.get('editPos')
        defeditor = edit_format.get('editor',QLineEdit)
        if defeditor ==  QCheckBox:
            #TODO hay que ponerle un nombre
            editor = QCheckBox(self.context.get('name'),parent)
            
        elif defeditor ==  QSpinBox:
            editor = QSpinBox(parent)
            editor.setMaximum(edit_format.get('max',99))
            editor.setMinimum(edit_format.get('min',0))
            
        elif defeditor in (QComboBox,QComboBoxIdx,WMultiCombo,WMultiList):
            #FIXME parche de presentacion
            if defeditor != WMultiList:   
                editor = defeditor(parent=parent )
            else:
                editor = defeditor()
                
            orlist = edit_format.get('source',[])
            if callable(orlist):
                self.fullList = sorted(orlist(item,self.parent()))
            else:
                self.fullList = orlist
            if isinstance(self.fullList[0],(list,tuple)):
                x,y = zip(*self.fullList)
                self.currentList = list(y)
                self.isDouble = True
            else:
                self.currentList = self.fullList
                self.isDouble = False

            if defeditor in (WMultiCombo,) :   #WMC siempre antes que QCB ya que es una especializacion
                if self.isDouble:
                    editor.load([ entry[0] for entry in self.fullList],self.currentList)
                else:
                    editor.load(self.currentList)
                #TODO  WMultiCombo as editable ... no lo veo
                #editor.setEditable(edit_format.get('editable',False))
            if defeditor in (QComboBoxIdx, QComboBox) :
                editor.addItems(self.currentList)
                editor.setEditable(edit_format.get('editable',False))
            elif defeditor in (WMultiList, ):
                editor.load(self.currentList,[])
                
        elif defeditor == QTextEdit:
            editor = defeditor()
            
        elif defeditor == WPowerTable :
            editor = defeditor(self.context('rowHead').rowCount() +2,2)
            editor.setHorizontalHeaderLabels(('nombre','valor'))
            context = []
            context.append((QLineEdit,{'setEnabled':False},None))
            context.append((QLineEdit,{'setEnabled':True},None))
            for x in range(item.rowCount()):
                for y,colDef in enumerate(context):
                    editor.addCell(x,y,colDef,defVal=None)
            editor.resizeRowsToContents()
            
        else:
            #FIXME dialogs probably won't be needed
            if defeditor == QLineEdit and self.context.get('rowHead').hasChildren():
                return
            editor = defeditor(parent)
            if isinstance(editor,QLineEdit) and edit_format.get('hidden',False):
                editor.setEchoMode(QLineEdit.Password)
            #editor.setText(dato)
        return editor
            

    def setEditorData(self, editor, index):
        model = index.model()
        edit_format = self.context.get('edit_tree',{})
        item = self.context.get('editPos')
        display = item.data(Qt.DisplayRole)
        dato = item.data(Qt.UserRole +1)
        #print('interno',dato,'externo',display,'<')
        getters = edit_format.get('getters')
        if not getters:
            getters = [ self._getDataForWidget ,]
        elif 'default' in getters:
            idx = getters.index('default')
            getters[idx] = self._getDataForWidget
        if getters:
            for funcion in getters:
                try:
                    dato,display = funcion(editor,item,self.parent(),dato,display)
                except Exception as e:
                    print('exception')
                    print(e)
                    print('funcion',funcion)
                    print('editor',editor)
                    print('item',item)
                    print('parent',self.parent())
                    print('datos',dato,display)
                    raise
        valor_defecto = None    
        if not dato:
            if isinstance(editor,QSpinBox):
                def_value = self.context.get('default',0)
            elif isinstance(editor,QCheckBox):
                def_value = self.context.get('default',False)
            else:
                def_value = self.context.get('default')
            if callable(def_value):
                valor_defecto = def_value(item,self.parent())
            else:
                valor_defecto = def_value
          
        setWidgetData(self,editor,dato,valor_defecto)

    
    def setModelData(self,editor,model,index):
        """
        TODO dobleSeleccion
        """
        
        
        model = index.model()
        values = None
        dvalue = ivalue = None
        item = self.context.get('editPos')
        datoWidget = getWidgetData(self,editor)
        
        if isinstance(datoWidget,(list,tuple,set,dict)):
            values = datoWidget
        else:
            ivalue = datoWidget
            dvalue = datoWidget
        
        if isinstance(editor, WMultiList):
            if not self.generalValidation(index,editor,values):
                return
                
        elif isinstance(editor, WMultiCombo):
                #TODO insercion
            if self.context.get('dtype','atom') == 'list':
                values = norm2List(datoWidget)
                if not self.generalValidation(index,editor,values):
                    return
            else:
                if not self.generalValidation(index,editor,dvalue,ivalue):
                    return
                
        elif isinstance(editor,QTextEdit):
            #item = self.context.get('editPos')
            if self.context.get('dtype','atom') == 'list':
                n,i,t = getRow(item)
                if t :
                    head = n
                else:
                    head = n.parent()
                values = datoWidget.split('\n')
                if not self.generalValidation(index,editor,values):
                    return
                item = head

            else:
                if not self.generalValidation(index,editor,dvalue,ivalue):
                    return

        elif isinstance(editor,QDialog):
                if not self.generalValidation(index,editor,values):
                    return

        else:
            if isinstance(editor,QComboBoxIdx):
                values = None
                ivalue = datoWidget[0]
                dvalue = datoWidget[1]
            if isinstance(editor, QComboBox) and self.isDouble:
                values = None
                ivalue,dvalue = datoWidget
            elif isinstance(editor, (QSpinBox,QCheckBox,)):
                dvalue = str(ivalue)
            elif isinstance(editor,WPowerTable):
                return
            elif isinstance(editor,QLineEdit) and self.context.get('edit_tree',{}).get('hidden',False):
                dvalue = '****'
            else:
                if dvalue in ('True','False'):
                    ivalue = str2bool(dvalue)            
    
            if not self.generalValidation(index,editor,dvalue,ivalue):
                return
                    
        setters = list(self.context.get('edit_tree',{}).get('setters',[]))
        if not setters:
            setters = [ self._updateModel, ]
        if 'default' in setters:
            idx = setters.index('default')
            setters[idx] = self._updateModel
        for funcion in setters:
            if not values:
                item = funcion(item,self.parent(),self.context,ivalue,dvalue)
            else:
                item = funcion(item,self.parent(),self.context,values)
                
    def generalValidation(self,index,editor,*lparms,**kwparms):
        # de momento suprimo el color rojo de fondo, ya que los cambios se pierden
        index.model().setData(index,None,Qt.BackgroundRole)
        self.parent().msgLine.setText('')
        self.parent().msgLine.setStyleSheet(None)
        ok, text = self.validator(editor,*lparms,**kwparms)
        if not ok:
            self.parent().msgLine.setText('Rechazada la validacion para {} : {}'.format(self.context.get('name'),text))
            self.parent().msgLine.setStyleSheet("background-color:yellow;")
            #index.model().setData(index,QColor(Qt.red),Qt.BackgroundRole)
            self.parent().setCurrentIndex(index)
            return False
        elif text and len(text.strip()) > 0:
            self.parent().msgLine.setText('{} : {}'.format(self.context.get('name'),text))
        return True

    def validator(self,editor,*lparms,**kwparms):
        msg = ''
        if isinstance(editor,(WMultiList,QDialog)) or (isinstance(editor,QTextEdit) and self.context.get('dtype','atom') != 'atom'):
            values = lparms[0]
            if self.context.get('mandatory') and len(values) == 0:
                msg = 'sin valor'
                return False , msg
        else:
            dvalue,ivalue = lparms[0:2]
            if self.context.get('mandatory') and (ivalue is None or dvalue == ''):
                msg = 'sin valor'
                return False, msg
        validators = self.context.get('edit_tree',{}).get('validators',[])
        if len(validators) == 0:
            return True, ''
        else:
            text = None
            for entry in validators:                
                ok,ptext = entry(self.context,editor,*lparms,**kwparms)
                if not ok:
                    return False, ptext
                if ptext and len(ptext.strip()) > 0:
                    text = '; '.join([text,ptext]) if text else ptext
        return True,text
                
    def _getDataForWidget(self,editor,item,view,dato,display):
        """
        view, dato, display not used
        """
        if isinstance(editor,WMultiList):
            inicial = []
            n,i,t = getRow(item)
            if n.hasChildren():
                for x in range(n.rowCount()):
                    nh,ih,th = getRow(n.child(x))
                    inicial.append(ih.data())
                return inicial,display
            elif i.data() is not None:  # hay varios casos en que la lista se ha colapsado en un solo campo
                return osSplit(i.data()),display   #aqui si merece la pena
            else:
                return [],''
                
        elif isinstance(editor,WMultiCombo): # WMC siemre antes que QCB porque es una especializacion
            #TODO doble seleccion 
            # TODO con insercion
            if self.context.get('dtype','atom') == 'list':
                aceptados = []
                n,i,t = getRow(item)
                if n.hasChildren():
                    for x in range(n.rowCount()):
                        nh,ih,th = getRow(n.child(x))
                        aceptados.append(ih.data())
            else:
                aceptados = norm2List(dato)
            return aceptados,display

        elif isinstance(editor,QTextEdit):
            # FIXME esto tiene que mejorar. Solo me sirve para el caso de case_sql
            n,i,t = getRow(item)
            if self.context.get('dtype','atom') == 'list':
                if t:
                    head = n
                else:
                    head = n.parent()
                dato = None
                for x in range(head.rowCount()):
                    nh,ih,th = getRow(n.child(x))
                    dato = '\n'.join([dato,ih.data()]) if dato else ih.data()
            return dato,display
            
        elif isinstance(editor,WPowerTable):
            result = []
            for x in range(item.rowCount()):
                childIdx = item.index().child(x,0)
                nomItem,sitem,typeItem = getRow(childIdx)
                datos = [nomItem.data(),branch2text(nomItem)]
                result.append(datos)
            return result,display
        
        else:
            return dato,display


    def _updateModel(self,*lparms):
        item = lparms[0]
        view  = lparms[1]
        context = lparms[2]
        if len(lparms) == 4:
            edit_item = self._redoTree(item,lparms[3])
        elif len(lparms) > 4:
            edit_item = self._changeItem(item,lparms[3],lparms[4])
        return edit_item
                
    def _redoTree(self,item,values):
        model = item.model()
        if item.column() != 0:
            item = model.itemFromIndex(item.index().sibling(item.row(),0))
        contador = item.rowCount()
        for k in range(contador):
            model.removeRow(0,item.index())
        for entrada in values:
            item.appendRow(makeRow(None,entrada))
        return item
    
    def _changeItem(self,item,ivalue,dvalue):
        model = item.model()
        index = item.index()
        if not dvalue:
            model.setData(index,str(index.data(Qt.UserRole +1)),Qt.EditRole)
        else:
            model.setData(index,dvalue, Qt.EditRole)                
        model.setData(index,ivalue, Qt.UserRole +1)
        item = model.itemFromIndex(index.sibling(index.row(),0))
        return item
          


class TroubledEntriesDlg(QDialog):
    def __init__(self,title,data,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Anomalias en el arbol')
        Lista = QListWidget()
        Lista.addItems(sorted(data))
        titulo = QLabel(title)
        meatlayout = QVBoxLayout()
        meatlayout.addWidget(titulo)
        meatlayout.addWidget(Lista)
        
        self.setLayout(meatlayout)
        self.setMinimumSize(640,220)
        
if __name__ == '__main__':
    exit()


