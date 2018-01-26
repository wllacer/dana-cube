# dana-cube

Dana-cube is a tool to automate the design, execution and visualization of __cross reference queries__, aka __pivot tables__ aka __multidimensional aggregate queries__.

## What's the problem:

I spent most of the last twenty years of my professional life mainly as a DBA and/or system manager  on "big databases" Now and then, i was sent as _"maiden for everything"_ to smaller customers and projects. And i ran also my private projects. Everywhere, be it great corporations or goverment offices, be it small shops or individual users with a database. there was the problem __how to extract information from the mass of data in a database beyond what's preprogrammed in the applications__.

I've seen a lot of propossed solutions (be it named _User reporting tools_, _DataWarehouse_ , _OLAP_ or _Bussiness Inteligence_ ) but the fact is that, whatever the technology, they tend to end as overblown, complex, "professional support and security" needed tools, and as resource hungry, closed and  rigid as the applications it should complement. And let's not talk about the licence costs when not open source. There are, though, a number of other tools for _OLAP_ or _data minig_ less demanding, but usually there tend to be complex , giving innecesary pain to the most basic steps

In real life, and those not "lucky" enough to have access to such a tool, everyone has gone the _Access/Excel_ route. Either by periodically being downloaded data or direct ODBC linking into this tools, users develop the reporting/analisys tools they need. I've seen quite a few more than interesting. Stability,  maintainability, and the chance of distributing it, is another story. My own experience with ODBC linking performance is less than good. And as a former DBA, piggybacking an uncontrollable tool (as the ODBC interface is) on a corporate database is a security and performance nightmare

