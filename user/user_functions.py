#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
    Tipos de funcion que reconocemos (api version 0)
        item, item,leaf, row, map basicamente identicos, solo que item,leaf solo ejecuta en items finales
            lparametro a pasar -> item
        colkey  necesito las claves de las columnas
            lparametro a pasar -> item,clave de columnas
        colparm parametros por pantalla asociados a la columna
        lparametro a pasar -> item,lista con columna y valor asociado
        rowparm parametros por pantalla asociados a la fila
        lparametro a pasar -> item,lista con fila y valor asociado
        kwparms parametros por pantalla libres
            lparamtro a pasar -> item
            kparametro a pasar -> parametros especificados
    
    Api version 1: (to do)
        lparm 0 -> item    TreeItem
        lparm 1 -> colkey  list
        lparm 2 -> rowparm
        lparm 3 -> colparm
        kparm   -> parametros auxiliares segun necesidad
    Metodos que pueden ser utilizadas para acceder a los datos del modelo (de TreeItem
    item.getPayload
    item.setPayload
    item.lenPayload
    item.getPayloadItem o item.gpi
    item.setPayloaDITEM o item.spi
    
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
from  util import uf_manager as ufm 
from util.record_functions import norm2List

def dhont(escanos,data):
    
  res = [0 for i in range(len(data))]
  tempd = [entry if entry else -float('Inf') for entry in data ] #data[:] compatiblidad v3
  
  for i in range(0,escanos):
    maxResto = max(tempd)
    elem = tempd.index(maxResto) 
    res[elem]+=1
    tempd[elem] = data[elem]/(res[elem] +1)
  # ajuste para nulos
  for i in range(len(data)):
     if data[i] == -float('Inf'): #is None:
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
        #"IU-UPeC":3.70205679981684,
        #"MÉS":0.136074096879415,
        "NÓS":0.282583040951081,
        "PODEMOS":12.7611604239852 + 3.70205679981684 +0.136074096879415,
        "PODEMOS-COMPROMÍS":2.69120804771348,
        "PODEMOS-En Marea-ANOVA-EU":1.63769352340476,
        "PP":28.9374594531795,
        "PSOE":22.1801820596102
        }
    try:
        return datos[partido]
    except KeyError:
        return None


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

#def porcentaje(item):
def porcentaje(*parms,**kwparms):
    item = parms[0]
    row = item.getPayload()
    suma=sum(filter(None,row))
    item.setPayload(list(map(lambda entry: entry*100/suma if entry is not None else None,row)))

#ef ordinal(item):
def ordinal(*parms,**kwparms):
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

#def senado(item):
def senado(*parms,**kwparms):
    item = parms[0]
    prov = item['key'].split(':')[-1]
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
    prov = item['key'].split(':')[-1]
    puestos = escanos(prov)
    if puestos is None:
        item.setPayload([ None for k in range(item.lenPayload())])
        return
    else:
        item.setPayload(dhont(puestos,item.getPayload()))


#def factoriza(item,colparm):
def factoriza(*parms,**kwparms):
    item = parms[0]
    colparm = parms[1]
    for k,entrada in enumerate(colparm):
        oldratio = resultados(entrada[0])
        if entrada[1] is None or entrada[1] in ('','0'):
            continue
        elif entrada[1] == '0.0':
            item.spi(k,0.0)
            continue
        newratio = float(entrada[1])
        if newratio is None  or oldratio == 0:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
            continue
        factor = newratio/oldratio
        
        if item.gpi(k) is None:
            continue
        item.spi(k,item.gpi(k)*factor)

#def factorizaAgregado(item,colparm):
def factorizaAgregado(*parms,**kwparms):
    item = parms[0]
    colparm = parms[1]
    for k,entrada in enumerate(colparm):
        oldratio = resultadosAgr(entrada[0])
        if entrada[1] is None or entrada[1] in ('','0'):
            continue

        newratio = float(entrada[1])
        if newratio is None  or oldratio == 0:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
            continue
        factor = newratio/oldratio
        
        if item.gpi(k) is None:
            continue

        item.spi(k,item.gpi(k)*factor)


