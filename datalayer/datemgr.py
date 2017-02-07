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

def getDateIndexElement(max_date, min_date, char):
    #TODO formatos todavia usan %
    minidx = []
    if char == 'w':
        min_rg = 0
        max_rg = 6 +1
        format = '%01d'
    elif char == 'v':
        min_rg = 0
        max_rg = 5 + 1
        format = '%01d'
    #
    elif char == 'd':
        min_rg = 1
        max_rg = 31 +1
        format = '%02d'
    elif char == 'J':
        min_rg = 1
        max_rg = 366 +1
        format = '%03d'
    elif char == 'W':
        min_rg = 1
        max_rg = 53 +1
        format = '%02d'
    elif char == 'm':
        min_rg = 1
        max_rg = 12+1
        format = '%02d'
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
        

    for j in range(min_rg, max_rg):
        #TODO este proceso solo funciona con dias, no con horas. es una limitacion conocida.
        #FIXME tengo la impresion que es un poco lento
        #TODO explorar la posibilidad de utilizar el paquete Dateutil 
        #minidx.append(QString(format % j)) 
        minidx.append(format % j) 

    return minidx

def getDateIndex(max_date,  min_date, fmt, **opciones):     
    ''' 
       TODO supera los intervalos mínimos
       TODO esta clarisimo que ademas admite seria optimizacion
    '''
    #DELIMITER = '.'
    base = []
    for char in fmt:
        result = getDateIndexElement(max_date, min_date, char)
        if len(base) == 0:
            base = result
        else:
            tmp = []
            for j in base:     #jerarquia de fechas anterior
                for k in result:   #jerarquia actual
                    tmp.append(j+DELIMITER+k)
            base = tmp      
    '''
    formateamos ahora de modo consistente a los otros cursores
    '''
    resultado = []
    if 'nholder' in opciones:   
        tamanyo = opciones['nkeys']+opciones['nholder']
    else:
        tamanyo = opciones['nkeys']
    for elem in base:
        final_record = [elem,] 
        temporal = elem.split(DELIMITER)
        for k in range(tamanyo):
            if k < len(temporal):
                final_record.append(DELIMITER.join(temporal[0:k+1]))
            else:
                final_record.append('')
        resultado.append(final_record)              
    #resultado = list(map(base,regFiller,**opciones))
    return resultado
    #normalizado = []
    #for i in base:
        #normalizado.append([i, ]) #convert into 0 list

    #return normalizado
        
def getDateEntry(psource, fmt, driver='QSQLITE'):
    
    source=norm2List(psource)[-1]  #no esta normalizado el uso de lista o parametros indivudales
    #DRIVERNAME
    marker = {}
    if driver in ('QSQLITE','sqlite'):
        function = 'strftime'
        marker["Y"] = '%Y'
        marker["m"]= '%m'
        marker["W"]= '%W'
        marker["d"] = '%d'
        marker["w"] = '%w'
        marker["J"] = '%J'
    #elif driver in ('mysql','mariadb','mysqldb','mysqlconnector'):  #GENERADOR
    elif driver in ('mysql',):  #GENERADOR
        function = 'DATE_FORMAT' 
        marker["Y"] = '%Y'
        marker["m"]= '%m'
        marker["W"]= '%U'
        marker["d"] = '%d'
        marker["w"] = '%w'
        marker["J"] = '%j'
    #elif driver in ('postgresql','postgres','pg','psycopg2','oracle'):
    elif driver in ('postgresql','oracle'):
        function = 'to_char'   
        marker["Y"] =  'YYYY'
        marker["m"]= 'MM'
        marker["W"]= 'WW'
        marker['v'] = 'W'
        marker["d"] = 'DD'
        marker["w"] = 'D'
        marker["J"] = 'DDD'
    else:
        print('Date conversions for driver %s still not implemented'%driver)
        return None
        
    #DELIMITER = '.'
        
    entrada={}

    fmt_string = ''

    for char in fmt:
        if fmt_string != '':
            fmt_string += DELIMITER
        fmt_string += marker[char]
    element = function + "("
    if driver in ('QSQLITE','sqlite'):
        element += "'" + fmt_string + "'," + source
    else:
        element += source + ",'" + fmt_string +  "'"
    element += ')'
    
    entrada['fmt'] = 'txt'
    entrada['mask']  = fmt
    entrada['name'] = source + '_' + fmt
    entrada['elem'] = element
    
    return entrada
    
