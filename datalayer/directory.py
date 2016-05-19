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
BACKEND = 'Alchemy' #'Alchemy' #or 'QtSql'
'''
Documentation, License etc.

@package estimaciones
'''
#from PyQt4.QtSql import *
if BACKEND == 'Alchemy':
    from  sqlalchemy import create_engine,inspect,MetaData, types
    from  sqlalchemy.exc import CompileError
    from  sqlalchemy.sql import text
else:
    from PyQt5.QtSql import * 
    from PyQt5.QtCore import QVariant
    
from access_layer import *

def fullName(schema=None,table=None,col=None):
    cadena = ''
    if schema is None:
        cadena = table
    else:
        cadena = '{}.{}'.format(schema,table)
    if table is None:
        return cadena
    if col is None:
        return cadena
    else:
        return '{}.{}'.format(cadena,col)

def dirQt(definition):
    
    db=dbConnectQt(definition)
    if db is None:
        print('Wooook')
    for table in db.tables(QSql.Tables|QSql.Views):
        print('\t',table)
        record =  db.record(table)
        for ind in range(record.count()):
            campo = record.field(ind)
            print('\t\t',campo.name(),QVariant.typeToName(campo.type()),campo.length(),campo.precision())
        
def dirAlchI(definition):
           
    #from sqlalchemy import inspect  
    #from sqlalchemy.exc import CompileError
    db=dbConnectAlch(definition)
    engine=db.engine #incredible
    if db is None:
        print('Wooook')
    inspector = inspect(engine)
    if len(inspector.get_schema_names()) is 0:
        schemata =[None,]
    else:
        print(inspector.get_schema_names())
        schemata=inspector.get_schema_names()  #behaviour with default

    for schema in schemata:
        print(fullName(schema))
        for table_name in inspector.get_table_names(schema):
            print('\t',fullName(schema,table_name))
            for column in inspector.get_columns(table_name,schema):
                #print('\t\t',campo.name(),campo.type(),campo.length(),campo.precision())
                #pprint(column)
                try:
                    name = column['name']
                    tipo = column.get('type','TEXT')
                    print("\t\t",fullName(schema,table_name,name),tipo)
                except CompileError: 
                #except CompileError:
                    print('Columna sin tipo')
            for fk in inspector.get_foreign_keys(table_name,schema):

                print("\t\t",fullName(schema,table_name,fk['constrained_columns']),'{}.{}()'.format(fk.get('referred_schema',''),
                                                                        fk['referred_table'],
                                                                        fk['referred_columns']
                                                                    )
                    )

def dirAlchM(definition):
    from sqlalchemy import MetaData
    db=dbConnectAlch(definition)
    engine=db.engine #incredible
    m = MetaData()
    m.reflect(engine)
    for table in m.tables.values():
        if table.name == 'sqlite_sequence':
            continue
        print('\t',table.name)
        for column in table.c:
            #print(column)
            print('\t\t',column.name,column.type)
        for fk in table.foreign_key_constraints:
            print('\t\t',fk.name,fk.column_keys,fk.referred_table)
            
def getTableFields(conn,tname,sname=None):
    inspector = inspect(conn.engine) #getInspector(definition)    
    schema = None
    if sname is None:
        parts=tname.split('.')
        if len(parts) > 1:
            schema = parts[0]
            table = parts[1]
        else:
            table = tname
    else:
        schema = sname
        table  = tname
    if schema is not None:
        if schema not in inspector.get_schema_names():
            print('esquema no existe')
            return
        
    if table in inspector.get_table_names(schema):
        pass
    else:
        print('tabla no existe en el esquema / base de datos')
        return 
    array = []
    for column in inspector.get_columns(table,schema):
        try:
            name = column['name']
            if name == 'fakedate':
                tipo = 'fecha'
            else:
                tipo = typeHandler(column.get('type'))
            array.append((fullName(schema,table,name),tipo))
        except CompileError: 
            array.append((fullName(schema,table,name),'ND'))
    return array        
    #for fk in inspector.get_foreign_keys(table,schema):

        #print("\t\t",fullName(schema,table,fk['constrained_columns']),'{}.{}()'.format(fk.get('referred_schema',''),
                                                                #fk['referred_table'],
                                                                #fk['referred_columns']
                                                            #))
def typeHandler(type):
    if  isinstance(type,(types.Numeric,types.Integer,types.BigInteger)):
          return 'numerico'
    elif isinstance(type,types.String):
          return 'texto'
    elif isinstance(type,(types._Binary,types.LargeBinary)):
          return 'binario'
    elif isinstance(type,types.Boolean):
          return 'booleano'
    elif isinstance(type,(types.Date,types.DateTime)):
          return 'fecha'
    elif isinstance(type,types.Time):
          return 'hora'
    else:
          print('Tipo {} no contemplado'.format(type))
          return 'ND'
     

def camposDeTipo(tipo,conn,tname,schema=None):
    if tipo not in ('numerico','texto','binario','booleano','fecha','hora','ND'):
        print(tipo,': Tipo no configurado')
        return None
    
    tmp = [ item[0] for item in getTableFields(conn,tname,schema) if item[1] == tipo ]
    return tmp
    
def getInspector(definition):
    db=dbConnectAlch(definition)
    engine=db.engine #incredible
    if db is None:
        print('Wooook')
    inspector = inspect(engine)
    return inspector

if __name__ == "__main__":
    
    definition={'driver':'QSQLITE','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False } 
    #dirQt(definition)
    #dirAlchI(definition)
    #dirAlchM(definition)
    conn = dbConnectAlch(definition)
    getTableFields(conn,'votos_locales')
    getTableFields(conn,'votos_locales','default') #TODO deberia contemplarse
    getTableFields(conn,'mio.tuyo')
    getTableFields(conn,'votos_v')
    pprint(getTableFields(conn,'votos_locales'))
    print(filter(lambda item: item[1] == 'fecha',getTableFields(conn,'votos_locales')))
    print(camposDeTipo('numerico',conn,'votos_locales'))
    
 