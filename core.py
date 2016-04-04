#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''

import sys

#from PyQt4.QtSql import *
from PyQt5.QtSql import *

from decimal import *
from pprint import *
from datetime import *

from util.fivenumbers import *
from util.yamlmgr import *
from datemgr import *
from datalayer.access_layer import *
from datalayer.query_constructor import  queryConstructor
    
def getLevel(entry):
    " ojo chequear por el valor -1 "
    if not isinstance(entry, (list, tuple)):
        return 0
    elif len(entry) == 1:
        return 0
    else:
        pos = len(filter(lambda x: x is not None, entry)) -1
                  
    if pos < 0 :
        return 0
    else:
        return pos
        
        
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
        self.lista_guias=list() 
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

        self.lista_funciones = self.getFunctions()

        self.lista_campos = self.getFields()
    #
    
    def getIndex(self, sql_string, num_fields=1, num_desc=0):
        '''
           devuelve dos tablas ligadas (codigo + descripción) para una guia 
           CLEAR code
        '''
        if self.db is None:
            return None
        indices = []
        desc    = []
        print('Index :',sql_string)
        idx_cursor = getCursor(self.db,sql_string)
        for record in idx_cursor:
            indices.append(record[0:num_fields])
            if num_desc == 0:
                desc.append(record[0:num_fields])
            else:
              row_d = [None for k in range(0,num_fields)]
              for j in range(num_fields, num_desc +  num_fields):
                 row_d[num_fields - 1 -j]=record[j]

              desc.append(row_d)
        return indices, desc
    

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
	  fields son campos auxiliares a incluir en la query
	'''
        print()
        print(fields)
        code_fld = 0
        desc_fld = 0
        
        sqlDef=dict()

        if 'source' in entrada.keys():
          sqlDef['tables'] = entrada['source']['table']
          if 'filter' in entrada['source']:
              sqlDef['base_filter']=entrada['source']['filter']
              
          sqlDef['fields'] = []
          if 'grouped by' in entrada['source']:
              sqlDef['fields'] += entrada['source']['grouped by'].split(',')
          if len(fields) > 0:
              sqlDef['fields'] += fields[:]
          sqlDef['fields'] += [entrada['source']['code'],]
          
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
    
                
 
    def getGuides(self):
        if self.db is None:
            return None

        date_cache={}
        
        for entrada in self.lista_guias:
            entrada['indice'] = []
            entrada['cabecera'] =  []
            constructor = []
            campos = []
            for ind, regla in enumerate(entrada['prod']):
                #idx = ind +1
                if entrada['type'] != 'd':
                    (sqlString, code_fld, desc_fld) = self.setGuidesSqlStatement(entrada['prod'][ind], campos )
                    #TODO campos.append(regla['elem'])   Puede ser util en ciertos casos, pero no tengo la casuistica
                    ind, desc = self.getIndex(sqlString, code_fld, desc_fld)             
                    
                    entrada['indice'].append(ind)
                    entrada['cabecera'].append(desc)

                else:
                    campo = entrada['base_fld']
                    fmt = entrada['prod'][ind]['mask']
                    if entrada['base_fld'] not in date_cache:
                        sqlString = self.setGuidesDateSqlStatement(entrada,campos)
                        row=getCursor(self.db,sqlString)
                        date_cache[campo] = (row[0][0], row[0][1])
                        
                    max_date = date_cache[campo][0]
                    min_date  = date_cache[campo][1]
                    
                    entrada['indice'].append (getDateIndex(max_date, min_date, fmt))
                    entrada['cabecera'].append(entrada['indice'][ind][ : ])

                
    def getFunctions(self):
        if len(self.lista_funciones ) == 0:
            lista_funciones = ['count', 'max', 'min', 'avg', 'sum']
        else:
            lista_funciones = self.lista_funciones[ : ]
        #TODO include functions which depend on DB driver
        return lista_funciones

    def getFields(self):
        '''
           crea/devuelve el atributo cubo.lista_campos
           parte de la base de los campos de la definición y añade los campos no textuales de las lista_guias
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

