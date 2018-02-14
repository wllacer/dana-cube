__Table of Contents__

1. [Auxiliary Functions][]
   1. [mergeString(string1,string2,connector)][]
   1. [getParentKey(clave,debug=False):][]
   1. [getOrderedText(desc,sparse=True,separator=None):][]
   1. [exportFilter(item,dim,filter=None):][]
1. [class Cubo:][]
   1. [Attributes][]
      1. [definition][]
      1. [nombre][]
      1. [db][]
      1. [lista_guias][]
      1. [lista_funciones ][]
      1. [lista_campos][]
      1. [dbdriver ][]
      1. [newModel __UNUSED__][]
      1. [recordStructure  ][]
   1. [Methods][]
      1. [ \_\_init\_\_(self, definicion,nombre=None,dbConn=None):][]
      1. [ getGuideNames(self):][]
      1. [ getFunctions(self):][]
      1. [ getFields(self):][]
      1. [ fillGuias(self):][]
      1. [ fillGuia(self,guidIdentifier,total=None):][]
   1. [Programming notes][]
1. [class Vista:][]
   1. [Attributes][]
      1. [cubo][]
      1. [agregado][]
      1. [campo][]
      1. [filtro][]
      1. [totalizado][]
      1. [stats][]
      1. [row_id][]
      1. [col_id][]
      1. [row_hdr_idx][]
      1. [col_hdr_idx][]
      1. [dim_row][]
      1. [dim_col][]
      1. [array][]
   1. [Methods][]
      1. [ \_\_init\_\_(self, cubo,prow, pcol,  agregado, campo, filtro='',totalizado=True, stats=True):][]
      1. [ setNewView(self,prow, pcol, agregado=None, campo=None, filtro='',totalizado=True, stats=True, force=False):][]
      1. [ toNewTree(self):][]
      1. [ toNewTree2D(self):][]
      1. [toArray(self)][]
      1. [toArrayFilter(self,filterrow,filtercol)][]
      1. [toList(self):][]
      1. [ recalcGrandTotal(self):][]
      1. [ traspose(self):][]
      1. [ export(self,parms,selArea=None):][]
   1. [Programming notes][]

# Auxiliary Functions
## mergeString(string1,string2,connector)
Adds two strings with a connector (surrounded with blanks) is any ot the strings is not null or not empty 

## getParentKey(clave,debug=False):
__OBSOLETE__
Get a parent's key from the child's one

* input parameters:
    * __clave__ item's key 
    * __debug__ NOT USED
* returns
    * parent's key

## getOrderedText(desc,sparse=True,separator=None):
__OBSOLETE__
From an array of texts (_desc_) returns a string with each value delimited (_separator_). If _sparse_ is true it returns only the last element, preceded from the separators

* input parameters
    * __desc__      An array of texts
    * __sparse__    boolean. True if only last value is of interest, False if all elements of desc are retrieved)
    * __separator__ character or string. A delimiter
* returns
    * a string

## exportFilter(item,dim,filter=None):

Auxiliary function.
Used as filter in export functions

* Input parameters
    * __item__ a GuideItem. Element to be checked
    * __dim__ a number, number of levels of the tree
    * __filter__ a dictionary with the filter requeriments
        * __content__ =  One of ('full','branch','leaf'). _full_ is everything, _branch_ only branches of the model tree; _leaf_ only leaves of the model_tree. Default _full__
        * __totals__ Boolean. True if download includes grand total. Default True
* Returns
    Boolean. True if accepted, False otherwise
    
* Note:
    The best way to call it is
        ```
        parms = { 'content':'full','totals':True}
        rowHdr = vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
        
        ```

# class Cubo:

## Attributes

### definition
Holds the active definition dictionary

### nombre
A name for the cube

### db

Holds the sqlAlchemy.connection active for this cube

### lista_guias
An array whith the current definition of the guides. Each element is a dictionary with

