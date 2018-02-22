# ToDo list


## Open Bugs

Serious errors which are either upstream or we haven't still found a solution

* BUG 0  __UPSTREAM__ __NOTIFY PENDING__ __BYPASSED__ 
    QStandardItem.insertColumn does NOT work. QStandardITem.insertColumns behaves erratically.
    Example at _./bug_0.py_
    
* BUG 1
    If any of the Items has a blank key (''), it is positioned in different places if it's row or column, and destroys the array
    Example.  at the _datos light_ cube, at the _geo_ or _region_ guide, thre is an entry _España_ which has this property . Just try to traspose it
    
*  BUG 2 __SOLVED__
    An addTab makes all tab headers the same. Not upstream as far as i can tell

 
## rough corners

Areas where the product __must__ be improved. They might not be errors but don't feel quite right

* Menu keyboard shorcuts

* Menu internationalization

* Move user function list to a text file. Fist option is the config file

* Display of date fields

* How to make a date filter in sqlite (whre the type does not exist)

## Needed Enhancements

Thing which shall belong to the app and aren't there now

* Local filter at the view data (w/o round trip to the DB)
* A different filter dialog in which the user selects which fields to append


## Wishlist

Things which would be a welcome addition to the application

* Use of CUBE / ROLLUP sintax where available

* __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't include bindings for QtSQL, but that is no showstopper anymore

* Integration with [pandas](http://pandas.pydata.org/) as data provider

* Integration with [Orange3 project](https://github.com/biolab/orange3) as data provider

* Integration with Django (use django as data source, core as django tool)


# Subsystems

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





