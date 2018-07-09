# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

from support.util.numeros import stats
from support.util.traverse import traverse,traverseBasic

(_ROOT, _DEPTH, _BREADTH) = range(3)
(_KEY,_ITEM) = range(2)

import base.config as config

#def traverse(tree, key=None, mode=1):
    #"""
    #__DOES NOT WORK NOW__
    
    #Auxiliary function.
    #Generator to navigate a tree, but as external function See base at util.treebasic.TreeModel

    #* Input parameter
        #* __tree__ the tree to be navigated
        #* __key__  the key of the element to start reading
        #* __mode__ type of navigation. One of (_ROOT, _DEPTH, _BREADTH) =range(3). _DEPTH navigates hierarchicaly, .BREADTH per level. Default _DEPTH

    #* returns
        #* next item in sequence
        
    #__NOTES__
    
    #More complex interface to current traverse at GuideItemModel. Should be upgraded to this specs.
    #See base at util.treebasic.TreeModel

    #"""
    #if type(tree) == GuideItemModel:
        #if not key:
            #return tree.traverse(tree.invisibleRootItem())
        #else:
            #return tree.traverse(key)
    #elif isinstance(tree,QStandardItemModel):
        #return traverseBasic(tree.invisibleRootItem())
    #else:
        #return tree.traverse(key,mode,output = _ITEM)

#def traverseBasic(root,base=None):
    #if base is not None:
       #yield base
       #queue = [ base.child(i) for i in range(0,base.rowCount()) ]
    #else:
        #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        ##print(queue)
        ##print('')
    #while queue :
        #yield queue[0]
        #expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
        #if expansion is None:
            #del queue[0]
        #else:
            #queue = expansion  + queue[1:]  
from PyQt5.QtCore import Qt,QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from PyQt5.QtGui import QColor
from support.util.numeros import isOutlier,fmtNumber,s2n

LEAF,BRANCH,TOTAL = range(1000,1000+3)

def searchTree(item,value,role):
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
        
    """
    lower = 0
    upper = item.rowCount()
    while lower < upper:   # use < instead of <=
        x = lower + (upper - lower) // 2
        val = item.child(x).data(role)
        #normalizo al tipo interno para evitar que se me escapen elementos 
        if type(val) == int:
            value = int(value)
        elif type(val) == float:
            value = float(value)
        elif type(val) == str:
            value = str(value)
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
            print(value,item.data(role),item.rowCount(),'castañazo')
            raise
    return None

def getBinPos(item,value,role):
    """
    Auxiliary function.
    Implement a binary search inside a QStandardItemModel to locate where an element should be placed
    Only perform the search in one hierarchical level
    currently REQUIRES that the children be ordered by default. As is the case in _danacube_
    
    * Input Parameters
        * __item__ (QStandardItem) parent of the level we are searching for
        * __value__ value we are searching for
        * __role__  the __Qt Role__ for the value. (An item can contain different data associated to different roles)
    
    * Returns
        the nur which has that _value_ or _None_
     
    * Programming notes.
        Look for GuideModel.searchHierarchy for usage
    """
    def _cmp(external,internal):
        if isinstance(internal,int):
            external = int(external)
        elif isinstance(internal,float):
            external = float(external)
        elif isinstance(internal,str):
            external = str(external)
            
        if external == internal:
            return '='
        elif external > internal:
            return '>'
        elif external < internal:
            return '<'
        else:
            return 'U' #undefined
        
    lower = 0
    upper = item.rowCount()
    if item.rowCount() > 0:
        lowval = item.child(lower).data(role)
        uppval  = item.child(upper -1).data(role)
        if _cmp(value,lowval) == '<':
            return 0
        elif _cmp(value,uppval) == '>':
            return None
    else:
        return None
    
    while lower < upper:   # use < instead of <=
        x = lower + (upper - lower) // 2
        val = item.child(x).data(role)
        #normalizo al tipo interno para evitar que se me escapen elementos 
        cmp = _cmp(value,val)
        if cmp == '=':
            return x #implica que admite duplicados por defincion
        elif cmp == '<':
            upper = x
        elif cmp == '>':
            if lower == x:
                return x +1
            lower = x
    return None

def modelSearch(item,value,role):
    """
    Auxiliary function.
    Implement a search inside a QStandardItemModel using QAbstractItemModel.match
    Performancewise is a bad choice (might be 15 times slower than the preceding one in a 1000 row case)
    """
    if role is None:
        prole = Qt.UserRole +1
    else:
        prole = role
    model = item.model()
    start = model.index(0,0,item.index() if item.index().isValid() else QModelIndex())
    result = model.match(start,prole,value,1,Qt.MatchExactly)
    if not result:
        return None
    return model.itemFromIndex(result[0])

def lineSearch(item,value,role):
    """
    Auxiliary function.
    Implement a search inside a QStandardItemModel navigating the tree
    Performancewise is a bad choice (might be 10 times slower than the binary search one in a 1000 row case)
    """
    if role is None:
        prole = Qt.UserRole +1
    else:
        prole = role
    for k in range(item.rowCount()):
        if item.child(k,0).data(prole) == value:
            return item.child(k,0)
    return None
    
#def searchTree(item,value,role):
    #"""
    #selector.  
        #For an special bad case case (1000 rows, no hierarchy)
        #binary search performance is about 15 times better than model search and about 10 times better than lineal seach
    #"""
    ##return binarySearch(item,value,role)
    ##return modelSearch(item,value,role)
    #return lineSearch(item,value,role)

