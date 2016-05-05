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

   

if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    #experimental()
    sql()
