# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from util.numeros import stats

(_ROOT, _DEPTH, _BREADTH) = range(3)
(_KEY,_ITEM) = range(2)

DELIMITER=':'

def traverse(tree, key=None, mode=1):
    return tree.traverse(key,mode,output = _ITEM)
    """
        variante de TreeDict.traverse().
        En lugar de las claves devuelve el item
        TODO deberia normalizar todos los traverses
        
    #"""
    #if key is not None:
        #yield tree.content[key]
        #queue = tree.content[key].childItems
    #else:
        #queue = tree.rootItem.childItems
        ##print(queue)
        ##print('')
    #while queue:
        #yield queue[0] 
        #expansion = queue[0].childItems
        #if mode == _DEPTH:
            #queue = expansion + queue[1:]  # depth-first
        #elif mode == _BREADTH:
            #queue = queue[1:] + expansion  # width-first

class TreeItem(object):
    def __init__(self, key, ord=None, desc=None, data=None, parent=None):
        self.key= key
        if desc is None:
            self.desc = key
        elif isinstance(desc,(list,tuple)):
            try:
                self.desc = ', '.join(desc)
            except TypeError:
                self.desc = ', '.join([str(item) for item in desc ])
        else:
            self.desc = desc
         
        self.parentItem = parent
        if ord is None:
            if parent is not None:
                self.ord = self.parent().childCount()
            else:
                self.ord = 0
        else:
            self.ord = ord
        self.itemData = data
        self.statsData = None
        self.origData = None
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None
        
    def getPayload(self):
        """ Devuelve una lista con el contenido (columnas) del item
        """
        if self.itemData is None or len(self.itemData) == 1:
            return None
        else:
            return self.itemData[1:]
    
    def getStatistics(self):
        return self.statsData
    
    def getLabel(self):
        if self.itemData is None:
            return None
        else:
            return self.itemData[0]
    
    def getKey(self):
        return self.key
    
    def hasChildren(self):
        if len(self.childItems) >0:
            return True
        else:
            return False
        
    def isTotal(self):
        if self.key == '//':
            return True
        else:
            return False
        
    def isBranch(self):
        if len(self.childItems) != 0 and not self.isTotal():
            return True
        else:
            return False
        
    def isLeaf(self):
        if len(self.childItems) == 0:
            return True
        else:
            return False

    def setData(self,data):
        self.itemData = data
        
    def setBackup(self):
        if self.origData is None :
            self.origData = self.itemData[:]

    def restoreBackup(self):
        if self.origData is not None :
            self.itemData = self.origData[:]
        else:
            self.itemData = None
      
    def lenPayload(self):
        return len(self.itemData) -1
    
    def setPayload(self,data):
        if self.itemData is None:
            self.itemData = [None,] + data
        else:
            self.itemData[1:] = data[:]
    
    def getPayloadItem(self,ind):
        try:
            return self.itemData[ind +1]
        except IndexError:
            return None      
    
    def gpi(self,ind):
        return self.getPayloadItem(ind)
    
    def setPayloadItem(self,ind,data):
        self.itemData[ind +1]=data
    
    def spi(self,ind,data):
        self.setPayloadItem(ind,data)
        
    def setLabel(self,label):
        if self.itemData is None:
            self.itemData = [label ,]
        else:
            self.itemData[0]=label
        
    def setStatistics(self):
        stat_dict = stats(self.getPayload())
        self.statsData=stat_dict

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0
    
    def depth(self):
        """
          la profundidad del arbol en ese punto. Empezando desde 1
        """
        ind = 0
        papi = self.parentItem
        while papi is not None:
            papi = papi.parentItem
            ind += 1
        return ind
    
    def getLevel(self):
        """
          el nivel actual. empieza en 0
        """
        return self.depth() -1
    
    def getFullDesc(self):
        fullDesc = [] #let the format be done outside
        fullDesc.append(self.desc)
        papi = self.parentItem
        while papi is not None:
            if papi.parentItem is None or papi.key == '//':  #FIXME esto es un chapu
                break
            fullDesc.insert(0,papi.desc) #Ojo insert, o sea al principio
            papi = papi.parentItem
        return fullDesc
    
    def getRoot(self):
        item = self
        while item.parentItem:
            item = item.parentItem
        return item

    def simplify(self):
        npay = list()
        ncab = list()
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            npay.append(value)
            ncab.append(k +1)
        return npay,ncab

    def simplifyHierarchical(self):
        profundidad = self.depth()
        tmppay = list()
        ncab = list()
        kitem = self
        while kitem.parent():
            tmppay.insert(0,kitem.getPayload())
            kitem = kitem.parent()
            
        npay = [list() for k in range(profundidad) ]    
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            for j in range(profundidad):
                npay[j].append(tmppay[j][k])
            ncab.append(k +1)
        return npay,ncab

    def model(self):
        rootItem = self.getRoot()
        return rootItem.modelID
    
    def __getitem__(self,campo):
        if campo == 'campo':
            return self.campo
        elif campo == 'desc':
            return self.desc
        elif campo == 'ord':
            return self.ord
        elif campo == 'key':
            return self.key
        elif isinstance(campo,int):
            return self.itemData[campo]
        else:
            return None
        
    def __str__(self): 
        return '{}->{}'.format(self.key,self.desc)
        
    def __repr__(self): 
        return 'TreeItem({},{},{})'.format(self.key,self.ord,self.desc)

