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

# import decimal
# import random

#def fmtNumber(number, fmtOptions):
    #""" taken from Rapid development with PyQT book (chapter 5) """
    #fraction, whole = math.modf(number)
    #sign = "-" if whole < 0 else ""
    #whole = "{0}".format(int(math.floor(abs(whole))))
    #digits = []
    #for i, digit in enumerate(reversed(whole)):
        #if i and i % 3 == 0:
            #digits.insert(0, fmtOptions["thousandsseparator"])
        #digits.insert(0, digit)
    #if fmtOptions["decimalplaces"]:
        #fraction = "{0:.7f}".format(abs(fraction))
        #fraction = (fmtOptions["decimalmarker"] +
                #fraction[2:fmtOptions["decimalplaces"] + 2])
    #else:
        #fraction = ""
    #text = "{0}{1}{2}".format(sign, "".join(digits), fraction)#
    
    #return text, sign

def num2text(number,numFmt=False,decChar= '.'):
    if not number:
        return ''
    if numFmt:
        return fmtNumber(number,{'decimalmarker':decChar})[0]
    elif decChar != '.':
        return '{}'.format(number).replace('.',decChar)
    else:
        return str(number)

def fmtNumber(number, optDict=None):
    fmtOpt = dict(thousandsseparator=",",
                    decimalmarker=".",
                    decimalplaces=2)
    if optDict:
        for item in fmtOpt:
            if item in optDict:
                fmtOpt[item] = optDict[item] if optDict[item] != '' else None

    if fmtOpt['thousandsseparator'] and fmtOpt['decimalmarker'] == fmtOpt['thousandsseparator']:
        fmtOpt['thousandsseparator'] = '.' if fmtOpt['decimalmarker'] == ',' else ','

    if isinstance(number,int):
        formatter = '{{:{}{}}}'.format(',' if fmtOpt['thousandsseparator'] else '',
                                        'd' if fmtOpt['decimalplaces'] else '',)
    else:
        formatter = '{{:{}{}{}{}}}'.format(',' if fmtOpt['thousandsseparator'] else '',
                                        '.' if fmtOpt['decimalplaces'] else '',
                                        fmtOpt['decimalplaces'] if fmtOpt['decimalplaces'] else '',
                                        'f' if fmtOpt['decimalplaces'] else '',)
    cadena = formatter.format(number)
    if fmtOpt['thousandsseparator'] not in (',','.'):
        cadena = cadena.replace(',',fmtOpt['thousandsseparator'])
    if fmtOpt['decimalmarker'] not in ('.',','):
        cadena = cadena.replace('.',fmtOpt['decimalmarker'])
    elif fmtOpt['thousandsseparator'] == '.' and fmtOpt['decimalmarker'] == ',':
        cadena = cadena.replace('.','@').replace(',','.').replace('@',',')
    sign = '-' if number < 0 else ''
    return cadena,sign
    

def is_number(s):
    if not s:
        return False
    try:
        n=str(float(s))
        if n == "nan" or n=="inf" or n=="-inf" : return False
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    except TypeError:
        return False
    return True

def s2n(s):
    """
     convert string to number (with good format) else None
    """
    if not s:
        return 0
    if type(s) in (int,float):
        return s
    try:
        i = int(s)
        return i 
    except ValueError:
        pass
    try:
        f = float(s)
        return f
    except ValueError:
        return None

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
 
def stats(plista):
    res=dict()
    if plista:
        datos = [item for item in plista if item is not None ]
        res['count']=len(datos)
    else:
        datos = []
    if len(datos) > 1:
        res['avg']=avg(datos)
        res['std']=std(datos)
        summary=fivesummary(datos)
        res['max']= summary[6]
        res['median']=summary[3]
        res['min']=summary[0]
        res['out_low']=summary[1]
        res['out_hig']=summary[5]
    else:
        res['avg']=None
        res['std']=None
        res['max']= None
        res['median']=None
        res['min']=None
        res['out_low']=None
        res['out_hig']=None

    return res

def isOutlier(item,stats_dict):
    if item is None:
        return False
    if stats_dict['count'] >1:
        if ( item <= stats_dict['out_low'] or item >= stats_dict['out_hig'] ):
            return True
    else:
        return False


        
def fivesummary(plista, nan=False):

    t_lista = [] 
    #if nan:
        #for i in range(0, len(plista)):
            #if is_number(plista[i]):
                #t_lista.append(plista[i])
    #else:
        #t_lista = list(plista)
    #FIXIT 
    #para operar con decimales de la base de datos los convertimos a float. NO es la mejor opcion
    for item in plista:
        if not item and not nan:
            t_lista.append(item)
        elif is_number(item):
            t_lista.append(float(item))
        
            
    
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
