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
from support.util.cadenas import *
from support.util.record_functions import *

from pprint import *
from copy import deepcopy
import datetime
import support.datalayer.datemgr as datemgr

import re

CLAUSE_PARMS = ('type','ltype','rtype','table','ltable','rtable','side','warn','driver')

def _getFmtArgs(**kwargs):
    """
    Copia de kwargs la lista de parametros de formateo
    """
    salida = dict()
    for ind in CLAUSE_PARMS:
       if ind in kwargs:
         salida[ind]=kwargs[ind]
    return salida

def queryFormat(sqlstring):
    """
    Presenta la sentencia SQL formateada. Si existe sqlparse lo utiliza
    
    """
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


def queryTransStatus(sqlString):
    """
    Determinar el estado transaccional tras ejecutar los comandos en sqlString.
    Posibles salidas
         None   -> El script no modifica el estado transaccional
         Open   -> El script deja una transaccion abierta (pero puede haber ejectuado alguna intermedia
         Closed -> El script cierra la transaccion al terminar de ejecutar
    Funciona por el caracter secuencial de ejecucion de los comandos en el script
    
    TODO Posible mejora  -> distinguir en estado open si el script cierra transacciones itermedias
    """
    import sqlparse
    
    DML = ('INSERT','UPDATE','DELETE')
    DDL = ('CREATE','ALTER','DROP')
    ACTIVE = DML + DDL
    TC  = ('COMMIT','ROLLBACK')
    status = None
    for statement in sqlparse.parse(sqlString):
        if statement.get_type() in ACTIVE:
            status = 'Open'
        elif statement.get_type() in TC:
            status = 'Closed'
    return status    

def changeTable(string,oldName,newName):
    """
    
    from cubeTree. Parece que es el que funciona, para patterns      
    Winner por aclamacion
    
    """
    pattern = r'(^|[^A-Za-z0-9_\.])('+oldName.replace('.',r'\.') + ')(\W|\.|$)'
    fileRepl   = r'\1'+ newName + r'\3'
    result = re.sub(pattern,fileRepl,string)
    return result    

def setPrefix(pbuffer,oldName,newName,excludeDict=[],excludeList=[]):
    """
        siempre sobre copias 
    """
    try:
        if isinstance(pbuffer,str):
            buffer = pbuffer
            if '.' in oldName:
                step = changeTable(buffer,oldName,newName)
                pureFile = oldName.split('.')[-1]
                return changeTable(step,pureFile,newName)
            else:
                return changeTable(buffer,oldName,newName)
        elif isinstance(pbuffer,(list,tuple,set)):  #es por completitud, como son inmutables los segundos ...
            if isinstance(pbuffer,tuple):  
                buffer = list(pbuffer)
            else:
                buffer = pbuffer[:]
            for k in range(len(buffer)):
                if k in excludeList:
                    continue
                buffer[k] = setPrefix(buffer[k],oldName,newName,excludeDict,excludeList)
            return buffer
        elif isinstance(pbuffer,dict):
            buffer = pbuffer.copy()  #FIXME valdra con esto ¿?
            for k in buffer:
                if k in excludeDict:
                    continue
                buffer[k] = setPrefix(buffer[k],oldName,newName,excludeDict,excludeList)
            return buffer
        else:
            return pbuffer
    except Exception as e:
        print(e)
        print(buffer)
        exit()
        
def normConcat(db,entry,sep=','):
    """
    Useful tric
    """
    from support.datalayer.access_layer import SQLConcat
    
    array = norm2List(entry)
    return [SQLConcat(db,array,sep),]
    #return [ [SQLConcat(db,array,sep),]]
def replTablePrefix(string,oldName,newName):
    return changeTable(string,oldName,newName)
    #import re
    #matchpattern=r'(\W*\w*\.)?('+oldName+')'
    #filematch = matchpattern+'\W'
    #fieldmatch=matchpattern+r'(\..*)'
    #fieldrepl = r'\1' + newName +r'\3'
    #string = re.sub(fieldmatch,fieldrepl,string)
    #return string

