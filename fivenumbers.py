import random

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
    lista.sort()
    #print lista

    mid = len(lista)/2
    if len(lista)%2 == 0:
        median  = (lista[mid - 1] + lista[mid] )/2.0
    else:
        median = lista[mid]
#
    return median
    
    
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
    mid=len(t_lista)/2
    if len(t_lista)%2 == 0:
       cuartil_1 = median(t_lista[0: mid ])
       cuartil_3 =median(t_lista[mid: ])
    else:
       cuartil_1 = median(t_lista[0: mid ])
       cuartil_3 = median(t_lista[mid+ 1: ])
    intercuartil = cuartil_3 - cuartil_1
    borde = intercuartil * 1.5
    low_whisker= mediana - borde
    hig_whisker = mediana + borde
    return  t_lista[0], low_whisker, cuartil_1, mediana, cuartil_3, hig_whisker, t_lista[-1]

def avg(tabla):
    return float(sum(tabla)) / len(tabla)
