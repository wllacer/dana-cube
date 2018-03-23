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
    if not string1 :
        merge = string2
    elif not string2:
        merge = string1
    elif len(string1.strip()) > 0 and len(string1.strip()) > 0:
        merge ='{} {} {}'.format(string1,connector,string2)
    elif len(string1.strip()) > 0 or len(string2.strip()) > 0: 
        merge ='{}{}'.format(string1,string2).strip()
    else:
        merge = ''

    return merge

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
