#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
   code is based on the simpletreemodel sample of the Qt/PyQt documentation,
           which is BSD licensed by Nokia and successors, and Riverbank
'''
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pprint import pprint

def porcentaje(row):
    suma=sum(filter(None,row))
    return list(map(lambda item: item*100/suma if item is not None else None,row))

USER_FUNCTION_LIST=( (porcentaje,'Porcentajes calculados en la fila','row'),
              )

    
row=[15,26,74,66,None,24]
print(USER_FUNCTION_LIST[0][0](row))