*  __name__   name of the guide as it appears in the user interface
*  __class__    '' normal or 'd' date (Ooptional)
*  __contexto__ 
    Information is internal and not expected to be queried by the user. The __context__ is a dictionary with following entries
    
    * 'table':table,   -> guide's domain table
    * 'code':code,      -> tuple of fields which contain the related values in the cube's table, when the view is created
    * 'desc':desc,      -> tuple of field at the domain's table whic contain the descriptive values. If empty code subtitutes for
    * 'groupby':groupby,_> fields needed to link a hierarchy of guides, included in code
    * 'columns':columns, _> full list of the fields needed on the select statement needed to create the guide
    * 'elems':elems,    ->  list of field to be included in the __group by__ statemet when the view is created
    * 'linkvia':linkvia   _> In case the guide is created via __join__ statements, the definition thereof
* __dir_row__ the generated model tree (__GuideItemModel__)

_contexto_ y _dir\_row_ are created only when __self.fillGuia__ is executed


### lista_funciones 
An array with the available Sql functions for the current database manager

### lista_campos
the list of fields available for evaluation in this cube
 
### dbdriver 
The name of the current type of database manager (it holds self.db.dialect.name)

### newModel __UNUSED__

### recordStructure  
holds the sql structure (list of columns --their fully qualified name and their formats)  of the base table on which the cube is defined.
For the time being is loaded thru __DanaCubeWindow.getCubeRecordInfo__

## Methods
###  \_\_init\_\_(self, definicion,nombre=None,dbConn=None):
Cube initialization 