def _sqlFmt(parametro,**kwargs):
    """Devuelve, de una entrada (parametro) la salida en un formato compatible con sqlClause
      acepta uno de la lista siguiente de parametros.
      
      Sin parametros devuelve formateado para texto (entrecomillado simple o doble si contiene comillas simples) o numero,
            dependiendo del contenido de parametro
      
      los precedidos con l y r son de sqlClause para definir el formato del lado izquierdo y derecho de la expresion.
      Tienen prioridad sobre un type
      type
      ltype | rtype
            definen el tipo de elemento (ver sqlClause). type es el especifico (ltype y rtype vienen de Clause)
            r referencia (campo). el defecto en la izquierda
            q subquery
            t texto o similar.    el defecto en la derecha
            n numerico o similar
            f fecha o similar (no de momento se asume que es texto      
      table
      ltable  | rtable 
           la tabla (prefijo) que hemos de colocar en los campos referencia (ltable y rtable de Clause)
      
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
       table=kwargs.get('rtable',table)
    
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
    
def setDateFilterCore(filtros):
    '''
    TODO doc API change
    convierte la clausula date filter en codigo que puede utilizarse como una clausula where. 
    Este componente acepta los fitros como algo externo, de modo que pueda ser utilizado en varias instancias dentro de las aplicaciones
    Retorna una tupla de condiciones campo BETWEEN x e y, con un indicador de formato apropiado (fecha/fechahora(
    
    '''
    from support.util.fechas import dateRange
    
    sqlClause = []
    if not filtros:
        return sqlClause
    if len(filtros) == 0 :
        return sqlClause
    for item in  filtros :
        clase_intervalo = item['date class']
        tipo_intervalo = item['date range']
        periodos = int(item['date period'])
        if isinstance(item['elem'],(list,tuple)):
            campo = item['elem'][0] #no debe haber mas
        else:
            campo = item['elem']
        if clase_intervalo == 0:
            continue
        if item['date class']:
                intervalo = dateRange(clase_intervalo,tipo_intervalo,periodo=periodos,fmt=item.get('date format'))
                sqlClause.append((campo,'BETWEEN',intervalo,'f'))
    return sqlClause
    
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
    """
    Crea la cadena para el SELECT
    
    kwargs utilizados
    *   'fields':[] 
    *   'select modifier':  DISTINCT|FIRST
    
    """
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

def tableNameSolver(tableName,prefix=None):
    def _locateLastAs(string):
        #vamos a ver si lleva un as incorporado
        pos = string.lower().find(' as ')
        mcampo = string.lower()
        while pos > 0:
            mcampo = mcampo[pos+4:]
            pos = mcampo.lower().find(' as ')
        if mcampo != string.lower():
            return string.lower().replace(' as '+mcampo,'').strip(),mcampo.strip()
        else:
            return string.strip(),''

    elemento,label =slicer(tableName)
    # pero la entrada puede tener tambien la etiqueta incorporada en la definicion de la tabla.
    # por cierto tiene prioridad sobre el valor en la tupla
    ktexto,iadfijo = _locateLastAs(elemento)
    if iadfijo != '':
        label = iadfijo 
    return ktexto,label
    

    
def _fromConstructor(**kwargs):
    """
    Crea la cadena para el FROM
    Retorna la cadena Y un diccionario con los sinomimos de las tablas involucradas
    si el fichero es una subquery se exige que vaya entre parentesis y tenga una clausula AS o equivalente programatico
    kwargs utilizados
    *   'tables':[ [table name or def,(label)]
                    ]
    
    
    ejemplos
    ```
     pepe = {}
    for definicion in ( 'periquin',
                                'periquin as torero',
                                 ('periquin',),
                                 (('periquin','manolin'),),
                                 ('periquin','manolin'),
                                (('periquin','uno'),('manolin','dos')),
                                'select fugde,pudge from record as tupi',  <== la coma requiere estar rodeada de parentesis o cruje
                                '(select fugde,pudge from record) as tupi',
                                '(select fugde,pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi)', <== error
                                (('(select fugde,pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi)','tupi'),)
                                ):
        pepe['tables'] = definicion
        print(queryConstructor(**pepe))  
    ```
    Resultado
    ```
     SELECT *  FROM periquin     
    SELECT *  FROM periquin AS torero     
    SELECT *  FROM periquin     
    SELECT *  FROM periquin AS manolin     
    SELECT *  FROM periquin AS tt0, manolin AS tt1     
    SELECT *  FROM periquin AS uno, manolin AS dos     
    SELECT *  FROM select fugde AS tt0, pudge from record AS tupi      <== error
    SELECT *  FROM (select fugde,pudge from record) AS tupi     
    SELECT *  FROM (select fugde AS tt0, pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi) AS tt1  <== errir    
    SELECT *  FROM (select fugde,pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi) AS tupi     
    
    y el dic de sinomimos queda
    
    
    {'periquin': 'periquin'}
    {'periquin': 'torero'}
    {'periquin': 'periquin'}
    {'periquin': 'manolin'}
    {'periquin': 't0', 'manolin': 't1'}
    {'periquin': 'uno', 'manolin': 'dos'}
    {'select fugde': 't0', 'pudge from record': 'tupi'} <== errir
    {'(select fugde,pudge from record)': 'tupi'}
    {'(select fugde': 't0', 'pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi)': 't1'}
    {'(select fugde,pudge from (select fugde,pudge,rufi) from satki where tupsi = turvi)': 'tupi'}
    ```
    """
    #def _locateLastAs(string):
        ##vamos a ver si lleva un as incorporado
        #pos = string.lower().find(' as ')
        #mcampo = string.lower()
        #while pos > 0:
            #mcampo = mcampo[pos+4:]
            #pos = mcampo.lower().find(' as ')
        #if mcampo != string:
            #return string.lower().replace(' as '+mcampo,'').strip(),mcampo.strip()
        #else:
            #return string.strip(),''
        
    statement = 'FROM '
    definicion = 'tables'
    if definicion not in kwargs:
       return ''
    entrada= norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''

   # ind = 0
    texto = []
    synonyms = {}
    for ind,kelem in enumerate(entrada):
        if num_elem > 1:
            label = 't{}'.format(ind)
        else:
            label = None
        ktexto,label = tableNameSolver(kelem,label)
        if label:
            synonyms[ktexto] = label
            ftexto = '{} AS {}'.format(ktexto,label)
        else:
            synonyms[ktexto] = ktexto
            ftexto = ktexto

        texto.append(ftexto)

    statement += ', '.join(texto)
    return statement,synonyms
    
def _whereConstructor(kwargs):
    """
    Crea la cadena para el WHERE
    
    kwargs utilizados
    *   'where':[]
    *   'base_filter: []
    
    """    
    statement = 'WHERE '
    definicion = 'where'
    complemento = 'base_filter'
    
    if definicion not in kwargs:
       kstatement = ''
    else:
       kstatement = searchConstructor(definicion,**kwargs)
     
    if complemento in kwargs:
       if kstatement == '':
          kstatement = kwargs[complemento]
       elif len(kwargs[complemento].strip()) == 0:
         pass
       else:
         kstatement = '({}) AND ({}) '.format(kwargs[complemento],kstatement)
         
    if kstatement.strip() == '':
      return ''
    else:
      return statement + ' ' + kstatement + ' '
      
def _withConstructor(**kwargs):
    """
    Crea la cadena para el WITH
    
    kwargs utilizados
    *   'with':[ {'query': definicion de cualquier otra query completa,
                    'name':  nombre de la clausula
                    }
                  ]
    
    """
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
        texto.append('{} AS {}'.format(elemento['name'],queryConstructor(**args)))
        
    statement += ', '.join(texto)
 
def _groupConstructor(**kwargs):
    """
    Crea la cadena para el group
    
    kwargs utilizados
    *   'group':[] 
    *   'having'
    
    """
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
            having_clause = searchConstructor('having',**kwargs)
            if having_clause.strip() != '':
                statement += 'HAVING {}'.format(having_clause)
       return statement
    else:
       return ''

def _orderConstructor(**kwargs):
    """
    Crea la cadena para el ORDER
    
    kwargs utilizados
    *   'order':[] 
    
    """
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
    
def searchConstructor(definicion,**kwargs):
    """
    Crea una cadena compatible con sintaxis de busqueda 
    
    kwargs utilizados
    *   definicion: []  'where',join_clause','having'. Indicac donde en los argumentos esta la definicion
    
    Sample code
    
    """
    statement = ''
    if definicion not in kwargs:
       return ''    
    
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''
  
    texto = []
    
    for ind,clausula in enumerate(entrada):
        ltype=None
        rtype=None
        izquierda,comparador,derecha,fmt=slicer(clausula,4,None)   
        gargs=_getFmtArgs(**kwargs)
        
        if fmt:
            gargs['rtype']=fmt

        if isinstance(izquierda,dict):
            leftString='({})'.format(searchConstructor(definicion,**izquierda))
            gargs['ltype']='q'
        else:
            leftString = izquierda
            
        if isinstance(derecha,dict):
            rightString='({})'.format(searchConstructor(definicion,**derecha)) 
            gargs['rtype']='q'  
        else:
            rightString = derecha
            
        texto.append(_sqlClause(leftString,comparador,rightString,**gargs))
    statement = ' AND '.join(texto)
    return statement
  
def _joinConstructor(**kwargs):
    """
    Crea la cadena para el JOIN
    
    kwargs utilizados
    *   'join': list of dict:
        * join_clause: list of list
            * rel_elem
            * connector, default '='
            * base_elem
        * join_modifier
        * join_filter
        * (table o ltable) y rtable (opt)
       
    El uso de los parametros tabla necesita una explicación.
    Por defecto deberia utilizarse el par 
    __ltable__ y __rtable__, para identificar la tabla que corresponde a la parte izquierda y derecha de la clausula.
    __ltable__ es obligatorio.
    Si __rtable__ no se especifica, el sistema busca el __ltable__ de la sentencia join inmediatamente anterior; y si no existe
    el de la tabla de la clausula FROM.  Si esta tuviera mas de una tabla, fallaría por no poder determinarlo
    
    __table__ debe entenderse como un sinónimo de __ltable__
    
    Que usar depende mucho del problema.
    
    requiere para resolver la clause searchConstructor('join_clause',...)
    
    ## Sample Use(de core.py)
    ```
        pepe = {'tables':'rental'}
    hugo = {'tables':'rental'}
    pepe['join'] = [{'join_clause': [('inventory_id','=','inventory_id')],
                             'table': 'inventory',
                             'join_filter': '','join_modifier': 'LEFT',}]

    hugo['join'] = [{'join_clause': [('inventory_id','=','inventory_id')],
                                    'rtable':'avionics','ltable': 'inventory',
                                    'join_filter': '','join_modifier': 'LEFT'},
                            {'join_clause': [('film_id', '=', 'film_id')],
                                    'ltable': 'film',
                                    'join_filter': '','join_modifier': 'LEFT'}
    ```
    que dan
    ``` 
        SELECT *FROM rental
            LEFT JOIN inventory ON inventory.inventory_id = rental.inventory_id

        SELECT * FROM rental
            LEFT JOIN inventory ON inventory.inventory_id = avionics.inventory_id
            LEFT JOIN film ON film.film_id = inventory.film_id
    ```
    """    
    definicion = 'join'
    if definicion not in kwargs:
        return ''
    if kwargs[definicion] is None:
        return ''
    entrada=norm2List(kwargs[definicion])
    num_elem = len(entrada)    
    if num_elem == 0:
        return ''
    statement = ''
    ind = 0
    texto = []
    optCache = [] #para optimizar
    for idx,elemento in enumerate(entrada):
        """
        tenemos que definir una serie de defectos para que solo falle en un numero limitado de veces
        """
        if not elemento.get('ltable'): 
            elemento['ltable'] = elemento.get('table')
        if not elemento.get('rtable'):
            #voy a asumir un defecto minimo (ltable anterior o en su defecto tables general si solo hay una)
            if idx > 0:
                rtable = entrada[idx -1].get('ltable',entrada[idx -1].get('table',''))
            else:
                if len(kwargs['labels']) > 1:
                    raise ValueError('Datos insuficientes para construir un join. utilice clausula rtable')
                else:
                    for clave in kwargs['labels'] :  #un poco absiurdo el for, per la otra alternativa era keys() ... con for
                        rtable = kwargs['labels'][clave]
            elemento['rtable'] = rtable
        left,llabel = tableNameSolver(elemento['ltable'],'l{}'.format(idx))
        right,rlabel = tableNameSolver(elemento['rtable'])
        elemento['ltable'] = left #kwargs['labels'][left]
        elemento['rtable'] = right #kwargs['labels'][right]
        prefijo = elemento.get('join_modifier','')
        if 'join_clause' in elemento:
            join_clause = mergeStrings('AND',
                                    searchConstructor('join_clause',**elemento,rtype='r'), #,ltable=ltable,rtable=rtable),
                                    elemento.get('join_filter'),
                                    spaced=True)

            optCache.append([prefijo,left,llabel,join_clause,right,None])
        if elemento.get('opt_clause'):
            optCache.append([prefijo,left,llabel,elemento.get('opt_clause'),right,None])

        
    #optimizacion. Veo que entradas son identicas y las acumulo
    # corner case -> uno de los "cortados" tiene sufijo explicito. No lo elimino
    for j in range(len(optCache)):
        if optCache[j][5] is not None:  #ya ha sido procesado y asimilado
                continue
        for k in range(j +1,len(optCache)):
            if optCache[k][5] is not None:
                continue
            iguales = True
            if optCache[k][2] != '': #excluyo los que tienen prefijo predefinido
                iguales = False
            else:
                for l in (0,1,3,4):
                    if optCache[j][l] != optCache[k][l]:
                        iguales = False
                        break
            if iguales:
                optCache[k][5] = j
                #optCache[k][2] = optCache[j][2]
    # pongo etiquetas y modifico lo que haya que modificar. Tengo que procesarlas todas porque necesito
    # etiquetas para los rfiles
    for j in range(len(optCache)):
        # Pongo las etiquetas en las lineas
        if optCache[j][2]:
            pass
        elif optCache[j][5] is not None:
            opfx = optCache[optCache[j][5]][2]
            optCache[j][2] = opfx
        elif optCache[j][2] == '':
            optCache[j][2] = 'l{}'.format(j)
            
        #cambio los prefijos de los campos en la clausula generada
        #. Primero referentes a ltable
        clausula = optCache[j][3]
        clausula = replTablePrefix(clausula.lower(),optCache[j][1].lower(),optCache[j][2])
        # cambio los prefijos referentes a rtable
        if j > 0 and optCache[j][4] == optCache[j -1][1]:
            if optCache[j -1][5] is not None:
                pfix = optCache[optCache[j -1][5]][2]
            else:
                pfix = optCache[j -1][2]
            clausula = replTablePrefix(clausula.lower(),optCache[j][4].lower(),pfix)
        optCache[j][3] = clausula
        
    for itm in optCache:
        if itm[5] is not None:  #ya ha sido procesado y asimilado
            continue
        texto.append('{0[0]} JOIN {0[1]} AS {0[2]} ON {0[3]}'.format(itm,clausula))
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
       
    el devolver un parm adicional en el from y luego incluirlo en kwargs es porque parece que los parametros ** se pasan por "valor" (lo que se pasan son los individuales
    '''
    kwargs['labels'] = None
    with_statement = _withConstructor(**kwargs)+' '
    
    from_statement,from_synonyms = _fromConstructor(**kwargs) 
    from_statement += ' '
    kwargs['labels']=from_synonyms #anyado los sinonimos que genere en el from
    
    join_statement = _joinConstructor(**kwargs)+' '

    select_statement = _selConstructor(**kwargs)+' '
    
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
  h1 = 'pepe'
  h2 = 'paco'
  print('{} {} {}'.format(h1,'y',h2))
  #print(queryConstructor(**pepe))


#print(queryConstructor(**pepe))
