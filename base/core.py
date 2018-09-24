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

import base.config as config

from support.util.record_functions import *
from base.tree import *
from support.util.fechas import *
from support.util.cadenas import *


from support.datalayer.access_layer import *
from support.datalayer.query_constructor import *

from support.util.numeros import stats,num2text

from support.datalayer.datemgr import getDateEntry, getDateIndexNew
from pprint import *

import time

from support.util.jsonmgr import dump_structure,dump_json   
try:
    import xlsxwriter
    XLSOUTPUT = True
except ImportError:
    XLSOUTPUT = False

#from PyQt5.QtCore import Qt
#from PyQt5.QtGui import QStandardItemModel, QStandardItem
#from base.cubetree import CubeItem,traverseTree



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
    
def exportVisibleFilter(item,dim,filter=None,dir='row',view=None):
    if view is None:
        pass
    else:
        if dir == 'row':
            entry = item
            while entry.parent():
                row = entry.row()
                pai = entry.parent().index() if entry.parent() else QModelIndex()
                if view.isRowHidden(row,pai):
                    return False
                entry = entry.parent()
        elif dir == 'col':
            pos = item.model().item2pos(item)
            if view.isColumnHidden(pos +1):
                return False
    return exportFilter(item,dim,filter)

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
 
def cursorTreeBased(tree,data,display=False):
    from base.tree import traverse
    """
    
    crear un cursor para guias multiplicando los elementos del arbol (hojas) * un array predeterminado
    para tener subdivisiones, p.e. por fechas sin tener que recurrir a consltar la base de datos
    
    Input parms
        * tree the StandardItemModel derived tree
        * array the array we want to integrate
        * Display = True if tree is used for guide content display (a pure QStandardItemModel), False when used for view guiding (a GuideItemModel)
    Output parms
        * cursor  an array similar to the cursors we merge during the fiillGuia processing
    
    """
    def depth(item):
        """
        depth of an item in the tree hierachy
        """
        depth = 0 
        pai = item
        while pai.parent():
            depth += 1
            pai = pai.parent()
        return depth
    
    def fullKeys(item,display):
        """
        returns an array with the keys of each of the branches leading to the item
        
        """
        record = []
        pai = item
        if display:
            role = Qt.DisplayRole
        else:
            role = Qt.UserRole +1
        record.insert(0,pai.data(role))
        while pai.parent():
            pai = pai.parent()
            record.insert(0,pai.data(role))
        return record
        
    cursor = []
    if isinstance(tree,QStandardItemModel):
        mtree = tree
    else:
        mtree  = tree.model()
    for item in traverse(mtree):
        if item.hasChildren():
            continue
        else:
            record = fullKeys(item,display)
            for entry in data:
                krec = record[:]
                norm = norm2List(entry)
                krec += norm
                cursor.append(krec)
    #pprint(cursor)
    return cursor
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
        filtros = self.definition.get('date filter')
        return setDateFilterCore(filtros)
        #return self.setDateFilterCore(filtros)

    #def setDateFilterCore(self,filtros):
        #'''
        #TODO doc API change
                    #mover a support.datalayer.access_layer
        #convierte la clausula date filter en codigo que puede utilizarse como una clausula where. 
        #Este componente acepta los fitros como algo externo, de modo que pueda ser utilizado en varias instancias dentro de las aplicaciones
        #Retorna una tupla de condiciones campo BETWEEN x e y, con un indicador de formato apropiado (fecha/fechahora(
        
        #'''
        #sqlClause = []
        #if not filtros:
            #return sqlClause
        #if len(filtros) == 0 :
            #return sqlClause
        #for item in  filtros :
            #clase_intervalo = item['date class']
            #tipo_intervalo = item['date range']
            #periodos = int(item['date period'])
            #if isinstance(item['elem'],(list,tuple)):
                #campo = item['elem'][0] #no debe haber mas
            #else:
                #campo = item['elem']
            #if clase_intervalo == 0:
                #continue
            #if item['date class']:
                    #intervalo = dateRange(clase_intervalo,tipo_intervalo,periodo=periodos,fmt=item.get('date format'))
                    #sqlClause.append((campo,'BETWEEN',intervalo,'f'))
        #return sqlClause
    

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
    
    def _setTableName(self,guiaId,prodRule):
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

        guia = self.definition['guides'][prodRule.get('origGuide')]
        idx = prodRule.get('origID',0)
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
    
            
   
    def _expandReference(self,guidID,prodRules=None):
        prodExpandida = []
        if not prodRules:
            prodRules = self.definition['guides'][guidID]['prod']        
        for prodId,produccion in enumerate(prodRules):
            produccion['origGuide'] = guidID
            produccion['origID'] = prodId
            if 'class' not in produccion:
                produccion['class'] = self.definition['guides'][guidID]['class']        
            if 'name' not in produccion:
                produccion['name'] = self.definition['guides'][guidID]['name']    
            if produccion.get('reference'):
                refId = [ item['name'] for item in self.lista_guias].index(produccion['reference'])
                prodInter = self._expandReference(refId)
                for prod in prodInter:
                    if produccion.get('link ref'):
                        prod['link ref'] = produccion.get('link ref')
                    prodExpandida.append(prod)
            else:
                prodExpandida.append(produccion)
        return prodExpandida
            
    def _expandDateProductions(self,guidID,prodRules=None):
        """
        las producciones tipo date son abreviaturas de jerarquias internas. Ahora es el momento de dedoblarlas
        Quedan como entradas simples en la tabla de contextos de la guia (bien marcadas como dates);
        tienen dos pequeñas peculiaridades:
        los atributos campo_base con el nombre del campo original y
        origID con el numero de la regla de producción original (para trazas)
        """
        prodExpandida = []
        if not prodRules:
            prodRules = self.definition['guides'][guidID]['prod']        
        for prodId,produccion in enumerate(prodRules):
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
                    datosfecha['origGuide'] = guidID
                    datosfecha['campo_base'] = campo  #estrictamente temporal
                    datosfecha['origID'] = prodId
                    prodExpandida.append(datosfecha)
            else:
                prodExpandida.append(produccion)
                
        return prodExpandida

    def _getProdCursor(self,contexto,ind,basefilter,datefilter):
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
            elemCtx = contexto[ind]
            
            table = elemCtx['table']
            columns = elemCtx['columns']
            code = elemCtx['code']
            link_ref = elemCtx.get('link ref')
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
            sqlDef['driver'] = self.db.dialect
            if link_ref:
                sqlDef['fields'] = setPrefix(sqlDef['fields'],contexto[ind -1]['table'],'s{}'.format(ind))
                sqlDef['join']=[{'table':'{} AS {}'.format(contexto[ind -1]['table'],'s{}'.format(ind)),
                                 'join_modifier':'LEFT',
                                'opt_clause':link_ref}]
            try:
                sqlString = queryConstructor(**sqlDef)
                print(queryFormat(sqlString))
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

    def createProdModel(self,raiz,cursor,contexto,prodId,total=None,display=False,cartesian=True):
        """
        De cursor al modelo que utilizamos para definir la guia
        Input
            raiz    (sobrecarga) la raiz del modelo QStandardItemModel o el modelo TreeDict  (version base del cubo)
            cursor  el cursor a integrar en el modelo
            contexto contexto de la regla de produccion
            prodId identificación de la regla
            total (si la guia va a ser creada con totalizadores. En el caso de QStandardItemModel ha sido un fracaso de otra manera)
            display en el formato que pide guidePreview
            cartesian: si el cruce entre distintos niveles es via un campo de enlace implicito o producto cartesiano
        Ahora mismo este codigo tiene el efecto secundario que en claves multicampo se crea implicitamente una jerarquia de valores
        TODO contemplar el caso contrario
        """
        columns = contexto['columns']   #columnas que van a obtenerse de la b.d.
        code = contexto['code']               #código que conforma la guia
        
        desc = contexto['desc']                #texto descriptivo de cada codigo
        groupby = contexto['groupby']
        
        ngroupby = len(groupby)
        ncols = len(columns)
        ndesc = len(columns) - len(code)
        ncode = len(code) # -ngroupby
                
        def getAttributes(record,contexto,total,cartesian):
            columns = contexto['columns']   #columnas que van a obtenerse de la b.d.
            ncols = len(columns)
            groupby = contexto['groupby']
            ngroupby = len(groupby)
            code = contexto['code']               #código que conforma la guia
            ncode = len(code) # -ngroupby
            desc = contexto['desc']                #texto descriptivo de cada codigo
            ndesc = len(columns) - len(code)
            

            pai_key = []
            key = None
            value = None
            """
            #version alternativa que no requiere de groupby explicito (si no es cartesiano)
            """
            if not cartesian and ncode > 1:
                ngroupby = ncode -1
            
            if ngroupby != 0:
                pai_key = record[0:ngroupby]
            key = normConcat(self.db,record[ngroupby:ncode])[0]
            value = normConcat(self.db,record[ncode:])[0] if ndesc > 0 else key
            return pai_key, key, value
        
        def insertElement(padre,key,value,display=False):
            if display:
                row = (QStandardItem(str(key)),QStandardItem(str(value)),)
                row[0].setData(key,Qt.UserRole +1)
                row[1].setData(value,Qt.UserRole +1)
                insertSorted(row,padre,Qt.UserRole  +1)                    
            else:
                item = GuideItem(key,value)
                insertSorted(item,padre,Qt.UserRole +1)
            
        def cooptCursor(padre,cursor,contexto,total,display,cartesian):
            for record in cursor:
                pai_key,key,value = getAttributes(record,contexto,total,cartesian)
                if pai_key:
                    if total:
                        pai_key.insert(0,'//')
                    pater = padre.getFullHeadInfo(content='key',format='array')
                else:
                    pater = []
                
                if pai_key == pater:
                    insertElement(padre,key,value,display)


        if cartesian:
            if raiz.rowCount() == 0:
                    cooptCursor(raiz,cursor,contexto,total,display,cartesian)
            else:
                worksheet = []
                for item in raiz.model().traverse():
                    if item.isLeaf():
                        worksheet.append(item)
                for item in worksheet:
                    cooptCursor(item,cursor,contexto,total,display,cartesian)
        else:
            for record in cursor:
                pai_key,key,value = getAttributes(record,contexto,total,cartesian)
                if total :
                    pai_key.insert(0,'//')
                if len(pai_key) == 0:
                    padre = raiz
                else:
                    padre = searchHierarchy(raiz.model(),pai_key,Qt.UserRole +1)
                if not padre:
                    continue
                else:
                    insertElement(padre,key,value,display)
        
        
        #model = raiz.model()
        #for item in model.traverse():
            #print(item.getFullKey(),'->-',item.text())
                   

    
    def setGroupBy(self,contexto,prodId,table,code,desc,columns,groupby):
        groupby = contexto[prodId -1]['code']
        if code != desc:
            code = groupby + code
            columns = code + desc
        else:
            code = desc = columns = groupby + code
        
        return groupby,code,desc,columns

    
    def fillGuia(self,guidIdentifier,total=None,generateTree=True,display=False,cartesian=False):
        '''
        TODO ripple doc
        Es el metodo con el que creamos la guia; de paso generamos informacion complementaria, el contexto
        Como campo de entrada
        guidIdentifier  es la gua a procesar. sobrecargada como el número de la guia en la lista o el nombre
        total . Si debe crearse con totalizadores. En el caso de QStandardItemModel ha sido la unica manera de
                hacerlo que no corrompiera el arbol
        generateTree  si genera el arbol o solo el contexto
        display si el arbol generado es solo para ver la guia (en guidePrevuew)
        cartesian: si el cruce entre distintos niveles es via un campo de enlace implicito o producto cartesiano
        
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
        
        WIP Para el caso de claves multicampo, en principio creo que case_sql puede quedar como hasta ahora
        '''
        def _createTree(total,display):
            if display:
                arbol = QStandardItemModel()
            else:
                arbol = GuideItemModel()
                arbol.setItemPrototype(GuideItem())
            arbol.name = self.lista_guias[guidId]['name']
            if total:  #el rebase no me ha traido mas que pesadillas
                raiz = arbol.invisibleRootItem()
                item = GuideItem('//','Grand Total')
                raiz.insertRow(0,(item,))
                tree = item
            else:
                tree = arbol.invisibleRootItem()  #para que __createProdModel solo necesite invocarse una vez
            return arbol,tree

        def setName():
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
                
            return nombre
        
        def renormElems():
            elems = norm2List(produccion['elem'])
            for k in range(len(elems)):
                if '(' in elems[k] or ' ' in elems[k]:
                    continue # no puedo cualificar campos sin provocar un desastre en una funcion
                if '.' not in elems[k]:
                    elems[k] = '{}.{}'.format(table,elems[k])
            produccion['elem'] = elems

        def fieldInfoOrdinary():
            #TODO renormalizar nombres si es posible
            if 'domain' in produccion:
                groupby = norm2List(produccion['domain'].get('grouped by',produccion.get('grouped by')))
                code = groupby + normConcat(self.db,produccion['domain'].get('code')) 
                desc = norm2List(produccion['domain'].get('desc'))
                columns = code + desc
                #filter = produccion['domain'].get('filter','')
            else:
                columns = code = desc = normConcat(self.db,produccion.get('elem'))
                groupby = []
            if prodId == 0:    
                elems = normConcat(self.db,produccion.get('elem'))
            else:
                elems = contexto[prodId -1]['elems'] + normConcat(self.db,produccion.get('elem'))
            return groupby,code,desc,columns,elems
        
        def fieldInfoCategory(nombre):
            renormElems()
            code = desc= columns = [caseConstructor(nombre,produccion),]
            if prodId == 0:    
                elems = code
            else:
                elems = contexto[prodId -1]['elems'] + code
            groupby = []
            return groupby,code,desc,columns,elems
        
        def fieldInfoCase(nombre):
            renormElems()
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
            groupby = []
            return groupby,code,desc,columns,elems

        def fieldInfoDate():
            renormElems()
            print('fieldInfoDate')
            pprint(produccion)
            code = desc = columns = norm2List(produccion.get('elem'))
                # la correcta asignacion de formatos fecha ha sido hecha al desdoblar
            if prodId == 0:    
                elems = norm2List(produccion.get('elem'))
            else:
                elems = contexto[prodId -1]['elems'] + norm2List(produccion.get('elem'))
            groupby = []
            return groupby,code,desc,columns,elems
            
        def categoriesCursorGen(): #self,tree,produccion,prodId,contexto,basefilter,datefilter):
            kcursor = []
            for entrada in produccion['categories']:
                if 'result' in entrada:
                    kcursor.append([entrada.get('result'),])
                else:
                    kcursor.append([entrada.get('default'),])
            kcursor.sort()
            if prodId == 0:
                cursor = kcursor
            else:
                cursor = cursorTreeBased(tree,kcursor,display)
                #cursor  = self._getProdCursor(contexto,prodId,basefilter,datefilter)
            return cursor
        
        def dateCursorGen( ):
            #self,tree,produccion,prodId,contexto,basefilter,datefilter,date_cache,origId,origGuide,guidId,table):
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
            kcursor = getDateIndexNew(date_cache[campo][0]  #max_date
                                        , date_cache[campo][1]  #min_date
                                        , kmask)
            if origId == 0 and guidId == origGuide:
                cursor = kcursor
            else:
                cursor = cursorTreeBased(tree,kcursor,display)
                #cursor  = self._getProdCursor(contexto,prodId,basefilter,datefilter)
            return cursor
    
        cubo = self.definition
        if isinstance(guidIdentifier,int):
            guidId = guidIdentifier
        else:
            guidId = [ item['name'] for item in self.lista_guias].index(guidIdentifier)
        guia = self.definition['guides'][guidId]
        
        date_cache = {}
        contexto = []

        if generateTree:
            arbol,tree = _createTree(total,display)
        
        prodReference = self._expandReference(guidId)
        #self.definition['guides'][guidId]['prod'] = prodReference
        # primero expandimos las entradas tipo fecha
        prodExpandida = self._expandDateProductions(guidId,prodReference) #,prodReference)
        
        for prodId,produccion in enumerate(prodExpandida):
            origGuide = produccion.get('origGuide',guidId)
            origId = produccion['origID']
            clase = produccion.get('class',guia.get('class','o'))
            # for backward compatibility only
            if clase == 'h':  
                clase = 'o'
                
            nombre = setName()

            table,basefilter,datefilter  = self._setTableName(guidId,produccion) #self._setTableName(guia,origId)
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
            # create el contexto
            if clase == 'o':
                groupby,code,desc,columns,elems = fieldInfoOrdinary()
            elif clase == 'c' and 'categories' in produccion:
                groupby,code,desc,columns,elems = fieldInfoCategory(nombre)
            elif clase == 'c' and 'case_sql' in produccion:
                groupby,code,desc,columns,elems = fieldInfoCase(nombre)
            elif clase == 'd':
                groupby,code,desc,columns,elems = fieldInfoDate()
            
            #if prodId > 0:
               #groupby = norm2List(produccion.get('domain',{}).get('grouped by',produccion.get('grouped by')))
            ## si tengo una jerarquia y no tengo group by cargo uno por defecto si es la misma tabla
            if not cartesian and prodId != 0 and len(groupby) == 0:
                groupby,code,desc,columns = self.setGroupBy(contexto,prodId,table,code,desc,columns,groupby)
                #if contexto[prodId -1]['table'] == table:  #por coherencia sin groop by es imposible sino
                    #groupby = contexto[prodId -1]['code']
                    #if code != desc:
                        #code = groupby + code
                        #columns = code + desc
                    #else:
                        #code = desc = columns = groupby + code
            #if prodId != 0:
                #cumgroup.append(code)
            
            if prodId == 0:
                linkvia = produccion.get('link via',[]) 
            else:
                linkvia = contexto[prodId -1]['linkvia'] + produccion.get('link via',[])
            
            contexto.append({'table':table,'code':code,'desc':desc,'groupby':groupby,'columns':columns,
                                #'acumgrp':cumgroup,'filter':basefilter,
                            'name':nombre,'filter':basefilter,'class':clase,   #TODO DOC + ripple to fillGuia
                            'origGuide':produccion.get('origGuide'),'origID':produccion.get('origID'),'link ref':produccion.get('link ref'),
                            'elems':elems,'linkvia':linkvia})
            # ahora a ejecutar
            if generateTree:
                if clase == 'c' and 'categories' in produccion:
                    cursor = categoriesCursorGen() #tree,produccion,prodId,contexto,basefilter,datefilter)
                elif clase == 'd':
                    ## obtengo la fecha minima y maxima. Para ello tendre que consultar la base de datos
                    cursor = dateCursorGen() #tree,produccion,prodId,contexto,basefilter,datefilter,date_cache,origId,origGuide,guidId,table)
                else:
                    cursor  = self._getProdCursor(contexto,prodId,basefilter,datefilter)
                self.createProdModel(tree,cursor,contexto[-1],prodId,total,display,cartesian)
        if generateTree:
            return arbol,contexto
        else:
            return contexto



