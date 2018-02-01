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
    """
    __DOES NOT WORK NOW__
    
    Auxiliary function.
    Generator to navigate a tree, but as external function See base at util.treebasic.TreeModel

    * Input parameter
        * __tree__ the tree to be navigated
        * __key__  the key of the element to start reading
        * __mode__ type of navigation. One of (_ROOT, _DEPTH, _BREADTH) =range(3). _DEPTH navigates hierarchicaly, .BREADTH per level. Default _DEPTH

    * returns
        * next item in sequence
        
    __NOTES__
    
    More complex interface to current traverse at GuideItemModel. Should be upgraded to this specs.
    See base at util.treebasic.TreeModel

    """

    return tree.traverse(key,mode,output = _ITEM)


from PyQt5.QtCore import Qt 
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtGui import QColor
from util.numeros import isOutlier,fmtNumber

LEAF,BRANCH,TOTAL = range(1000,1000+3)

def searchStandardItem(item,value,role):
    """
    Auxiliary function.
    Implement a binary search inside a QStandardItemModel.
    Extremely faster than the .find method.
    Only perform the search in one hierarchical level
    currently REQUIRES that the children be ordered by default. As is the case in _danacube_
    Actual binary search code was retrieved from StackOverflow. Sadly i lost the reference
    
    * Input Parameters
        * __item__ (QStandardItem) parent of the level we are searching for
        * __value__ value we are searching for
        * __role__  the __Qt Role__ for the value. (An item can contain different data associated to different roles)
    
    * Returns
        the item which has that _value_ or _None_
     
    * Programming notes.
        Look for GuideModel.searchHierarchy for usage
        
    __TODO__
    Make a variant which do not requires previous order
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
    This class mantains the format definition (for a display or background roles) for the value contents of an item in GuideItemModel (see the .data method)
    
    __NOTES__
    The current implementation is pretty lame, and compatibility forced from previous code, and the parameters needed by __util.numeros.fmtNumber__
    
    ## Properties
    ### __stats__ 
    Boolean. IF the tree will keep statistics for each row
    ### __format __
    A dictionary containing following entries
    * __yellowoutliers__  Boolean. If statistic ooutliers in a row will be backgrounded in yellow. Default True
    * __rednegatives__    Boolean. If negative values will be backgrounded in red- Default True
    * __thousandseparator__ a Char. character for thousands separation. Default "." (spanish style)
    * __decimalmarker__  a Char. decimal character. Default "," (spanish style)
    * __decimalplaces__  number of default decimal places for floating point values. Default 2
    
    ## Methods
    """
    def __init__(self,**opciones):
        """
        * Input parameters.
          A kwparms dict of
            * __stats__  Boolean. IF the tree will keep statistics for each row
            * __format __ A dictionary containing following entries                
                * __yellowoutliers__  Boolean. If statistic outliers in a row will be backgrounded in yellow. Default True
                * __rednegatives__    Boolean. If negative values will be backgrounded in red- Default True
                * __thousandseparator__ a Char. character for thousands separation. Default "." (spanish style)
                * __decimalmarker__  a Char. decimal character. Default "," (spanish style)
                * __decimalplaces__  number of default decimal places for floating point values. Default 2

        """
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
            self.format['decimalplaces'] = 2
            
