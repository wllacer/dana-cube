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



from dictmgmt.datadict import *    
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

def info2cube(dataDict,confName,schema,table,maxlevel=1):
    """
       de monento solo sustituyo
    """
    #TODO strftime no vale para todos los gestores de base de datos
    #pprint(dataDict)
    info = getTable(dataDict,confName,schema,table,maxlevel)                
    #pprint(info)
    
    #cubo = load_cubo()
    cubo = dict()
    cubo[table]=dict() # si hubiera algo ... requiescat in pace
    entrada = cubo[table]
    #entrada = dict()
    entrada['base filter']=""
    entrada['table'] = '{}.{}'.format(schema,table) if schema != "" else table
    
    entrada['connect']=dict()
    conn = dataDict.getConnByName(confName).data().engine
    
    print('Conexion ',conn.url,conn.driver)
    entrada['connect']["dbuser"] = None 
    entrada['connect']["dbhost"] =  None
    entrada['connect']["driver"] =  conn.driver
    entrada['connect']["dbname"] =  str(conn.url) #"/home/werner/projects/dana-cube.git/ejemplo_dana.db"
    entrada['connect']["dbpass"] =  None
    
    entrada['guides']=[]
    entrada['fields']=[]
    for fld in info['Fields']:
        if fld[1] in ('numerico'):
            entrada['fields'].append(fld[0])
        elif fld[1] in ('fecha'):
            entrada['guides'].append({'name':fld[0],
                                      'class':'d',
                                      'type':'Ymd',
                                      'prod':[{'fmt':'date','elem':fld[0]},]
                                      })  #no es completo
            #TODO cambiar strftime por la funcion correspondiente en otro gestor 
            entrada['guides'].append( genTrimestreCode(fld[0],conn.driver))

        else:
            entrada['guides'].append({'name':fld[0],
                                      'class':'o',
                                      'prod':[{'elem':fld[0],},]})  #no es completo
        """
                "prod": [
                    {   "domain": {
                            "filter": "code in (select distinct partido from votos_provincia where votes_percent >= 3)", 
                            "table": "partidos", 
                            "code": "code", 
                            "desc": "acronym"
                        }, 

                        "elem": "partido"
                    }
        """
    if maxlevel == 0:
        pass
    elif maxlevel == 1:
        for fk in info.get('FK',list()):
            desc_fld = getDescList(fk)
                
            entrada['guides'].append({'name':fk['Name'],
                                        'class':'o',
                                        'prod':[{'domain': {
                                                "filter":"",
                                                "table":fk['ParentTable'],
                                                "code":fk['ParentField'],
                                                "desc":desc_fld
                                            },
                                            'elem':fk['Field']},]
                                            })  #no es completo
    else:
        routier = []
        #path = ''
        path_array = []
        for fk in info.get('FK',list()):
            constructFKsheet(fk,path_array,routier)
            #constructFKsheet(fk,path,path_array,routier)
        
        for elem in routier:
            nombres = [ item['Name'] for item in elem]
            nombres.reverse()
            nombre = '@'.join(nombres)
            activo = elem[-1]
            base   = elem[0]
            rule =   {'domain': {
                                    "filter":"",
                                    "table":activo['ParentTable'],
                                    "code":activo['ParentField'],
                                    "desc":getDescList(activo)
                                },
                         'elem':activo['Field']}   #?no lo tengo claro
            if len(elem) > 1:
                #aqui vienen los join
                """select sum(film.film_id),category_id from film 
                   join film_category on film.film_id = film_category.film_id
                   group by category_id
                   *
                   "link via":[{
                        "table": "geo_rel",
                        "clause": [
                            {
                                "rel_elem":"hijo",
                                "base_elem":"votos_locales.municipio"
                            }
                            ],
                        "filter": "geo_rel.tipo_padre = 'P'"
                        }
                """
                rule['link via']=list()
                for idx in range(len(elem)-1):
                    actor = elem[idx]
                    join_clause = { "table":actor['ParentTable'],
                                    "clause":[{"rel_elem":actor["ParentField"],"base_elem":actor['Field']},],
                                    "filter":"" }
                    rule['link via'].append(join_clause)
                
            entrada['guides'].append({'name':nombre,
                                        'class':'o',
                                        'prod':[rule ,]
                                            })  #no es completo
            #for idx,nivel in enumerate(elem):
                #rule =  
                #if idx != 0:
                    #join = {"table": elem[idx -1]['ParentTable'],
                            #"clause": [
                                #{
                                    #"rel_elem":nivel['ParentTable'],
                                    #"base_elem":nivel['Field'],
                                #}
                                #],
                            #"filter": "",
                            #}
                    #rule['link via']=[join,]
                #prod_rules.insert(0,rule)
            #activa['prod']=prod_rules
            #if len(elem) > 1:
                #break 
    return cubo

