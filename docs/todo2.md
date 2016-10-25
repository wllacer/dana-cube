# ToDo list
__Nota__  el anterior y mas detallado TODO list está como ![este fichero](docs/todo2.md "Title")

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
    
* Incluir vistas en el cubo (2º escalon)
* Incluir extraccion de datos en cubo e interfaz con MatPlotLib  (critica para usuarios pero no tecnicamente)
* Filtros de entrada en el cubo
* Parametrizar ficheros de configuracion
* Traduccion
* Finalizar la gestion CRUD de cubos
* Ocultar las claves en las cadenas importantes

## Annoyances

* Como hacer que los arboles no se cierren y abran aleatoriamente
* Mensajes de usuario en caso de error graficos (proseguir desde util.base_dialogs. No funciona de momento)
    ** Danacube
    ** Danabrowse y asoociados
       *** __DONE__ danabrowse
       *** __DONE__ datadict
       *** __DONE__ dicttree
    * tablebrowse
    * cubebrowse
    * core & default
* unificar su tratamiento
* uso de variables globales
* ¿que hago con los errores SQL ?

* SQL performance ¿?

## Pequeños TODO

* Sesiones salvables
* Repaso de bugs (iniciar en danabrowse -> cubebrowse -> danacube)
* Unficar el tratamiento de arboles en la medida de lo posible
* Unificar (y aumentar el uso de decoradores)
* Mejorar la IU de los widgets de defecto
    ** __DONE__ eliminar la cabecera en WPropertySheet
* Eliminar sinonimos de variables en inicializaciones (p.e en danacube y DataDict)
* Filtrado, al menos, en tablebrowse

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
* ![cube bugs]docs/cube_todo.txt


### DanaBrowse

* __DONE__ Desaparce el menu a ratos.  Tengo que definir el widget primero
* Long term : threads __WISH__ 
* Long term : varias pestañas __WISH__ 
* long term : query recursiva
* Long term : properties
* Long term : set descriptive y las acciones contextuales de FK's (problema es salvarlo entre sesiones)
* __DONE__  Que pasa cuando se sustitye una edicion de cubo sin salvar. lo capturamos antes
* __DONE__  ?revisar el efecto en cubo de salir directamente de danabrowse
* __DONE__ Contadores en tablas y campos


### DANACUBE

*  Grandes totales desordenados en el caso de ENUMS


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


* __EXPERIMENTAL__: __PASS__ Substitute PySide for PyQt (licensing issues) (but only Qt4.8)

* __EXPERIMENTAL__ : __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't
                    include bindings for QtSQL

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

* __EXPERIMENTAL__: Integration of [plotly](https://plot.ly/) as reporting tool

* __EXPERIMENTAL__: Use of Graphs ¿? either Qt internal, D3.js or plotly (matplotlib for sure)

