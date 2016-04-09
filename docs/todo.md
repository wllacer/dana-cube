# ToDo list

## short term TODO list (2016)

* __DONE__ Python 3 compatible. (29/3/16)
* __DONE__ PyQt 5 works now as it worked with 4 (29/3/16)
* __DONE__. New test database.  (Sqlite) (2/4/16)
   * __DONE__ Date Handling codepaths tested (2/4/16)

* _WIP_ Code refactoring for clarity
  * _DONE_ data access layer isolation (2/4/16)
  * _DONE_ heavy simplification of core codepaths, and several internal structures.(6/4/16)
  * _DONE_ handling of date indexes. Code is handicrafted and full of 's..t'. Integration of dateutil would solve a lot
  of problems, but add a new dependency
  * _DONE_ Adapt GUI to new internal structures
  * name of elements in hierarchy YML
  
* New use cases
  * basic source a query instead of a table
  * post filter row/columns
  * more than one measure
  * function recode
 
* bugs
  * __DONE__ Kdevelop editor defaults is undermining Py 3 compatibility. Need to think about it (just better parametrization)
  * fivepoints metric (?)
  * _WIP_ Filters in guides pose some functional problems

  * __DONE__ in guides allow blank filter
 
* Performance
  * _HP_ municipio as guide performance is a horror
  
* Behaviour
  * complex keying in guides
  * _WIP_ collapsed hierarchy as default. Define ways of opening it 
  * _WIP_ Open maximized
  * Ability of expand only an entry
  * Hierarchical dates
  * _DONE_ allow to skip entries. I skip entries by default
  *


* Other output formats 
    * JSON
    * CSV
    * Raw Array
    * HTML table
    
* SQL error handling

* Database testing in other environmentes. First 3 are available to me
    * MySQL/ MariaDB
    * PostGreSQL
    * DB2
    * Oracle  (not available locally)
    * SQLServer (not available locally)

* Use of CUBE / ROLLUP sintax where available

* __WIP__Packaging
    * Configuration management

* __WIP__ GUI 
    * GUI refactoring based on Model-View
    * GUI for definition   (__HP__ showstopper for release)
 
* __EXPERIMENTAL__: use SqlAlchemy as data background, so dependencies on PyQt would only be on the presentation level
    * Date Management into alchemy
    * Cube/Rollp
 
* __EXPERIMENTAL__: Substitute PySlide for PyQt (licensing issues)

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

Lista de TODOs en el codigo a 7 de abril

core.py:           Esa idea es para poder tener campos parciales o derivados como guias TODO
core.py:          TODO fields son campos auxiliares a incluir en la query
core.py:          #TODO grouped by determina la jerarquia explicitamente.
core.py:        #TODO creo que fields sobra
core.py:           * cursor el resultado normalizado (con rellenos) y agreagado de la guia en todos sus niveles
core.py:           * des_row el array con la descripción  TODO es mejorable su proceso
core.py:           El comportamiento para guias de formato fecha es totalmente distinto del resto. TODO documentar proceso
core.py:        #TODO Mejorar los nombres de las fechas
core.py:        #TODO indices con campos elementales no son problema, pero no se si funciona con definiciones raras
core.py:        # TODO documentar y probablemente separar en funciones
core.py:    #TODO falta documentar
core.py:    #TODO falta implementar la five points metric
core.py:                #DONE rellenar sqlstring y lista de compra en cada caso
core.py:                    #DONE permitir en ciertas circunstancias que algunos registros se pierdan
core.py:           TODO puede simplificarse
core.py:           TODO documentar
core.py:           FIXME Funciona perfectamente con el ejemplo que uso, necesito explorar otras posibilidades de definicion
core.py:                    #FIXME asumo que solo existe un elemento origen en los campos fecha
core.py:                    #FIXME probablemente esta mal con descripciones de mas de un campo
core.py:         #TODO solo esperamos un campo de datos. Hay que generalizarlo
core.py:            #FIXME primera iteracion. Altamente ineficiente con indices chungos

datemgr.py:    #TODO formatos todavia usan %
datemgr.py:        #TODO este proceso solo funciona con dias, no con horas. es una limitacion conocida.
datemgr.py:        #TODO explorar la posibilidad de utilizar el paquete Dateutil 
datemgr.py:       TODO admite una leve posibilidad de mejora para excluir fechas imposibles
datemgr.py:       TODO esta clarisimo que ademas admite seria optimizacion
datemgr.py:        #FIXME tengo la impresion que es un poco lento
datemgr.py:    #FIXME no se procesa el zoom

danacube.pyw: # TODO ¿que pasa con las secuencias de escape?
danacube.pyw:         #TODO  falta el filtro
danacube.pyw: # FIXME LOW fivepointsmetric no definida. Suspendida de momento. No funciona como yo quiero
danacube.pyw:        #FIXME
danacube.pyw:                # FIXME fivepointsmetric

