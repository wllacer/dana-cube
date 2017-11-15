# -*- coding=utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''
DELIMITER = ':'
from decimal import *
from pprint import *

import datetime

import time
from util.record_functions import norm2List

DB_DATE_QUIRKS = {
    "sqlite":{
        "function":'strftime',
        "function_mask":"{0}('{2}',{1})" ,   #0 funcion 1 campo 2 formato
        "cat":"{} ||':'||'{}' ",
        "marker":{ "Y":'%Y', "m":'%m', "W":'%W', "d": '%d',"w": '%w',"J": '%J'},
        },
    "mysql":{
        "function":'DATE_FORMAT',
        "function_mask": "{0}({1},'{2}')",
        "cat":"CONCAT_WS(':',{},'{}')",
        "marker":{ "Y":'%Y', "m":'%m', "W":'%U', "d": '%d',"w": '%w',"J": '%j'},
        },
    "postgresql":{
        "function":'TO_CHAR',
        "function_mask": "{0}({1},'{2}')",
        "cat":"{} ||':'||'{}' ",
        "marker":{ "Y":'YYYY', "m":'MM', "W":'WW', "d": 'DD',"w": 'D',"J": 'DDD'},
        },
    "oracle":{
        "function":'TO_CHAR',
        "function_mask": "{0}({1},'{2}')",
        "cat":"{} ||:||'{}' ",
        "marker":{ "Y":'YYYY', "m":'MM', "W":'WW', "d": 'DD',"w": 'D',"J": 'DDD'},
        },
    }

def validate(date_text,fmt):  
    # Solo formatos ordinarios
    if ('C','Q','q') in fmt:
        return True
    formato = ''
    for char in fmt:
        if formato == '':
            formato += '%'+char
        else:
            formato += ':%'+char
        
    try:
        if date_text != datetime.datetime.strptime(date_text, formato).strftime(formato):
            raise ValueError
        return True
    except ValueError:
        return False

def getDateIndexElement(max_date, min_date, char):
    #TODO formatos todavia usan %
    minidx = []
    if char == 'w':
        min_rg = 0
        max_rg = 6 
        format = '%01d'
    elif char == 'v':
        min_rg = 0
        max_rg = 5 + 1
        format = '%01d'
    #
    elif char == 'd':
        min_rg = 1
        max_rg = 31 
        format = '%02d'
    elif char == 'J':
        min_rg = 1
        max_rg = 366 
        format = '%03d'
    elif char == 'W':
        min_rg = 1
        max_rg = 53 
        format = '%02d'
    elif char == 'm':
        min_rg = 1
        max_rg = 12
        format = '%02d'
    elif char == 'C':
        min_rg = 1 
        max_rg = 3 + 1 
        format = '%01d'
    elif char == 'Q':
        min_rg = 1 
        max_rg = 4 + 1 
        format = '%01d'
    elif char == 'q':
        min_rg = 1 
        max_rg = 2 + 1 
        format = '%01d'

    elif char == 'Y':
        # GENERADOR
        if isinstance(min_date,(datetime.time,datetime.date,)):
            min_rg = min_date.year
        else:
            min_rg=int(Decimal(str(min_date[0:4])))
        if isinstance(max_date,(datetime.time,datetime.date,)):
            max_rg = max_date.year + 1
        else:
            max_rg=int(Decimal(str(max_date[0:4])))+1
        format = '%04d'
        

    for j in range(min_rg, max_rg +1 ):
        #TODO este proceso solo funciona con dias, no con horas. es una limitacion conocida.
        #FIXME tengo la impresion que es un poco lento
        #TODO explorar la posibilidad de utilizar el paquete Dateutil 
        #minidx.append(QString(format % j)) 
        minidx.append(format % j) 

    return minidx

def getDateIndexNew(max_date,  min_date, fmt, **opciones):     
    ''' 
       TODO supera los intervalos mínimos
       TODO esta clarisimo que ademas admite seria optimizacion
       TODO como verificar que van a introducirse valores correctos HINT pasar a fecha python y provocar excepcion
    '''
    #DELIMITER = '.'
    previous = []
    next = []
    ranges = []
    for k,char in  enumerate(fmt):  
        # obtenemos el abanico de valores para este elemento
        ranges = getDateIndexElement(max_date, min_date, char)
        # si es el primer elemento creamos un cursor (list of list) con los valores
        if len(previous) == 0 :  #es el primer elemento
            previous = [ [item,] for item in ranges ]
            next = previous[:]
        else:
            # partiendo de los resultados de la iteracion anterior creamos un nuevo cursor con un atributo mas y 
            # lo rellenamos con el cruce anterior X rango de ese elemento
            previous = next[:]
            next = []
            for entrada in previous:
                for rango in ranges:
                    entry = list(entrada[:])
                    # TODO garantizar que eso sea una fecha valida
                    if validate(entry[-1]+DELIMITER+ rango,fmt[0:k+1]):
                        entry.append(entry[-1]+DELIMITER+ rango)  #k empieza en 0
                        next.append(entry)
        
    return next
        
