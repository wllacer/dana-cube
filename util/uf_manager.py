#!/usr/bin/env python
# -*- coding: utf-8 -*-


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
    """
    if 'name' not in kwparms or 'entry' not in kwparms:
        print('Parametro obligatorio no suminstrado (name, entry o type')
        return
    item= dict()
    item['exec'] = ((kwparms['entry'],kwparms.get('type'),kwparms.get('aux_parm'),),)
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
