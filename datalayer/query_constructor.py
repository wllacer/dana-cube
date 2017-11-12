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
from copy import deepcopy
import datetime
import datalayer.datemgr as datemgr

CLAUSE_PARMS = ('type','ltype','rtype','table','ltable','rtable','side','warn','driver')

def _getFmtArgs(**kwargs):
    salida = dict()
    for ind in CLAUSE_PARMS:
       if ind in kwargs:
         salida[ind]=kwargs[ind]
    return salida

def queryFormat(sqlstring):
    try:
        import sqlparse
        return sqlparse.format(sqlstring,reindent=True,keyword_case = 'upper',indent_width=2)+'\n\n'
    except ImportError:
        STATEMENT=('WITH','SELECT ','FROM ','WHERE ','LEFT OUTER JOIN ','GROUP BY ','ORDER BY ','WHERE ')
        cadena = sqlstring
        for entry in STATEMENT:
            salida = '\n{}\n\t'.format(entry)
            cadena = cadena.replace(entry,salida)
        cadena = cadena.replace(',',',\n\t')
        return cadena
    
def _sqlFmt(parametro,**kwargs):
    """Devuelve, de una entrada (parametro) la salida en un formato compatible con sqlClause
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
    type = kwargs.get('type')
    table = kwargs.get('table')
    lado = kwargs.get('side','')
    warn=kwargs.get('warn')
    
    # determinar el tipo correcto es un poco complicado
    if lado.upper() == 'L':
       type=kwargs.get('ltype',type)
       if not type:
           type = 'r'           
       table=kwargs.get('ltable',table)
           
    elif lado.upper() == 'R':
       type=kwargs.get('rtype',type)
       if not type:
           if isinstance(parametro,(int,float)):
               type = 'n'
           else: # cambio de politica de defecto si tiene comillas texto, si no parametro
               type = 'r'
       table=kwargs.get('ltable',table)
    
    if not type and isinstance(parametro,(int,float)):
        type = 'n'
        
    if type in ('r','q','p'):
        resultado = parametro   #.strip(). Me estaba empezando a cabrear
    elif type == 'n' :
        warntype=True
        resultado = '{}'.format(parametro).strip()
    else:
        warntype=True
        if isinstance(parametro,(int,float)):
            resultado="'{}'".format(parametro).strip()
        if isinstance(parametro,(datetime.date,datetime.time,datetime.datetime)) or type == 'f':
            resultado="'{}'".format(parametro).strip()
            if kwargs.get('driver') == 'oracle':
                resultado = datemgr.oracleDateString(parametro)
        elif  parametro.find("'") < 0 :
            resultado = "'{}'".format(parametro.strip())
        else:
            resultado = '"{}"'.format(parametro.strip())
        
    # prefijo si me viene indicado para campos, claro    
    if table is not None and  type == 'r':
        if '.' not in resultado:
            resultado = '{}.{}'.format(table,resultado)

    if warn == True:    
        return resultado,warntype
    else:
        return resultado
    
def _sqlClause(left,comparator,right=None,twarn=True,**kwargs):
    """Crea un operación logica con dos entradas (izquierda y derecha) con un operador de comparación
       
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
    #print('{} : {} :{}'.format(left,comparator,right))
    # ajusto el formato de la parte izquierda
    # flags para evitar expresiones valor comp valor
    lwarntype=False
    rwarntype=False
    operador = comparator.upper().strip()
    # argumento izquierda
    izquierda,lwarntype = _sqlFmt(left,side='L',warn=True,**kwargs)
    

    # y el mas raro todavia del EXISTS
    if izquierda.strip() == '':
        if 'EXISTS' in operador:
            return '{} {}'.format(operador,_sqlFmt(right,type='q') )
        else:
            print('El operador >{}< necesita un argumento izquierda'.format(operador))   
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
        listaD = [_sqlFmt(entry,side='R',**kwargs) for entry in right ]
        if operador in ('IN','NOT IN'):
            derecha = ",".join(listaD)
            return '{} {} ({})'.format(izquierda,operador,derecha)
        elif operador in ('BETWEEN','NOT BETWEEN'):
            return '{} {} {} AND {}'.format(izquierda,operador,listaD[0],listaD[-1])    
        return
        
    else:
        if right is None:
            if 'IS' in operador :
                return '{} {}'.format(izquierda,operador ) # la clausula is null es como es
            else:
                print('El operador >{}< necesita un argumento derecha'.format(operador))   
                return None

        derecha,rwarntype = _sqlFmt(right,side='R',warn=True,**kwargs)
        #1610 print(derecha)
        # checkeo el caso raro del IS (NOT) (NULL/TRUE/FALSE) (realmente no es un operador, sino operador y valor)
    
    if twarn and lwarntype and rwarntype:
        print('Ambos lados son valores, no variables. Abortando')
        return None
        #exit()
    
    return '{} {} {}'.format(izquierda,comparator,derecha)

