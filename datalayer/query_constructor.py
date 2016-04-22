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
from util.record_functions import *
from pprint import *



def sqlFmt(parametro,**kwargs):
    """
      Devuelve, de una entrada (parametro) la salida en un formato compatible con sqlClause
      acepta uno de la lista siguiente de parametros.
      
      Sin parametros devuelve formateado para texto (entrecomillado simple o doble si contiene comillas simples) o numero,
            dependiendo del contenido de parametro
      
      los precedidos con l y r son de sqlClause para definir el formato del lado izquierdo y derecho de la expresion.
      Tienen prioridad sobre un type
      type
      ltype
      rtype  definen el tipo de elemento (ver sqlClause). type es el especifico (ltype y rtype vienen de Clause)
            r referencia (campo). el defecto en la izquierda
            q subquery
            t texto o similar.    el defecto en la derecha
            n numerico o similar
            f fecha o similar (no de momento se asume que es texto      
      table
      ltable
      rtable la tabla (prefijo) que hemos de colocar en los campos referencia (ltable y rtable de Clause)
      
      side es para indicar si es lado izquierdo (l) o derecho (r) . Implica un cambio en los defectos.
        izquierdo devuelve por defecto referencia (nombre de campo o parametro dinámico)
        derecho el formato natural del contenido del parametro
        
      warn=True devuelve, ademas del valor un booleano que es verdadero si el resultado es fijo texto o numero, no variable
      
      Casos de prueba:
      
        print(sqlFmt('paco'))
        print(sqlFmt('paco',type='r'))
        print(sqlFmt('paco',type='t'))
        print(sqlFmt('paco',type='n'))
        print(sqlFmt('paco',side='l'))
        print(sqlFmt('paco',side='r'))
        print(sqlFmt('paco',side='r',type='r',rtype=None))
        print(sqlFmt(5))
        # print(sqlFmt(5,side='l')) falla como si pidiera un texto
        print(sqlFmt(5,side='r'))
        #print(sqlFmt(paco))

    
    """
    warntype=False
    type = ex(kwargs,'type')
    table = ex(kwargs,'table')
    lado = ex(kwargs,'side','')
    warn=ex(kwargs,'warn')
    
    # determinar el tipo correcto es un poco complicado
    if lado.upper() == 'L':
       type=ex(kwargs,'ltype',type)
       if not type:
           type = 'r'           
       table=ex(kwargs,'ltable',table)
           
    elif lado.upper() == 'R':
       type=ex(kwargs,'rtype',type)
       if not type:
           if isinstance(parametro,(int,float)):
               type = 'n'
           else:
               type = 't'
       table=ex(kwargs,'ltable',table)
    
    if not type and isinstance(parametro,(int,float)):
        type = 'n'
        
    if type in ('r','q'):
        resultado = parametro.strip()
    elif type == 'n' :
        warntype=True
        resultado = '{}'.format(parametro).strip()
    else:
        warntype=True
        if isinstance(parametro,(int,float)):
            resultado="'{}'".format(parametro).strip()
        elif  parametro.find("'") < 0 :
            resultado = "'{}'".format(parametro.strip())
        else:
            resultado = '"{}"'.format(parametro.strip())
        
    # prefijo si me viene indicado para campos, claro    
    if table is not None and  type == 'r':
        resultado = '{}.{}'.format(table,resultado)

    if warn == True:    
        return resultado,warntype
    else:
        return resultado
    
