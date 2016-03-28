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

from PyQt4.QtSql import *

from decimal import *
from pprint import *
from datetime import *

from fivenumbers import *
from yamlmgr import *
from datemgr import *

    
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
        #try:
        self.tabla = definicion['table']
        self.modelo=definicion['guides']
        self.filtro_base = definicion['base filter'] 
        self.campos = definicion['fields']
        #except KeyError:
        #    print( 'Error en los parametros de definicion del cubo')
        #    sys.exit(-1)
        self.db = self.setDatabase(definicion['connect'])
        
 
    # ahora generamos las definiciones internas para las fechas
        ind = -1
        dbdriver = definicion['connect']['driver']
        

        # ahora generamos una lista medio decente de manejar para las presentaciones
        '''
        estructura de la lista
            0 -> nombre
            1 -> type
            2 -> model.row
            3 -> model.col (prod)
            3,,n indices
        '''
        self.lista=list()
        for i in range(0, len(self.modelo)):
            entrada = self.modelo[i]
            if entrada['class'] != 'd':
                self.lista.append({'name':entrada['name'], 
                                            'type':entrada['class'],
                                            'prod':entrada['prod']
                                          })
            else:
                campo = entrada['prod'][0]['elem']
                j = 0
                for prod in getDateSlots(campo, dbdriver):
                    self.lista.append({'name':prod['name'], 
                                                'type':entrada['class'],
                                                'base_fld':campo, 
                                                'prod':[prod, ]
                                              })
                    j += 1
                    
        #dump_structure(self.lista, "lista_dump.yml")
        self.lista_funciones = []
        self.lista_funciones = self.getFunctions()
        self.lista_campos = []
        self.lista_campos = self.getFields()
    # 
    def setDatabase(self, constring):
        db = QSqlDatabase.addDatabase(constring['driver']);
        
        db.setDatabaseName(constring['dbname'])
        
        if constring['driver'] != 'QSQLITE':
            db.setHostName(constring['dbhost'])
            db.setUserName(constring['dbuser'])
            db.setPassword(constring['dbpass'])
        
        ok = db.open()
        # True if connected
        if ok:        
            return db
        else:
            print('conexion a bd imposible')
            sys.exit(-1)
            
        
    def getCursor(self, sql_string, num_fields=1):
    
        if self.db is None:
            return None
        indices = []
        query = QSqlQuery(self.db)
        if query.exec_(sql_string):
            while query.next():
                row = []
                for i in range(0,num_fields):
                    row.append(query.value(i).toString())
                indices.append(row)
        return indices

    def getIndex(self, sql_string, num_fields=1, num_desc=0):
        if self.db is None:
            return None
        indices = []
        desc    = []
        query = QSqlQuery(self.db)
        if query.exec_(sql_string):
            while query.next():
                row = []
                for i in range(0,num_fields):
                    row.append(query.value(i).toString())
                indices.append(row)
                row_d = []
                if num_desc == 0:
                    desc.append(row[ : ])
                else :
                    for i in range(0, num_fields - num_desc):
                        row_d.append(None)
                    for j in range(num_fields, num_desc +  num_fields):
                        row_d.append(query.value(j).toString())
                    desc.append(row_d)

        return indices, desc

    def getSqlStatement(self, entrada, fields):
        code_fld = 0
        desc_fld = 0
        fldString = ''
        coreString = ''
        if 'source' in entrada.keys():
            fuente = entrada['source']
            coreString = 'from %s ' % fuente['table']
            if 'filter' in fuente.keys():
                coreString += 'where %s ' % fuente['filter']
        
            if 'desc' in fuente.keys():
                fldString = fuente['code'] +',' + fuente['desc']
                desc_fld = fldString.count(',')
            else:
                fldlString = fuente['code']

            
            if 'grouped by' in fuente.keys():
                fldString = fuente['grouped by'] + ',' + fldString
            
            elif len(fields) > 0:
                fldString = ','.join([campo for campo in fields]) + ',' + fldString

            
        else:
            coreString = 'from %s ' % self.tabla
            if self.filtro_base !='':
                coreString += 'where %s ' % self.filtro_base

            
            fldString = entrada['elem']
            
            if len(fields) > 0:
                fldString = ','.join([campo for campo in fields]) + ',' + fldString
                
        code_fld = fldString.count(',') + 1 - desc_fld        
        orderString = ','.join([ str(x + 1) for x in range(code_fld)])
        orderString = 'order by '+orderString
        sqlString = 'select distinct '+fldString + ' ' + coreString + ' ' + orderString
        return sqlString, code_fld,desc_fld 
    
    def getGuides(self):
        if self.db is None:
            return None
            
        coreString = 'from %s ' % self.tabla
        if self.filtro_base !='':
            
            coreString += 'where %s ' % self.filtro_base
        date_cache={}
        
        for entrada in self.lista:
            entrada['indice'] = []
            entrada['cabecera'] =  []
            campos = []
            for ind, regla in enumerate(entrada['prod']):
                idx = ind +1
                if entrada['type'] != 'd':
                    (sqlString, code_fld, desc_fld) = self.getSqlStatement(entrada['prod'][idx -1], campos )
                    campos.append(regla['elem'])
                    ind, desc = self.getIndex(sqlString, code_fld, desc_fld)             
                    
                    entrada['indice'].append(ind)
                    entrada['cabecera'].append(desc)

                else:
                    campo = entrada['base_fld']
                    fmt = entrada['prod'][ind]['mask']
                    if campo not in date_cache:
                        sqlString = 'select max(%s),min(%s) ' % (campo, campo)
                        sqlString += coreString
                        row=self.getCursor(sqlString, 2)   #obtenemos  la fecha maxima y minima
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
        if len(self.lista_campos) == 0:
            lista_campos = self.campos[:]
            for entry in self.modelo:
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
        self.db = self.cubo.db
        # deberia verificar la validez de estos datos
        self.agregado=agregado
        self.campo = campo
        self.filtro = filtro
        
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None
        self.cur_row = None
        self.cur_col  = None
        self.row_idx = list()
        self.col_idx = list()
        self.row_hdr_idx = list()
        self.col_hdr_idx = list()
        self.dim_row = None
        self.dim_col = None
        self.hierarchy= False
        self.array = []

        self.setNewView(row, col)

    def setNewView(self,row, col, agregado=None, campo=None, filtro=''):
        dim_max = len(self.cubo.lista)
        if row < dim_max and col < dim_max:
            # validamos los parametros
            procesar = False
            if self.row_id <> row:
                procesar = True
                self.row_id = row
            if self.col_id <> col:
                procesar = True
                self.col_id = col
            if agregado is not None and agregado <> self.agregado:
                procesar = True
                self.agregado = agregado
            if campo is not None and campo <> self.campo:
                procesar = True
                self.campo = campo
            if self.filtro <> filtro:
                procesar = True
                self.filtro = filtro
                
            if procesar:
                self.row_id = row
                self.col_id = col
                
                self.row_idx = list()
                self.col_idx = list()
                self.row_hdr_idx = list()
                self.col_hdr_idx = list()
                
                self.cur_row=self.cubo.lista[self.row_id]
                self.cur_col = self.cubo.lista[self.col_id]
 
                self.dim_row = len(self.cur_row['indice'])
                self.dim_col = len(self.cur_col['indice'])

                print (self.cur_row['name'], self.cur_col['name'])
                
                if self.cur_row['type'] == 'h' or self.cur_col['type'] == 'h':
                    self.hierarchy = True
            
                indices = [ 0 for i in range(0,self.dim_row)]
                rows = [self.cur_row['indice'][i] for i in range(0,self.dim_row)] 
                row_hdr=[self.cur_row['cabecera'][i] for i in range(0,self.dim_row)]
                num_rows = [len(rows[i]) for i in range(0, self.dim_row)]

                self.merge_list(0, indices, rows, num_rows,self.dim_row, list(), self.row_idx, row_hdr, self.row_hdr_idx)

                indices = [ 0 for i in range(0, self.dim_col)]
                cols = [self.cur_col['indice'][i] for i in range(0, self.dim_col)] 
                cols_hdr = [self.cur_col['cabecera'][i] for i in range(0, self.dim_col)] 
                
                num_cols = [len(cols[i]) for i in range(0, self.dim_col)]

                self.merge_list(0, indices, cols, num_cols,self.dim_col, list(), self.col_idx,  cols_hdr, self.col_hdr_idx)
                #self.array=[[None for y in range(len(self.col_idx))] for x in range(len(self.row_idx))]

                self.putDataMatrixH()
        else:
            print( 'Limite dimensional excedido. Ignoramos')
        
    def putDataMatrixH(self):
        
        if self.db is None:      
            return None

        coreString = '%s(%s) from %s ' % (self.agregado, self.campo, self.cubo.tabla)
        if self.cubo.filtro_base <> '' and self.filtro <> '':
            coreString += 'where %s and %s ' % (self.cubo.filtro_base, self.filtro)
        elif self.filtro <> '' or self.cubo.filtro_base <> '':
            filtro_def = self.filtro + self.cubo.filtro_base 
            coreString += 'where %s ' % (filtro_def)

        self.array=[[None for y in range(len(self.col_idx))] for x in range(len(self.row_idx))]
        
        for i in range(self.dim_row):
            row_elem = ''
            for k in range(0, i+1):
                if row_elem <> '':
                    row_elem +=','

                row_dict = self.cur_row['prod'][k]
                row_elem += '%s'%row_dict['elem']

           

            for j in range(self.dim_col):
                col_elem = ''
                for m in range(0, j+1):
                    if col_elem <> '':
                        col_elem += ','
                    col_dict =  self.cur_col['prod'][m]
                    col_elem += '%s'%col_dict['elem']
                group_string = '%s,%s' % (row_elem, col_elem)
                
                select_string = " select %s," % (group_string)
                sql_string = select_string + coreString + 'group by '+group_string
                print (i, j, sql_string)

                query = QSqlQuery(self.db)
                if query.exec_(sql_string):
                    while query.next():
                        row_key=[None for x in range(0, self.dim_row)]
                        col_key =[None for x in range(0, self.dim_col)] 
                        k = 0
                        for r_ind in range(0, i +1):
                            row_key[r_ind] = query.value(k).toString()
                            k += 1
                        
                        row_id = self.row_idx.index(row_key)

                        for c_ind in range(0, j+1):
                            col_key[c_ind] = query.value(k).toString()
                            k += 1

                        col_id  = self.col_idx.index(col_key)

                        self.array[row_id][col_id]=query.value(k).toFloat()
        #pprint(self.array)
        
        
    def getPointLists(self):

        metricplist = [ [ list() for J in range(self.dim_col)] for i in range(self.dim_row)]
        
        
        for i in range(0,len(self.row_idx)):
            #print (cabecera)
            eje_x = getLevel(self.row_idx[i])
            #print(data)
            for j in range(0, len(self.col_idx)):
                eje_y = getLevel(self.col_idx[j])
                
                if self.array[i][j] is not None:
                    metricplist[eje_x][eje_y].append(self.array[i][j][0])
        
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
            html += '<tr>'
            for i in range(0, max_row):
                if k == max_col -1 :
                    if 'name' in self.cur_row['prod'][i].keys():
                        nombre =  self.cur_row ['prod'][i]['name']
                    else:
                        nombre =  self.cur_row ['name']
                else:
                    nombre = ''
                html +=('<th>%s< /th>'% nombre)
            for j in self.col_idx:
