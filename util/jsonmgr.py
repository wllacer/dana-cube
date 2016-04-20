# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''

import json

def load_cubo(fichero="cubo.json"):

    my_dict = {}
    try:
        with open(fichero) as infile:
            my_dict = json.load(infile)
    except IOError:
        print('Error de E/S en fichero %s'%fichero)
        my_dict= {}
    return my_dict

def dump_structure(data, fichero="cubo.json"):
    with open(fichero,'w') as outfile:
        json.dump(data,outfile, sort_keys=False,indent=4,ensure_ascii=False)
    
