# dana-cube

Dana-cube is a tool to automate the design, execution and visualization of cross reference queries, aka pivot tables aka multidimensional aggregate queries.

## What's the problem:

A common problem an SQL database users is to solve the need to resolve an aggregate (sum, aver,...) by two or more parameters, f.i. Give me the sum of sales per country and per line of product The, very simple, SQL query gives a tabular result (country,line,sum(sales)) but the normal way we want to is as a spreadsheet (countries as rows, lines as columns) but this is NOT usually available in most data query programs.
Resourceful users can use MS Access cross reference queries to get this or use Pivot Tables available in several spreadsheet programs, but the cost -and most ofter the unwieldness- of linking REAL databases to this products do not make them really sustainable options in the long run.

At the other end of the spectrum, very expensive (in more senses than cost) OLAP products tend to serve the same end, but are usually an overkill; and for various reasons distribution in an organization is restricted, lowering its impact

## What we provide

We provide a database, OS agnostic environment for runing and managing those kind of queries and show them in tabular fashion.

We have created an environment where you can run an -almost- arbitrary aggregate query and show it in tabular fashion.

![Screenshot](docs/screenshot.png "Title")

This is __not designed as an end user tool__ , rather it is designed to be used for knowledgable users (DBAs, developers, data owners) or as a ready made __API__ cum sample tool to be integrated in other's people work (as it still is in heavy development, _Caveat emptor_ ).


Each instance of the application runs against what we call a Cube. This is the view of a data table (or table-like DB object -a view, a select statement, ...) and the definition of the potential indexes over which to search. This indexes can be scalar fields or hierarchical structures. If the index is a date field; we automatically provide (for SQLITE, MySQL, PostGreSQL and Oracle, atm) for several subindexes (years, years-month, ...) The definition of the Cube is a simple text (Json) file like this

```
    "datos light": {
        "base filter": "", 
        "table": "votos_locales", 
        "guides": [
            {
                "prod": [
                    {
                        "source": {
                            "filter": "", 
                            "table": "partidos", 
                            "code": "code", 
                            "desc": "acronym"
                        }, 
                        "fmt": "txt", 
                        "elem": "partido"
                    }
                ], 
                "name": "partido", 
                "class": "o"
            }, 
            ...
        ], 
        "connect": {
            "dbuser": null, 
            "dbhost": null, 
            "driver": "QSQLITE", 
            "dbname": "/home/werner/projects/dana-cube.git/ejemplo_dana.db", 
            "dbpass": null
        }, 
        "fields": [
            "votes_presential", 
            "votes_percent", 
            "ord"
        ]
    }, 
 ```

Why a text file for definition? To avoid a dependency to a concrete DB Manager or of their DBA's . Second, text files are easier to distribute and for "emergency' changes. 

We provide a tool to manage these definitions, and another to generate directly from the database a basic outline
(screenshots should follow)

The tool is programmed in python2 + PyQt5?, but we test it also under python3.

## Sample Data
Since September 2016, we are using the Sakila/Pagila database as sample target (first in MySQL, the latter in PostGreSQL)
in Master

## Dependencies

Besides PyQt, we use:

