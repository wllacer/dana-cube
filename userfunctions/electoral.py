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
from support.util import uf_manager as ufm 
from support.util.record_functions import norm2List
from support.util.numeros import *


import base.config as config
from user.basic import *
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
        #return original
        factor = newratio
    else:
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
        "PSOE":22.1801820596102,
        "VOX":0.24
        }
    #print(partido,original, perRatio(original,partido,datos,newratios))
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
        "PSOE":22.1801820596102,
        "VOX":0.24
        }
    #print(partido,original, perRatio(original,partido,datos,newratios))
    return perRatio(original,partido,datos,newratios)

def resultados2016(original,*entrada):
    partido = entrada[1]
    newratios = {partido:entrada[2]}
    datos ={
        "CCa-PNC" : 0.327765732005388,
        "CDC" : 2.02510828001254,
        "C's" : 13.1585880502494,
        "EAJ-PNV" : 1.20216929454199,
        "ECP" : 3.57325088501732,
        "EH Bildu" : 0.773677579848839,
        "ERC-CATSÃ" : 2.64813668241083,
        "PODEMOS-COM" : 2.76347647720761,
        "PODEMOS-EN MAREA-ANOVA-EU" : 1.45569317511938,
        "PODEMOS-IU-EQUO" : 13.5169301159882,
        "PP" : 33.2621756426915,
        "PSOE" : 22.8017605601651,
        "VOX" : 0.197623640850552       
        }
    #print(partido,original, perRatio(original,partido,datos,newratios))
    return perRatio(original,partido,datos,newratios)

def resultados2016Agr(original,*entrada):
    partido = entrada[1]
    newratios = {partido:entrada[2]}
    datos ={
        "CCa-PNC" : 0.327765732005388,
        "CDC" : 2.02510828001254,
        "C's" : 13.1585880502494,
        "EAJ-PNV" : 1.20216929454199,
        #"ECP" : 3.57325088501732,
        "EH Bildu" : 0.773677579848839,
        "ERC-CATSÃ" : 2.64813668241083,
        #"PODEMOS-COM" : 2.76347647720761,
        #"PODEMOS-EN MAREA-ANOVA-EU" : 1.45569317511938,
        "PODEMOS-IU-EQUO" : 13.5169301159882 + 3.57325088501732 + 2.76347647720761 + 1.45569317511938 ,
        "PP" : 33.2621756426915,
        "PSOE" : 22.8017605601651,
        "VOX" : 0.197623640850552       
        }
    #print(partido,original, perRatio(original,partido,datos,newratios))
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
    # auxiliares ocultas
    ufm.registro_funcion(contexto,name='factoriza',entry=factoriza,aux_parm={'funAgr':resultados},
                         type='colparm',hidden=True,api=1)
    ufm.registro_funcion(contexto,name='factorizaAgregado',entry=factoriza,aux_parm={'funAgr':resultadosAgr},
                         type='colparm',hidden=True,api=1)
    # especificas
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
