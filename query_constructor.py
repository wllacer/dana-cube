#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

'''
Documentation, License etc.

@package estimaciones
'''
from pprint import *

def slicer(lista,num_elem=2):

  if not isinstance(lista,(list,tuple)):
     outlist =[lista,] + ['' for k in range(1,num_elem)]
  elif len(lista) <= num_elem :
     outlist=[elem for elem in lista] + ['' for k in range(len(lista),num_elem)]
  else:
     outlist=[lista[k] for k in range(num_elem -1)]+ [[lista[k] for k in range(num_elem -1,len(lista))],]
  return outlist


def selConstructor(kwargs):
    statement = 'SELECT '
    definicion = 'fields'
    if definicion not in kwargs:
       return ''
    
    if 'select_modifier' in kwargs:
       modifier = kwargs['select_modifier'].strip().upper()
       if modifier in ('DISTINCT','FIRST'):
	 statement += modifier + ' '

    if isinstance(kwargs[definicion],(str,unicode)):
      entrada = [kwargs[definicion],]
    else:
      entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      if elemento.strip().find(' ') == -1:
	texto = elemento.strip()
      else:
	texto = '({})'.format(elemento)
	
      if adfijo != '':
	texto = '{}({})'.format(adfijo.strip(),texto)
	
      if ind < (num_elem -1):
	statement += ' {},'.format(texto)
      else:
	statement += ' ' + texto + ' '
	
      ind += 1
    return statement

def fromConstructor(kwargs):
    statement = 'FROM '
    definicion = 'tables'
    if definicion not in kwargs:
       return ''
    
    if isinstance(kwargs[definicion],(str,unicode)):
      entrada = [kwargs[definicion],]
    else:
      entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      if elemento.strip().find(' ') == -1:
	texto = elemento.strip()
      else:
	texto = '({})'.format(elemento)
	
      if adfijo != '':
	texto = '{} as {}'.format(texto,adfijo.strip())
      elif num_elem > 1:
	texto = '{} as t{}'.format(texto,ind)
	
      if ind < (num_elem -1):
	statement += ' {},'.format(texto)
      else:
	statement += ' ' + texto + ' '
	
      ind += 1
    return statement
    
def whereConstructor(kwargs):
  
    statement = 'WHERE '
    definicion = 'where'
    complemento = 'base_filter'
    if definicion not in kwargs:
       kstatement = ''
    else:
       kstatement = searchConstructor(definicion,kwargs)
     
    if complemento in kwargs:
       if kstatement == '':
	 kstatement = complemento
       else:
         kstatement = '({}) AND ({})'.format(complemento,kstatement)
         
    if kstatement == '':
      return ''
    else:
      return statement + ' ' + kstatement
      
       
def groupConstructor(kwargs):
    statement = 'GROUP BY '
    definicion = 'group'
    
    if definicion not in kwargs:
       return ''
    
    if isinstance(kwargs[definicion],(str,unicode)):
      entrada = [kwargs[definicion],]
    else:
      entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for elemento in entrada:
      if elemento.strip().find(' ') == -1:
	texto = elemento.strip()
      else:
	texto = '({})'.format(elemento)
		
      if ind < (num_elem -1):
	statement += ' {},'.format(texto)
      else:
	statement += ' ' + texto + ' '
	
      ind += 1
    
    if statement.strip() != 'GROUP BY ':
       if 'having' in kwargs:
	  having_clause = searchConstructor('having',kwargs)
	  if having_clause.strip() != '':
	    statement += 'HAVING {}'.format(having_clause)
       return statement
    else:
       return ''

def orderConstructor(kwargs):
    statement = 'ORDER BY '
    definicion = 'order'
    if definicion not in kwargs:
       return ''
    
    if isinstance(kwargs[definicion],(str,unicode)):
      entrada = [kwargs[definicion],]
    else:
      entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      if isinstance(elemento,(int,long)):
	texto = '{}'.format(elemento)
      elif elemento.strip().find(' ') == -1:
	texto = elemento.strip()
      else:
	texto = '({})'.format(elemento)
	
      if adfijo != '':
	texto = '{}  {}'.format(texto,adfijo.strip())
	
      if ind < (num_elem -1):
	statement += ' {},'.format(texto)
      else:
	statement += ' ' + texto + ' '
	
      ind += 1
    return statement
    
def searchConstructor(definicion,kwargs):
    statement = ''

    if definicion not in kwargs:
       return ''    
    if isinstance(kwargs[definicion],(str,unicode)):
      entrada = [kwargs[definicion],]
    else:
      entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    print(num_elem,entrada)
        
    for kelem in entrada:
      elemento,adfijo,parms=slicer(kelem,3)   
      #if elemento.strip().find(' ') == -1:
      #	texto = elemento.strip()
      #else:
      #	texto = '({})'.format(elemento)
	
      nadfijo = adfijo.strip().upper()
      if nadfijo in ('IN','NOT IN'):
	texto = '{} {} ({})'.format(elemento.strip(),nadfijo,', '.join(parms))
      elif nadfijo in ('BETWEEN','NOT BETWEEN'):
	texto = '{} {} {} AND {}'.format(elemento.strip(),nadfijo,parms[0].strip(),parms[1].strip())
      else:
	if isinstance(elemento,dict):
	  nelemento = '({})'.format(searchConstructor(definicion,elemento))
	else:
	  nelemento = elemento.strip()
	if isinstance(parms,dict):
	  nparms = '({})'.format(searchConstructor(definicion,parms))
	else:
	  nparms = parms.strip()
	  
	texto = '{} {} {}'.format(nelemento,nadfijo,nparms)
	
      if ind < (num_elem -1):
	statement += ' {} AND'.format(texto)
      else:
	statement += ' ' + texto + ' '
	
      ind += 1
    return statement
  

def queryConstructor(**kwargs):
    '''
       tables
       fields
       select_modifier
       where
       base_filter
       group
       having
       order
    '''

	 
    with_statement = ''
    select_statement = selConstructor(kwargs)
    from_statement = fromConstructor(kwargs)
    join_statement = ''
    where_statement = whereConstructor(kwargs)
    group_statement = groupConstructor(kwargs)
    order_statement = orderConstructor(kwargs)
    
    '''
    with_statement
    ...
    join_statement
    ...
    '''
    return with_statement + select_statement + from_statement + join_statement + where_statement + group_statement + order_statement
  
if __name__ == '__main__':

  pepe=dict()
  clause1=dict()
  clause2=dict()

  clause1['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
  pepe['tables'] = 'paco'
  pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
  pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
  pepe['tables'] = 'paco'
  pepe['select_modifier'] = 'DISTINCT'
  clause2['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
		    ('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
		  )
  pepe['where']=((clause1,'OR',clause2),)
  #pepe['group']=('julia','claudia')
  #pepe['having']=(('campo','=','345'),)
  pepe['order']=(1,(2,'DESC'),3)
  pprint(pepe)
  #pepe['fields'] = '*'
  print(queryConstructor(**pepe))


#print(queryConstructor(**pepe))
