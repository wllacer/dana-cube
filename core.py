#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4.QtCore import *
#from PyQt4.QtGui import *
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
            print 'No se especifico definicion valida '
            sys.exit(-1)
        
        # los datos siguientes son la definicion externa del cubo
        #try:
        self.tabla = definicion['table']
        self.modelo=definicion['guides']
        self.filtro_base = definicion['base filter'] 
        self.campos = definicion['fields']
        #except KeyError:
        #    print 'Error en los parametros de definicion del cubo'
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
                                                'source':campo, 
                                                'prod':[prod, ]
                                              })
                    j += 1
                    
        #dump_structure(self.lista, "lista_dump.yml")
        
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
            print 'conexion a bd imposible'
            sys.exit(-1)
            
        
    def putIndex(self, sql_string, num_fields=1):
    
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
        
    def putGuidesModelo(self):
        if self.db is None:
            return None
        
        coreString = 'from %s ' % self.tabla
        if self.filtro_base <> '':
            coreString += 'where %s ' % self.filtro_base
        
        date_cache={}

        for entrada in self.lista:
            tipo = entrada['type']
            entrada['indice'] = []
            
            if    tipo == 'o':
                campo = entrada['prod'][0]['elem']
                sqlString = 'select distinct %s '%campo
                sqlString += coreString + ' order by 1'
                entrada['indice'].append(self.putIndex(sqlString))
                
            elif tipo == 'd':
                campo = entrada['source']
                fmt = entrada['prod'][0]['mask']
                if campo not in date_cache:
                    sqlString = 'select max(%s),min(%s) ' % (campo, campo)
                    sqlString += coreString
                    row=self.putIndex(sqlString, 2)   #obtenemos  la fecha maxima y minima
                    date_cache[campo] = (row[0][0], row[0][1])
                    
                max_date = date_cache[campo][0]
                min_date  = date_cache[campo][1]
                
                entrada['indice'].append (getDateIndex(max_date, min_date, fmt))
            elif tipo == 'h':
                campo = ''
                idx =1
                indices = []
                for level in entrada['prod']:
                    if campo == '':
                        campo = level['elem']
                        orstring = '%d'%idx
                    else:
                        idx += 1
                        campo += ',' + level['elem']
                        orstring += ',%d'%idx
                    sqlString = 'select distinct %s '%campo
                    sqlString += coreString 
                    sqlString += 'order by %s'%orstring
                    indices.append(self.putIndex(sqlString, idx))
                entrada['indice'] = indices
#



class Vista:
    def __init__(self, cubo,row, col,  agregado='sum', campo='fact', filtro=''):
        
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
        self.dim_row = None
        self.dim_col = None
        self.hierarchy= False
        self.array = []

        self.setNewView(row, col)

    def setNewView(self,row, col):
        dim_max = len(self.cubo.lista)
        if row < dim_max and col < dim_max:
            if self.row_id <> row or self.col_id <> col:
    
                self.row_id = row
                self.col_id = col
                

                self.cur_row=self.cubo.lista[self.row_id]
                self.cur_col = self.cubo.lista[self.col_id]
 
                self.dim_row = len(self.cur_row['indice'])
                self.dim_col = len(self.cur_col['indice'])

                print self.cur_row['name'], self.cur_col['name']
                
                if self.cur_row['type'] == 'h' or self.cur_col['type'] == 'h':
                    self.hierarchy = True
                    
                indices = [ 0 for i in range(0,self.dim_row)]
                rows = [self.cur_row['indice'][i] for i in range(0,self.dim_row)] 
                num_rows = [len(rows[i]) for i in range(0, self.dim_row)]
           
                self.merge_list(0, indices, rows, num_rows,self.dim_row, list(), self.row_idx)
                
                indices = [ 0 for i in range(0, self.dim_col)]
                cols = [self.cur_col['indice'][i] for i in range(0, self.dim_col)] 
                num_cols = [len(cols[i]) for i in range(0, self.dim_col)]

                self.merge_list(0, indices, cols, num_cols,self.dim_col, list(), self.col_idx)
            
                self.array=[[None for y in range(len(self.col_idx))] for x in range(len(self.row_idx))]
    

                self.putDataMatrixH()
        else:
            print 'Limite dimensional excedido. Ignoramos'
        
    def putDataMatrixH(self):
        if self.db is None:      
            return None

        coreString = '%s(%s) from %s ' % (self.agregado, self.campo, self.cubo.tabla)
        if self.cubo.filtro_base <> '' and self.filtro <> '':
            coreString += 'where %s and %s ' % (self.cubo.filtro_base, self.filtro)
        elif self.filtro <> '' or self.cubo.filtro_base <> '':
            filtro_def = self.filtro + self.cubo.filtro_base 
            coreString += 'where %s ' % (filtro_def)

        
        
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
                print i, j, sql_string

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
            #print cabecera
            eje_x = getLevel(self.row_idx[i])
            #print data
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
            #print data
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
 
    def  merge_list(self, level, indices, rows, num_rows,max_level, estado, result_list):
        
        #print(level, indices,num_rows,max_level, estado)
        
        if level >= max_level:
            return False
        cur_index = indices[level]
        if cur_index < num_rows[level]:
            pass
        else:
            return False
        cur_record = rows[level][cur_index]
        #print cur_record
        #print estado
        estamos = True
        while estamos:
            for i in range(0, level):
                if estado[i] != cur_record[i]:
                    #print 'rompen ', i, estado[i], cur_record[i]
                    estamos = False
                    break
            if not estamos:
                break
            entry = [ None for i in range(0, max_level)]
            for i in range(0, level +1):
                entry[i]=cur_record[i]
                
            result_list.append(entry)
            nestado = cur_record
            if (level +1 ) < max_level :
                self.merge_list(level +1, indices, rows, num_rows, max_level, nestado, result_list)
            indices[level] += 1
            if indices[level] >= num_rows[level]:
                break
            else:
                cur_record = rows[level][indices[level]]
    
#def main():
#    app = QApplication(sys.argv)
#    w = QTextBrowser()
#    
#    my_cubos = load_cubo()
#    cubo = Cubo(my_cubos['datos disco'])
##    db = cubo.getDatabase()
##    if db is None: 
##        html = QString('<html><body>')
##        html += 'Error de Conexion en la BD. Terminando'    
##        w.setHtml(html)
##        w.show()
##        sys.exit(app.exec_())
#    cubo.putGuidesModelo()
#    vista = Vista(cubo, 0, 1)
#    #vista.setNewView(3,  4)
#    html = QString('<html><body>')
#    html += vista.showTableDataH() 
#    html += '</body></html>'
#    w.setHtml(html)            
#    w.show()
##    tabla = []
##    for i in range(0, 5):
##        antes = datetime.now()
##        vista.putDataMatrixH()
##        delta = datetime.now() -antes
##        tabla.append(delta.total_seconds())
##    print tabla
##    print fivesummary(tabla)
##    print avg(tabla)
##    
#    #vista.showTableData(w) #, cubo)
#    sys.exit(app.exec_())
#
#if __name__ == "__main__":
#    main()
#
#'''
#Campo:<select_list> Funcion: <select_list>* elements depend on format of campo
#Lista (excluye campo si forma parte)
#'''