class Vista:
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

        self.setNewView(row, col)

    def setNewView(self,row, col, agregado=None, campo=None, filtro=''):
        dim_max = len(self.cubo.lista_guias)
        if row < dim_max and col < dim_max:
            # validamos los parametros
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
                
                self.row_hdr_idx = list()
                self.col_hdr_idx = list()
                self.row_hdr_txt = list()
                self.col_hdr_txt = list()
                
                self.cur_row=  self.cubo.lista_guias[self.row_id]
                self.cur_col = self.cubo.lista_guias[self.col_id]
 
                self.dim_row = len(self.cur_row['indice'])
                self.dim_col = len(self.cur_col['indice'])

                print (self.cur_row['name'], self.cur_col['name'])
                
                if self.cur_row['type'] == 'h' or self.cur_col['type'] == 'h':
                    self.hierarchy = True
                    
                # INICIO ANTIGUO
                indices = [ 0 for i in range(0,self.dim_row)]
                rows = [self.cur_row['indice'][i] for i in range(0,self.dim_row)] 
                row_hdr=[self.cur_row['cabecera'][i] for i in range(0,self.dim_row)]
                num_rows = [len(rows[i]) for i in range(0, self.dim_row)]

                self.merge_list(0, indices, rows, num_rows,self.dim_row, list(), self.row_hdr_idx, row_hdr, self.row_hdr_txt)

                indices = [ 0 for i in range(0, self.dim_col)]
                cols = [self.cur_col['indice'][i] for i in range(0, self.dim_col)] 
                cols_hdr = [self.cur_col['cabecera'][i] for i in range(0, self.dim_col)] 
                
                num_cols = [len(cols[i]) for i in range(0, self.dim_col)]

                self.merge_list(0, indices, cols, num_cols,self.dim_col, list(), self.col_hdr_idx,  cols_hdr, self.col_hdr_txt)
                #self.array=[[None for y in range(len(self.col_idx))] for x in range(len(self.row_idx))]
                # FIN ANTIGUO
                self.putDataMatrixH()
        else:
            print( 'Limite dimensional excedido. Ignoramos')
            
    def getPos(self,dimension,record,idx_row,idx_col,dim_dimension):
      
      if dimension == 'row':
          ambito = self.row_hdr_idx
          start_pos = 0  #eso deberia venir en los parametros
          end_pos   = start_pos + idx_row + 1
      elif dimension == 'col':
          ambito = self.col_hdr_idx
          start_pos = idx_row +1
          end_pos = start_pos + idx_col +1
      else:
          return None

      #TODO Buscar una clave formada por un array es venenoso.
      #   debo rodear con un try except para capturar cuando el registro no existe
      dim_key=[record[k] for k in range(start_pos,end_pos)] +[ None for k in range(end_pos,dim_dimension)]
      return ambito.index(dim_key)

    def putDataMatrixH(self):
        
        if self.cubo.db is None:      
            return None
            
        #aqui depositare el resultado final  
        self.array=[[None for y in range(len(self.col_hdr_idx))] for x in range(len(self.row_hdr_idx))]  

        # INIT NUEVO
        sqlDef = dict()
        sqlDef['tables']=self.cubo.definition['table']
        if len(self.cubo.definition['base filter'].strip()) > 0 and len(self.filtro.strip()) >0 :
           sqlDef['base_filter'] = '{} AND {}'.format(self.cubo.definition['base filter'], self.filtro)
        else:
            sqlDef['base_filter'] = '{} {}'.format(self.cubo.definition['base filter'], self.filtro).strip()
	# variablea auxiliares
        sqlDef['tgt_fields']=[[self.campo,self.agregado],]
        sqlDef['row_fields']=[ self.cur_row['prod'][k]['elem'] for k in range(self.dim_row)]
        sqlDef['col_fields']=[ self.cur_col['prod'][k]['elem'] for k in range(self.dim_col)]
	
        for i in range(self.dim_row):
            for j in range(self.dim_col):
                sqlDef['fields'] = [sqlDef['row_fields'][k] for k in range(i+1)]+[sqlDef['col_fields'][k] for k in range(j+1)] + \
                                    sqlDef['tgt_fields']
                sqlDef['group']  = [sqlDef['row_fields'][k] for k in range(i+1)]+[sqlDef['col_fields'][k] for k in range(j+1)]
                sqlQuery = queryConstructor(**sqlDef)
                print(i,j,sqlQuery)
                tmp_cursor = getCursor(self.cubo.db,sqlQuery)
                for record in tmp_cursor:  #por razones de rendimiento deberia ser una funcion especial en el getCursor
                    row_id = self.getPos('row',record,i,j,self.dim_row)
                    col_id = self.getPos('col',record,i,j,self.dim_col)
                    self.array[row_id][col_id]=record[-1]
                
	#FIN NUEVO
        #pprint(self.array)
        
        
    def getPointLists(self):

        metricplist = [ [ list() for J in range(self.dim_col)] for i in range(self.dim_row)]
        
        for i in range(0,len(self.row_hdr_idx)):
            #print (cabecera)
            eje_x = getLevel(self.row_hdr_idx[i])
            #print(data)
            for j in range(0, len(self.col_hdr_idx)):
                eje_y = getLevel(self.col_hdr_idx[j])
                
                if not(self.array[i][j] is None):
                    if isinstance(self.array[i][j],(list,tuple,set)):
                       metricplist[eje_x][eje_y].append(self.array[i][j][0])
                    else :
                       metricplist[eje_x][eje_y].append(self.array[i][j])
        
        return metricplist
        
    def fivepointsmetric(self):
        
        metricplist = self.getPointLists()
        metriclist = [  [fivesummary(metricplist[i][j]) for j in range(self.dim_col)]  for i in range(self.dim_row) ]
        
        return metriclist
        
       
    def showTableDataH(self,max_row=99, max_col=99): #,  cubo):
        if max_row >= self.dim_row:
            max_row = self.dim_row 
        if max_col >= self.dim_col:
            max_col = self.dim_col
            
        metrics = self.fivepointsmetric()
    
    
        html =('<table border=1>')
        #header
        for k in range(0, max_col):
            html += ('<tr>')
            for i in range(0, max_row):
                if k == max_col -1 :
                    if 'name' in self.cur_row['prod'][i].keys():
                        nombre =  self.cur_row ['prod'][i]['name']
                    else:
                        nombre =  self.cur_row ['name']
                else:
                    nombre = ''
                html +=('<th>{}< /th>'.format(nombre))
            for j in self.col_hdr_txt:
