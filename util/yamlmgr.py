# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''

import yaml

def load_cubo(fichero="cubo.yml"):

    my_dict = {}
    try:
        file_handle = open(fichero)
        my_dict = yaml.safe_load(file_handle)
        file_handle.close()
    except IOError:
        print('Error de E/S en fichero %s'%fichero)
        my_dict= {}
    return my_dict

def dump_structure(data, fichero="dump.yml"):
    stream = file(fichero, 'w')
    yaml.dump(data, stream)
    stream.close()
    
