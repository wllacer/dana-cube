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
    from  sqlalchemy import create_engine,inspect,MetaData
    from  sqlalchemy.exc import CompileError
    from  sqlalchemy.sql import text
else:
    from PyQt5.QtSql import * 
    from PyQt5.QtCore import QVariant
    
from access_layer import *

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
if __name__ == "__main__":
    
    definition={'driver':'QSQLITE','dbname': '/home/werner/projects/dana-cube.git/ejemplo_dana.db',
                'dbhost':None,'dbuser':None,'dbpass':None,'debug':False } 
    #dirQt(definition)
    dirAlchI(definition)
    #dirAlchM(definition)
 