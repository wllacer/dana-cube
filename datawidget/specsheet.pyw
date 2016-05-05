#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QGridLayout
#from PyQt5.QtWidgets import QLineEdit, QLabel, QDialog, QPushButton

# from models_cube2 import *

ITEM_TYPE=set(['#entry','#ientry','default','cubo','connect','fields','guides','favorites',
               'vista',
               'guide','prod','favorite',
               'domain','values',
               'join','case',
               'join_table','join_clause','category'])

ATTR_DICT=[u'agregado',
     u'base filter',
     u'case_sql',
     #u'categories',
     u'class',
     u'col',
     u'condition',
     u'cubo',
     u'date_fmt',
     u'dbhost',
     u'dbname',
     u'dbpass',
     u'dbuser',
     u'default',
     u'desc',
     u'driver',
     u'elem',
#     u'elemento',
     u'enum_fmt',
     u'filter',
     u'fmt',
     u'grouped_by',
     u'join operator',
     u'left',
     u'name',
     u'result',
     u'right',
     u'right_values',
     u'row',
     u'table',
     u'type']
"""
     'agregado',        -> Combo of functions
     'base filter',     -> String
     'case_sql',        -> String
     'class',           -> Combo Class Types
     'col',             -> Int (Combo of guides)
     'condition',       -> Combo of conditional expressions
     'cubo',            -> Combo of cubes
     'date_fmt',        -> Combo on date formats
     'dbhost',          -> String
     'dbname',          -> String
     'dbpass',          -> String (hidden)
     'dbuser',          -> String
     'default',         -> String 
     'desc',            -> Combo of fields (dep on guide.table)
     'driver',          -> Combo of drivers
     'elem',            -> Combo of fields 
     'enum_fmt',        -> Combo of formats
     'filter',          -> String
     'fmt',             -> Combo of formats
     'grouped_by',      -> Combo of fields (dep on  cubo.table)
     'join operator',   -> Combo of join operators (OUTER, LEFT, RIGHT ...)
     'left',            -> Combo of fields (dep on  cubo.table)
     'name',            -> String
     'result',          -> String
     'right',           -> Combo of fields (dep on  join.entry.table)
     'right_values',    -> String (list of ..)
     'row',             -> Combo of guides
     'table',           -> Combo of tables
     'type'             -> Combo of types (which type?)
"""

ITEM_ATTR = { 'cube':('table','base filter'),
               'conn':('driver','dbname','dbhost','dbuser','dbpass'),
               'fields': (None,),
               #'guides':None,
               #'favorites':None,
               'guide':('name','class','type'),
               'prod':('name','class','type'),
               'domain':('name','elem','filter','table','desc','grouped_by'),
               'values':('name','elem','date_fmt','case_sql','fmt','enum_fmt'),
               #'guide':('class','type'),   #type is a leftover
               #'prod':('elem','name'),
               #'domain':('name','filter','table','code','desc','grouped by'),
               #'case':('name','elem','fmt','enum_fmt','categories','case_sql'),
               'case':('name','elem','fmt','enum_fmt''case_sql'),
               #'join': None,
               'join_table':('name','filter','table','join operator'),
               'join_clause':('left','condition','right'),
               'category':('default','result','condition','right_values'),
               'default':('cubo',),
               'vista':('row','col','agregado','elem'),
               'favorite':('name',),
               #'date':('name','elem','type'),
              }


ID, CALLER, STARTTIME, ENDTIME, TOPIC = range(5)
DATETIME_FORMAT = "yyyy-MM-dd hh:mm"


