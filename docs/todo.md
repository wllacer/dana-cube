# ToDo list


## Open Bugs

Serious errors which are either upstream or we haven't still found a solution

* BUG 0  __UPSTREAM__ __QT__ __NOTIFY PENDING__ __BYPASSED__ 
    QStandardItem.insertColumn does NOT work. QStandardITem.insertColumns behaves erratically.
    Example at _./bug_0.py_
    
* BUG 1  __UPSTREAM__ __Not verified in current implementation__
    If any of the Items has a blank key (''), it is positioned in different places if it's row or column, and destroys the array
    Example.  at the _datos light_ cube, at the _geo_ or _region_ guide, thre is an entry _España_ which has this property . Just try to traspose it
    
*  BUG 2 __SOLVED__
    An addTab makes all tab headers the same. Not upstream as far as i can tell

*  BUG 3. __UPSTREAM__ __SQLITE__ __STUDY PENDING__ __BYPASSED__
    'Datos light's grandBrowse gets into inacceptable perfomance penalites with more than 6 joins (??) or two quite similar but distinct joins .  Further study needed
    
*   BUG 4. 
    setEditTrigger with various tabs seems not to work correctly. __SOLVED__Nor can i change menu text directly (see user function menu handling)
    
*   __UPSTREAM__ __STUDY PENDING__ __BYPASSED__ QStandardItem(*args) bombs system if args[0] is int and big (some millions, still not out)

*  BUG 5  __CLOSED__
    query_constructor has troubles handling file prefixes, esp with joins. and if both guides are "joined". 
    Actual implementation has troubles only with a few corner cases (pure link vias with more than one field to group, and only if not fully qualified), which can be bypassed with the use of domains.
    A correct general solution has been found, and was pretty simple
    
* BUG6  __CLOSED__ 
    guides with more than one field as elems might not behave properly.
    Significative problem for those DB's which don't use surrogate keys but compound ones.
    Don't know if my solution (catenate the fields)  is to everybody's taste. Presentationwise is the only choice, but i have doubts about performance during group operations on large tables (will indexes be used ¿?)

* BUG7 __CLOSED__ __DB BACKEND__
    In certain cases (f.i. _enums in PgSQL_ external order of the db. column (the value shown) is not the same for which the DB _ORDER  BY_ uses (the internal numeric value of the enum). Dana coding expects both to be the same and messes results acordingly. We have tried to solve it in a general way, without a serious performance penality (see. @base.core.createProdModel for the solution and @base.tree the *Search routines for performance issues)
    
## rough corners

Areas where the product __must__ be improved. They might not be errors but don't feel quite right

* __solved on main menus__ Menu keyboard shorcuts

* Menu internationalization

* __Solved__ Move user function list to a text file. Fist option is the config file. 

* __NOOP__  Date formatters need the config delimiter. For the time being, info will be split in access_layer and datemgr  definition of DB Drivers to a text file. Fist option is the config file

* __Solved__ Display of date fields. Delimiter is now a global setting; works as specified

* __Solved__  How to make a date filter in sqlite (whre the type does not exist) A bypass, you can edit the element in cubebrowse and will stick afterwards

* __Solved__ Don't allow in vista dialog to enter without selection of measures

* __Solved__ Current export implementation is fast, but does not take into account changes via danacube

* __Solved__ Restaurar valores originales no funciona ahora ¿?

* Windows integration ¿?

## Needed Enhancements

Thing which shall belong to the app and aren't there now

* Local filter at the view data (w/o round trip to the DB)
* __solved__ A different filter dialog in which the user selects which fields to append
* __solved__ (at least on paper) Dynamic reloading of user functions, and locating them OUTSIDE the python tree
* Move default definition to the same place as the user function definition tree
* __solved__ Performance enhacements when a guide includes categories and dates not in the first prod rule



## Wishlist

Things which would be a welcome addition to the application

* Use of CUBE / ROLLUP sintax where available

* __DONE__ Add Column/Row into view. Plus initial loading

* __NOOP__ Use of importlib finder mechanism instead of the crafted __init__.py file for user functions. 

* code a "create a plugin local directory"

* An specialized ComboBox for external/internal value lists. Same for WMultiBox. It's more or less solved but it is a hack

* Possibility of generating an independent matplotlib window for the graphs

* consistent error messaging

* Integration with [pandas](http://pandas.pydata.org/) as data provider. _Nothing done thus far_

* Integration with [Orange3 project](https://github.com/biolab/orange3) as data provider. 

* Integration with Django (use django as data source, core as django tool). _Nothing done thus far_

* __HOLD__ Use [PyQt5](https://pypi.python.org/pypi/PyQt5) as a wrapper of the various qt APIs. Doesn't include bindings for QtSQL, but that is no showstopper anymore

# Subsystems

## Admin 
Most of it is already in a new (and I hope better) implementation, but they still lack

### cubebrowse

* Guide subtype change
* __solved__ a general editor for categories & __solved__ case_sql
* __solved__ verify date filter 
* For reference guides
    * Document it
    * case with more than 2 levels. __solved__ but grouped by, can be a PITA
    * __solved__  categories and dates not on first level (and not too cpu consuming)
    * ref to complex links
* __solved__ No el add, sino el desplazamiento. en repeatable add debe dividirse en (insert after, insert before, append). General de editTree
* __solved__ Incluir llamada a la consulta de guia
* __solved__ Incluir llamada al grand total
* __solved__ Las fechas artificiales (trimestres, cuatrimestres, ...) como opciones de menu aqui y no en info2*
* Para sqlite que el selector de base de datos sea el selector de ficheros del sistema
* __solved__ Copy to other place. Falta el proceso de adaptacion de tablas
* __solved__ Restore

## Database backends

Everything related to the database backends

### Open Issues
* Database testing in other environmentes. First 3 are available to me
    * __DONE__ MySQL/ MariaDB
    * __DONE__ PostGreSQL   
    * DB2 (uninstalled)
    * __WIP__ Oracle. Issues detected
        * Extremely slow in my setup (with system)
        * What does it reads in danabrowse for a simple user? Fails with privileges
        * synonim handling
    * SQLServer (not available locally).
        * Date handling seems pretty unstandard and unfriendly ... will be hard work

* PostGreSQL
    * if a field is an enum they don't come orderer by text but internal and that destroys my algoritms. Seems hard to solve.
        * alt 1 Sort the cursor for the guide ...> might be a disaster for big cursors
        * alt 2 change the search algorithm. It's a servere performance penalty unless I find a way to catch the enums

* Use of CUBE / ROLLUP sintax where available

## Packaging

Everything related to the application packaging. Is an area still in the planning phase

    * Configuration management


## NoQT Core

* Is not sinchronized anymore. Needs quiet time at the main branch. Temporarily excluded


# Info

Every bit of technical info which might be useful for 3rd parties

## Adaptacion a un servidor concreto

* Funciones de fecha y hora (se supone que en datemgr)
   strftime(fmt,var) --> MYSQL DATE_FORMAT(var,fmt)
                         PG    to_char(var,fmt)| extract(fmt from var)
                         Ora   to_char
                         SyS   datepart (!!!)
* Nombre de driver (buscar #DRIVERNAME) y (acceslayer.driver2alch)
* Ojo que no todos escupen los mismos errores





