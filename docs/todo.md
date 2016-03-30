# ToDo list

## short term TODO list (2016)

* __DONE__ Python 3 compatible. (29/3/16)
* __DONE__ PyQt 5 works now as it worked with 4 (29/3/16)
* __WIP__. New test database. Minimally available. Dates missing (Sqlite) (30/3/16)

* _WIP_ Code refactoring for clarity
  * _WIP_ data access layer isolation
  * _HP_ name of elements in hierarchy YML
  
* New use cases
  * basic source a query instead of a table
  * post filter row/columns
  * more than one measure
 
* bugs
  * fivepoints metric

  * __DONE__ in guides allow blank filter
 
* Performance
  * _HP_ municipio as guide performance is a horror
  
* Behaviour
  * complex keying in guides
  * collapsed hierarchy as default
  * Ability of expand only a level entry
  * _HP_ allow to skip entries


* SQL error handling

* Database testing in other environmentes. First 3 are available to me
    * MySQL/ MariaDB
    * PostGreSQL
    * DB2
    * Oracle  (not available locally)
    * SQLServer (not available locally)

* Use of CUBE / ROLLUP sintax where available

* Packaging
 
* __EXPERIMENTAL__: use SqlAlchemy as data background, so dependencies on PyQt would only be on the presentation level
    * Date Management into alchemy
    * Cube/Rollp
 
* __EXPERIMENTAL__: Substitute PySlide for PyQt (licensing issues)

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)