def caseConstructor(name,datos=None,**kwargs):
    """
       Crea una sentencia case de la definicion guias[i][prod][j]
       Para categorias definidas a mano
       
       Caso ejemplo
       
       datos = {u'class': u'c',u'elem': [u'partido'],u'name': u'ideologia',
               u'rules': [
                         {u'class': u'c',u'elem': [u'partido',u'name': u'ideologia',u'ncode': 1,u'ndesc': 0,u'string': u''
                        u'enum': [
                                 {u'default': u'otros'},
                                 {u'condition': u'in',u'result': u'Derecha',u'values': [3316, 4688]},
                                 {u'condition': u'in',u'result': u'Centro',u'values': [1079, 4475]},
                                 {u'condition': u'in',u'result': u'Izquierda',u'values': [3484]},
                                 {u'condition': u'in',u'result': u'Extrema Izquierda',
                                    u'values': [3736,5033,4850,5008,5041,2744,5026]},
                                 {u'condition': u'in',u'result': u'Separatistas',u'values': [5063, 4991, 1528]},
                                 {u'condition': u'in',u'result': u'Nacionalistas',u'values': [1533, 4744, 4223]}
                                 ],
                        }
                        ]
                }
    sqlCase(datos,table='votos_provincia')

    """
    # pequeña rutina de traduccion necesaria para el nombre de los formatos
    fmtTrans = {'txt':'t','t':'t','num':'n','n':'n','date':'f','d':'f'}
    #pprint(datos)
    entrada =  datos
    enum = entrada['categories']
    elem = norm2List(entrada['elem'])[0]
    #name = entrada['name']
    
    default = ''
    selector = ''
    # para los resultados
    table=kwargs.get('table')
    fmt_res=fmtTrans[entrada.get('fmt','txt')]
    fmt_val=fmtTrans[entrada.get('enum_fmt','txt')]
    # aqui creo la sentencia
    casetree=[]
    for entry in enum:

        if 'default' in entry:
            default=_sqlFmt(entry['default'],type=fmt_res)
            continue
        
        condicion = _sqlClause(elem,entry['condition'],entry['values'],rtype=fmt_val,twarn=False,ltable=table)
        casetree.append('{} THEN {}'.format(condicion,_sqlFmt(entry['result'],type=fmt_res)))
    selector = ' WHEN '.join(casetree)
    #pprint(kwargs)
    if default != '':
       default = 'ELSE {}'.format(default) 
    clausula = 'CASE WHEN {} {} END AS {}'.format(selector,default,name)
    return clausula

def _selConstructor(**kwargs):
    statement = 'SELECT '
    definicion = 'fields'
    if definicion not in kwargs:
       return 'SELECT * '
    
    if 'select_modifier' in kwargs:
       modifier = kwargs['select_modifier'].strip().upper()
       if modifier in ('DISTINCT','FIRST'):
            statement += modifier + ' '
            
    entrada=norm2List(kwargs[definicion])
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

def _fromConstructor(**kwargs):
    statement = 'FROM '
    definicion = 'tables'
    if definicion not in kwargs:
       return ''
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''

    ind = 0
    texto = []
    
    for ind,kelem in enumerate(entrada):
        elemento,adfijo=slicer(kelem)
      
        ktexto = elemento.strip()

        if adfijo != '':
            ktexto = '{} as {}'.format(texto,adfijo.strip())
        elif num_elem > 1:
            ktexto = '{} as t{}'.format(texto,ind)
            
        texto.append(ktexto)
    statement += ', '.join(texto)
    return statement
    
def _whereConstructor(kwargs):
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
      
