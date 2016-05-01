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
DELIMITER=':'

def norm2List(entrada):
    """
       devuelve una entrada que puede ser una lista o un escalar como lista siempre
       
    """
    if isinstance(entrada,(list,tuple)):
       return entrada
    else:
       return [entrada ,]
      
def norm2String(entrada,separador=', '):
    """
       devuelve una entrada que puede ser una lista o un escalar como escalar siempre con un separador
       
    """
    if isinstance(entrada,(list,tuple)):
       return separador.join(entrada)
    else:
       return entrada
   
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
       si la lista es de menor longitud se rellena con las entradas necesarias con el valor 'defval'
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
    level = entrada.count(DELIMITER)
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
        
    indice = DELIMITER.join(record[0:num_components])
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
        indice[k] = DELIMITER.join(record[pos_ini:pos_ini+num_components])
        
    for k in ('row','col'):
        if k == 'row':
            pos_fin = 0
        else:
            pos_fin = 1
        record.insert(pos_fin,indice[k])    
        #TODO lista no consecutiva
    else:
       return

def regTree(record,**kwargs):
    triad=[None,None,None]
    regHasher2D(record,**kwargs)
    triad[2]=record[-1] #datos
    try:
        triad[0]=kwargs['rdir'][record[0]] #row parent
        triad[1]=kwargs['cdir'][record[1]] #col parent
        del record[3:]
        for k in range(3):
          record[k]=triad[k]
    except KeyError:
        del record[:]
    
def regFiller(record,**kwargs):

    if 'pholder' in kwargs:
        pos_ini = kwargs['pholder']
    else:
        pos_ini = 1
        
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

def row2dict(row,keys):
  '''
    Convierte tupla en diccionario
  '''
  dic = dict()
  for idx in range(len(row)):
    dic[keys[idx]]=row[idx]
  return dic

def dict2row(dict,keys):
  '''
    Convierte diccionario en tupla
  '''
  row = [None for k in range(len(keys))]
  for idx,clave in enumerate(keys):
    if clave in dict:  #si la clave no existe lo dejamos en nulo
      row[idx]=dict[idx]
  return row

def extrae(datos,campo):
  '''
    extrae columnas de un diccionario o lista bidimensional
    salida en forma de lista
    
    Codigo mejorable ¿?
  '''
  
  if isinstance(campo,(list,tuple)):
     if isinstance(datos,dict):  
       return [[datos[k][m] for m in campo] for k in sorted(datos)]
     elif isinstance(datos,(list,tuple)) and isinstance(datos[0],dict):
       return [[datos[k][m] for m in campo] for k in range(len(datos))]
     elif isinstance(datos,(list,tuple)):
       return [[datos[k][int(m)] for m in campo] for k in range(len(datos))]
  else: 
    if isinstance(datos,dict):  
      return [datos[k][campo] for k in sorted(datos)]
    elif isinstance(datos,(list,tuple)) and isinstance(campo,(int,long)):
      return [datos[k][campo] for k in range(len(datos))]
    elif isinstance(datos,(list,tuple)) and campo.isdigit():
      return [datos[k][int(campo)] for k in range(len(datos))]
    elif isinstance(datos,(list,tuple)) and isinstance(datos[0],dict):
      return [datos[k][campo] for k in range(len(datos))]
    else:
      print ('error de asignacion')

def trans(vector,reglas):
  '''
    trans transforma un vector de acuerdo con unas reglas
    
    transformacion = +regla
    regla = {delta:funcion,**parmlist}|{o:origen,(d:destino|v:variacion)}|{map:funcion,**parmlist}
    origen = index|index,factor
    destino = index|index,factor
    variacion=factor 
    
    delta  llama a una funcion que debe recibir el vector original y los parametros que se desee como diccionario
            retorna un vector de diferencias (positivo aunemta,negativo disminuye)
    map    invoca list(map) con los parametros que se indiquen      
            
    map puede incluirse como una opcion. TODO
    find y reduce no por cambiar el tamaño del array. NO es mi intencion que esta función lo modifique
  '''
  if not isinstance(reglas,(list,tuple)):
    print ( 'trans necesita una lista como parametro')
    exit()
    
  vector_salida = [vector[i] for i in range(len(vector)) ]

  for a in reglas:
      if isinstance(a,(list,tuple)):
        vector_salida = trans(vector_salida,a)
      else:
        vector_salida=ker_trans(vector_salida,a)
  return vector_salida

def ker_trans(vector,regla):
  vector_salida = [vector[i] for i in range(len(vector)) ]

  base_data = 0
  # proceso la entrada 

  if  'delta' in regla:
    funcion = regla['delta']
    parm_dict = dict()
    for key in regla :
      if key == 'delta':
        continue
      parm_dict[key] = regla[key]
    
    a_qty_delta = funcion(vector,**parm_dict)
    for i in range(len(a_qty_delta)):
      vector_salida[i] += a_qty_delta[i] 
  else:
      
    if isinstance(regla['o'],(int,long)):
      k_entrada = (regla['o'],1.0)
    else :
      k_entrada = regla['o']

    de_idx = k_entrada[0]
    de_qty = vector[de_idx]* k_entrada[1]  #integer division. es lo que me interesa en este caso
    # proceso la salida
    if 'd' in regla:
      if isinstance(regla['d'],(int,long)):
        k_salida = (regla['d'],1.0)
      else :
        k_salida = elem['d']

      a_idx = k_salida[0]
      a_qty = de_qty * k_salida[1]
      vector_salida[de_idx] = vector_salida[de_idx] - de_qty
      vector_salida[a_idx] += a_qty
    elif 'v' in regla:  # variacion en el mismo elemento
      a_idx = de_idx
      a_qty = de_qty * regla['v'] 
      vector_salida[de_idx] += a_qty
    else:
      pass
  return vector_salida  

