# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
'''
#from PyQt4.QtSql import *
from PyQt5.QtSql import *

def dbConnect(constring):
    '''
      establece la conexion con una base de datos.
      constring es un diccionario con los parametros necesarios en QtSQl
	  driver,
	  dbname
	  dbhost
	  dbuser
	  dbpass
    '''
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
            
def getCursor(db, sql_string):
    '''
        ante una query devuelve un cursor normalizado:  una lista de registros, que a su vez es una lista de campos.
        aisla las 'peculiaridades' de QtSql
        Los parametros son evidentes:
           db la conexion a base de datos
           sql_string lo que se va a ejecutar
    '''
    if db is None:
	return None
    if sql_string is None or sql_string.strip() == '':
        return None
      
    cursor = []
    query = QSqlQuery(db)
    if query.exec_(sql_string):
	while query.next():
	    row = []
	    for j in range(0,query.record().count()):
	       row.append(query.value(j))   
	    cursor.append(row)
    return cursor

