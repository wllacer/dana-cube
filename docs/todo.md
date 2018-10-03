# ToDo list


## Open Bugs

Serious errors which are either upstream or we haven't still found a solution

* BUG 0  __UPSTREAM__ __QTBUG-69387__ __BYPASSED__ 
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
    
 BUG8 __REOPENED__
    Bug will be kept open for a while, as i don't trust I got all the corner cases 
    Danacube trees are not exactly ordered as I expected.
    Reason 1:
        (sometimes they are inserted/expected by key others by value). Use of binary search produces strange results in clone tree, at least. 
        Solved Via commit __[master 144d08f]__ _Normalizar insercion con orden via API en guideItem.insertSorted_ Controlo exactamente que rol es criterio de ordenacion
    Reason 2
        There is a second source of this behaviour for DANACUBE used models: sortt at views sorts the underlying model, so the traverse method  does not return the same order. Usually this is not a problem but I've located (at least) following potentially incorrect behaviours:
        
    *   __SOLVED__ the guideItemModel methods pos2item item2pos are written on a (false) expectation of stability. Commit __[master a2678cf0]__ specializes both functions to serve both in static or dynamic situation. Dynamic demands a relatively expensive dictionary at the tree level
    
    *  __SOLVED__ Uses of pos2item item2pos: Use in hide/show as dynamic else -as of today-  static. 
    
    *  ~~sert/delete (column/row) after initial creation can be troublesome. ~~ The current mechanism @Danacube recalculates the array after every change of the tree definition
    
    *   binary search:
        * Has not a clear solution, if we still want to be performant. We create the trees ordered but TreeView action can modify them internaly, and binary searches will not work afterward
        Three styles for search: Binary Search (i.e. ordered), Unordered search using .match and unordered search by direct comparision.
        QAbstractItemModel.Match is an extremely bad performer in general.
        With few elements O(100) performance using unsorted algorithms is only slightly worse, but with big datasets performance for unsorted criteria is 3-5 times worse. 
        In the geo-detail sample (about 8000 entries in 3 levels)  creation of the tree becomes unbearable if we use unsorted algorithms (is expensive anyway), Therefore We have decided to keep the ordered asumption as default
        
        * In one particular instance "disordering" effects have been bypassed executing searchHierachicalUnsorted if element not found after a binary search (hiddenElemsMgr.switchVectorVisibility_ at DanaCube). While not a perfect solution seems to work for most cases.
        Performance tests at test_xx
    
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


* Windows integration 
    * __solved__ base.uf_handler 24 spliy libname (de / a \\)
    * __solved__ support.util.jsonmgr 126 de ~ a os.environ[HOMEPATH]
    
* __solved__ search hierachy not always work as expected (did not take into account variability in tree's life cicle)

## Needed Enhancements

Thing which shall belong to the app and aren't there now

* Local filter at the view data (w/o round trip to the DB)
* __solved__ A different filter dialog in which the user selects which fields to append
* __solved__ (at least on paper) Dynamic reloading of user functions, and locating them OUTSIDE the python tree
* Move default definition to the same place as the user function definition tree
* __solved__ Performance enhacements when a guide includes categories and dates not in the first prod rule
* __done__ in column fusion end with hiding the source columns
* __done__  Restaurar valores originales, debe incluir "desocultar"                                                                                                                                                                                          
* Unify cloneSubTree @GuideItemModel and @treeEditorUtil.  former is newer

Things to move ~~hidden~~/cartesian guide out of experimental

*  __solved__ _HiddenElems_ manage hierarchies, incl. hide/show branches/leaves @columns
* __solved__ _HiddenElems_ mass update
* __solved__ Filter hidden Elements in downloads (then put hidden out of experimental status)
* __solved__ hide sorted rows does not work (seems never to get the corresponding row id) have a look at _dnacube.hiddenElemsMgr.switchVectorVisibility_
* code,desc,columns simplify structure @core
* _cartesian_ date behaviour
* __solved__ graphics and hidden data 

* Substitute routines to get rowid/colid rownr/colnr for __getitem__ access. ~~And check correctness (rowid & colid are swapped now)~~

Graphic subsystem 

* __solved__ graphics and hierarchies. FInd a standard
* __solved__ graphic presentation Qt5 or independent, (or both)

## Wishlist

Things which would be a welcome addition to the application

* Use of CUBE / ROLLUP sintax where available

* __DONE__ Add Column/Row into view. Plus initial loading

* __NOOP__ Use of importlib finder mechanism instead of the crafted __init__.py file for user functions. 

* Trazability of user function calls at danacube

* code a "create a plugin local directory"

* An specialized ComboBox for external/internal value lists. Same for WMultiBox. It's more or less solved but it is a hack

* Possibility of generating an independent matplotlib window for the graphs

* consistent error messaging

* Integration with [pandas](http://pandas.pydata.org/) as data provider. _Nothing done thus far_

* Integration with [Orange3 project](https://github.com/biolab/orange3) as data provider. 

* Integration with Django (use django as data source, core as django tool). _Nothing done thus far_

* __HOLD__ Use [PyQt5](https://pypi.python.org/pypi/PyQt5) as a wrapper of the various qt APIs. Doesn't include bindings for QtSQL, but that is no showstopper anymore

# Subsystems

## New graphic

* __done__ multicharts.
    *  code clean up
    *  extent to other graphs if it has sense
* __done__ propagate on view changes..
    *  __done__ hide/show column
* __done__ hidden rows
* __done__ Internal changes (changed using NavigationTool)
    * Change chart type
    * Open mpl window
    * Basic export data
    * zoom ¿?
    * __done__ On hide clear data ¿?
    __note__ context menu does not work with FigureCanvas so my plan went thru the drain. Will check alternatives
* barh ejeX
* __done__ Otra vez las Castillas
* __done__ (creo) dumps esporádicos en column
* clean up code
* ejeX con funciones
* click on head and columns
* __done__ Performance check (suffers a _Zugszwang_:  MPL figures have to be closed to be garbage collected, but the delay this action causes is noticeable). A rewrite of the code (reusing figures instead of closing/openinig) must be necesary
* screen real state (> default < 50 %)
* more info in graphs (texts and so on ...)
    
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
* In cubbebrowse add element should directly trigger the editor
* Lock when db not available

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





