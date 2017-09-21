# Funciones de usuario (plugins)
Son funciones que el usuario puede añadir para ejecutar procesos especiales sobre el cubo (En la versión actual *por cada fila individual*). Estos aparecen en un menú separado

El código que puede ejecutarse es arbitrario, aunque el sistema ofrece la posibilidad de lanzar funciones parametrizadas interactivamente sin necesidad de programar la interfaz de usuario. 

Tambien esta contemplado la ejecución (desde un sólo punto de menú) de una secuencia de funciones 
En la aplicación existe un subdirectorio **./user** donde se pueden guardar los objetos Python programados por el usuario, con la organización que se desee

El sistema esta diseñado para permitir restaurar, en cualquier momento, los valores iniciales del cubo

## Los modulos de usuario. Requerimientos
 En los fuentes se requiere el siguiente import:
 
```
from  util import uf_manager as ufm 
```

Por compatibildad con el resto de la aplicación se aconseja incluir lo siguiente (para permitir compatibilidad v2 y v3 de python)

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
  ...
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
```

En el módulo se pueden incluir cualquier codigo Python. Las funciones de usuario se recomienda que utilicen la siguiente forma

```
def funcionUsuario (*parms, **kwparms):
    ...
```

En un apartado posterior se describen que parametros se recibiran. El sistema NO espera retorno de estas funciones

Para incluir una o mas funciones en el subsistema, en el módulo debe incluirse (una sola vez) una funcion __register__ con un único parametro (el contexto), que contiene las llamadas de registro en el sistema que deseemos, p.e.

```
def register(contexto):
    ufm.registro_funcion(contexto,name='porcentaje',entry=porcentaje,type='item',seqnr=1,
                         text='Porcentaje calculados en la fila')
    ufm.registro_funcion(contexto,name='asigna',entry=asigna,type='item,leaf',seqnr=10,
    ufm.registro_funcion(contexto,name='combinaVarios',entry=consolida,
                         aux_parm={'desde':('5008','5041','5033'),'hacia':('3736',)},type='colkey',seqnr=20,
                         text='Agrupa en uno las candidaturas de Compleja')
    # secuencias de funciones
    ufm.registro_secuencia(contexto,name='combinaCompleja',list=('absorbeUno','absorbeOtro','combinaVarios'),seqnr=23,sep=True,
                           text='Todo lo anterior')
    ufm.registro_secuencia(contexto,name='simul_voto',list=('combinaCompleja','factorizaAgregado'),
                            seqnr=31,text='Simulacion de voto. combinaCompleja Agregado')
```

En un apartado posterior se describen que parametros de estas llamadas

## Tipos de función y parametros que reciben

Los tipos de función determinan que parametros vamos a pasar (necesitamos en nuestra funcion) y si requieren alguna accion especial. Una misma entrada puede tener uno o mas tipos asociados. Los tipos que actualmente reconocemos son:

* __item__ (el defecto) sólo pasamos el item (linea) para el proceso en el modulo

* __leaf__ En cubos jerarquizados sólo se procesan las lineas que son hojas (finales)

* __colkey__  requerimos los identificadores de las distintas columnas

* __colparm__ el usuario es presentado con una lista de las columnas para que dé valores especificos para cada una de ellas

* __rowparm__ el usuario es presentado con una lista de las filas para que dé valores especificos para cada una de ellas

* __kwparm__  el usuario es presentado con campos arbitrarios para que les de valor (ver *aux_parm* en el registro)

Todos los tipos acabados en *parm* son 'automágicamente' interactivos, es decir el sistema genera un diálogo para que el usario introduzca un valor para cada uno de ellos. Rowparm sería cuando el parametro depende de la fila y Colparm cuando este está asociado a una columna concreta. Kwparm permite dar valor a parámetros arbitrarios. En la versión actual debe usuarse si se desean valores iniciales en los parámetros

Si la parametrización no requiere de itervención del usuario, sino que está prefijada, debe utilizarse la cláusula *aux_parm* en el registro

En los tipos de funcion implementados actualmente los parametros que se reciben son:

* en __\*parms__

    * __parms[0]__ recibe un objeto __TreeItem__ (la fila que se va a procesar). Todos los tipos lo reciben. Para manipularlo existen metodos que se detallan mas adelante

    * __parms[1]__ es nulo o una lista con las cabeceras de las distintas columnas. Cada elemento es una tupla con el código interno y el texto de la cabecera de la columna. Recibido con el tipo *colkey*

    * __parms[2]__ es nulo o una lista con elementos para cada una de las filas. Para cada fila tenemos una tupla con el código interno,el texto de la cabecera de la fila y un valor asociado a ella (devuelve strings. si no ha tecleado nada la cadena '' ). Recibido con el tipo *rowparm*

    * __parms[3]__ es nulo o una lista con elementos para cada una de las columnas. Para cada fila tenemos una tupla con el código interno,el texto de la cabecera de la columna y un valor asociado a ella (devuelve strings. si no ha tecleado nada la cadena '' ). Recibido con el tipo *colparm*
        
* en __\*\*kwparms__

    * un diccionario con pares clave-valor. El valor puede ser una lista. Se pasa con el tipo *kwparm* y si se ha registrado con *aux_parm*

        
## parametros de registro

Para __registro_funcion__:

* Elementos generales

    * __name__    Nombre (obligatorio y único). Una cadena de texto

    * __entry__   entry_point (obligatorio). la referencia a una función ejecutable python. Varias entradas pueden definir el mismo (con otros parametros. El entry_point debe estar definido en el módulo en que se ejecuta el register o ser accesible a él (vía _import_)

    * __type__    tipo de parametro. Uno o varios (separados por comas) de los tipos de funcion. Por defecto es 'item'

    * __aux_parm__    parametros auxiliares. Un diccionario con pares clave:valor.  El valor puede ser una lista

    * __text__    texto con el que aparecerá en el menú. Si no se define, se utiliza el nombre

    * __api__      versión de la interfaz que se usa. El defecto es 1. No se utiliza por ahora
    
* para presentacion (opcionales)

    * __seqnr__   numero de orden con el que se presenta en el menú. 

    * __sep__     True o False. Determina si se dibuja un separador tras el. Defecto False

    * __hidden__  True o False. Si es True no se muestra en el menú. Util cuando solo se usan dentro de secuencias. Defecto False
    


Para __registro_secuencia__:

* Elementos generales

    * __name__    Nombre (obligatorio y único). Una cadena de texto

    * __list__    Una lista con nombres de _funciones de usuario o secuencias registradas previamente_. Se ejecutarán en el orden que aparecen en la lista. 

    * __text__    texto con el que aparecerá en el menú. Si no se define, se utiliza el nombre
    
* para presentacion (opcionales)

    * __seqnr__   numero de orden con el que se presenta en el menú. 

    * __sep__     True o False. Determina si se dibuja un separador tras el. Defecto False

    * __hidden__  True o False. Si es True no se muestra en el menú. Defecto False
    

Las funciones o secuencias incluidas en la lista no necesitan estar definidas o registradas en el módulo mismo, pero debe tenerse en cuenta que el proceso de registro evalua los modulos en el directorio en orden alfabético. Si se utilizan varios módulos recomendamos registrar las secuencias que utilicen elementos de varios de ellos en un módulo con un nombre alfabéticamente alto (p.e. _zzsequences.py_ )
    
    
## Metodos que pueden ser utilizadas para acceder a los datos del modelo (de TreeItem)

Una función de usuario puede utilizar todos los métodos de _TreeItem_, pero se recomienda (salvo que se tenga muy claro) que se limiten a usar los siguientes métodos

* __item.getPayload()__ Devuelve una lista con los valores del item (fila). En principio cada valor corresponde a la columna correspondiente (aunque el tamaño de la lista puede no ser igual al número de columnas)

* __item.setPayload(list)__ Actualiza el contenido del item con la lista de valores que se especifique. El número de elementos puede variar en la operación

* __item.lenPayload__ Devuelve el numero de elementos que contiene el item

* __item.getPayloadItem(idx)__ o __item.gpi(idx)__ Devuelve el elemento idx del item o None si no tiene valor o no existe

* __item.setPayloadItem(idx,valor)__ o __item.spi(idx,valor)__ Actualiza el elemento idx del item con el valor que se pasa. El  indice debe existir previamente
    
* __item.getKey()__ e __item.getLabel()_ devuelven la clave y el texto del item(fila)
    
## Un registro anotado.

En La aplicación ejemplo hemos definido una serie de funciones, unas de uso general

* __porcentaje__ expresa los elementos de la fila en porcentajes

* __ordinal__ expresa el orden descendente del valor de los elemento

* __consolida__ mueve una(s) columna sobre otra(s)

* __nfactoriza__ realiza simulaciones de cambios (porcentuales) de valor de las columnas

Y otras especificas de la aplicacion (__asigna__ y __senado__ ) que no vamos a detallar aquí

Veamos como podemos registrarlas como funcion de usuario

```
def register(contexto):
    # funciones ocultas. no aparecen en menu
    ufm.registro_funcion(contexto,name='factoriza',entry=nfactoriza,aux_parm={'funAgr':resultados},type='colparm',hidden=True,api=1)
    ufm.registro_funcion(contexto,name='factorizaAgregado',entry=nfactoriza,aux_parm={'funAgr':resultadosAgr},type='colparm',hidden=True,api=1)
```
La simulación depende de los valores que el usuario defina para cada columna. Con _type=colparm_ el sistema automaticamente generará un dialogo para introducir los datos.Tenemos dos posibles casos, por ello las dos entradas distintas con el mismo _entry_

En este caso la simulación cada caso necesita una función especial para dar un parametro inicial fijo para cada columna. esto lo hacemos pasando la funcion como parametro _aux\_parm={'funAgr':...}_ distinto en cada caso

La simulación no nos interesa por si misma sino con un fin (_ver abajo_), asi que no va a tener entradas en el menú (_hidden=True_). Al ser ocultas no nos molestamos en definir un texto

```
    # funciones elementales
    ufm.registro_funcion(contexto,name='porcentaje',entry=porcentaje,type='item',seqnr=1,
                         text='Porcentaje calculados en la fila')
    ufm.registro_funcion(contexto,name='ordinal',entry=ordinal,type='item',seqnr=2,sep=True,
                         text='ordinales')
    ufm.registro_funcion(contexto,name='asigna',entry=asigna,type='item,leaf',seqnr=10,
                         text='Asignacion de escaños')
    ufm.registro_funcion(contexto,name='Senado',entry=senado,type='item,leaf',seqnr=11,sep=True)
```

Una serie de funciones de usuario básicas. Las dos últimas con _type=...,leaf_ sólo tiene sentido se ejecutan en los nodos finales(hoja) (en este caso, asignar escaños que solo tiene sentido evaluar en la circunscripción mas pequeña)

En el menú aparecerán las primeras en el orden de _seqnr_. Como en alguna de ellas se especifica _sep=True_ el menú presentará un separador tras ellas

```
    ufm.registro_funcion(contexto,name='absorbeUno',entry=consolida,
                         aux_parm={'desde':'4850','hacia':('3736','5008','5041','5033')},type='colkey',seqnr=20,
                         text='Integra x en Compleja')
    ...
    ufm.registro_funcion(contexto,name='combinaVarios',entry=consolida,
                         aux_parm={'desde':('5008','5041','5033'),'hacia':('3736',)},type='colkey',seqnr=20,
                         text='Agrupa en uno las candidaturas de Compleja')
    ufm.registro_funcion(contexto,name='absorbeArbitrario',entry=consolida,
                         aux_parm={'desde':'4850','hacia':('3736','5008','5041','5033')},type='colkey,kwparm',seqnr=20,
                         text='Integra x arbitraria en y arbitraria, ')

    # secuencias de funciones
    ufm.registro_secuencia(contexto,name='combinaCompleja',list=('absorbeUno','absorbeOtro','combinaVarios'),seqnr=23,sep=True,
                           text='Todo lo anterior')
```

En nuestro caso, hay varios casos en que debemos mover los valores de una columna a otra. Para identificar las columnas nuestra funcion debe saber el codigo de las columnas, de ahí que especifique el tipo _type=colkey_. 

Que columnas se mueven lo determino con _aux\_parm={desde:...,hacia:...}_ Con esto creamos entradas en el menu para los casos mas habituales (las dos entradas primeras -y otras-).

Si deseamos que el usuario eliga interactivamente que columnas mover (el tercer caso), al poner _type=...kwparm' hacemos que el sistema presente un dialogo con _desde_ y _hacia_ para que el usuario eliga, con el valor de defecto que figure en _aux\_parm_

En nuestro caso, varias de estas acciones se ejecutan juntas habitualmente. Al definir una secuencia _ufm.registro_secuencia(_ creamos una entrada que ejecuta las funciones de usuario que introducimos en _list('absorbeUno',.._ Cada una de las entradas debe coincidir con el _name=_ de una función registrada anteriormente

Notese que las tres funciones tienen el mismo _seqnr_ En que orden apareceran en el menú entre ellas es arbitrario

```
    ufm.registro_secuencia(contexto,name='simul_voto',list=('combinaCompleja','factorizaAgregado'),
                            seqnr=31,text='Simulacion de voto. combinaCompleja Agregado')
    ufm.registro_secuencia(contexto,name='simul_agregado',
                           list=('combinaCompleja','factorizaAgregado','asigna'),
                           seqnr=32,text='SImulacion de escaños. combinaCompleja Agregado')
    ufm.registro_secuencia(contexto,name='simul',list=('combinaCompleja','factoriza','asigna'),sep=True,
                           seqnr=33,text='SImulacion de escaños. separado')
```    
Otros ejemplos de secuencia. Vease que en la lista se puede incluir otra secuencia (_combinaCompleja_ en nuestro ejemplo) y es donde usamos las funciones que primero definimos como ocultas (_factoriza..._)    
    

