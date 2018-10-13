#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from pprint import pprint

import sys

from PyQt5.QtCore import Qt,QSortFilterProxyModel
from PyQt5.QtGui import QCursor,QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView,QAction, QStatusBar, QMenu, QMenuBar, QMessageBox, QFileDialog,QFontDialog,QColorDialog

import base.config as config

class BaseDialogWindow(QMainWindow):

    def __init__(self, *args):
        #apply(QMainWindow.__init__, (self, ) + args)
        super(BaseDialogWindow, self).__init__(*args)
        #self.setCaption("Network Client")
        self.setWindowTitle("Network Clien")
        self.actionInformation=QAction( "Information")
        self.actionInformation.setWhatsThis("Informational Message")
        self.actionInformation.setText("&Information")
        self.actionInformation.setStatusTip("Show an informational mesagebox.")

        self.actionInformation.triggered.connect(self.slotInformation)


        self.actionWarning=QAction( "Warning")
        self.actionWarning.setWhatsThis("Warning Message")
        self.actionWarning.setText("&Warning")
        self.actionWarning.setStatusTip("Show a warning mesagebox.")

        self.actionWarning.triggered.connect(self.slotWarning)

        self.actionCritical=QAction( "Critical")
        self.actionCritical.setWhatsThis("Critical Message")
        self.actionCritical.setText("&Critical")
        self.actionCritical.setStatusTip("Show an informational mesagebox.")

        self.actionCritical.triggered.connect(self.slotCritical)

        self.actionAbout=QAction( "About")
        self.actionAbout.setWhatsThis("About")
        self.actionAbout.setText("&About")
        self.actionAbout.setStatusTip("Show an about box.")

        self.actionAbout.triggered.connect(self.slotAbout)     


        self.actionAboutQt=QAction( "AboutQt")
        self.actionAboutQt.setWhatsThis("About Qt Message")
        self.actionAboutQt.setText("About &Qt")
        self.actionAboutQt.setStatusTip("Show an about box for Qt.")

        self.actionAboutQt.triggered.connect(self.slotAboutQt)

        self.actionFile=QAction( "OpenFile")
        self.actionFile.setWhatsThis("Open File")
        self.actionFile.setText("&Open")
        self.actionFile.setStatusTip("Open a file.")
        
        self.actionFile.triggered.connect(self.slotFile)


        self.actionFont=QAction( "Font")
        self.actionFont.setWhatsThis("Select a font")
        self.actionFont.setText("&Font")
        self.actionFont.setStatusTip("Select a font")

        self.actionFont.triggered.connect(self.slotFont) 


        self.actionColor=QAction( "Color")
        self.actionColor.setWhatsThis("Select a color")
        self.actionColor.setText("&Color")
        self.actionColor.setStatusTip("Select a color")

        self.actionColor.triggered.connect(self.slotColor) 

        # Statusbar
        self.statusBar=QStatusBar(self)

        # Define menu
        
        
        self.messageMenu = self.menuBar().addMenu("&Mensajes")
        self.messageMenu.addAction(self.actionInformation)
        self.messageMenu.addAction(self.actionWarning)
        self.messageMenu.addAction(self.actionCritical)

        self.dialogMenu= self.menuBar().addMenu("&Standard dialogs")
        self.dialogMenu.addAction(self.actionFile)
        self.dialogMenu.addAction(self.actionFont)
        self.dialogMenu.addAction(self.actionColor)

        self.helpMenu=self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.actionAbout)
        self.helpMenu.addAction(self.actionAboutQt)


    def slotInformation(self):
        QMessageBox.information(self,
                                "Information",
                                "A plain, informational message")

    def slotWarning(self):
        QMessageBox.warning(self,
                            "Warning",
                            "What you are about to do will do some serious harm .")


    def slotCritical(self):
        QMessageBox.critical(self,
                                "Critical",
                                "A critical error has occurred.\nProcessing will be stopped!")

    def slotAbout(self):
        QMessageBox.about(self,
                          "About me",
                          "A demo of message boxes and standard dialogs.")

    def slotAboutQt(self):
        QMessageBox.aboutQt(self)


    def slotFile(self):
        filename=QFileDialog.getOpenFileName(self, "FileDialog",".", "Python (*.py *.pyw);;Configuration (*.json)","Configuration (*.json)")

    def slotFont(self):
        (font, ok) = QFontDialog.getFont(self)

    def slotColor(self):
        color=QColorDialog.getColor(QColor("linen"), self, "ColorDialog")


def main(args):
    app=QApplication(args)
    win=BaseDialogWindow()
    win.show()
    app.lastWindowClosed.connect(quit)
    
    app.exec_()

if __name__=="__main__":
        main(sys.argv)
     
