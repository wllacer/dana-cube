#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
'''
Ver documentacion general de la api en ../docs/user_functions.md
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
from support.util import uf_manager as ufm 
from support.util.record_functions import norm2List
from support.util.numeros import *


import base.config as config

"""
Funciones de usuario genéricas

"""

def porcentaje(*parms,**kwparms):
    """
    Convierte a porcentajes sobre el total de esta fila.
    
    tipo = item
    """
    item = parms[0]
    row = item.getPayload()
    suma=sum(filter(None,row))
    item.setPayload(list(map(lambda entry: entry*100./suma if entry is not None else None,row)))


def ordinal(*parms,**kwparms):
    """
    Convierte a numero de orden dentro de la fila. (el primero es el mayor). 
    
    tipo = item
    """
    item = parms[0]
    """
        para ser compatible con python3 he tenido que sustituir los nulos por -Inf
    """
    tmp = [entry if entry else -float('Inf') for entry in item.getPayload() ]  #compatibilidad python 3
    ordtmp = [ None for k in range(item.lenPayload())]
    round = 1
    while round <= item.lenPayload():
        maximo = max(tmp)
        if maximo == -float('Inf'): #is None:
            break
        else:
            donde = tmp.index(maximo)
            ordtmp[donde]=round
            tmp[donde] = -float('Inf') #None
            round += 1
    item.setPayload(ordtmp)


def factoriza(*parms,**kwparms):
    """
    Parametro por keyword = funAgr  una referencia a una funcion python que devuelve un valor para una columna concreta
    funAgr(valor_actual,referencia de la columna compatible con colparm)
    Se trata de un simulador.
    El usuario envia la variación que se desea para cada una de las columnas.
    Si no se especifica el paramtro funAgr, el valor de entrada para cada columna se considera el porcentaje de variacion
    Si funAgr se especifica, el valor sera el devuelto por la función
    Si se desea que el valor resultante sea 0, debe ponerse 0.0 en la entrada de la columna, no 0
    En esta versión la variación se define implicitamente en porcentajes

    tipo = item,colparm
    Utilizar aux_parm para referenciar la función .
    
    TODO. El comportamiento cuando no existe valor previo no es realista
    """

    item = parms[0]
    colparm = parms[3]
    funAgr = kwparms.get('funAgr')
    
    for k,entrada in enumerate(colparm):
        codigo = entrada[0]
        desc = entrada[1]
        valor = entrada[2]            
        base = item.gpi(k)
        
        if not base:
            continue

        if valor is None or valor in ('','0'):
            continue
                
        if funAgr:
            newvalue = funAgr(base,*entrada)
            if newvalue:
                item.spi(k,newvalue)
        else:
                
            if valor[-1] == '%':
                dato = base * s2n(valor[:-1])/100
            else:
                dato = s2n(valor)
            item.spi(k,dato)
            
def consolida(*parms,**kwparms):
    """
    Agrega el contenido de una o varias columnas (parametro desde) en otra (parametro hacia) y borra la columna origen.
    Si el destino es una lista de columnas, se agrega a la primera que encuente con valor. Si no encuentra no se ejecuta.
    caso que no exista ninguna columna destino con valor se agrega a la última de la lista
    En esta versión las columnas se identifican por la clave, por lo que necesitamos esta información de las columnas
    
    tipo = item,colkey
    debe usar aux_parm para especificar los parametros
        desde, columna(s) origen
        hacia, columna(s) destino
        searchby = (key|value) criterio de busqueda. defecto key
    opcionalmente puede ejecutarse como kwparm para especificar desde,hacia interactivamente
    """
    item = parms[0]
    column = parms[1]
    if kwparms.get('searchby','key') == 'key':
        colkey = [ norm2List(data)[0] for data in column] #compatibilidad de apis por la via rapida
    elif kwparms.get('searchby') == 'value':
        colkey = [ norm2List(data)[1] for data in column] #compatibilidad de apis por la via rapida
    else:
        return
    
    desde=kwparms.get('desde')
    if desde is None:
        return 
    hacia=kwparms.get('hacia')
    if hacia is None:
        return
    difuntas = []
    for idx in norm2List(desde):
        try:
            difunta = colkey.index(idx)
            difuntas.append(difunta)
        except ValueError:
            continue
        if not item.gpi(difunta):
            continue
        for candidatura in norm2List(hacia):
            try:
                cakey = colkey.index(candidatura)
            except ValueError:
                continue
            suma = item.gpi(difunta)
            if item.gpi(cakey) is not None:  #se presentaban en la provincia
                suma += item.gpi(cakey)    
                item.spi(cakey,suma)
                item.spi(difunta,None)
                break
        else:  #cuando no hay candidaturas destino. va a la ultima de la lista
            cakey = colkey.index(candidatura)
            item.spi(cakey,item.gpi(difunta))
            item.spi(difunta,None)
    pass
    # borra la columna original  TODO documentar el uso de tree
    if 'tree' in kwparms:
        for entrada in difuntas:
            kwparms['tree'].hideColumn(entrada +1)
            
def transfiere(*parms,**kwparms):
    """
    Agrega parte del contenido de una o varias columnas (parametro desde) en otra (parametro hacia) y borra la columna origen.
    Si el destino es una lista de columnas, se agrega a la primera que encuente con valor. Si no encuentra no se ejecuta.
    caso que no exista ninguna columna destino con valor se agrega a la última de la lista
    En esta versión las columnas se identifican por la clave, por lo que necesitamos esta información de las columnas
    
    tipo = item,colkey
    debe usar aux_parm para especificar los parametros
        desde, columna(s) origen
        hacia, columna(s) destino
        porcentaje, porcentaje de la columna origen que va al destino. Sin porcentaje se asume el 100%
        searchby = (key|value) criterio de busqueda. defecto key
    opcionalmente puede ejecutarse como kwparm para especificar desde,hacia interactivamente
    """
    item = parms[0]
    column = parms[1]
    if kwparms.get('searchby','key') == 'key':
        colkey = [ norm2List(data)[0] for data in column] #compatibilidad de apis por la via rapida
    elif kwparms.get('searchby') == 'value':
        colkey = [ norm2List(data)[1] for data in column] #compatibilidad de apis por la via rapida
    else:
        return
    
    desde=kwparms.get('desde')
    if desde is None:
        return 
    porcentaje=kwparms.get('porcentaje')
    if porcentaje is None or porcentaje == '100':
        porcentaje = 1.0
    else:
        porcentaje = float(porcentaje)/100.
        
    hacia=kwparms.get('hacia')
    if hacia is None:
        return

    for idx in norm2List(desde):
        try:
            difunta = colkey.index(idx)
        except ValueError:
            continue
        if not item.gpi(difunta):
            continue
        for candidatura in norm2List(hacia):
            try:
                cakey = colkey.index(candidatura)
            except ValueError:
                continue
            suma = item.gpi(difunta)
            if type(suma) == int:
                pasa = int(suma * porcentaje)
            else:
                pasa = suma * porcentaje
            resto = suma - pasa
                
            if item.gpi(cakey) is not None:  #se presentaban en la provincia
                pasa += item.gpi(cakey)    
                item.spi(cakey,pasa)
                item.spi(difunta,resto)
                break
        else:  #cuando no hay candidaturas destino. va a la ultima de la lista
            suma = item.gpi(difunta)
            if type(suma) == int:
                pasa = int(suma * porcentaje)
            else:
                pasa = suma * porcentaje
            resto = suma - pasa
            cakey = colkey.index(candidatura)
            item.spi(cakey,pasa)
            item.spi(difunta,resto)
    pass

def seed(*parms,**kwparms):
    """
    TODO doc
    """
    item = parms[0]
    column = parms[1]
    if kwparms.get('searchby','key') == 'key':
        colkey = [ norm2List(data)[0] for data in column] #compatibilidad de apis por la via rapida
    elif kwparms.get('searchby') == 'value':
        colkey = [ norm2List(data)[1] for data in column] #compatibilidad de apis por la via rapida
    else:
        return
    columna = colkey.index(kwparms.get('destino'))
    base = kwparms.get('valor inicial')

    if base[-1] == '%':
        suma = sum(filter(None,item.getPayload()))
        dato = suma * s2n(base[:-1])/100
    elif base[-1] == 'P': #promedio:
        dato = s2n(base[:-1])*avg(filter(None,item.getPayload()))
    elif base[-1] == 'M': #mediana:
        dato = s2n(base[:-1])*median(filter(None,item.getPayload()))
    else:
        dato = s2n(base)
    item.spi(columna,dato)
    
def exec_map(*parms,**kwparms):
    """
    Ejecuta un map sobre la lista. 
    Con o sin parametros si estos se ajustan al mismo estandar de las funciones de usuario
    """
    function = kwparms.get('function')
    if not function:
        return 
    item = parms[0]
    item.setPayload(list(map(function,item.getPayload())))
    ### esto esta comentado por no tener experiencia real con ello
    #if any(parm[k] is not None for k in range(1,len(parms))) or kwparms is not None:
        #item.setPayload(list(map(lambda p: function(p, *parms,**kwparms), item.getPayload())))
    #else:    
        #item.setPayload(list(map(function,item.getPayload()))
"""
FUnciones auxiliares de agregacion
"""

"""
Registro de funciones y secuencias
"""
def register(contexto):
    # auxiliares
    # funciones
    ufm.registro_funcion(contexto,name='porcentaje',entry=porcentaje,type='item',seqnr=1,
                         text='Porcentaje calculados en la fila')
    ufm.registro_funcion(contexto,name='ordinal',entry=ordinal,type='item',seqnr=2,
                         text='Número de orden descendente en la fila')
    ufm.registro_funcion(contexto,name='agrupa',entry=consolida,type='colkey,kwparm',seqnr=3, 
                         aux_parm= { 'desde':None,'hacia':None,'searchby':'value'},
                         text='fusiona columnas')
    ufm.registro_funcion(contexto,name='transfiere',entry=transfiere,type='colkey,kwparm',seqnr=3, 
                         aux_parm= { 'desde':None,'hacia':None,'porcentaje':100,'searchby':'value'},
                         text='transfiere parcialmente columnas')
    ufm.registro_funcion(contexto,name='inicializa',entry=seed,type='colkey,kwparm',seqnr=3, 
                         aux_parm= {'destino':None, 'valor inicial':0,'searchby':'value'},
                         text='inicializa columna a un valor fijo')
    #ufm.registro_funcion(contexto,name='simula',entry=factoriza,type='colparm',seqnr=4,sep=True,
                         #text='Realiza simulaciones')
    
KWARGS_LIST = { }
    
if __name__ == '__main__':
    row=[15,26,74,66,None,24]

    data = [33.03,
    22.66,
    21.1,
    13.05,
    #2.63,
    #2.01,
    #1.2,
    ]
    totescanos = 350
    print(dhont(totescanos,data))
