#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datalayer.access_layer import DRIVERS, AGR_LIST 

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
     u'name',
     u'pos',
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

TYPE_DICT = set([u'base',
     u'default_base',
     'connect',
     u'default_start',
     'domain',
     'vista'])

TYPE_LIST = set(['case_sql',
     'fields',
     'values'])

NO_ADD_LIST = set([
    u'cubo',u'vista',u'row',u'col',u'agregado',u'elemento',
    u'base filter',u'connect',u'dbuser',u'dbhost',u'driver',u'dbname',u'dbpass',
    ])
TYPE_LIST_DICT = set([
     'categories',
     'clause',
     'guides',
     'prod',
     'link via'])

COMPLEX_TYPES = TYPE_DICT | TYPE_LIST | TYPE_LIST_DICT

GUIDE_CLASS = ( 
    ('o','normal',),
    ('c','categorias',),
    ('h','jerarquia',),
    ('d','fecha',),
    );
LOGICAL_OPERATOR = ('in','not in','between','not between','=','!=','<','>','>=','<=')
ENUM_FORMAT = ( ('t','texto'),('n','numerico'),('d','fecha'))
TIPO_FECHA = ('Ymd', 'Ym','Ymw','YWw') 

EDITED_ITEMS = set([
     u'agregado',  # AGR_LIST
     u'base_elem', #             field of  Reference  table
     u'base filter', # free text
     u'class',     # GUIDE_CLASS *
     u'code',      #             field of FK table (key)
     u'col',       # number (a guide of base)
     u'condition', # LOGICAL_OPERATOR
     u'cubo',      # uno de los cubos del fichero
     u'dbhost',    # free text
     u'dbname',    # free text 
     u'dbpass',    # free text (ver como ocultar)
     u'dbuser',    # free text
     u'default',   # free text
     u'desc',       #             field of FK table (values)
     u'driver',   # DRIVERS
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'enum_fmt',  # ENUM_FORMAT
     u'filter',    # free text
     u'fmt',       # en prod = FORMATO, en categories ENUM_FORMAT
     u'grouped by',#              field of FK table or derived value ??
     u'name',      # free text
     u'rel_elem',  #              field of FK table
     u'result',    # free text
     u'row',       # number (a guide of base)
     u'table',     # table ...
     u'type'])     # TIPO_FECHA

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
    })

DYNAMIC_COMBO_ITEMS = set([
     u'base_elem', #             field of  Reference  table
     u'code',      #             field of FK table (key)
     u'col',       # number (a guide of base)
     u'cubo',      # uno de los cubos del fichero
     u'desc',       #             field of FK table (values)
     u'elem',      #              field of table, or derived value 
     u'elemento',  # FIELD of cube
     u'fields',
     u'grouped by',#              field of FK table or derived value ??
     u'rel_elem',  #              field of FK table
     u'row',       # uno de los cubos del fichero
     u'table',
    ])
