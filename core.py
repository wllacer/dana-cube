#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
TODO si utilizo un filter en la guia ¿deberia que estar en la query?
FIXME y propagarse en el filtro si es jerarquico
# FIXED la union de filtros no funcionaba. Faltaba el AND
# DONE esto es una funcion reutilizable mergeString
#FIXED ahora si el indice no existe para un valor no se dispara error
#TODO En ciertas circunstancias debe o no provocarse y/o informar del error

'''

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from util.tree import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.fivenumbers import stats

from datemgr import getDateIndex,getDateEntry
from pprint import *

import time


def mergeString(string1,string2,connector):
    if len(string1.strip()) > 0 and len(string1.strip()) > 0:
        merge ='{} {} {}'.format(string1,connector,string2)
    elif len(string1.strip()) > 0 or len(string2.strip()) > 0: 
        merge ='{}{}'.format(string1,string2).strip()
    else:
        merge = ''
    return merge

def getParentKey(clave,debug=False):
    """
      define el padre de un elemento via la clave
    """
    nivel=getLevel(clave)
    if nivel > 0:
        padreKey = DELIMITER.join(clave.split(DELIMITER)[0:nivel])
        return padreKey
    else:
       return None


def getOrderedText(desc,sparse=True,separator=None):
    if desc is None:
        return None
    levels = len(desc)
    texto = ''
    for j in range(levels -1):
        if sparse:
            texto +=separator
        else:
            texto += (desc[j]+separator)
    # especial fechas. no se que efectos secundarios puede tener
    texto += desc[-1]
    return texto
        
    
          
class Cubo:
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
        
        self.dbdriver = self.definition['connect']['driver']
        
        self.__setGuias()
        
        self.lista_funciones = getAgrFunctions(self.db,self.lista_funciones)
        # no se usa en core. No se todavia en la parte GUI
        self.lista_campos = self.getFields()
    #
    def getGuideNames(self):
        tabla = []
        for guia in self.lista_guias:
            tabla.append(guia['name'])
        return tuple(tabla)

    def getFunctions(self):
        '''
           INTERFAZ EXTERNA
           obtiene las funciones disponibls por la base de datos
        '''
        return self.lista_funciones
           
    def getFields(self):
        '''
           crea/devuelve el atributo cubo.lista_campos
        '''
        if len(self.lista_campos) == 0:
            lista_campos = self.definition['fields'][:]
            # este añadido no parece tener sentido por ahora. comentado FIXME
            #for entry in self.definition['guides']:
                #for regla in entry['prod']:
                    #if 'fmt' in regla.keys():
                        #if regla['fmt'] in ('txt', 'date'):
                            #continue
                    #lista_campos.append(regla['elem'])
        else:
            lista_campos = self.lista_campos [ : ]
        return lista_campos

    def __setGuidesSqlStatement(self, entrada, fields):
        '''
          entrada es definition[guides][i][prod][j]: Contiene array
              -> source
                  -> code
                  -> desc
                  -> table
                  -> filter
                  -> grouped by (no usada excepto en join en una misma tabla)
              -> related_via (para joins)
                  -> table
                    "table": "geo_rel",
                    "parent_elem":"padre",
                    "child_elem":"hijo",
                    "filter": "geo_rel.tipo_padre = 'P'"

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
          #REFINE grouped by determina la jerarquia explicitamente.
          #     hay que hallar la manera de determinarla implicitamente
          if 'grouped by' in entrada['source']:
              sqlDef['fields'] += norm2List(entrada['source']['grouped by'])
          if len(fields) > 0:
              sqlDef['fields'] += fields[:]

          sqlDef['fields'] += norm2List(entrada['source']['code'])
          
            
          if 'desc' in entrada['source']:
              desc_tup = norm2List(entrada['source']['desc'])
              sqlDef['fields'] += desc_tup
              desc_fld = len(desc_tup)
        else:
          sqlDef['tables'] = self.definition['table']
          if len(self.definition['base filter'].strip()) > 0:
             sqlDef['base filter']=self.definition['base_filter']
             
          sqlDef['fields'] = norm2List(entrada['elem'])
          
        code_fld = len(sqlDef['fields']) - desc_fld  
        
        sqlDef['order'] = [ str(x + 1) for x in range(code_fld)]
        
        sqlDef['select_modifier']='DISTINCT'
        sqlString = queryConstructor(**sqlDef)
        return sqlString, code_fld,desc_fld 
    
    def __setGuidesDateSqlStatement(self, entrada, fields=None):
        #REFINE creo que fields sobra
        sqlDef=dict()
        sqlDef['tables'] = self.definition['table']
        if len(self.definition['base filter'].strip()) > 0:
           sqlDef['base_filter']=self.definition['base filter']
        sqlDef['fields'] = [[entrada['base_date'],'max'],
                            [entrada['base_date'],'min'],
                            ]
        return queryConstructor(**sqlDef) 

    def __setGuias(self):
        '''
           Crea la estructura lista_guias para cada una de las guias (dimensiones) que hemos definido en el cubo.
           Proceden de las reglas de produccion (prod) de la definicion
           Es una tupla con una entrada (diccionario) por cada guia con los siguientes elementos:
           *  name   nombre con el que aparece en la interfaz de usuario (de la definicion)
           *   class    '' normal, 'd' fecha (Opcional)
           *  elem   lista con los campos de la TABLA PRINCIPAL que cubren esa guia (de la definicion en la prod
           *  rules  lista con cada una de las reglas de produccion de los niveles. Contiene
                *   name
                *   string   cadena sql para crear el dominio de la guia (de prod )
                *   case_string para categorias
                *   ncode    numero de campos que forman la clave de la iteracion
                *   ndesc    numero de campso de la descripción
                *   elem     lista con los campos de la TABLA PRINCIPAL que cubren ese nivel
                *   date_fmt      (solo fechas) estructura de fecha que deseo
                *   enum     (solo categorias) estructura de enumeracion
                *   fmt      (opcional). Formato especial para los valores del campo 
                *   enum_fmt (opcional)  en categorias formato de los elementos a enumerar si no son el defecto
                *   base_date (solo fechas) campo original de fechas
 

           * dir_row el array indice (para realizar busquedas)

           
           Estos tres últimos elemnentos se cargan en self.fillGuias; separado para poder refrescarlo en cualquier
           momento
           
           El comportamiento para guias de formato fecha es totalmente distinto del resto. TODO documentar proceso
           
           FIXME Funciona perfectamente con el ejemplo que uso, necesito explorar otras posibilidades de definicion
           
        '''
        #TODO indices con campos elementales no son problema, pero no se si funciona con definiciones raras

        
        self.lista_guias = []
        ind = 0
        #para un posible backtrace
        nombres = [ entrada['name'] for entrada in self.definition['guides'] ]
        
        for entrada in self.definition['guides']:
            guia = {'name':entrada['name'],'class':entrada['class'],'rules':[],'elem':[]}
            self.lista_guias.append(guia)
            #FIXME produccion = entrada['prod']   GENERADOR  
            produccion = entrada.get('prod',dict())
            for componente in produccion:
                if 'name' in componente:
                    nombre = componente['name']
                else:
                    nombre = guia['name']
                if 'class' in componente:
                    clase = componente['class']
                else:
                    clase = guia['class']
                ##TODO hay que normalizar lo de los elementos
                if clase != 'd':  #las fechas generan dinamicamente guias jerarquicas
                    guia['elem'] +=norm2List(componente['elem'])
                if clase == 'd':
                    if 'mask' not in componente:
                        componente['mask'] = 'Ymd'  #(agrupado en año mes dia por defecto'
                        base_date = norm2List(componente['elem'])[-1]
                    #
                    for k in range(len(componente['mask'])):
                        kmask = componente['mask'][0:k+1]                   
                        datosfecha= getDateEntry(componente['elem'],kmask,self.dbdriver)
                        guia['elem'] += [datosfecha['elem'],]
                        guia['rules'].append({'string':'',
                                    'ncode':len(guia['elem']),
                                    'ndesc':0,
                                    'elem':[datosfecha['elem'],],
                                    'name': nombre +'_'+ kmask,
                                    'date_fmt': datosfecha['mask'],
                                    'class':clase,
                                    'base_date':base_date
                                    })

                elif clase == 'c':
                    #TODO falta por documentar lo especifico de las categorias
                    #FIXME la generacion del CASE requiere unos parametros que se calculan luego.
                    #      eso entorpece el codigo
                    elem=norm2List(componente['elem'])
                    # en lugar de una defincion compleja tengo algo suave
                    if 'case_sql' in componente:
                        k1 =' '.join(componente['case_sql']).replace('$$1',elem[-1]).replace('$$2',nombre)
                        elem[-1]= k1
                    else:
                        elem[-1] = [caseConstructor(nombre,componente),]
                          
                    if 'source' in componente:  #TODO no usada. No parece tener sentido
                        (sqlString,code_fld,desc_fld) = self.__setGuidesSqlStatement(componente,[])
                        enum = None
                    elif 'categories' not in componente:
                        aux_entrada = { 'elem':elem }
                        (sqlString,code_fld,desc_fld) = self.__setGuidesSqlStatement(aux_entrada,[])
                        enum = None
                    else:
                        sqlString= ''
                        code_fld = len(guia['elem'])
                        desc_fld = 0
                        enum=componente['categories']

                    guia['rules'].append({'string':sqlString,
                                'ncode':code_fld,
                                'ndesc':desc_fld,
                                'elem': elem,
                                #'elem':caseConstructor(guia['rules'][-1])
                                'name':nombre,
                                'class':clase,
                                'enum':enum
                                })

                    if 'enum_fmt' in componente:
                        guia['rules'][-1]['enum_fmt']=componente['enum_fmt']
                    if 'categories' not in componente:
                       aux_entrada = { 'elem':guia['rules'][-1]['elem'][-1]}
                       (sqlString,code_fld,desc_fld) = self.__setGuidesSqlStatement(aux_entrada,[])
                       print(sqlString)
                    else:
                       guia['rules'][-1]['enum']=componente['categories'] 
                else:
                    (sqlString,code_fld,desc_fld) = self.__setGuidesSqlStatement(componente,[])

                    guia['rules'].append({'string':sqlString,
                                                    'ncode':code_fld,
                                                    'ndesc':desc_fld,
                                                    'elem':guia['elem'][:],
                                                    'name':nombre,
                                                    'class':clase})
                if 'related via' in componente:
                    guia['rules'][-1]['join']=componente['related via']
                if 'fmt' in componente:
                    guia['rules'][-1]['fmt']=componente['fmt']
                
    def fillGuia(self,guiaId):
        # TODO documentar y probablemente separar en funciones
        # TODO ahora debo de poder integrar fechas y categorias dentro de una jerarquia
        #      probablemente el cursor += no es lo que se necesita en estos casos
        date_cache = {}
        #print(time.time(),'A procesar ',len(self.lista_guias))

        entrada = self.lista_guias[guiaId]
        cursor = []
        idx = 0 #para evitar los casos en que rules esta vacio GENERADOR
        for idx,componente in enumerate(entrada['rules']):
            sqlString=''
            lista_compra={'nkeys':componente['ncode'],'ndesc':componente['ndesc']}
            if componente['ncode'] < len(entrada['elem']):
                lista_compra['nholder']=len(entrada['elem'])-componente['ncode']
                if  componente['ndesc'] == 0:
                    lista_compra['ndesc']= componente['ncode']
                elif componente['ndesc'] != 1:
                    lista_compra['pholder'] = - componente['ndesc']
                
                    
            if componente['class'] == 'd':
                #TODO demasiadas vueltas                
                #REFINE asumo que solo existe un elemento origen en los campos fecha
                #campo = componente['elem'][-1]
                campo= componente['base_date']
                # obtengo la fecha mayor y menor
                if campo in date_cache:
                    pass
                else:
                    #TODO solo se requiere consulta a la base de datos si el formato incluye 'Y'
                    sqlString = self.__setGuidesDateSqlStatement(componente)
                    row=getCursor(self.db,sqlString)
                    date_cache[campo] = [row[0][0], row[0][1]] 
                    
                cursor += getDateIndex(date_cache[campo][0]  #max_date
                                                , date_cache[campo][1]  #min_date
                                                , componente['date_fmt'],
                                                **lista_compra)
                
            elif componente['class'] == 'c':
                if componente['string'] != '':
                    sqlString=componente['string']
                    cursor += getCursor(self.db,sqlString,regHashFill,**lista_compra)
                else:
                    nombres = [ [item['result'] if 'result' in item else item['default'],] for item in componente['enum']]
                    for elem in nombres:
                        regHashFill(elem,**lista_compra)
                    cursor += sorted(nombres)

            else:  
                sqlString=componente['string']
                cursor += getCursor(self.db,sqlString,regHashFill,**lista_compra)
            if DEBUG:
                print(time.time(),guiaId,idx,sqlString)
        cursor = sorted(cursor)
        tree=TreeDict()
        for entryNum,elem in enumerate(cursor):
            if componente['ndesc'] == 0:
                desc=[elem[0],] 
            else:
                desc=elem[-componente['ndesc']:] 
            key=elem[0]
            parentId = getParentKey(key)
            tree.append(TreeItem(key,entryNum,desc),parentId)
            
        if DEBUG:              
            print(time.time(),guiaId,idx,'creada')
        entrada['dir_row']=tree
            
                #print(time.strftime("%H:%M:%S"),dir_row[0])
                #print(time.strftime("%H:%M:%S"),dir_row[0])

                
