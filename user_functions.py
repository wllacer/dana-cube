#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   code is based on the simpletreemodel sample of the Qt/PyQt documentation,
           which is BSD licensed by Nokia and successors, and Riverbank
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

def dhont(escanos,data):
    
  res = [0 for i in range(len(data))]
  tempd = data [:]
  
  for i in range(0,escanos):
    maxResto = max(tempd)
    elem = tempd.index(maxResto) 
    res[elem]+=1
    tempd[elem] = data[elem]/(res[elem] +1)
  # ajuste para nulos
  for i in range(len(data)):
     if data[i] is None:
         res[i] = None
         
  return res

def escanos(provincia):
    asignacion = {"01":4,"02":4,"03":12,"04":6,"05":3,"06":6,"07":8,"08":31,"09":4,"10":4,
                "11":9,"12":5,"13":5,"14":6,"15":8,"16":3,"17":6,"18":7,"19":3,"20":6,
                "21":5,"22":3,"23":5,"24":5,"25":4,"26":4,"27":4,"28":36,"29":11,"30":10,
                "31":5,"32":4,"33":8,"34":3,"35":8,"36":7,"37":4,"38":7,"39":5,"40":3,
                "41":12,"42":2,"43":6,"44":3,"45":6,"46":15,"47":5,"48":8,"49":3,"50":7,
                "51":1,"52":1}
    if provincia is None or provincia not in asignacion:
        return None
    else:
        return asignacion[provincia]

def porcentaje(row):
    suma=sum(filter(None,row))
    return list(map(lambda item: item*100/suma if item is not None else None,row))

def simula(item):
    prov = item['key'].split(':')[-1]
    puestos = escanos(prov)
    if puestos is None:
        item.itemData[1:]= [ None for k in range(len(item.itemData)-1)]
        return
    else:
        item.itemData[1:] = dhont(puestos,item.itemData[1:])
  
def unPodemos(item,colkey):
    potemos = colkey.index('3736')+1
    for candidatura in ('5008','5041','5033'):
        cakey = colkey.index(candidatura) +1
        if item.itemData[cakey] is None:
            continue
        item.itemData[potemos] = item.itemData[cakey]  #solo uno puede ser nulo
        item.itemData[cakey]=None
    #print(item.itemData[potemos],item.orig_data[potemos])    
    #print(item.itemData[cakey],item.orig_data[cakey])    
    
def borraIU(item,colkey):
    difunta = colkey.index('4850') +1
    if item.itemData[difunta] is None:
        return
    for candidatura in ('3736','5008','5041','5033'):
        cakey = colkey.index(candidatura) +1
        if item.itemData[cakey] is not None:  #se presentaban en la provincia
            if item.itemData[difunta] is None:
                pass #deberia ser break pero bueno
            else:
                item.itemData[cakey] += item.itemData[difunta]
                item.itemData[difunta]=None
            break
        
def newScenario(item,colkey):
    borraIU(item,colkey)
    unPodemos(item,colkey)
    simula(item)
            
USER_FUNCTION_LIST=( (porcentaje,'Porcentajes calculados en la fila','row'),
                     (simula,'simulacion de escaños','item'),
                     (borraIU,'Integra IU en Podemos','colkey'),
                     (unPodemos,'Solo presenta una columna de Podemos','colkey'),
                     (newScenario,'Todo lo anterior','colkey'),
              )

    
row=[15,26,74,66,None,24]
print(USER_FUNCTION_LIST[0][0](row))
