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

# class Cubo:

## Attributes

### definition

### nombre

### db = dbConn

### lista_guias

### lista_funciones 

### lista_funciones 

### lista_campos
        
### dbdriver = self.db.dialect.name

### newModel __UNUSED__

### recordStructure  __DERIVED__

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
    

###  setDateFilter(self):
__INTERNAL__

convierte la clausula date filter en codigo que puede utilizarse como una clausula where 
Retorna una tupla de condiciones campo BETWEEN x e y, con un indicador de formato apropiado (fecha/fechahora(

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

    
    Information is internal and not expected to be queried by the user. The __context__ is a dictionary with following entries
    * 'table':table,   -> guide's domain table
    * 'code':code,      -> tuple of fields which contain the related values in the cube's table, when the view is created
    * 'desc':desc,      -> tuple of field at the domain's table whic contain the descriptive values. If empty code subtitutes for
    * 'groupby':groupby,_> fields needed to link a hierarchy of guides, included in code
    * 'columns':columns, _> full list of the fields needed on the select statement needed to create the guide
    * 'elems':elems,    ->  list of field to be included in the __group by__ statemet when the view is created
    * 'linkvia':linkvia   _> In case the guide is created via __join__ statements, the definition thereof

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

### agregado

### campo

### filtro

### totalizado

### stats

### row_id

### col_id

### row_hdr_idx

### col_hdr_idx

### dim_row

### dim_col

### array


## Methods

###  __init__(self, cubo,prow, pcol,  agregado, campo, filtro='',totalizado=True, stats=True):

###  setNewView(self,prow, pcol, agregado=None, campo=None, filtro='',totalizado=True, stats=True, force=False):

###   __setDateFilter(self):

###   __setDataMatrix(self):

###  toNewTree(self):

###  toNewTree2D(self):
    ###  setContext(row,col):

###  recalcGrandTotal(self):
    ###  cargaAcumuladores():
    ###  procesa():

###  traspose(self):

###  fmtHeader(self,dimension, separador='\n', sparse=False): #, rango= None,  max_level=None)

###  __exportHeaders(self,tipo,header_tree,dim,sparse,content):

###  getExportData(self,parms,selArea=None):

###  export(self,parms,selArea=None):, s
    ###  csvFormatString(cadena):
    
## Programming notes
def createVista(cubo,x,y):
def experimental():
###  presenta(vista):

# Auxiliary functions

## traverse(tree, key=None, mode=1):
## searchStandardItem(item,value,role):

# class TreeFormat(object):

## Attributes

### format

### stats

## Methods

### __init__(self,**opciones):

## Programming notes    

# class GuideItemModel(QStandardItemModel):

## Attributes

### colTreeIndex

### datos

### name

## Methods

### __init__(self,parent=None):

### traverse(self,base=None):

### numRecords(self):

### len(self):

### lenPayload(self,leafOnly=False):

### searchHierarchy(self,valueList,role=None):

### setStats(self,switch):

### data(self,index,role):

### filterCumHeader(self,total=True,branch=True,leaf=True,separador='\n',sparse=True):

## Programming notes

# class GuideItem(QStandardItem):

## Attributes

### originalValue

### stats

## Methods

### __init__(self,*args):  solo usamos valor (str o standarItem)

### setData(self,value,role):

### type(self):

### data(self,role):

### __str__(self):

### __repr__(self):

### getPayload(self,leafOnly=False):

### setPayload(self,lista,leafOnly=False):

### lenPayload(self,leafOnly=False):

### getPayloadItem(self,idx):

### setPayloadItem(self,idx,valor):

### _getHead(self):

### getKey(self):

### getLabel(self):

### depth(self):

### getFullKey(self):

### getFullDesc(self):

### searchChildren(self,value,role=None):

### setColumn(self,col,value):

### getColumn(self,col):

### getColumnData(self,idx,role=None):

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

## Programming notes
