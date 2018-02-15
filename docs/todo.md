# ToDo list


## Open Bugs

* BUG 0  __UPSTREAM__ __NOTIFY PENDING__ __BYPASSED__ 
    QStandardItem.appendColumn does NOT work. QStandardITem.appendColumns behaves erratically.
    Example at _./bug_0.py_
    
* BUG 1
    If any of the Items has a blank key (''), it is positioned in different places if it's row or column, and destroys the array
    Example.  at the _datos light_ cube, at the _geo_ or _region_ guide, thre is an entry _España_ which has this property . Just try to traspose it
    
*  BUG 2 __PRELIMINAR__ __UPSTREAM (?)__
    An addTab makes all tab headers the same

## Database backends

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
__WIP__

    * Configuration management


## Needed Enhancements

* Display of date fields

## Info

### Adaptacion a un servidor concreto

* Funciones de fecha y hora (se supone que en datemgr)
   strftime(fmt,var) --> MYSQL DATE_FORMAT(var,fmt)
                         PG    to_char(var,fmt)| extract(fmt from var)
                         Ora   to_char
                         SyS   datepart (!!!)
* Nombre de driver (buscar #DRIVERNAME) y (acceslayer.driver2alch)
* Ojo que no todos escupen los mismos errores



## Wishlist

* Use of CUBE / ROLLUP sintax where available

* __HOLD__ Use [qtpy](https://pypi.python.org/pypi/QtPy) as a wrapper of the various qt APIs. Doesn't include bindings for QtSQL but is no showstopper anymore

* Integration with [pandas](http://pandas.pydata.org/) as data provider

* Integration with [pandas](http://pandas.pydata.org/) as data provider

* Integration with [Orange3 project](https://github.com/biolab/orange3) as data provider

* Integration with Django (use django as data source, core as django tool)