class Vista:
    #TODO falta documentar
    #TODO falta implementar la five points metric
    def __init__(self,cubo,prow,pcol,agregado,campo,**kwparm):
        """
        parametrros:
            __cubo__
            __prow__
            __pcol__
            __agregado__
            __campo__
            __kwparm__
                filtro='',
                totalizado=True,
                stats=True, 
                cartesian=False):
        """
    #def __init__(self, cubo,prow, pcol,  agregado, campo, filtro='',totalizado=True, stats=True, cartesian=False):
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
        self.filtro = kwparm.get('filtro','')
        self.totalizado = kwparm.get('totalizado',True)
        self.stats = kwparm.get('stats',True)
        self.cartesian = kwparm.get('cartesian',False)
        
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
        
        self.setNewView(row, col,agregado, campo, **kwparm)  #filtro,totalizado, stats,cartesian=cartesian)

    def setNewView(self,prow,pcol,agregado,campo,**kwparm):
    ##def setNewView(self,prow, pcol, agregado=None, campo=None, filtro='',totalizado=True, stats=True, force=False, cartesian=False):
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
    
        filtro = kwparm.get('filtro','')
        totalizado = kwparm.get('totalizado',True)
        stats = kwparm.get('stats',True)
        force = kwparm.get('force',False)
        cartesian = kwparm.get('cartesian',False)
    
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
        if self.cartesian != cartesian:
            procesar = True
            self.cartesian = cartesian
            
        if procesar:
        
            self.row_id = row
            self.col_id = col
            
                    
            #for k,entrada in enumerate(self.lista_guias):
            for item in (row,col):
                #TODO TOT-V
                self.cubo.lista_guias[item]['dir_row'],self.cubo.lista_guias[item]['contexto']=\
                    self.cubo.fillGuia(item,
                                                total=self.totalizado if item == row else False,
                                                cartesian=self.cartesian if item == row else False)

            self.dim_row = len(self.cubo.lista_guias[row]['contexto'])
            self.dim_col = len(self.cubo.lista_guias[col]['contexto'])
                
            self.row_hdr_idx = self.cubo.lista_guias[row]['dir_row']
            self.row_hdr_idx.orthogonal = None
            self.row_hdr_idx.vista = None
            self.col_hdr_idx = self.cubo.lista_guias[col]['dir_row']
            self.col_hdr_idx.orthogonal = None
            self.col_hdr_idx.vista = None
            self._setDataMatrix()
            
    def getAttributes(self):
        defVista = [self.row_id,self.col_id,self.agregado,self.campo ]

        atrVista = {
            'filtro': self.filtro,
            'totalizado':self.totalizado,
            'stats':self.stats,
            'force' :None,
            'cartesian':self.cartesian
            }
        return defVista,atrVista
        
    def  _setDateFilter(self):
        return self.cubo.setDateFilter()
     
    def __prepareJoin(self,joins,baseRef,name=None):
        if isinstance(baseRef,(list,tuple)):
            if isinstance(baseRef[0],(list,tuple)):
                baseTable = baseRef[0][0]
            else:
                baseTable = baseRef[0]
        else:
            baseTable = baseRef
            
        resultado = []
        for idx,entrada in enumerate(joins):
            if len(entrada) == 0:
                continue
            join_entrada = dict()
            join_entrada['join_modifier']='LEFT'
            if idx < len(joins) -1 or name is None:
                join_entrada['table'] = entrada.get('table')
            else:
                #What if it has prefix ¿?
                join_entrada['table'] ='{} AS {}'.format(entrada.get('table'),name)
            join_entrada['join_filter'] = entrada.get('filter')
            join_entrada['join_clause'] = []
            if idx == 0:
                join_entrada['rtable'] =baseTable

            for clausula in entrada['clause']:
                #TODO solo admite campos elementales en la clausula, 
                base_elem = clausula.get('base_elem')
                rel_elem = clausula.get('rel_elem')
                entradilla = (rel_elem,clausula.get('condition','='),base_elem)
                join_entrada['join_clause'].append(entradilla)
            resultado.append(join_entrada)
            #pprint(resultado)
        return resultado

    def  _setDataMatrix(self):
        """
        __setDateFilter
        __prepareJoin
        """
        #TODO clarificar el codigo
        basePfx = 'base'
        baseTable =self.cubo.definition['table'] 
        #REFINE solo esperamos un campo de datos. Hay que generalizarlo
        self.array = []
        sqlDef = dict()
        #sqlDef['select_modifier']=None
        sqlDef['tables']=[ [baseTable,basePfx],]
        sqlDef['base_filter']=mergeString(self.filtro,self.cubo.definition.get('base filter',''),'AND')
        sqlDef['where'] = []
        sqlDef['where'] += self._setDateFilter()
        ## si no copio tengo sorpresas
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
                """
                #Garantizar que la optimización no se lleva el prefijo por delante
                """
                tmpLinks = []
                if row['linkvia']:
                    pfx = 'r{}_{}'.format(x,y)
                    tmpLinks += self.__prepareJoin(row['linkvia'],sqlDef['tables'],'r{}_{}'.format(x,y))
                    trow = setPrefix(row['elems'],row['linkvia'][-1]['table'],pfx)
                    #trow = list(map(lambda i:setPrefix(i,row['linkvia'][-1]['table'],pfx),row['elems']))
                else:
                    trow = row['elems'][:]
                if col['linkvia']:
                    pfx  ='c{}_{}'.format(x,y)
                    tmpLinks += self.__prepareJoin(col['linkvia'],sqlDef['tables'],'c{}_{}'.format(x,y))
                    tcol = setPrefix(col['elems'],col['linkvia'][-1]['table'],pfx)
                    #tcol = list(map(lambda i:setPrefix(i,col['linkvia'][-1]['table'],pfx),col['elems']))
                else:
                    tcol = col['elems'][:]
                sqlDef['join'] = tmpLinks
                
                #trow = row['elems'][:]
                #tcol = col['elems'][:]
                if self.totalizado: #and x != 0:
                    try:
                        pos = trow.index("'//'")
                        del trow[pos]
                    except ValueError:
                        pass
                sqlDef['group'] = trow + tcol
                if self.totalizado:
                    rowFields =["'//'",] + trow 
                    numRowElems = len(rowFields)
                    colFields = tcol
                    numColElems = len(colFields)
                    sqlDef['fields'] = rowFields + colFields + [(self.campo,self.agregado)]
                else:
                    sqlDef['fields'] =sqlDef['group']  + [(self.campo,self.agregado)]
                    rowFields = trow
                    numRowElems = len(rowFields)
                    colFields = tcol
                    numColElems = len(colFields)
                                    
                sqlDef['order'] = [ str(x + 1) for x in range(len(sqlDef['group']))]
                sqlDef['driver'] = self.cubo.dbdriver
                sqlDef = setPrefix(sqlDef,baseTable,basePfx,excludeDict=('tables','table','ltable'))
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
            
    
    def __setAndBackup(self,item,idx,data):
        """
        Internal function. In fact should be decoupled from the instance
        Sets the column _idx_ of the _item_ with _data_, and performs an initial backup
        """
        item.setColumn(idx,data,REF)
        cell = item.getColumn(idx)
        cell.setBackup()
        
    def __setTreeContext(self,rowTree,colTree):
        """
        Internal function. In fact should be decoupled from the instance
        Sets tree.colTreeIndex
        """
        rowTree.vista = self
        rowTree.coordinates = (1,0)
        colTree.vista = self
        colTree.coordinates = (1,0)
        rowTree.orthogonal = colTree
        colTree.orthogonal = rowTree
        return None
        
        
    def newTreeLoad(self):
        self.__setTreeContext(self.row_hdr_idx,self.col_hdr_idx)
        self.row_hdr_idx.clearData()
        self.col_hdr_idx.clearData()

        rowdict = self.row_hdr_idx.asDict()
        coldict = self.col_hdr_idx.asDict()
        for record in self.array:
            rownr = rowdict[record[0].getFullKey()]['idx'] + 1
            colnr = coldict[record[1].getFullKey()]['idx'] + 1
            tupla= self.__newColumn(rownr,colnr,record)
            for entry in tupla:
                entry.setBackup()

    def __newColumn(self,row,col,data):
        retorno = []
        for dim,tree in enumerate((self.row_hdr_idx,self.col_hdr_idx)):
            rowparent = data[dim].parent()
            if not rowparent:
                rowparent=tree.invisibleRootItem()
            rownr = data[dim].row()
            colItem = GuideItem(data)
            if dim == 0:
                colnr = col
            elif dim == 1:
                colnr = row
            rowparent.setChild(rownr,colnr,colItem)
            retorno.append(colItem)
        return retorno            
    
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
    
    def Tree2Array(self):
        """
        TODO document
        """
        maxCols = self.col_hdr_idx.numRecords()
        result= []
        for row in self.row_hdr_idx.traverse():
            pl = row.getPayload()
            if len(pl) < maxCols:
                pl += [ None for k in range(maxCols - len(pl)) ]
            result.append(pl)
        return result
 
    def Tree2ArrayFiltered(self,filterrow=lambda x:True,filtercol=lambda x:True):
        """
        TODO document
        """
        coldict=self.col_hdr_idx.asDictFilter(filtercol)
        rowdict=self.row_hdr_idx.asDictFilter(filterrow)
        result = [ [ None for j in range(len(coldict)) ] for i in range(len(rowdict)) ]
        maxCols = self.col_hdr_idx.numRecords()
        for row in self.row_hdr_idx.traverse():
            if row.getFullKey() in rowdict:
                r= rowdict[row.getFullKey()]['idx']
                pl = row.getPayload()
                if len(pl) < maxCols:
                    pl += [ None for k in range(maxCols - len(pl)) ]
 
                for col in coldict:
                    c = coldict[col]['idx']
                    co = coldict[col]['oidx']
                    result[r][c]=pl[co]

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
        #self.newTreeLoad()

    def __getExportData(self,parms,selArea=None):
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
        if scope == 'visible':
            filterRow = lambda x,y=self.dim_row,z=pfilterRow,k='row',l=selArea: exportVisibleFilter(x,y,z,dir=k,view=l)
            filterCol     = lambda x,y=self.dim_col,z=pfilterCol,k='col',l=selArea: exportVisibleFilter(x,y,z,dir=k,view=l)

        else:
            filterRow = lambda x,y=self.dim_row,z=pfilterRow: exportFilter(x,y,z)
            filterCol     = lambda x,y=self.dim_col,z=pfilterCol: exportFilter(x,y,z)
        row_sparse = pfilterRow.get('Sparse',True)
        col_sparse = pfilterCol.get('Sparse',True)
        
        #translated = parms.get('NumFormat',False)
        numFmt = parms.get('NumFormat',False)
        decChar = parms.get('csvProp',{}).get('decChar','.')
 
        # si no esta ya creados los row_hdr_idx con datos (lo que significa ortogonal) ejecuto desde array
        # si ya lo estan desde el arbol (mas eficiente y tiene datos modificados)
        if self.row_hdr_idx.orthogonal is None:
            tmpArray = self.toArrayFilter(filterRow,filterCol)
        else:
            tmpArray = self.Tree2ArrayFiltered(filterRow,filterCol)
        rows = self.row_hdr_idx.asHdrFilter(filterRow, sparse=row_sparse,format='array') #no puedo usar offset
        cols = self.col_hdr_idx.asHdrFilter(filterCol,sparse=col_sparse,format='array')
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
         
        ctable,dim_row,dim_col = self.__getExportData(parms,selArea)
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
    
    def sinAgregado(self,dim):
        """
        TODO add to doc
        devuelve triplas como agrega (v. infra) pero sin datos
        """
        vector = []
        if dim == 'row':
            tree = self.row_hdr_idx
        elif dim == 'col':
            tree = self.col_hdr_idx

        for elem in tree.traverse():

            vector.append([elem.data(Qt.DisplayRole),
                           elem.data(Qt.UserRole +1),
                           None
                        ])
        return vector

    def agrega(self,dim,list_func):
        """
        TODO add to doc
        Permite obtener agregados sobre filas y columnas
        
        *Input parms
            * __dim__ (row/col) which dim is to be used as guide
            * __list_func__ a function which admit a list as parameter
            
        * Returns a list with three components each
            * display name of element 
            * key name of element
            * result of function for this element 
        """
        from PyQt5.QtCore import Qt
        from base.tree import LEAF

        vector = []
        if dim == 'row':
            tree = self.row_hdr_idx
            prefilter =  tree.orthogonal.asDictFilter(lambda x:x.type() == LEAF)
            filtro = sorted( [ prefilter[entry]['oidx'] for entry in prefilter ])
            for elem in tree.traverse():
                lista = list(filter(None,elem.getPayloadFiltered(filtro)))
                vector.append([elem.data(Qt.DisplayRole),
                            elem.data(Qt.UserRole +1),
                            list_func(lista)
                            ])
        elif dim == 'col':
            tabla = self.Tree2ArrayFiltered(filterrow=lambda x:x.type() == LEAF)
            idx=0
            tree = self.col_hdr_idx
            for elem in tree.traverse():
                lista = list(filter(None,[ linea[idx] for linea in tabla ]))
                vector.append([elem.data(Qt.DisplayRole),
                            elem.data(Qt.UserRole +1),
                            list_func(lista)
                            ])
                idx +=1
        return vector

    def agregaPct(self,dim):
        """
        TODO add to doc
        variante de agrega que devuelve el porcentaje del total por dumension
        """
        vector = self.agrega(dim,sum)
        total = sum([v[2] for v in vector if v[2] is not None])
        for k,entry in enumerate(vector):
            vector[k][2] = vector[k][2] *100./ total
        return vector