def getDateEntry(psource, fmt, driver='sqlite'):
    
    source=norm2List(psource)[-1]  #no esta normalizado el uso de lista o parametros indivudales
    #DRIVERNAME
    try:
        marker = DB_DATE_QUIRKS[driver]['marker']
        function = DB_DATE_QUIRKS[driver]['function']
        fmask = DB_DATE_QUIRKS[driver]['function_mask']
    except KeyError :
        print('Date conversions for driver %s still not implemented'%driver)
        return None
        
    #DELIMITER = '.'
        
    entrada={}

    fmt_string = ''

    for char in fmt:
        if fmt_string != '':
            fmt_string += DELIMITER
        fmt_string += marker[char]
    element = fmask.format(function,source,fmt_string)
    
    entrada['fmt'] = 'txt'
    entrada['mask']  = fmt
    entrada['name'] = source + '_' + fmt
    entrada['elem'] = element
    
    return entrada
    

def makeCaseArrayInterval(interval,driver):
    rangos = {
        "cuatrimestre": (('01','04',),('05','08'),('09','12')),
        "trimestre": (('01','03',),('04','06'),('07','09'),('10','12')),
        "quincena":(('01','15'),('16','31'),)
        }
    placeholder = '$$1'
    try:
        function = DB_DATE_QUIRKS[driver]['function']
        function_mask = DB_DATE_QUIRKS[driver]['function_mask']
        year_marker= DB_DATE_QUIRKS[driver]['marker']['Y']
        month_marker = DB_DATE_QUIRKS[driver]['marker']['m']
        day_marker =  DB_DATE_QUIRKS[driver]['marker']['d']
        cat_stmt = DB_DATE_QUIRKS[driver]['cat']
    except KeyError:
        print('Date conversions for driver %s still not implemented'%driver)
        return None

    pyear_stmt = function_mask.format(function,placeholder,year_marker)

    if interval == 'C':
        nombre = 'cuatrimestre'
        selector = function_mask.format(function,placeholder,month_marker)
        pyear_stmt = function_mask.format(function,placeholder,year_marker)
    elif interval == 'Q':
        nombre = 'trimestre'
        selector = function_mask.format(function,placeholder,month_marker)
        pyear_stmt = function_mask.format(function,placeholder,year_marker)
    elif interval == 'q':
        selector = function_mask.format(function,placeholder,day_marker)
        pyear_stmt = function_mask.format(function,placeholder,year_marker+':'+month_marker)
        cat_stmt = cat_stmt.replace(':','-')
        nombre = 'quincena'
    else:
        return None
    rango = rangos[nombre]
    
    case_array = []
    case_array.append("CASE")    
    for k,entry in enumerate(rango):
        destination = cat_stmt.format(pyear_stmt,str(k +1))
        sel_stmt ="WHEN {} BETWEEN '{}' AND '{}' THEN {}".format(selector,entry[0],entry[1],destination)
        case_array.append(sel_stmt)
    case_array.append("END AS $$2")
    
    return case_array

def getIntervalCode(interval,fieldname,driver):
    if interval == 'C':
       nombre = 'cuatrimestre'
    elif interval == 'Q':
        nombre = 'trimestre'
    elif interval == 'q':
        nombre == 'quincena'
    else:
        return None
    
    try:
        function = DB_DATE_QUIRKS[driver]['function']
        function_mask = DB_DATE_QUIRKS[driver]['function_mask']
        year_marker= DB_DATE_QUIRKS[driver]['marker']['Y']
    except KeyError:
        print('Date conversions for driver %s still not implemented'%driver)
        return None
    
    case_array=makeCaseArrayInterval(interval,driver)
    
    year_stmt = function_mask.format(function,fieldname,year_marker)
    trimestre = {
            "name": fieldname+"_"+ nombre,
            "class":"h",
            "prod": [
                {
                    "elem": year_stmt,
                    "name": "año",
                    "class":"o"
                },
                {
                    "elem": fieldname,
                    "case_sql":case_array,
                    "name": "trimestre",
                    "class":"c"
                    }
                ]
            }
    return trimestre

def genTrimestreCode(fieldname,driver='sqlite'):
    return getIntervalCode('Q',fieldname,driver)
def genCuatrimestreCode(fieldname,driver='sqlite'):
    return getIntervalCode('C',fieldname,driver)
def genQuincenaCode(fieldname,driver='sqlite'):
    return getIntervalCode('q',fieldname,driver)
    
def oracleDateString(pcadena):
    import re
    delimitadores = ('YYYY','MM','DD','HH24','MI','SS')
    cadena = '{}'.format(pcadena)
    desguace = re.split('[ \-:]+',cadena)
    salida = "TO_DATE('{}','".format(cadena)
    for k in range(len(desguace)):
        if k == 0:
            salida = salida + delimitadores[k]
        elif k < 3:
            salida = '-'.join((salida,delimitadores[k]))
        elif k == 3:
            salida = ' '.join((salida,delimitadores[k]))
        else:
            salida = ':'.join((salida,delimitadores[k]))
    return salida + "')"
        
                
