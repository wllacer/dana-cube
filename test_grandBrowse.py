#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


from research.grandBrowse import *
from PyQt5.QtWidgets import QApplication 

def test(cuboId,mostrar=True,ejecutar=False,salida=False):
    from support.util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos[cuboId])
    generaQuery(cubo,mostrar,ejecutar,salida)
    #pprint(cursor)

def UberTest(mostrar=False,ejecutar=True,salida=False):
    from support.util.jsonmgr import load_cubo

    # TODO normalizar los nombres de ficheros y campos a FQN
    mis_cubos = load_cubo()
    for cuboId in mis_cubos:
        if cuboId == 'default':
            continue
        print('Ahora para el cubo ',cuboId)
        cubo = Cubo(mis_cubos[cuboId])
        cubo.nombre = cuboId
        generaQuery(cubo,mostrar,ejecutar,salida)
        
if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    #export()
    config.DEBUG = False
    UberTest(mostrar=True,ejecutar=False)
    #test("rental",ejecutar=False)
