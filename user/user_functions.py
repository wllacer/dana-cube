#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Ver documentacion general de la api en ../docs/user_functions.md
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
from  util import uf_manager as ufm 
from util.record_functions import norm2List
from util.numeros import *


import config
"""
Funciones auxiliares
"""
def dhont(escanos,data):
  corte=sum(filter(None,data))*0.03
  res = [0 for i in range(len(data))]
  #aplico el corte del 3%
  tempd = [entry if entry and entry >= corte else -float('Inf') for entry in data ] #data[:] compatiblidad v3
  for i in range(0,escanos):
    maxResto = max(tempd)
    elem = tempd.index(maxResto) 
    res[elem]+=1
    tempd[elem] = data[elem]/(res[elem] +1)
  # ajuste para nulos
  for i in range(len(data)):
     if data[i] == -float('Inf'): #is None:
         res[i] = None
  # estetica sin escaños es nulo
  for i in range(len(res)):
      if res[i] == 0:
          res[i] = None
  return res

def perRatio(original,clave,oldratios,newratios):
    """
    oldratios,newratios dict key:value
    """
    oldratio = float(oldratios.get(clave,0.))
    newratio = float(newratios.get(clave,oldratio))

    if oldratio == 0.:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
        return original
    factor = newratio/oldratio
    return original*factor
    
def resultados(original,*entrada):
    partido = entrada[1]
    newratios = {partido:entrada[2]}
    datos ={
        "C's":14.0382822541147,
        "CCa-PNC":0.327843488841832,
        "DL":2.26783878634305,
        "EAJ-PNV":1.20945172577815,
        "EH Bildu":0.876122122040471,
        "EN COMÚ":3.72133439799253,
        "ERC-CATSI":2.40333940776187,
        "GBAI":0.122531253309765,
        #"IU-UPeC":3.70205679981684,
        #"MÉS":0.136074096879415,
        "NÓS":0.282583040951081,
        "PODEMOS":12.7611604239852 + 3.70205679981684 +0.136074096879415,
        "PODEMOS-COMPROMÍS":2.69120804771348,
        "PODEMOS-En Marea-ANOVA-EU":1.63769352340476,
        "PP":28.9374594531795,
        "PSOE":22.1801820596102
        }
    print(partido,original, perRatio(original,partido,datos,newratios))
    return perRatio(original,partido,datos,newratios)

def resultadosAgr(original,*entrada):
    partido = entrada[1]
    newratios = {partido:entrada[2]}
    datos ={
        "C's":14.0382822541147,
        "CCa-PNC":0.327843488841832,
        "DL":2.26783878634305,
        "EAJ-PNV":1.20945172577815,
        "EH Bildu":0.876122122040471,
        #"EN COMÚ":3.72133439799253,
        "ERC-CATSI":2.40333940776187,
        "GBAI":0.122531253309765,
        #"IU-UPeC":3.70205679981684,
        #"MÉS":0.136074096879415,
        "NÓS":0.282583040951081,
        "PODEMOS":12.7611604239852 + 0.136074096879415 + 3.70205679981684 + 2.69120804771348 +1.63769352340476 +3.72133439799253,
        #"PODEMOS-COMPROMÍS":2.69120804771348,
        #"PODEMOS-En Marea-ANOVA-EU":1.63769352340476,
        "PP":28.9374594531795,
        "PSOE":22.1801820596102
        }
    print(partido,original, perRatio(original,partido,datos,newratios))
    return perRatio(original,partido,datos,newratios)


def escanos(provincia):
    # cambi 46 son 16, 24 pasa a 4
    asignacion = {"01":4,"02":4,"03":12,"04":6,"05":3,"06":6,"07":8,"08":31,"09":4,"10":4,
                "11":9,"12":5,"13":5,"14":6,"15":8,"16":3,"17":6,"18":7,"19":3,"20":6,
                "21":5,"22":3,"23":5,"24":4,"25":4,"26":4,"27":4,"28":36,"29":11,"30":10,
                "31":5,"32":4,"33":8,"34":3,"35":8,"36":7,"37":4,"38":7,"39":5,"40":3,
                "41":12,"42":2,"43":6,"44":3,"45":6,"46":16,"47":5,"48":8,"49":3,"50":7,
                "51":1,"52":1}
    if provincia is None or provincia not in asignacion:
        return None
    else:
        return asignacion[provincia]