def getDateSlots(fieldname, driver='QSQLITE', zoom='n'):
    #FIXME no se procesa el zoom
    """
      fechas julianas excluidas en sqlite  no es lo que quiero
    """
    base_collection= []
    zoom_collection=[]
    if driver  in ('QSQLITE','sqlite'):
        base_col=('Y', 'Ym', 'YW', 'YW','m', 'md', 'mw', 'W', 'Ww','d', 'w', )
        # base_col=('Y', 'Ym', 'YW', 'YW','m', 'md', 'mw', 'W', 'Ww', 'J', 'd', 'w', )
    else:
        base_col=('Y', 'Ym', 'YW', 'Ymv','m', 'mv', 'md', 'mw','mvw',  'W', 'Ww', 'J', 'd', 'w','v' )
    zoom_col=('Ymd', 'Ymw','YWw')    
    #zoom_col=('YJ','Ymd', 'Ymw', 'YmWw','YWw')
        
    for i in base_col:
        base_collection.append(getDateEntry(fieldname, i,  driver)) 
    for entrada in zoom_col:
        tuplas = []
        for l in range(len(entrada)):
            tuplas.append(getDateEntry(fieldname,entrada[0:l+1],driver))
        zoom_collection.append(tuplas)
        #print(entrada)
        #pprint(tuplas)
    return base_collection,zoom_collection

def genTrimestreCode(fieldname,driver='QSQLITE'):
    """
       TODO ver si se puede simplificar utilizando esta sintaxis
            cadena_a = '{1}({2},{3})'
            cadena = cadena_a
            print(cadena.format('SQL1','FUNC','%x','var'))

    """
    trimarray = (
            ("('01','02','03')",'1'),
            ("('04','05','06')",'2'),
            ("('07','08','09')",'3'),
            ("('10','11','12')",'4'),
            )
    placeholder = '$$1'
    
    if driver in ('QSQLITE','sqlite'):
        function = 'strftime'
        function_mask ="{0}('{2}',{1})"
        year_marker='%Y'
        month_marker = '%m'
        cat_stmt = "{} ||:||'{}' "
    #elif driver in ('mysql','mariadb','mysqldb','mysqlconnector'):  #GENERADOR
    elif driver in ('mysql',):
        function = 'DATE_FORMAT'
        function_mask ="{0}({1},'{2}')"
        year_marker='%Y'
        month_marker = '%m'
        cat_stmt = "CONCAT_WS(':',{},'{}')"
    #elif driver in ('postgresql','postgres','pg','psycopg2','oracle'):
    elif driver in ('postgresql','oracle'):
        function = 'TO_CHAR'
        function_mask ="{0}({1},'{2}')"
        year_marker='YYYY'
        month_marker = 'MM'
        cat_stmt = "{} ||:||'{}' "
    else:
        print('Date conversions for driver %s still not implemented'%driver)
        return None

    year_stmt = function_mask.format(function,fieldname,year_marker)
    pyear_stmt = function_mask.format(function,placeholder,year_marker)
    selector = function_mask.format(function,placeholder,month_marker)
    print(year_stmt,selector)
    case_array = []
    case_array.append("case")
    for entry in trimarray:
        sel_stmt ='{} in {}'.format(selector,entry[0])
        concatenation = cat_stmt.format(pyear_stmt,entry[1])
        
        cadena="when {} then {}".format(sel_stmt,concatenation)
        case_array.append(cadena)
    case_array.append("end as $$2")

    trimestre = {
            "name": fieldname+"_trimestre",
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
        
                
