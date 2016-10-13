#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''

from pprint import pprint

   
def sql():
  pepe=dict()
  clause1=dict()
  pepe['tables']='votos_locales'
  pepe['fields']=['geo_rel.padre','partido',('votes_presential','sum')]
  pepe['group']=['partido',]
  pepe['join']={'table':'geo_rel',
                'join_filter':"geo_rel.tipo_padre = 'P'",
                'join_clause':(('padre','=','votos_locales.municipio'),),
               }

  #clause2=dict()
  #pepe['fields']=(""" case 
        #when partido in (3316,4688) then '1 derecha'
    #when partido in (1079,4475) then '2 centro'
        #when partido in (3484) then '3 izquierda'
    #when partido in (3736,5033,4850,5008,5041,2744,5026) then '4 extrema'
        #when partido in (5063,4991,1528) then '5 separatistas'
        #when partido in (1533,4744,4223) then '6 nacionalistas'
    #else
         #'otros'
    #end as categoria""" ,'partido',('seats','sum'))
  #pepe['tables']='votos_provincia'
  #pepe['group']=('categoria',)
  #pepe['lfile']='sempronio'
  #pepe['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
  #pepe['tables'] = 'paco'
  ##pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
  #pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
  ##pepe['tables'] = 'paco'
  ##pepe['select_modifier'] = 'DISTINCT'
  #pepe['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
                    #('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
                  #)
  ##pepe['where']=((clause1,'OR',clause2),)
  ##pepe['group']=('julia','claudia')
  ##pepe['having']=(('campo','=','345'),)
  #pepe['base_filter']=''
  #pepe['order']=(1,(2,'DESC'),3)
  #pprint(pepe)
  ##pepe['fields'] = '*'

  print(queryConstructor(**pepe))



from datadict import *    
from tablebrowse import *

#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QSplitter

from datalayer.query_constructor import *


def traverse(root,base=None):
    if base is not None:
       yield base
       queue = base.listChildren() 
    else:
        queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        #print(queue)
        #print('')
    while queue :
        yield queue[0]
        expansion = queue[0].listChildren() 
        if expansion is None:
            del queue[0]
        else:
            queue = expansion  + queue[1:]             
    
def browse(base):
    numConn = base.rowCount()
    for i in range(0,numConn):
        conn = base.child(i)
        print(conn.text(),conn.getRow())
        numSch = conn.rowCount()
        if numSch == 0:
            continue
        for j in range(0,numSch):
            schema = conn.child(j)
            print('\t',schema.text())
            numTab = schema.rowCount()
            if numTab == 0:
                continue
            for k in range(0,numTab):
                table = schema.child(k)
                print('\t\t',table.text(),table.getRow())
                
def browseTables(base):
    numConn = base.rowCount()
    for i in range(0,numConn):
        conn = base.child(i)
        #print(conn.text(),conn.getRow())
        numSch = conn.rowCount()
        if numSch == 0:
            continue
        for j in range(0,numSch):
            schema = conn.child(j)
            #print('\t',schema.text())
            numTab = schema.rowCount()
            if numTab == 0:
                continue
            for k in range(0,numTab):
                table = schema.child(k)
                #print(table.text())
                print(table.getFullDesc())
                info = table.getFullInfo()
                FK = info.get('FK')
                if FK :
                    pprint(info)

def browse0(base):                    
    numConn = base.rowCount()
    for i in range(0,numConn):
        conn = base.child(i)
        print(conn.text())

from cubebrowse import *



if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')    
    app = QApplication(sys.argv)
    #window = TableBrowserWin('MariaBD Local','sakila','film',pdataDict=None)
    #dataDict=DataDict()
    #window = TableBrowserWin('MariaBD Local','sakila','film',pdataDict=dataDict)
    ##window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    #window.show()
    #sys.exit(app.exec_())

    #dict=DataDict('JeNeQuitePas')
    dataDict=DataDict()
    #dataDict=DataDict(conn='MariaBD Local',schema='sakila')
    #dataDict=DataDict(conn='Pagila',schema='public')
    #for entry in traverse(dataDict.hiddenRoot):
        #tabs = '\t'*entry.depth()
        #if not entry.isAuxiliar():
            #print(entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    #browse(dataDict.hiddenRoot)
    #browseTables(dataDict.hiddenRoot)
    #browse0(dataDict.hiddenRoot)
    #info = getTable(dataDict,'MariaBD Local','sakila','rental')            
    #info = getTable(dataDict,'MariaBD Local','sakila','film')            
    #cubo = info2cube(dataDict,'MariaBD Local','sakila','rental')            
    info2cube(dataDict,'Pagila','public','rental')            
    #pprint(info)
    #pprint(cubo)
    #cursor = localQuery(dataDict.conn['MariaBD Local'],info,1)
    #modelo = QStandardItemModel()
    #for row in cursor:
        #modelRow = [ QStandardItem(str(fld)) for fld in row ]
        #modelo.appendRow(modelRow)
    #print(modelo.rowCount(),modelo.columnCount())
    #for k in range(modelo.rowCount()):
        #datos = [ modelo.item(k,j).data(Qt.DisplayRole) for j in range(modelo.columnCount()) ]
        ##datos = [ itm.data(Qt.DisplayRole) for itm in deRow ]
        #print(datos)
    ##getTable(dataDict,'Elecciones 2105','','partidos')            
"""
SELECT  geo_rel.padre, partido, sum(votes_presential)  
FROM votos_locales  
     JOIN geo_rel ON geo_rel.hijo = votos_locales.municipio AND geo_rel.tipo_padre = 'P'  
     GROUP BY geo_rel.padre, partido  
     
"related via":[{
    "table": "geo_rel",
    "clause": [
        {
            "rel_elem":"hijo",
            "base_elem":"votos_locales.municipio"
        }
        ],
    "filter": "geo_rel.tipo_padre = 'P'"
                        }
                        ],

"""
