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
*TAG
    ** documentacion elemental
    ** generar la version
* Incluir vistas en el cubo (2º escalon)
* Incluir extraccion de datos en cubo e interfaz con MatPlotLib  (critica para usuarios pero no tecnicamente)
* Filtros de entrada en el cubo
* Parametrizar ficheros de configuracion
* Traduccion

## Pequeños TODO

* Sesiones salvables
* Finalizar la gestion CRUD de cubos
* Repaso de bugs (iniciar en danabrowse -> cubebrowse -> danacube)
* Ocultar las claves en las cadenas importantes

### CubeBrowse

* __DONE__ cubeBrowseWin  para general y local 
* __DONE__ Funcion para salvar / recuperar el cubo. No automático como hasta ahora.
    **    __DONE__ salva. Desactivada por el momento para evitar basura . s/DEVELOP en cubebrowse
    **    __DONE__ Opciones en interfaz de usuario
        *** __DONE__ Salvar
        *** __DONE__ Restaurar
* __WISH__ Salvar el fichero de configuración solo si se han producido cambios (no se si merece la pena) 
* __WISH__ Presentar en las guias de defecto el numero de valores distintos para la guia (o mejor en danabrowse ¿?) 
* __DONE__ que los distintos atributos se presenten siempre en el mismo orden en un arbol del cubo, creo
* ![cube bugs]docs/cube_todo.txt


### DanaBrowse

* __DONE__ Desaparce el menu a ratos.  Tengo que definir el widget primero
* Long term : threads __WISH__ 
* Long term : varias pestañas __WISH__ 
* __DONE__  Que pasa cuando se sustitye una edicion de cubo sin salvar. lo capturamos antes
* __DONE__  ?revisar el efecto en cubo de salir directamente de danabrowse


## Annoyances

* Como hacer que los arboles no se cierren y abran aleatoriamente
* Mensajes de usuario en caso de error graficos (proseguir desde util.base_dialogs. No funciona de momento)





* __EXPERIMENTAL__: __PASS__ Substitute PySide for PyQt (licensing issues) (but only Qt4.8)

* __EXPERIMENTAL__ : __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't
                    include bindings for QtSQL

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

* __EXPERIMENTAL__: Integration of [plotly](https://plot.ly/) as reporting tool

* __EXPERIMENTAL__: Use of Graphs ¿? either Qt internal, D3.js or plotly (matplotlib for sure)

