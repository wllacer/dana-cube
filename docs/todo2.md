
# ToDo list
__Nota__  el anterior y mas detallado TODO list está como ![este fichero](docs/todo2.md "Title")

## TODOLIST
*  querybrowser limitado
*  unificar QStandardItemModels (en CubeTree, TableBrowse y DictTree)
## nuevo wizard guia
*  __DONE__ añadir entradas en categorias
*  __DONE__ no salva categoria ??
*  plantearnos el filtro __DONE__ y el grouped by
*  __DONE__ algun sistema de comprobación que son correctas las definciones de guia
*  plantearse ocultar el dominio en las complejas
*  __DONE__ joe con los links
*  __DONE__ (Parcialmente desestimado) Comprobar los selectores de fechas un poco raros (cuatrimestres, etc, ...)

## catatonia
*  __BUG__crash con datos incompletos en definicion de vista. 
*  copiar guia de otro cuvbo
*  __DONE__ en cambio de fichero se me ha escapado uno en un filtro. fin de cadena cubeutil.changeTable

## Nueva base de datos electoral
*  Incluir FileSelector en conexiones (danabrowse) para sqlite
*  __NO REPRO PROV__ Generacion cubo en vista trae campos no existentes en la vista (SQLITE)
*  __3D PARTY__ problema en sqlite: no campos numericos para Fields (de hecho, campos sin tipo)

## Verificacion de los wizard
*  __PARTIAL__ change schema en conexion. NO se verifican la validez de los cambios. Caveat Emptor
*  COPY UP/DOWN de guia
*  retornar el cursor al elemento editado
*  s/fieldEditor/WMultiBox
*  __WIP__ la creacion "ex nihilo" de guia.(en general edicion completa de guia)
*  grouped by en domain. Grouped by sera tratado como dato interno ( Sum (prod[0:n-1].elem))
*  wzFieldList wGuideList no se usa.
*  __WIP__ ver comportamiento reglas enlazadas con paginas de detalle
*  prod de sin domain a domain ¿como?
*  unificar los traverse
*  __DONE__ uso inadecuado de acceso a campos en el cache

*  __DONE__ eliminar qsqlite como driver
*  __DONE__ normalizar uso de self.cache
*  __SOLVED__ ? Que tablas entran en el cache. Todas Como añadir tablas en el cache dinamicamento o entrar todo el esquema
*  __DONE__ no perder elementos auxiliares en link via
*  __DONE__ wzdomain no forma parte de las cadenas de produccion ya
*  __WON'T FIX__ en arrays de un solo elemento no presentarlo como un array (fields y elem).  rompe el caracter generico
*  __DONE__ __BUG__ date filter campos bloqueados no funciona
*  __DONE__ __BUG__ wzCategories. cierre
*  __DONE__ wzCategories. Huecos y borrado de lineas
*  __DONE__ Nombre == valor en la presentacion
*  __DONE__ salida de wzLink
*  __DONE__ Rename es errático
*  __WON'T FIX__ WzBaseFilter no activado. Debe hacerse directamente de DanaCube o edición libre
*  __DONE__ date filter con campos forzados (es decir no fechas). Para sqlite
*  __WONT'FIX__ creacion "ex nihilo" de cubo. los cubos deben crearse via Danabrowse o funcion de copia
*  __PARTIAL__ creadas en cubemgmt.cubeutil funcioes para cambiar esquemas y nombres de tabla. Dudas sobre como usarlo en el codigo. Cambio de fichero realizado (implica entre otras cosas anular la cache). Cambio de esquema en cambio de conexion

## Grandes TODO (para pasar de serie)

* __DONE__ Completar la distribucion de codigo sobre danabrowse (una vez hecha se taggea como version base )
   ** __DONE__ Cubebrowse convertido en widget
   ** __DONE__ Integracion en danabrowse
        *** __DONE__ as ventana independiente (no me interesa)
        *** __DONE__ Como widget
        *** __DONE__ Opcion de salvar 
        *** __DONE__ Splitter especifico
*__DONE__TAG
    ** __DONE__ documentacion elemental
    ** __DONE__ generar la version
    
* __DONE__ Incluir vistas en el cubo (2º escalon)

* __DONE__ Incluir extraccion de datos en cubo
* __NOW__ interfaz con MatPlotLib  (critica para usuarios pero no tecnicamente)
* __NOW__ Filtros de entrada en el cubo
    ** __DONE__ interfaz de usuario con guias
    ** __DONE__ Integracion en Danacube
    ** __DONE__ Serializacion (v.infra)
    ** reeditar filtro
