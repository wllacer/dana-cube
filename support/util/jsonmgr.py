# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''
from pprint import pprint
import json
import os
import datetime

def load_cubo(fichero="cubo.json"):
    my_dict = {}
    try:
        with open(fichero) as infile:
            my_dict = json.load(infile)
    except IOError:
        print('Error de E/S en fichero. Probablemente fichero no exista %s'%fichero)
        my_dict= None
    return my_dict

def dump_json(data, fichero="cubo.json"):
    with open(fichero,'w') as outfile:
        json.dump(data,outfile, sort_keys=False,indent=4,ensure_ascii=False)
    
def dump_structure(new_data, fichero="cubo.json",**flags):
    total = flags.get('total',True)
    secure = flags.get('secure',False) 
    """
    new_data = tree2dict(self.hiddenRoot,isDictionaryEntry)
    """
    baseCubo=load_cubo(fichero)
    k_new_data = dict()
    
    if total:
        k_new_data = new_data
    else:
        added, removed, modified, same = dict_compare(new_data,baseCubo)
        for entry in added:
            k_new_data[entry] = new_data[entry]
        for entry in removed:
            k_new_data[entry] = baseCubo[entry]
        for entry in same:
            k_new_data[entry] = baseCubo[entry]
        for entry in modified:
            # con los borrados hay un problema, pues la edicion debe asumirse parcial. La unica opcion que he encotrado es borrar si esta vacia
            if new_data[entry]:
                k_new_data[entry] = new_data[entry]
    if secure:
        # proceso datos de seguridad (los dejo como estaban. asi puedo usarlo con y sin)
        for entry in k_new_data:
            if not isinstance(k_new_data[entry],dict):
                continue
            if not baseCubo:
                continue
            if k_new_data[entry].get('connect'):
                k_new_data[entry]['connect'] = baseCubo[entry]['connect']

    if baseCubo == k_new_data:
        return
    # para python 3 y pico que ordenan por defecto
    o_new_data = {}
    for clave in sorted(k_new_data):
        o_new_data[clave] = k_new_data[clave]
    #no grabo si no hay cambios
    dump_json(baseCubo,'{}.{}'.format(fichero,datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    dump_json(o_new_data,fichero)

def dump_config(new_data, fichero=".danabrowse.json",**flags):
    total = flags.get('total',True)
    secure = flags.get('secure',False) 
    """
    new_data = tree2dict(self.hiddenRoot,isDictionaryEntry)
    """
    baseCubo=load_cubo(fichero)
    k_new_data = dict()
    
    if total:
        k_new_data = new_data
    else:
        k_new_data = { clave:new_data[clave] if clave != 'Conexiones' else dict() for clave in new_data }
        added, removed, modified, same = dict_compare(new_data['Conexiones'],baseCubo['Conexiones'])
        for entry in added:
            k_new_data['Conexiones'][entry] = new_data['Conexiones'][entry]
        for entry in removed:
            k_new_data['Conexiones'][entry] = baseCubo['Conexiones'][entry]
        for entry in same:
            k_new_data['Conexiones'][entry] = baseCubo['Conexiones'][entry]
        for entry in modified:
            # con los borrados hay un problema, pues la edicion debe asumirse parcial. La unica opcion que he encotrado es borrar si esta vacia
            if new_data['Conexiones'][entry]:
                k_new_data['Conexiones'][entry] = new_data['Conexiones'][entry]
    if secure:
        # proceso datos de seguridad (los dejo como estaban. asi puedo usarlo con y sin)
        for entry in k_new_data['Conexiones']:
            if not baseCubo:
                break
            if not isinstance(k_new_data['Conexiones'][entry],dict):
                continue
            if k_new_data['Conexiones'][entry].get('dbpass'):
                k_new_data['Conexiones'][entry]['dbpass'] = baseCubo.get('Conexiones',{}).get(entry,{}).get('dbpass','')
            if k_new_data['Conexiones'][entry].get('dbuser'):
                k_new_data['Conexiones'][entry]['dbuser'] = baseCubo.get('Conexiones',{}).get(entry,{}).get('dbuser','')

    if baseCubo == k_new_data:
        return
    #no grabo si no hay cambios
    if baseCubo:
        dump_json(baseCubo,'{}.{}'.format(fichero,datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
    dump_json(k_new_data,fichero)
    
def getConfigFileName(pName=None):
    # Configuration file
    #TODO para ser efectivo de verdad necesita mas logica
    if not pName:
        name = '.danabrowse.json'
    else:
        name = pName
        
    if os.name == "nt":
        appdir = os.path.expanduser('~/Application Data/Dana')
        if not os.path.isdir(appdir):
            os.mkdir(appdir)
        configFilename = appdir + "/"+name
    else:
        configFilename = os.path.expanduser('~/'+name)
    return configFilename
#
# de http://stackoverflow.com/questions/4527942/comparing-two-dictionaries-in-python
# el original es el segundo
def dict_compare(nuevo, original):
  nuevo_keys = set(nuevo.keys())
  original_keys = set(original.keys())
  intersect_keys = nuevo_keys.intersection(original_keys)
  added = nuevo_keys - original_keys
  removed = original_keys - nuevo_keys
  modified = set(o for o in intersect_keys if nuevo[o] != original[o])
  same = set(o for o in intersect_keys if nuevo[o] == original[o])
  return added, removed, modified, same

if __name__ == '__main__':
    #base = { 'entry1':1,
             #'entry2':{'connect':{'pepe':'hugo','dbpass':'mariano'}},
             #'entry4':2,
             #'entry3':3
           #}
    #nuevo = { 'entry1':1,
              #'entry2':{'connect':{'pepe':'hugo','dbpass':'fernandez'}},
        #}
    #dump_structure(base,nuevo,'pepelaalfa.txt')
    #dump_structure(base,nuevo,'pepelaalfa.txt',total=False,secure=True)
    base = {
    "Conexiones": {
        "Elecciones 2105": {
            "dbport": "",
            "dbhost": "",
            "driver": "sqlite",
            "dbpass": "",
            "debug": False,
            "dbuser": "",
            "dbname": "/home/werner/projects/dana-cube.git/ejemplo_dana.db"
        },
        "Pagila": {
            "dbhost": "localhost",
            "driver": "postgresql",
            "dbpass": "",
            "debug": False,
            "dbuser": "werner",
            "dbname": "pagila"
        }
    }
    }
    nuevo = {
    "Conexiones": {
        "Elecciones 2105": {
            "dbport": "",
            "dbhost": "",
            "driver": "sqlite",
            "dbpass": "",
            "debug": False,
            "dbuser": "",
            "dbname": "/home/werner/projects/dana-cube.git/otro_dana.db"
        },
        "Pagila": {
            "dbhost": "localhost",
            "driver": "postgresql",
            "dbpass": "",
            "debug": False,
            "dbuser": "werner",
            "dbname": "pagila"
        }
    },
    "configuracion" :
         { 'uno':1,'dos':2}
         
     
    }
    #dump_config(base,nuevo,'pepelaalfa.txt')
    dump_config(base,nuevo,'pepelaalfa.txt',total=False,secure=True)
        
