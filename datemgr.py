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
from datetime import *

import time

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
    elif char == 'd':
        min_rg = 0
        max_rg = 31 +1
        format = '%02d'
    elif char == 'J':
        min_rg = 0
        max_rg = 366 +1
        format = '%03d'
    elif char == 'W':
        min_rg = 0
        max_rg = 53 +1
        format = '%02d'
    elif char == 'm':
        min_rg = 0
        max_rg = 12+1
        format = '%02d'
    elif char == 'Y':
        # ????
        min_rg=int(Decimal(str(min_date[0:4])))
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
       TODO admite una leve posibilidad de mejora para excluir fechas imposibles
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
    if isinstance(psource,(list,tuple)):  #hay problemas de congruencia entre modulos
       source = psource[0]
    else:
       source = psource
    marker = {}
    if driver == 'QSQLITE':
        function = 'strftime'
        marker["Y"] = '%Y'
        marker["m"]= '%m'
        marker["W"]= '%W'
        marker["d"] = '%d'
        marker["w"] = '%w'
        marker["J"] = '%J'
    elif driver == 'QMYSQL':
        function = 'DATE_FORMAT' 
        marker["Y"] = '%Y'
        marker["m"]= '%c'
        marker["W"]= '%U'
        marker["d"] = '%d'
        marker["w"] = '%w'
        marker["J"] = '%j'
    elif driver in ('QPSQL', 'QOCI'):
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
    if driver == 'QSQLITE':
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
    if driver == 'QSQLITE':
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

