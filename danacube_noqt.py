#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint
import argparse

from PyQt5.QtWidgets import QApplication

from noqt.danacube import *
from noqt.core import Cubo,Vista, mergeString
#from dialogs import *
#from util.jsonmgr import *
#from models import *

#import user as uf

#from util.decorators import *

#from filterDlg import filterDialog
#from dictmgmt.datadict import DataDict
#from cubemgmt.cubetree import traverseTree
#from datalayer.query_constructor import searchConstructor

#from util.mplwidget import SimpleChart
#from util.uf_manager import *

#import exportWizard as eW

#from util.treestate import *
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