def sqlClause(left,comparator,right=None,twarn=True,**kwargs):
    """
       Crea un operación logica con dos entradas (izquierda y derecha) con un operador de comparación
       
       kwargs procesados: (el resto pasa a sqlFmt)
       ltype tipo de formato  del elemento de la izquierda
       rtype tipo de formato  del elemento de la derecha
            r referencia (campo). el defecto en la izquierda
            q subquery
            t texto o similar.    el defecto en la derecha
            n numerico o similar
            f fecha o similar (no de momento se asume que es texto
       ltable
       rtable 
       twarn=True
          Si ambos lados de la expresion no contienen variables, devuelve None
          
       casos de prueba   

        print(sqlClause('pepe','=','hugo',ltable='adam'))
        print(sqlClause('pepe','is null'))
        print(sqlClause('pepe','is not null'))
        #print(clause('pepe','='))
        print(sqlClause("paco", '=' , "pepe's bar"))
        print(sqlClause("paco", 'IN' , (1,7,3,2,5,),ltype='t'))
        print(sqlClause("paco", 'BETWEEN' , (1,71,3,150,5)))
        print(sqlClause("paco", 'BETWEEN' , (1,71,3,150,5),rtype='t'))


    """
    # ajusto el formato de la parte izquierda
    # flags para evitar expresiones valor comp valor
    lwarntype=False
    rwarntype=False
    operador = comparator.upper().strip()
    # argumento izquierda
    izquierda,lwarntype = sqlFmt(left,side='L',warn=True,**kwargs)
    
    # checkeo el caso raro del IS (NOT) (NULL/TRUE/FALSE) (realmente no es un operador, sino operador y valor)
    if right is None:
       if 'IS' in operador :
         return '{} {}'.format(izquierda,operador ) # la clausula is null es como es
       else:
         print('El operador >{}< necesita un argumento derecha'.format(operador))   
         return None
    # si la parte derecha es una lista solo vale para 'BETWEEN' y 'IN'
    if isinstance(right,(list,tuple)):
        # oracle admite una sintaxis (lista) = set pero mejor no plantearla
        #
        if operador not in ('IN','NOT IN','BETWEEN','NOT BETWEEN'):
            print('El operador >{}< no admite listas de valores'.format(operador))
            return None
        if len(right) > 2 and operador in ('BETWEEN','NOT BETWEEN'):
            print('El operador >BETWEEN< necesita 2 valores sólo. Usando el 1 y último de la lista')
        rwarntype=True
        listaD = [sqlFmt(entry,side='R',**kwargs) for entry in right ]
        if operador in ('IN','NOT IN'):
            derecha = ",".join(listaD)
            return '{} {} ({})'.format(izquierda,operador,derecha)
        elif operador in ('BETWEEN','NOT BETWEEN'):
            return '{} {} {} AND {}'.format(izquierda,operador,listaD[0],listaD[-1])    
        return
        
    else:
        derecha,rwarntype = sqlFmt(right,side='R',warn=True,**kwargs)
    
    if twarn and lwarntype and rwarntype:
        print('Ambos lados son valores, no variables. Abortando')
        return None
        #exit()
    
    return '{} {} {}'.format(izquierda,comparator,derecha)

def sqlCase(datos=None,**kwargs):
    """
       Crea una sentencia case de la definicion lista_guias[i]
       Para categorias definidas a mano
    """
    pprint(datos)
    entrada =  datos
    enum = entrada['enum']
    elem = entrada['elem'][0]
    name = entrada['name']
    
    default = ''
    selector = ''
    # para los resultados
    table=ex(kwargs,'table')
    fmt_res=ex(entrada,'fmt','t')
    fmt_val=ex(entrada,'enum_fmt')
    # aqui creo la sentencia
    casetree=[]
    for entry in enum:

        if 'default' in entry:
            default=sqlFmt(entry['default'],type=fmt_res)
            continue
        
        condicion = sqlClause(elem,entry['condition'],entry['values'],rtype=fmt_val,twarn=False,ltable=table)
        casetree.append('{} THEN {}'.format(condicion,sqlFmt(entry['result'],type=fmt_res)))
    selector = ' WHEN '.join(casetree)
    #pprint(kwargs)
    if default != '':
       default = 'ELSE {}'.format(default) 
    clausula = 'CASE WHEN {} {} END AS {}'.format(selector,default,name)
    return clausula