def searchHierarchy(model,valueList,role=None):
    """
        Does a search thru all the hierarchy given the key/value data. 
        As 1st level function to be able to use in QStandardItemModels
        Uses searchStandardItem 
    
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
    elem = model.invisibleRootItem()
    parent = model.invisibleRootItem()
    for k,value in enumerate(valueList):
        elem = searchTree(parent,value,prole)
        if not elem:
            return None
        parent = elem
    return elem


def _getHeadColumn(item):
    """
    __NEW API__
    
    for a given row, returns the current row header (i.e. the sibling which has column 0)
    as function not as method
    * returns
    the item with column 0 from the current row
    
    """
    if item.column() == 0:
        return item
    else:
        ref = item.data(REF)
        if ref:
            return ref[0]
        else:
            indice = item.index() 
            colind = indice.sibling(indice.row(),0)
            return item.model().itemFromIndex(colind)
    
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

(SHOW,KEY,REF,ORIG) = (Qt.DisplayRole,Qt.UserRole +1,Qt.UserRole +2, Qt.UserRole +3)

class ListWrapper():
    """
    __NEW API__
    """
    def __init__(self,val):
        self.val = val
        
    def __setitem__(self,idx,value):
        if idx < len(self.val):
            self.val[idx] = value
    
    def __getitem__(self,idx):
        if idx < len(self.val):
            return self.val[idx]
        else:
            return None
    
    def __repr__(self):
        cadena = ' '
        for i in range(len(self.val)):
            cadena += '{}, '.format(self.val[i])
        
        return '[{}]'.format(cadena)

    def __str__(self):
        return self.__repr__()
    
class NewGuideItem(QStandardItem):
    """
    __NEW API__
    
    """
    valpos=2

    def __init__(self,*args,**kwargs):
        """
        todo añadir parent
        """
        key = None
        value = None
        if len(args) >= 2:
            key = args[0]
            value = args[1]
        elif len(args) ==1:
            key =args[0]
            
        super().__init__()
        if key:
            if isinstance(key,(list,tuple)):
                self.reference = ListWrapper(key)
                self.setData(self.reference,Qt.UserRole +2)
            else:
                self.setData(key,Qt.UserRole + 1)
        if value:
            self.setData(value,Qt.DisplayRole)


    def setData(self,value,role):
        if role in (KEY,):
            coredata = self.data(REF)
            if coredata is None:
                super().setData(value,role)
            else:
                coredata[NewGuideItem.valpos]=value
        else:
            return super().setData(value,role)
        #print(self.data(REF),self.data(INT),self.data(SHOW))
        
    def data(self,role):
        #if role == SHOW:              #presumiblemente innecesaria
            #if super().data(role) is None:
                #return self.data(INT)
            #else:
                #return super().data(role)
        if role == KEY:
            if super().data(role) is None and super().data(REF):
                return self.data(REF)[NewGuideItem.valpos]
            else:
                return super().data(role)
        else:
            return super().data(role)
        
    def __getitem__(self,campo):
        """
        ___NEW API__
        
        We define three types of fields
        * __'key'__  the UsdrRole content
        * __'value'__ the DisplaRole content
        * a number: the playload column
        
        """
        if campo == 'key':
            return self.data(Qt.UserRole +1)
        elif campo == 'value':
            return self.data(Qt.DisplayRole)
        else:
            return None        
            
class GuideItem(NewGuideItem):
    """
    
    This class is an specialization of [QStandardItem](http://doc.qt.io/qt-5/qstandarditem.html) for use with __GuideItemModel__ 
    
    We have developed it to be the model for [QTableViews](http://doc.qt.io/qt-5/qtableview.html), when we want to manipulate two-dimensional arrays, and the rows are suposed to be linked in a hierarchical tree, thus

    o ------> row 
          |-> row 
               |
               |--> row 
               |--> row 
    
    row is  
        row head + payload  (the equivalent of ) row head + data col1 + data col2 + .... ) 
        
    In our current implementation _GuideItem_ instantiates every element of the row.
    
    Column 0 of each row is the row header and has two data inside it:
        * the internal __key__ accessed via the Qt.Role (Qt.QUserRole +1) and
        * an human readable _value_. Accessd via the Qt.Role Qt.QDisplayRole
        
    When we navigate the tree we access for each row the row header.
    
    The other columns of the row is what we call _payload_, and can be accessed thru the header individually or as a block
    
    
    ## Attributes

    both are given value during the application workflow
    
    ### originalValue
        A value for the item which to return 
    ### stats
        a dict with following entries (excluidn null values)
            * __avg__  average
            * __std__  standard deviation
            * __max__  max value
            * __median__ median value
            * __min__  minimum value
            * __out_low__  upper threshold for low outliers
            * __out_hig__  lower threshold for upper outliers

    """
    """
    
    ## Methods reimplemented from [QStandardItem](http://doc.qt.io/qt-5/qstandarditem.html). See documentation there.
    up to NEW API
    """
    coordinates = (0,1)
    
    def __init__(self,*args,**kwargs):  #
        super(GuideItem, self).__init__(*args,**kwargs)
        self.originalValue = self.data(Qt.UserRole +1)
        if self.index().column() == 0:
            self.stats = None
            
    #def setData(self,value,role):
        #super(GuideItem, self).setData(value,role)
        
    def type(self):
        """ 
            We define three different types of items (really of the rows)
            TOTAL which correspond to the grand total
            BRANCH rows which have children 
            LEAF   rows without children

        """
        if self.data(Qt.UserRole +1) == '//':
            return TOTAL
        elif self.hasChildren():
            return BRANCH
        else:
            return LEAF
        
    def data(self,role):
        """
        We make Qt.UserRole +1 as default role if Qt.DisplayRole returns None
        
        """
        valor = super(GuideItem, self).data(role)
        if role in (Qt.DisplayRole, ) and valor is None:
            valor = super(GuideItem,self).data(Qt.UserRole +1)
        return valor
    
    def __str__(self):
        return "<" + str(self.data(Qt.DisplayRole)) + ">"

    def __repr__(self):
        return "<" + str(self.data(Qt.UserRole +1)) + ">"
    
    def clone(self):
        """
        __NEW API__
        uso super().data para evitar que se cuelen display data que no son
        """
        if self.data(REF):
            nitem = GuideItem(self.data(REF),super().data(SHOW))
        else:
            nitem = GuideItem(self.data(KEY),super().data(SHOW))
        return nitem

    def __getitem__(self,campo):
        """
        ___NEW API__
        
        We define three types of fields
        * __'key'__  the UsdrRole content
        * __'value'__ the DisplaRole content
        * a number: the playload column
        
        """
        
        if not self.model():
            (row_axis,col_axis) = GuideItem.coordinates
        else:
            (row_axis,col_axis) = self.model().coordinates
        if campo == 'rowid':
            tmp = self.data(REF)
            if tmp:
                return tmp[row_axis]
            else:
                if self.model():
                    return _getHeadColumn(self)
                else:
                    return None
        elif campo == 'colid':
            tmp = self.data(REF)
            if tmp:
                return tmp[col_axis]
            else:
                if self.model() and self.model().orthogonal:
                    return self.model().orthogonal.pos2item(self.column()-1)  #la columna 0 es el item cabecera
                else:
                    return None
        elif campo == 'rownr':
            if self.column() == 0:
                if self.model():
                    return self.model().item2pos(self)
                else:
                    return 0
            else:
                return _getHeadColumn(self)['rownr']
        elif campo == 'colnr':
            return self.column()
        elif isinstance(campo,int):
            return self.getColumnData(campo +1)
        else:
            return super().__getitem__(campo)

    """
    
    ##  General methods QStandardItem should have
    
    """
    def depth(self):
        """
        hierachical level of the row
        
        * returns
        An integer with the current level, starting from 0
        """
        # depth is evaluated backwards, from the actual item up to the root item
        depth = 0
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            pai = pai.parent()
            depth += 1
        return depth
    
    def getHead(self):
        """
        TODO document now as a public method
        for a given row, returns the current row header (i.e. the sibling which has column 0)
        
        * returns
        the item with column 0 from the current row
        """
        return _getHeadColumn(self)
        
    def searchChildren(self,value,role=None):
        """
        We seach for a specific value inside the children of the current row
        
        * Input parameters
            * __value__ the value to be searched for. Type be QStandardItem.setData compatible
            * __role__ Qt.Role, if not specified Qt.UserRole +1
        * Returns
        An item which contains this value or None
        
        * Implementation notes
        Wide faster and hierachical level specific than model().find
        Currently the values of the rows have to be sorted in advance
        """
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        return searchTree(self,value,prole)

   
    def getColumn(self,col):
        """
        Returns the item at column _col_ for the current row_hdr_idx
        
        * Input parameters
            * __col__ the index of the column requested. 0 is not allowed
        
        * Returns
        The item at that column or None if it doesn't exist
        
        * Implementation notes
        Surprisingly such a method does not exist at QStandardItem
        """
        if self.column() != 0:
            return None
        indice = self.index() 
        colind = indice.sibling(indice.row(),col)
        if colind.isValid():
            return self.model().itemFromIndex(colind)
        else:
            return None
        
    def setColumn(self,col,value,role=Qt.UserRole +1):
        """
        __CONVERT__ __NEW API__
        Method to set , for the current row, a payload entry at position _col_ with value _value_ .
        It's a destructive function: if the column already exist is replaced with the new version
        Can only be executed on GuideItems with column 0 (the head of the row)
        
        * Input parameters
            * __col__ the index of the column to be set. 0 is not allowed
            * __value__ the value to be inserted. Type be QStandardItem.setData compatible
            * __role__ Qt.Role, if not specified Qt.UserRole +1
            
        * returns
            a reference to the new column item or None (if 0 happens to be specified at _col_)
            
        * Implementation notes.
            QtStandardItem.insertColumn and QStandardItem.insertColumns are most probably faulty, and the need to create a list of QStandardItem (or derived) before using QStandardItem.insertColumns is unconfortable to program. 
            Column 0 is not allowed because (as it is the head of the row,i.e. _self_) it would destroy _self_
        """
        if col == 0:
            return None
        elif self.column() != 0:
            return None
    
        orig = self.getColumn(col)
        
        if not orig or orig.data(REF) is None:
            # creamos una nueva entrada en el array
            colItem = self.model().orthogonal.pos2item(col -1)
            #print(col,colItem,colItem['key'],colItem['value'])
            if role == REF:
                newtuple = value
            elif not role or role == KEY:
                newtuple = [self,colItem,value]
            else:
                newtuple = [self,colItem,None]
            self.model().vista.array.append(newtuple)
            # actualizamos el arbol de fila
            tree = self.model()
            pai = self.parent() if self.parent() else self.model().invisibleRootItem()
            row = self.row()
            nrItem = GuideItem(value)
            pai.setChild(row,col,nrItem)
            if self.model().orthogonal:
            #actualizamos el arbol de columnas
                tree = self.model().orthogonal
                pai = colItem.parent() if colItem.parent() else colItem.model().invisibleRootItem()
                row = colItem.row()
                col = self.model().item2pos(self) +1
                ncItem = GuideItem(value)
                pai.setChild(row,col,ncItem)
                #pongo los datos
            if role and role != KEY:
                nrItem.setData(value,role)
            return nrItem
        else:
            orig.setData(value,role)
            return orig
    
        """
        # with insertColumns, which does not work again
        colItem = GuideItem()
        self.insertColumns(col,1,(colItem,))
        return colItem
        #
        # this is the code needed if insertColumns should behave badly
        row = self.index().row()
        if self.parent() is None:
            pai = self.model().invisibleRootItem()
        else:
            pai = self.parent()
        colItem = GuideItem()
        if role is None:
            colItem.setData(value,Qt.UserRole +1)
        else:
            colItem.setData(value,role)
        pai.setChild(row,col,colItem)
        return colItem
        """
    def setUpdateColumn(self,col,value,role=None):
        """
        Method to set , for the current row, a payload entry at position _col_ with value _value_ .
        If the item already exist it is updated, else is created
        Can only be executed on GuideItems with column 0 (the head of the row)
        
        * Input parameters
            * __col__ the index of the column to be set. 0 is not allowed
            * __value__ the value to be inserted. Type be QStandardItem.setData compatible
            * __role__ Qt.Role, if not specified Qt.UserRole +1
            
        * returns
            a reference to the new column item or None (if 0 happens to be specified at _col_)
            
        """
        if col == 0:
            return None
        elif self.column() != 0:
            return None
        
        columna = self.getColumn(col)
        if columna is None or type(columna) == QStandardItem or columna.data(REF) is None:
            columna = self.setColumn(col,value,role)
        else:
            if role is None:
                columna.setData(value,Qt.UserRole +1)
            else:
                columna.setData(value,role)
     
        return columna   
     
    def rowTraverse(self):
        """
        __EXPERIMENTAL__
        generator navigate the payload elements inside a row after the current one
        
        Implementation note:
            If the corresponding column is still not defined it returns a QStandardItem, not a real column
        If we use expanded functionality of the class we must code like
        ```
            for item in self.rowTraverse():
                if type(item) == QStandardItem:
                    pass
                else:
                    ...
        ```
        """
        indice = self.index() 
        k = indice.column() + 1
        colind = indice.sibling(indice.row(),k)
        while colind.isValid():
            yield self.model().itemFromIndex(colind)
            k +=1
            colind = indice.sibling(indice.row(),k)

    """
    
    ## General methods which make up the API for __user functions__
    
    """
    def getPayload(self):
        """
        Returns a list with the values of the payload (columns 1 .. of the current row
        """
        return [ item.data(Qt.UserRole +1) for item in self.rowTraverse() ]
    
    def setPayload(self,lista): 
        """
        Updates in one step all the values of the payload.
        If len(lista) < len(vector) only those values get updated; otherwise the vector will be expanded as apropiate
        
        * Input parameters
             __lista__ a list with the new values for the vector 
        """
        indice = self.index() 
        lastLeaf = 0
        for idx,valor in enumerate(lista): 
            col = idx + 1                
            self.setUpdateColumn(col,valor)

    def lenPayload(self):
        """
        Length of the payload for this __numRecords__
        
        * Returns
        Length of the payload
        
        * implementation notes
        QStandardItem.columnCount() does not seem to work, it should be lenPayload = columnCount -1.
        In this case the use of the generator seems not that performant
        """
        #if self.hasChildren():
            #return 0
        indice = self.index() #self.model().indexFromItem(field)
        idx = 0
        colind = indice.sibling(indice.row(),idx +1)
        while colind.isValid():
            idx +=1
            colind = indice.sibling(indice.row(),idx +1)
        return idx

    def getPayloadFiltered(self,filtro):
        """
        TODO add to doc
        Funcion que retorna el payload (ver getPayload) pero solo de aquellas columnas incluidas en el filtro
        
        * Input Parameter
            * __filtro__ una lista con los indices -de payload- que queremos recuperar
        
        * Notas: Para generar el filtro lo mas comodo es 

        ```
        prefilter =  tree.orthogonal.asDictFilter(lambda x:x.type() == LEAF)
        filtro = sorted( [ prefilter[entry]['oidx'] for entry in prefilter ])
        ```
        """
        base = self.getPayload()
        resultado = []
        if len(base) == len(filtro):
            return base
        else:
            for i in filtro:
                if i >= len(base):
                    break
                resultado.append(base[i])
            return resultado

    def setPayloadFiltered(self,datos,filtro):
        """
        TODO add to doc
        Funcion que carga el payload (ver setPayload) pero solo de aquellas columnas incluidas en el filtro
        
        * Input Parameter
            * __datos__  la lista de valores que corresponden a cada uno de los elementos del filtro
            * __filtro__ una lista con los indices -de payload- que queremos grabar
        
        * Notas
        len(Datos) = len(filtro)
            
        """
        for k,i in enumerate(filtro):
            self.setPayloadItem(i,datos[k])
    
    def getPayloadItem(self,idx):
        """
        Returns the data at payload position _idx_ for the current row
        It corresponds to column idx + 1
        
        * Input parameters
            * __idx__ the index inside the payload.
        
        * Returns
        The item at that column or None if it doesn't exist
        
        
        """
        column = self.getColumn(idx +1)
        if column:
            return self.getColumn(idx +1).data(Qt.UserRole +1)
        else:
            return None
    
    def setPayloadItem(self,idx,valor):
        """
         Method to set , for the current row, a payload column at index _idx_ with value _value_ .
        If the item already exist it is updated, else is created
        It will correspond to column = idx +1
        
        * Input parameters
            * __idx__ the index of the payload to be set. 
            * __value__ the value to be inserted. 
            
        * returns
            a reference to the new column item or None 
       """
        return self.setUpdateColumn(idx +1,valor)
    
    def getKey(self):
        """
        
        returns the internal key of the current row 
        
        """
        return self.getHead().data(Qt.UserRole +1)
    
    def getLabel(self):
        """
        
        returns the display value for the current row 
        
        """

        return self.getHead().data(Qt.DisplayRole)

        
    """
    
    ##  Application specific methods
    
    """

    def getColumnData(self,idx,role=None):
        """
        Returns data from an specified index and role inside the payload.
        
        * Input parameter
            * __idx__ the index in the payload 
            * __role__ data associated to that role. Default is Qt.UserRole +1
            
        * Implementation notes
            For compatibility with other tree implementations
        """
        item = self.getColumn(idx +1)
        if item is not None:
            return item.data(role if role is not None else Qt.UserRole +1)
        else:
            return None

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
        delim = config.DELIMITER
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
        item = self.getHead()
        # ahora obtengo los valores cuando no tengo que iterar por la jerarquia
        clave = None
        if format == 'single':
            return item.data(rol)
        elif format == 'string':
            clave = str(item.data(rol))
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
                clave = str(pai.data(rol)) + delim + clave
            elif format == 'array':
                clave.insert(0,pai.data(rol))
            pai = pai.parent()
        return clave

    def getFullKey(self):
        """

        obtains the key of the row in string format (i.e each hierachical step separated by config.DELIMITER ).
        Key is the DB internal key and Qt.UserRole + 1 data
        
        """
        return self.getFullHeadInfo(content='key',format='string')

    def getFullDesc(self):
        """

        obtains the description of the row in array format (i.e each hierachical step in an occurrence of a list ).
        Description is the presentation values of the keys and Qt.DisplayRole data
        
        """
        return self.getFullHeadInfo(content='value',format='array')

    def getStatistics(self):
        """
        
        returns the statistics gathered for this row 
        
        """
        return self.getHead().stats
    
    def isTotal(self):
        """
        
        Boolean to check if the row is a totalizer row
        
        """
        if self.type() == TOTAL:
            return True
        else:
            return False
        
    def isBranch(self):
        """
        
        Boolean to check if the row is a branch row (has children of its own)
        
        """
        if self.type() == BRANCH:
            return True
        else:
            return False
    def isLeaf(self):
        """
        
        Boolean to check if the row is a leaf row (has no children of its own)
        
        """
        if self.type() in (QStandardItem.UserType,'LEAF'):
            return True
        else:
            return False

    def restoreBackup(self):
        """
        
        Returns the payload item to the original value
        If executed at the header restores the full row
        
        """
        if self.column() != 0:
            self.setData(None,Qt.DisplayRole)
            self.setData(self.originalValue,Qt.UserRole +1)
        else:
            for item in self.rowTraverse():
                if type(item) == QStandardItem:
                    pass
                else:
                    item.setData(None,Qt.DisplayRole)
                    item.setData(item.originalValue,Qt.UserRole +1)
            
    def setBackup(self):
        """
        
        Sets the current value as  backup value (self.originalValue) for a payload column
        If executed at the header restores the full row
        
        For orthogonality sake we allow to process the full row if executed at the header
        
        """
        if self.column() != 0:
            if self.originalValue is None:
                self.originalValue = self.data(Qt.UserRole +1)
        else:
            for item in self.rowTraverse():
                if type(item) == QStandardItem:
                    pass
                else:
                    if self.originalValue is None:
                        self.originalValue = self.data(Qt.UserRole +1)
        
    def setStatistics(self):
        """
        
        Executes the statistic gathering routine at the row 
        Only executable at the row header
        
        The statistics routine is util.numeros.stats and creates a dict with following entries (excluidn null values)
            * __avg__  average
            * __std__  standard deviation
            * __max__  max value
            * __median__ median value
            * __min__  minimum value
            * __out_low__  upper threshold for low outliers
            * __out_hig__  lower threshold for upper outliers
            

        """
        if self.column() == 0:
            stat_dict = stats(self.getPayload())
            self.stats=stat_dict

    def simplify(self):
        """
        We get the value of the elements in the payload which are not Null (None)
        Only to be executed at the head
        * return
            * A list with the values of the non null payload
            * A list with the indexes of those elements
        
        """
        if self.column() != 0:
            return None,None
        npay = list()
        ncab = list()
        for k,value in enumerate(self.getPayload()):
            if not value:
                continue
            npay.append(value)
            ncab.append(k)
        return npay,ncab

    def simplifyHierarchical(self):
        """
        We get the value of the elements in the payload at this level and its parents. Only return those which are not Null at this level
        Only to be executed at the head
        
        * return
            * A list for each hiearchical level of lists of values of the non null payload
            * A list with the indexes of those elements
        
        """
        if self.column() != 0:
            return None,None

        profundidad = self.depth()
        tmppay = list()
        ncab = list()
        npay = list()
        
        tmppay,ncab = self.simplify()
        npay.append(tmppay[:])
        kitem = self.parent()
        while kitem:
            tmppay = kitem.getPayload()
            npay.insert(0,[ tmppay[i] for i in ncab ])
            kitem = kitem.parent()

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
        self.coordinates = GuideItem.coordinates
        
    def traverse(self,base=None):
        return traverse(self,base)
        #"""
        #Generator to navigate the tree. It only reads the head items of each rows

        #* Input parameter
            #* __base__ initial item to process. default is .invisibleRootItem, but this element is not yielded
        #* returns
            #* next item in sequence
        
        #__TODO__
        
        #It would be nice to put it functionally on par to util.treebasic.TreeModel
        #"""
        #if base is not None:
            #yield base
            #queue = [ base.child(i) for i in range(0,base.rowCount()) ]
        #else:
            #root = self.invisibleRootItem()
            #queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #while queue :
            #yield queue[0]
            #expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
            #if expansion is None:
                #del queue[0]
            #else:
                #queue = expansion  + queue[1:]            
       
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
        * __oidx__ the original index without filter
        
        * Implementation notes
        Enhanced version of the _asDict_ method. Allows any filtering 
        """

        diccionario = {}
        oidx= idx = 0
        for item in self.traverse():
            if filter(item):
                diccionario[item.getFullKey()]={'idx':idx,'objid':item,'oidx':oidx}
                idx += 1
            oidx +=1
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

    def clearData(self):
        """
        TODO insert in documentation
        Function to clear all payload in the tree. This explicit navigation is the only way I found to reset col.originalValue
        """
        #payloadLen = self.lenPayload()
        for elem in self.traverse():
            papi = elem.parent() if elem.parent() else self.invisibleRootItem()
            columnas = elem.lenPayload()
            for ind in range(columnas):
                papi.setChild(elem.row(),ind +1,None)
            #for col in elem.rowTraverse():
                #col.setData(None,REF)
                #col.setData(None,KEY)
                #col.setData(None,SHOW)
                #col.originalValue = None

    def cloneSubTree(self,entryPoint=None,filter=None,payload=False):
        """
        TODO add to doc
        Generate a new tree from entryPoint and its children
        
        * Input parms
            *
            * __entryPoint__ a GuideItem as hierachical head of what to export
            * __filter__ a function which does some filtering at the tree (default is no filter)
            * __payload__ boolean. If True copies the payload
            
        * returns
            a tree
        
        """
        newTree = GuideItemModel()
        for item in self.traverse(entryPoint):
            if filter and not filter(item):
                continue
            papi = item.parent()
            npapi = None
            if papi:
                ref = papi.getFullHeadInfo(content='key',format='array')
                while len(ref) > 0:
                    npapi = newTree.searchHierarchy(ref)
                    if npapi:
                        break
                    else:
                        ref.remove(ref[0])
            if not npapi:  
                npapi = newTree.invisibleRootItem()
            nitem = item.clone()
            npapi.appendRow((nitem,))
            # aqui pues setPayload verifca la columna y solo tiene valor si item en arbol
            if payload:
                pl=item.getPayload()
                nitem.setPayload(pl)
        return newTree 
    
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
            elem = searchTree(parent,value,prole)
            if not elem:
                return None
            parent = elem
        return elem

    def item2pos(self,pitem):
        """
        dado el item obtengo su posicion relativa en la navegacion de arbol
        FIXME no performance oriented  (Cost O(N))
        
        """
        idx = 0
        for item in self.traverse():
            if item is pitem:
                return idx
            idx +=1
        return None
    
    def pos2item(self,pord):
        """
        dada la posicion obtengo el item 
        FIXME no performance oriented
        """
        if pord < 0:
            return None
        idx = 0
        for item in self.traverse():
            if idx == pord:
                return item
            idx +=1
        return None
    
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
            retorno = item.data(role)
            if type(item) == QStandardItem:
                tipoCabecera = _getHeadColumn(item).type()
            else:
                tipoCabecera = item.getHead().type()
            #TODO TOTAL COLOR begin
            if tipoCabecera == TOTAL:
                retorno = QColor(Qt.gray)
            if tipoCabecera == BRANCH:
                retorno =  QColor(Qt.lightGray)
            #TOTAL COLOR end
            if item.data(Qt.DisplayRole) is None:
                return retorno
            elif index.column() != 0:
                datos = item.data(Qt.DisplayRole)
                if datos is None or datos == '':
                    return  retorno
                datos = float(datos)
                if self.datos.format['yellowoutliers'] and self.datos.stats:
                    if isOutlier(datos,item.getStatistics()):
                        retorno =  QColor(Qt.yellow)
                if self.datos.format['rednegatives'] and datos < 0 :
                    retorno = QColor(Qt.red)
            return retorno   
         
        elif role == Qt.DisplayRole:
            datos = item.data(role)
            if index.column() == 0:
                return datos
            if datos == None or datos == '':
                return None
            datos = s2n(datos)
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
