#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Part of  Dana-Cube Proyect by Werner Llácer (c) 2012-2018

Distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html
Please see https://github.com/wllacer/dana-cube#license for further particulars about licencing of the Dana-Cube Project 

"""
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from PyQt5.QtWidgets import QApplication

from noqt.danacube import *
from noqt.core import Cubo,Vista, mergeString
#from support.gui.dialogs import *
#from support.util.jsonmgr import *
#from models import *

#import user as uf

#from support.util.decorators import *

#from base.filterDlg import filterDialog
#from base.datadict import DataDict
#from base.cubetree import traverseTree
#from support.datalayer.query_constructor import searchConstructor

#from support.gui.mplwidget import SimpleChart
#from support.util.uf_manager import *

#import base.exportWizard as eW

#from support.util.treestate import *
if __name__ == '__main__':
    import sys

    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    parser = generaArgParser()
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = DanaCubeWindow(args)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
