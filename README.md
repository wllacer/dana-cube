# dana-cube

Dana-cube is a tool to automate the design, execution and visualization of __cross reference queries__, aka __pivot tables__ aka __multidimensional aggregate queries__.

## What's the problem:

A common problem an SQL database users is to solve the need to resolve an aggregate (sum, aver,...) by two or more parameters, f.i. Give me the sum of sales per country and per line of product The, very simple, SQL query gives a tabular result (country,line,sum(sales)) but the normal way we want to is as a spreadsheet (countries as rows, lines as columns) but this is NOT usually available in most data query programs.

Some DB products (fi. Oracle and MSSQL) offer their own private means of generate such queries, but they're not always availabe in general query tools

Resourceful users can use MS Access cross reference queries to get this or use Pivot Tables available in several spreadsheet programs, but the cost -and most ofter the unwieldness- of linking REAL databases to this products do not make them really sustainable options in the long run.

At the other end of the spectrum, very expensive (in more senses than cost) OLAP products tend to serve the same end, but are usually an overkill; and for various reasons distribution in an organization is restricted, lowering its impact

## What we provide

We provide a database, OS agnostic environment for runing and managing those kind of queries and show them in tabular fashion.

We have created an environment where you can run an -almost- arbitrary aggregate query and show it in tabular fashion.

Each instance of the application runs against what we call a Cube. This is the view of a data table (or table-like DB object -a view, a select statement, ...) and the definition of the potential indexes over which to search. This indexes can be scalar fields or hierarchical structures. If the index is a date field; we automatically provide (for SQLITE, MySQL, PostGreSQL and Oracle, atm) for several subindexes (years, years-month, ...)

This is __not designed as an end user tool__ , rather it is designed to be used for knowledgable users (DBAs, developers, data owners) or as a ready made __API__ cum sample tool to be integrated in other's people work (as it still is in heavy development, _Caveat emptor_ ).

We provide a number of main programs:
* __danacube.py__  Is our main tool where we execute our aggregate accesses to the database (to the cube), and provide means to show graphics or to export the results into several data formats

![Screenshot](docs/image/danacube_ss.png "Title")

* __cubebrowse.py__ Is a tool designed to manipulate the cube definitions. They are a plain Json file (see below) and can be edited by hand if necessary

![Screenshot](docs/image/cubebrowse_ss.png "Title")

* __danabrowse.py__ We can browse the contents of the database servers in our environment, and if necessary, generate direct cube definitions from the catalog of the database 

![Screenshot](docs/image/danabrowse_ss.png "Title")

* __danaquery.py__ A very simple tool to execute arbitrary sql code against database servers in our environment

![Screenshot](docs/image/danaquery_ss.png "Title")

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

We provide a tool to manage these definitions, and another to generate directly from the database a basic outline
(screenshots should follow)

The tool is programmed in python3 + PyQt5 but it might be possible to be run under Python2 (we try to be as much compatible as possible, but haven't tested it in a while)

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

__Update 2017/12/27__  We have a new core based on qt standard models. It simplifies a lot programming and has solved a number of perfomance isses with long guides

What does it means?

* We deem that we have achieved a functional 'completeness' of the cube tool (_danacube.pyw_) , so it should be useful for valiant user; but that it still lacks proper outside testing (so, for sure, many bugs ahead) and  documentation (hope to solve it soon)

* What we know it's missing:
    * Unknown bugs all around (i know i'm not perfect). And a few known ;-)
    * The user interface is implemented just for my needs and lacks internationalization (worse still, it's now a mix of english and spanish)
    * It's reasonably well tested with __Sqlite__, __MySQL__, __PostgreSQL__, and  __ORACLE__ ; but i haven't had the chance to adapt/test it against __DB2__ or __MSSQL Server__ ¿Any volunteer?
    * As of the last release Oracle support is still missing heavy testing..
    * Nor performance, neither security have been, till now, top priority goals. _You've been warned_
    * Legalese is missing in code (copyrights, licence specs, and so on)

I've changed my code management policy. and plan to upstream the changes to _Github_ ASAP, but only _sparse updates to the release code_, so if something crashes, pls. look at the commits at __master__ still not in the released code.

I've been able to install __Oracle__ in my computer, and it seems that some changes are needed (specially in the administrative tools). Expect soon working code.
My computer is too weak to run MsSQL :-(




Active tasks can be read [here](../docs/todo.md) (Obsolete )



## Help Needed

We could profit from someone knowledgable in UI development. I'm a DBA type and, well, it's kind of difficult for me

Testers are welcome.

## Out there ...

If you feel my package isn't cooked enough for you (nor for me either :-( ) have a look at the [Cubes project](https://github.com/DataBrewery/cubes) It might be of interest for you

A.M.D.G. & B.V.M.
