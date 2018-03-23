#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


'''
Documentation, License etc.

TODO
    to array y funciones para extraer las cabeceras
'''

import config

from util.record_functions import *
from util.tree import *
from util.fechas import *
from util.cadenas import *

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

#from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QStandardItemModel, QStandardItem
#from cubemgmt.cubetree import CubeItem,traverseTree



def getParentKey(clave,debug=False):
    """
      define el padre de un elemento via la clave
    """
    nivel=getLevel(clave)
    if nivel > 0:
        padreKey = config.DELIMITER.join(clave.split(config.DELIMITER)[0:nivel])
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
        
def exportFilter(item,dim,filter=None):
    """
    Auxiliary function.
    Used as filter in export functions
    
    * Input parameters
        * __item__ a GuideItem. Element to be checked
        * __dim__ a number, number of levels of the tree
        * __filter__ a dictionary with the filter requeriments
            * __content__ =  One of ('full','branch','leaf'). _full_ is everything, _branch_ only branches of the model tree; _leaf_ only leaves of the model_tree. Default _full__
            * __totals__ Boolean. True if download includes grand total. Default True

    * Returns
        Boolean. True if accepted, False otherwise
        
    * Note:
        The best way to call it is
            ```
            parms = { 'content':'full','totals':True}
            rowHdr = vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
            ```
    """
    #scope = filter.get('scope','all') #no usado
    if filter is None:
        return True

    contentFilter = filter.get('content','full')
    total = filter.get('totals',True) 

    
    if contentFilter == 'full':
        return True
    
    elif contentFilter == 'branch' and dim > 1:
        branch = True
        leaf = False
    else: #if contentFilter == 'leaf':
        branch = False
        leaf = True

    tipo = item.type()
    
    if tipo == TOTAL and total:
        return True
    elif tipo == BRANCH and branch:
        return True
    elif tipo == LEAF and leaf:
        return True
    else:
        return False

    return True
          
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
        self.file = self.definition.get('table')   #TODO document
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
        self.newModel = True
        
        
        
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
        TODO doc API change
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

    def fillGuias(self,total=None,generateTree=False):
        """
        TODO ripple doc
        WARNING API break. No risk because it isn't used
        
           De una sola operacion generamos toda la información sobre las guias -incluidos los arboles-
           el diccionario ha sido generado en __setGuias
           
           No se usa internamente, ya que puede consumir recursos excesivos en la inicialización del cubo.
           En otros momentos lo he activado. Lo dejo como opcion a los usuarios
           
            generateTree  si genera el arbol o solo el contexto
        """
        lista = []
        for k,entrada in enumerate(self.lista_guias):
            lista.append(self.fillGuia(k,total=total,generateTree=generateTree))
        return lista
    
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
        if config.DEBUG:
            print(time.time(),'Datos ',queryFormat(sqlString))

        return cursor

    def _createProdModel(self,raiz,cursor,contexto,prodId,total=None):
        """
        De cursor al modelo que utilizamos para definir la guia
        Input
            raiz    (sobrecarga) la raiz del modelo QStandardItemModel o el modelo TreeDict  (version base del cubo)
            cursor  el cursor a integrar en el modelo
            contexto contexto de la regla de produccion
            prodId identificación de la regla
            total (si la guia va a ser creada con totalizadores. En el caso de QStandardItemModel ha sido un fracaso de otra manera)
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
                    row[k] = str(row[k]) #.replace(config.DELIMITER,'/') #OJO todas las claves son Alfanumericas
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
                if total:  #no viene recogido previamente
                    papid = ["//",]+papid
                if len(papid) == 0:
                    item = GuideItem()
                    item.setData(value,Qt.DisplayRole)
                    item.setData(key,Qt.UserRole +1)
                    raiz.appendRow((item,))                    
                else:
                    #if total:  #no viene recogido previamente
                        #papid = ["//",]+papid
                    parent = raiz.model().searchHierarchy(papid)
                    if not parent:
                        #print('Ilocalizable',papid)
                        continue
                    else:
                        item = GuideItem()
                        item.setData(value,Qt.DisplayRole)
                        item.setData(key,Qt.UserRole +1)
                        parent.appendRow((item,))
            # No aplica ya. Mantenido por si fuera necesario volver
            #elif isinstance(raiz,TreeDict):
                ## problemas inesperados con valores nulos
                #for k in range(len(row)):
                    #if row[k] is None:
                        #row[k] = 'NULL'
                ##descripcion
                #if ndesc == 0:
                    #value=', '.join(row)  
                #else:
                    #value=', '.join(row[-ndesc:])
                ##clave separada jeraruqicamnet por config.DELIMITER
                #key=config.DELIMITER.join(row[0:len(code)])   #asi creo una jerarquia automatica en claves multiples
                #parentId = getParentKey(key)
                #raiz.append(TreeItem(key,entryNum,value),parentId)
    
    
    def fillGuia(self,guidIdentifier,total=None,generateTree=True):
        '''
        TODO ripple doc
        Es el metodo con el que creamos la guia; de paso generamos informacion complementaria, el contexto
        Como campo de entrada
        guidIdentifier  es la gua a procesar. sobrecargada como el número de la guia en la lista o el nombre
        total . Si debe crearse con totalizadores. En el caso de QStandardItemModel ha sido la unica manera de
                hacerlo que no corrompiera el arbol
        generateTree  si genera el arbol o solo el contexto
        
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

        __NOTAS__
        La funcion ahora mismo es algo "heterodoxa". Hace dos cosas al mismo tiempo, genera el arbol y/o el contexto.
        No estan separadas porque la logica es identica, pero dificil de separar. Además la creacion del arbol necesita del contexto
        '''
        cubo = self.definition
        if isinstance(guidIdentifier,int):
            guidId = guidIdentifier
        else:
            guidId = [ item['name'] for item in self.lista_guias].index(guidIdentifier)
        guia = self.definition['guides'][guidId]
        
        date_cache = {}
        contexto = []

        if generateTree:
            #arbol = QStandardItemModel()
            #raiz = arbol.invisibleRootItem()
            arbol = GuideItemModel()
            arbol.name = self.lista_guias[guidId]['name']
            if total:  #el rebase no me ha traido mas que pesadillas
                raiz = arbol.invisibleRootItem()
                item = GuideItem()
                item.setData('Grand Total',Qt.DisplayRole)
                item.setData('//',Qt.UserRole +1)
                raiz.insertRow(0,(item,))
                tree = item
            else:
                tree = arbol.invisibleRootItem()  #para que __createProdModel solo necesite invocarse una vez
        
        # primero expandimos las entradas tipo fecha
        prodExpandida = self._expandDateProductions(guidId)
        
        for prodId,produccion in enumerate(prodExpandida):
            origId = produccion['origID']
            clase = produccion.get('class',guia.get('class','o'))
            # for backward compatibility
            if clase == 'h':  
                clase = 'o'
                
                        
            if len(prodExpandida) == 1: 
                nombre = produccion.get('name',guia.get('name')) 
            elif produccion.get('name'):
                l_prod = produccion.get('name').split('.')[-1]
                if l_prod == guia.get('name'):
                    nombre = l_prod + '_' + str(prodId).replace(' ','_').strip()
                elif l_prod.startswith(guia.get('name')):
                    nombre = l_prod
                else:
                    nombre = guia.get('name') + '_' + l_prod
            else:
                nombre = guia.get('name')+'_'+str(prodId).replace(' ','_').strip()

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
            if config.DEBUG:
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
                if generateTree:
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
                if generateTree:
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
                    pprint(cursor)
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
                            'name':nombre,'filter':basefilter,'class':clase,   #TODO DOC + ripple to fillGuia
                            'elems':elems,'linkvia':linkvia})
            if generateTree:
                if isSQL:
                    cursor = self._getProdCursor(contexto[-1],basefilter,datefilter)
                
    
                self._createProdModel(tree,cursor,contexto[-1],prodId,total)

            #for item in traverse(tree):
                #print(item.parent().data(Qt.DisplayRole) if item.parent() is not None else '??',
                      #item.data(Qt.DisplayRole))          
                
        if generateTree:
            return arbol,contexto
        else:
            return contexto



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
        self.totalizado = totalizado
        self.stats = stats
        self.row_id = None   #son row y col. a asignar en setnewview
        self.col_id = None

        self.row_hdr_idx = None
        self.col_hdr_idx = None
        #self.row_hdr_txt = list()
        #self.col_hdr_txt = list()

        self.dim_row = None
        self.dim_col = None
        #self.hierarchy= False
        self.array = []
        
        self.setNewView(row, col,agregado, campo, filtro,totalizado, stats)

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
                #TODO TOT-V
                self.cubo.lista_guias[item]['dir_row'],self.cubo.lista_guias[item]['contexto']=self.cubo.fillGuia(item,total=self.totalizado if item == row else False)

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
            contexto_row.insert(0,{'elems':["'//'",],'linkvia':[]})
            #TOT-Y contexto_col.insert(0,{'elems':["'//'",],'linkvia':[]})
        maxRowElem = len(contexto_row[-1]['elems'])
        maxColElem = len(contexto_col[-1]['elems'])
        
        for x,row in enumerate(contexto_row):
            for y,col in enumerate(contexto_col):
                trow = row['elems'][:]
                tcol = col['elems'][:]
                if self.totalizado: #and x != 0:
                    try:
                        pos = trow.index("'//'")
                        del trow[pos]
                    except ValueError:
                        pass
                #TOT-Y START
                #if self.totalizado and y != 0:
                    #try:
                        #pos = tcol.index("'//'")
                        #del tcol[pos]
                    #except ValueError:
                        #pass
                #TOT-Y end
                sqlDef['group'] = trow + tcol
                #numRowElems = len(row['elems'])
                #numColElems = len(col['elems'])
                #sqlDef['fields']=row['elems']+col['elems'] + [(self.campo,self.agregado)]
                if self.totalizado:
                    rowFields =["'//'",] + trow 
                    #if x > 0:
                        #rowFields =["'//'",] + trow 
                    #else:
                        #rowFields = trow
                    numRowElems = len(rowFields)
                    #TOT-Y start
                    #if y > 0:
                        #colFields =["'//'",] + tcol 
                    #else:
                    #TOT-
                    colFields = tcol
                    numColElems = len(colFields)
                    sqlDef['fields'] = rowFields + colFields + [(self.campo,self.agregado)]
                else:
                    sqlDef['fields'] =sqlDef['group']  + [(self.campo,self.agregado)]
                    rowFields = trow
                    numRowElems = len(rowFields)
                    colFields = tcol
                    numColElems = len(colFields)
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
                              'col':{'nkeys':numColElems,
                                     'init':numRowElems,},
                              'cdir':self.col_hdr_idx
                              }

                cursor = getCursor(self.cubo.db,sqlstring,regTreeGuide,**lista_compra)
                self.array +=cursor 
                if config.DEBUG:
                    print(time.time(),'Datos ',queryFormat(sqlstring))

        #pprint(self.array)
     
    
    def __setAndBackup(self,item,idx,data):
        """
        Internal function. In fact should be decoupled from the instance
        Sets the column _idx_ of the _item_ with _data_, and performs an initial backup
        """
        item.setColumn(idx,data)
        cell = item.getColumn(idx)
        cell.setBackup()
        
    def __setTreeContext(self,rowTree,colTree):
        """
        Internal function. In fact should be decoupled from the instance
        Sets tree.colTreeIndex
        """
        rowTree.vista = self
        colTree.vista = self
        rowTree.orthogonal = colTree
        colTree.orthogonal = rowTree
        #colindex = []
        #idx = 1
        #for item in colTree.traverse():
            #colindex.append({'objid':item,'key':item.getFullKey()})
            #idx += 1
        #rowTree.colTreeIndex = {'idx':colindex} #{'dict':coldict,'idx':colindex}
        # rowTree.colTreeIndex['leaf'] = [ idx for idx,obj in enumerate(rowTree.colTreeIndex['idx']) if obj['objid'].type() == LEAF ]
        return None
        
    def toNewTree(self):
        coldict = self.col_hdr_idx.asDict()
        for record in self.array:
            row = record[0]
            colnr = coldict[record[1].getFullKey()]['idx'] + 1
            self.__setAndBackup(row,colnr,record[2])
        if self.stats:
            self.row_hdr_idx.setStats(True)

        self.__setTreeContext(self.row_hdr_idx,self.col_hdr_idx)
        
    def toNewTree2D(self):
        rowdict = self.row_hdr_idx.asDict()
        coldict = self.col_hdr_idx.asDict()
        for record in self.array:
            row = record[0]
            col = record[1]
            rownr = rowdict[row.getFullKey()]['idx'] + 1
            colnr = coldict[col.getFullKey()]['idx'] + 1
            
            self.__setAndBackup(row,colnr,record[2])
            self.__setAndBackup(col,rownr,record[2])
        if self.stats:
            self.row_hdr_idx.setStats(True)
            self.col_hdr_idx.setStats(True)
        
        self.__setTreeContext(self.row_hdr_idx,self.col_hdr_idx)

            
    def toArray(self):
        coldict=self.col_hdr_idx.asDict()
        rowdict=self.row_hdr_idx.asDict()

        result = [ [ None for j in range(len(coldict)) ] for i in range(len(rowdict)) ]
        
        for record in self.array:
            col = coldict[record[1].getFullKey()]['idx']
            row = rowdict[record[0].getFullKey()]['idx']
            result[row][col] = record[2]

        return result

    def toArrayFilter(self,filterrow=lambda x:True,filtercol=lambda x:True):
        """        
        Convert the raw data of the view in a two dimensional array, for further processing. Non existing values are returned as None.

        Aditionally two filter functions are specified as parameters, one for rows, the other for columns. Each function accepts an item tree  as parameter (GuideItem) and returns a boolean value: True if it will be processed, False otherwise

        * Input parameters
            * __filterrow__ filter function for rows.
            * __filtercol__ filter function for columns

        * Returns
        a two dimensional array with the values. Only acceptable rows/columns are included in the array

        """
        coldict=self.col_hdr_idx.asDictFilter(filtercol)
        rowdict=self.row_hdr_idx.asDictFilter(filterrow)

        result = [ [ None for j in range(len(coldict)) ] for i in range(len(rowdict)) ]
        
        for record in self.array:
            try:
                col = coldict[record[1].getFullKey()]['idx']
                row = rowdict[record[0].getFullKey()]['idx']
            except KeyError:
                continue
            result[row][col] = record[2]

        return result
            
    def toList(self,*parms,**kwparms):
        """
        Converts the view results in a list of texts
        * Input parameters. All optional
            * __colHdr__  boolean if a column header will be shown. default True
            * __rowHdr__  boolean if a row header will be shown. default True
            * __numFmt__ python format for the numeric values. Default = '      {:9,d}'
            * __colFmt__    python format for the column headers. Default = ' {:>n.ns}', where n is the len of the numeric format minus 1
            * __rowFmt__   python format for the row headers. Default = ' {:20.20s}', 
            * __hMarker__  hierachical marker (for row header). Default _'  '_
            * __rowHdrContent__ one of ('key','value'). Default 'value'
            * __colHdrContent__ one of ('key','value'). Default 'value'
            * __rowFilter__ a filtering function
            * __colFilter__ a filtering function
        Returns
            a tuple of formatted lines
        """
        colHdr=kwparms.get('colHdr',True)
        rowHdr=kwparms.get('rowHdr',True)
        numFormat = kwparms.get('numFmt','      {:9,d}')
        numLen = len(numFormat.format(0))
        colFormat = kwparms.get('colFmt',' {{:>{0}.{0}s}}'.format(numLen -1))
        rowFormat = kwparms.get('rowFmt','{:20.20s}')
        rowLen = len(rowFormat.format(''))
        hMarker = kwparms.get('hMarker','  ')
        rowContent = kwparms.get('rowHdrContent','value')
        colContent = kwparms.get('colHdrContent','value')
        rowFilter = kwparms.get('rowFilter',lambda x:True)
        colFilter = kwparms.get('colFilter',lambda x:True)
        
        result = []
        tmpArray = self.toArrayFilter(rowFilter,colFilter)
        
        if colHdr:
            colHeaders = self.col_hdr_idx.asHdrFilter(colFilter,content=colContent,format='string',sparse=True)
            if rowHdr:
                hdr = ' '*rowLen
            else:
                hdr = ''
            for item in colHeaders:
                hdr += colFormat.format(item)
        result.append(hdr)
        
        if rowHdr:
            rowHeaders = self.row_hdr_idx.asHdrFilter(rowFilter,content=rowContent,format='string',delimiter=hMarker,sparse=True)
            
        for k,line in enumerate(tmpArray):
            dataLine = ''
            for dato in line:
                if dato is not None:
                    dataLine += numFormat.format(dato)
                else:
                    dataLine +=' '*numLen
            if rowHdr:
                dataLine = rowFormat.format(rowHeaders[k]) + dataLine
            result.append(dataLine)
            
        return result
                
    
    def recalcGrandTotal(self):
        """
           TODO
        """
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
        for elem in arbol.traverse():
            prof = elem.depth()
            if len(padres) < prof:
                padres.append(elem.parent())
                acumuladores.append([ {'max':0,'min':0,'count':0,'sum':0} for k in range(numcol)])
                cargaAcumuladores()
            elif len(padres) == prof:
                if padres and padres[-1] == elem.parent():
                    cargaAcumuladores()
                else:
                    print('cambio de padre')
            elif len(padres) > prof:
                procesa()
                del padres[-1]
                del acumuladores[-1]
                cargaAcumuladores()
                #if padres[-1] == elem.parent():
                    #print('no cambia nada')
                #else:
                    #print('nuevo padre')
                    #padres.append(elem.parent())
                #print('para atras')
        else:
            while True: #padres[-1].parent() is not None:
                procesa()
                del padres[-1]
                del acumuladores[-1]
                if len(padres) == 0 or padres[-1] is None:
                    break
    
    def traspose(self):
        """
        TODO
        """
        tmp_col = self.row_id
        tmp_row = self.col_id
        
        self.row_id = tmp_row
        self.col_id = tmp_col
        
        self.dim_row = len(self.cubo.lista_guias[self.row_id]['contexto'])
        self.dim_col = len(self.cubo.lista_guias[self.col_id]['contexto'])

        rtmp = self.row_hdr_idx
        ctmp = self.col_hdr_idx
        self.row_hdr_idx = ctmp  #self.cubo.lista_guias[self.row_id]['dir_row']
        self.col_hdr_idx = rtmp  #self.cubo.lista_guias[self.col_id]['dir_row']


    def __getExportData(self,parms):
        """
            *parms['file']
            *parms['type'] = ('csv','xls','json','html')
            *parms['csvProp']['fldSep'] 
            *parms['csvProp']['decChar']
            *parms['csvProp']['txtSep'] 
            *parms['NumFormat'] 
            parms['filter']['scope'] = ('all') #,'visible,'select') 
            *parms['filter']['row/col']['content'] = ('full','total','branch','leaf')
            parms['filter']['row/col']['totals'] 
            *parms['filter']['row/col']['Sparse'] 
            
        """
        pfilter = parms.get('filter',{})
        scope = pfilter.get('scope','all')
        pfilterRow = pfilter.get('row',{})
        pfilterCol = pfilter.get('col',{})
        row_sparse = pfilterRow.get('Sparse',True)
        col_sparse = pfilterCol.get('Sparse',True)
        
        #translated = parms.get('NumFormat',False)
        numFmt = parms.get('NumFormat',False)
        decChar = parms.get('csvProp',{}).get('decChar','.')
 
        tmpArray = self.toArrayFilter(lambda x,y=self.dim_row,z=pfilterRow: exportFilter(x,y,z),
                                      lambda x,y=self.dim_col,z=pfilterCol: exportFilter(x,y,z))
        
        rows = self.row_hdr_idx.asHdrFilter(lambda x,y=self.dim_row,z=pfilterRow: exportFilter(x,y,z),
                                            sparse=row_sparse,format='array') #no puedo usar offset
        cols = self.col_hdr_idx.asHdrFilter(lambda x,y=self.dim_col,z=pfilterCol: exportFilter(x,y,z),
                                            sparse=col_sparse,format='array')
        dim_row = max([ len(item) for item in rows])
        dim_col = max([ len(item) for item in cols])

        num_rows = len(rows)
        num_cols = len(cols)
        
        ctable = []
        # relleno las lineas con las cabeceras de columnas
        for j in range(dim_col):
            vector = []
            for k in range(dim_row):
                vector.append('')

            vector[dim_row:] = [column[j] if j < len(column) else '' for column in cols ]
            # insertar nombres especiales
            ctable.append(vector)   
            
        # inclyo el nombre de la guia fila
        ctable[dim_col -1][dim_row -1] = self.row_hdr_idx.name
        
        # relleno las lineas de datos con cabeceras de filas
        for i,linea in enumerate(tmpArray):
            vector = []
            for k in range(dim_row):
                if k >= len(rows[i]):
                    vector.append('')
                else:
                    vector.append(rows[i][k])
            vector[dim_row : ] = [ num2text(valor,numFmt=numFmt,decChar=decChar) for valor in linea ]
            ctable.append(vector)

        return ctable,dim_row,dim_col
    
    def export(self,parms,selArea=None):
        if 'file' not in parms:
            print('Nombre de fichero no disponible')
            return -1
        file = parms['file']
        type = parms.get('type','csv')
        if type == 'xls' and not XLSOUTPUT:
            type = 'csv'
            print('Xls writer no disponible, pasamos a csv')
        csvProp = parms.get('csvProp',{})
        fldSep  = csvProp.get('fldSep',',')
        txtSep = csvProp.get('txtSep',"'") 

        def csvFormatString(cadena):
            if fldSep in cadena:
                if txtSep in cadena:
                    cadena = cadena.replace(txtSep,txtSep+txtSep)
                return '{0}{1}{0}'.format(txtSep,cadena)
            else:
                return cadena
            
        ctable,dim_row,dim_col = self.__getExportData(parms)
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
        return 0
# monkeypatch
Vista.toTree = Vista.toNewTree
Vista.toTree2D = Vista.toNewTree2D

from util.decorators import stopwatch
@stopwatch
def createVista(cubo,x,y):
    vista = Vista(cubo,x,y,'sum',cubo.lista_campos[0],totalizado=True)
    vista.toNewTree2D()
    print(vista.row_hdr_idx.numRecords(),'X',vista.col_hdr_idx.numRecords())
    

    
def bugFecha():
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    #vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    vista = Vista(cubo,'fecha','partidos importantes','sum','votes_presential',totalizado=True)
    for item in vista.row_hdr_idx.traverse():
        print(item.data(Qt.DisplayRole),item.data(Qt.UserRole +1))
    for line in vista.toList():
        print(line)
    print()

def toList():
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    #vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    vista = Vista(cubo,'fecha','partidos importantes','sum','votes_presential',totalizado=True)
    for line in vista.toList():
        print(line)
    print()
    for line in vista.toList(rowHdrContent='key',rowFilter=lambda x:x.type() == TOTAL):
        print(line)

def checkFilter():
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    parms = { 'content':'full','totals':True}
    #pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
    parms['content']='branch'
    parms['totals']=False
    pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
           
def checkArrays():
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'municipio','partidos importantes','sum','votes_presential',totalizado=True)
    
    result = []

    if vista.row_hdr_idx.colTreeIndex is None:
        vista.toNewTree()   
    toArrayQD(vista)
    toArray(vista)
    toArrayFilter(vista,lambda x:True,lambda x:True)
 
@stopwatch
def toArrayQD(vista):
    """
    to array quick and dirty
    """
    result = []

    if vista.row_hdr_idx.colTreeIndex is None:
        vista.toNewTree()   
        
    numCols = vista.col_hdr_idx.numRecords()
    #now we get the data for each row
    for item in vista.row_hdr_idx.traverse():
        datos = item.getPayload()
        # relleno para tener valores en todas las columnas
        contenido = len(datos)
        if numCols - contenido > 0:
            datos.extend( [ None for k in range(numCols - contenido)])
        result.append(datos)

    return result

@stopwatch
def toArray(vista):    
    return vista.toArray()

@stopwatch
def toArrayFilter(vista,filterrow,filtercol):
    
    return vista.toArrayFilter(filterrow,filtercol)

def getHeadersFilter():
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    pprint(vista.row_hdr_idx.asHdrFilter(lambda x:x.type() in (BRANCH, LEAF) ))
    
def getHeaders(**parms):
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["experimental"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    #pprint(vista.row_hdr_idx.asHdr())
    #pprint(vista.row_hdr_idx.asHdr(content='key'))
    #pprint(vista.row_hdr_idx.asHdr(content='value'))
    #pprint(vista.row_hdr_idx.asHdr(offset=vista.dim_col))
    #pprint(vista.row_hdr_idx.asHdr(format='array',offset=vista.dim_col))
    print(vista.dim_row)
    pprint(vista.row_hdr_idx.asHdr(format='array',normArray=vista.dim_row +1))
 
def getBaseHeaders(**parms):
    from util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    for item in vista.row_hdr_idx.traverse():
        print(item.data(Qt.DisplayRole))
        print(item.getFullHeadInfo())
        print(item.getFullHeadInfo(content='value'))
        print(item.getFullDesc())
        print(item.getFullHeadInfo(content='value',format='array'))
        print(item.getFullHeadInfo(content='value',format='array',sparse=True))
        print(item.getFullHeadInfo(content='value',format='string'))
        print(item.getFullHeadInfo(content='value',format='string',sparse=True))
        print(item.data(Qt.UserRole +1))
        print(item.getFullHeadInfo(content='key'))
        print(item.getFullKey())
        print(item.getFullHeadInfo(content='key',format='string'))
 
def export():
    from util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
    #vista.toNewTree()
    export_parms = {'NumFormat':True,'csvProp':{'decChar':','}}
    export_parms['file'] = 'ejemplo.dat'
    vista.export(export_parms)

def testTree():
    from util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
    vista.toTree2D()
    for item in vista.row_hdr_idx.traverse():
        print(item.simplifyHierarchical())
        
def testTraspose():
    from util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    vista.toTree2D()
    vista.traspose()
    print(vista.col_hdr_idx.asHdr())
    for item in vista.row_hdr_idx.traverse():
        print(item.getPayload())

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
    #guia = 'ideologia'

    mis_cubos = load_cubo()
    
    #for cuboId in mis_cubos:
        #if cuboId == 'default':
            #continue
        #print('\n----',cuboId,'----\n')
        #cubo = Cubo(mis_cubos[cuboId])
        #cubo.nombre = cuboId
        #iters = len(cubo.lista_guias)
        #for i in range(iters):
            #for j in range(iters):
                #print(cuboId,'::',cubo.lista_guias[i]['name'],cubo.lista_guias[j]['name'])
                #createVista(cubo,i,j)

    cuboId = micubo
    cubo = Cubo(mis_cubos[cuboId])
    #cubo.nombre = cuboId
    #iters = len(cubo.lista_guias)
    #for i in range(iters):
        #for j in range(iters):
            #print(cuboId,'::',cubo.lista_guias[i]['name'],cubo.lista_guias[j]['name'])
            #createVista(cubo,i,j)
            
    #cubo = Cubo(mis_cubos[micubo],qtModel=True)
    #cubo.nombre = micubo
    #guiax,dummy = cubo.fillGuia(1,total=True)
    #guiax.rebaseTree()
    #for item in guiax.traverse():
        #print('\t'*item.depth(),item.data(Qt.UserRole +1))
    #guiax,dummy = cubo.fillGuia(0)
    #for item in guiax.traverse():
        #print('\t'*item.depth(),item.data(Qt.UserRole +1))
    
    vista = Vista(cubo,'municipio','partidos importantes','sum','votes_presential',totalizado=True)
    vista.toNewTree2D()
    hdr = ' '*20 
    for item in vista.col_hdr_idx.traverse():
        hdr += '{:>14s} '.format(item.data(Qt.DisplayRole))
    print(hdr)
    for item in vista.row_hdr_idx.traverse():
#        if item is not None:
        rsults = item.getPayload()
        datos = ''
        for dato in rsults:
            if dato is not None:
                datos += '      {:9,d}'.format(dato)
            else:
                datos +=' '*15
        print('{:20s}{}'.format(item.data(Qt.DisplayRole),datos))
        #print('\t'*item.depth(),item.data(Qt.UserRole +1),item.gpi(2))

    #for item in vista.row_hdr_idx.traverse():
##        if item is not None:
        #print('\t'*item.depth(),item.data(Qt.DisplayRole),item.lenPayload(),item.getPayload())
        ##print('\t'*item.depth(),item.data(Qt.UserRole +1),item.gpi(2))
    #pprint(vista.row_hdr_idx.content)
    #print(vista.row_hdr_idx['CA08:16'])
    #vista.row_hdr_idx.setHeader()
    #vista.row_hdr_idx.getHeader()
    #for item in vista.col_hdr_idx.traverse():
        #print('\t'*item.depth(),item.data(Qt.DisplayRole))

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




if __name__ == '__main__':
    # para evitar problemas con utf-8, no lo recomiendan pero me funciona
    import sys
    #print(sys,version_info)
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    export()
    #tabla = toArray()
    #for item in tabla:
        #print(len(item),item)
    #getHeaders()
    #getHeadersFilter()
    fr = lambda x:x.type() == TOTAL
    fg = lambda x:True
    #testTraspose()
    #bugFecha()
    #extract()
