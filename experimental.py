#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

# para evitar problemas con utf-8, no lo recomiendan pero me funciona
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

'''
Documentation, License etc.

@package estimaciones
'''

from util.yamlmgr import *
from util.record_functions import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from datemgr import getDateSlots
from pprint import *

class NCubo:
    def __init__(self, definicion):
        if definicion is None :
            print('No se especifico definicion valida ')
            sys.exit(-1)
        
        # los datos siguientes son la definicion externa del cubo
        #pprint(definicion)
        self.definition = definicion
        self.db = dbConnect(self.definition['connect'])
        # inicializo (y cargo a continuacion) los otros atributos       
        self.lista_guias= []
        self.lista_funciones = []
        self.lista_campos = []
        
        # ahora generamos las definiciones internas para las fechas
        #ind = -1
        dbdriver = self.definition['connect']['driver']
        

        # ahora generamos una lista medio decente de manejar para las presentaciones
        '''
        estructura de la lista
            0 -> nombre
            1 -> type
            2 -> model.row
            3 -> model.col (prod)
            3,,n indices
        '''
        #FiXME TODO este codigo aparentemente es obsoleto, solo la parte de fechas tiene sentido
        for i in range(0, len(self.definition['guides'])):
            entrada = self.definition['guides'][i]
            if entrada['class'] != 'd':
                self.lista_guias.append({'name':entrada['name'], 
                                            'type':entrada['class'],
                                            'prod':entrada['prod']
                                          })
            else:
                campo = entrada['prod'][0]['elem']
                j = 0
                for prod in getDateSlots(campo, dbdriver):
                    self.lista_guias.append({'name':prod['name'], 
                                                'type':entrada['class'],
                                                'base_fld':campo, 
                                                'prod':[prod, ]
                                              })
                    j += 1
                    
        #dump_structure(self.lista, "lista_dump.yml")
        self.setGuias()
        self.lista_funciones = getAgrFunctions(self.db,self.lista_funciones)
        # no se usa en core. No se todavia en la parte GUI
        self.lista_campos = self.getFields()
    #
    def getFields(self):
        '''
           crea/devuelve el atributo cubo.lista_campos
           parte de la base de los campos de la definición y añade los campos no textuales de las lista_guias
           Esa idea es para poder tener campos parciales o derivados como guias TODO
        '''
        if len(self.lista_campos) == 0:
            lista_campos = self.definition['fields'][:]
            for entry in self.definition['guides']:
                for regla in entry['prod']:
                    if 'fmt' in regla.keys():
                        if regla['fmt'] in ('txt', 'date'):
                            continue
                    lista_campos.append(regla['elem'])
        else:
            lista_campos = self.lista_campos [ : ]
        return lista_campos

    def setGuidesSqlStatement(self, entrada, fields):
        '''
          entrada es definition[guides][i][prod][j]: Contiene array
              -> source
                  -> code
                  -> desc
                  -> table
                  -> filter
                  -> grouped by (no usada)
              -> fmt
              -> elem
            parametros implicitos  (para campos sin source, es decir base general
              -> definition.table
              -> definition.base_filter
              -> entrada.elem
          TODO fields son campos auxiliares a incluir en la query
        '''
        code_fld = 0
        desc_fld = 0
        
        sqlDef=dict()

        if 'source' in entrada.keys():
          sqlDef['tables'] = entrada['source']['table']
          if 'filter' in entrada['source']:
              sqlDef['base_filter']=entrada['source']['filter']
              
          sqlDef['fields'] = []
          #TODO grouped by determina la jerarquia explicitamente.
          #     hay que hallar la manera de determinarla implicitamente
          if 'grouped by' in entrada['source']:
              sqlDef['fields'] += entrada['source']['grouped by'].split(',')
          if len(fields) > 0:
              sqlDef['fields'] += fields[:]
          sqlDef['fields'] += entrada['source']['code'].split(',')
          
          if 'desc' in entrada['source']:
              desc_tup = entrada['source']['desc'].split(',')
              sqlDef['fields'] += desc_tup
              desc_fld = len(desc_tup)
        else:
          sqlDef['tables'] = self.definition['table']
          if len(self.definition['base filter'].strip()) > 0:
             sqlDef['base filter']=self.definition['base_filter']
          sqlDef['fields'] = entrada['elem']
          
        code_fld = len(sqlDef['fields']) - desc_fld  
        
        #print(code_fld,desc_fld,sqlDef['fields'])
        sqlDef['order'] = [ str(x + 1) for x in range(code_fld)]
        sqlDef['select_modifier']='DISTINCT'
        
        sqlString = queryConstructor(**sqlDef)
        return sqlString, code_fld,desc_fld 
    
    def setGuidesDateSqlStatement(self, entrada, fields):
        #TODO creo que fields sobra
        sqlDef=dict()
        sqlDef['tables'] = self.definition['table']
        if len(self.definition['base filter'].strip()) > 0:
           sqlDef['base_filter']=self.definition['base filter']
        sqlDef['fields'] = [[entrada['base_fld'],'max'],
                            [entrada['base_fld'],'min'],
                            ]
        return queryConstructor(**sqlDef)            
 
    def setGuias(self):
        #TODO manejo de fechas
        #TODO indices con campos elementales no son problema, pero no se si funciona con definiciones raras
        self.lista_guias = []
        for ind,entrada in enumerate(self.definition['guides']):
            self.lista_guias.append({'name':entrada['name'],'rules':[],'elem':[]})
            for idx,componente in enumerate(entrada['prod']):
                if entrada['class'] == 'd':
                    self.lista_guias[ind]['elem'].append(componente['elem'])
                else:
                    (sqlString,code_fld,desc_fld) = self.setGuidesSqlStatement(componente,[])
                    self.lista_guias[ind]['rules'].append({'string':sqlString,'ncode':code_fld,'ndesc':desc_fld})
                    self.lista_guias[ind]['elem'].append(componente['elem'])
                #pprint(componente)
    def fillGuias(self):

        for ind,entrada in enumerate(self.lista_guias):
            cursor = []
            for idx,componente in enumerate(entrada['rules']):
                if len(componente) == 0: #TODO fechas
                    continue
                sqlstring=componente['string']
                lista_compra={'nkeys':componente['ncode'],'ndesc':componente['ndesc']}
                if componente['ncode'] < len(entrada['elem']):
                    lista_compra['nholder']=len(entrada['elem'])-componente['ncode']
                    if componente['ndesc'] != 1:
                        lista_compra['pholder'] = - componente['ndesc']
                print(ind,idx,sqlstring,lista_compra)
                cursor += getCursor(self.db,sqlstring,regHashFill,**lista_compra)
            entrada['cursor']=sorted(cursor)    
            entrada['dir_row']=[record[0] for record in entrada['cursor'] ]  #para navegar el indice con menos datos
            entrada['des_row']=[record[-componente['ndesc']:] for record in entrada['cursor']] #probablemenente innecesario
            #print(time.strftime("%H:%M:%S"),dir_row[0])

class NVista:
    def __init__(self, cubo,row, col,  agregado, campo, filtro=''):
        
        self.cubo = cubo
        # deberia verificar la validez de estos datos
        self.agregado=agregado
        self.campo = campo
        self.filtro = filtro
        
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None
        self.cur_row = None
        self.cur_col  = None
        self.row_hdr_idx = list()
        self.col_hdr_idx = list()
        self.row_hdr_txt = list()
        self.col_hdr_txt = list()
        self.dim_row = None
        self.dim_col = None
        self.hierarchy= False
        self.array = []

def get_query():
    return

def experimental():
    vista = None
    mis_cubos = load_cubo()
    cubo = NCubo(mis_cubos['datos locales'])
    #pprint(cubo.definition)
    #pprint(cubo.lista_funciones)
    #pprint(cubo.lista_campos)
    
    cubo.fillGuias()
    pprint(cubo.lista_guias[5]['des_row'][1:20])
    
    get_query()

if __name__ == '__main__':
    experimental()
        