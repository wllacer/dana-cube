#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
'''

from pprint import *

def ex(structure,value,defval=None):
    """
      devuelve el valor de la estructura definido por el indice value
      si no existe o es nulo devuelve None o el valor de defecto que queramos
    """
    try:
        if structure[value] is None:
            return defval
        else:
            return structure[value]
    except (KeyError ,IndexError) :
        return defval

def slicer(lista,num_elem=2,defval=''):
    """
       De una lista de tamaño arbitrario (incluye un elemento atomico) se devuelve una lista de
       un numero limitado de campos (el parametro num_elem)
       si la lista es de menor longitud se rellena con las entradas necesarias con el valor def_val
       si es mayor, el último elemento es una lista con el resto 
    """

    if not isinstance(lista,(list,tuple)):
        outlist =[lista,] + [defval for k in range(1,num_elem)]
    elif len(lista) <= num_elem :
        outlist=[elem for elem in lista] + [defval for k in range(len(lista),num_elem)]
    else:
        outlist=[lista[k] for k in range(num_elem -1)]+ [[lista[k] for k in range(num_elem -1,len(lista))],]
    return outlist

def getLevel(entrada):
    '''
       sustituto del get level como array
       el : es separador de nivel (espero que eso no entre en conflicto con textos reales TODO
       
    '''
    level = entrada.count(':')
    return level
    
def getRecordLevel(record):
    '''
       determino el ultimo nivel activo en un registro
    '''
    " ojo chequear por el valor -1 "
    if not isinstance(record, (list, tuple)):
        return 0
    elif len(record) == 1:
        return 0
    else:
        pos = len(filter(lambda x: x is not None, record)) -1
                  
    if pos < 0 :
        return 0
    else:
        return pos


def regHashFill(record,**kwargs):

    regHasher(record,**kwargs)
    if 'pholder' in kwargs or 'nholder' in kwargs or 'vholder' in kwargs:
        regFiller(record,**kwargs)

def regHashFill2D(record,**kwargs):

    regHasher2D(record,**kwargs)
    if 'pholder' in kwargs or 'nholder' in kwargs or 'vholder' in kwargs:
        regFiller(record,**kwargs)


    
def regHasher(record,**kwargs):
    
    if 'nkeys' in kwargs:
        num_components = kwargs['nkeys']
    elif 'ndesc' in kwargs:
        num_components = len(record) -kwargs['ndesc']
    else:
        num_components = len(record) -1
        
    indice = ':'.join(record[0:num_components])
    record.insert(0,indice)

def regHasher2D(record,**kwargs):
    
    indice=dict()
    for k in ('row','col'):
        dimension = kwargs[k]
        if 'nkeys' in dimension:
            num_components = dimension['nkeys']
        else:
            num_components = 1
        if 'init' in dimension :
            pos_ini = dimension['init']
        else:
            pos_ini = 0
        indice[k] = ':'.join(record[pos_ini:pos_ini+num_components])
        
    for k in ('row','col'):
        if k == 'row':
            pos_fin = 0
        else:
            pos_fin = 1
        record.insert(pos_fin,indice[k])    
        #TODO lista no consecutiva
    else:
       return

def regFiller(record,**kwargs):

    if 'pholder' in kwargs:
        pos_ini = kwargs['pholder']
    else:
        pos_ini = -1
        
    if 'nholder' in kwargs:
        num_elem = kwargs['nholder']
    else:
        return
    
    if 'vholder' in kwargs:
        value = kwargs['vholder']
    else:
        value = ''
                 
    for k in range(num_elem):
        record.insert(pos_ini,value)