def escanosCat(provincia):
    # cambi 46 son 16, 24 pasa a 4
    asignacion = {"08":85,"17":17,"25":15,"43":18 }
    if provincia is None or provincia not in asignacion:
        return None
    else:
        return asignacion[provincia]
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
Funciones particulares de la BD. electoral
"""
#def senado(item):
def senado(*parms,**kwparms):
    item = parms[0]
    prov = item['key'].split(config.DELIMITER)[-1]
    tmp = [entry if entry else -float('Inf') for entry in item.getPayload() ] 
    ordtmp = [ None for k in range(item.lenPayload())]
    maximo = max(tmp)
    donde = tmp.index(maximo)
    if prov in ('51','52'):
        ordtmp[donde]=1
    else:
        ordtmp[donde]=3
        tmp[donde] = -float('Inf')
        maximo = max(tmp)
        donde = tmp.index(maximo)
        ordtmp[donde]=1
        tmp[donde] = -float('Inf')

    item.setPayload(ordtmp)
            
#def asigna(item):
def asigna(*parms,**kwparms):
    item = parms[0]
    prov = item['key'].split(config.DELIMITER)[-1]
    puestos = escanos(prov)
    if puestos is None:
        item.setPayload([ None for k in range(item.lenPayload())])
        return
    else:
        item.setPayload(dhont(puestos,item.getPayload()))

def asignaCat(*parms,**kwparms):
    item = parms[0]
    prov = item['key'].split(config.DELIMITER)[-1]
    puestos = escanosCat(prov)
    if puestos is None:
        item.setPayload([ None for k in range(item.lenPayload())])
        return
    else:
        item.setPayload(dhont(puestos,item.getPayload()))

"""
Registro de funciones y secuencias
"""
def register(contexto):
    # auxiliares
    ufm.registro_funcion(contexto,name='factoriza',entry=factoriza,aux_parm={'funAgr':resultados},type='colparm',hidden=True,api=1)
    ufm.registro_funcion(contexto,name='factorizaAgregado',entry=factoriza,aux_parm={'funAgr':resultadosAgr},type='colparm',hidden=True,api=1)
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
    
    ufm.registro_funcion(contexto,name='asigna',entry=asigna,type='item,leaf',seqnr=10,
                         text='Asignacion de escaños',
                         db='datos locales,datos light')
    ufm.registro_funcion(contexto,name='asignaCat',entry=asignaCat,type='item,leaf',seqnr=10,
                         text='Asignacion de escaños',
                         db='datos catalonia')
    ufm.registro_funcion(contexto,name='Senado',entry=senado,type='item,leaf',seqnr=11,sep=True,
                         db='datos locales')

    ufm.registro_funcion(contexto,name='borraIU',entry=consolida,
                         aux_parm={'desde':'4850','hacia':('5008','5041','5033','3736')},type='colkey',seqnr=20,
                         text='Integra UI en Podemos',
                         db='datos locales,datos light')
    ufm.registro_funcion(contexto,name='borraMes',entry=consolida,
                         aux_parm={'desde':'4976','hacia':('5008','5041','5033','3736')},type='colkey',seqnr=20,
                         text='Integra Mès en Podemos',
                         db='datos locales,datos light')
    ufm.registro_funcion(contexto,name='unPodemos',entry=consolida,
                         aux_parm={'desde':('5008','5041','5033'),'hacia':('3736',)},type='colkey',seqnr=20,
                         text='Agrupa en uno las candidaturas de Podemos',
                         db='datos locales,datos catalonia,datos light')
    ufm.registro_secuencia(contexto,name='Podemos',list=('borraIU','borraMes','unPodemos'),seqnr=23,sep=True,
                           text='Todo lo anterior',
                           db='datos locales,datos light')
    ufm.registro_secuencia(contexto,name='simul_voto',list=('Podemos','factorizaAgregado','porcentaje'),
                            seqnr=31,text='Simulacion de voto. Podemos Agregado',
                         db='datos locales,datos light')
    ufm.registro_secuencia(contexto,name='simul_agregado',
                           list=('Podemos','factorizaAgregado','asigna'),
                           seqnr=32,text='SImulacion de escaños. Podemos Agregado',
                         db='datos locales,datos light')
    ufm.registro_secuencia(contexto,name='simul',list=('borraIU','borraMes','factoriza','asigna'),sep=True,
                           seqnr=33,text='SImulacion de escaños. separado',
                         db='datos locales')

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