def consolida(*parms,**kwparms):
    item = parms[0]
    colkey = parms[1]
    desde=kwparms.get('desde')
    if desde is None:
        return 
    hacia=kwparms.get('hacia')
    if hacia is None:
        return
    for idx in norm2List(desde):
        try:
            difunta = colkey.index(idx) +1
        except ValueError:
            continue
        for candidatura in norm2List(hacia):
            try:
                cakey = colkey.index(candidatura) +1
            except ValueError:
                continue
            if item.itemData[cakey] is not None:  #se presentaban en la provincia
                if item.itemData[difunta] is None:
                    pass #deberia ser break pero bueno
                else:
                    item.itemData[cakey] += item.itemData[difunta]
                    item.itemData[difunta]=None
                break

    pass

def nconsolida(*parms,**kwparms):
    item = parms[0]
    colkey = parms[1]
    rowparm = parms[2]
    colparm = parms[3]
    
    desde=kwparms.get('desde')
    if desde is None:
        return 
    hacia=kwparms.get('hacia')
    if hacia is None:
        return
    
    for idx in norm2List(desde):
        try:
            difunta = colkey.index(idx) +1
        except ValueError:
            continue
        for candidatura in norm2List(hacia):
            try:
                cakey = colkey.index(candidatura) +1
            except ValueError:
                continue
            if item.itemData[cakey] is not None:  #se presentaban en la provincia
                if item.itemData[difunta] is None:
                    pass #deberia ser break pero bueno
                else:
                    item.itemData[cakey] += item.itemData[difunta]
                    item.itemData[difunta]=None
                break

    pass
#def simula(item,colparm):
def simula(*parms,**kwparms):
    item = parms[0]
    colparm = parms[1]
    
    factoriza(item,colparm)
    asigna(item)
       
def register(contexto):
    ufm.registro_funcion(contexto,name='porcentaje',entry=porcentaje,type='item',seqnr=1,
                         text='Porcentaje calculados en la fila')
    ufm.registro_funcion(contexto,name='ordinal',entry=ordinal,type='item',seqnr=2,sep=True,
                         text='ordinales')
    ufm.registro_funcion(contexto,name='asigna',entry=asigna,type='item,leaf',seqnr=10,
                         text='Asignacion de escaños')
    ufm.registro_funcion(contexto,name='Senado',entry=senado,type='item,leaf',seqnr=11,sep=True)
    ufm.registro_funcion(contexto,name='borraCol (api 1)',entry=nconsolida,api=1,
                         aux_parm={'desde':'4850','hacia':('3736','5008','5041','5033')},type='colkey,kwparm',seqnr=20,
                         text='Mueve columnas especificas')

    ufm.registro_funcion(contexto,name='borraIU (api 1)',entry=nconsolida,api=1,
                         aux_parm={'desde':'4850','hacia':('3736','5008','5041','5033')},type='colkey',seqnr=20,
                         text='Integra UI en Podemos api 1')

    ufm.registro_funcion(contexto,name='borraIU',entry=consolida,
                         aux_parm={'desde':'4850','hacia':('3736','5008','5041','5033')},type='colkey',seqnr=20,
                         text='Integra UI en Podemos')
    ufm.registro_funcion(contexto,name='borraMes',entry=consolida,
                         aux_parm={'desde':'4976','hacia':('3736','5008','5041','5033')},type='colkey',seqnr=20,
                         text='Integra Mès en Podemos')
    ufm.registro_funcion(contexto,name='unPodemos',entry=consolida,
                         aux_parm={'desde':('5008','5041','5033'),'hacia':('3736',)},type='colkey',seqnr=20,
                         text='Agrupa en uno las candidaturas de Podemos')
    ufm.registro_secuencia(contexto,name='Podemos',list=('borraIU','borraMes','unPodemos'),seqnr=23,sep=True,
                           text='Todo lo anterior')
    ufm.registro_funcion(contexto,name='factoriza',entry=factoriza,type='colparm',hidden=True)
    ufm.registro_funcion(contexto,name='factorizaAgregado',entry=factorizaAgregado,type='colparm',hidden=True)
    ufm.registro_secuencia(contexto,name='simul_voto',list=('Podemos','factorizaAgregado'),
                            seqnr=30,text='Simulacion de voto. Podemos Agregado')
    #list=('borraIU','borraMes','unPodemos','factorizaAgregado'),
    ufm.registro_secuencia(contexto,name='simul_agregado',
                           list=('Podemos','factorizaAgregado','asigna'),
                           seqnr=31,text='SImulacion de escaños. Podemos Agregado')
    ufm.registro_secuencia(contexto,name='simul',list=('Podemos','asigna'),
                           seqnr=32,text='SImulacion de escaños. separado')
    
                     

KWARGS_LIST = { simula:(None,)}
    
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
