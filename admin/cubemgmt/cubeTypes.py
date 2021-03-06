#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from support.datalayer.access_layer import DRIVERS, AGR_LIST 
from support.util.fechas import CLASES_INTERVALO, TIPOS_INTERVALO

"""
Documentacion funcioanl de los atributos del cubo en docs/tree_docs.md
    Definimos los tipos y si son hojas o nodos intermedios. Ojo todos los elementosde TYPE_LIST actuan, segun 
    la circunsancia de una u otra forma (son arrays de valores).
    
Practicamente todas las definiciones son obsoletas, pero las mantenemos por razones de compatiblidad (no se donde me pueden aparecer de repente)
    
"""
"""

Definiciones activas

"""
GUIDE_CLASS = ( 
    ('o','normal',),
    ('c','categorias',),
    ('h','jerarquia',),
    ('d','fecha',),
    );
LOGICAL_OPERATOR = ('in','between','like','=','!=','<','>','>=','<=','not in','not between','not like','is null','is not null')
ENUM_FORMAT = ( ('txt','texto'),('num','numerico'),('date','fecha'))
TIPO_FECHA = ('Ymd', 'Ym','Ymw','YWw') 
#FECHADOR = (('Y','Año'),('C','Cuatrimestre'),('Q','Trimestre'),('m','Mes'),('q','Quincena'),('W','Semana del Año'),('w','semana'),('d','Día'))
FECHADOR = (('Y','Año'),('m','Mes'),('W','Semana del Año'),('w','semana'),('d','Día'))
"""

definiciones probablemente obsoletas

"""
ITEM_TYPE = set([
     u'agregado',
     u'base',
     u'base filter',
     u'base_elem',
     u'case_sql',
     u'categories',
     u'class',
     u'clause',
     u'code',
     u'col',
     u'condition',
     u'connect',
     u'cubo',
     u'date filter',
     u'date range',
     u'date class',
     u'date period',
     u'dbhost',
     u'dbname',
     u'dbpass',
     u'dbuser',
     u'default',
     u'default_base',
     u'desc',
     u'driver',
     u'elem',
     u'elemento',
     u'enum_fmt',
     u'fields',
     u'filter',
     u'fmt',
     u'grouped by',
     u'guides',
     u'mask',
     u'name',
     # u'pos', no se de donde sale
     u'prod',
     u'rel_elem',
     u'link via',
     u'result',
     u'row',
     u'domain',
     u'table',
     u'type',
     u'values',
     u'vista'])

TYPE_LEAF = set([
    'agregado',
    'base_elem',
    'base filter',
    #'case_sql',
    'class',
    'code',
    'col',
    'condition',
    'cubo',
    'date class',
    'date period',
    'date range',
    'date start',
    'date end',
    'date format',
    'dbhost',
    'dbname',
    'dbpass',
    'dbuser',
    'default',
    'desc',
    'driver',
    'elem',
    'elemento',
    'enum_fmt',
    'fields',
    'filter',
    'fmt',
    'grouped by',
    'mask',
    'name',
    'rel_elem',
    'result',
    'row',
    'table',
    'type',
    'values'])
"""
    Estos tres tipos son fundamentales en isDictionary pues determinan el repliegue del arbol como cubo
"""
TYPE_ARRAY = set(['fields',
     'values',
     'code',
     'desc',
     'elem',
     'grouped_by'])

TYPE_EDIT = set (['case_sql'])

TYPE_LIST = TYPE_ARRAY | TYPE_EDIT

TYPE_DICT = set([u'base',
     u'default_base',
     'connect',
     'domain',
     'vista',])

TYPE_LIST_DICT = set([
     'categories',
     'clause',
     'guides',
     'prod',
     'link via',
     'date filter'])

COMPLEX_TYPES = TYPE_DICT | TYPE_LIST | TYPE_LIST_DICT 


"""
    son elementos que solo se definen a traves de otras pantallas o directamente en la generacion.
    NO ADD LIST de momento es inactiva
"""
NO_ADD_LIST = set([
    u'base',
    u'cubo',u'vista',u'row',u'col',u'agregado',u'elemento',
    u'base filter',u'connect',u'dbuser',u'dbhost',u'driver',u'dbname',u'dbpass',
    u'date class',u'date period',u'date range',
    u'domain',
    u'link via',u'clause'
    ])


NO_EDIT_LIST = set([u'base',u'clause'])
NO_DELETE_LIST = set([u'base',u'cubo',u'vista',u'row',u'col',u'agregado',u'elemento',
    u'base filter',u'connect',u'dbuser',u'dbhost',u'driver',u'dbname',u'dbpass',])
"""
   son los tipos que tienen valor y hay que editar
"""
EDITED_ITEMS = set([
    'agregado',
    'class',
    'code',
    'col',
    'condition',
    'cubo',
    'date class',
    'date period',
    'date range',
    'dbhost',
    'dbname',
    'dbpass',
    'dbuser',
    'default',
    'desc',
    'driver',
    'elem',
    'elemento',
    'filter',
    'fmt',
    'grouped by',
    'mask',
    'name',
    'result',
    'row',
    'table' ])

FREE_FORM_ITEMS = set([
     u'base filter',
     u'case_sql',
     u'dbhost',    # free text
     u'dbname',    # free text 
     u'dbpass',    # free text (ver como ocultar)
     u'dbuser',    # free text
     u'default',   # free text
     u'filter',    # free text
     #u'name',      # free text
     u'result',    # free text
     u'values',
    ])
STATIC_COMBO_ITEMS = dict({
     u'agregado': AGR_LIST,
     u'class': GUIDE_CLASS ,
     u'condition': LOGICAL_OPERATOR,
     u'driver': DRIVERS,
     u'enum_fmt': ENUM_FORMAT,
     u'fmt': ENUM_FORMAT,
     u'type': TIPO_FECHA,
     u'date class':[ (k,item) for k,item in enumerate(CLASES_INTERVALO) ],
     u'date range':[ (k,item) for k,item in enumerate(TIPOS_INTERVALO)],
    })

TABLE_ITEMS = set([
     u'table',     #
    ])

COLUMN_ITEMS = set([
     u'base_elem', #             field of  Reference  table
     u'code',      #             field of FK table (key)
     u'cubo',      # uno de los cubos del fichero
     u'desc',       #             field of FK table (values)
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'fields',    #
     u'grouped by',#              field of FK table or derived value ??
     u'rel_elem',  #              field of FK table
     u'table',     #
    ])

OTHER_DYNAMIC_ITEMS = set([
     u'col',       # number (a guide of base)
     u'row',       # uno de los cubos del fichero
    ])

DYNAMIC_COMBO_ITEMS = TABLE_ITEMS | COLUMN_ITEMS | OTHER_DYNAMIC_ITEMS