#def constructFKsheet(elemento,path, path_array,routier):
def constructFKsheet(elemento, path_array,routier):    
    #kpath = path+'.'+elemento['Name']
    path_array_local = path_array[:]
    path_array_local.append(elemento)
    #if 'FK' not in elemento:
    #print(kpath)
    routier.append(path_array_local)
    for fkr in elemento.get('FK',list()):
        constructFKsheet(fkr,path_array_local,routier)
        #constructFKsheet(fkr,kpath, path_array_local,routier)
        
def getDescList(fk):
    desc_fld = []
    for fld in fk['CamposReferencia']:
        if fld[1] == 'texto':
            desc_fld.append(fld[0])
    if len(desc_fld) == 0:
        #print('No proceso correctamente por falta de texto',fk)
        desc_fld = fk['ParentField']
#            continue
    return desc_fld

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from util.tree import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.fivenumbers import stats

from datemgr import getDateIndex,getDateEntry
from pprint import *

from core import Cubo
from VistaSkel import VistaSkel

import time

def experimento():
    from util.jsonmgr import load_cubo
    def presenta(vista):
        guia=vista.row_hdr_idx
        ind = 0
        for key in guia.traverse(mode=1):
            elem = guia[key]
            print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
            ind += 1
    vista = None
    mis_cubos = load_cubo('experimento.json')
    cubo = Cubo(mis_cubos['customer'])
    #pprint(cubo.definition)
    #pprint(cubo.definition)
    #pprint(cubo.lista_funciones)
    #pprint(cubo.lista_campos)
    #pprint(cubo.lista_guias[6])
    for ind,guia in enumerate(cubo.lista_guias):
        print(ind,guia['name'])
    #cubo.fillGuias()
    #ind= 5
    #cubo.fillGuia(ind)
    #cubo.lista_guias[ind]['dir_row'].display()
    for k in range(len(cubo.lista_guias)):
        vista=VistaSkel(cubo,k,0,'sum','customer_id')
        print('\n\n\n')
        
from dictmgmt.dictTree import *
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    exit()
    app = QApplication(sys.argv)
    dataDict=DataDict(conn='MariaBD Local',schema='sakila')
    cubo = info2cube(dataDict,'MariaBD Local','sakila','customer',3)   
    pprint(cubo)
    dump_structure(cubo,'experimento.json')
    experimento()
    exit()

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
    for entry in traverse(dataDict.hiddenRoot):
        tabs = '\t'*entry.depth()
        if not entry.isAuxiliar():
            print(entry.fqn(),entry.getFullDesc(), entry.getRow(),entry.gpi()) #(tabs,entry) #entry.text(),'\t',entry.getRow())
    #browse(dataDict.hiddenRoot)
    #browseTables(dataDict.hiddenRoot)
    #browse0(dataDict.hiddenRoot)
    #info = getTable(dataDict,'MariaBD Local','sakila','rental')            
    #info = getTable(dataDict,'MariaBD Local','sakila','film')            
    #cubo = info2cube(dataDict,'MariaBD Local','sakila','customer',2)   
    #pprint(cubo)
    #dump_structure(cubo,'experimento.json')
    #info2cube(dataDict,'Pagila','public','rental')            
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
     
"link via":[{
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
