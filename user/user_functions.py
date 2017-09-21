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

"""
Funciones auxiliares
"""
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

def resultados(*entrada):
    partido = entrada[1]
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


def resultadosAgr(*entrada):
    partido = entrada[1]
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
    item.setPayload(list(map(lambda entry: entry*100/suma if entry is not None else None,row)))


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



def nfactoriza(*parms,**kwparms):
    """
    Parametro por keyword = funAgr  una referencia a una funcion python que devuelve un valor para una columna concreta
    Se trata de un simulador.
    El usuario envia la variación que se desea para cada una de las columnas.
    Si no se especifica el paramtro funAgr, se modifica directamente el valor de la columna.
    Si funAgr se especifica, el valor se modifica por la razon entre el solicitado por el usuario y el devuelto por la funcion.
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
        if valor is None or valor in ('','0'):
            continue
        newratio = float(valor)
        if newratio is None:
            continue
        if item.gpi(k) is None:
            continue
        
        if funAgr:
            oldratio = funAgr(*entrada)
            if oldratio == 0:  #FIXME para evitar division por 0 pereo no tiene mucho sentido
                continue
            factor = newratio/oldratio
            item.spi(k,item.gpi(k)*factor)
        else:
            item.spi(k,item.gpi(k)*newratio / 100.0)
            
def consolida(*parms,**kwparms):
    """
    Agrega el contenido de una o varias columnas (parametro desde) en otra (parametro hacia) y borra la columna origen.
    Si el destino es una lista de columnas, se agrega a la primera que encuente con valor. Si no encuentra no se ejecuta.
    TODO: caso que no exista ninguna columna destino
    En esta versión las columnas se identifican por la clave, por lo que necesitamos esta información de las columnas
    
    tipo = item,colkey
    debe usar aux_parm para especificar los parametros desde, hacia
    opcionalmente puede ejecutarse como kwparm para especificar desde,hacia interactivamente
    """
    item = parms[0]
    column = parms[1]
    colkey = [ norm2List(data)[0] for data in column] #compatibilidad de apis por la via rapida
    
    desde=kwparms.get('desde')
    if desde is None:
        return 
    hacia=kwparms.get('hacia')
    if hacia is None:
        return

    #for idx in norm2List(desde):
        #try:
            #difunta = colkey.index(idx) +1 
        #except ValueError:
            #continue
        #for candidatura in norm2List(hacia):
            #try:
                #cakey = colkey.index(candidatura) +1
            #except ValueError:
                #continue
            #if item.itemData[cakey] is not None:  #se presentaban en la provincia
                #if item.itemData[difunta] is None:
                    #pass #deberia ser break pero bueno
                #else:
                    #item.itemData[cakey] += item.itemData[difunta]
                    #item.itemData[difunta]=None
                    #print(item.itemData[cakey],item.gpi(cakey),item.gpi(cakey -1))
                    #exit()
                #break

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
                #if item.gpi(difunta) is None:
                    #pass #deberia ser break pero bueno
                #else:
                item.spi(cakey,suma)
                item.spi(difunta,None)
                break
    pass

"""
Funciones particulares de la BD. electoral
"""
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


"""
Registro de funciones y secuencias
"""
def register(contexto):
    # auxiliares
    ufm.registro_funcion(contexto,name='factoriza',entry=nfactoriza,aux_parm={'funAgr':resultados},type='colparm',hidden=True,api=1)
    ufm.registro_funcion(contexto,name='factorizaAgregado',entry=nfactoriza,aux_parm={'funAgr':resultadosAgr},type='colparm',hidden=True,api=1)
    # funciones
    ufm.registro_funcion(contexto,name='porcentaje',entry=porcentaje,type='item',seqnr=1,
                         text='Porcentaje calculados en la fila')
    ufm.registro_funcion(contexto,name='ordinal',entry=ordinal,type='item',seqnr=2,sep=True,
                         text='ordinales')
    ufm.registro_funcion(contexto,name='asigna',entry=asigna,type='item,leaf',seqnr=10,
                         text='Asignacion de escaños')
    ufm.registro_funcion(contexto,name='Senado',entry=senado,type='item,leaf',seqnr=11,sep=True)

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
    ufm.registro_secuencia(contexto,name='simul_voto',list=('Podemos','factorizaAgregado'),
                            seqnr=31,text='Simulacion de voto. Podemos Agregado')
    ufm.registro_secuencia(contexto,name='simul_agregado',
                           list=('Podemos','factorizaAgregado','asigna'),
                           seqnr=32,text='SImulacion de escaños. Podemos Agregado')
    ufm.registro_secuencia(contexto,name='simul',list=('Podemos','factoriza','asigna'),sep=True,
                           seqnr=33,text='SImulacion de escaños. separado')
    
    #ufm.registro_secuencia(contexto,name='simul_v1_simple',
                           #list=('Podemos','factoriza','asigna'),
                           #seqnr=40,text='SImulacion de escaños. Simple. Version 1')                 
    #ufm.registro_secuencia(contexto,name='simul_v1_agregado',
                           #list=('Podemos','factorizaAgregado','asigna'),
                           #seqnr=41,text='SImulacion de escaños. Agregado Podemos. Version 1')                 

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