class GuideItem(QStandardItem):
    """
    ## Attributes

    ### originalValue

    ### stats

    """
    """
    
    ## Methods reimplemented from QStandardItem
    
    """
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        super(GuideItem, self).__init__(*args)
        self.originalValue = self.data(Qt.UserRole +1)
        if self.index().column() == 0:
            self.stats = None
            
    #def setData(self,value,role):
        #super(GuideItem, self).setData(value,role)
        
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

    def __getitem__(self,campo):
        if campo == 'key':
            return self.data(Qt.UserRole +1)
        elif campo == 'value':
            return self.data(Qt.DisplayRole)
        elif isinstance(campo,int):
            return self.getColumnData(int)
        else:
            return None

    """
    
    ## General methods which conform the API for __user functions__
    
    """
    def getPayload(self):
        lista=[]
        indice = self.index() #self.model().indexFromItem(field)
        k = 1
        colind = indice.sibling(indice.row(),k)
        while colind.isValid():
            lista.append(colind.data(Qt.UserRole +1)) #print(colind.data())
            k +=1
            colind = indice.sibling(indice.row(),k)
        return lista
    
    def setPayload(self,lista): 
        indice = self.index() 
        lastLeaf = 0
        for k,valor in enumerate(lista): 
            col = k + 1                
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
        if self.hasChildren() and leafOnly:
            return None
        indice = self.index() #self.model().indexFromItem(field)
        cont = 1
        colind = indice.sibling(indice.row(),cont)
        while colind.isValid():
            cont +=1
            colind = indice.sibling(indice.row(),cont)
        return cont


    
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
    
    def getKey(self):
        return self._getHead().data(Qt.UserRole +1)
    
    def getLabel(self):
        return self._getHead().data(Qt.DisplayRole)


    """
    
    ##  General methods
    
    """
    def depth(self):
        depth = 0
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            pai = pai.parent()
            depth += 1
        return depth
    
    def _getHead(self):
        if self.column() == 0:
            return self
        else:
            indice = self.index() 
            colind = indice.sibling(indice.row(),0)
            return self.model().itemFromIndex(colind)

    def getFullHeadInfo(self,**parms):
        """
        * parms
            * content = ('key','value')
            * format  = ('simple','string','array')
            * delimiter  (only if format == string)
            * sparse = boolean. Default False
        """
        rol = Qt.DisplayRole
        if 'content' in parms and parms['content'] == 'key':
                rol = Qt.UserRole +1
        format = 'single'
        delim = DELIMITER
        if 'format' in parms:
            sparse = parms.get('sparse',False)
            if parms['format'] == 'string':
                format = 'string'
                delim = parms.get('delimiter',delim)
            elif parms['format'] == 'array':
                format = 'array'
            else:
                pass   # revert to single if not specified
            
        # por si no se pide en la columna 0
        item = self._getHead()
        # ahora obtengo los valores cuando no tengo que iterar por la jerarquia
        clave = None
        if format == 'single':
            return item.data(rol)
        elif format == 'string':
            clave = item.data(rol)
            if sparse:
                for k in range(item.depth()):
                    clave = delim + clave
                return clave
        elif format == 'array':
            clave = []
            clave.append(item.data(rol))
            if sparse:
                for k in range(item.depth()):
                    clave.insert(0,'')
                return clave

        pai = item.parent()
        while pai is not None and pai != item.model().invisibleRootItem():
            if format == 'string':
                clave = pai.data(rol) + delim + clave
            elif format == 'array':
                clave.insert(0,pai.data(rol))
            pai = pai.parent()
        return clave
        
    def getFullKey(self):
        return self.getFullHeadInfo(content='key',format='string')

    def getFullDesc(self):
        return self.getFullHeadInfo(content='value',format='array')
        
    def searchChildren(self,value,role=None):
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        return searchStandardItem(self,value,prole)

    def setColumn(self,col,value):
        #colItem = GuideItem()
        #colItem.setData(value,Qt.UserRole +1)
        #self.insertColumn(col,[colItem,])
        row = self.index().row()
        if self.parent() is None:
            pai = self.model().invisibleRootItem()
        else:
            pai = self.parent()
        colItem = GuideItem()
        colItem.setData(value,Qt.UserRole +1)
        pai.setChild(row,col,colItem)
        return self
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
    """
    
    ##  Application specific methods
    
    """
    #def childCount(self):
        #return self.rowCount()
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
        
    def setStatistics(self):
        if self.column() == 0:
            stat_dict = stats(self.getPayload())
            self.stats=stat_dict

    def simplify(self):
        npay = list()
        ncab = list()
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            npay.append(value)
            ncab.append(k)
        return npay,ncab

    def simplifyHierarchical(self):
        profundidad = self.depth()
        tmppay = list()
        ncab = list()
        kitem = self
        while kitem:
            tmppay.insert(0,kitem.getPayload())
            kitem = kitem.parent()
            
        npay = [list() for k in range(profundidad +1) ]  
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            for j in range(profundidad +1):
                npay[j].append(tmppay[j][k])
            ncab.append(k)

        return npay,ncab
    
        
