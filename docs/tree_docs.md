# reglas de produccion del fichero cubo

*   \<cube_file\> ::= \<cube_defs\>+ [ \<default\> ]

Un fichero cubo esta compuesto 
    * __\<cube_defs\>__ por una o mas definciones de __cubos__ : representaciones de tablas de la base de datos y sus las definicion de los criterios de ordenacion que deseamos obtener y, opcionalmente
    * __\<default\>__ la vista inicial con la que queremos que el programa comience
    
 
## definicion de cubos individuales

*  \<cube_defs\> ::= nombre ':' \<definicion de cubo\>

El __cubo__ es la unidad con la que trabajamos. Representa una tabla base de la base de datos, con la lista de __campos__ (numéricos) sobre los que deseamos realizar consultas y una serie de __guías__ que son los potenciales _criterios de agregación_  que deseamos utilizar. Un cubo está identificado por un nombre único

Para entender la terminología, en una query SQL del tipo

```
select provincia,partido,sum(votos) 
from resultados2015
group by provincia,partido

```
* _provincia_ y _partido_ serían __guias__
* _votos_ un __campo__ y
* _resultados2015_ la __tabla__

el conjunto de los campos por los que deseamos agrupar formarían las guias y el conjunto de las definiciones un __cubo__, por ejemplo

``` 
"datos light": {
        "connect": {
            "dbhost": "None",
            "dbname": "/home/werner/projects/dana-cube.git/ejemplo_dana.db",
            "dbpass": "None",
            "dbuser": "None",
            "driver": "qsqlite"
        },
        "table": "main.votos_locales",
        "base filter": "",
        "fields": [
            "votes_presential",
            "main.votos_locales.ord",
            "votes_percent"
        ],
        "guides": [
            {
                "class": "o",
                "name": "partidos importantes",
                "prod": [
                    {
                        "domain": {
                            "code": "code",
                            "desc": "acronimo",
                            "filter": "code in (select distinct partido_id from votos_provincia where votes_percent >= 3)",
                            "table": "main.partidos"
                        },
                        "elem": "partido_id",
                        "fmt": "txt"
                    }
                ]
            },
            {
                "class": "o",
                "name": "Comunidad Autonoma",
                "prod": [
                    {
                        "domain": {
                            "code": "region",
                            "desc": "nombre",
                            "filter": "provincia = ''",
                            "table": "main.localidades"
                        },
                        "elem": "region",
                        "fmt": "txt"
                    }
                ]
            }...
       
    },
```