* input parameters
    * __definicion__ -> dictionary with the structure of the cube to create (definition acording to (cube docs)[./tree_docs.md]
    * __nombre__     -> (optional) a name for the cube
    * __dbConn__     -> (optional) If the database connection is already open, it can be reused with this parm (_a sqlAlchemy connection_)

###  getGuideNames(self):
Returns an array with the names of the guides

* returns
    * a tuple of strings

###  getFunctions(self):
Returns an array with the names of available db functions (sum,avg, ...) for this cube. Allows for special handling of a database backend

* returns
    * a tuple of strings

###  getFields(self):
Return the list of fields available for evaluation in this cube. First time invocation creates the list, according to the cube definition

* returns
    * a tuple of strings
    

###  fillGuias(self):
__DEBUG ONLY__

We allow in a single step to generate all the guides (executes __self.fillGuia__ internally for each defined guide), and it's corresponding value trees. 
Resource usage migth be excesive. It's not used internally and should be used only for debugging purposes

###  fillGuia(self,guidIdentifier,total=None):
__DEBUG ONLY__

Is the method used to generate the guide, i.e. access the DataBase and fill its tree. It generates and keeps some context information. 

Should be explictily called only for debugging purposes. Each subsequent execution clears all the values related to the guide
 
* input parameters
    * __guidIdentifier__ guide to be processed. Accept both the name or the number (offset in the list)
    * __total__ . Boolean. If rows for totals have to be created. 
* Output
    * __arbol__    A __GuideItemModel__.  Is the model which contains the data tree of the guide
    * __contexto__ A dictionary with information needed n subsequent use of the guide

    


## Programming notes

The normal use is just to instantiate the class and use it as parameter for the view(s) neededs

```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])
vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
``` 
As the sample shows, the dictionary which holds the cube definition is not created inside the module, but read from a Json file thru the _load\_cubo_ function


For debugging purposes it might be useful to get the content of one of the guides. A sample follows


```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *
from PyQt5.QtCore import Qt

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])

guiax,dummy = cubo.fillGuia(1,total=True)

for item in guiax.traverse():
    print('\t'*item.depth(),item.data(Qt.DisplayRole),item.data(Qt.UserRole +1))

```

# class Vista:

## Attributes

### cubo
The reference to the __Cubo__ for which this view is definde

### agregado
Name of the sql agregate function we are using in this view

### campo
Name of the field which is aggregated in the view

### filtro
An sql fragment compatible with a __select__ statement, used to filter the resulting data BEFORE aggregation

### totalizado
Boolean. Determines if the view has a grand total row

### stats
Boolean. Determines if we hold basic statistic data for each row. (see __GuideItemModel.setStats__ for details)

### row_id
Integer. The index in self.cubo.lista_guias of the row guide

### col_id
Integer. The index in self.cubo.lista_guias of the column guide

### row_hdr_idx
GuideItemModel. the tree for the row guide

### col_hdr_idx
GuideItemModel. the tree for the column guide

### dim_row
Integer. Number of nested levels of aggregation for the row 

### dim_col
Integer. Number of nested levels of aggregation for the column

### array
Holds the raw results of the view. It is an array of tuples (rowItem. colItem, numeric value)

## Methods

###  \_\_init\_\_(self, cubo,prow, pcol,  agregado, campo, filtro='',totalizado=True, stats=True):

Instances the view. It implies access to the database and generation of the __self.array__

* Input parameters
    * __cubo__ Reference of the Cubo we'll be using
    * __prow__ Name or Index of the guide will be used as row
    * __pcol__ Name or Index of the guide will be used as column
    * __agregado__ Name of the sql aggregate function to use
    * __campo__ Name of the column which well be aggregated
    * __filtro__ sql fragment to filter the query before aggregation
    * __totalizado__ boolean. If a Grand Total row will be generated
    * __stats__ boolean. Rows will have basic statistic

###  setNewView(self,prow, pcol, agregado=None, campo=None, filtro='',totalizado=True, stats=True, force=False):

Allows to change any parameter of the current view and reevaluate it. Only the row and column are mandatory, parameters not included will use the value of the last run

* Input parameters
    * __cubo__ Reference of the Cubo we'll be using
    * __prow__ Name or Index of the guide will be used as row
    * __pcol__ Name or Index of the guide will be used as column
    * __agregado__ Name of the sql aggregate function to use
    * __campo__ Name of the column which well be aggregated
    * __filtro__ sql fragment to filter the query before aggregation
    * __totalizado__ boolean. If a Grand Total row will be generated
    * __stats__ boolean. Rows will have basic statistic
    * __force__ boolean. If there is no change relative to the previous execution (or view instatiation) the view is not reevaluated, unless this parameter is set 

###  toNewTree(self):

From the __self.array__ loads each element of the row model (self.row_hdr_idx) with a vector with the value for each element in the column model

###  toNewTree2D(self):

From the __self.array__ 
* loads each element of the row model (self.row_hdr_idx) with a vector with the value for each element in the column model.
* loads each element of the column model (self.col_hdr_idx) with a vector with the value for each element in the row model.

### toArray(self)

Convert the raw data of the view in a two dimensional array, for further processing. Non existing values are returned as None

* Returns
   a two dimensional array with the values

### toArrayFilter(self,filterrow,filtercol)

Convert the raw data of the view in a two dimensional array, for further processing. Non existing values are returned as None.

Aditionally two filter functions are specified as parameters, one for rows, the other for columns. Each function accepts an item tree  as parameter (GuideItem) and returns a boolean value: True if it will be processed, False otherwise

* Input parameters
    * __filterrow__ filter function for rows.
    * __filtercol__ filter function for columns

* Returns
   a two dimensional array with the values. Only acceptable rows/columns are included in the array

### toList(self):
Converts the view results in a list of texts

* Input parameters. All optional
    * __colHdr__  boolean if a column header will be shown. default True
    * __rowHdr__  boolean if a row header will be shown. default True
    * __numFmt__ python format for the numeric values. Default = _'      {:9,d}'_
    * __colFmt__    python format for the column headers. Default = _' {:>n.ns}'_, where _n_ is the len of the numeric format minus 1
    * __rowFmt__   python format for the row headers. Default = _' {:20.20s}'_, 
    * __hMarker__  hierachical marker (for row header). Default _'  '_    
    * __rowHdrContent__ one of ('key','value'). Default 'value'
    * __colHdrContent__ one of ('key','value'). Default 'value'
    * __rowFilter__ a filtering function
    * __colFilter__ a filtering function

* Returns
    a tuple of formatted lines


###  recalcGrandTotal(self):

If any manipulation has been made ONLY to the leaf elements of the row model, this method reconstruct the corresponding values to the branch and total elements

###  traspose(self):

If the models are filled using the __toNewTree2D__ method, this method allows to traspose the view (change row for column)


###  export(self,parms,selArea=None):

This method allows for the export of the view data as files in several formats.
Prior to the export __self.toNewTree__ or __self.toNewTree2D__ must have been called

* Input Parameters
    * __parms__ a dictionary with the ata needed to export the data. The parms allowed are:
    
        * __file__  (_mandatory_) name of the destination file
        
        * __type__  One of {'csv','xls','json','html'}. If _xls_ is not available, defaults to _csv_. _html_ generates ONLY  a table definition fragment, NOT a full html page. If not present defaults to _csv__
        
        * __csvProp__ A dictionary with specific parameters for csv conversion 
        
            * __fldSep__  Field separator char. Default ','
            
            * __decChar__ Default Decimal character. Default '.'
            
            * __txtSep__  Text separator char. Default "'"
            
        * __NumFormat__ Boolean. If numbers will be formatted with separators. Default=False
        
        * __filter__ A dictionary selecting What data are exported
        
            * __scope__ One of ('all')
            
            * __row__ or __col__ a dictionary with filter for rows/columns
            
                * __content__ =  One of ('full','branch','leaf'). _full_ is everything, _branch_ only branches of the model tree; _leaf_ only leaves of the model_tree. Default _full__
                
                * __totals__ Boolean. True if download includes grand total. Default True
                
                * __Sparse__ Boolean. True if header elements are only filled the first time they appear. Default True
    
    * __selArea__ An array limiting the output __UNUSED__ 
    
* Returns
    Numeric 0 if correct, -1 if something went wrong



    
## Programming notes


We show a sample of how we coud get a view and show it in an array formatted with headers

this particular case can be solved with the __toList__ method 

```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *
from PyQt5.QtCore import Qt

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])

vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
for line in vista.toList(numFmt=' {:14,.2F}'):
    print(line)
```
But if you prefer to code it in detail (with slightly different formatting)

```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *
from PyQt5.QtCore import Qt

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])

vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
# the names of the guides ('provincia','partidos') might be sustituted for their indexes eg.
# vista = Vista(cubo,3,1,'sum','votes_presential',totalizado=True)
vista.toNewTree()

#now we get the column headers
hdr = ' '*20 
for item in vista.col_hdr_idx.traverse():
    hdr += '{:>14s} '.format(item.data(Qt.DisplayRole))
print(hdr)

#now we get the data for each row
for item in vista.row_hdr_idx.traverse():
    rsults = item.getPayload()
    datos = ''
    for dato in rsults:
        if dato is not None:
            datos += '      {:9,d}'.format(dato)
        else:
            datos +=' '*15
    # and we print including the header for each row
    print('{:20s}{}'.format(item.data(Qt.DisplayRole),datos))
    
```
The easiest way to access the model data is via the statement
```
for item in vista.row_hdr_idx.traverse():
```
it returns the row in a hierarchy (if the guide is hierarchical) and in the default order of the generated _order by_ statement of the guide (the code values, not the description)

For each row (item) there are three methods you have to check

* __item.data(Qt.DisplayRole)__, which holds the description of the element

* __item.data(Qt.UserRole + 1)__, which holds the internal value of the element

* __item.getPayload()__, which is an array with the values por each column (None if not defined for this row, else a numeric value)

And a second sample how to export to a csv file


```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *
from PyQt5.QtCore import Qt

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])

vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)

export_parms = {'file':'datos.csv'}
vista.export(export_parms)

```