class Vista:
    #TODO falta documentar
    #TODO falta implementar la five points metric
    def __init__(self, cubo,row, col,  agregado, campo, filtro='',totalizado=True, stats=True):
        
        self.cubo = cubo
        # deberia verificar la validez de estos datos
        self.agregado=agregado
        self.campo = campo
        self.filtro = filtro
        self.totalizado = True
        self.stats = True
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None

        self.row_hdr_idx = list()
        self.col_hdr_idx = list()
        #self.row_hdr_txt = list()
        #self.col_hdr_txt = list()

        self.dim_row = None
        self.dim_col = None
        #self.hierarchy= False
        self.array = []
        
        self.setNewView(row, col)
        
    def setNewView(self,row, col, agregado=None, campo=None, filtro='',totalizado=True, stats=True):
        
        dim_max = len(self.cubo.lista_guias)
        
        # validaciones. Necesarias porque puede ser invocado desde fuera
        if row >= dim_max or col >= dim_max:
            print( 'Limite dimensional excedido. Ignoramos')
            return 
        elif  agregado is not None and agregado not in  self.cubo.lista_funciones:
            print('Funcion de agregacion >{}< no disponible'.format(agregado))
            return
        elif campo is not None and campo not in self.cubo.lista_campos:
            print('Magnitud >{}< no disponible en este cubo'.format(campo))
            return
        else:
            pass
        # Determinamos si han cambiado los valores
        
        procesar = False
        if self.row_id != row:
            procesar = True
            self.row_id = row
        if self.col_id != col:
            procesar = True
            self.col_id = col
        if agregado is not None and agregado != self.agregado:
            procesar = True
            self.agregado = agregado
        if campo is not None and campo != self.campo:
            procesar = True
            self.campo = campo
        if self.filtro != filtro:
            procesar = True
            self.filtro = filtro
        if self.totalizado != totalizado:
            procesar = True
            self.totalizado = totalizado
        if self.stats != stats:
            procesar = True
            self.stats = stats
            
        if procesar:
        
            self.row_id = row
            self.col_id = col
            
            self.dim_row = len(self.cubo.lista_guias[row]['rules'])
            self.dim_col = len(self.cubo.lista_guias[col]['rules'])

            for guia in self.cubo.lista_guias:
                if 'dir_row' in guia:
                    del guia['dir_row']
                    
            self.cubo.fillGuia(row)
            self.cubo.fillGuia(col)
            self.row_hdr_idx = self.cubo.lista_guias[row]['dir_row']
            self.col_hdr_idx = self.cubo.lista_guias[col]['dir_row']
        
            self.__setDataMatrix()
            
    def  __setDataMatrix(self):
         #TODO clarificar el codigo
         #REFINE solo esperamos un campo de datos. Hay que generalizarlo
        #self.array = [ [None for k in range(len(self.col_hdr_idx))] for j in range(len(self.row_hdr_idx))]
        self.array = []
        for i in range(0,self.dim_row):
            # el group by en las categorias necesita codigo especial
            if self.cubo.lista_guias[self.row_id]['rules'][i]['class'] == 'c':
                group_row = [self.cubo.lista_guias[self.row_id]['rules'][i]['name'],]
            else:
                group_row = self.cubo.lista_guias[self.row_id]['rules'][i]['elem']
            for j in range(0,self.dim_col):
                sqlDef=dict()
                sqlDef['tables']=self.cubo.definition['table']
                #sqlDef['select_modifier']=None
                sqlDef['fields']= self.cubo.lista_guias[self.row_id]['rules'][i]['elem'] + \
                                  self.cubo.lista_guias[self.col_id]['rules'][j]['elem'] + \
                                  [(self.campo,self.agregado)]
                sqlDef['base_filter']=mergeString(self.filtro,self.cubo.definition['base filter'],'AND')
                sqlDef['join']=[]
                #TODO claro candidato a ser incluido en una funcion
                if 'join' in self.cubo.lista_guias[self.row_id]['rules'][i]:
                   row_join = self.cubo.lista_guias[self.row_id]['rules'][i]['join']
                   for entry in row_join:
                       join_entry = dict()
                       join_entry['table'] = entry.get('table')
                       join_entry['join_filter'] = entry.get('filter')
                       join_entry['join_clause'] = []
                       for clausula in entry['clause']:
                           entrada = (clausula.get('rel_elem'),'=',clausula.get('base_elem'))
                           join_entry['join_clause'].append(entrada)
                       sqlDef['join'].append(join_entry)
                if 'join' in self.cubo.lista_guias[self.col_id]['rules'][j]:
                   col_join = self.cubo.lista_guias[self.col_id]['rules'][j]['join']
                   for entry in col_join:
                       join_entry = dict()
                       join_entry['table'] = entry.get('table')
                       join_entry['join_filter'] = entry.get('filter')
                       join_entry['join_clause'] = []
                       for clausula in entry['clause']:
                           entrada = (clausula.get('rel_elem'),'=',clausula.get('base_elem'))
                           join_entry['join_clause'].append(entrada)
                       sqlDef['join'].append(join_entry)
                # esta desviacion es por las categorias
                if self.cubo.lista_guias[self.col_id]['rules'][j]['class'] == 'c':
                    group_col = [self.cubo.lista_guias[self.col_id]['rules'][j]['name'],]
                else:
                    group_col = self.cubo.lista_guias[self.col_id]['rules'][j]['elem']
                #sqlDef['group']=self.cubo.lista_guias[self.row_id]['rules'][i]['elem'] + \
                                  #self.cubo.lista_guias[self.col_id]['rules'][j]['elem']
                sqlDef['group']= group_row + group_col
                #sqlDef['having']=None
                #sqlDef['order']=None
                sqlstring=queryConstructor(**sqlDef)
                
                #
                lista_compra={'row':{'nkeys':len(self.cubo.lista_guias[self.row_id]['rules'][i]['elem']),},
                              'rdir':self.row_hdr_idx,
                              'col':{'nkeys':len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem']),
                                     'init':-1-len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem']),},
                              'cdir':self.col_hdr_idx
                              }
                
                #cursor_data=getCursor(self.cubo.db,sqlstring,regHasher2D,**lista_compra)
                self.array +=getCursor(self.cubo.db,sqlstring,regTree,**lista_compra)
                if DEBUG:
                    print(time.time(),'Datos ',sqlstring)
    
    def grandTotal(self):
        array = []
        for j in range(0,self.dim_col):
            sqlDef=dict()
            sqlDef['tables']=self.cubo.definition['table']
            #sqlDef['select_modifier']=None
            sqlDef['fields']= self.cubo.lista_guias[self.col_id]['rules'][j]['elem'] + \
                                [(self.campo,self.agregado)]
            sqlDef['base_filter']=mergeString(self.filtro,self.cubo.definition['base filter'],'AND')
            sqlDef['join']=[]
            #TODO claro candidato a ser incluido en una funcion
            if 'join' in self.cubo.lista_guias[self.col_id]['rules'][j]:
                col_join = self.cubo.lista_guias[self.col_id]['rules'][j]['join']
                for entry in col_join:
                    join_entry = dict()
                    join_entry['table'] = entry.get('table')
                    join_entry['join_filter'] = entry.get('filter')
                    join_entry['join_clause'] = []
                    for clausula in entry['clause']:
                        entrada = (clausula.get('rel_elem'),'=',clausula.get('base_elem'))
                        join_entry['join_clause'].append(entrada)
                    sqlDef['join'].append(join_entry)
            # esta desviacion es por las categorias
            group_col = self.cubo.lista_guias[self.col_id]['rules'][j]['elem']
            sqlDef['group']= group_col
            #sqlDef['having']=None
            #sqlDef['order']=None
            sqlstring=queryConstructor(**sqlDef)
            
            #
            lista_compra={'nkeys':len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem']),
                          'init':-1-len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem']),
                          'dir':self.col_hdr_idx
                         }
            
            #cursor_data=getCursor(self.cubo.db,sqlstring,regHasher2D,**lista_compra)
            array +=getCursor(self.cubo.db,sqlstring,regTree1D,**lista_compra)
            if DEBUG:
                print(time.time(),'Datos ',sqlstring)
        return array
        
    def toTable(self):

        table = [ [None for k in range(self.col_hdr_idx.count())] for j in range(self.row_hdr_idx.count())]
        for record in self.array:
            try:
                ind_1 = record[0].ord
                ind_2 = record[1].ord
                table[ind_1][ind_2]=record[-1]
            except KeyError:
                continue
            except IndexError:
                print('{} o {} fuera de rango'.format(ind_1,ind_2))
        if DEBUG:
            print(time.time(),'table ',len(table),self.row_hdr_idx.count(),len(table[0])) 
        return table

    def toKeyedTable(self):
        ktable = [ [None for k in range(self.col_hdr_idx.count()+1)] for j in range(self.row_hdr_idx.count()+1)]
        ktable[0][0] = None
        ind = 1
        for key in self.col_hdr_idx.traverse(mode=1):
            elem = self.col_hdr_idx[key]
            ktable[0][elem.ord +1] = key
            ind += 1
        ind = 1
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            ktable[elem.ord +1][0] = key
            ind += 1

        table = self.toTable()
        ind = 0
        for elem in ktable:
           if ind == 0:
               ind += 1
               continue

           elem[1:] = table[ind][:]
        return ktable
    
    def toCsv(self,row_sparse=True,col_sparse=False,translated=True,separator=';',string_sep="'"):
        ctable = [ ['' for k in range(self.col_hdr_idx.count()+self.dim_row)] 
                             for j in range(self.row_hdr_idx.count()+self.dim_col) ]
     
        ind = 1
        def csvFormatString(cadena):
            if separator in cadena:
                return string_sep + cadena + string_sep
            else:
                return cadena
        for key in self.col_hdr_idx.traverse(mode=1):
            elem = self.col_hdr_idx[key]
            desc = elem.getFullDesc()   
            if col_sparse:
                k = len(desc) -1
                ctable[k][elem.ord +self.dim_row] = csvFormatString(desc[k])
            else:
                for k in range(len(desc)):
                    ctable[k][elem.ord +self.dim_row] = csvFormatString(desc[k])

            
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            desc = elem.getFullDesc()   
            if row_sparse:
                k = len(desc) -1
                ctable[elem.ord + self.dim_col][k]=csvFormatString(desc[k])
            else:
                for k in range(len(desc)):
                    ctable[elem.ord + self.dim_col][k]=csvFormatString(desc[k])
        table = self.toTable()
        # probablemente este paso intermedio es innecesario
        ind = 0
        for elem in ctable[self.dim_col : ]:
           elem[self.dim_row:] = [str(dato) if dato is not None else '' for dato in table[ind] ]
           ind += 1
        lineas=[]
        for row in ctable:
            lineas.append(separator.join(row))
            
        return lineas
    
    def toNamedTable(self):
        ntable = [ [ None for k in range(self.col_hdr_idx.count()+1)] for j in range(self.row_hdr_idx.count()+1)]
        ntable[0][0] = None
        ind = 1
        for key in self.col_hdr_idx.traverse(mode=1):
            elem = self.col_hdr_idx[key]
            ntable[0][elem.ord +1] = getOrderedText(elem.getFullDesc(),sparse=False,separator='\n')
            ind += 1
        ind = 1
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            ntable[elem.ord +1][0] = getOrderedText(elem.getFullDesc(),sparse=True,separator='\t')
            ind += 1

        table = self.toTable()
        ind = 0
        for elem in ntable:
           if ind == 0:
               ind += 1
               continue

           elem[1:] = table[ind][:]
        return ntable
        #for elem in ktable:
            #print(elem)
            
    def toTree(self):
        array = self.toTable()
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    array[elem.ord][:]
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()
        if DEBUG:
            print(time.time(),'Tree ',len(array),self.row_hdr_idx.count())  

    def toTree2D(self):
        array = self.toTable()
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    array[elem.ord][:]
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()
        for key in self.col_hdr_idx.traverse(mode=1):
            elem = self.col_hdr_idx[key]
            datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    [ array[ind][elem.ord] for ind in range(self.row_hdr_idx.count()) ]
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()

        if self.totalizado:
            self.row_hdr_idx.rebaseTree()
            tabla = self.grandTotal()
            datos =['Gran Total',]+[elem[1] for elem in tabla]
            elem = self.row_hdr_idx['//']
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()

                    
        if DEBUG:       
            print(time.time(),'Tree ',len(array),self.row_hdr_idx.count())  

    def recalcGrandTotal(self):
        def cargaAcumuladores():
            if elem.isLeaf():
                for k in range(len(acumuladores)):
                    for ind,item in enumerate(elem.getPayload()):
                        if item is not None:
                            acumuladores[k][ind]['max'] = max(acumuladores[k][ind]['max'],item)
                            acumuladores[k][ind]['min'] = min(acumuladores[k][ind]['min'],item)
                            acumuladores[k][ind]['sum'] += item
                            acumuladores[k][ind]['count'] += 1
        def procesa():
            if self.agregado == 'avg':
                datos = [item['sum']/item['count'] if item['count'] != 0 else None for item in acumuladores[-1] ]
            else:
                datos = [item[self.agregado] if item[self.agregado] != 0 else None for item in acumuladores[-1] ]
            padres[-1].setPayload(datos)
            if self.stats :
                padres[-1].setStatistics()

        
        arbol = self.row_hdr_idx
        numcol = self.col_hdr_idx.count()
        padres = []
        acumuladores = []
        for key in arbol.traverse(mode=1):
            elem = arbol[key]
            prof = elem.depth()
            if len(padres) < prof:
                padres.append(elem.parentItem)
                acumuladores.append([ {'max':0,'min':0,'count':0,'sum':0} for k in range(numcol)])
                cargaAcumuladores()
            elif len(padres) == prof:
                if padres[-1] == elem.parentItem:
                    cargaAcumuladores()
                else:
                    print('cambio de padre')
            elif len(padres) > prof:
                procesa()
                del padres[-1]
                del acumuladores[-1]
                cargaAcumuladores()
                #if padres[-1] == elem.parentItem:
                    #print('no cambia nada')
                #else:
                    #print('nuevo padre')
                    #padres.append(elem.parentItem)
                print('para atras')
        else:
            while padres[-1].parent() is not None:
                procesa()
                del padres[-1]
                del acumuladores[-1]
    
    def traspose(self):
        tmp_col = self.row_id
        tmp_row = self.col_id
        
        self.row_id = tmp_row
        self.col_id = tmp_col
        
        self.dim_row = len(self.cubo.lista_guias[self.row_id]['rules'])
        self.dim_col = len(self.cubo.lista_guias[self.col_id]['rules'])

        self.row_hdr_idx = self.cubo.lista_guias[self.row_id]['dir_row']
        self.col_hdr_idx = self.cubo.lista_guias[self.col_id]['dir_row']

        
    def fmtHeader(self,dimension, separador='\t', sparse=False, rango= None,  max_level=None):
        '''

           TODO documentar
           TODO en el caso de fechas debe formatearse a algo presentable
           TODO some codepaths are not executed by now
        '''
        #print(dimension, separador, sparse, rango,  max_level)

        """
           begin new code
           (funcionalidad abreviada)
        """
        if dimension == 'row':
            indice = self.cubo.lista_guias[self.row_id]['dir_row']
            id=self.row_id
            if max_level is None:
                max_level = self.dim_row
        elif dimension == 'col':
            indice = self.cubo.lista_guias[self.col_id]['dir_row']
            id=self.col_id
            if max_level is None:
                max_level = self.dim_col
        else:
            print('Piden formatear la cabecera >{}< no implementada'.format(dimension))
            exit(-1)

        cab_col = [None for k in range(indice.count() +1)]

        for key in indice.traverse(None,1):
            idx = indice[key].ord
            desc = indice[key].getFullDesc()
            cur_level = indice[key].getLevel() #getLevel(key)
            if cur_level >= max_level:  #odio los indices en 0. siempre off by one 
                continue
            if rango is not None:
                if rango[0] <= idx <= rango[1]:
                    pass
                else:
                    continue
            texto=getOrderedText(desc,sparse,separador)
            # chapuzilla por ver si las fechas pueden modificarse
            cab_col[idx+1]= texto if not sparse else desc[-1]
        return cab_col

def experimental():
    from util.jsonmgr import load_cubo
    def presenta(vista):
        guia=vista.row_hdr_idx
        ind = 0
        for key in guia.traverse(mode=1):
            elem = guia[key]
            print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
            ind += 1
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['experimento'])
    #pprint(cubo.definition)
    #pprint(cubo.definition)
    #pprint(cubo.lista_funciones)
    #pprint(cubo.lista_campos)
    #pprint(cubo.lista_guias[6])
    for ind,guia in enumerate(cubo.lista_guias):
        print(ind,guia['name'])
    #cubo.fillGuias()
    #ind= 5
    #cubo.fillGuia(ind)
    #cubo.lista_guias[ind]['dir_row'].display()
    #pprint(cubo.lista_guias[ind]['dir_row'].content)
    #for node in cubo.lista_guias[ind]['dir_row'].traverse(None,2):
        #print(node)
    #pprint(sorted(cubo.lista_guias[1]['dir_row'])) esto devuelve una lista con las claves
    #pprint(cubo.lista_guias)

    #cubo.fillGuia(1)
    ##pprint(cubo.lista_guias[5])   
    #guia=cubo.lista_guias[5]['dir_row']
    #ind = 0
    #for key in guia.traverse(mode=1):
        #elem = guia[key]
        #print (ind,key,elem.ord,elem.desc)
        #ind += 1

    vista=Vista(cubo,3,0,'sum','votes_presential')
    #pprint(vista.grandTotal())
    #tabla = vista.toKeyedTable()
    vista.toTree2D()
    vista.recalcGrandTotal()
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #print(col_hdr)
    #for key in vista.row_hdr_idx.content:
        #elem = vista.row_hdr_idx[key]
        #print(elem,elem.itemData,elem.depth())
    #vista.traspose()
    #row_hdr = vista.fmtHeader('row',separador='\n',sparse='True')
    #print(col_hdr)
    #for key in vista.row_hdr_idx.content:
        #elem = vista.row_hdr_idx[key]
        #pprint(elem)
    #print(vista.row_hdr_idx.count())
    #presenta(vista)
    #print(vista.dim_row)
    #vista.row_hdr_idx.rebaseTree()
    #pprint(vista.row_hdr_idx.content)
    #print(vista.row_hdr_idx['//'].key)
    #for key in vista.row_hdr_idx.traverse(None,1):
        ##print(key,vista.row_hdr_idx[key].desc,vista.row_hdr_idx[key].getFullDesc(),getOrderedText(vista.row_hdr_idx[key].getFullDesc(),sparse=False,separator=':'))
        #print(key,vista.row_hdr_idx[key].desc,vista.row_hdr_idx[key].depth())
    #for elem in vista.array:
        #print(elem[0].desc,elem[1].desc,elem[2])
    
    #tabla = vista.toTable()    
    #row_hdr = vista.fmtHeader('row',sparse=True)
    ####pprint(row_hdr)
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #pprint(col_hdr)
    #idx = 0
    #print('',col_hdr)
    #for ind,record in enumerate(tabla):

        #stat_data=stats(record)
        #for idx,item in enumerate(record):
            #if item is None:
                #continue
            #if item <= stat_data['out_low'] or item >= stat_data['out_hig']:
                #print('{} en {}:  {} es un outlier'.format(row_hdr[ind +1],col_hdr[idx+1],item))
        

        
    #tabla = vista.toIndexedTable()    
    #row_hdr = vista.fmtHeader('row',sparse=True)
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #idx = 0
    #print('',col_hdr)
    #for record in  tabla:
        #print(row_hdr[record[0]['idx']],record[1:])
        #idx += 1



if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    reload(sys)
    sys.setdefaultencoding('utf-8')

    experimental()
        
