
#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import time
import sqlparse

from util.record_functions import *
from datalayer.access_layer import *
from datalayer.query_constructor import *

from PyQt5.QtWidgets import QApplication

from core import Cubo, Vista

from dictmgmt.datadict import DataDict
from filterDlg import filterDialog

from cubemgmt.cubetree import traverseTree
from util.tree import _DEPTH,_BREADTH

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
        yield tree.content[key]
        queue = tree.content[key].childItems
    else:
        queue = tree.rootItem.childItems
        #print(queue)
        #print('')
    while queue:
        yield queue[0] 
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
    DEBUG=False    
    vista = None
    mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['experimento'])
    #vista=Vista(cubo,1,2,'avg','votes_percent')
    cubo = Cubo(mis_cubos['datos light'])
    vista=Vista(cubo,5,1,'avg','votes_percent')
    summaryGuia = []
    for k in range(len(cubo.lista_guias)):
        cubo.fillGuia(k)
        guia = cubo.lista_guias[k]
        dataGuia = []
        for item in traverse(guia['dir_row']):
            dataGuia.append((item.key,item.desc))
        summaryGuia.append({'name':guia['name'],'format':guia.get('fmt','texto'),
                            'source':guia['elem'] if guia['class'] != 'c' else guia['name'] ,
                            'values':dataGuia,
                            'class':guia['class']}
                            )
    #for elem in vista.array:
        #print(elem[0].desc,elem[1].desc,elem[2])
    pprint(summaryGuia)
    #dios mio que lio 
    
    confData = cubo.definition['connect']
    confName = '$$TEMP'
    (schema,table) = cubo.definition['table'].split('.')
    if table == None:
        table = schema
        schema = ''  #definitivamente necesito el esquema de defecto
    iters = 0
    dict = DataDict(conn=confName,schema=schema,table=table,iters=iters,confData=confData) #iters todavia no procesamos
    tabInfo = []
    gotcha = False
    for item in traverseTree(dict.hiddenRoot):
        if item == dict.hiddenRoot:
           continue
        tabs = '\t'*item.depth()
        if gotcha:
            if item.isAuxiliar():
                gotcha = False
                break
            else:
                summaryGuia.append({'name':item.fqn(),'format':item.getColumnData(1),})
        if item.isAuxiliar():
            gotcha = 'True'
        
       # print(tabs,item.text(),item.getColumnData(1))
    form = filterDialog(summaryGuia,'Version experimental')
    form.show()
    if form.exec_():
        pprint(form.result)
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

def  parser():
    stmt = "partido_id = '0993'"
    parsed = sqlparse.parse(stmt)
    print(parsed)
    
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from pprint import pprint

from widgets import * 

from util.fechas import *
 
"""
  DEBUG DATA start
"""
cubo = None
from core import Cubo, Vista
from util.jsonmgr import load_cubo
from datalayer.directory import camposDeTipo
from danacube import *
        
def dateFilter():
    from core import Cubo
    from util.jsonmgr import load_cubo
    from dialogs import dateFilterDlg
    
    
    app = QApplication(sys.argv)
    #parametros = [ 1, 0, 2,3, False, False ]
    #mis_cubos = load_cubo()
    #cubo = Cubo(mis_cubos['film'])
    #vista=Vista(cubo,1,0,'sum','sakila.film.film_id')
    danacube = DanaCube()
    #descriptores = camposDeTipo("fecha",vista.cubo.db,vista.cubo.definition['table'])
    descriptores = [ item['name'] for item in danacube.recordStructure if item['format'] == 'fecha' ]
    print(descriptores)
    form = dateFilterDlg(descriptores)
    #form.show()
    if form.exec_():
        #cdata = [form.context[k][1] for k in range(len(parametros))]
        #print('a la vuelta de publicidad',cdata)
        sqlGrp = []
        #OJO form.result lleva los indices desplazados respecto de form.data
        for entry in form.result:
            if entry[1] != 0:
                intervalo = dateRange(entry[1],entry[2],periodo=entry[3])
                sqlGrp.append((entry[0],'BETWEEN',intervalo))
        if len(sqlGrp) > 0:
            print(searchConstructor('where',{'where':sqlGrp}))
        sys.exit()


if __name__ == '__main__':
    import sys
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #app = QApplication(sys.argv)
    dateFilter()
    #jerarquias()
    #parser()
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