Try to find an alternative to Access as frontend to external databases, or enter Linux desktop ... You're left out in the cold. Very, very cold. Being honest, _OpenOffice_ and derivatives, have a huge "black hole" regarding database interaction. Neither its _Base_ component, nor its interface to outside databases are even minimally comparable to Microsoft's. [KDE's Kexi](http://www.kexi-project.org/) might have interesting features, but does not address Access' functionality as an interface to external databases ... and so on.

I have no need either for a standalone database or a query tool. You'll find a lot of alternatives out there (even though we provide a very simple query tool as part of the package). But there is a tool __I do need__ 

Probably the most common problem an SQL database users is to solve the need to __resolve an aggregate (sum, aver,...) by two or more parameters and show them in array (spreadsheet) form__.

An example will explain it. Supose a database with electoral results, and what whe need is a query of the type  _Give me the sum of votes per party and and per electoral district_ .In  _SQL_ this is a very simple query, like

```
    select partido_id,provincia,sum(votes_presential)
    from votos_locales
    group by partido_id,provincia
```
and gives results in the form

```
"993"	"12"	"2134"
"993"	"46"	"7101"
"993"	"47"	"1570"
"1033"	"23"	"1188"
"1070"	"24"	"1027"
"1079"	"01"	"10468"
"1079"	"02"	"33676"
"1079"	"03"	"154037"
"1079"	"04"	"44320"
"1079"	"05"	"15892"
"1079"	"06"	"45252"
"1079"	"07"	"71446"
....
```
While all the info is there, it's clear that an analyst is better server if data could be shown in an array format (parties as rows, electoral districts as columns) and with some additional info, more or less like 

```

                               C's       EH Bildu        EAJ-PNV             PP           PSOE        PODEMOS           GBAI        CCa-PNC        IU-UPeC   ...
Grand Total               3,500,541        218,467        301,585      7,215,752      5,530,779      3,182,082         30,554         81,750        923,133  
Araba/Álava                  10,468         21,179         28,297         33,609         25,293         48,265                                        6,794                                                                                                         
Albacete                     33,676                                       85,152         65,074         32,155                                        9,277                                                                                                         
Alicante/Alacant            154,037                                      296,709        188,367                                                      33,293
Almería                      44,320                                      117,407         89,022         39,482                                       10,776                                                                                                         
Ávila                        15,892                                       46,963         20,129         11,863                                        3,878                                                                                                         
Badajoz                      45,252                                      137,501        148,347         47,203                                       12,281                                                                                                         
Balears, Illes               71,446                                      140,542         88,542        111,416                                       11,434
Barcelona                   386,143                                      321,268        463,612                                                            
Burgos                       33,373                                       81,780         44,488         36,612                                       10,099                                                                                                         
Cáceres                      28,293                                       87,729         84,532         34,552                                        7,216                                                                                                         
Cádiz                        94,707                                      179,054        180,667        130,215                                       38,798                                                                                                         
Castellón/Castelló           48,220                                       98,341         66,450                                                       9,565
...
```
Sadly, this is usually __NOT available in most data query programs__. Some DB products (fi. Oracle and MSSQL) offer their own private means of generate such queries, but they're not always available in general tools. MS Access _cross reference queries_ or _Pivot Tables_ available in several spreadsheet programs, DO offer this functionality, but the cost -and most ofter the unwieldness- of linking REAL databases to this products do not make them really sustainable options in the long run.

## What we provide

We provide a module (and its _API_) which aims to simplify the generation of such arrays /cross references, allowing to integrate it in any Python module. Thru such an interface the generation of the above sample could be reduced to the following Python core (with formatting extracted):

```
from dana-cube.util.jsonmgr import load_cubo
from dana-cube.core import *

mis_cubos = load_cubo()
cubo = Cubo(mis_cubos["datos light"])
vista = Vista(cubo,'provincia','partidos importantes','sum','votes_presential',totalizado=True)
resultado = vista.toList()
for linea in resultado:
    print(linea)
```
As you can see from the sample, we __do not refer directly to the underlying database, but to an abstraction__. Each instance runs against what we call a __Cube__. This is the view of a data table (or table-like DB object -a view, a select statement, ...) and the definition of the potential fields to query and the criteria over which to search (which we call __guides__ ). This criteria can be scalar fields or hierarchical structures. If the guide is a date field; we automatically provide (for SQLITE, MySQL, PostGreSQL and Oracle, atm) for several subindexes (years, years-month, ...). And every different aggregation is what we call a __Vista__. We provide this abstraction as an Json text file ( _vide infra_ )

As you will notice, this is _not designed as an end user tool_ , rather it is designed to be used for knowledgable users (DBAs, developers, data owners) or as a ready made __API__ cum sample tool to be integrated in other's people work (as it still is in heavy development, _Caveat emptor_ ).

But we do provide and __end user tool__, which can be used standalone: It is called  __danacube.py__  Is our main tool where we execute our aggregate accesses to the database (to the cube), and provide means to show graphics or to export the results into several data formats

![Screenshot](docs/image/danacube_ss.png "Title")

An end user can not define their own cubes, nor use guides outside what's defined in the configuration file. ¿Why? One reason is that it allows showing the end user an view to the data which doesn't need to ajust exactly to the internal database structure. On the other hadn, it's a way carefull DBAs can limit what is available for search in a production database, beyond the database own security.

The tool is open to user extensions, so special test can be run over the data. See [docs here](docs/user_functions.md)-still only spanish- for the user functon module


## Where to run the tool

The tool is programmed in _python3_ + _PyQt5_ but it might be possible to be run under _Python2_ (we try to be as much compatible as possible, but haven't tested it in a while). And we have made avaliable the core functionality _without_ the need of using Qt

The infrastructure is database agnostic. We use [SqlAlchemy](http://www.sqlalchemy.org/) as data backend, so in theory every database which can be accessed thru it should be available, although a few specific changes might be needed 

## The definitions file

The definition of the Cube is a simple text (Json) file like this

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

You can find the documentation at [this place (spanish only)](docs/tree_docs.md)
We provide, also, some administrative tools to work with the cube definitions:

* __cubebrowse.py__ Is a tool designed to manipulate the cube definitions. They are a plain Json file (see below) and can be edited by hand if necessary

![Screenshot](docs/image/cubebrowse_ss.png "Title")

* __danabrowse.py__ We can browse the contents of the database servers in our environment, and if necessary, generate direct cube definitions from the catalog of the database 

![Screenshot](docs/image/danabrowse_ss.png "Title")

* __danaquery.py__ A very simple tool to execute arbitrary sql code against database servers in our environment

![Screenshot](docs/image/danaquery_ss.png "Title")


## Documentation

* The API for the core functionality us [here](docs/core_api.md)
* The full definition specs can be found at [this place (spanish only)](docs/tree_docs.md)
* The user functions specs can be found [this place (spanish only)](docs/user_functions.md)

## Sample Data
We will provide a test database (with results of the Spanish General Election in 2015) for several supported databases, with minimal changes between them.
You will find both a _sample_data.zip_ and a _sample_data.tar.gz_ file in the root directory of the project, there you'll find both a cube definition file and a DB dump for the samples

As a matter of fact, the tool grew analizing those data



## Dependencies

Besides PyQt, we use:

* [SqlAlchemy](http://www.sqlalchemy.org/) as a data backend (only core functionality).Main reason is transparent access to the catalogs
* [DateUtil](https://pypi.python.org/pypi/python-dateutil/2.6.0) for some date related functions
* [SqlParse](https://pypi.python.org/pypi/sqlparse/0.2.2) ( _Optional_ ) for some trace outputs
* [XlsxWriter](https://pypi.python.org/pypi/XlsxWriter) Guess it ...
* [Matplotlib](http://matplotlib.org/) for all the graphic stuff

## License

For my part, while I (Werner Llácer Viciano) retain all ownership of the code, this is an open source product.

__Best policy__ would be to comply to the terms of the __LGPL__ license family (I find it the most honest license both for the authors and the users)

__a good enough policy__ would be to acknowledge my autorship of this piece of code and to send upstream all corrections and enhancements to the original functionality.

If in doubt, or your legal overlords demand some clear answer, then, my code is __LGPL v2 and/or greater than__ licensed. For . __more grave doubts__ please contact me, We'll broker an favorable agreement.

A few _caveats_ :
* Any module installed via the __"user functions"__ functionality is __NOT bound__ to the above mentioned license. That functionality was intendended for the users to extend the capabilities of the tool, so they remain (whatever the mode of linking) property of their developers. In spite of this, those provided by my as samples, are still mine, and licencing aplies (but you have unrestricted right to fork)
* From my point of view, data used and/ore produced by the tool, are owned by their users, not, in any way, by the tool (i.e. me)
* IIRC, the *GPL licenses demand that the code must be made available by the distributor. I think that linking where the source of Danacube resides covers it. Although it might be, from the practical POV a bad idea: repositories may move, version changes could be destructive, and any private enhancement could get lost, ...
* I'm not into legal hairsplitting, so just to avoid confusion, I don't mind if the code is used in/distributed with products under other open source license in the broad sense, as long as they honor my licensing for my code.
* IIRC, my jurisdiction -Spain- DOES NOT recognize software patents, so don't bother me with that. I wonder, anyhow, what would be "patentable" in my algorithms ... and if, not covered by thousands of previous art.

Qt, PyQt -and the additional libraries-, licensing might impose other restrictions, please keep an eye on it (AFAIK PyQt is/was __GPL__ licensed)

## DANACUBE enters __ALPHA__

What does it means?

* We deem that we have achieved a functional 'completeness' of the cube tool (_danacube.pyw_) , so it should be useful for valiant user; but that it still lacks proper outside testing (so, for sure, many bugs ahead) and  documentation (hope to solve it soon)

* What we know it's missing:
    * Unknown bugs all around (i know i'm not perfect). And a few known ;-)
    * Public API for the core functionality is still open (need input for use cases)
    * The user interface is implemented just for my needs and lacks internationalization (worse still, it's now a mix of english and spanish)
    * It's reasonably well tested with __Sqlite__, __MySQL__, __PostgreSQL__,; 
    * As of the last release __Oracle__ 's support, while it works, is still missing thorough testing..
    * I haven't had the chance to adapt/test it against __DB2__ or __MSSQL Server__ ¿Any volunteer?
    * Nor performance, neither security have been, till now, top priority goals. _You've been warned_
    * Legalese is missing in code (copyrights, licence specs, and so on)


__Update 2017/12/27__  We have a new core based on qt standard models. It simplifies a lot programming and has solved a number of perfomance isses with long guides, BUT we keep a pure non-qt core subsystem for those interested



Active tasks can be read [here](../docs/todo.md) (Obsolete )



## Help Needed

We could profit from someone knowledgable in UI development. I'm a DBA type and, well, it's kind of difficult for me

Testers are welcome.

## Out there ...

If you feel my package isn't enough for you  have a look at the following projects of similar technology.They might be of interest for you

* [Cubes project](https://github.com/DataBrewery/cubes)
* [Pandas project](https://pandas.pydata.org/)

A.M.D.G. & B.V.M.