#                if max_col == 1:
#                    html +=('<th>%s< /th>'% j[0])
#                else:
                    html += ('<th>{}< /th>'.format(j[k]))
            html +=('</tr>')
            
        for i in range(0,len(self.row_hdr_idx)):
            #print cabecera
            
            style = ''
            eje_x = 0
            if self.dim_row > 1:
                eje_x = getLevel(self.row_hdr_idx[i])
                if eje_x >= max_row:
                    continue
                if eje_x == 0:
                    style = 'style="color:blue"'
            html += ('<tr {}>'.format(style))
            
            for item in self.row_hdr_txt[i]:
                html +=('<td>{}< /td>'.format(item))
            #print(data)
            j = 0
            for elem in self.array[i]:
                style=''
                eje_y = 0
                if self.dim_col > 1:
                    eje_y = getLevel(self.col_hdr_idx[j])
                    if eje_y >= max_col:
                        continue
                    if eje_y == 0:
                        style = 'style="color:blue"'
                        
                if elem is None or elem == 0:
                    html += ('<td {}></td>'.format(style))
                else:
                    if elem < metrics[eje_x][eje_y][1] or elem > metrics[eje_x][eje_y][5] :
                        style = 'style="color:red"'
                    html +=('<td {}>{}< /td>'.format(style, elem))
                j += 1
            html += ('</tr>')
        html += ('</table>')
        return html
 
    def  merge_list(self, level, indices, rows, num_rows,max_level, estado, result_list, rows_hdr=[], result_hdr=[]):
        
        #print(level, indices,num_rows,max_level, estado)
        
        if level >= max_level:
            return False
        cur_index = indices[level]
        if cur_index < num_rows[level]:
            pass
        else:
            return False
        cur_record = rows[level][cur_index]
        cur_record_hdr = rows_hdr[level][cur_index]
        #print(estado)
        estamos = True
        while estamos:
            for i in range(0, level):
                if estado[i] != cur_record[i]:
                    #print ('rompen ', i, estado[i], cur_record[i])
                    estamos = False
                    break
            if not estamos:
                break
            entry = [ None for i in range(0, max_level)]
            entry_hdr = entry[ : ]
            for i in range(0, level +1):
                entry[i]=cur_record[i]
            result_list.append(entry)
            for i in range(0, level +1):
                if cur_record_hdr[i] is None:
                    entry_hdr[i] = rows_hdr[i][indices[i]][i]
                else:   
                    entry_hdr[i]=cur_record_hdr[i]
            result_hdr.append(entry_hdr)
            nestado = cur_record
            if (level +1 ) < max_level :
                self.merge_list(level +1, indices, rows, num_rows, max_level, nestado, result_list,  rows_hdr, result_hdr)
            indices[level] += 1
            if indices[level] >= num_rows[level]:
                break
            else:
                cur_record = rows[level][indices[level]]
                cur_record_hdr = rows_hdr[level][indices[level]]