class TreeDict(object):
    def __init__(self):
        self.content={}
        self.rootItemKey="/"
        self.rootItem=TreeItem(self.rootItemKey,-1,"RootNode")
        self.rootItem.modelID = self
        self.name = None

    def rebaseTree(self):
        if not self.exists('//'):
            self.content['//']=self.rootItem
            self.content['//'].key = '//'
            self.content['//'].desc= "Grand Total"
            newRoot=TreeItem(self.rootItemKey,-1,"RootNode")
            newRoot.appendChild(self.rootItem)
            self.rootItem.parentItem = newRoot
            self.rootItem = newRoot
            self.rootItem.modelID = self

       
    def __append(self,node):
        if node.parentItem == None:
            node.parentItem = self.rootItem
        self.content[node.key]=node
        node.parentItem.appendChild(node)
    
    def append(self,node,parentKey=None):
        if parentKey is None:
            self.__append(node)
        else:
        # este lo dejo fallar
        # tengo dos opciones
        # 1) try e ignorar las claves inexistentes y
        # 2) construir las claves sobre la marcha. De momento voy a ignorarla, puede capturar mas casos generales
            try:
                node.parentItem = self.content[parentKey]
            except KeyError :
                node.parentItem = None

            self.__append(node)

        
    def searchNode(self,key):
        try:
            return self.content[key]
        except KeyError:
            return None
     
    def count(self):
        return len(self.content)
    
    def __lenIter(self,elem):

        has = elem.childCount()
        if has != 0:
            for item in elem.childItems:
                has += self.__lenIter(item)
        return has
        
    def len(self):
        return self.__lenIter(self.rootItem)

    def queryAdd(self,node):
        if node.parentItem != None :
            pass
        else:
           node.parentItem = self.searchNode(node.key) #FIXME no tengo claro que esto sea lo que quiero
           if node.parentItem == None:
               node.parentItem = self.rootItem
        self.__add(node)
        
    def item(self,key):
        return self.__getitem__(key)
    
    def __getitem__(self, key):
        return self.content[key]
    
    def exists(self,key):
        item = self.content.get(key,None)
        if item:
            return True
        else:
            return False
    def display(self, key=None, depth=_ROOT):
        if key is None:
            children = self.rootItem.childItems
        else:
            children = self.content[key].childItems
        if depth == _ROOT:
            print("{0}".format(key))
        else:
            print("\t"*depth, "{0}".format(key))

        depth += 1
        for child in children:
            self.display(child.key, depth)  # recursive call



    def traverse(self, key=None, mode=_DEPTH, output = _KEY):
        # Obtenido de
        # Brett Kromkamp (brett@perfectlearn.com)
        # You Programming (http://www.youprogramming.com)
        # May 03, 2014, que afirma
        # Python generator. Loosly based on an algorithm from 
        # 'Essential LISP' by John R. Anderson, Albert T. Corbett, 
        # and Brian J. Reiser, page 239-241
        #if key is None:
            #yield self.rootItem.childItems[0].key
            #queue = self.rootItem.childItems[1:]
        #else:
            
        if key is not None:
            yield self.item(key) if output == _ITEM else key
            queue = self.item(key).childItems
        else:
            queue = self.rootItem.childItems
        while queue:
            yield queue[0] if output == _ITEM else queue[0].key
            expansion = queue[0].childItems
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def restrictedTraverse(self, key=None, mode=_DEPTH):
        # 
        # Basado en el anterior
        # FIXME solo valido para arboles equilibrados
        #
        if key is not None:
            yield key
            queue = self.content[key].childItems
        else:
            queue = self.rootItem.childItems
        while queue:
            if queue[0].childCount() > 0:
                yield queue[0].key
                expansion = queue[0].childItems   
            else:
                expansion = []
            if mode == _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode == _BREADTH:
                queue = queue[1:] + expansion  # width-first

    def setHeader(self):
        header = [None for k in range(self.count())] 
        for item in self.traverse(output = _ITEM):
            clave = item.getFullDesc()
            try:
                header[item.ord] = clave
            except IndexError:
                print('Canturriazo',self.count(),item,item.ord,item.model().name)
                exit()
        return header

    def getHeader(self,tipo='row',separador='\n',sparse=True):
        if sparse:
            cabecera = [ item[-1].replace(DELIMITER,'-') for item in self.setHeader() ]
        else:
            cabecera = [ separador.join([ entry.replace(DELIMITER,'-') for entry in item]) for item in self.setHeader()]
        if tipo == 'row':
            return cabecera
        else:
            return ['',] + cabecera

    def filterCumHeader(self,total=True,branch=True,leaf=True,separador='\n',sparse=True):
        lista = []
        for item in self.traverse(output = _ITEM):
            if total and item.isTotal():
                pass
            elif branch and item.isBranch():
                pass
            elif leaf and item.isLeaf():
                pass
            else:
                continue
            
            clave = item.getFullDesc()
            if sparse:
                for k in range(len(clave) -1):
                    clave[k]=''
            lista.append((item,clave,))
        return lista
        
