#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

@package estimaciones
# 0.3
'''
from pprint import pprint


from datetime import date,datetime
from dateutil.relativedelta import *
from dateutil.rrule import *
from dateutil.parser import parse

CLASES_INTERVALO = ('todo','actual','intervalo','ultimo intervalo Abierto','ultimo intervalo Cerrado')
TIPOS_INTERVALO = ('año','cuatrimestre','trimestre','mes','quincena','semana','dia')


def isDate(string):
    try:
        k = parse(string)
    except ValueError:
        return False
    return True

def ldm(anyo,mes):
    if mes in (1,3,5,7,8,10,12):
       return 31
    elif mes in (4,6,9,11):
       return 30
    else:
       if (anyo // 400 == 0 and  anyo // 100 == 0)  or (anyo // 100 != 0 and anyo // 4 == 0):
           return 29
       else:
           return 28
   
        
def dateRange(clase_idx,range_idx,fecha=None,periodo=None,fmt=None):
    if fecha is None:
        fecha = date.today()+relativedelta(days=-1)
    if periodo is None:
        periodo = 0
    intervalo = [None,None]
    try:
        clase = CLASES_INTERVALO[clase_idx]
        range = TIPOS_INTERVALO[range_idx]
    except IndexError:
        print('La clase o tipo de intervalos temporales no esta definida')
        return intervalo

    if    clase == CLASES_INTERVALO[0]:
        return intervalo
    elif    clase == CLASES_INTERVALO[1]:
        intervalo = dateActual(range,fecha,periodo)
    elif  clase == CLASES_INTERVALO[2]:
        intervalo = datePeriodo(range,fecha,periodo)
    elif  clase == CLASES_INTERVALO[3]:
        intervalo = dateUltimoAbierto(range,fecha,periodo)
    elif  clase == CLASES_INTERVALO[4]:
        intervalo = dateUltimoCerrado(range,fecha,periodo)

    if not fmt:
        return intervalo
    elif fmt == 'fecha':
        return intervalo
    elif fmt == 'fechahora':
        dtintervalo = list(map(lambda d: datetime(d.year,d.month,d.day),intervalo))
        dtintervalo[1]=dtintervalo[1]+relativedelta(hours=23,minutes=59,seconds=59)
        return dtintervalo
    else:
        return intervalo
        
def dateActual(flag,HOY,intervalo=None):
    # actual:
    DESDE = None
    HASTA = None
    if flag == TIPOS_INTERVALO[0]:
       DESDE = date(HOY.year,1,1)
       HASTA = date(HOY.year,12,31)
    elif flag == TIPOS_INTERVALO[1]:
       if HOY.month in (1,2,3,4):
            DESDE = date(HOY.year,1,1)
            HASTA = date(HOY.year,4,30)
       elif HOY.month in (5,6,7,8):
            DESDE = date(HOY.year,5,1)
            HASTA = date(HOY.year,8,31)
       elif HOY.month in (9,10,11,12):
            DESDE = date(HOY.year,9,1)
            HASTA = date(HOY.year,12,31)
    elif flag == TIPOS_INTERVALO[2]:
       if HOY.month in (1,2,3):
            DESDE = date(HOY.year,1,1)
            HASTA = date(HOY.year,3,31)
       elif HOY.month in (4,5,6):
            DESDE = date(HOY.year,4,1)
            HASTA = date(HOY.year,6,30)
       elif HOY.month in (7,8,9):
            DESDE = date(HOY.year,6,1)
            HASTA = date(HOY.year,9,30)
       elif HOY.month in (10,11,12):
            DESDE = date(HOY.year,10,1)
            HASTA = date(HOY.year,12,31)
    elif flag == TIPOS_INTERVALO[3]:
       DESDE = date(HOY.year,HOY.month,1)
       HASTA = date(HOY.year,HOY.month,ldm(HOY.year,HOY.month))
    elif flag == TIPOS_INTERVALO[4]:
       if HOY.day <= 15:
           DESDE=date(HOY.year,HOY.month,1)
           HASTA=date(HOY.year,HOY.month,15)
       else:
           DESDE=date(HOY.year,HOY.month,16)
           HASTA=date(HOY.year,HOY.month,ldm(HOY.year,HOY.month))
    elif flag == TIPOS_INTERVALO[5]:
       diasemana = HOY.weekday()
       DESDE = HOY+relativedelta(days=-(diasemana))
       HASTA = HOY+relativedelta(days=+(6-diasemana))
    elif flag == TIPOS_INTERVALO[6]:
       DESDE=HASTA=HOY
       
    return DESDE,HASTA

def datePeriodo(flag,HOY,intervalos=None):
    # actual:
    HASTA = HOY
    if intervalos is None:
       factor = 1
    else:
       factor = intervalos
    if flag == TIPOS_INTERVALO[0]:
        DESDE=HOY+relativedelta(years=-factor)
    elif flag == TIPOS_INTERVALO[1]:
        DESDE=HOY+relativedelta(months=-factor*4)
    elif flag == TIPOS_INTERVALO[2]:
        DESDE=HOY+relativedelta(months=-factor*3)
    elif flag == TIPOS_INTERVALO[3]:
        DESDE=HOY+relativedelta(months=-factor)
    elif flag == TIPOS_INTERVALO[4]:
        DESDE=HOY+relativedelta(days=-factor*15)
    elif flag == TIPOS_INTERVALO[5]:
        DESDE=HOY+relativedelta(days=-factor*7)
    elif flag == TIPOS_INTERVALO[6]:
        HASTA=HOY
        DESDE = HASTA+relativedelta(days=-(factor -1))
    return DESDE,HASTA

def dateUltimoAbierto(flag,HOY,intervalos=None):
    # actual:
    DESDE,HASTA = dateActual(flag,HOY)
    if intervalos is None:
       factor = 1
    else:
       factor = intervalos
    if flag == TIPOS_INTERVALO[0]:
        DESDE=DESDE+relativedelta(years=-factor)
    elif flag == TIPOS_INTERVALO[1]:
        DESDE=DESDE+relativedelta(months=-factor*4)
    elif flag == TIPOS_INTERVALO[2]:
        DESDE=DESDE+relativedelta(months=-factor*3)
    elif flag == TIPOS_INTERVALO[3]:
        DESDE=DESDE+relativedelta(months=-factor)
    elif flag == TIPOS_INTERVALO[4]:
        DESDE=DESDE+relativedelta(days=-factor*15)
    elif flag == TIPOS_INTERVALO[5]:
        DESDE=DESDE+relativedelta(days=-factor*7)
    elif flag == TIPOS_INTERVALO[6]:
        HASTA=HOY
        DESDE = HASTA+relativedelta(days=-(factor -1))

    return DESDE,HASTA

def dateUltimoCerrado(flag,HOY,intervalos=None):
    # actual:
    HASTA,PFIN = dateActual(flag,HOY)
    HASTA=HASTA+relativedelta(days=-1)
    if intervalos is None:
       factor = 1
    else:
       factor = intervalos
    if flag == TIPOS_INTERVALO[0]:
        DESDE = HASTA+relativedelta(years=-factor,days=+1)
    elif flag == TIPOS_INTERVALO[1]:
        DESDE = HASTA+relativedelta(months=-factor*4,days=+1)
    elif flag == TIPOS_INTERVALO[2]:
        DESDE = HASTA+relativedelta(months=-factor*3,days=+1)
    elif flag == TIPOS_INTERVALO[3]:  #el calculo del mes es un poco mas sutil (debe calcularse desde el inico del mes anterior,el +1 dia no funciona
        HASTA = HASTA+relativedelta(days=+1)
        DESDE = HASTA+relativedelta(months=-factor)
        HASTA = HASTA+relativedelta(days=-1)
    elif flag == TIPOS_INTERVALO[4]:
        DESDE = HASTA+relativedelta(days=-(factor*15 -1))
    elif flag == TIPOS_INTERVALO[5]:
        DESDE = HASTA+relativedelta(days=-(factor*7 -1))
    elif flag == TIPOS_INTERVALO[6]:
        if HASTA == date.today():
           HASTA = HASTA+relativedate(days=-1)
           DESDE = HASTA+relativedelta(days=-(factor))
        else:
           DESDE = HASTA+relativedelta(days=-(factor -1))
    return DESDE,HASTA

def test():
    AHORA = datetime.now() 
    HOY   = date.today()
    CLASES_INTERVALO = ('actual','intervalo','ultimoAbierto','ultimoCerrado')
    TIPOS_INTERVALO = ('año','cuatrimestre','trimestre','mes','quincena','semana','dia')
    #print(AHORA,HOY)
    #DESDE = date(HOY.year,1,1)
    #print(DESDE)
    #print('Proximo Mes',HOY+relativedelta(months=+1))
    #print('Proximo Mes menos una semana',HOY+relativedelta(months=+1,weeks=-1))
    #DESDE = None
    #HASTA = None
    print('el actual')
    periodo = 3
    for flag in TIPOS_INTERVALO:
        print(flag)
        print ('\t actual  de {0[0]} a {0[1]}'.format(dateActual(flag,HOY)))
        print ('\t periodo de {0[0]} a {0[1]}'.format(datePeriodo(flag,HOY,periodo)))
        print ('\t abieto  de {0[0]} a {0[1]}'.format(dateUltimoAbierto(flag,HOY,periodo)))
        print ('\t cerrado de {0[0]} a {0[1]}'.format(dateUltimoCerrado(flag,HOY,periodo)))
        
        
        intervalo = dateUltimoCerrado(flag,HOY,periodo)
        dtintervalo = list(map(lambda d: datetime(d.year,d.month,d.day),intervalo))
        print(intervalo,dtintervalo)
        #pprint (list(rrule(DAILY,dtstart=dtintervalo[0]).between(dtintervalo[0],dtintervalo[1],inc=True)))
        
if __name__ == '__main__':

    #experimental()
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    test()
