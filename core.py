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
# 0.3
TODO si utilizo un filter en la guia ¿deberia que estar en la query?
FIXME y propagarse en el filtro si es jerarquico
# FIXED la union de filtros no funcionaba. Faltaba el AND
# DONE esto es una funcion reutilizable mergeString
#FIXED ahora si el indice no existe para un valor no se dispara error
#TODO En ciertas circunstancias debe o no provocarse y/o informar del error

'''


from util.record_functions import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from datemgr import getDateSlots,getDateIndex
from pprint import *

def mergeString(string1,string2,connector):
    if len(string1.strip()) > 0 and len(string1.strip()) > 0:
        merge ='{} {} {}'.format(string1,connector,string2)
    elif len(string1.strip()) > 0 or len(string2.strip()) > 0: 
        merge ='{}{}'.format(string1,string2).strip()
    else:
        merge = ''
    return merge

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
        

        self.setGuias()
        self.lista_funciones = getAgrFunctions(self.db,self.lista_funciones)
        # no se usa en core. No se todavia en la parte GUI
        self.lista_campos = self.getFields()
    #
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
          #REFINE grouped by determina la jerarquia explicitamente.
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
          sqlDef['fields'] = entrada['elem'].split(",")
          
        code_fld = len(sqlDef['fields']) - desc_fld  
        
        
        sqlDef['order'] = [ str(x + 1) for x in range(code_fld)]
        
        sqlDef['select_modifier']='DISTINCT'
        
        sqlString = queryConstructor(**sqlDef)
        return sqlString, code_fld,desc_fld 
    
    def setGuidesDateSqlStatement(self, entrada, fields=None):
        #REFINE creo que fields sobra
        sqlDef=dict()
        sqlDef['tables'] = self.definition['table']
        if len(self.definition['base filter'].strip()) > 0:
           sqlDef['base_filter']=self.definition['base filter']
        sqlDef['fields'] = [[entrada['elem'][0],'max'],
                            [entrada['elem'][0],'min'],
                            ]
        return queryConstructor(**sqlDef)            
 
    def setGuias(self):
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
 
           * YA NO cursor el resultado normalizado (con rellenos) y agreagado de la guia en todos sus niveles
           * dir_row el array indice (para realizar busquedas)
           * des_row el array con la descripción  TODO es mejorable su proceso
           
           Estos tres últimos elemnentos se cargan en self.fillGuias; separado para poder refrescarlo en cualquier
           momento
           
           El comportamiento para guias de formato fecha es totalmente distinto del resto. TODO documentar proceso
           
           FIXME Funciona perfectamente con el ejemplo que uso, necesito explorar otras posibilidades de definicion
           
        '''
        #TODO Mejorar los nombres de las fechas
        #TODO indices con campos elementales no son problema, pero no se si funciona con definiciones raras

        
        self.lista_guias = []
        ind = 0
        
        nombres = [ entrada['name'] for entrada in self.definition['guides'] ]
        #indice = nombres.index('partido')
        #pprint(self.definition['guides'][indice])
        
        for entrada in self.definition['guides']:
            # las guias clase = 'd' generan varias entradas
            if entrada['class'] == 'd':
                (slots,datetrees) = getDateSlots(entrada['prod'][0]['elem'],self.dbdriver)
                #primero las jerarquizadas
                for elemento in datetrees:
                    self.lista_guias.append({'name':entrada['name'] +'_'+ elemento[-1]['mask'],
                                             'class':'d','rules':[],'elem':[],
                                             'formula':elemento})
                    ind += 1
                # luego las individuales
                for elemento in slots:
                    self.lista_guias.append({'name':entrada['name'] +'_'+ elemento['mask'],
                                             'class':'d','rules':[],'elem':[],
                                             'formula':elemento})
                    ind += 1
            else:
                self.lista_guias.append({'name':entrada['name'],'class':entrada['class'],'rules':[],'elem':[]})
                ind += 1

          
        for entrada in self.lista_guias:
            if 'formula' in entrada:
                if isinstance(entrada['formula'],dict):  #error de definicion en getDateSlots. FIXME deberia desaparecer
                    produccion = [entrada['formula'],]
                else:
                    produccion = entrada['formula']
            else:
                produccion = self.definition['guides'][nombres.index(entrada['name'])]['prod']
            
            for componente in produccion:
                if 'name' in componente:
                    nombre = componente['name']
                else:
                    nombre = entrada['name']
                if 'class' in componente:
                    clase = componente['class']
                else:
                    clase = entrada['class']
                ##TODO hay que normalizar lo de los elementos
                if isinstance(componente['elem'],(list,tuple)): 
                    entrada['elem'] += componente['elem']
                else:
                    entrada['elem'] += [componente['elem'],]
                if clase == 'd':
                    entrada['rules'].append({'string':'',
                                'ncode':len(entrada['elem']),
                                'ndesc':0,
                                'elem':[componente['elem'],],
                                'name':nombre +'_'+ componente['mask'],
                                'date_fmt': componente['mask'],
                                'class':clase
                                })
                elif clase == 'c':
                    entrada['rules'].append({'string':'',
                                'ncode':len(entrada['elem']),
                                'ndesc':0,
                                'elem':[componente['elem'],],
                                'name':nombre,
                                'class':clase,
                                'enum':componente['categories'],
                                })

                else:

                    #entrada['elem'] += componente['elem'].split(',')
                    (sqlString,code_fld,desc_fld) = self.setGuidesSqlStatement(componente,[])
                    entrada['rules'].append({'string':sqlString,
                                                    'ncode':code_fld,
                                                    'ndesc':desc_fld,
                                                    'elem':entrada['elem'][:],
                                                    'name':nombre,
                                                    'class':clase})
                if 'fmt' in componente:
                    entrada['rules'][-1]['fmt']=componente['fmt']
                if 'enum_fmt' in componente:
                    entrada['rules'][-1]['enum_fmt']=componente['enum_fmt']
                if clase == 'c':
                    entrada['rules'][-1]['elem'][-1]=caseConstructor(entrada['rules'][-1])
            #pprint(entrada)
            #no deberia serme util 
            #if 'formula' in entrada:    
                #del entrada['formula']
            
    def fillGuias(self):
        # TODO documentar y probablemente separar en funciones
        # TODO ahora debo de poder integrar fechas y categorias dentro de una jerarquia
        #      probablemente el cursor += no es lo que se necesita en estos casos
        date_cache = {}
        for ind,entrada in enumerate(self.lista_guias):
            cursor = []
            for idx,componente in enumerate(entrada['rules']):
                lista_compra={'nkeys':componente['ncode'],'ndesc':componente['ndesc']}
                if componente['ncode'] < len(entrada['elem']):
                    lista_compra['nholder']=len(entrada['elem'])-componente['ncode']
                    if componente['ndesc'] != 1:
                        lista_compra['pholder'] = - componente['ndesc']
                        
                if componente['class'] == 'd':
                    #REFINE asumo que solo existe un elemento origen en los campos fecha
                    campo = componente['elem'][-1]
                    # obtengo la fecha mayor y menor
                    if campo in date_cache:
                        pass
                    else:
                        sqlString = self.setGuidesDateSqlStatement(componente)
                        row=getCursor(self.db,sqlString)
                        date_cache[campo] = [row[0][0], row[0][1]] 
                    cursor += getDateIndex(date_cache[campo][0]  #max_date
                                                   , date_cache[campo][1]  #min_date
                                                   , componente['date_fmt'],
                                                   **lista_compra)
                    print(ind,idx,sqlString,lista_compra)
                elif componente['class'] == 'c':
                    #FIXME placeholders, etc
                    nombres = [ [item['result'] if 'result' in item else item['default'],] for item in componente['enum']]
                    cursor += sorted(nombres)
                else:  
                    sqlstring=componente['string']
                    print(ind,idx,sqlstring,lista_compra)
                    cursor += getCursor(self.db,sqlstring,regHashFill,**lista_compra)
                
                cursor = sorted(cursor)
                entrada['dir_row']=[record[0] for record in cursor]  #para navegar el indice con menos datos
                # pensado con descripciones en mas de un campo. la sintaxis luego es una pes
                if componente['ndesc'] == 0:
                    entrada['des_row']=[[record[0],] for record in cursor ] 
                else:
                    entrada['des_row']=[record[-componente['ndesc']:] for record in cursor] 
                
                #print(time.strftime("%H:%M:%S"),dir_row[0])
                #print(time.strftime("%H:%M:%S"),dir_row[0])
                