#                if max_col == 1:
#                    html +=('<th>%s< /th>'% j[0])
#                else:
                    html += ('<th>%s< /th>'%j[k])
            html +=('</tr>')
            
        for i in range(0,len(self.row_idx)):
            #print cabecera
            
            style = ''
            eje_x = 0
            if self.dim_row > 1:
                eje_x = getLevel(self.row_idx[i])
                if eje_x >= max_row:
                    continue
                if eje_x == 0:
                    style = 'style="color:blue">'
            html += '<tr %s>'%style
            
            for item in self.row_idx[i]:
                html +=('<td>%s< /td>')% str(item)
            #print(data)
            j = 0
            for elem in self.array[i]:
                style=''
                eje_y = 0
                if self.dim_col > 1:
                    eje_y = getLevel(self.col_idx[j])
                    if eje_y >= max_col:
                        continue
                    if eje_y == 0:
                        style = 'style="color:blue"'
                        
                if elem is None or elem == 0:
                    html += ('<td %s></td>')%style
                else:
                    if elem[0] < metrics[eje_x][eje_y][1] or elem[0] > metrics[eje_x][eje_y][5] :
                        style = 'style="color:red"'
                    html +=('<td %s>%d< /td>')% (style, elem[0])
                j += 1
            html += '</tr>'
        html += '</table>'
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

