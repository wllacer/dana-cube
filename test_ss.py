#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from research.cubespread import guidePreview
from PyQt5.QtWidgets import QApplication    
from support.util.jsonmgr import load_cubo

if __name__ == '__main__':
    import sys

    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    app = QApplication(sys.argv)
    mis_cubos = load_cubo()
    cubo = mis_cubos['datos light']
    form = guidePreview(cubo)
    form.show()
    if form.exec_():
        pass
        sys.exit()
