 
### traverse(tree, key=None, mode=1):
 

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

 
### searchStandardItem(item,value,role):
 

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
 
# class TreeFormat(object):
 

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
 
### __init__(self,**opciones):
 

* Input parameters.
  A kwparms dict of
    * __stats__  Boolean. IF the tree will keep statistics for each row
    * __format __ A dictionary containing following entries                
        * __yellowoutliers__  Boolean. If statistic outliers in a row will be backgrounded in yellow. Default True
        * __rednegatives__    Boolean. If negative values will be backgrounded in red- Default True
        * __thousandseparator__ a Char. character for thousands separation. Default "." (spanish style)
        * __decimalmarker__  a Char. decimal character. Default "," (spanish style)
        * __decimalplaces__  number of default decimal places for floating point values. Default 2

 
# class GuideItemModel(QStandardItemModel):
 

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
    * __searchHierarchy__
    
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

### __init__(self,parent=None):
 
 
### traverse(self,base=None):
 

Generator to navigate the tree  

* Input parameter
    * __base__ initial item to process. default is .invisibleRootItem, but this element is not yielded
* returns
    * next item in sequence

__TODO__

It would be nice to put it functionally on par to util.treebasic.TreeModel
 
### numRecords(self,type=None):

Returns the number of items in the tree. The type parameter allows filtering of an item subtype
The standard model _rowCount_ method only gives the number of direct children of the first level. 

* Input Parameters
    * __type__ integer. the type of the item to be searched for (an integer above 1000. See Qt.StandardItem.UserType
    
* returns
The number of items in the tree
 

### asDict(self):
 

returns a dictionary view of the tree. The purpose is to allow a quasi direct access to the item based on the key values

* Returns
A dictionary whose keys are the fullkeys of the items. The fullkey is a string which concatenates the keys of the tree hierarchy of the item. To each item is attached, as value a dict with following entries

    * __idx__ the ordinal of the item in the tree traversal
    * __objid__ a reference to the item itself
    *

* Implementation notes
Trees are meant to be navigated via traversal, but are complex to use as direct access (via the key). This function generates a dictionary which can be accessed directly via the key.
Python didn't allowed a QStandardItem as a dict key, so we had to use the key as index. It is the full hierachical key to ensure unicity
 

### asHdr(self,**parms):
 

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
 

### asDictFilter(self,filter):
 

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
 

### asHdrFilter(self,filter,**parms):
 

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
 

### def lenPayload(self,leafOnly=False):

Returns the maximum lenght of the payload for each item. (in fact the length of the orthogonal model)
QStandardItem.columnCount() give some incorrect results

* Input parameters
    * leafOnly. Boolean. counting is done only for leaf elements

* returns 
    * the number of columns expected
    
* Programming notes
    Implementation will vary, most probably

### searchHierarchy(self,valueList,role=None):
 
    Does a search thru all the hierarchy given the key/value data

* Input parameters
    * __valueList__ an array with the hierachy data to be searched
    * __role__ the Qt.Role the data is associated with
    
* Returns
    An Item of the tree which mastches the valueList
    
* Programming notes
    Which data is searched depends on the role. Qt.UserRole +1 searches for internal keys; Qt.DisplayRole for description 

    
### setStats(self,switch):

Sets (and evaluate) the per row statistics. While they are per row(item) are calculated once per tree

* Input parameters:
    * __switch__ a Boolean, activates or deactivates the statistics

* returns
    none. If activated loads the items with the corresponding statistics
 

### data(self,index,role):

Reimplementation of QStandardItemModel.data for the needs of danacube. It will be invoked when a view associated with the model is redrawn

* Input parameters
    * __index__ a QIndexModel which identifies the item
    * __role__ which Qt.Role are we handling
    
* Programming notes
We define special actions for following cases
    * Qt.TextAlignmentRole. For column 0 -the value- left aligned, else -the vector- right aligned (they are numbers)
    * Qt.BackgroundRole. Color if the conditions in TreeFormat are met 
    * Qt.DisplayRole. Formats the numeric vector 
 

# class GuideItem(QStandardItem):
 

## Attributes

### originalValue

### stats

 
### __init__(self,*args):  #solo usamos valor (str o standarItem)
 
 
### setData(self,value,role):
 
 
### type(self):
 
 
### data(self,role):
 
 
### __str__(self):
 
 
### __repr__(self):
 
 
### getPayload(self,leafOnly=False):
 
 
### setPayload(self,lista,leafOnly=False):
 
 
### lenPayload(self,leafOnly=False):
 

columnCount() no me funciona correctametne con los nodos hoja, asi que he tenido que 
escribir esta rutina
 
### getPayloadItem(self,idx):
 
 
### setPayloadItem(self,idx,valor):
 
 
### _getHead(self):
 
 
### getKey(self):
 
 
### getLabel(self):
 
 
### depth(self):
 
 
### getFullHeadInfo(self,**parms):
 

* parms
    * content = ('key','value')
    * format  = ('simple','string','array')
    * delimiter  (only if format == string)
    * sparse = boolean. Default False
 
### getFullKey(self):
 
 
### getFullDesc(self):
 
 
### searchChildren(self,value,role=None):
 
 
### setColumn(self,col,value):
 
 
### getColumn(self,col):
 
 
### getColumnData(self,idx,role=None):
 

VITAL ver que aqui idx no es la columna en el sentido de Qt sino de Payload, es decir desplazado por uno (la columna 0 es la "cabecera"
 
### childCount(self):
 
 
### getStatistics(self):
 
 
### isTotal(self):
 
 
### isBranch(self):
 
 
### isLeaf(self):
 
 
### restoreBackup(self):
 
 
### setBackup(self):
 
 
### gpi(self,ind):
 
 
### spi(self,ind,data):
 
 
### setStatistics(self):
 
 
### getLevel(self):
 
 
### getFullDesc(self):
 
 
### simplify(self):
 
 
### simplifyHierarchical(self):
 
 
### __getitem__(self,campo):
 
