#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

'''

DEBUG = True
TRACE=True
DELIMITER=':'

from util.record_functions import *
from noqt.tree import *
from util.fechas import *

from datalayer.access_layer import *
from datalayer.query_constructor import *

from util.numeros import stats,num2text

from datalayer.datemgr import getDateEntry, getDateIndexNew
from pprint import *

import time

from util.jsonmgr import dump_structure,dump_json
try:
    import xlsxwriter
    XLSOUTPUT = True
except ImportError:
    XLSOUTPUT = False

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
#from cubemgmt.cubetree import CubeItem,traverseTree

def searchStandardItem(item,value,role):
    """
       modelo general de funcion de busqueda binaria en hijos de un QStandardItem o derivados
       como funcion generica porque se repite en varias circunstancias
       SOLO vale con children ordenados por el valor de busqueda (eso es muy importante)
    """
    lower = 0
    upper = item.rowCount()
    while lower < upper:   # use < instead of <=
        x = lower + (upper - lower) // 2
        val = item.child(x).data(role)
        if value == val:
            return item.child(x)
        elif value > val:
            if lower == x:   # this two are the actual lines
                break        # you're looking for
            lower = x
        elif value < val:
            upper = x
    return None

class GuideItemModel(QStandardItemModel):
    def __init__(self,parent=None):
        super(GuideItemModel, self).__init__(parent)

                                   
    def traverse(self,base=None):
        if base is not None:
            yield base
            queue = [ base.child(i) for i in range(0,base.rowCount()) ]
        else:
            root = self.invisibleRootItem()
            queue = [ root.child(i) for i in range(0,root.rowCount()) ]
        while queue :
            yield queue[0]
            expansion = [ queue[0].child(i) for i in range(0,queue[0].rowCount()) ]
            if expansion is None:
                del queue[0]
            else:
                queue = expansion  + queue[1:]            
       
    def searchHierarchy(self,valueList,role=None):
        """
          busco el elemento padre con toda la jerarquia de una tacada. No se con los grandes totales
        """
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        elem = self.invisibleRootItem()
        parent = self.invisibleRootItem()
        for k,value in enumerate(valueList):
            elem = searchStandardItem(parent,value,prole)
            if not elem:
                return None
            parent = elem
        return elem
    
class GuideItem(QStandardItem):
    def __init__(self,*args):  #solo usamos valor (str o standarItem)
        super(GuideItem, self).__init__(*args)
    
    
    def depth(self):
        depth = 0
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            pai = pai.parent()
            depth += 1
        return depth
    
    def getFullKey(self):
        clave = self.data(Qt.UserRole +1)
        pai = self.parent()
        while pai is not None and pai != self.model().invisibleRootItem():
            clave = pai.data(Qt.UserRole +1) + DELIMITER + clave
        return clave
        
    def searchChildren(self,value,role=None):
        if role is None:
            prole = Qt.UserRole +1
        else:
            prole = role
        return searchStandardItem(self,value,prole)

    def setColumn(self,col,value):
        row = self.index().row()
        if self.parent() is None:
            pai = self.model().invisibleRootItem()
        else:
            pai = self.parent()
        colItem = GuideItem()
        colItem.setData(value,Qt.UserRole +1)
        colItem.setData(value,Qt.DisplayRole)
        pai.setChild(row,col,colItem)

    def __str__(self):
        return "<" + self.text() + ">"

    def __repr__(self):
        return "<" + self.data(Qt.DisplayRole) + ">"
        
def mergeString(string1,string2,connector):
    if not string1 :
        merge = string2
    elif not string2:
        merge = string1
    elif len(string1.strip()) > 0 and len(string1.strip()) > 0:
        merge ='{} {} {}'.format(string1,connector,string2)
    elif len(string1.strip()) > 0 or len(string2.strip()) > 0: 
        merge ='{}{}'.format(string1,string2).strip()
    else:
        merge = ''
    return merge

def getParentKey(clave,debug=False):
    """
      define el padre de un elemento via la clave
    """
    nivel=getLevel(clave)
    if nivel > 0:
        padreKey = DELIMITER.join(clave.split(DELIMITER)[0:nivel])
        return padreKey
    else:
       return None


def getOrderedText(desc,sparse=True,separator=None):
    if desc is None:
        return None
    levels = len(desc)
    texto = ''
    for j in range(levels -1):
        if sparse:
            texto +=separator
        else:
            texto += (desc[j]+separator)
    # especial fechas. no se que efectos secundarios puede tener
    texto += desc[-1]
    return texto
        
    
          
class Cubo:
    def __init__(self, definicion,nombre=None,dbConn=None):
        """
        Inicialización del cubo 
        Parametros
        definicion -> estructura diccionario con la configuración del cubo
        nombre     -> (opcional) nombre del cubo
        dbConn     -> (opciona) puede usarse para invocarlo en situaciones en que la conexion de la BD.
                    ya esta activa. Pensado para pruebas en cubebrowse
        """
        if definicion is None :
            print('No se especifico definicion valida ')
            sys.exit(-1)
        
        # los datos siguientes son la definicion externa del cubo
        #pprint(definicion)
        self.definition = definicion
        self.nombre = nombre
        if not dbConn:
            self.db = dbConnect(self.definition['connect'])
        else:
            self.db = dbConn
        # inicializo (y cargo a continuacion) los otros atributos       
        self.lista_guias= []
        self.__setGuias()
        
        self.lista_funciones = []
        self.lista_funciones = getAgrFunctions(self.db,self.lista_funciones)
        
        self.lista_campos = []
        self.lista_campos = self.getFields()
        
        self.dbdriver = self.db.dialect.name #self.definition['connect']['driver']
        
        
        
        
        # no se usa en core. No se todavia en la parte GUI
        
        
        #self.__fillGuias()  #LLENADO GUIAS
      
    #
    def getGuideNames(self):
        """
        crea un array con los nombres de las guias
        """
        tabla = []
        for guia in self.lista_guias:
            tabla.append(guia['name'])
        return tuple(tabla)

    def getFunctions(self):
        '''
           INTERFAZ EXTERNA
           obtiene las funciones disponibls por la base de datos
        '''
        return self.lista_funciones
           
    def getFields(self):
        '''
           crea/devuelve el atributo cubo.lista_campos.
           No se espera que varia durante la vida del cubo
        '''
        if len(self.lista_campos) == 0:
            lista_campos = self.definition['fields'][:]
        else:
            lista_campos = self.lista_campos [ : ]
        return lista_campos

    def setDateFilter(self):
        '''
        convierte la clausula date filter en codigo que puede utilizarse como una clausula where 
        Retorna una tupla de condiciones campo BETWEEN x e y, con un indicador de formato apropiado (fecha/fechahora(
        '''
        sqlClause = []
        filtros = self.definition.get('date filter')
        if not filtros:
            return sqlClause
        if len(filtros) == 0 :
            return sqlClause
        for item in  filtros :
            clase_intervalo = CLASES_INTERVALO.index(item['date class'])
            tipo_intervalo = TIPOS_INTERVALO.index(item['date range'])
            periodos = int(item['date period'])
            if clase_intervalo == 0:
                continue
            if item['date class']:
                    intervalo = dateRange(clase_intervalo,tipo_intervalo,periodo=periodos,fmt=item.get('date format'))
                    sqlClause.append((item['elem'],'BETWEEN',intervalo,'f'))
        return sqlClause
    

    def __setGuias(self):
        '''
           Crea la estructura lista_guias para cada una de las guias (dimensiones) que hemos definido en el cubo.
           Proceden de las reglas de produccion (prod) de la definicion
           Es una tupla con una entrada (diccionario) por cada guia con los siguientes elementos:
           *  name   nombre con el que aparece en la interfaz de usuario (de la definicion)
           *   class    '' normal, 'd' fecha (Opcional)
           *  contexto 
           * dir_row el array indice (para realizar busquedas)
           El contexto y dir_row se crea directamente durante el fill guia
        '''
        self.lista_guias = []
        ind = 0
        #para un posible backtrace
        nombres = [ entrada['name'] for entrada in self.definition['guides'] ]
        
        for entrada in self.definition['guides']:
            guia = {'name':entrada['name'],'class':entrada['class'],'contexto':[],'elem':[]}
            self.lista_guias.append(guia)

    def fillGuias(self):
        """
           De una sola operacion generamos toda la información sobre las guias -incluidos los arboles-
           el diccionario ha sigo generado en __setGuias
           
           No se usa internamente, ya que puede consumir recursos excesivos en la inicialización del cubo.
           En otros momentos lo he activado. Lo dejo como opcion a los usuarios
        """
        for k,entrada in enumerate(self.lista_guias):
            entrada['dir_row'],entrada['contexto']=self.fillGuia(k)
    
    def _setTableName(self,guia,idx):
        """
        Para una regla de producción concreta en una guia obtiene la tabla base que corresponde para 
        el dominio de definición que deseo
        
        input
           guia  definicion de la guia correspondiente
           idx   indice de la produccion en la tupla de contextos
        output
           table_name nombre de la tabla
           filter filtro asociado
        """
        basefilter = None
        datefilter = None
        entrada = guia['prod'][idx]
        if 'domain' in entrada:
            table_name = entrada['domain'].get('table')  # se supone que tiene que existir
            basefilter = entrada['domain'].get('filter')
        elif 'link via' in entrada:
            table_name = entrada['link via'][-1].get('table')
        else:
            table_name = self.definition.get('table')
            if len(self.definition.get('base filter','')) > 0:
                basefilter = self.definition['base filter']
            if 'date filter' in self.definition:
                datefilter = self.setDateFilter()
        return table_name,basefilter,datefilter
            
   
    def _expandDateProductions(self,guidID):
        """
        las producciones tipo date son abreviaturas de jerarquias internas. Ahora es el momento de dedoblarlas
        Quedan como entradas simples en la tabla de contextos de la guia (bien marcadas como dates);
        tienen dos pequeñas peculiaridades:
        los atributos campo_base con el nombre del campo original y
        origID con el numero de la regla de producción original (para trazas)
        """
        prodExpandida = []
        guia = self.definition['guides'][guidID]
        
        for prodId,produccion in enumerate(guia['prod']):
            produccion['origID'] = prodId
            if produccion.get('class','o') == 'd' or produccion.get('fmt','txt') == 'date':
                code = norm2List(produccion.get('elem'))
                campo = code[0] #solo podemos trabajar con un campo
                # si no existe por lo que sea mask, defecto es año y mes
                mascara = produccion.get('mask','Ym')
                for kmask in [ mascara[0:k+1] for k in range(len(mascara)) ]:
                    # esta llamada me devuelve una estructura como el contexto,especialmente el atributo
                    # correctamente formateado  TODO faltan los atributos calculados (Cuatrimestres,trimestres y quincenas)
                    datosfecha= getDateEntry(campo,kmask,self.dbdriver)
                    datosfecha['class'] = 'd'
                    datosfecha['campo_base'] = campo  #estrictamente temporal
                    datosfecha['origID'] = prodId
                    prodExpandida.append(datosfecha)
            else:
                prodExpandida.append(produccion)
                
        return prodExpandida

    def _getProdCursor(self,contexto,basefilter,datefilter):
        """
        De una regla de produccion ampliada (de su contexto mas bien) y con los filtros generales de la tabla (o dominio)
        creo la sentencia SQL y obtengo el cursor correspondiente
        INput
           contexto de una regla de produccion (cf. fillGuia)
           basefilter
           datefilter   los filtros de defecto y fecha de la tabla del cubo o dominio
        Output
            cursor   un cursor sql
        """
        table = contexto['table']
        columns = contexto['columns']
        code = contexto['code']
        #filter = contexto.get('filter','')
        sqlDef = {}
        sqlDef['tables'] = table
        sqlDef['fields'] = columns
        if basefilter is not None:
            sqlDef['base_filter'] = basefilter
        if datefilter is not None:
            sqlDef['where'] = datefilter
        sqlDef['order'] = [ str(x + 1) for x in range(len(code))]
        sqlDef['select_modifier']='DISTINCT'
        sqlDef['driver'] = self.dbdriver
        try:
            sqlString = queryConstructor(**sqlDef)
        except:
            print('Zasss')
            pprint(sqlDef)
            pprint(table)
            pprint(columns)
            pprint(filter)
            pprint
            raise
        cursor=getCursor(self.db,sqlString)
        if DEBUG:
            print(time.time(),'Datos ',queryFormat(sqlString))

        return cursor

    def _createProdModel(self,raiz,cursor,contexto,prodId):
        """
        De cursor al modelo que utilizamos para definir la guia
        Input
            raiz    (sobrecarga) la raiz del modelo QStandardItemModel o el modelo TreeDict  (version base del cubo)
            cursor  el cursor a integrar en el modelo
            contexto contexto de la regla de produccion
            prodId identificación de la regla
            
        Ahora mismo este codigo tiene el efecto secundario que en claves multicampo se crea implicitamente una jerarquia de valores
        TODO contemplar el caso contrario
        """
        columns = contexto['columns']
        code = contexto['code']
        desc = contexto['desc']
        groupby = contexto['groupby']
        
        ngroupby = len(groupby)
        ncols = len(columns)
        ndesc = len(columns) - len(code)
        cache_parents = [ None for i in range(len(code))]
        ncode = len(code) -ngroupby
        #ndesc = len(columns) - len(code)

        for entryNum,row in enumerate(cursor):
            # renormalizamos el contenido del cursor
            for k in range(len(row)):
                if row[k] is None:
                    row[k] = ''
                else:
                    row[k] = str(row[k]).replace(DELIMITER,'/')  #OJO todas las claves son Alfanumericas
            if ndesc == 0:
                value = ', '.join(row[-ncode:])
            else:
                value = ', '.join(row[-ndesc:])
            #
            # ahora debo localizar donde en la jerarquia tiene que encontrarse. Eso varia por tipo
            # Notese que para GuideItemModel utilizo un sistema de cache para reducir el numero de busquedas
            #
            if isinstance(raiz,QStandardItem):

                papid = row[0:len(code)]
                key = papid[-1]
                del papid[-1]
                #TODO cache sigue siendo necesario
                if len(papid) == 0:
                    parent = raiz
                else:
                    parent = raiz.model().searchHierarchy(papid,Qt.DisplayRole)
                    if not parent:
                        print('Ilocalizable',papid)
                parent.appendRow((GuideItem(key),GuideItem(value),))
                
            elif isinstance(raiz,TreeDict):
                # problemas inesperados con valores nulos
                for k in range(len(row)):
                    if row[k] is None:
                        row[k] = 'NULL'
                #descripcion
                if ndesc == 0:
                    value=', '.join(row)  
                else:
                    value=', '.join(row[-ndesc:])
                #clave separada jeraruqicamnet por DELIMITER
                key=DELIMITER.join(row[0:len(code)])   #asi creo una jerarquia automatica en claves multiples
                parentId = getParentKey(key)
                raiz.append(TreeItem(key,entryNum,value),parentId)
    
    
    def fillGuia(self,guidIdentifier,qtModel = None):
        '''
        Es el metodo con el que creamos la guia; de paso generamos informacion complementaria, el contexto
        Como campo de entrada
        guidIdentifier  es la gua a procesar. sobrecargada como el número de la guia en la lista o el nombre
        qtModel (Experimental) tipo de modelo que genera. Por defecto TreeDict que no es qt
        El contexto que genera para cada produccion es
            {'table':table,   -> tabla del dominio de la guia
            'code':code,      -> lista de campos que contienen el code (valor interno) de la produccion
            'desc':desc,      -> id. de la descripcion (valor externo). SI no hay es igual que el code
            'groupby':groupby,_> campos que se requieren en una jerarquia para enlazar los niveles. Forma parte
                                 de code
            'columns':columns, _> Lista cmpleta de todos los campos que deben aparecer en la clausula select de la guia
            'elems':elems,    -> Lista de campos que se incluyen como criterios de agregacion al solicitar los datos de                             
                                    la vista con esa guia
            'linkvia':linkvia   _> Clausulas join necesarias para ir de la tabla de datos a donde residen los criterios 
                                    de agregacion
            })

        '''
        
        cubo = self.definition
        if isinstance(guidIdentifier,int):
            guidId = guidIdentifier
        else:
            guidId = [ item['name'] for item in self.lista_guias].index(guidIdentifier)
        guia = self.definition['guides'][guidId]
        
        date_cache = {}
        contexto = []
        
        #arbol = QStandardItemModel()
        #raiz = arbol.invisibleRootItem()
        if qtModel is None:
            tree=TreeDict()
            tree.name = guia['name']
        else:
            arbol = GuideItemModel()
            tree = arbol.invisibleRootItem()  #para que __createProdModel solo necesite invocarse una vez
        
        # primero expandimos las entradas tipo fecha
        prodExpandida = self._expandDateProductions(guidId)
        
        for prodId,produccion in enumerate(prodExpandida):
            origId = produccion['origID']
            clase = produccion.get('class',guia.get('class','o'))
            # for backward compatibility
            if clase == 'h':  
                clase = 'o'
            nombre = produccion.get('name',guia.get('name')+'_'+str(prodId).replace(' ','_').strip())
            table,basefilter,datefilter  = self._setTableName(guia,origId)
            cumgroup = []
            groupby= []
            code = []
            desc = []
            columns = []
            #filter = None
            isSQL = True
            cursor = None
            elems = []
            linkvia = []
            if DEBUG:
                print(self.nombre,guia['name'],nombre)
            """
            El esquema es comun para cada tipo de guia
            primero determino los campos codigo, descripciones y groupby para formar la query que crea el dominio
            (y la obtengo si no implica consulta a la base de datos)
            El groupby son los campos que necesito arrastrar del nivel jerarquico superior para poder enlazar entre niveles
            
            Luego determino que campos (elems) seran los que se necesitaran para el group by en la consulta real
            """
            if clase == 'o':
                if 'domain' in produccion:
                    groupby = norm2List(produccion['domain'].get('grouped by'))
                    code = groupby + norm2List(produccion['domain'].get('code')) 
                    desc = norm2List(produccion['domain'].get('desc'))
                    columns = code + desc
                    #filter = produccion['domain'].get('filter','')
                else:
                    columns = code = desc = norm2List(produccion.get('elem'))
                   
                if prodId == 0:    
                    elems = norm2List(produccion.get('elem'))
                else:
                    elems = contexto[prodId -1]['elems'] + norm2List(produccion.get('elem'))
                
            elif clase == 'c' and 'categories' in produccion:
                isSQL = False
                # esto no es necesario en esta fase
                code = desc= columns = [caseConstructor(nombre,produccion),]
                cursor = []
                for entrada in produccion['categories']:
                    if 'result' in entrada:
                        cursor.append([entrada.get('result'),])
                    else:
                        cursor.append([entrada.get('default'),])
                
                if prodId == 0:    
                    elems = code
                else:
                    elems = contexto[prodId -1]['elems'] + code

            elif clase == 'c' and 'case_sql' in produccion:
                campos = norm2List(produccion.get('elem')) + [nombre, ]
                transformado = []
                for linea in produccion['case_sql']:
                    for k,campo in enumerate(campos):
                        linea = linea.replace('$${}'.format(str(k +1)),campo)
                    transformado.append(linea)
                code = desc = columns = [' '.join(transformado),]

                if prodId == 0:    
                    elems = code
                else:
                    elems = contexto[prodId -1]['elems'] + code

            elif clase == 'd':
                isSQL = False
                code = desc = columns = norm2List(produccion.get('elem'))
                # obtengo la fecha minima y maxima. Para ello tendre que consultar la base de datos
                campo = produccion.get('campo_base') #solo podemos   trabajar con un campo
                if campo in date_cache:
                    pass
                else:
                    #TODO solo se requiere consulta a la base de datos si el formato incluye 'Y'
                    #REFINE creo que fields sobra
                    sqlDefDate=dict()
                    sqlDefDate['tables'] = table
                    if basefilter is not None:
                        sqlDefDate['base_filter'] = basefilter
                    if datefilter is not None:
                        sqlDefDate['where'] = datefilter
                    sqlDefDate['fields'] = [[campo,'max'],[campo,'min'],]
                    sqlDefDate['driver'] = self.dbdriver
                    try:
                        sqlStringDate = queryConstructor(**sqlDefDate) 
                    except:
                        raise()
                    row=getCursor(self.db,sqlStringDate)
                    if not row[0][0]:
                        # un bypass para que no se note 
                        date_cache[campo] = [datetime.date.today(),datetime.date.today()]
                    else:
                        date_cache[campo] = [row[0][0], row[0][1]] 
                    #
                # TODO, desplegarlo todo

                kmask = produccion.get('mask')     
                #FIXME valido fechas pero todos los formatos no son compatibles con esa validacion
                cursor = getDateIndexNew(date_cache[campo][0]  #max_date
                                            , date_cache[campo][1]  #min_date
                                            , kmask)
                # la correcta asignacion de formatos fecha ha sido hecha al desdoblar
                if prodId == 0:    
                    elems = norm2List(produccion.get('elem'))
                else:
                    elems = contexto[prodId -1]['elems'] + norm2List(produccion.get('elem'))


            # si tengo una jerarquia y no tengo group by cargo uno por defecto si es la misma tabla
            if prodId != 0 and len(groupby) == 0:
                if contexto[prodId -1]['table'] == table:  #por coherencia sin groop by es imposible sino
                    groupby = contexto[prodId -1]['code']
                    if code != desc:
                        code = groupby + code
                        columns = code + desc
                    else:
                        code = desc = columns = groupby + code
            #if prodId != 0:
                #cumgroup.append(code)
           
            if prodId == 0:
                linkvia = produccion.get('link via',[]) 
            else:
                linkvia = contexto[prodId -1]['linkvia'] + produccion.get('link via',[])
            
            contexto.append({'table':table,'code':code,'desc':desc,'groupby':groupby,'columns':columns,
                             #'acumgrp':cumgroup,'filter':basefilter,
                             'elems':elems,'linkvia':linkvia})
            if isSQL:
                cursor = self._getProdCursor(contexto[-1],basefilter,datefilter)
            
 
            self._createProdModel(tree,cursor,contexto[-1],prodId)

        if qtModel is None:
            # es el unico modo que genere un ordinal unico 
            k = 0
            for item in tree.traverse(output=1): #por item
                item.ord = k
                k += 1
            return tree,contexto
        else:
            #for item in traverse(tree):
                #print(item.parent().data(Qt.DisplayRole) if item.parent() is not None else '??',
                      #item.data(Qt.DisplayRole))
                
            return arbol,contexto

class Vista:
    #TODO falta documentar
    #TODO falta implementar la five points metric
    def __init__(self, cubo,prow, pcol,  agregado, campo, filtro='',totalizado=True, stats=True):
        self.cubo = cubo
        # acepto tanto nombre como nuero de columna y fila.
        # NO Controlo el error en este caso. Es lo suficientemente serio para abendar
        if isinstance(prow,int):
            row = prow
        else:
            row = [ item['name'] for item in cubo.lista_guias].index(prow)
        if isinstance(pcol,int):
            col = pcol
        else:
            col = [ item['name'] for item in cubo.lista_guias].index(pcol)
        
        # deberia verificar la validez de estos datos
        self.agregado=agregado
        self.campo = campo
        self.filtro = filtro
        self.totalizado = True
        self.stats = True
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None

        self.row_hdr_idx = list()
        self.col_hdr_idx = list()
        #self.row_hdr_txt = list()
        #self.col_hdr_txt = list()

        self.dim_row = None
        self.dim_col = None
        #self.hierarchy= False
        self.array = []
        
        self.setNewView(row, col)

    def setNewView(self,prow, pcol, agregado=None, campo=None, filtro='',totalizado=True, stats=True, force=False):
        # acepto tanto nombre como nuero de columna y fila.
        # NO Controlo el error en este caso. Es lo suficientemente serio para abendar
        if isinstance(prow,int):
            row = prow
        else:
            row = [ item['name'] for item in self.cubo.lista_guias].index(prow)
        if isinstance(pcol,int):
            col = pcol
        else:
            col = [ item['name'] for item in self.cubo.lista_guias].index(pcol)
        
        dim_max = len(self.cubo.lista_guias)
        
        # validaciones. Necesarias porque puede ser invocado desde fuera
        if row >= dim_max or col >= dim_max:
            print( 'Limite dimensional excedido. Ignoramos',row,dim_max,col,dim_max)
            return 
        elif  agregado is not None and agregado not in  self.cubo.lista_funciones:
            print('Funcion de agregacion >{}< no disponible'.format(agregado))
            return
        elif campo is not None and campo not in self.cubo.lista_campos:
            print('Magnitud >{}< no disponible en este cubo'.format(campo))
            return
        else:
            pass
        # Determinamos si han cambiado los valores
        
        procesar = False
        if force:
            procesar = True
        if self.row_id != row:
            procesar = True
            self.row_id = row
        if self.col_id != col:
            procesar = True
            self.col_id = col
        if agregado is not None and agregado != self.agregado:
            procesar = True
            self.agregado = agregado
        if campo is not None and campo != self.campo:
            procesar = True
            self.campo = campo
        if self.filtro != filtro:
            procesar = True
            self.filtro = filtro
        if self.totalizado != totalizado:
            procesar = True
            self.totalizado = totalizado
        if self.stats != stats:
            procesar = True
            self.stats = stats
            
        if procesar:
        
            self.row_id = row
            self.col_id = col
            
                    
            #for k,entrada in enumerate(self.lista_guias):
            for item in (row,col):
                self.cubo.lista_guias[item]['dir_row'],self.cubo.lista_guias[item]['contexto']=self.cubo.fillGuia(item)

            self.dim_row = len(self.cubo.lista_guias[row]['contexto'])
            self.dim_col = len(self.cubo.lista_guias[col]['contexto'])
                
            self.row_hdr_idx = self.cubo.lista_guias[row]['dir_row']
            self.col_hdr_idx = self.cubo.lista_guias[col]['dir_row']
        
            self.__setDataMatrix()
            

    def  __setDateFilter(self):
        return self.cubo.setDateFilter()
        
    def  __setDataMatrix(self):
         #TODO clarificar el codigo
         #REFINE solo esperamos un campo de datos. Hay que generalizarlo
        #self.array = [ [None for k in range(len(self.col_hdr_idx))] for j in range(len(self.row_hdr_idx))]
        self.array = []
        sqlDef = dict()
        sqlDef['tables']=self.cubo.definition['table']
        #sqlDef['select_modifier']=None
        sqlDef['base_filter']=mergeString(self.filtro,self.cubo.definition.get('base filter',''),'AND')
        sqlDef['where'] = []
        sqlDef['where'] += self.__setDateFilter()
        
        # si no copio tengo sorpresas
        contexto_row = self.cubo.lista_guias[self.row_id]['contexto'][:]
        contexto_col = self.cubo.lista_guias[self.col_id]['contexto'][:]
        """
        TODO de momento solo totales en row, como era la version anterior.
        Incluir totales de columan tiene una serie de efectos secundarios en todas las operaciones de columna.
        Debería estudiarlo porque merece la pena
        """
        if self.totalizado:
            self.row_hdr_idx.rebaseTree()
            #self.col_hdr_idx.rebaseTree()
            contexto_row.insert(0,{'elems':["'//'",],'linkvia':[]})
            #contexto_col.insert(0,{'elems':["'//'",],'linkvia':[]})
        maxRowElem = len(contexto_row[-1]['elems'])
        maxColElem = len(contexto_col[-1]['elems'])
        
        for x,row in enumerate(contexto_row):
            for y,col in enumerate(contexto_col):
                if self.totalizado and x == 0:
                    sqlDef['group'] = col['elems']
                    numRowElems = len(row['elems'])
                    numColElems = len(col['elems'])
                    sqlDef['fields'] = row['elems'] + col['elems'] + [(self.campo,self.agregado)]
                else:
                    sqlDef['group'] = row['elems'] + col['elems']
                    numRowElems = len(row['elems'])
                    numColElems = len(col['elems'])
                    sqlDef['fields'] = sqlDef['group']  + [(self.campo,self.agregado)]
                joins = row['linkvia'] + col['linkvia']
                sqlDef['join'] = []
                for entrada in joins:
                    if len(entrada) == 0:
                        continue
                    join_entrada = dict()
                    join_entrada['join_modifier']='LEFT'
                    join_entrada['table'] = entrada.get('table')
                    join_entrada['join_filter'] = entrada.get('filter')
                    join_entrada['join_clause'] = []
                    for clausula in entrada['clause']:
                        entrada = (clausula.get('rel_elem'),'=',clausula.get('base_elem'))
                        join_entrada['join_clause'].append(entrada)
                    sqlDef['join'].append(join_entrada)
                
                sqlDef['order'] = [ str(x + 1) for x in range(len(sqlDef['group']))]
                sqlDef['driver'] = self.cubo.dbdriver
                sqlstring=queryConstructor(**sqlDef)
                lista_compra={'row':{'nkeys':numRowElems,},
                              'rdir':self.row_hdr_idx,
                              'col':{'nkeys':numColElems,'init':numRowElems,},
                              'cdir':self.col_hdr_idx
                              }
                cursor = getCursor(self.cubo.db,sqlstring,regTree,**lista_compra)
                self.array +=cursor #getCursor(self.cubo.db,sqlstring,regTree,**lista_compra)
                if DEBUG:
                    print(time.time(),'Datos ',queryFormat(sqlstring))

        #pprint(self.array)
        
    def toTable(self):
        """
           convertir los datos en una tabla normal y corriente
        """
        table = [ [None for k in range(self.col_hdr_idx.len())] for j in range(self.row_hdr_idx.len())]
        for record in self.array:
            try:
                ind_1 = record[0].ord
                ind_2 = record[1].ord  
                table[ind_1][ind_2]=record[-1]
            except KeyError:
                continue
            except IndexError:
                print('{} o {} fuera de rango'.format(ind_1,ind_2))
        if DEBUG:
            print(time.time(),'table ',len(table),self.row_hdr_idx.len(),len(table[0])) 
        return table

    #def toKeyedTable(self):
        #ktable = [ [None for k in range(self.col_hdr_idx.len()+1)] for j in range(self.row_hdr_idx.len()+1)]
        #ktable[0][0] = None
        #ind = 1
        #for key in self.col_hdr_idx.traverse(mode=1):
            #elem = self.col_hdr_idx[key]
            #ktable[0][elem.ord +1] = key
            #ind += 1
        #ind = 1
        #for key in self.row_hdr_idx.traverse(mode=1):
            #elem = self.row_hdr_idx[key]
            #ktable[elem.ord +1][0] = key
            #ind += 1

        #table = self.toTable()
        #ind = 0
        #for elem in ktable:
           #if ind == 0:
               #ind += 1
               #continue

           #elem[1:] = table[ind][:]
        #return ktable
    
    #def toCsv(self,row_sparse=True,col_sparse=False,translated=True,separator=';',string_sep="'"):
        #ctable = [ ['' for k in range(self.col_hdr_idx.len()+self.dim_row)] 
                             #for j in range(self.row_hdr_idx.len()+self.dim_col) ]
     
        #ind = 1
        #def csvFormatString(cadena):
            #if separator in cadena:
                #return string_sep + cadena + string_sep
            #else:
                #return cadena
        #for key in self.col_hdr_idx.traverse(mode=1):
            #elem = self.col_hdr_idx[key]
            #desc = elem.getFullDesc()   
            #if col_sparse:
                #k = len(desc) -1
                #ctable[k][elem.ord +self.dim_row] = csvFormatString(desc[k])
            #else:
                #for k in range(len(desc)):
                    #ctable[k][elem.ord +self.dim_row] = csvFormatString(desc[k])

            
        #for key in self.row_hdr_idx.traverse(mode=1):
            #elem = self.row_hdr_idx[key]
            #desc = elem.getFullDesc()   
            #if row_sparse:
                #k = len(desc) -1
                #ctable[elem.ord + self.dim_col][k]=csvFormatString(desc[k])
            #else:
                #for k in range(len(desc)):
                    #ctable[elem.ord + self.dim_col][k]=csvFormatString(desc[k])
        #table = self.toTable()
        ## probablemente este paso intermedio es innecesario
        #ind = 0
        #for elem in ctable[self.dim_col : ]:
           #elem[self.dim_row:] = [str(dato) if dato is not None else '' for dato in table[ind] ]
           #ind += 1
        #lineas=[]
        #for row in ctable:
            #lineas.append(separator.join(row))
            
        #return lineas
    
    #def toNamedTable(self):
        #ntable = [ [ None for k in range(self.col_hdr_idx.len()+1)] for j in range(self.row_hdr_idx.len()+1)]
        #ntable[0][0] = None
        #ind = 1
        #for key in self.col_hdr_idx.traverse(mode=1):
            #elem = self.col_hdr_idx[key]
            #ntable[0][elem.ord +1] = getOrderedText(elem.getFullDesc(),sparse=False,separator='\n')
            #ind += 1
        #ind = 1
        #for key in self.row_hdr_idx.traverse(mode=1):
            #elem = self.row_hdr_idx[key]
            #ntable[elem.ord +1][0] = getOrderedText(elem.getFullDesc(),sparse=True,separator='\t')
            #ind += 1

        #table = self.toTable()
        #ind = 0
        #for elem in ntable:
           #if ind == 0:
               #ind += 1
               #continue

           #elem[1:] = table[ind][:]
        #return ntable
        ##for elem in ktable:
            ##print(elem)
            
    #def toTree(self):
        #array = self.toTable()
        #for key in self.row_hdr_idx.traverse(mode=1):
            #elem = self.row_hdr_idx[key]
            #datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    #array[elem.ord][:]
            #elem.setData(datos)
            #if self.stats:
                #elem.setStatistics()
        #if DEBUG:
            #print(time.time(),'Tree ',len(array),self.row_hdr_idx.len())  

    def toTree2D(self):
        array = self.toTable()
        k = 0
        for key in self.row_hdr_idx.traverse(mode=1):
            elem = self.row_hdr_idx[key]
            datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    array[elem.ord][:]
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()
            k += 1
        k = 0
        for key in self.col_hdr_idx.traverse(mode=1):
            elem = self.col_hdr_idx[key]
            datos = [ getOrderedText(elem.getFullDesc(),sparse=True,separator=''),] +\
                    [ array[ind][elem.ord] for ind in range(self.row_hdr_idx.len()) ]
            elem.setData(datos)
            if self.stats:
                elem.setStatistics()
            k += 1
        #if self.totalizado:
            #self.row_hdr_idx.rebaseTree()
            #tabla = self.__grandTotal()
            #datos =['Gran Total',]+[elem[1] for elem in tabla]
            #elem = self.row_hdr_idx['//']
            #elem.setData(datos)
            #if self.stats:
                #elem.setStatistics()

                    
        if DEBUG:       
            print(time.time(),'Tree ',len(array),self.row_hdr_idx.len())  

    def recalcGrandTotal(self):
        def cargaAcumuladores():
            if elem.isLeaf():
                for k in range(len(acumuladores)):
                    for ind,item in enumerate(elem.getPayload()):
                        if item is not None:
                            acumuladores[k][ind]['max'] = max(acumuladores[k][ind]['max'],item)
                            acumuladores[k][ind]['min'] = min(acumuladores[k][ind]['min'],item)
                            acumuladores[k][ind]['sum'] += item
                            acumuladores[k][ind]['count'] += 1
        def procesa():
            if self.agregado == 'avg':
                datos = [item['sum']/item['count'] if item['count'] != 0 else None for item in acumuladores[-1] ]
            else:
                datos = [item[self.agregado] if item[self.agregado] != 0 else None for item in acumuladores[-1] ]
            padres[-1].setPayload(datos)
            if self.stats :
                padres[-1].setStatistics()

        
        arbol = self.row_hdr_idx
        numcol = self.col_hdr_idx.len()
        padres = []
        acumuladores = []
        for elem in arbol.traverse(mode=1,output=1):
            prof = elem.depth()
            if len(padres) < prof:
                padres.append(elem.parentItem)
                acumuladores.append([ {'max':0,'min':0,'count':0,'sum':0} for k in range(numcol)])
                cargaAcumuladores()
            elif len(padres) == prof:
                if padres[-1] == elem.parentItem:
                    cargaAcumuladores()
                else:
                    print('cambio de padre')
            elif len(padres) > prof:
                procesa()
                del padres[-1]
                del acumuladores[-1]
                cargaAcumuladores()
                #if padres[-1] == elem.parentItem:
                    #print('no cambia nada')
                #else:
                    #print('nuevo padre')
                    #padres.append(elem.parentItem)
                #print('para atras')
        else:
            while padres[-1].parent() is not None:
                procesa()
                del padres[-1]
                del acumuladores[-1]
    
    def traspose(self):
        tmp_col = self.row_id
        tmp_row = self.col_id
        
        self.row_id = tmp_row
        self.col_id = tmp_col
        
        self.dim_row = len(self.cubo.lista_guias[self.row_id]['rules'])
        self.dim_col = len(self.cubo.lista_guias[self.col_id]['rules'])

        rtmp = self.row_hdr_idx
        ctmp = self.col_hdr_idx
        self.row_hdr_idx = ctmp  #self.cubo.lista_guias[self.row_id]['dir_row']
        self.col_hdr_idx = rtmp  #self.cubo.lista_guias[self.col_id]['dir_row']

        
    def fmtHeader(self,dimension, separador='\n', sparse=False): #, rango= None,  max_level=None):
        """
           begin new code
           (funcionalidad abreviada)
           Probablemente obsoleto
        """
        if dimension == 'row':
            return self.row_hdr_idx.getHeader('row',separador,sparse)
        elif dimension == 'col':
            return self.col_hdr_idx.getHeader('col',separador,sparse)
        else:
            print('Piden formatear la cabecera >{}< no implementada'.format(dimension))
            return None
    
    
    def __exportHeaders(self,tipo,header_tree,dim,sparse,content):
        if tipo.lower() == 'list':
            tabla = list()
        elif tipo.lower() == 'dict':
            tabla = dict()
        else:
            return None
        ind = 0
        
        for elem in header_tree.traverse(mode=1,output=1):
            entrada = ['' for k in range(dim) ]
            if content == 'branch' and elem.isLeaf() and dim > 1:
                continue
            if content == 'leaf' and not elem.isLeaf():
                continue
            
            desc = elem.getFullDesc()
            depth = elem.depth()
            
            if sparse:
                #entrada[depth -1] = desc[-1].replace(':','-')
                entrada[depth -1] = desc[-1].replace(':','-')
            else:
                for k in range(len(desc)):
                    entrada[k] = desc[k].replace(':','-')
            
            #print(desc,depth,len(desc),entrada)
            
            if content == 'branch' and dim > 1:
                del entrada[dim -1 ]
            elif content == 'leaf' :
                while len(entrada) > 1:
                    del entrada[0]
                    
            entrada.append(elem)
            
            if tipo.lower() == 'list':
                entrada.append(elem.ord)
                tabla.append(entrada)
            else:
                entrada.append(ind)
                tabla[elem.ord] = entrada
            ind += 1
            

        return tabla 
    

    def getExportDataArray(self,parms,selArea=None):
        """
            Parece obsoleta ... deberia adaptarse a lo de la de abajo (sin array)
            
            *parms['file']
            *parms['type'] = ('csv','xls','json','html')
            *parms['csvProp']['fldSep'] 
            *parms['csvProp']['decChar']
            *parms['csvProp']['txtSep'] 
            *parms['NumFormat'] 
            parms['filter']['scope'] = ('all','visible,'select') 
            *parms['filter']['content'] = ('full','branch','leaf')
            parms['filter']['totals'] 
            *parms['filter']['horSparse'] 
            *parms['filter']['verSparse']

        """
        contentFilter = parms['filter']['content']
        row_sparse = parms['filter']['horSparse']
        col_sparse = parms['filter']['verSparse']
        translated = parms['NumFormat']
        numFmt = parms['NumFormat']
        decChar = parms['csvProp']['decChar']

        
        ind = 1
                
        dim_row = self.dim_row if not self.totalizado else self.dim_row + 1
        dim_col = self.dim_col
            
        row_hdr = self.__exportHeaders('List',self.row_hdr_idx,dim_row,row_sparse,contentFilter)
        col_hdr = self.__exportHeaders('List',self.col_hdr_idx,dim_col,col_sparse,contentFilter)
        
        num_rows = len(row_hdr)
        num_cols = len(col_hdr)
        
        dim_row = len(row_hdr[0]) -2
        dim_col = len(col_hdr[0]) -2
        
        ctable = [ ['' for k in range(num_cols + dim_row)] 
                                for j in range(num_rows +dim_col) ]

        for i in range(num_cols):
            for j,colItem in enumerate(col_hdr[i]):
                if j >= dim_col:
                    break
                ctable[j][i + dim_row]=colItem
                
        for i in range(num_rows):
            for j,rowItem in enumerate(row_hdr[i]):
                if j >= dim_row:
                    break
                ctable[i + dim_col][j]=rowItem
                
        table = self.toTable()
        
        for i in range(num_rows):
            x = row_hdr[i][-1]
            for j in range(num_cols):
                y = col_hdr[j][-1]
                ctable[i + dim_col][j + dim_row] = num2text(table[x][y]) if table[x][y] else ''  #TODO aqui es el sito de formatear numeros
        return ctable,dim_row,dim_col

    
    def getExportData(self,parms,selArea=None):
        """
            *parms['file']
            *parms['type'] = ('csv','xls','json','html')
            *parms['csvProp']['fldSep'] 
            *parms['csvProp']['decChar']
            *parms['csvProp']['txtSep'] 
            *parms['NumFormat'] 
            parms['filter']['scope'] = ('all') #,'visible,'select') 
            *parms['filter']['row/col']['content'] = ('full','branch','leaf')
            parms['filter']['row/col']['totals'] 
            *parms['filter']['row/col']['Sparse'] 
            

        """
        scope = parms['filter']['scope']
        contentFilterR = parms['filter']['row']['content']
        contentFilterC = parms['filter']['col']['content']
        totalR = parms['filter']['row']['totals'] 
        totalC = parms['filter']['col']['totals'] 
        row_sparse = parms['filter']['row']['Sparse']
        col_sparse = parms['filter']['col']['Sparse']
        translated = parms['NumFormat']
        numFmt = parms['NumFormat']
        decChar = parms['csvProp']['decChar']
 
        # filterCumHeader(self,total=True,branch=True,leaf=True,separador='\n',sparse=True):
        if contentFilterR == 'full':
            branchR = True
            leafR = True
        elif contentFilterR == 'branch' and self.dim_row > 1:
            branchR = True
            leafR = False
        else: #if contentFilter == 'leaf':
            branchR = False
            leafR = True

        if contentFilterC == 'full':
            branchC = True
            leafC = True
        elif contentFilterC == 'branch' and self.dim_col > 1:
            branchC = True
            leafC = False
        else: #if contentFilter == 'leaf':
            branchC = False
            leafC = True
            
        rows=self.row_hdr_idx.filterCumHeader(sparse=row_sparse,branch=branchR,leaf=leafR,total=totalR)
        cols=self.col_hdr_idx.filterCumHeader(sparse=col_sparse,branch=branchC,leaf=leafC,total=totalC)
        
        dim_row = max([ len(item[1]) for item in rows])
        dim_col = max([ len(item[1]) for item in cols])

        num_rows = len(rows)
        num_cols = len(cols)
        
        ctable = [ ['' for k in range(num_cols + dim_row)] 
                                for j in range(num_rows +dim_col) ]

        columns = [item[0].ord for item in cols ]
        #def extract(self,filter,crossFilter):
            #result = []
            #columns = [item[0].ord for item in crossFilter ]
            #for item in filter:
                #payload = item.getPayload()
                #result.append([payload[k] for k in columns])
            #return result
        
        for ind in range(dim_col):
            ctable[ind][dim_row:]=[item[1][ind] if ind <len(item[1]) else '' for item in cols  ]
        ind = dim_col
        for entrada in rows:
            for k,valor in enumerate(entrada[1]): #cabeceras
                ctable[ind][k]=valor
            payload = entrada[0].getPayload()
            ctable[ind][dim_row:] = [  num2text(payload[k]) for k in columns]
                
            ind +=1
        return ctable,dim_row,dim_col
    
    def export(self,parms,selArea=None):
        file = parms['file']
        type = parms['type']
        if type == 'xls' and not XLSOUTPUT:
            type = 'csv'
            print('Xls writer no disponible, pasamos a csv')
        fldSep  = parms['csvProp']['fldSep']
        txtSep = parms['csvProp']['txtSep'] 

        def csvFormatString(cadena):
            if fldSep in cadena:
                if txtSep in cadena:
                    cadena = cadena.replace(txtSep,txtSep+txtSep)
                return '{0}{1}{0}'.format(txtSep,cadena)
            else:
                return cadena
            
        if parms.get('source') == 'array':
            ctable,dim_row,dim_col = self.getExportDataArray(parms,selArea=None)
        else:
            ctable,dim_row,dim_col = self.getExportData(parms,selArea=None)
            
        if type == 'csv':
            with open(parms['file'],'w') as f:
                for row in ctable:
                    csvrow = [ csvFormatString(item) for item in row ]
                    f.write(fldSep.join(csvrow) + '\n')
            f.closed
        elif type == 'json':
            dump_json(ctable,parms['file'])
        elif type == 'html':
            fldSep = '</td><td>'
            hdrSep = '</th><th>'
            with open(parms['file'],'w') as f:
                f.write('<table>\n')
                f.write('<head>\n')
                cont = 0
                for row in ctable:
                    htmrow = [item.strip() for item in row ]
                    if cont < dim_col:
                        f.write('<tr><th>'+hdrSep.join(htmrow) + '</th></tr>\n')
                        cont +=1
                    elif cont == dim_col:
                        f.write('</thead>\n')
                        f.write('<tr><td>'+fldSep.join(htmrow) + '</td></tr>\n')
                        cont += 1
                    else:
                        f.write('<tr><td>'+fldSep.join(htmrow) + '</td></tr>\n')
                f.write('</body>\n')
                f.write('</table>\n')
            f.closed

        elif type == 'xls':
            workbook = xlsxwriter.Workbook(parms['file'])
            worksheet = workbook.add_worksheet()
            for i,entrada in enumerate(ctable):
                for j,item in enumerate(entrada):
                    worksheet.write(i, j,item.strip())
            workbook.close()
    #return lineas

def experimental():
    from cubemgmt.cubetree import recTreeLoader,dict2tree,navigateTree,CubeItem,traverseTree
    from util.jsonmgr import load_cubo
    def presenta(vista):
        guia=vista.row_hdr_idx
        ind = 0
        for key in guia.traverse(mode=1):
            elem = guia[key]
            print (ind,key,elem.ord,elem.desc,elem.parentItem.key)
            ind += 1
    vista = None
    #micubo = 'rental'
    #micubo = 'datos catalonia'
    micubo = 'datos light'
    guia = 'ideologia'
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos[micubo])
    cubo.nombre = micubo
    vista = Vista(cubo,5,0,'sum',cubo.lista_campos[0],totalizado=True)
    vista.toTree2D()
    #pprint(vista.row_hdr_idx.content)
    #print(vista.row_hdr_idx['CA08:16'])
    #vista.row_hdr_idx.setHeader()
    #vista.row_hdr_idx.getHeader()
    for item in vista.col_hdr_idx.traverse(output = 1):
        print('\t'*item.depth(),item.getFullDesc(),item.ord)

    #print(vista.col_hdr_idx.getHeader())
    #for k,guia in enumerate(cubo.lista_guias):
        #vista = Vista(cubo,k,0,'sum',cubo.lista_campos[0])

    #for micubo in mis_cubos:
        #if micubo == 'default':
            #continue
        #cubo = Cubo(mis_cubos[micubo])
        #cubo.nombre = micubo
        #cubo.fillNewGuias()
        #for k,guia in enumerate(cubo.lista_guias):
            #vista = Vista(cubo,k,0,'sum',cubo.lista_campos[0])
            
        #cubo.nombre = micubo
        #cubo.fillNewGuias()
    #tree = cubo.fillGuia(5)
    #pprint(tree.content)
    #pprint(cubo.definition)
    #pprint(cubo.definition)
    #pprint(cubo.lista_funciones)
    #pprint(cubo.lista_campos)
    #pprint(cubo.getGuideNames())
    #for ind,guia in enumerate(cubo.lista_guias):
        #print(ind,guia['name'])
    #cubo.fillGuias()
    #ind= 5
    #cubo.fillGuia(ind)
    #cubo.lista_guias[ind]['dir_row'].display()
    #pprint(cubo.lista_guias[ind]['dir_row'].content)
    #for node in cubo.lista_guias[ind]['dir_row'].traverse(None,2):
        #print(node)
    #pprint(sorted(cubo.lista_guias[1]['dir_row'])) esto devuelve una lista con las claves
    #pprint(cubo.lista_guias)

    #cubo.fillGuia(1)
    ##pprint(cubo.lista_guias[5])   
    #guia=cubo.lista_guias[5]['dir_row']
    #ind = 0
    #for key in guia.traverse(mode=1):
        #elem = guia[key]
        #print (ind,key,elem.ord,elem.desc)
        #ind += 1
    #vista=Vista(cubo,'fecha','partidos importantes','sum','votes_presential')
    ##vista=Vista(cubo,6,0,'sum','votes_presential')
    #arbol = vista.row_hdr_idx
    ##raiz = arbol.rootItem
    #for item in arbol.traverse(output=1):
        #print(item.key,item)
        ##print(item,item.getRoot(),item.model())
    #print(arbol.count())
    #print(arbol.len())
    #pprint(vista.grandTotal())
    #tabla = vista.toKeyedTable()
    #vista.toTree2D()
    vista.recalcGrandTotal()
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #print(col_hdr)
    #for key in vista.row_hdr_idx.content:
        #elem = vista.row_hdr_idx[key]
        #print(elem,elem.itemData,elem.depth())
    #vista.traspose()
    #row_hdr = vista.fmtHeader('row',separador='\n',sparse='True')
    #print(col_hdr)
    #for key in vista.row_hdr_idx.content:
        #elem = vista.row_hdr_idx[key]
        #pprint(elem)
    #print(vista.row_hdr_idx.len())
    #presenta(vista)
    #print(vista.dim_row)
    #vista.row_hdr_idx.rebaseTree()
    #pprint(vista.row_hdr_idx.content)
    #print(vista.row_hdr_idx['//'].key)
    #for key in vista.row_hdr_idx.traverse(None,1):
        ##print(key,vista.row_hdr_idx[key].desc,vista.row_hdr_idx[key].getFullDesc(),getOrderedText(vista.row_hdr_idx[key].getFullDesc(),sparse=False,separator=':'))
        #print(key,vista.row_hdr_idx[key].desc,vista.row_hdr_idx[key].depth())
    #for elem in vista.array:
        #print(elem[0].desc,elem[1].desc,elem[2])
    
    #tabla = vista.toTable()    
    #row_hdr = vista.fmtHeader('row',sparse=True)
    ####pprint(row_hdr)
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #pprint(col_hdr)
    #idx = 0
    #print('',col_hdr)
    #for ind,record in enumerate(tabla):

        #stat_data=stats(record)
        #for idx,item in enumerate(record):
            #if item is None:
                #continue
            #if item <= stat_data['out_low'] or item >= stat_data['out_hig']:
                #print('{} en {}:  {} es un outlier'.format(row_hdr[ind +1],col_hdr[idx+1],item))
        

        
    #tabla = vista.toIndexedTable()    
    #row_hdr = vista.fmtHeader('row',sparse=True)
    #col_hdr = vista.fmtHeader('col',separador='\n',sparse='True')
    #idx = 0
    #print('',col_hdr)
    #for record in  tabla:
        #print(row_hdr[record[0]['idx']],record[1:])
        #idx += 1



if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    experimental()
        