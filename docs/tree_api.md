
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
