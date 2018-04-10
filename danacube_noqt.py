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
#from support.gui.dialogs import *
#from support.util.jsonmgr import *
#from models import *

#import user as uf

#from support.util.decorators import *

#from base.filterDlg import filterDialog
#from base.datadict import DataDict
#from base.cubetree import traverseTree
#from support.datalayer.query_constructor import searchConstructor

#from support.util.mplwidget import SimpleChart
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