* [SqlAlchemy](http://www.sqlalchemy.org/) as a data backend (only core functionality). If you don't 
want it, can be made to fallback to plain PyQt/QtSql (by hand, actually, and only for the cube viewer)
* [DateUtil](https://pypi.python.org/pypi/python-dateutil/2.6.0) for some date related functions
* [SqlParse](https://pypi.python.org/pypi/sqlparse/0.2.2) ( _Optional_ ) for some trace outputs
* [XlsxWriter](https://pypi.python.org/pypi/XlsxWriter) Guess it ...
* [Matplotlib](http://matplotlib.org/)

## License

For my part, while I (Werner Llácer Viciano) retain all ownership of the code, this is an open source product.

__Best policy__ would be to comply to the terms of the __LGPL__ license family (I find it the most honest license both for the authors and the users)

__a good enough policy__ would be to acknowledge my autorship of this piece of code and to send upstream all corrections and enhancements to the original functionality.

If in doubt, or your legal overlords demand some clear answer, then, my code is __LGPL v2 and/or greater than__ licensed.
Two _caveats_ :
* IIRC, the *GPL licenses demand that the code must be made available by the distributor. I think that linking where the source of Danacube resides covers it. Although it might be, from the practical POV a bad idea: repositories may move, version changes could be destructive, and any private enhancement could get lost, ...
* I'm not into legal hairsplitting, so just to avoid confusion, I don't mind if the code is used in/distributed with products under other open source license in the broad sense, as long as they honor my licensing for my code

Qt, PyQt -and the additional libraries-, licensing might impose other restrictions, please keep an eye on it (AFAIK PyQt is/was __GPL__ licensed)

## DANACUBE enters __ALPHA__

__Update 2017/02/01__. New alpha release

With today's release (version 0.10), we enter alpha. What does it means?

* We deem that we have achieved a functional 'completeness' of the cube tool (_danacube.pyw_) , so it should be useful for valiant user; but that it still lacks proper outside testing (so, for sure, many bugs ahead) and  documentation (hope to solve it soon)

* What we know it's missing:
    * Unknown bugs all around (i know i'm not perfect)
    * The user interface is implemented just for my needs and lacks internationalization (worse still, it's now a mix of english and spanish)
    * It's reasonably well tested with __Sqlite__, __MySQL__ and __PostgreSQL__; __ORACLE__ has some issues (_see below_; but i haven't had the chance to adapt/test it against __DB2__ or __MSSQL Server__ ¿Any volunteer?
    * As of today (2017/02/02) Oracle support is only partial, as it has issues  constructed statements for guides
    * Nor performance, neither security have been, till now, top priority goals. _You've been warned_
    * The way User functions have been implemented is a 'hack'. Working on a better solution
    * The administrative interface (_danabrowse.pyw_) and support, is still not 100% functional (but as the administrative files are pure JSON, this is not a showstopper)
    
    * Legalese is missing in code (copyrights, licence specs, and so on)

I've changed my code management policy. and plan to upstream the changes to _Github_ ASAP, but only _weekly updates to the release code_, so if something crashes, pls. look at the commits at __master__ still not in the released code.

I've been able to install __Oracle__ in my computer, and it seems that some changes are needed (specially in the administrative tools). Expect soon working code.
My computer is too weak to run MsSQL :-(


## Actual Status

_Update on the day of the Conversion of the Apostol Paul 2017_ As of today we enter __ALPHA__ status (see above for what it means)

_Update XXIII ordinary sunday (vesper of S. Raphael Archangel 2016_ . For the first time, the code has all the main components in place. A release will be tagged during the day
Of course there are still lots of bugs or areas with a minimal implementation, but the tool is usable on its full life cycle, so real debugging, -and fleshing- can start
It only lacks -as a full subsystem- export capabilities. For end users they are critical, but as a subsystem fully isolated, they aren't as important from the application architecture POV

_Update Feast of St. Francis of Borja 2016_ We have merged today the development tree at _Github_  The core code is more or less in an alfa release state, but the ancilliary tools aren't still there

_Update Feast of St. Peter Canisius 2016_ I've integrated SqlAlchemy as (selectable but default) backend. Couple of reasons why:
    * Better licensing terms 
    * PyQt/QtSql as open product lacks some drivers i find useful
    * Gets me more debugging info
    
_Update Feast of St. Cletus & Marcellin 2016_ I've changed a lot of internals in the move from lists to dictionaries (trees) for
the guides. Performance is noticeable faster, and the code is better. Still haven't a release 

_Update Feast of St. Georg 2016_ I used lists for guide definition and retrieval. I've discovered that using dictionaries
enhances performance over 10000 % (read __100 TIMES__ ), but i have to rewrite almost everything again

_Update Saturday of the BVM_: New GUI based on the Model View elements of Qt. Still some parts missing

_Update Feria after Feast of St. Vincent Ferrer 2016_: __MASTER WORKS__. Only functionality missing is a statistical test (fivepoints) i've disabled pending
further revisions. Outside of this, it's functionally identical to the '12 version

_Update Feast of St. Vincent Ferrer 2016_: Work has progressed steadily. Upgrade to new versions seems to work, and i'm 
in a process of heavy refactoring of the core functionality. Sadly that implies that _MASTER_ is broken, and might be for some time.
I made a release from the old codebase which does work. Still have to master Github to know how to mantain them in parallel, so pls. be patient with bugs in there

_Update Easter Monday 2016_: work has resumed. At first we'll center only in Python 3 -and Qt 5- compatibility). 

I hope to make some inroads into new functionality.


Active tasks can be read [here](../docs/todo.md)


## Historical info

### History:
As of June,12 2012 HEAD is loaded with functional code (it just lacks some UI functions we want in 0.1). The user interface is rather primitive and has been "lifted" from the "numbers" example of Mark Summerfield's book "Rapid GUI Programming with Python and Qt. Definitive Guide to PyQt?"

### Current Plans (Just for historical value. Nothing came out of it)
Updated at the Feast of St. Agnes, 2014 In case you haven't noticed it, development has stalled, but i'm still out there. I hope to resume work in the short term. Probably i'll drop QtSql? as DB backend ... 

Updated at the Feast of the Sacred Hearth of Jesus, 2012. Due to some rather unexpected events -not all negative-, release schedule is in a bit of flux. But let's see how things develop Version 0.1 Due July, 1. Although HEAD should be usable by now. We plan to have all the core functionality implemented by then, with only minor functional aspects wanting. UI, error handling and doc will still be primitive we could introduce several intermediate releases and

By September, 15 release Version 0.2 Our milestone for this version is to introduce an n-dimensional interface (several queries shown at once -or at least in tabs), and to close other known deficiences (and as much of the unknown posible ;-)

We have still no plans to introduce an UI to generate the YAML (text) definition file at the core of the product. We try to be DB agnostic and the retrieval of the catalog is not an standard area, nor QtSQl abstract this. We are researching into this ...

## Help Needed

We could profit from someone knowledgable in UI development. I'm a DBA type and, well, it's kind of difficult for me

Testers are welcome.

## Out there ...

If you feel my package isn't cooked enough for you (nor for me either :-( ) have a look at the [Cubes project](https://github.com/DataBrewery/cubes) It might be of interest for you

A.M.D.G. & B.V.M.
