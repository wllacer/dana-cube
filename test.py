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
#from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication
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

def getTable(dd,confName,schemaName,tableName):
    con = dd.getConnByName(confName)
    if con is None:
        print('Conexion {} no definida'.format(confName))
        return
    sch = con.getChildrenByName(schemaName)
    if sch is None:
        print('Esquema {} no definido'.format(schemaName))
        return
    tab = sch.getChildrenByName(tableName)
    if sch is None:
        print('Tabla {} no definid'.format(tableName))
        return
    print(tab.getFullDesc())
    return tab.getFullInfo()

def SQLsimple(conn,info):
    pepe=dict()
    if info.get('schemaName','') != '':
        pepe['tables']= info['schemaName'] + '.' + info['tableName']
    else:
        pepe['tables'] = info['tablename']
    pepe['fields'] = [ item[0] for item in info['Fields'] ]
    
    sqls = queryConstructor(**pepe)
    pprint(getCursor(conn,sqls))
    return
def SQLwFK(conn,info):
    """
    TODO relaciones con mas de un campo como enlace
    TODO comprobar que nombres de tablas no colisionan
    TODO informacion de formatos para la tabla de visualizacion
    TODO generalizar :
        * sin FKs
        * con FKs recursivas
    """
    pepe=dict()
    if info.get('schemaName','') != '':
        pepe['tables']= info['schemaName'] + '.' + info['tableName']
        pepe['fields'] = [ pepe['tables']+'.'+item[0] for item in info['Fields'] ]
    else:
        pepe['tables'] = info['tablename']
        pepe['fields'] = [ item[0] for item in info['Fields'] ]
    if info['FK']:
        pepe['join'] = []
        for relation in info['FK']:
            entry = dict()
            entry['table'] = relation['ParentTable']
            entry['join_clause'] = ((pepe['tables']+'.'+relation['Field'],'=',relation['ParentTable']+'.'+relation['ParentField']),)
            pepe['join'].append(entry)
            campos = [entry['table']+'.'+elem[0] for elem in relation['CamposReferencia'] ]
            # con esto insertamos a partir del elemento de enlace
            idx = pepe['fields'].index(entry['join_clause'][0][0])
            pepe['fields'][idx+1:idx+1] = campos
    #pepe['join']={'table':'geo_rel',
                #'join_filter':"geo_rel.tipo_padre = 'P'",
                #'join_clause':(('padre','=','votos_locales.municipio'),),
                #}
    pprint(pepe)
    sqls = queryConstructor(**pepe)
    pprint(sqls)
    #pprint(getCursor(conn,sqls))
    return
    pepe['fields']=['geo_rel.padre','partido',('votes_presential','sum')]
    pepe['group']=['partido',]


if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)
    #dict=DataDict('JeNeQuitePas')
    dataDict=DataDict()
    #for entry in traverse(dataDict.hiddenRoot):
        #tabs = '\t'*entry.depth()
        #if not entry.isAuxiliar():
            #print(entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    #browse(dataDict.hiddenRoot)
    #browseTables(dataDict.hiddenRoot)
    #browse0(dataDict.hiddenRoot)
    info = getTable(dataDict,'MariaBD Local','sakila','customer')            

    SQLwFK(dataDict.conn['MariaBD Local'],info)
    #getTable(dataDict,'Elecciones 2105','','partidos')            
