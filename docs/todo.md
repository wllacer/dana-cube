# ToDo list

## short term TODO list (2016)

* __DONE__ Python 3 compatible. (29/3/16)
* __DONE__ PyQt 5 works now as it worked with 4 (29/3/16)
* __DONE__. New test database.  (Sqlite) (2/4/16)
   * __DONE__ Date Handling codepaths tested (2/4/16)

* SQLA Browser
    * Falta casi todo
    * ¿Como representa SQLAlchemy las FK a otro esquema?. Mejor dicho se referred_schema tiene valor o no cuando ser trata
       del esquema de defecto? Asumiré que siempre tiene valor y si no hay nombre de esquema es que se trata del mismo esquema
    * Asociaciones con mas de un campo de enlace ¿Como las representa SQLA
    * ¿Como definir cosas no SQL? Por ejemplo
        * Claves, donde no existen
        * Campos descripcion
        * Asociaciones virtuales
        * Filtros, tanto en tabla como en asociacion
        
    * Menu -> Connexion -> New
        * En el caso de SQLite deberia llamarse a un buscador de ficheros
        * appendConnection 4 argumentos es excesivo. Revisar
        * Revisar la vida de las conexiones en datadict.conn[]
        * en modificar; ver por que falla updateModel con refresh. Restaurar en appendConnection el posicionado
        * _BUG_ refresh de conexion en mysqld (parada en bg) casca en connection.refresh (no detecta que la base de datos esta down
        * El cancel en (connection)->Edit provoca un refresco, pese a todo
        * __DONE__ (connection)->Connect. abenda exec_objct(updateModel). La reorganizacion no le ha ido bien
    
* _WIP_ Code refactoring for clarity
  *__DONE__ data access layer isolation (2/4/16)
  *__DONE__ heavy simplification of core codepaths, and several internal structures.(6/4/16)
  *__DONE__ handling of date indexes. I devolved to a simple structure, each date format must be defined explicitly
  *__DONE__ Adapt GUI to new internal structures
  * name of elements in hierarchy YML

* Now In Progres
  * __DONE__ Row functions. _WIP_ lack some further testing
        * Special cases await (election simulator)
        * function with parameters: 
               * one per column
               * one per row
               * kwarg list
        * _TODO_ fumctions and hidden columns
        * _TODO_ Provide a consistent API
  * Charting output (use of matplotlib (https://www.boxcontrol.net/embedding-matplotlib-plot-on-pyqt5-gui.html)
  * Export infraestructure
  * __DONE__ Grand Total (only row)
    * From cube  (__DONE__)
    * Calculated  
    * Presentation 
    * _HOLD_ functionally not its place (now in view should be in model)
  * Dynamic Filter
        * _WIP_ rough UI is in place (propertySheetEditor)

 
 
* Definition generation by application
  * __HOLD__ SQL pregeneration (only partially makes sense)
  
* New use cases
  * __HOLD__  _WIP_ diferent types of guides  (on hold till definition settles
  * General
    * Login screen for DB that need it
    * _WIP_ Favorites function (definitions in new configuration)
    * Preset time intervals as general option in cube (this,(N) period (today backwards),(N) last (not including))x(week,month,year)
    * basic source a query instead of a table
    * more than one measure
    * __DONE__ function: recode (partially solved with categories/ user functions)
    * Data export (see below)
    * include Time as valid format
    * __DONE__ programatically predesigned case
  * Presentation
    * Ability to handle collapse/expand on columns
    * Aditional info on double/right click (stats data | source data)
  * Configuration
    * create from directory entry
    * ready made entries
  * Context menu https://wiki.python.org/moin/PyQt/Creating%20a%20context%20menu%20for%20a%20tree%20view
  * __HOLD__ (configuration) Preset time intervals as general option in cube (this,(N) period (today backwards),(N) last (not including))x(week,month,year) 
  * Traspose on actual data not view base data
  * Replayable log (w || w&o parameters ?)

* bugs
  * __DONE__ Kdevelop editor defaults is undermining Py 3 compatibility. Need to think about it (just better parametrization)
  * __DONE__ fivepoints metric 
  * Normalize definition.prod.elem as list
  * _WIP_ Filters in guides pose some functional problems
  * Dates as guides generate a lot of invalid dates (out of range, inexistent)
  * Dates as headers must be reformated
  * Integration of dates and categories in hierarchies (casi irresoluble, penaliza gravemente el rendimiento)
  * KABOOM on cube change -> cancel
  * tamaño de algun elemento de la lista
  * Alchemy no carga en Python3
  * Cabeceras de columnas con GRAND_TOTAL one off
  * en el WPowerWidget separar configuracion de datos para poder usar tuplas
  * RED NEGATIVE NUMBERS no funciona correctamente
  * en WPropertySheet que ocurre si context != data
  * Restore y estadísticas 
  * Ocultar celdas en WPowerWidget
  
  * __DONE__ in guides allow blank filter
 
* Performance
  * __DONE__ municipio as guide performance is a horror. _WIP_ I used lists for guide definition and retrieval. I've discovered that using dictionaries enhances performance over 10000 % (read __100 TIMES__ ), but i have to rewrite almost everything again
    used trees of dict, which also simplifies gui programming
  * A decision has to be made to load guides with the cube or specifically for each view
  
* Behaviour
  * complex keying in guides
  *__DONE__ collapsed hierarchy as default. Define ways of opening it 
  *__DONE__ Open maximized
  *__DONE__ Ability of expand only an entry
  * Hierarchical dates
  *__DONE__ allow to skip entries. I skip entries by default
  *


* Other output formats 
    * JSON
    * _WIP_ CSV  (? direct invocation of spreadsheet)
    *    Hidden/Shown rows/columns
    * __DONE__Raw Array. In fact almost new default
    * HTML table
    * Printing
    * ? graphical frontend as d3.js
    
* SQL error handling

* Database testing in other environmentes. First 3 are available to me
    * MySQL/ MariaDB
    * PostGreSQL
    * DB2
    * Oracle  (not available locally)
    * SQLServer (not available locally)

* Use of CUBE / ROLLUP sintax where available

* _WIP_ Packaging
    * Configuration management

* GUI 
    * __DONE__ GUI refactoring based on Model-View (excluding new functionality)
    * _WIP_ GUI for definition. Browse Ok Edit Haaard   (__HP__ showstopper for release)
 
* _WIP_ : use SqlAlchemy as data background, so dependencies on PyQt would only be on the presentation level
    * integration __DONE__. Now selectable by (internal) parameter. ¿Faster?
    * Date Management into alchemy
    * Cube/Rollp
 
* __EXPERIMENTAL__: __PASS__ Substitute PySlide for PyQt (licensing issues) (but only Qt4.8)

* __EXPERIMENTAL__ : __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't
                    include bindings for QtSQL

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

* __EXPERIMENTAL__: Integration of [plotly](https://plot.ly/) as reporting tool

* __EXPERIMENTAL__: Use of Graphs ¿? either Qt internal, D3.js or plotly (matplotlib for sure)

