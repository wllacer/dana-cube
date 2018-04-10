#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals



'''
Documentation, License etc.

TODO
    to array y funciones para extraer las cabeceras
'''
def mergeString(string1,string2,connector):
    """
    __OBSOLETE__ use mergeStrings
    
    old version, deprecate
    """
    return mergeStrings(connector,string1,string2,spaced=True)


def mergeStrings(connector,*list,spaced=False):
    """
    
    Permite unir cadenas u objetos convertibles en cadenas en una sola secuencia. Nulos y sin valor son eliminados. Pudes ser invocado con un parametro por elemento o con * co una lista o tupla

    Si se desea mantener las instancias sin valor (pero no nulas) use util.record_functions.norm2String
    
    """
    klist = [ str(item).strip() for item in list if item is not None and len(str(item).strip()) > 0 ]
    if len(klist) == 0:
        return ''
    if spaced:
        connector = ' '+connector+' '
    return connector.join(klist)


def toNormString(entrada,placeholder='_'):
    """
    Funcion para convertir una cadena en su "equivalente" ASCII. Funciona para textos españoles, al menos. 
    
    Pensada para convertir cualquier texto en nombre de campo SQL
    Eliminamos diacriticos,
    Convertimos todo lo que no sea texto o numerico a '_' como marcador
    SI detecta un caracter irreducible (>128) lo convierte en al cedena u... con ... su valor numerico
    Y todo a minuscula
    
    """
    import unicodedata
    norm_form = unicodedata.normalize('NFD',entrada)
    resultado = ""
    for char in norm_form:
        if unicodedata.category(char) == 'Lu': #string uppercase
            nchar = char.lower()
        elif unicodedata.category(char) in ('Ll','Nd','Nl','No'):
            nchar = char
        elif unicodedata.combining(char):
            continue
        else:
            if ord(char) > 127:
                nchar = char
            else:
                nchar = placeholder

        if ord(nchar) > 128:
            nchar = 'u' + str(ord(nchar))

        resultado += nchar
        
            
    return resultado