from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QColor
from util.numeros import isOutlier,fmtNumber

LEAF,BRANCH,TOTAL = range(1000,1000+3)

def searchStandardItem(item,value,role):
    """
       modelo general de funcion de busqueda binaria en hijos de un QStandardItem o derivados
       como funcion generica porque se repite en varias circunstancias
       SOLO vale con children ordenados por el valor de busqueda (eso es muy importante)
    """
    lower = 0
    upper = item.rowCount()
    while lower < upper:   # use < instead of <=
        x = lower + (upper - lower) // 2
        val = item.child(x).data(role)
        try:
            if value == val:
                return item.child(x)
            elif value > val:
                if lower == x:   # this two are the actual lines
                    break        # you're looking for
                lower = x
            elif value < val:
                upper = x
        except TypeError:
            print(value,item.data(),item.rowCount(),'castañazo')
            raise
    return None


class TreeFormat(object):
    """
    Esta clase solo tiene propiedades de formateo del modelo (unado se usa en uan view)
    La forma actual es por compatibilidad con implementaciones anteriores
    """
    def __init__(self,**opciones):
        self.format = {}
        if 'stats' in opciones:
            self.stats = opciones['stats']
        else:
            self.stats = False
        if 'format' in opciones:
            self.format = opciones['format']
        else:
            self.format['yellowoutliers'] = True
            self.format['rednegatives'] = True
            self.format['thousandsseparator'] = "."
            self.format['decimalmarker'] = ","
            self.format['decimalplaces'] = 0
            
        
