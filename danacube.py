#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from base.danacube import DanaCubeWindow,generaArgParser
from PyQt5.QtWidgets import QApplication 

if __name__ == '__main__':
    import sys

    # con utf-8, no lo recomiendan pero me funciona
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    
    parser = generaArgParser()
    args = parser.parse_args()
    #FOR DEBUGER args.cubeFile = 'testcubo.json'
    app = QApplication(sys.argv)
    window = DanaCubeWindow(args)
    window.resize(app.primaryScreen().availableSize().width(),app.primaryScreen().availableSize().height())
    window.show()
    sys.exit(app.exec_())
