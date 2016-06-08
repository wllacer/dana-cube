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
from core import Cubo,Vista
from datalayer.query_constructor import *
from operator import attrgetter,methodcaller

from pprint import pprint


(_ROOT, _DEPTH, _BREADTH) = range(3)

def presentaIndice(cubo,num):
    guia=cubo.lista_guias[num]['dir_row']
    ind = 0
    for key in traverse(guia,mode=1):
        elem = guia[key]
        print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
        ind += 1

def experimental():
    from util.jsonmgr import load_cubo
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['experimento'])
    for ind,guia in enumerate(cubo.lista_guias):
        print(ind,guia['name'])

    ind=4
    pprint(cubo.lista_guias[4])
    #cubo.fillGuia(ind)
    #guia=cubo.lista_guias[ind]['dir_row']
    #vista=Vista(cubo,1,5,'avg','votes_percent')
    #resultado=vista.toCsv(col_sparse=True)
    #for entrada in resultado:
        #print(entrada)
    #for elem in (sorted(guia.content,key=methodcaller('childCount'),reverse=True)):
        #print(elem,sorted(guia[elem].childItems,key=attrgetter('desc')))
        #print(elem,sorted(guia[elem].childItems,key=methodcaller('childCount'),reverse=True))
        #print(elem)
def traverse(tree, key=None, mode=1):
    # Obtenido de
    # Brett Kromkamp (brett@perfectlearn.com)
    # You Programming (http://www.youprogramming.com)
    # May 03, 2014, que afirma
    # Python generator. Loosly based on an algorithm from 
    # 'Essential LISP' by John R. Anderson, Albert T. Corbett, 
    # and Brian J. Reiser, page 239-241
    if key is not None:
        yield key
        queue = tree.content[key].childItems
    else:
        queue = tree.rootItem.childItems
        print(queue)
        print('')
    while queue:
        yield queue[0].key
        expansion = queue[0].childItems
        if mode == _DEPTH:
            queue = expansion + queue[1:]  # depth-first
        elif mode == _BREADTH:
            queue = queue[1:] + expansion  # width-first
   
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

from datalayer.access_layer import *
from datalayer.directory import *
from util.tree import *

def getSchemas(inspector,catalogo):
    if len(inspector.get_schema_names()) is 0:
        print('No schema available')
        schemata =[None,]
    else:
        default_schema = inspector.default_schema_name
        print(default_schema,inspector.get_schema_names())
        for schema in inspector.get_schema_names():  #behaviour with default
           catalogo.append(TreeItem(schema,data=[schema,True if schema == default_schema else False]))
           for table_name in inspector.get_table_names(schema):
               pass
           
               
    #return schemata

def dir2tree():

    definition={'driver':'sqlite','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False } 
    definition={'driver':'postgresql','dbname': 'pagila',
                'dbhost':'localhost','dbuser':'werner','dbpass':None,'debug':False } 
    
    catalogo = TreeDict()
    inspector = getInspector(definition)    
    getSchemas(inspector,catalogo)
    for k in catalogo.traverse(mode=1):
        print(k)

def mysqlSchema():
    definition={'driver':'mysql','dbname': 'fiction',
                'dbhost':'localhost','dbuser':'root','dbpass':'toor','debug':False } 
    definition={'driver':'mysql','dbname': 'fiction',
                'dbhost':'localhost','dbuser':'root','dbpass':'toor','debug':False } 
    #dirQt(definition)
    definition={'driver':'postgresql','dbname': 'pagila',
                'dbhost':'localhost','dbuser':'werner','dbpass':None,'debug':False } 
    dirAlchI(definition)
    #dirAlchM(definition)
    #conn = dbConnectAlch(definition)
    #getTableFields(conn,'votos_locales')
    #getTableFields(conn,'votos_locales','default') #TODO deberia contemplarse
    #getTableFields(conn,'mio.tuyo')
    #getTableFields(conn,'votos_v')
    #pprint(getTableFields(conn,'votos_locales'))
    #print(filter(lambda item: item[1] == 'fecha',getTableFields(conn,'votos_locales')))
    #print(camposDeTipo('numerico',conn,'votos_locales'))

def multischema():
    definition = []
    definition.append({'driver':'sqlite','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False })
    definition.append({'driver':'mysql','dbname': None,
                'dbhost':'localhost','dbuser':'root','dbpass':'toor','debug':False })
    definition.append({'driver':'postgresql','dbname': 'pagila',
                'dbhost':'localhost','dbuser':'werner','dbpass':None,'debug':False } )

    definition.append({'driver':'mysql','dbname': 'fiction',\
                'dbhost':'localhost','dbuser':'demo','dbpass':'demo123','debug':False }) 
    conn = []
    
    for conf in definition:
        if conf['driver'] == 'mysql' and conf['dbname'] is None:
            pass
        else:
            conn.append(dbConnectAlch(conf))
      
    for conexion in conn:
        engine=conexion.engine #incredible
        inspector = inspect(engine)
        if len(inspector.get_schema_names()) is 0:
            schemata =[None,]
        else:
            schemata=inspector.get_schema_names()  #behaviour with default
        print(engine,inspector.default_schema_name,schemata)
        
        for schema in schemata:
            if schema == inspector.default_schema_name:
                schema = None
            for entry in inspector.get_sorted_table_and_fkc_names(schema):

            #for table_name in inspector.get_table_names(schema):
                try:
                    print(entry[0])
                    if entry[1] is not None or len(entry[1][0]) == 0:
                        pprint(entry[1])
                    #print('\t',schema,table_name)
                    #for column in inspector.get_columns(table_name,schema):
                        #try:
                            #name = column['name']
                            #tipo = column.get('type','TEXT')
                            #print("\t\t",fullName(schema,table_name,name),tipo,typeHandler(tipo))
                        #except CompileError: 
                        ##except CompileError:
                            #print('Columna sin tipo')

                except OperationalError:
                    print('error operativo en ',schema,table_name)
                    continue


        conexion.close()
def recrea_config():
    from util.jsonmgr import dump_structure,getConfigFileName
    definition = {'Conexiones':dict()}
    definition['Conexiones']['Elecciones 2105']={'driver':'sqlite','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False }
    definition['Conexiones']['Pagila']={'driver':'postgresql','dbname': 'pagila',
                'dbhost':'localhost','dbuser':'werner','dbpass':None,'debug':False } 

    definition['Conexiones']['MariaBD Local']={'driver':'mysql','dbname': 'fiction',\
                'dbhost':'localhost','dbuser':'demo','dbpass':'demo123','debug':False }
    dump_structure(definition,getConfigFileName())
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')
    
    #experimental()
    #dir2tree()
    #mysqlSchema()
    #multischema()
    recrea_config()