def selConstructor(kwargs):
    statement = 'SELECT '
    definicion = 'fields'
    if definicion not in kwargs:
       return 'SELECT * '
    
    if 'select_modifier' in kwargs:
       modifier = kwargs['select_modifier'].strip().upper()
       if modifier in ('DISTINCT','FIRST'):
            statement += modifier + ' '
            
    if isinstance(kwargs[definicion],(list,tuple)):
        entrada = kwargs[definicion]
    else:
        entrada = [kwargs[definicion],]
    #if isinstance(kwargs[definicion],str):
      #entrada = [kwargs[definicion],]
    #else:
      #entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      
      elemento,adfijo=slicer(kelem)
      #if elemento.strip().find(' ') == -1:
      texto = elemento.strip()
      #else:
        #texto = '({})'.format(elemento)

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
    
    if isinstance(kwargs[definicion],(list,tuple)):
        entrada = kwargs[definicion]
    else:
        entrada = [kwargs[definicion],]
    #if isinstance(kwargs[definicion],str):
        #entrada = [kwargs[definicion],]
    #else:
        #entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      #if elemento.strip().find(' ') == -1:
      texto = elemento.strip()
      #else:
        #texto = '({})'.format(elemento)

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
          kstatement = kwargs[complemento]
       elif len(kwargs[complemento].strip()) == 0:
         pass
       else:
         kstatement = '({}) AND ({}) '.format(kwargs[complemento],kstatement)
         
    if kstatement == '':
      return ''
    else:
      return statement + ' ' + kstatement + ' '
      
       
def groupConstructor(kwargs):
    statement = 'GROUP BY '
    definicion = 'group'
    
    if definicion not in kwargs:
       return ''
    
    if isinstance(kwargs[definicion],(list,tuple)):
        entrada = kwargs[definicion]
    else:
        entrada = [kwargs[definicion],]
    #if isinstance(kwargs[definicion],str):
        #entrada = [kwargs[definicion],]
    #else:
        #entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for elemento in entrada:
      #if elemento.strip().find(' ') == -1:
      texto = elemento.strip()
      #else:
        #texto = '({})'.format(elemento)
            
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
    
    if isinstance(kwargs[definicion],(list,tuple)):
        entrada = kwargs[definicion]
    else:
        entrada = [kwargs[definicion],]
    #if isinstance(kwargs[definicion],str):
        #entrada = [kwargs[definicion],]
    #else:
        #entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      if isinstance(elemento,int):
        texto = '{}'.format(elemento)
      #elif elemento.strip().find(' ') == -1:
      texto = elemento.strip()
      #else:
        #texto = '({})'.format(elemento)

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
    if isinstance(kwargs[definicion],(list,tuple)):
        entrada = kwargs[definicion]
    else:
        entrada = [kwargs[definicion],]
    #if isinstance(kwargs[definicion],str):
        #entrada = [kwargs[definicion],]
    #else:
        #entrada = kwargs[definicion]
      
    ind = 0
    num_elem = len(entrada)
    #print(num_elem,entrada)
        
    for kelem in entrada:
      elemento,adfijo,parms=slicer(kelem,3)   
      #if elemento.strip().find(' ') == -1:
      texto = elemento.strip()
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
  pepe['fields']=(""" case 
        when partido in (3316,4688) then '1 derecha'
    when partido in (1079,4475) then '2 centro'
        when partido in (3484) then '3 izquierda'
    when partido in (3736,5033,4850,5008,5041,2744,5026) then '4 extrema'
        when partido in (5063,4991,1528) then '5 separatistas'
        when partido in (1533,4744,4223) then '6 nacionalistas'
    else
         'otros'
    end as categoria""" ,'partido',('seats','sum'))
  pepe['tables']='votos_provincia'
  pepe['group']=('categoria',)
  """
  pepe['where']=(('campo','in','galba','oton','vitelio','vespasiano'),)
  pepe['tables'] = 'paco'
  #pepe['tables'] = ('cesar',('augusto','octavio'),'select * from table2')
  pepe['fields'] = ('cayo','tiberio magno',('caligula',),('octavio.claudio',),('Neron','sum'),('galba','avg'))
  #pepe['tables'] = 'paco'
  #pepe['select_modifier'] = 'DISTINCT'
  clause2['where'] = ( ('cayo','=',"'caligula'"),('neron','ne',"'domicio'"),('avg(galba)','!=','sum(neron)'),
		    ('miselect','is null'),('','EXISTS','(select paco from hugo where none)')
		  )
  #pepe['where']=((clause1,'OR',clause2),)
  #pepe['group']=('julia','claudia')
  #pepe['having']=(('campo','=','345'),)
  pepe['base_filter']=''
  pepe['order']=(1,(2,'DESC'),3)
  pprint(pepe)
  #pepe['fields'] = '*'
  """
  print(queryConstructor(**pepe))


#print(queryConstructor(**pepe))