# monkeypatch
Vista.toTree = Vista.newTreeLoad
Vista.toNewTree = Vista.newTreeLoad
Vista.toTree2D = Vista.newTreeLoad
Vista.toNewTree2D = Vista.newTreeLoad

from support.util.decorators import stopwatch
@stopwatch
def createVista(cubo,x,y):
    vista = Vista(cubo,x,y,'sum',cubo.lista_campos[0],totalizado=True)
    vista.toNewTree2D()
    print(vista.row_hdr_idx.numRecords(),'X',vista.col_hdr_idx.numRecords())
    

    
def bugFecha():
    from support.util.jsonmgr import load_cubo

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
    from support.util.jsonmgr import load_cubo

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
    from support.util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    parms = { 'content':'full','totals':True}
    #pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
    parms['content']='branch'
    parms['totals']=False
    pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
  
  
def checkFilterDerived():
    from support.util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    parms = { 'content':'full','totals':True}
    #pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
    parms['content']='branch'
    parms['totals']=False
    pprint(vista.row_hdr_idx.asHdrFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
    pprint(vista.row_hdr_idx.asDictFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z)))
    filterArray(vista,parms)
    print('Ahora el nuevo\n')
    vista.toNewTree2D()
    filterTree(vista,parms)


@stopwatch
def filterArray(vista,parms):
    a1 = vista.toArrayFilter(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z),lambda x:True)
