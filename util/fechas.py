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
   
        
def dateRange(clase,range,fecha=None,periodo=None):
    if fecha is None:
        fecha = date.today()+relativedelta(days=-1)
    if periodo is None:
        periodo = 0
    intervalo = [None,None]
    if    clase == mCLASES[0]:
        intervalo = dateActual(range,fecha,periodo)
    elif  clase == mCLASES[1]:
        intervalo = datePeriodo(range,fecha,periodo)
    elif  clase == mCLASES[2]:
        intervalo = dateUltimoAbierto(range,fecha,periodo)
    elif  clase == mCLASES[3]:
        intervalo = dateUltimoCerrado(range,fecha,periodo)
    return intervalo
        
def dateActual(flag,HOY,periodo=None):
    # actual:
    DESDE = None
    HASTA = None
    if flag == 'año':
       DESDE = date(HOY.year,1,1)
       HASTA = date(HOY.year,12,31)
    elif flag == 'cuatrimestre':
       if HOY.month in (1,2,3,4):
            DESDE = date(HOY.year,1,1)
            HASTA = date(HOY,year,4,30)
       elif HOY.month in (5,6,7,8):
            DESDE = date(HOY.year,5,1)
            HASTA = date(HOY.year,8,31)
       elif HOY.month in (9,10,11,12):
            DESDE = date(HOY.year,9,1)
            HASTA = date(HOY.year,12,31)
    elif flag == 'trimestre':
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
    elif flag == 'mes':
       DESDE = date(HOY.year,HOY.month,1)
       HASTA = date(HOY.year,HOY.month,ldm(HOY.year,HOY.month))
    elif flag == 'quincena':
       if HOY.day <= 15:
           DESDE=date(HOY.year,HOY.month,1)
           HASTA=date(HOY.year,HOY.month,15)
       else:
           DESDE=date(HOY.year,HOY.month,16)
           HASTA=date(HOY.year,HOY.month,ldm(HOY.year,HOY.month))
    elif flag == 'semana':
       diasemana = HOY.weekday()
       DESDE = HOY+relativedelta(days=-(diasemana))
       HASTA = HOY+relativedelta(days=+(6-diasemana))
    elif flag == 'dia':
       DESDE=HASTA=HOY
       
    return DESDE,HASTA

def datePeriodo(flag,HOY,periodos=None):
    # actual:
    HASTA = HOY
    if periodos is None:
       factor = 1
    else:
       factor = periodos
    if flag == 'año':
        DESDE=HOY+relativedelta(years=-factor)
    elif flag == 'cuatrimestre':
        DESDE=HOY+relativedelta(months=-factor*4)
    elif flag == 'trimestre':
        DESDE=HOY+relativedelta(months=-factor*3)
    elif flag == 'mes':
        DESDE=HOY+relativedelta(months=-factor)
    elif flag == 'quincena':
        DESDE=HOY+relativedelta(days=-factor*15)
    elif flag == 'semana':
        DESDE=HOY+relativedelta(days=-factor*7)
    elif flag == 'dia':
       DESDE=HASTA=HOY      
    return DESDE,HASTA

def dateUltimoAbierto(flag,HOY,periodos=None):
    # actual:
    DESDE,HASTA = dateActual(flag,HOY)
    if periodos is None:
       factor = 1
    else:
       factor = periodos
    if flag == 'año':
        DESDE=DESDE+relativedelta(years=-factor)
    elif flag == 'cuatrimestre':
        DESDE=DESDE+relativedelta(months=-factor*4)
    elif flag == 'trimestre':
        DESDE=DESDE+relativedelta(months=-factor*3)
    elif flag == 'mes':
        DESDE=DESDE+relativedelta(months=-factor)
    elif flag == 'quincena':
        DESDE=DESDE+relativedelta(days=-factor*15)
    elif flag == 'semana':
        DESDE=DESDE+relativedelta(days=-factor*7)
    elif flag == 'dia':
       DESDE=HASTA=HOY      
    return DESDE,HASTA

def dateUltimoCerrado(flag,HOY,periodos=None):
    # actual:
    HASTA,PFIN = dateActual(flag,HOY)
    HASTA=HASTA+relativedelta(days=-1)
    if periodos is None:
       factor = 1
    else:
       factor = periodos
    if flag == 'año':
        DESDE = HASTA+relativedelta(years=-factor,days=+1)
    elif flag == 'cuatrimestre':
        DESDE = HASTA+relativedelta(months=-factor*4,days=+1)
    elif flag == 'trimestre':
        DESDE = HASTA+relativedelta(months=-factor*3,days=+1)
    elif flag == 'mes':  #el calculo del mes es un poco mas sutil (debe calcularse desde el inico del mes anterior,el +1 dia no funciona
        HASTA = HASTA+relativedelta(days=+1)
        DESDE = HASTA+relativedelta(months=-factor)
        HASTA = HASTA+relativedelta(days=-1)
    elif flag == 'quincena':
        DESDE = HASTA+relativedelta(days=-(factor*15 -1))
    elif flag == 'semana':
        DESDE = HASTA+relativedelta(days=-(factor*7 -1))
    elif flag == 'dia':
       DESDE=HASTA    
    return DESDE,HASTA

def test():
    AHORA = datetime.now() 
    HOY   = date.today()
    mCLASES = ('actual','intervalo','ultimoAbierto','ultimoCerrado')
    mTYPES = ('año','cuatrimestre','trimestre','mes','quincena','semana','dia')
    #print(AHORA,HOY)
    #DESDE = date(HOY.year,1,1)
    #print(DESDE)
    #print('Proximo Mes',HOY+relativedelta(months=+1))
    #print('Proximo Mes menos una semana',HOY+relativedelta(months=+1,weeks=-1))
    #DESDE = None
    #HASTA = None
    print('el actual')
    periodo = 3
    for flag in mTYPES:
        print(flag)
        print ('\t actual  de {0[0]} a {0[1]}'.format(dateActual(flag,HOY)))
        print ('\t periodo de {0[0]} a {0[1]}'.format(datePeriodo(flag,HOY,periodo)))
        print ('\t abieto  de {0[0]} a {0[1]}'.format(dateUltimoAbierto(flag,HOY,periodo)))
        print ('\t cerrado de {0[0]} a {0[1]}'.format(dateUltimoCerrado(flag,HOY,periodo)))

if __name__ == '__main__':

    #experimental()
    test()
