## -*- coding=utf -*-
"""
Part of  Global Common modules by Werner Llácer (c) 2012-2018

As an integral part of a project distributed under an Open Source Licence, the licence of the proyect
Used as  standalone module or outside the scope of  a project valid according to the  previous paragraph, or when  in doubt, distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

BACKEND = 'Alchemy' #'Alchemy' #or 'QtSql'
DRIVERS = ('sqlite','mysql','postgresql','oracle','db2','odbc') #todavia no implementadas las dos ultimas
AGR_LIST = ('count', 'max', 'min', 'avg', 'sum')
CURR_HANDLERS = {'sqlite':'pysqlite','mysql':'mysqlconnector','postgresql':'psycopg2','oracle':'cx_oracle','db2':None,'odbc':None}
DEFAULT_SCHEMA = {'sqlite':'main','mysql':'@dbname','postgresql':'public','oracle':'@dbuser','db2':None,'odbc':None}
SYSTEM_SCHEMAS = {'mysql':('information_schema','mysql','performance_schema'),
                  'postgresql':('information_schema',),
                  'oracle':('anonymous','apex_public_user','apex_040000','ctxsys','flows_files','mdsys','outln','sys','system','xdb','xs$null')
                }
SUPPORTS_ROLLUP = {'sqlite':False,'mysql':False,'postgresql':True,'oracle':True,'db2':True,'odbc':True }
'''
Documentation, License etc.

@package estimaciones
'''
#from PyQt4.QtSql import *
#transitional
from support.datalayer.query_constructor import queryFormat
from support.util.record_functions import norm2String

from  sqlalchemy import create_engine,types, inspect
from  sqlalchemy.sql import text
from PyQt5.QtSql import *    
from PyQt5.QtGui import QStandardItemModel, QStandardItem
#if BACKEND == 'Alchemy':
    #from  sqlalchemy import create_engine
    #from  sqlalchemy.sql import text
#else:
    #from PyQt5.QtSql import *    
    
from pprint import pprint
import datetime 

def qtSqlDeprecated():
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)

    msg.setText("El Backend QtSql ha sido deprecado")
    msg.setWindowTitle("Backend incorrecto")
    msg.setDetailedText(""" Ya no ofrecemos la opcion de utilizar QtSql como gestor de accesos a las bases de datos. se activa automaticamente SqlAlchemy """)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()

def typeHandler(type):
    if  isinstance(type,(types.Numeric)):
          return 'numerico'
    elif isinstance(type,(types.Integer,types.BigInteger)):
          return 'entero'
    elif isinstance(type,types.String):
          return 'texto'
    elif isinstance(type,(types._Binary,types.LargeBinary)):
          return 'binario'
    elif isinstance(type,types.Boolean):
          return 'booleano'
    elif isinstance(type,types.Date):
          return 'fecha'
    elif isinstance(type,types.DateTime):
          return 'fechahora'
    elif isinstance(type,types.Time):
          return 'hora'
    else:
          # print('Tipo {} no contemplado'.format(type))
          return '{}'.format(type)
    return None

def driver2if(driver):
    if   BACKEND == 'Alchemy':
        return driver2Alch(driver.lower())
    elif BACKEND == 'QtSql':
        return driver2Qt(driver.lower())
    else:
        print('Not implemented')
        exit(-1)

#DRIVERNAME
def driver2Qt(pdriver):
    driver = pdriver.lower()
    if driver in ('sqlite','qsqlite'): #solo compatibilidad codigo actural
        return 'QSQLITE'
    elif driver in ('mysql',):
    #elif driver in ('mysql','mariadb','mysqldb','msyqlconnector'):
        return 'QMYSQL'
    elif driver ('postgresql',):
    #elif driver ('postgresql','postgres','pg','psycopg2'):
        return 'QPSQL'
    elif driver == 'oracle':
        return 'QOCI'
    else:
        return driver
      
def internal2genericDriver(pdriver):
    if not pdriver:
        return None
    for external in CURR_HANDLERS:
        if CURR_HANDLERS[external] == pdriver:
            return external
            break #innecesario pero clarificador
    return None

def setLimitString(string,db,**kwargs):
    lim = kwargs.get('LIMIT')
    off = kwargs.get('OFFSET')
    if lim:
        driver = db.dialect.name
        tmpstring = ''
        if driver in ('sqlite','mysql','postgresql'):
            tmpstring= ' LIMIT {} '.format(lim)
            if off:
                tmpstring = tmpstring + ' OFFSET {}'.format(off)
        else:
            #TODO
            pass
        return tmpstring
    return ''

def driver2Alch(pdriver):
    driver = pdriver.lower()
    if driver in ('sqlite','qsqlite'):
        return 'sqlite'
    #elif driver in ('mysql','mysqlconnector','mariadb'):  #FIXME
    elif driver in ('mysql','postgresql','oracle'):
        return driver + '+' + CURR_HANDLERS[driver]
    #elif driver in ('mysql',):  #FIXME
        #return 'mysql+mysqlconnector'
    ##elif driver in ('mysqldb',):
        ##return 'mysql+mysqldb'
    ##elif driver in ('postgresql','postgres','pg','psycopg2'): #FIXME
    #elif driver in ('postgresql',): #FIXME
        #return 'postgresql+psycopg2'
    #elif driver == 'oracle':
        #return 'oracle+cx_oracle'
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
    global BACKEND
    if BACKEND == 'QtSql':
        qtSqlDeprecated()
        BACKEND = 'Alchemy'
        return dbConnectQt(constring)

    if BACKEND == 'Alchemy':
        return dbConnectAlch(constring)
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
    
def dbDict2Url(conDict):
    if conDict.get('debug',False):
        print ('Parametros de conexion:')
        for entry in conDict:
            if entry == 'dbpass':
                continue
            print('{}:{}'.format(entry,conDict[entry]))
            
    driver = driver2Alch(conDict['driver'])
    if 'debug' in conDict:
        debug=conDict['debug']
    else:
        debug=False
    dbname = conDict['dbname']
    #GENERADOR
    pos = dbname.find('://')
    if pos > 0:
    #if driver == dbname[0:len(driver)]:
        #driver = dbname[0:pos]    
        print('Ya viene definida la base de datos')
        context = dbname
    else:
        if conDict['driver'] not in ('QSQLITE','sqlite','qsqlite'):
            host = conDict['dbhost']
            user = conDict['dbuser']
            password = conDict['dbpass']
            context = '{}://{}:{}@{}/{}'.format(driver,user,password,host,dbname)
        else:
            context = '{}:///{}'.format(driver,dbname)
    return context

def dbConnectAlch(conDict):
    """
    """
    context = dbDict2Url(conDict)
    if 'debug' in conDict:
        debug=conDict['debug']
    else:
        debug=False

    engine = create_engine(context,echo=debug)
    return engine.connect()

def dbConnectQt(conDict):
    db = QSqlDatabase.addDatabase(driver2Qt(conDict['driver']));
    
    db.setDatabaseName(conDict['dbname'])
    
    if conDict['driver'] not in ('QSQLITE','sqlite'):
        db.setHostName(conDict['dbhost'])
        db.setUserName(conDict['dbuser'])
        db.setPassword(conDict['dbpass'])
    
    ok = db.open()
    # True if connected
    if ok:        
        return db
    else:
        print('conexion a bd imposible')
        sys.exit(-1)

def getCursorLim(db,sql_string,**kwargs):
    if db is None:
        return None
    if sql_string is None or sql_string.strip() == '':
        return None
      
    sqlString=text(sql_string + setLimitString(sql_string,db,**kwargs) )

    cursor= []

    return db.execute(sqlString)
    
def getCursorAlch(db, sql_string,funcion=None,**kwargs):
    if db is None:
        return None
    if sql_string is None or sql_string.strip() == '':
        return None
      
    sqlString=text(sql_string + setLimitString(sql_string,db,**kwargs) )

    cursor= []
    try:
        resultCursor = db.execute(sqlString)
    except Exception as e:
        print('!!!!! ERROR !!!!')
        print(e)
        showQueryError(repr(e), queryFormat(sql_string))
        return []

    for row in resultCursor:
        trow = list(row) #viene en tupla y no me conviene
        if callable(funcion):
            funcion(trow,**kwargs)
        if trow != []:
            cursor.append(trow)
        #if lim:
            #if cont < lim:
                #cont += 1
            #else:
                #break
    return cursor

def XgetCursor(db, sql_string,funcion=None,**kwargs):
    """
        Version experimental.
        Sorprendentemente cargar directamente en el Qmodelo es entre un 25 y un 50% mas de tiempo que generar el array
        y luego cargar el modelo
        Como es logico no proseguimos con ese experimento
    """
    if db is None:
        return None
    if sql_string is None or sql_string.strip() == '':
        return None
    
    if 'model' in kwargs:
        model = kwargs['model']
        ItemClass = kwargs.get('iclass',QStandardItem)
        toModel = True
      
    sqlString=text(sql_string)
    cursor= []
    lim = kwargs.get('LIMIT')
    if lim:
        cont = 0
    for row in db.execute(sqlString):
        trow = list(row) #viene en tupla y no me conviene
        if callable(funcion):
            funcion(trow,**kwargs)
        if trow != []:
            if toModel:
                modelRow = [ ItemClass(str(fld)) for fld in trow ]
                model.appendRow(modelRow)
            else:
                cursor.append(trow)
            
        if lim:
            if cont < lim:
                cont += 1
            else:
                break
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
        lista_funciones = list(AGR_LIST)
    else:
        lista_funciones = plista[ : ]
    #TODO include functions which depend on DB driver
    return lista_funciones

def getDefaultSchema(db):
    ins = inspect(db.engine)
    schema = ins.default_schema_name
    if schema is None:  #para SQLITE
        return 'main'
    else:
        return schema

def fqn(db,fileName):
    divfN = fileName.split('.')
    if len(divfN) == 2:
        return fileName
    schema = getDefaultSchema(db)
    return '{}.{}'.format(schema,fileName)
    
def SQLConcat(db,array,sep=','):
    if len(array) ==0:
        return ""
    elif len(array) == 1:
        return array[0]
    
    if db.dialect in ('mysql','odbc'):
        return 'CONCAT_WS("{}",{})'.format(sep,','.join(array))
    else:
        return "|| '{}' || ".format(sep).join(array)

def showQueryError(error_text,query):
    from PyQt5.QtWidgets import QMessageBox
    
    msg = QMessageBox()
    msg.setMinimumSize(330,330)
    msg.setIcon(QMessageBox.Warning)

    msg.setText("Error en la ejecucion SQL")
    #msg.setInformativeText(detailed_error)
    msg.setWindowTitle("Error de SQL")
    msg.setInformativeText(error_text)
    msg.setDetailedText(query)
    msg.setStandardButtons(QMessageBox.Ok)                
    retval = msg.exec_()

def sql2PyAggregate(db_function,table,maxcols):
    """
    to support.datalayer.access_layer
    __db_function__ sql function to emulate (in text)
    __table__          array to process (n rows X (maximal) maxcols columns)
    __maxcols__     maximum number of columns of the table
    
    convertimos las funciones de agregacion de SQL en funciones Python. Notese que se ejecutan ignorando nulos
    Recibimos un array con los valores de datos y agrupamos por filas
    sum,max y min no tienen problema, 
    pero count solo cuenta las instancias del nivel anterior (un truco sería hacer un sum). De todas maneras no acabo de ver la posibilidad de realizar funciones significativas sobre count
    avg es el promedio del nivel inferior, lo que es conceptualmente distinto del avg que genera la base de datos. Mala solucion tiene
    """
    from statistics import mean 
    list_functions = {'count':len, 'max':max, 'min':min, 'avg':mean, 'sum':sum}
    function = list_functions[db_function]
    nhijos = len(table)
    resultado = [ ]
    for k in range(maxcols):
        vector = [ table[i][k] for i in range(nhijos) if k < len(table[i]) ]
        resultado.append(function(list(filter(lambda x:x is not None,vector))))
    return resultado

if __name__ == '__main__':
    definition1={'driver':'sqlite','dbname': '/home/werner/projects/scifi/scifi.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False } 
    definition2={'driver':'mysql','dbname': 'sakila',
                'dbhost':'localhost','dbuser':'root','dbpass':'***','debug':False } 

    definition3={'driver':'oracle','dbname': 'EX',
                'dbhost':'localhost','dbuser':'demo','dbpass':'***','debug':True } 
    
    conn = dbConnect(definition1)
    print(getDefaultSchema(conn))
    cursor = getCursor(conn,'select * from city')
    pprint(cursor)
    