class ItemEdit(QDialog):

    FIRST, PREV, NEXT, LAST = range(4)

    def __init__(self, parent=None):
        super(ItemEdit, self).__init__(parent)

        self.entradas=[]
        for k,item in enumerate(ATTR_DICT):
            triada = []
            triada.append(QLabel(item))
            triada.append(QLineEdit())
            triada[0].setBuddy(triada[1])
            self.entradas.append(triada)            
            
        #callerLabel = QLabel("&Caller:")
        #self.callerEdit = QLineEdit()
        #callerLabel.setBuddy(self.callerEdit)
        #today = QDate.currentDate()
        #startLabel = QLabel("&Start:")
        #self.startDateTime = QDateTimeEdit()
        #startLabel.setBuddy(self.startDateTime)
        #self.startDateTime.setDateRange(today, today)
        #self.startDateTime.setDisplayFormat(DATETIME_FORMAT)
        #endLabel = QLabel("&End:")
        #self.endDateTime = QDateTimeEdit()
        #endLabel.setBuddy(self.endDateTime)
        #self.endDateTime.setDateRange(today, today)
        #self.endDateTime.setDisplayFormat(DATETIME_FORMAT)
        #topicLabel = QLabel("&Topic:")
        #topicEdit = QLineEdit()
        #topicLabel.setBuddy(topicEdit)
        
        firstButton = QPushButton()
        firstButton.setIcon(QIcon(":/first.png"))
        prevButton = QPushButton()
        prevButton.setIcon(QIcon(":/prev.png"))
        nextButton = QPushButton()
        nextButton.setIcon(QIcon(":/next.png"))
        lastButton = QPushButton()
        lastButton.setIcon(QIcon(":/last.png"))
        addButton = QPushButton("&Add")
        addButton.setIcon(QIcon(":/add.png"))
        deleteButton = QPushButton("&Delete")
        deleteButton.setIcon(QIcon(":/delete.png"))
        quitButton = QPushButton("&Quit")
        quitButton.setIcon(QIcon(":/quit.png"))
        addButton.setFocusPolicy(Qt.NoFocus)
        deleteButton.setFocusPolicy(Qt.NoFocus)

        fieldLayout = QGridLayout()
        linea = 0
        for k in range(0,len(ATTR_DICT)):
            fieldLayout.addWidget(self.entradas[k][0], linea, 0)
            fieldLayout.addWidget(self.entradas[k][1], linea, 1, 1, 6)
            linea += 1
        fieldLayout.setHorizontalSpacing(1)
        fieldLayout.setVerticalSpacing(0)
            #fieldLayout.addWidget(startLabel, 1, 0)
        #fieldLayout.addWidget(self.startDateTime, 1, 1)
        #fieldLayout.addWidget(endLabel, 1, 2)
        #fieldLayout.addWidget(self.endDateTime, 1, 3)
        #fieldLayout.addWidget(topicLabel, 2, 0)
        #fieldLayout.addWidget(topicEdit, 2, 1, 1, 3)
        
        navigationLayout = QHBoxLayout()
        navigationLayout.addWidget(firstButton)
        navigationLayout.addWidget(prevButton)
        navigationLayout.addWidget(nextButton)
        navigationLayout.addWidget(lastButton)
        fieldLayout.addLayout(navigationLayout,linea, 0, 1, 2)
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(addButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        fieldLayout.addLayout(buttonLayout,0, 11, 3, 1)
        layout = QHBoxLayout()
        layout.addLayout(fieldLayout)
#        layout.addLayout(buttonLayout)

        self.setLayout(layout)

        #self.model = None # TreeModel("cubo.json")

        #self.mapper = QDataWidgetMapper(self)
        #self.mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        #self.mapper.setModel(self.model)
        #self.mapper.setRootIndex(self.model.index(0,0,QModelIndex()))
        #        print(self.mapper.rootIndex().row(),self.mapper.rootIndex().column())
        # for k in range(len(ATTR_DICT)):
            # self.mapper.addMapping(self.entradas[k][1], k)
        #self.mapper.toFirst()
        #self.mapper.setCurrentIndex(28)
        #buttonBox.accepted.connect(self.accept)
        firstButton.clicked.connect(lambda: self.saveRecord(ItemEdit.FIRST))
        prevButton.clicked.connect(lambda: self.saveRecord(ItemEdit.PREV))
        nextButton.clicked.connect(lambda: self.saveRecord(ItemEdit.NEXT))
        lastButton.clicked.connect(lambda: self.saveRecord(ItemEdit.LAST))
        addButton.clicked.connect(self.addRecord)
        deleteButton.clicked.connect(self.deleteRecord)
        quitButton.clicked.connect(self.accept)

        self.setWindowTitle("Item editor")


    def reject(self):
        self.accept()


    def accept(self):
        self.mapper.submit()
        QDialog.accept(self)

        
    def addRecord(self):
        row = self.model.rowCount()
        self.mapper.submit()
        self.model.insertRow(row)
        self.mapper.setCurrentIndex(row)
        #now = QDateTime.currentDateTime()
        #self.startDateTime.setDateTime(now)
        #self.endDateTime.setDateTime(now)
        self.callerEdit.setFocus()


    def deleteRecord(self):
        for k in (3,5,12,13,15):
          self.entradas[k][0].hide()
          self.entradas[k][1].hide()
          
        #caller = self.callerEdit.text()
        #starttime = self.startDateTime.dateTime().toString()
        #if (QMessageBox.question(self,
                #"Delete",
                #"Delete call made by<br>{} on {}?".format(
                #caller, starttime),
                #QMessageBox.Yes|QMessageBox.No) ==
                #QMessageBox.No):
            #return
        #row = self.mapper.currentIndex()
        #self.model.removeRow(row)
        #self.model.submitAll()
        #if row + 1 >= self.model.rowCount():
            #row = self.model.rowCount() - 1
        #self.mapper.setCurrentIndex(row)


    def saveRecord(self, where):
        row = self.mapper.currentIndex()
        max_rows = self.model.rowCount()
        print(row,where,max_rows)
        self.mapper.submit()
        if where == ItemEdit.FIRST:
            row = 0
        elif where == ItemEdit.PREV:
            row = 0 if row <= 1 else row - 1
        elif where == ItemEdit.NEXT:
            print('upa',row + 1)
            row += 1
            if row >= max_rows:
                row = max_rows - 1
            
        elif where == ItemEdit.LAST:
            row = max_rows - 1
        print('debe salir',row,max_rows)

        self.mapper.setCurrentIndex(row)
        print('despues de todo',self.mapper.currentIndex())

def main():
    app = QApplication(sys.argv)
    form = ItemEdit()
    form.show()
    sys.exit(app.exec_())

main()

