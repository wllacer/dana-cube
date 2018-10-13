#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from pprint import pprint

def registro_funcion(context,**kwparms):
    """
    Parametros a evaluar
    a) lista general
    name    Nombre (obligatorio)
    entry   entry_point (obligatorio)
    type    tipo_parm (depende de aplicacion)
    aux_parm    parametros auxiliares 
    text    texto en menu
    b) para presentacion (opcionales)
    seqnr   secuencia en menu
    sep     separador tras entrada
    hidden  si oculto
    c) cualqiier cosa por aplicacion
    api determina que interfaz utiliza en danacube
    """
    if 'name' not in kwparms or 'entry' not in kwparms:
        print('Parametro obligatorio no suminstrado (name, entry o type')
        return
    item= dict()
    item['exec'] = ((kwparms['entry'],kwparms.get('type'),kwparms.get('aux_parm'),kwparms['name'],),)
    item['text'] = kwparms.get('text',kwparms['name'])  
    for entrada in kwparms:
        if entrada in ('name','entry','text','type','aux_parm'):
            continue
        item[entrada] = kwparms[entrada]
    #item['seqnr'] = kwparms.get('seqnr',999) 
    #item['sep'] = kwparms.get('sep',False)
    #item['hidden'] = kwparms.get('hidden',False)
    context[kwparms['name']] = item
    return None

def registro_secuencia(context,**kwparms):
    """
    TODO secuencia de secuencia
    Parametros a evaluar
    name    Nombre (obligatorio)
    list    lista de funciones a ejecutar, opcionalmente con parametro auxiliar
    text    texto en menu
    seqnr   secuencia en menu
    sep     separador tras entrada
    hidden  si oculto
    c) cualqiier cosa por aplicacion
    """
    if 'name' not in kwparms or 'list' not in kwparms:
        print('Parametro obligatorio no suminstrado (name)')
        return
    item= dict()
    lista = list()
    for entrada in kwparms['list']:
        if isinstance(entrada,(list,set,tuple)):
            nombre = entrada[0]
            parms = entrada[1]
        else:
            nombre = entrada
            parms = None
        if entrada not in context:
            print('Uno de los elementos de la secuencia no existe',entrada)
            return
        for modulos in context[entrada]['exec']:
            lista.append(modulos)
            if parms is not None:
                lista[-1][2]=parms #deberia añadir y no modificar. TODO
    item['exec'] = lista
    item['text'] = kwparms.get('text',kwparms['name'])  
    for entrada in kwparms:
        if entrada in ('name','list','text'):
            continue
        item[entrada] = kwparms[entrada]
    
    #item['seqnr'] = kwparms.get('seqnr',9999) 
    #item['sep'] = kwparms.get('sep',False)
    #item['hidden'] = kwparms.get('hidden',False)
    context[kwparms['name']] = item
    return None

def uf_discover(uf,dictionary):
    """
    uf libreria (directorio de funciones)
    dictionary  diccionario de funciones
    """
    for name in uf.__all__:
        plugin = getattr(uf, name)
        try:
            # see if the plugin has a 'register' attribute
            register_plugin = plugin.register
        except AttributeError:
            # raise an exception, log a message, 
            # or just ignore the problem
            print(name,'has no attribute register')
            pass
        else:
            # try to call it, without catching any errors
            register_plugin(dictionary)

def uf_discover_file(uf,plugins,configFile):
    """
    uf libreria (directorio de funciones)
    dictionary  diccionario de funciones
    """
    from support.util.jsonmgr import load_cubo
    toollist = readUM(uf)
    definiciones = load_cubo(configFile)
    if not definiciones:
        uf_discover(uf,plugins)
        return
    else:
        defs = definiciones['user functions']
    functions = {}
    sequences = {}
    #TODO ordered dict ¿?
    for item in defs:
        entrada = defs[item]
        if entrada['class'] == 'sequence':
            sequences[item] = entrada
            sequences[item]['name'] = item
        elif entrada['class'] == 'function':
            functions[item] = entrada
            functions[item]['name'] = item
            try:
                gosh = toollist[entrada['entry']]
                functions[item]['entry'] = gosh
            except KeyError:
                print('Funcion de usuario {} no definida'.format(entrada['entry']))
                del functions[item]
                continue
            if 'aux_parm' in functions[item]:
                auxiliares = functions[item]['aux_parm']
                bien = True
                for parametro in auxiliares:
                    if parametro.startswith('fun'):
                        try:
                            auxiliares[parametro] = toollist[auxiliares[parametro]]
                        except KeyError:
                            print('Funcion de usuario {} no definida'.format(auxiliares[parametro]))
                            bien = False
                            break
                if not bien:
                    del functions[item]
    #pprint(functions)
    for entrada in functions:
        registro_funcion(plugins,**functions[entrada])
    for entrada in sequences:
        registro_secuencia(plugins,**sequences[entrada])

def readUM(context,toollist= None):
    withReturn = False
    if not toollist:
        withReturn = True
        toollist = {}
    import inspect as ins
    for entrada in context.__all__:
        source = getattr(context,entrada)
        for func in ins.getmembers(source,ins.isfunction):
            if func[0] in toollist:
                continue
            toollist[func[0]] = func[1]
        
        for clase in ins.getmembers(source,ins.isclass):
            if clase[0] in toollist:
                continue
            toollist[clase[0]] = clase[1]
    if withReturn:
        return toollist
