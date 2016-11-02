#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time

from util.record_functions import *
from datalayer.access_layer import *
from datalayer.query_constructor import *

from PyQt5.QtWidgets import QApplication

from core import Cubo, Vista

from dictmgmt.datadict import DataDict
from cubemgmt.cubetree import traverseTree
string1="SELECT DISTINCT  region, provincia, nombre FROM  localidades WHERE  provincia <> '' and municipio = '' and isla = '' ORDER BY  1, 2"

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

def jerarquias():
    """
        El usar una lista como guia                          cuesta 15.2 segundos para el ejemplo
                un  diccionario (sin funcionalidad adicional)        0.06 segundos 
                un  diccionario (con funcionalidad adicional)        0.12 segundos (mas de 100 veces mejor)
    """
    from util.jsonmgr import load_cubo
        
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['experimento'])

    vista=Vista(cubo,1,2,'avg','votes_percent')
    for elem in vista.array:
        print(elem[0].desc,elem[1].desc,elem[2])
     
    confData = cubo.definition['connect']
    confName = '$$TEMP'
    (schema,table) = cubo.definition['table'].split('.')
    if table == None:
        table = schema
        schema = ''  #definitivamente necesito el esquema de defecto
    iters = 0
    dict = DataDict(conn=confName,schema=schema,table=table,iters=iters,confData=confData) #iters todavia no procesamos
    for item in traverseTree(dict.hiddenRoot):
        print(item.text())
    #cubo.fillGuias()
    #pprint(cubo.lista_guias[5]['dir_row'][0:10])
    #pprint(cubo.lista_guias[5]['des_row'][0:10])
    ## caso 0
    #string1="select distinct region,provincia,nombre from localidades order by 1,2,3"
    #cursor = getCursor(cubo.db,string1)
    #pprint(cursor[0:10])
    ## caso 1
    #string2="""
    #WITH t_municipio as (select codigo,nombre from geo where tipo = 'M'),
        #t_provincia as (select codigo,nombre from geo where tipo = 'P'),
            #t_region as (select codigo,nombre from geo where tipo = 'R'),
            #r_m_p as (select padre,hijo from geo_rel where tipo_padre = 'P'),
            #r_p_r as (select padre,hijo from geo_rel where tipo_padre = 'R')
            
    #select codigo as region,null as provincia,null as municipio,nombre from t_region
    #union
    #select r_p_r.padre,codigo as provincia,null as muncipio,nombre
        #from t_provincia
            #join r_p_r on hijo = t_provincia.codigo 
    #union
    #select r_p_r.padre,r_m_p.padre as provincia,codigo as muncipio,nombre
        #from t_municipio
            #join r_m_p on r_m_p.hijo = t_municipio.codigo
            #join r_p_r on r_p_r.hijo = r_m_p.padre
    #order by 1,2,3
    #"""
    #cursor = getCursor(cubo.db,string1)
    #pprint(cursor[0:10])


if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    app = QApplication(sys.argv)

    jerarquias()
    exit()

    #pepe=dict()
    #clause1=dict()
    #clause2=dict()

    ##pepe['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
    ##pepe['tables'] = 'paco'
    ##pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
    ##pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
    ##pepe['tables'] = 'paco'
    #pepe['select_modifier'] = 'DISTINCT'
    #clause1['where'] = (('campo','not in','galba','oton','vitelio','vespasiano'),)
    #clause2['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
                    #('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
                    #)
    #pepe['where']=((clause1,'OR',clause2),)
    ##pepe['group']=('julia','claudia')
    ##pepe['having']=(('campo','=','345'),)
    #pepe['base_filter']=''
    #pepe['order']=(1,(2,'DESC'),3)
    ##pepe['ltable']='sempronio'
    ##pprint(pepe)
    ##pepe['fields'] = '*'

    #print(queryConstructor(**pepe))


#print(queryConstructor(**pepe))

