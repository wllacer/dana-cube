#!/usr/bin/python
# -*- coding=utf -*-

"""
Part of  Global Common modules by Werner Llácer (c) 2012-2018

As an integral part of a project distributed under an Open Source Licence, the licence of the proyect
Used as  standalone module or outside the scope of  a project valid according to the  previous paragraph, or when  in doubt, distributed according to the terms of the GNU LGPL v2.0 license or higher numbered versions.
The text of that particular version is available at https://www.gnu.org/licenses/old-licenses/lgpl-2.0.html

"""

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
    fileName = getPath(fichero)
    
    with open(fileName,'w') as outfile:
        json.dump(data,outfile, sort_keys=False,indent=4,ensure_ascii=False)
    #trace data
    print('fichero ',fileName,' grabado')

def dump_structure(new_data, fichero="cubo.json",**flags):
    flags['secure_paths'] = (('*','connect'),)
    dump_data(new_data,fichero,**flags)


def dump_config(new_data, fichero=".danabrowse.json",**flags):
    flags['secure_paths'] = (('Conexiones','*','dbpass'),('Conexiones','*','dbuser'))
    dump_data(new_data,fichero,**flags)
    
def dump_data(new_data, fichero=None,**flags):
    """
    flags sorted -> if alphabetically sorted output
             secure -> if dynamic changes in user/pwd are NOT written
             secure_paths --> array of paths (arrays) of which elements are "securized"
    """
    total = flags.get('total',True)
    secure = flags.get('secure',False)
    secure_paths = flags.get('secure_paths',[])
    sorted = flags.get('sorted',False)
    
    oldData=load_cubo(fichero)
    k_new_data = dict()
    
    if total:
        k_new_data = new_data
    else:
            
        k_new_data = dictMerge(oldData,new_data,sorted=sorted)
        
        if secure:
            result = dict()
            for path in secure_paths:
                print(path)
                filterDictSubset(result,path,oldData)
            massUpdate(k_new_data,result)
  
    if oldData == k_new_data:
        return
    #no grabo si no hay cambios
    if oldData:
        dump_json(oldData,'{}.{}'.format(fichero,datetime.datetime.now().strftime("%Y%m%d-%H%M%S")))
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
        #print(pFichero,' instanciado en ',fichero)
        return fichero
    else:
        base = Path(os.getcwd())
        resultado = base / fichero
        if pFichero == fichero.name and not resultado.exists():
            res2 = getAppDir(create=True)  / fichero
            #print(pFichero,' instanciado en ',res2)
            return res2.resolve()
        else:
            #print(pFichero,' instanciado en ',resultado)
            return resultado.resolve()
        
def getConfigFileName(pName=None):
    """
    determina la posicion y nombre de Configuration file.
    Es ahora  un placeholder de getPath, usado por compatibilidad
    """
    resultado =getPath(pName if pName else '.danabrowse.json') 
    return str(resultado)    



def dictMerge(oldData,newData,sorted=False):
    k_new_data = dict()
    added, removed, modified, same = dict_compare(newData,oldData)
    for entry in added:
        k_new_data[entry] = newData[entry]
    for entry in removed:
        k_new_data[entry] = oldData[entry]
    for entry in same:
        k_new_data[entry] = oldData[entry]
    for entry in modified:
        # si es un diccionario muevo elemento a elemento
        if newData[entry] and isinstance(newData[entry],dict) and isinstance(oldData[entry],dict):
            k_new_data[entry] = dictMerge(oldData[entry],newData[entry])
        elif newData[entry]:  #se supone que deberia salir siempre por aqui
            k_new_data[entry] = newData[entry]
    if sorted:
        sk_new_data = dict()
        for clave in sorted(k_new_data):
            sk_new_data[clave] = k_new_data[clave]
        return sk_new_data
    else:
        return k_new_data


def filterDictSubset(result,secuencia,recurso,cabecera=list()):
    dest = cabecera[:]
    for ind,clave in enumerate(secuencia):
        if clave == '*':
            for nclave in recurso:
                nseq = (nclave,) + secuencia[ind +1:]
                filterDictSubset(result,nseq,recurso,dest)
            break
        else:
            recurso = recurso.get(clave)
            if recurso is None:
                dest = list()
                break
            else:
                dest.append(clave)
    else:
        #print(dest,recurso)
        result[tuple(dest)]=recurso

def massUpdate(recurso,valores):
    for entrada in valores:
        update(recurso,valores[entrada],*entrada)
        
def update(tabla,nuevovalor,*clave):
    dest = tabla
    for step in clave[:-1]:
        if step in dest:
            dest= dest[step]
        else:
            break
    else:
        dest[clave[-1]] = nuevovalor

            
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
    #print(os.getcwd())
    #fichero = 'pepe'
    #fichero1 = './pepe'
    #for fichero in ('pepe','./pepe','../../circo/maximo','/home/werner/pepe','$HOME/paco','.cursi','testcubo.json'):
        #print('{:20} -> {}'.format(fichero,getPath(fichero)))
    #print(getConfigFileName())
    #dump_config(nuevo,'pepelaalfa.txt')
    #dump_config(base,nuevo,'pepelaalfa.txt',total=False,secure=True)
    def get_nested(data, *args):
            if args and data:
                element  = args[0]
                if element:
                    value = data.get(element)
                    return value if len(args) == 1 else get_nested(value, *args[1:])

    #activo= load_cubo('testcubo.json')
    #activo['rental']['connect']['dbuser']='hugo'
    #activo['rental']['connect']['dbpass']='sanchez'
    #activo['samping']= 'Hehoheho'
    #dump_structure(activo,'testcubo.json',secure=True,total=False)
    #pprint(nuevo)
    activo= load_cubo('.danabrowse.json')
    activo['Conexiones']['Pagila']['dbuser']='hugo'
    activo['Conexiones']['Pagila']['dbpass']='sanchez'
    activo['samping']= 'Hehoheho'
    dump_config(activo,'.danabrowse.json',secure=True,total=False)