* \<defincion de cubo\>:= 'connect :' \<connect\> 'table :' \<table\> 'fields :' \<fields\> 'guides :' \<guides\> 'base_filter': \<base filter\> [ 'date_filter :' \<date filter\>


### conexiones

*   \<connect\> ::= 'dbhost :' dbhost dbname :' dbname 'dbuser :' dbuser 'dbpass :'dbpass 'driver :' driver

```
        "connect": {
            "driver": "postgresql",
            "dbname": "dana_sample",
            "dbhost": "localhost",
            "dbuser": "demo",
            "dbpass": "demo123"
        },

```

Son los criterios de conexion a la base de datos, de acuerdo con las especificaciones de SQLAlchemy.

Se desaconseja el uso de __dbpass__ ya que implica tener una clave guardada en un fichero de texto. Para evitar esto las funciones de la aplicación se invocan con el parametro __--secure__ (por defecto). En este caso la clave (y el usuario) se toma dinámicamente  y puede estar vacía en el fichero de configuración.

Los drivers que actualmente aceptamos son : _sqlite, postgresql, mysql, oracle, db2, mssql_  (Los dos últimos no están activos en la versión actual
    
*  \<table\> ::= tablename | schema '.' tablename | query de la base de datos

Identificamos el nombre de la tabla dentro de la base de datos que vamos a utilizar. Puede ser una tabla, vista o directamente una query sobre la base de datos.

Puede especificarse con o sin esquema (las utilidades siempre lo generan con esquema). En el caso de _Sqlite_ el esquema siempre es _main_. En el caso de _Mysql_ (y compatibles) cada base de datos se considera un esquema dentro de la instancia

*  \<base_filter\> ::= querySQL

Podemos definir un criterio de filtro previo a la agrupación. El valor de defecto es "", es decir sin filtro. Por ejemplo, si incluimos

```
        "base_filter" = "anyo_eleccion = '2015" 
``` 
sólo se procesaran en el cubo los registos de ese año.

* \<date_filter\> ::= __*TODO*__

### Campos
*  \<fields\> :: = campo +

Fields es una lista de todos las columnas de la tabla sobre los que deseamos calcular agregaciones. Pueden ser nombres simples o cualificados (esquema.tabla.columna) o funciones SQL sobre los mismos. 

Se espera que estos campos sean de algún formato numérico o con contenidos que el gestor pueda automáticamente convertirlos a numérico (como es el caso con _sqlite_)

### guias
*   \<guides\> = \<guide_def\>+   

Una lista con todas y cada uno de las posibles guias (criterios de agrupación) que se deseen para esa tabla. Todo cubo debería contener al menos dos.

* \<guide_def\> ::= 'name :' name 'class :' \<class\>  'prod :' <prod>

* \<class\> ::= o , c , h , d

* \<prod\> ::= \<ordinary_prod\> , \<category_prod\> , ( \<ordinary_prod\> , \<category_prod\> )+ , \<date_prod\>

* \<ordinary_prod  \> ::= [ \<name\> ] \<elem\>+ [  \<domain\> ]  [\<fmt\>] 

* \<category_prod \> ::= [ \<name\> ] \<elem\> ( \<categories\> , \<case_sql\> ) [\<fmt\>] [\enum_fmt\>]

* \<date_prod \> ::= [ \<name\> ] \<elem\>  \<class\>  \<fmt\> \<mask\>

Cada guía tiene un nombre único dentro de cubo (con el que aparecerá en el programa), una clase asociada y una serie de reglas de producción (definición de como obtenemos los valores de la guia).

Actualmente soportamos las siguientes clases:

* __o__ ordinaria. Un solo elemento asociado definido de columnas de la tabla u otras relacionadas.

```
                    {
                        "fmt": "txt",
                        "elem": "partido_id",
                        "domain": {
                            "table": "public.partidos",
                            "desc": "acronym",
                            "filter": "",
                            "code": "code"
                        }
                    }
```

* __c__ categoría. La definición no es un campo de la base de datos sino una agrupación de valores definida por el usuario

```
                        "categories": [
                            {
                                "default": "otros"
                            },
                            {
                                "condition": "in",
                                "result": "Derecha",
                                "values": [
                                    "3316",
                                    "4688"
                                ]
                            }, ...
                        ],
                        "elem": "partido_id",
                        "fmt": "txt"
                    }
 
```
  
* __h__ jerárquica. La guia tiene mas de un componente organizado jerarquicamente. Una jerarquía puede tener tanto elementos ordinarios como categorias

```
              "prod": [
                    {
                        "class": "o",
                        "elem": "strftime('%Y',fakedate)",
                        "name": "año"
                    },
                    {
                        "case_sql": [
                            "case",
                            "when strftime('%m',$$1) in ('01','02','03')  then strftime('%Y',$$1)|'\\:1'",
                            "when strftime('%m',$$1) in ('04','05','06')  then strftime('%Y',$$1)|'\\:2'",
                            "when strftime('%m',$$1) in ('07','08','09') then strftime('%Y',$$1)|'\\:3'",
                            "when strftime('%m',$$1) in ('10','11','12') then strftime('%Y',$$1)|'\\:4'",
                            "end as $$2"
                        ],
                        "class": "c",
                        "elem": "fakedate",
                        "name": "trimestre"
                    }
                ]
```
* __d__ date (fecha) un tipo de jerarquía especial (por defecto resultados agrupados por año y mes ) para fechas definida automáticamente por la aplicación

```
           {
                "class": "d",
                "name": "fecha",
                "prod": [
                    {
                        "elem": "fakedate",
                        "fmt": "date"
                    }
                ]
            }
```
Cada una de ellas tiene pequeña variaciones en la estructura de la definición.


* \<name\> ::= 'name :' nombre
* \<elem\> ::= 'elem :' ( campo , campo \<link via\> )

Cada regla de producción puede tener un __nombre__ específico. Especialemnte en las asociaciones jerárquicas se recomienda utilizarlo

El __elemento__ es el campo o campos por el que hacemos la agrupación. Técnicamente el contentido de _GROUP BY_ que generamos. Puede contener cualquier valor que sea aceptable dentro de la sentencia GROUP BY del  gestor que utilizamos ( una columna o función de base de datos ). 

Si el elemento se deriva de la tabla base del cubo no es necesario nada más. Si el elemento procede de otra tabla (a la que en SQL se accederia por un _join_) el sistema requiere que con la cláusula __link\_via__ especifiquemos su acceso

Para una guía debemos conocer el __dominio de definición__, es decir el conjunto de valores aceptables para esta guía. Con este fin definimos, en las guias __ordinarias__, la entrada __domain__, que nos dá el conjunto de valores aceptables para esta guía  y, habitualmente, el texto con el que queremos presentarlos (para poder traducir la codificación interna de los campos en valores con sentido para el usuario ). Si no se especifica el dominio de definición son los distintos valores del campo existentes en la tabla.

En las guías tipo __categoría__ la propia definición realiza esta función de determinación del dominio de definición a través de las cláusulas __case\_sql__ o __categories__ , en función si es más eficaz para el usuario especificar las categorías con una sentencia _CASE_ o definiendolas a mano

En las guías tipo __date__, al ocuparse sólo de fechas no se requiere este dominio, sino una especificación de la jerarquía de fechas que deseamos presentar-


* \<domain\> ::=   \<table\>  \<code\>+ [ \<desc\>+ ]  [ \<filter\> ] [ \<grouped by\> ]

* \<table\> ::= 'table :' nombre_de_tabla
* \<code\> ::=  'code:'  (nombre de campo)+
* \<desc\> ::=  'desc:'  (nombre de campo)+
* \<filter\> ::= 'filter :' ("" , clasula_select )
* \<grouped by\> ::= nombre de campo+

Con esta clausula determinamos el dominio de definición, con __table__ denotando la tabla donde residen los valores, __code__ el campo o campos que corresponden al elemento o elementos de la guía (en relación uno a uno con ellos) y __desc__ el campo o campos que contienen el texto por el que vamos a suusituir los valores en la presentación.

__filter__ nos permite reducir el conjunto de registros de la tabla que queramos procesaran

En dominios jerarquicos puede ser necesario incluir un descriptor que nos indique que campo de un dominio intermedio corresponde al dominio de nivel superior. Para ello utilizamos la clausula __grouped by__, p.e. en

```
               "prod": [
                    {
                        "domain": {
                            "code": "region",
                            "desc": "nombre",
                            "filter": "provincia = ''",
                            "table": "main.localidades"
                        }, ...
                    },
                    {
                        "domain": {
                            "code": "provincia",
                            "desc": "nombre",
                            "filter": "provincia <> '' and municipio = '' and isla = ''",
                            "grouped by": "region",
                            "table": "main.localidades"
                        },
                        ...
                    }
                ]
```
denotamos que en el dominio de provincia la región (el primer nivel de jerarquía) esta definida en la columna "region" (notesé que ambos niveles utilizan la misma tabla con distintos criterios de selección ) __filter__) para cada uno de los dominios, actuando como vistas separadas


* \<categories\> ::= \<defaut value\> \<category item\>+
* \<default value> ::= 'default ::=' valor
* \<category item\> ::= 'result :=' valor 'condition :=' condition 'values :'valor+

Con la clausula _categories_ podemos definir las agrupaciones de valores del campo base en lo que deseemos. POdemos especificar un __default_, es decir un valor para todos los que no pertenezcan a una categoria definida

Cada catergoria esta definida por un valor resultado y una condición logica sobre los valores del campo, p.e. concreto
```
                           {
                                "condition": "in",
                                "result": "Derecha",
                                "values": [
                                    "3316",
                                    "4688"
                                ]
                            }
```
 implicaria que la categoria 'Derecha' estaria formada por el resultado de la condicion
```
    campo in ('3316','4688')
```

Dado que en un fichero json todos los valores son textuales, se recomienda encarecidamente que se utilicen los parametros __fmt__ y __fmt\_out__ para un correcto funcionamiento del sistema, si se utilizan campos numéricos en la guia

* \<case_sql\> ::= (codigo_sql)+

Con esta clausula generamos texto _SQL_ como definición de la guía. Puede ser cualquier texto que sea compatible con un elemento de la clausula _SELECT_ y _GROUP BY_ del gestor concreto,. Normalmente sería una clausula _CASE_, de ahi el nombre. En una lista ponemos código sql compatible linea a linea. Para evitar problemas de nombres, el nombre del campo sobre el que hacemos la operacion debe sustituirse por "$$1" y el valor de la clausula _AS_ con $$2.

El nombre procede de la cláusula _CASE_ que es el caso mas habitual. Otras clausulas(como subselects) son potencialmente usables, pero consulte con sus DBAs correspondiente ya que pueden generar serios problemas de rendimiento o no ser compatibles con _SELECT_ y _GROUP BY_ en su gestor concreto

*  \<link via\> ::= 'link via :' \<link path\>+
*  \<link path\> ::= 'table :' link_table ['filter :' ("",sentencia) ] 'clause :' \<join clause\>+
*  \<join clause\> ::= 'base_elem :' campo+ [ 'condition :' \<condition\>' ]rel_elem' campo+
*  \<condition\> ::=  ('in','between','like','=','!=','<','>','>=','<=','not in','not between','not like','is null','is not null')
Con estas clausulas generamos codigo con la estructura generica del tipo

```
   SELECT ...,(link_table.)guide_elem
   FROM   tabla_cubo
   JOIN   link_table ON tabla_cubo.base_elem = link_table.rel_elem AND filter
   
```
y en el caso de múltiples clauses ( _0 y _1 denotan las respectivas entradas en la lista de __clause__; y _F el último elemento de la lista)

```
   SELECT ...,(link_table_F.)guide_elem
   FROM   tabla_cubo
   JOIN   link_table_0 ON tabla_cubo.base_elem_0 = link_table.rel_elem_0 AND filter_0
   JOIN   link_table_1 ON link_table_0.base_elem_1 = link_table_1.rel_elem_0 AND filter_1
   ...
   
```
Opcionalemnte se puede especificar una clausula de enlace que no sea la condición igual (normalmente no recomendado)

* \<\fmt\>::= 'fmt ::= \<fmt_clause\>
* \<\enum_fmt\>::= 'enum_fmt ::= \<fmt_clause\>
* \<fmt\>::= 'fmt ::= ' ( 'txt' , 'num' ,'date')

En algunas circunstacias puede ser recomendable incluir un formato del campo para asegurar correctas ordenaciones o comparaciones en el gestor.

En las guias _ordinarias_, normalmente corresponde al definido en la base de datos y no suele ser necesario especificarlo. 

En _categorias_ podemos necesitar dos de ellos, __fmt__ el que corresponde al campo sobre el que agrupamos y __enum_fmt__ que corresponde al formato del resultados. Si no se especifica, se asume que es _'txt'_.

Para las guias tipo _date_debería incluirse siempre (aunque casi siempre sea _'date'_ )


Atributos específicos de cada tipo:

## La entrada de defecto

la entrada default, esta compuesta por la identicación del cubo y la definción de la vista que vamos a abrir. Ejemplo

```
    "default": {
        "cubo": "datos locales",
        "vista": {
            "agregado": "sum",
            "col": "1",
            "elemento": "votes_presential",
            "row": "3"
        }
    },

```
*   <\default\> ::= 'default :'\<cubeid\> <\view_def\>
*   \<cubeid \>   ::=  "cubo" ":" cube_name

El nombre del cubo debe coincidir con uno de los cubos definidos en el fichero

*   \<view_def \> ::=  "view" ":" \<view_detail\>


*   \<view_detail \> ::= "row" ":" guide_id
                   "col" ":" guide_id
                   "elemento" ":" field_id
                   "agregado" ":" \<agregate_fn\>
    * __guide\_id__     es el ordinal de los criterios  guia que queremos analizar.
    
    * __field_id__  es el nombre del campo sobre el que realizamos la consulta

    *   __\<agregate_fn\>__ ::= 'sum' | 'count' | 'avg' | 'max' |'min'  Es la función de agregación que vamos a ejecutar sobre el campo. Las funciones permitidas esán documentadas en _datalayer.access_layer.AGR_LIST_

## relacion completa de las reglas BNF

*  \<cube_file\> ::= \<cube_defs\>+ [ \<default\> ]
*  \<cube_defs\> ::= nombre ':' \<definicion de cubo\>
* \<defincion de cubo\>:= 'connect :' \<connect\> 'table :' \<table\> 'fields :' \<fields\> 'guides :' \<guides\> 'base_filter': \<base filter\> [ 'date_filter :' \<date filter\>
*   \<connect\> ::= 'dbhost :' dbhost dbname :' dbname 'dbuser :' dbuser 'dbpass :'dbpass 'driver :' driver
*  \<table\> ::= tablename | schema '.' tablename | query de la base de datos
*  \<base_filter\> ::= querySQL
* \<date_filter\> ::= __*TODO*__
*  \<fields\> :: = campo +
*   \<guides\> = \<guide_def\>+   
*   \<guides\> = \<guide_def\>+   
* \<guide_def\> ::= 'name :' name 'class :' \<class\>  'prod :' <prod>
* \<class\> ::= o , c , h , d
* \<prod\> ::= \<ordinary_prod\> , \<category_prod\> , ( \<ordinary_prod\> , \<category_prod\> )+ , \<date_prod\>
* \<ordinary_prod  \> ::= [ \<name\> ] \<elem\>+ [  \<domain\> ]  [\<fmt\>] 
* \<category_prod \> ::= [ \<name\> ] \<elem\> ( \<categories\> , \<case_sql\> ) [\<fmt\>] [\enum_fmt\>]
* \<date_prod \> ::= [ \<name\> ] \<elem\>  \<class\>  \<fmt\> \<mask\>
* \<name\> ::= 'name :' nombre
* \<elem\> ::= 'elem :' ( campo , campo \<link via\> )
* \<domain\> ::=   \<table\>  \<code\>+ [ \<desc\>+ ]  [ \<filter\> ] [ \<grouped by\> ]
* \<table\> ::= 'table :' nombre_de_tabla
* \<code\> ::=  'code:'  (nombre de campo)+
* \<desc\> ::=  'desc:'  (nombre de campo)+
* \<filter\> ::= 'filter :' ("" , clasula_select )
* \<grouped by\> ::= nombre de campo+
* \<categories\> ::= \<defaut value\> \<category item\>+
* \<default value> ::= 'default ::=' valor
* \<category item\> ::= 'result :=' valor 'condition :=' condition 'values :'valor+
* \<case_sql\> ::= (codigo_sql)+
*  \<link via\> ::= 'link via :' \<link path\>+
*  \<link path\> ::= 'table :' link_table ['filter :' ("",sentencia) ] 'clause :' \<join clause\>+
*  \<join clause\> ::= 'base_elem :' campo+ [ 'condition :' \<condition\>' ]rel_elem' campo+
*  \<condition\> ::=  ('in','between','like','=','!=','<','>','>=','<=','not in','not between','not like','is null','is not null')
* \<\fmt\>::= 'fmt ::= \<fmt_clause\>
* \<\enum_fmt\>::= 'enum_fmt ::= \<fmt_clause\>
* \<fmt\>::= 'fmt ::= ' ( 'txt' , 'num' ,'date')
*   <\default\> ::= 'default :'\<cubeid\> <\view_def\>
*   \<cubeid \>   ::=  "cubo" ":" cube_name
*   \<view_def \> ::=  "view" ":" \<view_detail\>

*   \<view_detail \> ::= "row" ":" guide_id
                   "col" ":" guide_id
                   "elemento" ":" field_id
                   "agregado" ":" \<agregate_fn\>
* __guide\_id__     es el ordinal de los criterios  guia que queremos analizar.
* __field_id__  es el nombre del campo sobre el que realizamos la consulta
*   __\<agregate_fn\>__ ::= 'sum' | 'count' | 'avg' | 'max' |'min' 