class Vista:
    #TODO falta documentar
    #TODO falta implementar la five points metric
    def __init__(self, cubo,row, col,  agregado, campo, filtro=''):
        
        self.cubo = cubo
        # deberia verificar la validez de estos datos
        self.agregado=agregado
        self.campo = campo
        self.filtro = filtro
        
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None

        self.row_hdr_idx = list()
        self.col_hdr_idx = list()
        self.row_hdr_txt = list()
        self.col_hdr_txt = list()

        self.dim_row = None
        self.dim_col = None
        self.hierarchy= False
        self.array = []
        
        self.setNewView(row, col)
        
    def setNewView(self,row, col, agregado=None, campo=None, filtro=''):
        
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
            
        if procesar:
        
            self.row_id = row
            self.col_id = col
            
            self.dim_row = len(self.cubo.lista_guias[row]['rules'])
            self.dim_col = len(self.cubo.lista_guias[col]['rules'])
            if  self.dim_row  > 1 or self.dim_col > 1: #No se si es necesario
                self.hierarchy = True
            
            self.row_hdr_idx = self.cubo.lista_guias[row]['dir_row']
            self.col_hdr_idx = self.cubo.lista_guias[col]['dir_row']
            self.row_hdr_txt = self.cubo.lista_guias[row]['des_row']
            self.col_hdr_txt = self.cubo.lista_guias[col]['des_row']
        
            self.setDataMatrix()
            
    def  setDataMatrix(self):
         #TODO clarificar el codigo
         #REFINE solo esperamos un campo de datos. Hay que generalizarlo
        self.array = [ [None for k in range(len(self.col_hdr_idx))] for j in range(len(self.row_hdr_idx))]

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
                lista_compra={'row':{'nkeys':len(self.cubo.lista_guias[self.row_id]['rules'][i]['elem'])},
                              'col':{'nkeys':len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem']),
                                     'init':-1-len(self.cubo.lista_guias[self.col_id]['rules'][j]['elem'])}
                              }
                print('Datos ',sqlstring,lista_compra)
                cursor_data=getCursor(self.cubo.db,sqlstring,regHasher2D,**lista_compra)
                #print(time.strftime("%H:%M:%S"),cursor_data[0])
                for record in cursor_data:
                    try:
                        row_idx = self.row_hdr_idx.index(record[0])
                        col_idx = self.col_hdr_idx.index(record[1])
                    #REFINE En ciertas circunstancias debe o no provocarse y/o informar del error
                    except ValueError:
                        continue
                    #print('{} de {}, {} de {}'.format(row_idx,len(dir_row),col_idx,len(dir_col)))
                    self.array[row_idx][col_idx] = record[-1]

    def fmtHeader(self,dimension, separador='\t', sparse=False, rango= None,  max_level=None):
        '''
           TODO puede simplificarse
           TODO documentar
           TODO en el caso de fechas debe formatearse a algo presentable
        '''
        #print(dimension, separador, sparse, rango,  max_level)
        cab_col = []
        if dimension == 'row':
            indice = self.cubo.lista_guias[self.row_id]['dir_row']
            datos  = self.cubo.lista_guias[self.row_id]['des_row']
            if max_level is None:
                max_level = self.dim_row
        elif dimension == 'col':
            indice = self.cubo.lista_guias[self.col_id]['dir_row']
            datos = self.cubo.lista_guias[self.col_id]['des_row']
            if max_level is None:
                max_level = self.dim_col
        else:
            print('Piden formatear la cabecera >{}< no implementada'.format(dimension))
            exit(-1)
            
        for ind,key in enumerate(indice):
            cur_level = getLevel(key)
            if cur_level >= max_level:  #odio los indices en 0. siempre off by one 
                continue
            if rango is not None:
                if rango[0] <= ind <= rango[1]:
                    pass
                else:
                    continue
            #FIXME primera iteracion. Altamente ineficiente con indices chungos
            tmp_table = datos[ind][:]
            if len(tmp_table) >= cur_level +1:
                if sparse:
                    for k in range(0,cur_level):
                        tmp_table[k]=' '*8
                base = separador.join(tmp_table)
            else:
                tmp_idx_arr = key.split(':')
                base = separador.join(tmp_table)
                for k in range(cur_level,0,-1):
                    if not sparse:
                        idx=':'.join(tmp_idx_arr[0:k])
                        texto = separador.join(datos[indice.index(idx)])
                    else:
                        texto = ' '*8
                    base = '{}{}{}'.format(texto,separador,base)
                    
            cab_col.append(base)
                
               
        return cab_col

def experimental():
    from util.jsonmgr import load_cubo
    vista = None
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos['experimento'])
    #pprint(cubo.definition)
    #pprint(cubo.definition)
    #pprint(cubo.lista_funciones)
    #pprint(cubo.lista_campos)
    pprint(cubo.lista_guias)
    cubo.fillGuias()
    #pprint(cubo.lista_guias[2])
    #pprint(cubo.lista_guias[6])   
    vista=Vista(cubo,2,0,'sum','votes_presential')
    idx = 0
    print('',vista.col_hdr_txt)
    for record in vista.array:
        print(vista.row_hdr_txt[idx],record)
        idx += 1



if __name__ == '__main__':
    experimental()
        
