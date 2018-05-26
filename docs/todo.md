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
    query_constructor has torubles handling with file prefixes, esp with joins. and if both guides are "joined". 
    Actual implementation has troubles only with a few corner cases (pure link vias with more than one field to group, and only if not fully qualified), which can be bypassed with the use of domains.
    A correct general solution has been found, and was pretty simple
    
* BUG6  __CLOSED__ __WIP__
    guides with more than one field as elems might not behave properly.
    Significative problem for those DB's which don't use surrogate keys but compound ones. Don't know if my solution is to everybodies taste

## rough corners

Areas where the product __must__ be improved. They might not be errors but don't feel quite right

* Menu keyboard shorcuts

* Menu internationalization

* __Solved__ Move user function list to a text file. Fist option is the config file. 

* Move definition of DB Drivers to a text file. Fist option is the config file

* __Solved__ Display of date fields. Delimiter is now a global setting; works as specified

* How to make a date filter in sqlite (whre the type does not exist)

* __Solved__ Don't allow in vista dialog to enter without selection of measures

* __Solved__ Current export implementation is fast, but does not take into account changes via danacube

## Needed Enhancements

Thing which shall belong to the app and aren't there now

* Local filter at the view data (w/o round trip to the DB)
* A different filter dialog in which the user selects which fields to append
* Dynamic reloading of user functions, and locating them OUTSIDE the python tree
* Move default definition to the same place as the user function definition tree

## Wishlist

Things which would be a welcome addition to the application

* Use of CUBE / ROLLUP sintax where available

* Add Column/Row into view. Plus initial loading

* __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't include bindings for QtSQL, but that is no showstopper anymore

* Integration with [pandas](http://pandas.pydata.org/) as data provider

* Integration with [Orange3 project](https://github.com/biolab/orange3) as data provider

* Integration with Django (use django as data source, core as django tool)


# Subsystems

## Admin 
Most of it is already in a new (and I hope better) implementation, but they still lack
* Guide subtype change
* a general editor for categories & case_sql
* verify date filter 

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
    * SQLServer (not available locally)


* Use of CUBE / ROLLUP sintax where available

## Packaging

Everything related to the application packaging. Is an area still in the planning phase

    * Configuration management


## NoQT Core

* Is not sinchronized anymore. Needs quiet time at the main branch


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





