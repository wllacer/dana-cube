# -*- coding=utf -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''
import math
# import random

def is_number(s):
    try:
        n=str(float(s))
        if n == "nan" or n=="inf" or n=="-inf" : return False
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True




def is_number(s):
    try:
        n=str(float(s))
        if n == "nan" or n=="inf" or n=="-inf" : return False
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True


def median(lista):
    '''
      calcula la mediana de una lista
    '''
    lista.sort() #en teoria viene ordenado, pero asi podemos usarlo independientemente

    mid = len(lista)//2
    if len(lista)%2 == 0:
        median  = (lista[mid - 1] + lista[mid] )/2.0
    else:
        median = lista[mid]
#
    return median
    
def avg(tabla):
    '''
      calcula el promedio de una lista
    '''
    return sum(tabla) / len(tabla)
  
def variance(tabla):
    ''' 
    calcula la varianza de una lista
    '''
    return list(map(lambda x: (x - avg(tabla))**2, tabla))
  
def std(tabla):
    '''
    calcula la desviacion típica MUESTRAL. 
    '''
    #return math.sqrt(avg(variance(tabla))) 
    return math.sqrt(sum(variance(tabla))/(len(tabla) -1))
    
def fivesummary(plista, nan=False):

    t_lista = [] 
    if nan:
        for i in range(0, len(plista)):
            if is_number(plista[i]):
                t_lista.append(plista[i])
    else:
        t_lista = list(plista)
        
    t_lista.sort()
    
    mediana = median(t_lista)
    mid=len(t_lista)//2
    if len(t_lista)%2 == 0:
       cuartil_1 = median(t_lista[0: mid ])
       cuartil_3 = median(t_lista[mid: ])
    else:
       cuartil_1 = median(t_lista[0: mid ])
       cuartil_3 = median(t_lista[mid+ 1: ])
    intercuartil = cuartil_3 - cuartil_1
    borde = intercuartil * 1.5
    low_whisker= mediana - borde
    hig_whisker = mediana + borde
    return  t_lista[0], low_whisker, cuartil_1, mediana, cuartil_3, hig_whisker, t_lista[-1]

def outliers(plista, nan= False) :
     fivenmbrs= fivesummary(plista,nan)
     out_elem = []
     for elem in plista:
       if elem < fivenmbrs[1] or elem > fivenmbrs[5] :
          out_elem.append(elem)
     return out_elem
   
def outliers_inc(plista, fivenmbrs) :
     fivenmbrs= fivesummary(plista)
     out_elem = []
     for elem in plista:
       if elem < fivenmbrs[1] or elem > fivenmbrs[5] :
          out_elem.append(elem)
     return out_elem
  
def qualitycontrol(texto,tabla):
  
  if len(tabla) <= 2:
     print ("solo {} datos para {}. Saliendo".format(len(tabla),texto))
     return
 
  fivenmr = fivesummary(tabla)
  print ()
  print ('  {:20}                        ({} elementos)'.format(texto,len(tabla)))
  print ('        media {:5.1f} ± {:5.1f}'.format(avg(tabla),std(tabla)))
  print ('      mediana {:5.1f}'.format(fivenmr[3]))
  if fivenmr[0] < fivenmr[1]:
      alarma_low = '<===='
  else:
      alarma_low = ''
  if fivenmr[5] < fivenmr[6]:
      alarma_hig = '<===='
  else:
      alarma_hig = ''
  print ('          min {:5.1f} ( {:5.1f} ) {}'.format(fivenmr[0],fivenmr[1],alarma_low))
  print ('          max {:5.1f} ( {:5.1f} ) {}'.format(fivenmr[6],fivenmr[5],alarma_hig))
  print ()
  outliers_l = outliers_inc(tabla,fivenmr)
  if len(outliers_l) > 0:
    print('Hay algunos outliers :',outliers_l)

if __name__ == '__main__':
 
    #s=[1,2]
    s=[20,10,10,6,6,6,5,5,5,5,5,3,3,3,3,3,3,3,1,1,1,1,1,1,1]
    qualitycontrol('prueba',s)
