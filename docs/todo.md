# ToDo list

## short term TODO list (2016)

* __DONE__ Python 3 compatible. (29/3/16)
* __DONE__ PyQt 5 works now as it worked with 4 (29/3/16)
* __DONE__. New test database.  (Sqlite) (2/4/16)
   * __DONE__ Date Handling codepaths tested (2/4/16)

* _WIP_ Code refactoring for clarity
  * _DONE_ data access layer isolation (2/4/16)
  * _DONE_ heavy simplification of core codepaths, and several internal structures.(6/4/16)
  *  handling of date indexes. Code is handicrafted and full of 's..t'. Integration of dateutil would solve a lot
  of problems, but add a new dependency
  * Adapt GUI to new internal structures
  * name of elements in hierarchy YML
  
* New use cases
  * basic source a query instead of a table
  * post filter row/columns
  * more than one measure
 
* bugs
  * __DONE__ Kdevelop editor defaults is undermining Py 3 compatibility. Need to think about it (just better parametrization)
  * fivepoints metric (?)

  * __DONE__ in guides allow blank filter
 
* Performance
  * _HP_ municipio as guide performance is a horror
  
* Behaviour
  * complex keying in guides
  * collapsed hierarchy as default
  * Ability of expand only a level entry
  * _HP_ allow to skip entries


* Other output formats besides GUI
    * JSON
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

* GUI to generate definitions file
 
* __EXPERIMENTAL__: use SqlAlchemy as data background, so dependencies on PyQt would only be on the presentation level
    * Date Management into alchemy
    * Cube/Rollp
 
* __EXPERIMENTAL__: Substitute PySlide for PyQt (licensing issues)

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider
