 
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

 
# class GuideItem(QStandardItem):
 


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



## Methods reimplemented from [QStandardItem](http://doc.qt.io/qt-5/qstandarditem.html). See documentation there

 
### __init__(self,*args):  #
 
 
### type(self):
 

    We define three different types of items (really of the rows)
    TOTAL which correspond to the grand total
    BRANCH rows which have children 
    LEAF   rows without children

 
### data(self,role):
 

We make Qt.UserRole +1 as default role if Qt.DisplayRole returns None

 
### __str__(self):
 
 
### __repr__(self):
 
 
### __getitem__(self,campo):
 


We define three types of fields
* __'key'__  the UsdrRole content
* __'value'__ the DisplaRole content
* a number: the playload column



##  General methods QStandardItem should have

 
### depth(self):
 

hierachical level of the row

* returns
An integer with the current level, starting from 0
 
### _getHead(self):
 

for a given row, returns the current row header (i.e. the sibling which has column 0)

* returns
the item with column 0 from the current row
 
### searchChildren(self,value,role=None):
 

We seach for a specific value inside the children of the current row

* Input parameters
    * __value__ the value to be searched for. Type be QStandardItem.setData compatible
    * __role__ Qt.Role, if not specified Qt.UserRole +1
* Returns
An item which contains this value or None

* Implementation notes
Wide faster and hierachical level specific than model().find
Currently the values of the rows have to be sorted in advance
 
### getColumn(self,col):
 

Returns the item at column _col_ for the current row_hdr_idx

* Input parameters
    * __col__ the index of the column requested. 0 is not allowed

* Returns
The item at that column or None if it doesn't exist

* Implementation notes
Surprisingly such a method does not exist at QStandardItem
 
### setColumn(self,col,value,role=None):
 

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
 
### setUpdateColumn(self,col,value,role=None):
 

Method to set , for the current row, a payload entry at position _col_ with value _value_ .
If the item already exist it is updated, else is created
Can only be executed on GuideItems with column 0 (the head of the row)

* Input parameters
    * __col__ the index of the column to be set. 0 is not allowed
    * __value__ the value to be inserted. Type be QStandardItem.setData compatible
    * __role__ Qt.Role, if not specified Qt.UserRole +1
    
* returns
    a reference to the new column item or None (if 0 happens to be specified at _col_)
    
 
### rowTraverse(self):
 

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


## General methods which make up the API for __user functions__

 
### getPayload(self):
 

Returns a list with the values of the payload (columns 1 .. of the current row
 
### setPayload(self,lista): 
 

Updates in one step all the values of the payload.
If len(lista) < len(vector) only those values get updated; otherwise the vector will be expanded as apropiate

* Input parameters
     __lista__ a list with the new values for the vector 
 
### lenPayload(self):
 

Length of the payload for this __numRecords__

* Returns
Length of the payload

* implementation notes
QStandardItem.columnCount() does not seem to work, it should be lenPayload = columnCount -1.
In this case the use of the generator seems not that performant
 
### getPayloadItem(self,idx):
 

Returns the data at payload position _idx_ for the current row
It corresponds to column idx + 1

* Input parameters
    * __idx__ the index inside the payload.

* Returns
The item at that column or None if it doesn't exist


 
### setPayloadItem(self,idx,valor):
 

 Method to set , for the current row, a payload column at index _idx_ with value _value_ .
If the item already exist it is updated, else is created
It will correspond to column = idx +1

* Input parameters
    * __idx__ the index of the payload to be set. 
    * __value__ the value to be inserted. 
    
* returns
    a reference to the new column item or None 
 
### getKey(self):
 


returns the internal key of the current row 

 
### getLabel(self):
 


returns the display value for the current row 



##  Application specific methods

 
### getColumnData(self,idx,role=None):
 

Returns data from an specified index and role inside the payload.

* Input parameter
    * __idx__ the index in the payload 
    * __role__ data associated to that role. Default is Qt.UserRole +1
    
* Implementation notes
    For compatibility with other tree implementations
 
### getFullHeadInfo(self,**parms):
 

* parms
    * content = ('key','value')
    * format  = ('simple','string','array')
    * delimiter  (only if format == string)
    * sparse = boolean. Default False
 
### getFullKey(self):
 


obtains the key of the row in string format (i.e each hierachical step separated by DELIMITER ).
Key is the DB internal key and Qt.UserRole + 1 data

 
### getFullDesc(self):
 


obtains the description of the row in array format (i.e each hierachical step in an occurrence of a list ).
Description is the presentation values of the keys and Qt.DisplayRole data

 
### getStatistics(self):
 


returns the statistics gathered for this row 

 
### isTotal(self):
 


Boolean to check if the row is a totalizer row

 
### isBranch(self):
 


Boolean to check if the row is a branch row (has children of its own)

 
### isLeaf(self):
 


Boolean to check if the row is a leaf row (has no children of its own)

 
### restoreBackup(self):
 


Returns the payload item to the original value
If executed at the header restores the full row

 
### setBackup(self):
 


Sets the current value as  backup value (self.originalValue) for a payload column
If executed at the header restores the full row

For orthogonality sake we allow to process the full row if executed at the header

 
### setStatistics(self):
 


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
    

 
### simplify(self):
 

We get the value of the elements in the payload which are not Null (None)
Only to be executed at the head
* return
    * A list with the values of the non null payload
    * A list with the indexes of those elements

 
### simplifyHierarchical(self):
 

We get the value of the elements in the payload at this level and its parents. Only return those which are not Null at this level
Only to be executed at the head

* return
    * A list for each hiearchical level of lists of values of the non null payload
    * A list with the indexes of those elements

 
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
 
### __init__(self,parent=None):
 
 
### traverse(self,base=None):
 

Generator to navigate the tree. It only reads the head items of each rows

* Input parameter
    * __base__ initial item to process. default is .invisibleRootItem, but this element is not yielded
* returns
    * next item in sequence

__TODO__

It would be nice to put it functionally on par to util.treebasic.TreeModel
 
### numRecords(self,type=None):
 

Returns the number of items in the tree.
The standard model _rowCount_ method only gives the number of direct children of the first level

* Input Parameters
    * __type__ integer the type to be searched for (an integer above 1000. See Qt.StandardItem.type())
    
* returns
The number of items in the tree
 
### asDict(self):
 

returns a dictionary view of the tree. The purpose is to allow a quasi direct access to the item based on the key values

*Returns

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
 
### lenPayload(self,leafOnly=False):
 

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

#  MonkeyPatch section
   Definition of synonims of methods of the previous classes, used either for simplicity or compatibility

* GuideItemModel.len = GuideItemModel.numRecords

* GuideItem.childCount = GuideItem.rowCount
* GuideItem.gpi = GuideItem.getPayloadItem
* GuideItem.spi = GuideItem.setPayloadItem
* GuideItem.getLevel = GuideItem.depth
* GuideItem.getHeader = GuideItem.getFullHeadInfo

