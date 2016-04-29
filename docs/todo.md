# ToDo list

## short term TODO list (2016)

* __DONE__ Python 3 compatible. (29/3/16)
* __DONE__ PyQt 5 works now as it worked with 4 (29/3/16)
* __DONE__. New test database.  (Sqlite) (2/4/16)
   * __DONE__ Date Handling codepaths tested (2/4/16)

* _WIP_ Code refactoring for clarity
  *__DONE__ data access layer isolation (2/4/16)
  *__DONE__ heavy simplification of core codepaths, and several internal structures.(6/4/16)
  *__DONE__ handling of date indexes. Code is handicrafted and full of 's..t'. Integration of dateutil would solve a lot
  of problems, but add a new dependency
  *__DONE__ Adapt GUI to new internal structures
  * name of elements in hierarchy YML
  
* New use cases
  * _WIP_ diferent types of guides
  * General
    * Login screen for DB that need it
    * Favorites function
    * Preset time intervals as general option in cube (this,(N) period (today backwards),(N) last (not including))x(week,month,year)
    * basic source a query instead of a table
    * more than one measure
    * function: recode (partially solved with categories)
    * Data export (see below)
  * Presentation
    * Ability to handle collapse/expand on columns
    * Data filtering (pre / post)
    * Aditional info on double/right click (stats data | source data)
* bugs
  * __DONE__ Kdevelop editor defaults is undermining Py 3 compatibility. Need to think about it (just better parametrization)
  * __DONE__ fivepoints metric 
  * _WIP_ Filters in guides pose some functional problems
  * Dates as headers must be reformated
  * Integration of dates and categories in hierarchies

  * __DONE__ in guides allow blank filter
 
* Performance
  * __DONE__ municipio as guide performance is a horror. _WIP_ I used lists for guide definition and retrieval. I've discovered
    that using dictionaries enhances performance over 10000 % (read __100 TIMES__ ), but i have to rewrite almost everything again
    used trees of dict, which also simplifies gui programming
  
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
    * _WIP_ CSV
    * __DONE__Raw Array. In fact almost new device
    * HTML table
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

* _WIP_  GUI 
    * __DONE__ GUI refactoring based on Model-View (excluding new functionality)
    * GUI for definition   (__HP__ showstopper for release)
 
* _WIP_ : use SqlAlchemy as data background, so dependencies on PyQt would only be on the presentation level
    * integration __DONE__. Now selectable by (internal) parameter. ¿Faster?
    * Date Management into alchemy
    * Cube/Rollp
 
* __EXPERIMENTAL__: Substitute PySlide for PyQt (licensing issues)

* __EXPERIMENTAL__: Definition language compatible to CUBES (?)

* __EXPERIMENTAL__: Integration with [pandas](http://pandas.pydata.org/) as data provider

* __EXPERIMENTAL__: Integration with Django (use django as data source, core as django tool)

* __EXPERIMENTAL__: Integration of [plotly](https://plot.ly/) as reporting tool

