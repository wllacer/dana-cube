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
from pathlib import Path

def load_cubo(fichero="cubo.json"):
    my_dict = {}
    try:
        with open(getPath(fichero)) as infile:
            my_dict = json.load(infile)
    except IOError:
        print('Error de E/S en fichero. Probablemente fichero no exista %s'%fichero)
        my_dict= {}
    return my_dict

def dump_json(data, fichero="cubo.json"):
    with open(getPath(fichero),'w') as outfile:
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


def getAppDir(create=True):
    """
    Obtiene el directorio de defecto de datos de la aplicacion.
    Utiliza la variable de entorno APPDATA si existe; si no el directorio de defecto del usuario
    """
    appdata = os.environ.get('APPDATA')
    if not appdata: #no existe directorio de configuracion. Entonces a Home
        appdir = Path.home()
    else:
        confdir = Path(appdata)
        if not confdir.is_dir():
            appdir = Path.home()
        else:
            appdir =confdir / 'wernerllacer.com/DanaCube'
            if not appdir.exists() and create:
                #creo el directorio para danacube
                appdir.mkdir(parents=True)
    return appdir
    
def getPath(pFichero):
    """
    Determino el path real de un fichero 
    Existen tres casos
    1) Si fichero  es un path absoluto se retorna el mismo
    2) si es un path relativo (con subdirectorios o comenzando con ./ -o .\\, segun) lo consideramos relativo respecto del directorio de trabajo -donde se ha invocado la aplicacion
    3) Si es independiente ( simplemente un nombre de fichero) se busca en el directorio de arranque, y si no existe en el directorio de datos de la aplicacion (ver getAppDir)..
    En el caso de los ficheros independientes SIEMPRE los crea en el directorio de datos de la aplicacion
    """
    fichero = Path(pFichero)
    if fichero.is_absolute():
        return fichero
    else:
        base = Path(os.getcwd())
        resultado = base / fichero
        if pFichero == fichero.name and not resultado.exists():
            res2 = getAppDir(create=True)  / fichero
            return res2.resolve()
        else:
            return resultado.resolve()
        
def getConfigFileName(pName=None):
    """
    determina la posicion y nombre de Configuration file.
    Es ahora  un placeholder de getPath, usado por compatibilidad
    """
    resultado =getPath(pName if pName else '.danabrowse.json') 
    return str(resultado)    

    
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
    print(os.getcwd())
    fichero = 'pepe'
    fichero1 = './pepe'
    for fichero in ('pepe','./pepe','../../circo/maximo','/home/werner/pepe','$HOME/paco','.cursi','testcubo.json'):
        print('{:20} -> {}'.format(fichero,getPath(fichero)))
    #print(getConfigFileName())
    #dump_config(nuevo,'pepelaalfa.txt')
    #dump_config(base,nuevo,'pepelaalfa.txt',total=False,secure=True)
        