class GuideItemModel(QStandardItemModel):
    def __init__(self,parent=None):
        super(GuideItemModel, self).__init__(parent)
        self.name = None
        self.datos = TreeFormat()  #es por compatibilidad, son formatos
        self.colTreeIndex = None
        
    def traverse(self,base=None):
        if base is not None:
            yield base
            queue = [ base.child(i) for i in range(0,base.rowCount()) ]
        else:
            root = self.invisibleRootItem()
            queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        while queue :
            yield queue[0]
            expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
            if expansion is None:
                del queue[0]
            else:
                queue = expansion  + queue[1:]            
       
    def numRecords(self):
        """
        El modelo estandard no da este valor con jerarquias
        """
        count = 0
        for item in self.traverse():
            count += 1
        return count
    
    def len(self):
        return self.numRecords()

    def lenPayload(self,leafOnly=False):
        """
        columnCount() no me funciona correctametne con los nodos hoja, asi que he tenido que 
        escribir esta rutina
        """
        if leafOnly:
            return len(self.colTreeIndex['leaf']) 
        else:
            return len(self.colTreeIndex['idx'])

    def searchHierarchy(self,valueList,role=None):
        """
          busco el elemento padre con toda la jerarquia de una tacada. No se con los grandes totales
        """
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        elem = self.invisibleRootItem()
        parent = self.invisibleRootItem()
        for k,value in enumerate(valueList):
            elem = searchStandardItem(parent,value,prole)
            if not elem:
                return None
            parent = elem
        return elem

    def setStats(self,switch):
        self.datos.stats = switch
        if self.datos.stats:
            for item in self.traverse():
                item.setStatistics()
        else:
            return None
    def data(self,index,role):
        if not index.isValid():
            return None
        item = self.itemFromIndex(index)
        if role == Qt.TextAlignmentRole:
            if index.column() != 0:
                return Qt.AlignRight| Qt.AlignVCenter
            else:
                return Qt.AlignLeft| Qt.AlignVCenter
        elif role == Qt.BackgroundRole:
            #TODO TOTAL COLOR begin
            #if item.type() == TOTAL:
                #return QColor(Qt.cyan)
            #if item.type() == BRANCH:
                #return QColor(Qt.gray)
            #TOTAL COLOR end
            if item.data(Qt.DisplayRole) is None:
                return item.data(role)
            if index.column() != 0:
                #TOTAL COLOR begin
                #if item._getHead().type() == TOTAL:
                    #return QColor(Qt.cyan)
                #if item._getHead().type() == BRANCH:
                    #return QColor(Qt.gray)
                #TOTAL COLOR
                if self.datos.format['yellowoutliers'] and self.datos.stats:
                    if isOutlier(item.data(Qt.DisplayRole),item.getStatistics()):
                        return QColor(Qt.yellow)
                if self.datos.format['rednegatives'] and item.data(Qt.DisplayRole) < 0 :
                    return QColor(Qt.red)
        elif role == Qt.DisplayRole:
            datos = item.data(role)
            if datos == None:
                return None
            if index.column() == 0:
                return datos
            else:
                text, sign = fmtNumber(datos,self.datos.format)
                return '{}{}'.format(sign if sign == '-' else '',text)               
        else:
            return item.data(role)

    def filterCumHeader(self,total=True,branch=True,leaf=True,separador='\n',sparse=True):
        lista = []
        for item in self.traverse(output = _ITEM):
            if total and item.isTotal():
                pass
            elif branch and item.isBranch():
                pass
            elif leaf and item.isLeaf():
                pass
            else:
                continue
            
            clave = item.getFullDesc()
            if sparse:
                for k in range(len(clave) -1):
                    clave[k]=''
            lista.append((item,clave,))
        return lista
    