class GuideItemModel(QStandardItemModel):
    """
    __GuideItemModel__ is an extension of Qt's [QStandardItemModel](https://doc.qt.io/qt-5/qstandarditemmodel.html), specially crafted for holding trees with vector like items (defined as GuideItem, see below).
    They also have some attributes and methods specific for the handling of danacube
    
    In danacube the guides of a view (row_hdr_idx, col_hdr_idx) are implemented with this class
    
    ## Implementation details
    
    Of the methods, following are reimplemetation of base methods, and are task tailored
        * __\_\_init\_\___
        * __data__
        
    Those are provided as extensions to the general model I miss
        * __traverse__
        * __numRecords__
        * __lenPayload__
        * __searchHierarchy
        
    The rest is task tailored for danacube, but the __as*__ methods can be used as a frame for less specific work
    
    ## Attributes
    
    
        
    ### datos
    A TreeFormat object. Holds the formating info for the tree. THe name is merely historical
    
    ### name
    Holds the name of the guide on which the tree is based. Is not mandatory

    ### vista
    En que vista se utiliza (activado en core.vista.toNewArray*
    
    ### orthogonal
    Cual es el otro modelo que complementa la vista (activado en core.vista.toNewArray*)
    """
    def __init__(self,parent=None):
        super(GuideItemModel, self).__init__(parent)
        self.name = None
        self.datos = TreeFormat()  #es por compatibilidad, son formatos
        #self.colTreeIndex = None
        self.vista = None
        self.orthogonal = None
        
    def traverse(self,base=None):
        """
        Generator to navigate the tree  

        * Input parameter
            * __base__ initial item to process. default is .invisibleRootItem, but this element is not yielded
        * returns
            * next item in sequence
        
        __TODO__
        
        It would be nice to put it functionally on par to util.treebasic.TreeModel
        """
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
       
    def numRecords(self,type=None):
        """
        Returns the number of items in the tree.
        The standard model _rowCount_ method only gives the number of direct children of the first level
        
        * Input Parameters
            * __type__ integer the type to be searched for (an integer above 1000. See Qt.StandardItem.type())
            
        * returns
        The number of items in the tree
        """
        count = 0
        for item in self.traverse():
            if type is None or type < QStandardItem.UserType:
                count += 1
            elif item.type() == type :
                    count +=1
        return count

    def asDict(self):
        """
        returns a dictionary view of the tree. The purpose is to allow a quasi direct access to the item based on the key values
        
        *Returns
        
        A dictionary whose keys are the fullkeys of the items. The fullkey is a string which concatenates the keys of the tree hierarchy of the item. To each item is attached, as value a dict with following entries
        * __idx__ the ordinal of the item in the tree traversal
        * __objid__ a reference to the item itself
        *
        
        * Implementation notes
        Trees are meant to be navigated via traversal, but are complex to use as direct access (via the key). This function generates a dictionary which can be accessed directly via the key.
        Python didn't allowed a QStandardItem as a dict key, so we had to use the key as index. It is the full hierachical key to ensure unicity
        """
        diccionario = {}
        idx = 0
        for item in self.traverse():
            diccionario[item.getFullKey()]={'idx':idx,'objid':item}
            idx += 1
        return diccionario
    
    def asHdr(self,**parms):
        """
        Returns a list with an element for every item in the tree. Each element contains data which can be used as headers
        
        * Input parms.
        
        A kwparm whith can contain any of the following entries
        * parms used by GuideItem.getFullHeadInfo
            * content = ('key','value'). Default 'value'
            * format  = ('simple','string','array'). Default 'simple'
            * delimiter  (only if format == string). Concatenation delimiter
            * sparse = boolean. Default False
        * specific parms
            * offset. a number of blank elements to precede the list
            * normArray. a number only if format = array, all elements will have at least this length (num of entries)
            
        * returns
        A list with one element for each item in the tree. What is offered in each element varies according to the input parameters:
            * Content
                * if 'key' we return the internal key of the item (the domain's _code_ of the guide).
                * if 'value' its display text (the domain's _desc_ of the guide
            * format  
                * if 'simple' just the value for this entry (production rule in guide)
                * if 'string' the hierarchy of keys concatenated in one string
                * if 'array'  an array with the hierarchy of keys
                
        * Implementation notes
        In danacbue the need for header structures related to the guides has been an usual task. This function is a generic one to generate such headers
        """
        cabecera = []
        for item in self.traverse():
            cabecera.append(item.getFullHeadInfo(**parms))
        
        # para incluir elementos de offset por otras cabeceras
        if 'offset' in parms and parms['offset'] > 0:
            for k in range(parms['offset']):
                cabecera.insert(0,[''] if parms.get('format','simple') == 'array' else '')
        # para que los arrays vuelvan ya con una longitud minima unificada -por definicion dim_x +1 lo malo es que no puedo recuperarlo por defecto
        if parms.get('format','simple') == 'array' and parms.get('normArray',1) > 1:
            for elem in cabecera:
                diff = parms.get('normArray',1) - len(elem)
                if diff > 0:
                    for k in range(diff):
                        elem.append('')
        return cabecera
        
    def asDictFilter(self,filter):
        """
        returns a dictionary view of the tree, but only those items for which the filter applies.
        
        * Input parameter
            * __filter__ a function which returns a boolean and accept a QStandardItem as parameter

        *Returns
        
        A dictionary whose keys are the fullkeys of the items. The fullkey is a string which concatenates the keys of the tree hierarchy of the item. To each item is attached, as value a dict with following entries
        * __idx__ the ordinal of the item in the filtered tree traversal 
        * __objid__ a reference to the item itself
        *
        
        * Implementation notes
        Enhanced version of the _asDict_ method. Allows any filtering 
        """

        diccionario = {}
        idx = 0
        for item in self.traverse():
            if filter(item):
                diccionario[item.getFullKey()]={'idx':idx,'objid':item}
                idx += 1
        return diccionario
    
    def asHdrFilter(self,filter,**parms):
        """
        Returns a list with an element for every item in the tree for which the filter is True. Each element contains data which can be used as headers
        
        * Input parms.
        * __filter__ a function which returns a boolean and accept a QStandardItem as parameter
        * A kwparm whith can contain any of the following entries
            * parms for getFullHeadInfo
                * content = ('key','value')
                * format  = ('simple','string','array')
                * delimiter  (only if format == string)
                * sparse = boolean. Default False
            * specific parms
                * offset. a number
                * normArray. a number only if format = array
        
        * returns
        A list with one element for each item in the filtered tree. What is offered in each element varies according to the input parameters:
            * Content
                * if 'key' we return the internal key of the item (the domain's _code_ of the guide).
                * if 'value' its display text (the domain's _desc_ of the guide
            * format  
                * if 'simple' just the value for this entry (production rule in guide)
                * if 'string' the hierarchy of keys concatenated in one string
                * if 'array'  an array with the hierarchy of keys

        * Implementation notes
        Enhanced version of the _asDict_ method. Allows any filtering 
        """
        cabecera = []
        for item in self.traverse():
            if filter(item):
                cabecera.append(item.getFullHeadInfo(**parms))
        
        # para incluir elementos de offset por otras cabeceras
        if 'offset' in parms and parms['offset'] > 0:
            for k in range(parms['offset']):
                cabecera.insert(0,[''] if parms.get('format','simple') == 'array' else '')
        # para que los arrays vuelvan ya con una longitud minima unificada -por definicion dim_x +1 lo malo es que no puedo recuperarlo por defecto
        if parms.get('format','simple') == 'array' and parms.get('normArray',1) > 1:
            for elem in cabecera:
                diff = parms.get('normArray',1) - len(elem)
                if diff > 0:
                    for k in range(diff):
                        elem.append('')
        return cabecera
    
    def lenPayload(self,leafOnly=False):
        """
        Returns the maximum lenght of the payload for each item. (in fact the length of the orthogonal model)
        QStandardItem.columnCount() give some incorrect results
        
        * Input parameters
            * leafOnly. Boolean. counting is done only for leaf elements
        
        * returns 
            * the number of columns expected
            
        * Programming notes
            Implementation will vary, most probably
        """
        if self.orthogonal is None:
            return 0
        elif not leafOnly:
            return self.orthogonal.numRecords()
        else:
            return self.orthogonal.numRecords(type=LEAF)

    def searchHierarchy(self,valueList,role=None):
        """
          Does a search thru all the hierarchy given the key/value data
        
        * Input parameters
            * __valueList__ an array with the hierachy data to be searched
            * __role__ the Qt.Role the data is associated with
            
        * Returns
            An Item of the tree which mastches the valueList
            
        * Programming notes
            Which data is searched depends on the role. Qt.UserRole +1 searches for internal keys; Qt.DisplayRole for description 
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
        """
        Sets (and evaluate) the per row statistics. While they are per row(item) are calculated once per tree
        
        * Input parameters:
            * __switch__ a Boolean, activates or deactivates the statistics
        
        * returns
            none. If activated loads the items with the corresponding statistics
        """
        
        self.datos.stats = switch
        if self.datos.stats:
            for item in self.traverse():
                item.setStatistics()
        else:
            return None
        
    def data(self,index,role):
        """
        Reimplementation of QStandardItemModel.data for the needs of danacube. It will be invoked when a view associated with the model is redrawn
        
        * Input parameters
            * __index__ a QIndexModel which identifies the item
            * __role__ which Qt.Role are we handling
            
        * Programming notes
        We define special actions for following cases
            * Qt.TextAlignmentRole. For column 0 -the value- left aligned, else -the vector- right aligned (they are numbers)
            * Qt.BackgroundRole. Color if the conditions in TreeFormat are met 
            * Qt.DisplayRole. Formats the numeric vector
        """
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
            if index.column() == 0:
                return datos
            if datos == None:
                return None
            else:
                text, sign = fmtNumber(datos,self.datos.format)
                return '{}{}'.format(sign if sign == '-' else '',text)               
        else:
            return item.data(role)

    
"""
#  MonkeyPatch section
   Definition of synonims of methods of the previous classes, used either for simplicity or compatibility

* GuideItemModel.len = GuideItemModel.numRecords

* GuideItem.childCount = GuideItem.rowCount
* GuideItem.gpi = GuideItem.getPayloadItem
* GuideItem.spi = GuideItem.setPayloadItem
* GuideItem.getLevel = GuideItem.depth
* GuideItem.getHeader = GuideItem.getFullHeadInfo

"""
GuideItemModel.len = GuideItemModel.numRecords
GuideItem.childCount = GuideItem.rowCount
GuideItem.gpi = GuideItem.getPayloadItem
GuideItem.spi = GuideItem.setPayloadItem
GuideItem.getLevel = GuideItem.depth
GuideItem.getHeader = GuideItem.getFullHeadInfo

if __name__ == '__main__':
    pass