* __NOW__ Filtros previos por tiempo ( campo + periodo (dia, ...). 
    ** __DONE__ Interfaz de usuario. __FALTA__ el caso especial que no existan campos fecha
    ** __DONE__ Integracion en Danacube. __FALTA__ Debe integrarse en cubebrowse, mejor
    ** __DONE__ Serializacion.
* __NOW__ Claves multicampo
* __DONE__ BUG Grandes totales desordenados.
    ** ENUMS (film cualquiera con rating)
    ** Primer caso. Es un off by one. -(datos light 6,0)En este caso es porque la primera columna es nula. Ademas hay un pequeño problema de calidad de datos, pero no parece ser de interes ahora
    ** Con fillGuias al inicializar el cubo, volver a ejecutar la vista genera otra entrada en los totale
* __NOW__ documentacion preliminar
* __NOW__ Como hacer que los arboles no se cierren y abran aleatoriamente
    * funciona salvo un problema en borrados

*  Terrible rendimiento (al menos en MySQL) en dictmgmt/dictree.getValueSpread() (select count(*) from (select distinct field from table) as base). Es una funcionalidad utilisima; ahora mismo la he desconectado
    * He modificado la query a select count(distinct campo) from file.  Parece mejorar algo el rendimiento
    * He desactivado de momento esto como opcion directa y lo sustituire por una accion indivudual sobre los campos

* Traduccion
* Finalizar la gestion CRUD de cubos
* Ocultar las claves en las cadenas importantes

## Pequeños TODO
 
* Sesiones salvables
* Repaso de bugs (iniciar en danabrowse -> cubebrowse -> danacube)
* Unficar el tratamiento de arboles en la medida de lo posible
* __DONE__ Unificar (y aumentar) el uso de decoradores
* Mejorar la IU de los widgets de defecto
    ** __DONE__ eliminar la cabecera en WPropertySheet
* Eliminar sinonimos de variables en inicializaciones (p.e en danacube y DataDict)
* __DONE__ Filtrado en tablebrowse
* __DONE__ Filtrado en DanaCube
* Parametrizar ficheros de configuracion
* Uso de formateo en tablebrowse y en danacube debe unificarse y flexibilizarse
* El sistema de generacion de query admite mejoras (limit) y falta comprobar con claves compuestas
* (CRASH) al consultar vista staff_list (falta un campo) --> errores de ejecucion SQL
* __DONE__ BUG cancelar wizard vacia datos en cubebrowse
* __DONE__ s/self.model/self.baseModel/g para evitar colisiones con la funcion .model() de las ItemViews
* Utilizacion de validadores en los campos de entrada.
* __DONE__ (performance) poder limitar la generacion del diccionario a tablas concretas relacionadas con una sola
    ** __DONE__ (BUG) cuando se elige nivel 0 falla la obtencion de FKS (obviamente). __PARCHE__
    ** __DONE__ (Limitacion) reservado a relaciones en el mismo esquema __TODO__
* DANACUBE. Salvar filtro de modo menos radical
* __HOLD__ DANACUBE  cargar de inicio mas cosas. Genera grandes totales raros

* __DONE__ Interfaz de usuario del filtro (simplemente cambiando QTextEdit por QLineEdit he conseguido lo que queria
* CRASH. danacube con 0 registros tras filtro
* __DONE__ Salvar defecto
* __DONE__ Incluir filtro en defaults
* __DONE__ Limpiar pantalla en cambio de cubo
* Crear una funcion TreeModel.clear(). puede simplificar cosas en cambios de cubo y vistas
* rango de fechas desde/hasta, directamente



## Annoyances

* en la verificacion de logicales tener en cuenta is null(is not null) -CubeCRUD y tablebrowse-

* Mensajes de usuario en caso de error graficos (proseguir desde util.base_dialogs. No funciona de momento)
    ** Danacube
    ** Danabrowse y asoociados
       *** __DONE__ danabrowse
       *** __DONE__ datadict
       *** __DONE__ dicttree
       *** Tengo que decidr que hacer en el caso de los mensajes algo superfluos en danacube.suprimidos por ahora. debe ser configurable
    * tablebrowse
    * cubebrowse
    * core & default
* unificar su tratamiento
* uso de variables globales
* ¿que hago con los errores SQL ?
* Renombrar conexiones en danabrowse
*¿Donde estan las columnas en Danabrowse?
* Mejorar la presentacion de las propiedades de la vista http://stackoverflow.com/questions/5631078/sqlalchemy-print-the-actual-query
* __DONE__ Me parece que la clave extrangera aparece dos veces en "Browse with fk". Confirmado
* SQL performance ¿? 
    ** __VIP__ perdida de rendimiento en DanaBrowse con la inclusion de contadores
    ** __DONE__ supresion de resizeToContent para mejorar -extraordinariamente- el rendimiento en tablas. Me obliga a poner cabeceras
* El diccionario es pasado entre danabrowse u tablebrowse demasiadas veces
* Color en mensajes de error
* Hay funciones en filterDlg que pueden reutilzarse

* __DONE__ NO me genera correctamente los arboles de FK
* __WIP__ Reescritura del wizard para usarlo mas facilmente
* Codigo para generar cubo necesita una iteración

* Danacube como widget

### CubeBrowse

* __DONE__ cubeBrowseWin  para general y local 
* __DONE__ Funcion para salvar / recuperar el cubo. No automático como hasta ahora.
    **    __DONE__ salva. Desactivada por el momento para evitar basura . s/DEVELOP en cubebrowse
    **    __DONE__ Opciones en interfaz de usuario
        *** __DONE__ Salvar
        *** __DONE__ Restaurar
* __WISH__ Salvar el fichero de configuración solo si se han producido cambios (no se si merece la pena) 
* __DONE__ Presentar en las guias de defecto el numero de valores distintos para la guia (hecho en DanaBrowse) 
* __DONE__ que los distintos atributos se presenten siempre en el mismo orden en un arbol del cubo, creo
* __DONE__ ¿Realmente necesito el diccionario completo en todos los casos?
* ![cube bugs]docs/cube_todo.txt
* (BUG) Borrar default no funciona 
* __DONE__ (BUG) source no esta especializado. Se me habia olvidado que ahora es domain
    ** __DONE__ Ser mas permisivo con atributos no especificados (ahora los guarda)
    ** En edicion contemplar caso que el atributo NO exista en el diccionario
* Problemas si no se especifica el esquema. probablemente deba incluir en la def. de la conexion el esquema de defecto.
* __DONE__ (BUG) problemas donde se define localContext
* __DONE__ (BUG) tratamiento de listas provocado por el cambio en el control de atributos


### DanaBrowse

* __DONE__ Desaparce el menu a ratos.  Tengo que definir el widget primero
* Long term : properties
* Long term : set descriptive y las acciones contextuales de FK's (problema es salvarlo entre sesiones)
* __DONE__  Que pasa cuando se sustitye una edicion de cubo sin salvar. lo capturamos antes
* __DONE__  ?revisar el efecto en cubo de salir directamente de danabrowse
* __DONE__ Contadores en tablas y campos
* Si cancelo al inicio casca 


### DANACUBE

* Juraria que habia implementado el ocultar columnas (a lo peor copiar de tablebrowse)
* Revisar la implementacion de las fechas (funciona, pero no se porqué)
* __DONE__ al fin fechas formateadas algo decentemente

 ### tablebrowse 
 
* Long term : threads __WISH__ 
* Long term : varias pestañas __WISH__ 
* long term : query recursiva
 * __WIP__Ordenar por columnas
    ** __DONE__ orden alfanumerico http://stackoverflow.com/questions/11938459/sorting-in-pyqt-tablewidget
    ** __DONE__ en tablebrowse
    ** __DONE__ en danabrowse
 __DONE__ Filtros
 __DONE__ Query libre (muy limitada como filtro)
 * __DONE__ Ocultar columnas
    ** __DONE__ en tablebrowse
 * __DONE__ Con cubebrowse como ejemplo separar widget y main window
* __DONE__ Formatos de columna en tablebrowse mas chachis. Pude ser una annoyance


 Mucho del código se puede sacar a una de las utilidades
 Controlar errores ejecucion SQL

# BUGS

## CubeBrowse

* __DONE__ Paso a cubebrowse abre otra vez el diccionario  (ojo) __BUG__
Con el debuger no pasa, pero aparentemente sí con el codigo normal
Solo ocurre en Python2 no en 3. (por cierto usar isinstance(x,basestring) )
s/type(/isinstance/
* danabrowse.pyw:334:            if type(item) == ConnectionTreeItem:
* datadict.py:64:            if type(item) != ConnectionTreeItem:
* datadict.py:75:            if type(item) != ConnectionTreeItem:
* datadict.py:191:                if type(item) != ConnectionTreeItem:
* datemgr.py:50:        if type(min_date) is datetime:
* datemgr.py:54:        if type(max_date) is datetime:
* dictTree.py:158:        if type(self) == ConnectionTreeItem :
* dictTree.py:160:        elif type(self) == SchemaTreeItem:
* dictTree.py:162:        elif type(self) == TableTreeItem :
* dictTree.py:176:        while item is not None and type(item) is not TreeModel:
* dictTree.py:215:        while item is not None and type(item) is not ConnectionTreeItem:
* dictTree.py:221:        while item is not None and type(item) is not SchemaTreeItem:
*dictTree.py:227:        while item is not None and type(item) is not TableTreeItem:
* dictTree.py:374:        if type(self.data()) is ConnectionTreeItem:
* tablebrowse.py:186:        if type(pdataDict) is DataDict:


* al intentar borrar entradas. es como si hubiera ido demasiado rapido. No reproduce por defecto
 File "/home/werner/projects/dana-cube.git/cubebrowse.py", line 269, in openContextMenu
    setContextMenu(item,menu,self)        
UnboundLocalError: local variable 'item' referenced before assignment

* __DONE__ El sistema de salvado se dispara si se activa una generacion despues de cerrada la primera


## DANABROWSE e hijos
Limpieza general
( - Ya superado
  + incluido,
  next -> siguiente iteracion,
  bypass -> comportamiento modificado para evitar el problema -pero no resuelto en sí
  NOOP   -> eso
  
next -> danabrowse.pyw:200:        #TODO variables asociadas del diccionario. Reevaluar al limpiar
+ danabrowse.pyw:276:            #TODO mensaje informativo
- danabrowse.pyw:299:    #TODO actualizar el arbol tras hacer la edicion   
hold -> danabrowse.pyw:395:            #TODO deberia verificar que se han cambiado los datos
- danabrowse.pyw:399:            #TODO modificar el arbol, al menos desde ahí
next -> danabrowse.pyw:39:       TODO unificar en un solo sitio
- danabrowse.pyw:90:       TODO faltan datos adicionales para cada item, otro widget, cfg del widget, formato de salida
- danabrowse.pyw:91:       FIXME los botones estan fatal colocados
- dictmgmt.datadict.py:109:    #TODO probablemente padre sea un parametro inncecesario
+ dictmgmt.datadict.py:128:            #TODO deberia ampliar la informacion de no conexion
+ dictmgmt.datadict.py:175:                ##TODO gestionar error de conexion no existente
next ->dictmgmt.datadict.py:44:        #FIXME eliminar parametros espureos
- dictmgmt.datadict.py:83:        definimos el modelo. Tengo que ejecutarlo cada vez que cambie la vista. TODO no he conseguido hacerlo dinamicamente
dictmgmt.dictTree.py:263:        #FIXME no podemos poner el icono de momento
- dictmgmt.dictTree.py:345:        ##TODO cambiar la columna 
bypass -> dictmgmt.dictTree.py:346:        #TODO de desconectada a conectada
- dictmgmt.dictTree.py:368:            #FIXME no podemos poner el icono de momento
dictmgmt.dictTree.py:379:            #TODO deberia verificar que de verdad lo esta
- dictmgmt.dictTree.py:419:        #FIXME no podemos poner el icono de momento
- dictmgmt.dictTree.py:448:        #FIXME no podemos poner el icono de momento
next -> dictmgmt.dictTree.py:579:        #FIXME ver si puede utilizarse nomenclatura fqn() aquí

# tablebrowse

NOOP -> tablebrowse.py:148:            #FIXME horrible la sentencia de abajo y consume demasiados recursos. Debo buscar una alternativa
tablebrowse.py:167:        #TODO variables asociadas del diccionario. Reevaluar al limpiar
NOOP -> tablebrowse.py:52:            #TODO seguro que puede pitonizarse
next ->tablebrowse.py:86:    TODO limit generico
next -> tablebrowse.py:87:    TODO relaciones con mas de un campo como enlace
next -> tablebrowse.py:91:    TODO generalizar :
- datalayer/access_layer.py:176:    ##TODO debería controlar los errores de conexion
- datalayer/access_layer.py:206:    #TODO ¿sera posible que Alch me devuelva directamente una lista? NO
next -> datalayer/access_layer.py:207:    #TODO buscar una alternativa mas potable para el limite
NOOP -> datalayer/access_layer.py:252:    #TODO include functions which depend on DB driver
(ELIMINADO) datalayer/directory.py:216:    getTableFields(conn,'votos_locales','default') #TODO deberia contemplarse
NOOP ->datalayer/query_constructor.py:377:      #FIXME no entiendo porque necesito renormalizar la cadena


* __EXPERIMENTAL__: __PASS__ Substitute PySide for PyQt (licensing issues) (but only Qt4.8)

* __EXPERIMENTAL__ : __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't
                    include bindings for QtSQL

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

* __EXPERIMENTAL__: Integration of [plotly](https://plot.ly/) as reporting tool

* __EXPERIMENTAL__: Use of Graphs ¿? either Qt internal, D3.js or plotly (matplotlib for sure)