class GuideItem(QStandardItem):
    #
    #  funciones reimplementadas
    #
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        super(GuideItem, self).__init__(*args)
        self.originalValue = self.data(Qt.UserRole +1)
        if self.index().column() == 0:
            self.stats = None
    def setData(self,value,role):
        super(GuideItem, self).setData(value,role)
    def type(self):
        if self.data(Qt.UserRole +1) == '//':
            return TOTAL
        elif self.hasChildren():
            return BRANCH
        else:
            return LEAF
        
    def data(self,role):
        valor = super(GuideItem, self).data(role)
        if role in (Qt.DisplayRole,Qt.UserRole +1) and valor is None:
            valor = super(GuideItem,self).data(Qt.UserRole +1)
        return valor
    
    def __str__(self):
        return "<" + str(self.data(Qt.DisplayRole)) + ">"

    def __repr__(self):
        return "<" + str(self.data(Qt.UserRole +1)) + ">"

    #
    # funciones de API user functions
    #
    def getPayload(self,leafOnly=False):
        lista=[]
        indice = self.index() #self.model().indexFromItem(field)
        k = 1
        colind = indice.sibling(indice.row(),k)
        while colind.isValid():
            if leafOnly:
                if self.model().colTreeIndex['idx'][k]['objid'].type() == LEAF:
                    lista.append(colind.data(Qt.UserRole +1)) #print(colind.data())
            else:
                lista.append(colind.data(Qt.UserRole +1)) #print(colind.data())
            k +=1
            colind = indice.sibling(indice.row(),k)
        return lista
    
    def setPayload(self,lista,leafOnly=False):
        indice = self.index() 
        lastLeaf = 0
        for k,valor in enumerate(lista): 
            if leafOnly:
                col = self.model().colTreeIndex['leaf'][k] +1
            else:
                col = k +1
                
            colind = indice.sibling(indice.row(),col)
            if colind.isValid():
                item = self.model().itemFromIndex(colind)
                if not isinstance(item,GuideItem):
                    colroot = indice.sibling(indice.row(),0)
                    ritem = self.model().itemFromIndex(colroot)
                    ritem.setColumn(col,valor)
                else:
                    item.setData(valor,Qt.UserRole +1)
            else:
                colroot = indice.sibling(indice.row(),0)
                item = self.model().itemFromIndex(colroot)
                item.setColumn(col,valor)

    def lenPayload(self,leafOnly=False):
        """
        columnCount() no me funciona correctametne con los nodos hoja, asi que he tenido que 
        escribir esta rutina
        """
        return self.model().lenPayload(leafOnly)
        #lo de abajo es como deberia ser, al tener colTreeIndex puedo escribir la version resumida de arriba
        #indice = self.index() #self.model().indexFromItem(field)
        #cont = 1
        #colind = indice.sibling(indice.row(),cont)
        #while colind.isValid():
            #cont +=1
            #colind = indice.sibling(indice.row(),cont)
        #return cont


    
    def getPayloadItem(self,idx):
        indice = self.index() #self.model().indexFromItem(field
        colind = indice.sibling(indice.row(),idx + 1)
        if colind.isValid():
            return self.model().itemFromIndex(colind).data(Qt.UserRole +1)
        else:
            return None

    def setPayloadItem(self,idx,valor):
        indice = self.index() #self.model().indexFromItem(field
        colind = indice.sibling(indice.row(),idx + 1)
        if colind.isValid():
            item = self.model().itemFromIndex(colind)
            if not isinstance(item,GuideItem):
                colroot = indice.sibling(indice.row(),0)
                ritem = self.model().itemFromIndex(colroot)
                ritem.setColumn(idx +1,valor)
            else:
                item.setData(valor,Qt.UserRole +1)
        else:
            colroot = indice.sibling(indice.row(),0)
            item = self.model().itemFromIndex(colroot)
            item.setColumn(idx +1,valor)
    
    def _getHead(self):
        if self.column() == 0:
            return self
        else:
            indice = self.index() 
            colind = indice.sibling(indice.row(),0)
            return self.model().itemFromIndex(colind)

    def getKey(self):
        return self._getHead().data(Qt.UserRole +1)
    
    def getLabel(self):
        return self._getHead().data(Qt.DisplayRole)


    #
    #  funciones de API general
    #
    def depth(self):
        depth = 0
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            pai = pai.parent()
            depth += 1
        return depth
    
    def getFullKey(self):
        clave = self.data(Qt.UserRole +1)
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            clave = pai.data(Qt.UserRole +1) + DELIMITER + clave
            pai = pai.parent()
        return clave

    def getFullDesc(self):
        if item.column() != 0:
            fuente = self.index().sibling(self.index(),0)
            print(self,self.parent(),fuente)
        else:
            fuente = self
        clave = fuente.data(Qt.DisplayRole)
        pai = fuente.parent()
        while pai is not None and pai != fuente.model().invisibleRootItem():
            clave = pai.data(Qt.UserRole +1) + DELIMITER + clave
            pai = pai.parent()
        return clave
        
    def searchChildren(self,value,role=None):
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        return searchStandardItem(self,value,prole)

    def setColumn(self,col,value):
        row = self.index().row()
        if self.parent() is None:
            pai = self.model().invisibleRootItem()
        else:
            pai = self.parent()
        colItem = GuideItem()
        colItem.setData(value,Qt.UserRole +1)
        pai.setChild(row,col,colItem)
        #colItem.setBackup()
   
    def getColumn(self,col):
        if self.column() != 0:
            return None
        indice = self.index() 
        colind = indice.sibling(indice.row(),col)
        if colind.isValid():
            return self.model().itemFromIndex(colind)
        else:
            return None
        
    def getColumnData(self,idx,role=None):
        """
        VITAL ver que aqui idx no es la columna en el sentido de Qt sino de Payload, es decir desplazado por uno (la columna 0 es la "cabecera"
        """
        indice = self.index() #self.model().indexFromItem(field
        colind = indice.sibling(indice.row(),idx + 1)
        if colind.isValid():
            return self.model().itemFromIndex(colind).data(role if role is not None else Qt.UserRole +1)
        else:
            return None
