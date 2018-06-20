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
import re

from pprint import *
from copy import deepcopy
from support.util.cadenas import mergeStrings

import base.config as config

def norm2List(entrada):
    """
       devuelve una entrada que puede ser una lista o un escalar como lista siempre
       Solucion para los parentesis obtenida gracias a
       stackoverflow.com/questions/1648537/how-to-split-a-string-by-commas-positioned-outside-of-parenthesis
       Falla con parentesis dentro de parentesis.
       
    """
    if not entrada:
        return []
    if isinstance(entrada,(list,tuple)):
       return entrada
    elif '(' in entrada:
        return re.split(r',\s*(?=[^)]*(?:\(|$))', entrada)

    else:
       return re.split(r', *',entrada)
      
def norm2String(entrada,separador=', '):
    """
    devuelve una entrada que puede ser una lista o un escalar como escalar siempre con un separador
    Mantiene las instancias sin valor (pero no nulas).
    Si no se desea ese comportamiento use util.cadenas.mergeStrings
    """
    
    if not entrada:
        return ''
    if isinstance(entrada,(list,tuple)):
        if isinstance(entrada[0],(int,float)):
            return separador.join([str(elem) for elem in entrada])
        else:
            return separador.join(entrada)
    elif isinstance(entrada,set):
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
    level = entrada.count(config.DELIMITER)
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
    try:
        #GENERADOR. Vaya Chapu
        trecord = list(map(str,record[0:num_components]))
        indice = config.DELIMITER.join(trecord)
        #indice = config.DELIMITER.join(record[0:num_components])
    except TypeError:
        print('type error')
        print(num_components)
        pprint(record)
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
        trecord = list(map(lambda x:str(x).replace(config.DELIMITER,'/'),record[pos_ini:pos_ini+num_components]))
        indice[k] = config.DELIMITER.join(trecord)
        #indice[k] = config.DELIMITER.join(record[pos_ini:pos_ini+num_components])
        
    for k in ('row','col'):
        if k == 'row':
            pos_fin = 0
        else:
            pos_fin = 1
        record.insert(pos_fin,indice[k])    
        #TODO lista no consecutiva
    else:
       return
   
def regTreeGuide(record,**kwargs):
    from PyQt5.QtCore import Qt
    """
    convertir el registro en una tripleta (row,col,valor) con row y col los items de CubeItemModel)
    """
    dictionaries = ('rdir','cdir')
    triad = [None,None,record[-1]]
    for k,dim in enumerate(('row','col')):
        dimension = kwargs[dim].get('nkeys',1)
        if dim == 'row':
            pos_ini = 0
        else:
            pos_ini = kwargs['row'].get('nkeys',1)
        krecord = list(map(lambda x:str(x),record[pos_ini:pos_ini+dimension]))
        parent = kwargs[dictionaries[k]].searchHierarchy(krecord)
        if parent is None:
            #print(record,dim,pos_ini,dimension,'falla')
            del record[:]
            return
        else:
            triad[k] = parent
    record[0:3] = triad
    del record[3:]
    
def regTree(record,**kwargs):
    triad=[None,None,None]
    regHasher2D(record,**kwargs)
    triad[2]=record[-1] #datos
    onerror = False
    try:
        triad[0]=kwargs['rdir'][record[0]] #row parent
        triad[1]=kwargs['cdir'][record[1]] #col parent
        del record[3:]
        for k in range(3):
          record[k]=triad[k]
    except KeyError:
        #print('Egog',triad,record)
        del record[:]

def regTree1D(record,**kwargs):
    duad=[None,None]
    regHasher(record,**kwargs)
    duad[1]=record[-1] #datos
    try:
        duad[0]=kwargs['dir'][record[0]] #col parent
        del record[2:]
        for k in range(2):
          record[k]=duad[k]
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
      row[idx]=dict.get(clave)
    #if clave in dict:  #si la clave no existe lo dejamos en nulo
      #row[idx]=dict[idx]
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
        k_salida = regla['d']

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

def defaultFromContext(context,*args,**kwargs):
    if isinstance(context,dict):
        results = dict()
        results = deepcopy(kwargs)
        for item in context:
            results[item] = kwargs.get(item,context[item])
    else:
        results = []
        for k,item in enumerate(context):
            if k >= len(args):
                break
            if args[k]:
                results.append(args[k])
            else:
                results.append(context[k])
    return results

def osSplit(texto,delim=','):
    """
    Old style split navegando toda la cadena
    La version basada en re (norm2List) no funciona si los agrupadores no son parentesis y tampoco si estan anidados
    No se sustituye porque osSplit es mucho mas cara que norm2List  (en una cadena normalita 41 uS frente a 7 uS (la u el el micro)
    en el uso que he dado hasta ahora norm2List me vale 
    
    WIP
    """
    openclose = { '(':')','[':']','{':'}' }
    ani = 0
    literal = None
    resultado = []
    ultpos = 0
    stack = []
    for k in range(len(texto)):
        """
        orden de precedencia --> comillas
                                                 parentesis y barras ahora mismo se consideran equivalentes. Esto funciona de milagro
                                                 separadores
        """
        # las comillas no funciona el tema del stack porque pueden aparecer no apareadas siempre que alternen 
        # uso una logica "ternaria" o asi None -> no hay texto, Literal hay y es el delimitador que sea
        if texto[k] in ("'",'"'):
            if literal == texto[k]:
                literal = None
            elif literal:
                pass
            else:
                literal = texto[k]
        # para los pares de caracteres uso un contador de anidacion y un stack con los cars. de apertura
        # al detectar un cierre saco la ultima entrada del stack y veo si es el correspondiente cierre.
        # el contador me evita consultar el stack vacio y me permite verificar el cierre al final (podria hacerlo con len(stack)
        # pero ...
        if texto[k] in ('(','[','{') and not literal:
            ani += 1
            stack.append(texto[k])
        elif texto[k] in (')',']','}') and not literal:
            ani -= 1
            if ani < 0 or openclose[stack.pop()] != texto[k]:
                raise ValueError('Parentesis no balanceados en {}'.format(texto))
        elif texto[k] == delim:
            if ani == 0 and literal is None:  #debe ser cero pero nunca se sabe
                resultado.append(texto[ultpos:k])
                ultpos = k +1
    else:
        if ani != 0 or literal is not None:
            raise ValueError('Parentesis o cadenas de texto no balanceados en {}'.format(texto))
        else:
            resultado.append(texto[ultpos:])
    return resultado

if __name__ == '__main__':
    #prueba de funciones
    pass
