# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

BACKEND = 'Alchemy' #'Alchemy' #or 'QtSql'
DRIVERS = ('sqlite','mysql','postgresql','oracle') #('db2','odbc') todavia no implementadas
'''
Documentation, License etc.

@package estimaciones
'''
#from PyQt4.QtSql import *
#transitional
from  sqlalchemy import create_engine
from  sqlalchemy.sql import text
from PyQt5.QtSql import *    

#if BACKEND == 'Alchemy':
    #from  sqlalchemy import create_engine
    #from  sqlalchemy.sql import text
#else:
    #from PyQt5.QtSql import *    
    
from pprint import pprint


def driver2if(driver):
    if   BACKEND == 'Alchemy':
        return driver2Qt(driver.lower())
    elif BACKEND == 'QtSql':
        return driver2Alch(driver.lower())
    else:
        print('Not implemented')
        exit(-1)

def driver2Qt(pdriver):
    driver = pdriver.lower()
    if driver in ('sqlite','qsqlite'): #solo compatibilidad codigo actural
        return 'QSQLITE'
    elif driver in ('mysql','mariadb'):
        return 'QMYSQL'
    elif driver ('postgresql','postgres','pg'):
        return 'QPSQL'
    elif driver == 'oracle':
        return 'QOCI'
    else:
        return driver
      
def driver2Alch(pdriver):
    driver = pdriver.lower()
    if driver in ('sqlite','qsqlite'):
        return 'sqlite'
    elif driver in ('mysql','mariadb'):
        return 'mysql+mysqldb'
    elif driver in ('postgresql','postgres','pg'):
        return 'postgresql+psycopg2'
    elif driver == 'oracle':
        return 'oracle+cx_oracle'
    else:
        return driver

# yadada ... y know i could set functions as variables but ...
def dbConnect(constring):
    """
      establece la conexion con una base de datos.
      constring es un diccionario con los parametros necesarios en QtSQl
          driver,
          dbname
          dbhost
          dbuser
          dbpass
    """
    if BACKEND == 'Alchemy':
        return dbConnectAlch(constring)
    elif BACKEND == 'QtSql':
        return dbConnectQt(constring)
    else:
        print('Not implemented')
        exit(-1)
 
def getCursor(db, sql_string,funcion=None,**kwargs):
    """
        ante una query devuelve un cursor normalizado:  una lista de registros, que a su vez es una lista de campos.
        aisla las 'peculiaridades' de QtSql, y permite el preprocesamiento de los registros individuales
        Los parametros son :
           db la conexion a base de datos
           sql_string lo que se va a ejecutar
           una función que se aplica a cada uno de los registros individualmente
           **kwargs el diccionario de rigor para parametros variable
    """
    if BACKEND == 'Alchemy':
        return getCursorAlch(db, sql_string,funcion,**kwargs)
    elif BACKEND == 'QtSql':
        return getCursorQt(db, sql_string,funcion,**kwargs)
    else:
        print('Not implemented')
        exit(-1)
    
def dbConnectAlch(constring):

    driver = driver2Alch(constring['driver'])
    if 'debug' in constring:
        debug=constring['debug']
    else:
        debug=False
    dbname = constring['dbname']
    if constring['driver'] not in ('QSQLITE','sqlite'):
        host = constring['dbhost']
        user = constring['dbuser']
        password = constring['dbpass']
        context = '{}://{}:{}@{}/{}'.format(driver,user,password,host,dbname)
    else:
        print(driver,dbname)
        context = '{}:///{}'.format(driver,dbname)
    engine = create_engine(context,echo=debug)
    return engine.connect()

def dbConnectQt(constring):
    db = QSqlDatabase.addDatabase(driver2Qt(constring['driver']));
    
    db.setDatabaseName(constring['dbname'])
    
    if constring['driver'] not in ('QSQLITE','sqlite'):
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

def getCursorAlch(db, sql_string,funcion=None,**kwargs):
    if db is None:
        return None
    if sql_string is None or sql_string.strip() == '':
        return None
      
    sqlString=text(sql_string)
    cursor= []
    #TODO ¿sera posible que Alch me devuelva directamente una lista?
    for row in db.execute(sqlString):
        trow = list(row) #viene en tupla y no me conviene
        if callable(funcion):
            funcion(trow,**kwargs)
        if trow != []:
            cursor.append(trow)
    return cursor

def getCursorQt(db, sql_string,funcion=None,**kwargs):
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
            if row != []:
                cursor.append(row)
           
    return cursor

def getAgrFunctions(db,plista = None):
    '''
      Devuelve la lista de funciones agregadas que soporta la base de datos
    '''
    if plista is None or len(plista ) == 0:
        lista_funciones = ['count', 'max', 'min', 'avg', 'sum']
    else:
        lista_funciones = plista[ : ]
    #TODO include functions which depend on DB driver
    return lista_funciones