#
    #  Compatibilidad TreeItem (no todas se incluyen)
    #
    def childCount(self):
        return self.rowCount()
    def getStatistics(self):
        return self._getHead().stats
    def isTotal(self):
        if self.type() == TOTAL:
            return True
        else:
            return False
    def isBranch(self):
        if self.type() == BRANCH:
            return True
        else:
            return False
    def isLeaf(self):
        if self.type() in (QStandardItem.UserType,'LEAF'):
            return True
        else:
            return False

    def restoreBackup(self):
        if self.column() != 0:
            self.setData(self.originalValue,Qt.UserRole +1)
        else:
            indice = self.index()
            k = 1
            colind = indice.sibling(indice.row(),k)
            while colind.isValid():
                item = self.model().itemFromIndex(colind)
                try:
                    item.setData(item.originalValue,Qt.UserRole +1)
                except AttributeError:
                    pass
                k +=1
                colind = indice.sibling(indice.row(),k)

            
    def setBackup(self):
        if self.column() != 0:
            if self.originalValue is None:
                self.originalValue = self.data(Qt.UserRole +1)
        
    def gpi(self,ind):
        return self.getPayloadItem(ind)
    def spi(self,ind,data):
        return self.setPayloadItem(ind,data)
    def setStatistics(self):
        if self.column() == 0:
            stat_dict = stats(self.getPayload())
            self.stats=stat_dict
    def getLevel(self):
        return self.depth()
    def getFullDesc(self):
        if self.column() != 0:
            return None
        valor = []
        valor.insert(0,self.data(Qt.DisplayRole))
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            valor.insert(0,pai.data(Qt.DisplayRole))
            pai = pai.parent()
        return valor

    #def getRoot(self):
        #pass
    def simplify(self):
        npay = list()
        ncab = list()
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            npay.append(value)
            ncab.append(k +1)
        return npay,ncab

    def simplifyHierarchical(self):
        profundidad = self.depth()
        tmppay = list()
        ncab = list()
        kitem = self
        while kitem.parent():
            tmppay.insert(0,kitem.getPayload())
            kitem = kitem.parent()
            
        npay = [list() for k in range(profundidad) ]    
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            for j in range(profundidad):
                npay[j].append(tmppay[j][k])
            ncab.append(k +1)
        return npay,ncab
    
    def __getitem__(self,campo):
        if campo == 'key':
            return self.data(Qt.UserRole +1)
        elif campo == 'value':
            return self.data(Qt.DisplayRole)
        elif isinstance(campo,int):
            return self.getColumnData(int)
        else:
            return None
    
    
if __name__ == '__main__':
     item=TreeItem('alfa')
     #item.setLabel('omega')
     datos = [1,2,3,4,5]
     item.setPayload(datos)
     print(item,item.itemData)
