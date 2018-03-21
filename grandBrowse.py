#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

TODO
    Falta incluir los filtros del cubo
'''

import config

#from util.record_functions import *
#from util.tree import *
#from util.fechas import *

from datalayer.access_layer import *
from datalayer.query_constructor import *
from core import *

#from util.numeros import stats,num2text

#from datalayer.datemgr import getDateEntry, getDateIndexNew
from pprint import *

from util.decorators import *

import time

from util.jsonmgr import dump_structure,dump_json

def toNormString(entrada,placeholder='_'):
    """
    Funcion para convertir una cadena en su "equivalente" ASCII. Funciona para textos españoles, al menos. 
    FIXME No acaba de salir bien con caracteres ascii expandidos tipo (Þ)
    Pensada para convertir cualquier texto en nombre de campo SQL
    Eliminamos diacriticos,
    Convertimos todo lo que no sea texto o numerico a '_' como marcador
    Y todo a minuscula
    
    """
    import unicodedata
    norm_form = unicodedata.normalize('NFD',entrada)
    resultado = ""
    for char in norm_form:
        if unicodedata.category(char) == 'Lu': #string uppercase
            resultado += char.lower()
        elif unicodedata.category(char) in ('Ll','Nd','Nl','No'):
            resultado += char
        elif unicodedata.combining(char):
            pass
        else:
            resultado += placeholder

    return resultado
    


def changeTable(string,oldName,newName):
    import re
    
 
    matchpattern=r'(\W*\w*\.)?('+oldName+')'
    filematch = matchpattern+'\W'
    filerepl  = r'\1'+ newName
    fieldmatch=matchpattern+r'(\..*)'
    fieldrepl = r'\1' + newName +r'\3'
    while re.search(fieldmatch,string):# 
        string = re.sub(fieldmatch,fieldrepl,string)
    if '.' in oldName:   #es necesario todavia ??
        return changeTable(string,oldName.split('.')[-1],newName)
    else:
        return string
            
def fullQualifyInString(string,tableName):
    import re

    sufix = tableName.split('.')[-1]
    matchpattern=r'([^\w\.])('+sufix+')'  
    filematch = matchpattern+r'(\.\w*)'
    filerepl = r'\1'+tableName+r'\3'
 
    if re.search(filematch,string): 
        string = re.sub(filematch,filerepl,string)
        
    return string
    

def fieldFqN(field,table):
    """
    table is suposed to be fqn
    """
    if  '(' in field or ' ' in field:
        # aqui se entiende que el campo tiene que estar al menos cualificado por el nombre de la tabla
        # con menos no puedo hacerlo sin provocar un desastre
        return fullQualifyInString(field,table)
    #forma absolutamente barbara
    return '{}.{}'.format(table,field.split('.')[-1])


def swapPrefix(string,prefix,tabla):
    pos = string.lower().find(' as ')
    if pos > 0:
        mcampo = string[0:pos]
    else:
        mcampo = string

    if '(' in mcampo or ' ' in mcampo:
        return changeTable(mcampo,tabla,prefix)
    fldArray = mcampo.split('.')
    return '{}.{}'.format(prefix,fldArray[-1])

def catenate(db,array,delim=' '):
    if db.dialect == 'mysql':
        return 'CONCAT_WS({},{})'.format(delim,','.join(array))
    else:
        return "|| '{}' || ".format(delim).join(array)
        
     
def getPartialTitle(title,field,lastResource):
    if ' ' in field or '(' in field:
        pos = field.lower().find(' as ')
        if pos > 0:
            mcampo = field[pos+4:]
            return mcampo
        else:
            mcampo = lastResource
    else:
        mcampo = field.split('.')[-1]
    return '{}_{}'.format(title,mcampo)
    
def generateFullQuery(cubo):
    #defSchema = cubo.db.engine().Inspector.default_schema_name
    factTable = fqn(cubo.db,cubo.file)
    
    campos = list()
    joins  = list()
    # primero los campos factuales
    for item in cubo.getFields():
        campos.append([fieldFqN(item,factTable),'fact',factTable])
    # obtenemos el contexto de todas las guias
    contexto = cubo.fillGuias(generateTree=False)
    # para cada nivel en cada guia
    for i,dimension in enumerate(contexto):
        for j,level in enumerate(dimension):
                        
            lvlTable = fqn(cubo.db,level['table'])
            
            if lvlTable == factTable:
                prefix = 'fact'
            else:
                prefix = 'd{}_{}'.format(i,j)
               
               

            titulo = toNormString(level['name'])

            if level['class'] == 'd':
                # solo tomamos el ultimo elemento,los demas son redundantes
                campos.append([fieldFqN(level['desc'][-1],lvlTable),prefix,lvlTable,titulo])
            else:

                tmpDesc = list(map(lambda item:fieldFqN(item,lvlTable),level['desc']))
                #campos.append([catenate(cubo.db,tmpDesc),prefix,lvlTable,titulo])
                for k,item in enumerate(tmpDesc):
                    if len(tmpDesc) > 1:
                        titulo_parcial = getPartialTitle(titulo,item,k)
                        campos.append([item,prefix,lvlTable,titulo_parcial])
                    else:
                        campos.append([item,prefix,lvlTable,titulo])
            
            if lvlTable != factTable:
                # como es un join implicito primero generamos una entrada como si viniera de Link Via 
                lastEntry = dict()
                lastEntry['table'] = lvlTable
                lastEntry['filter'] = level['filter']
                lastEntry['clause'] = []
                for k,destino in enumerate(level['code']):
                    lastEntry['clause'].append({'base_elem':level['elems'][k],'rel_elem':destino})
                # construimos la cadena definitiva de enlaces
                path = level['linkvia'] + [lastEntry,]
                
                ultPaso = len(path) -1 
                basePfx = 'fact'
                baseTbl = factTable
                
                for k,arco in enumerate(path):
                    joinentry = ''
                    tgtTbl = fqn(cubo.db,arco['table'])
                    if k == ultPaso:
                        tgtPfx = prefix
                    else:
                        tgtPfx = '{}_{}'.format(prefix,k)
                    
                    for clausula in arco['clause']:
                        entrada = '{} {} {}'.format(
                            fieldFqN(clausula['base_elem'],baseTbl),
                            clausula.get('condition','='),
                            fieldFqN(clausula['rel_elem'],tgtTbl)
                            )

                    joinentry += '{}{}'.format(' AND ' if joinentry != ''  else '',entrada)
                    
                    if arco['filter']:
                        filtro = fullQualifyInString(arco['filter'],baseTbl)
                        filtro = fullQualifyInString(arco['filter'],tgtTbl)
                        joinentry += ' AND {}'.format(filtro)


                    joins.append([joinentry,tgtTbl,tgtPfx,baseTbl,basePfx])
                    basePfx = tgtPfx
                    baseTbl = tgtTbl

    # ahora eliminamos joins duplicados
    # la forma un poco convoluta para no alterar los indices en joins antes de la cuenta
    #pprint(campos)
    #pprint(joins)
    cadenasJoin = [ elem[0] for elem in joins]
    refJoin = [elem[4] for elem in joins]
    cadenasPfx  = [ elem[1] for elem in campos]

    hay = len(cadenasJoin)
    for i,joinQuery in enumerate(cadenasJoin):
        if not joinQuery:
            continue
        for j in range(i +1,hay):
            if not cadenasJoin[j]:
                continue
            if joinQuery.strip() == cadenasJoin[j].strip():
                cadenasJoin[j] = None
                joins[j][0] = None
                while True:
                    try:
                        idx = refJoin.index(joins[j][2])
                        joins[idx][4] = joins[i][2]
                        refJoin[idx] = None
                    except ValueError:
                        break
                
                while True:
                    try:
                        idx = cadenasPfx.index(joins[j][2])
                        campos[idx][1] = joins[i][2] #los prefijos estan en columnas distintas
                        cadenasPfx[idx]=None
                    except ValueError:
                        break
    #limpio los joins
    joins = [ item for item in joins if item[0]]
           
    select_string = ''
    
    for campo in campos:
        if len(campo) > 3:
            campoStr = '{} as {}'.format(swapPrefix(campo[0],campo[1],campo[2]),campo[3])
        else:
            campoStr = swapPrefix(campo[0],campo[1],campo[2])
            
        if select_string == '':
            select_string = campoStr
        else:
            select_string += ' ,{}'.format(campoStr)
            
    sqlString = ' SELECT {} FROM {} AS {} '.format(select_string,factTable,'fact')
    for join in joins:
        joinentry = join[0]
        tgtTbl = join[1]
        tgtPfx = join[2]
        baseTbl = join[3]
        basePfx = join[4]
        joinentry = swapPrefix(joinentry,basePfx,baseTbl)
        joinentry = swapPrefix(joinentry,tgtPfx,tgtTbl)

        sqlString += 'JOIN {} as {} on {} '.format(tgtTbl,tgtPfx,joinentry)
        
    return sqlString


@stopwatch
def test():
    from util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["rental"])
    query = generateFullQuery(cubo)
    print(queryFormat(query))
    cursor = getCursor(cubo.db,query,LIMIT=1000)
    #pprint(cursor)

def UberTest():
    from util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos = load_cubo()
    for cuboId in mis_cubos:
        if cuboId == 'default':
            continue
        print('Ahora para el cubo ',cuboId)
        cubo = Cubo(mis_cubos[cuboId])
        query = generateFullQuery(cubo)
        print(queryFormat(query))
    
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    export()
    #tabla = toArray()
    #for item in tabla:
        #print(len(item),item)
    #getHeaders()
    #getHeadersFilter()
    fr = lambda x:x.type() == TOTAL
    fg = lambda x:True
    #testTraspose()
    #bugFecha()
    #UberTest()
    test()
    