@stopwatch
def filterTree(vista,parms):
    a2 = vista.Tree2ArrayFiltered(lambda x,y=vista.dim_row,z=parms: exportFilter(x,y,z),lambda x:True)  
    
def checkArrays():
    from support.util.jsonmgr import load_cubo

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
    from support.util.jsonmgr import load_cubo

    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    pprint(vista.row_hdr_idx.asHdrFilter(lambda x:x.type() in (BRANCH, LEAF) ))
    
def getHeaders(**parms):
    from support.util.jsonmgr import load_cubo

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
    from support.util.jsonmgr import load_cubo

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
    from support.util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
    #vista.toNewTree()
    export_parms = {'NumFormat':True,'csvProp':{'decChar':','}}
    export_parms['file'] = 'ejemplo.dat'
    vista.export(export_parms)
    vista.toNewTree2D()
    export_parms['file'] = 'ejemplo1.dat'
    vista.export(export_parms)

def testTree():
    from support.util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
    vista.toTree2D()
    agay = vista.Tree2Array()
    for lin in agay:
        print(len(agay),':',lin)
    #for item in vista.row_hdr_idx.traverse():
        #print(item.simplifyHierarchical())
        
def testTraspose():
    from support.util.jsonmgr import load_cubo
    mis_cubos = load_cubo()
    cubo = Cubo(mis_cubos["datos light"])

    vista = Vista(cubo,'geo','partidos importantes','sum','votes_presential',totalizado=True)
    vista.toTree2D()
    vista.traspose()
    print(vista.col_hdr_idx.asHdr())
    for item in vista.row_hdr_idx.traverse():
        print(item.getPayload())

def experimental():
    from support.util.jsonmgr import load_cubo
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
    checkFilterDerived()
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
