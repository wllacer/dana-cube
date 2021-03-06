#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import sys

sys.path.append('/home/werner/projects/dana-cube.git')


'''
Documentation, License etc.

TODO
    Free date download. Requires special settings in cubo.json
'''

import base.config as config

#from support.util.record_functions import *
#from base.tree import *
#from support.util.fechas import *

from support.datalayer.access_layer import *
from support.datalayer.query_constructor import *
from base.core import *

#from support.util.numeros import stats,num2text

#from support.datalayer.datemgr import getDateEntry, getDateIndexNew
from pprint import *

from support.util.decorators import *
from support.util.cadenas import mergeString,toNormString

import time

from support.util.jsonmgr import dump_structure,dump_json

    


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
    fields = norm2List(field)
    result = []
    for field in fields:
        if  '(' in field or ' ' in field:
            # aqui se entiende que el campo tiene que estar al menos cualificado por el nombre de la tabla
            # con menos no puedo hacerlo sin provocar un desastre
            result.append(fullQualifyInString(field,table))
        else:
    #forma absolutamente barbara
            result.append('{}.{}'.format(table,field.split('.')[-1]))
    return norm2String(result)


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

def catenate(db,array,sep=' '):
    if db.dialect == 'mysql':
        return 'CONCAT_WS("{}",{})'.format(sep,','.join(array))
    else:
        return "|| '{}' || ".format(sep).join(array)
    
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
    
def generateFullQuery(cubo, autoDates=True):
    """
    corazon de 
    """
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
                campos.append([catenate(cubo.db,tmpDesc),prefix,lvlTable,titulo])
            
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
                    
                    if arco.get('filter') and arco.get('filter').strip():
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

        sqlString +='LEFT JOIN {} as {} on {} '.format(tgtTbl,tgtPfx,joinentry)
        
    # filtros generales
    
    filtroGeneral = None
    filtroFechas  = None
    if cubo.definition.get('base filter') and cubo.definition.get('base filter').strip():
        filtroGeneral = changeTable(fullQualifyInString(cubo.definition['base filter'],factTable,),factTable,'fact')
    if cubo.definition.get('date filter'):
        tmpDF = searchConstructor('where',where=cubo.setDateFilter(),driver=cubo.dbdriver)
        filtroFechas = changeTable(fullQualifyInString(tmpDF,factTable,),factTable,'fact')
    if filtroGeneral or filtroFechas:    
        sqlString += 'WHERE {}'.format(mergeString(filtroGeneral,filtroFechas,'AND'))
    return sqlString


@stopwatch
def generaQuery(cubo,mostrar=False,ejecutar=True,salida=False):
    query = generateFullQuery(cubo)
    #print(queryFormat(query))
    if mostrar:
        print(queryFormat(query))
    if ejecutar:
        try:
            cursor = getCursor(cubo.db,query,LIMIT=1000)
            if salida:
                pprint(cursor)
        except Exception as e:
            print('!!!!! ERROR !!!!', cubo.nombre)
            print(e)
    return(query)
  
from support.datalayer.querywidget import *

class browsePreview(QDialog):
    from support.util.jsonmgr import load_cubo
    def __init__(self,cubo,parent=None):
        super().__init__(parent)
        mis_cubos =  load_cubo('/home/werner/projects/dana-cube.git/cubo.json')
        cubo = Cubo(mis_cubos[cubo])
        query = generaQuery(cubo,ejecutar=False)
        
        self.tree = QueryTab(cubo.db,script=query)
        meatLayout=QGridLayout()
        meatLayout.addWidget(self.tree)
        self.setLayout(meatLayout)    
        self.tree.execute()

def test(cuboId,mostrar=True,ejecutar=False,salida=False):
    from support.util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos = load_cubo('/home/werner/projects/dana-cube.git/cubo.json')
    cubo = Cubo(mis_cubos[cuboId])
    generaQuery(cubo,mostrar,ejecutar,salida)
    #pprint(cursor)

def UberTest(mostrar=False,ejecutar=True,salida=False):
    from support.util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos =  load_cubo('/home/werner/projects/dana-cube.git/cubo.json')
    for cuboId in mis_cubos:
        if cuboId == 'default':
            continue
        print('Ahora para el cubo ',cuboId)
        cubo = Cubo(mis_cubos[cuboId])
        cubo.nombre = cuboId
        generaQuery(cubo,mostrar,ejecutar,salida)
        
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    sys.path.append('/home/werner/projects/dana-cube.git')
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #export()
    config.DEBUG = False
    app = QApplication(sys.argv)
    #UberTest(mostrar=True,ejecutar=False)
    #test("rental",mostrar=True,ejecutar=True,salida=True)
    browsePreview("rental")
    
