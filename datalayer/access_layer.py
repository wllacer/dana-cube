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
            
def getCursor(db, sql_string,funcion=None,**kwargs):
    '''
        ante una query devuelve un cursor normalizado:  una lista de registros, que a su vez es una lista de campos.
        aisla las 'peculiaridades' de QtSql, y permite el preprocesamiento de los registros individuales
        Los parametros son :
           db la conexion a base de datos
           sql_string lo que se va a ejecutar
           una función que se aplica a cada uno de los registros individualmente
           **kwargs el diccionario de rigor para parametros variable
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
            if callable(funcion):
                funcion(row,**kwargs)
            cursor.append(row)
    return cursor

def getFunctions(db,plista = None):
    '''
      Devuelve la lista de funciones agregadas que soporta la base de datos
    '''
    if plista is None or len(plista ) == 0:
        lista_funciones = ['count', 'max', 'min', 'avg', 'sum']
    else:
        lista_funciones = plista[ : ]
    #TODO include functions which depend on DB driver
    return lista_funciones
