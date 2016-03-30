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