def _withConstructor(**kwargs):
    statement = 'WITH '
    definicion = 'with'
    if definicion not in kwargs:
        return ''
   
    entrada=norm2List(kwargs[definicion])

    ind = 0
    num_elem = len(entrada)
    texto = []
    for elemento in entrada:
        args=deepcopy(elemento['query'])
        
        texto.append('{} as {}'.format(elemento['name'],queryConstructor(**args)))
        
    statement += ', '.join(texto)
 
def _groupConstructor(**kwargs):
    statement = 'GROUP BY '
    definicion = 'group'
 
 
    if definicion not in kwargs:
       return ''
    
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''
    
    ind = 0
    texto = []
    for elemento in entrada:
      # en el caso de las categorias se pasa el AS al group y eso no funciona y hay que quitarlo GENERADOR
      #FIXME no entiendo porque necesito renormalizar la cadena
      nelemento = norm2String(elemento)  
      pos = nelemento.upper().find(' AS ')
      if pos > 0:
          kelemento = nelemento[0:pos]
      else:
        kelemento = nelemento
      #1610 print(kelemento)
      texto.append(kelemento.strip())
    
    statement += ', '.join(texto)
    
    if statement.strip() != 'GROUP BY':
       if 'having' in kwargs:
            having_clause = searchConstructor('having',kwargs)
            if having_clause.strip() != '':
                statement += 'HAVING {}'.format(having_clause)
       return statement
    else:
       return ''

def _orderConstructor(**kwargs):
    statement = 'ORDER BY '
    definicion = 'order'
    if definicion not in kwargs:
       return ''
    
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)
    if num_elem == 0:
        return ''
    ind = 0

    texto = []
    for kelem in entrada:
      elemento,adfijo=slicer(kelem)
      texto.append('{} {}'.format(_sqlFmt(elemento,side='l'),adfijo.strip()))
    statement += ', '.join(texto)
    return statement
    
def searchConstructor(definicion,kwargs):
    statement = ''
    if definicion not in kwargs:
       return ''    
    
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''
  
    ind = 0
    #print(num_elem,entrada)
    texto = []
    for ind,kelem in enumerate(entrada):
        ltype=None
        rtype=None
        #izquierda,comparador,derecha=slicer(kelem,3,None)   
        izquierda,comparador,derecha,fmt=slicer(kelem,4,None)   
        gargs=_getFmtArgs(**kwargs)
        if fmt:
            gargs['rtype']=fmt

        if isinstance(izquierda,dict):
            args = deepcopy(izquierda) # no quiero efectos secundarios
            izquierda='({})'.format(searchConstructor(definicion,args))
            gargs['ltype']='q'
        if isinstance(derecha,dict):
            args = deepcopy(derecha) # no quiero efectos secundarios
            derecha='({})'.format(searchConstructor(definicion,args)) 
            gargs['rtype']='q'  
        texto.append(_sqlClause(izquierda,comparador,derecha,**gargs))
    statement = ' AND '.join(texto)
    return statement
  
def _joinConstructor(**kwargs):
    definicion = 'join'
    if definicion not in kwargs:
        return ''
    if kwargs[definicion] is None:
        return ''
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''

    #DEBUG print(kwargs[definicion],entrada)
    statement = ''
    ind = 0
    texto = []
    definicion = 'join_clause'
    for elemento in entrada:
        prefijo = elemento.get('join_modifier','')
        tabla = elemento.get('table','')
        join_filter=elemento.get('join_filter','')
        args=deepcopy(elemento)
        args['rtype']='r'
        join_clause = searchConstructor(definicion,args)
        if join_filter != '' and join_clause != '':
            join_clause = '{} AND {}'.format(join_clause,join_filter).strip()
        else:
            join_clause = '{}{}'.format(join_clause,join_filter).strip()
        texto.append('{} JOIN {} ON {}'.format(prefijo, tabla, join_clause))
        
    statement += ' '.join(texto)
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
       driver
    '''
	 
    with_statement = _withConstructor(**kwargs)+' '
    select_statement = _selConstructor(**kwargs)+' '
    from_statement = _fromConstructor(**kwargs)+' '
    join_statement = _joinConstructor(**kwargs)+' '
    where_statement = _whereConstructor(kwargs)+' '
    group_statement = _groupConstructor(**kwargs)+' '
    order_statement = _orderConstructor(**kwargs)+' '
    
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
  pepe['lfile']='sempronio'
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