if __name__ == '__main__':
   vista = None
   mis_cubos = load_cubo()
   cubo = Cubo(mis_cubos['datos locales'])
   cubo.getGuides()
   #if cubo is None:
     #print ('vaya pifia')
   #else:
     #print('construi un cubo')
     #print('Definicion      ')
     #pprint(cubo.definition)
     #print('lista_guias     ')
     ##pprint(cubo.lista_guias)
     #print('lista_campos    ',cubo.lista_campos)
     #print('lista_funciones ',cubo.lista_funciones)
     #print('DB              ',cubo.db)
   # 
   row =7
   col =0
   agregado = 'sum'
   campo = 'votes_presential'
   #        
   if vista is None:
      vista = Vista(cubo, row, col, agregado, campo)       
   #else:
   #   vista.setNewView(row, col, agregado, campo)
   #if vista is None:
     #print('Ahora pifie con la vista')
   #else:
     #'''?
        #x_hdr_txt|idx === cur_x['cabecera|indice'] agrupado para la presentacion
       
     #'''
     #print('agregado     ',vista.agregado)
     #print('array        ',vista.array)
     #print('campo        ',vista.campo)
     #print('col_hdr_txt  ',vista.col_hdr_txt)
     #print('col_hdr_idx  ',vista.col_hdr_idx)
     #pprint(vista.col_hdr_idx)
     #print('col_id       ',vista.col_id)
     #print('cubo         ',vista.cubo)
     #print('cur_col      ',vista.cur_col)
     #pprint(vista.cur_row['indice'])
     #print('cur_row      ',vista.cur_row)
     #print('dim_col      ',vista.dim_col)
     #print('dim_row      ',vista.dim_row)
     #print('filtro       ',vista.filtro)
     #print('hierarchy    ',vista.hierarchy)
     #print('row_hdr_txt  ',vista.row_hdr_txt)
     #pprint('row_hdr_idx      ',vista.row_hdr_idx)
     #print('row_id       ',vista.row_id)
     
   #for i in range(len(vista.row_hdr_idx)):
     #if vista.row_hdr_idx[i] != vista.cur_row['indice'][0][i]:
        #print('got cha',vista.row_hdr_idx[i],vista.cur_row['indice'][i])
   pprint(vista.cur_row['indice'])
   #pprint(vista.showTableDataH())
