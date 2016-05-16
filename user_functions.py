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

def resultados(partido):
    datos ={
        "C's":14.0382822541147,
        "CCa-PNC":0.327843488841832,
        "DL":2.26783878634305,
        "EAJ-PNV":1.20945172577815,
        "EH Bildu":0.876122122040471,
        "EN COMÚ":3.72133439799253,
        "ERC-CATSI":2.40333940776187,
        "GBAI":0.122531253309765,
        "IU-UPeC":3.70205679981684,
        "MÉS":0.136074096879415,
        "NÓS":0.282583040951081,
        "PODEMOS":12.7611604239852,
        "PODEMOS-COMPROMÍS":2.69120804771348,
        "PODEMOS-En Marea-ANOVA-EU":1.63769352340476,
        "PP":28.9374594531795,
        "PSOE":22.1801820596102
        }
    return datos[partido]

def resultadosAgr(partido):
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
    try:
        return datos[partido]
    except KeyError:
        return None


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

def asigna(item):
    prov = item['key'].split(':')[-1]
    puestos = escanos(prov)
    if puestos is None:
        item.itemData[1:]= [ None for k in range(len(item.itemData)-1)]
        return
    else:
        item.itemData[1:] = dhont(puestos,item.itemData[1:])


def factoriza(item,colparm):
    for k,entrada in enumerate(colparm):
        oldratio = resultados(entrada[0])
        if entrada[1] is None or entrada[1] in ('','0'):
            continue
        print(entrada[1])
        newratio = float(entrada[1])
        if newratio is None  or oldratio == 0:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
            continue
        factor = newratio/oldratio
        
        if item.itemData[k +1] is None:
            continue
        print(k,item.itemData[0],item.itemData[k+1],factor)
        item.itemData[k+1] = item.itemData[k+1]*factor

def factorizaAgregado(item,colparm):
    for k,entrada in enumerate(colparm):
        oldratio = resultadosAgr(entrada[0])
        if entrada[1] is None or entrada[1] in ('','0'):
            continue
        print(entrada[1])
        newratio = float(entrada[1])
        if newratio is None  or oldratio == 0:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
            continue
        factor = newratio/oldratio
        
        if item.itemData[k +1] is None:
            continue
        print(k,item.itemData[0],item.itemData[k+1],factor)
        item.itemData[k+1] = item.itemData[k+1]*factor

def unPodemos(item,colkey):
    potemos = colkey.index('3736')+1
    for candidatura in ('5008','5041','5033'):
        cakey = colkey.index(candidatura) +1
        if item.itemData[cakey] is None:
            continue
        if item.itemData[potemos] is None:
            item.itemData[potemos] = item.itemData[cakey]  #solo uno puede ser nulo
        else:
            item.itemData[potemos] += item.itemData[cakey]  #solo uno puede ser nulo
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

def borraMes(item,colkey):
    difunta = colkey.index('4976') +1
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
    #asigna(item)

def simula(item,colparm):
    factoriza(item,colparm)
    asigna(item)
            
USER_FUNCTION_LIST=( ('Porcentajes calculados en la fila',((porcentaje,'row',),)),
                     ('Asignacion de escaños',((asigna,'item','leaf'),)),
                     ('Integra IU en Podemos',((borraIU,'colkey',),)),
                     ('Integra Mès en Podemos',((borraMes,'colkey',),)),
                     ('Solo presenta una columna de Podemos',((unPodemos,'colkey',),)),
                     ('Todo lo anterior',(
                                           (borraIU,'colkey',),
                                           (borraMes,'colkey'),
                                           (unPodemos,'colkey',),
                                           (asigna,'item',)
                                         )),
                     ('Simulacion resultados',(
                                           (borraIU,'colkey',),
                                           (borraMes,'colkey',),
                                           (unPodemos,'colkey',),
                                           (factorizaAgregado,'colparm',),
                                           (asigna,'item','leaf'),
                                           )),
              )
KWARGS_LIST = { simula:(None,)}
    
row=[15,26,74,66,None,24]
print(USER_FUNCTION_LIST[0][1][0][0](row))
