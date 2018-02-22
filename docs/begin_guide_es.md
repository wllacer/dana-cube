__Tabla de Contenidos__

* [Instalar el producto](#instalar-el-producto)
* [Instalar las bases de datos de ejemplo](#instalar-las-bases-de-datos-de-ejemplo)
* [Trabajar con un cubo](#trabajar-con-un-cubo)
    * [Estructura de menus](#estructura-de-menus)
    * [Flujo de trabajo](#flujo-de-trabajo)
        * [Obtener la información](#obtener-la-información)
        * [Filtrar la información](#filtrar-la-información)
        * [Mejorar la presentacion](#mejorar-la-presentacion)
        * [Manipular los datos](#manipular-los-datos)
        * [Exportar los datos](#exportar-los-datos)
* [Configurar un cubo](#configurar-un-cubo)
    * [configurar la conexion](#configurar-la-conexion)
    * [analizar los datos existentes](#analizar-los-datos-existentes)
    * [crear el cubo](#crear-el-cubo)

__WARNING__ _during development time, images may not appear in this document_

# Instalar el producto

Por el momento la instalación es manual, es decir una vez instalados en el entorno los requisitos, se descarga la aplicación y listo para ejecutar.
Puede descargar, bien 

* [una version estable](https://github.com/wllacer/dana-cube/releases) o

* clonar el arbol de desarrollo, descargandolo en [formato zip](https://github.com/wllacer/dana-cube/archive/master.zip) o directamente de _git_ 

```
    git clone https://github.com/wllacer/dana-cube.git
```
Si se desea utilizarla como API recordad que debe copiarse en el subdirectorio __site_packages__ de la version de Python que se usa

# Instalar las bases de datos de ejemplo

_Si lo que se desea es meramente evaluar las capacidades del producto, recomendamos utilizar __sqlite__ como "backend", ya que no requiere recursos de base de datos externos a la persona que lo prueba_

* Extraer en un fichero temporal el __sample\_data.zip__ o __sample\_data.tar.gz__  (depende la herramienta que sea mas comoda)
* Crear una base de datos para la aplicació o utlizar una existente (mejor crear, son datos de prueba)
* Cargar en la base de datos el correspondiente fichero *_dump.sql
* Si queremos probar con __sqlite__, sencillamente dejar __ejemplo_dana.db__ en el directorio de trabajo
* Mover al directorio de trabajo el correspondiente  __cubo\*\.json__ renombrandolo como __cubo.json__ simplemente
* Modificar en el fichero __cubo.json__ las clausulas __connect__ para adaptarlas al entorno 

# Trabajar con un cubo

## Estructura de menus

* Cubo
    * Abrir cubo
    * Convertir vista actual a defecto
    * Guardar Filtros permanetnemente
    * Salvar rango Fechas
* Vista
    * Abrir vista
    * Cambiar vista actual
    * Cerrar vista actual
* Usar Filtros
    * Editar Filtro
    * Borrar Filtros
    + Editar Rango Fechas
    * Borrar rango fechas

* Opciones
    * Exportar Datos 
    * Trasponer datos 
    * Presentacion 
    * Graficos 
    
* Funciones de usuario
    * restaurar valores originales
    * Funciones generales ... 
    * Funciones especificas ...
    

## Flujo de trabajo

### Obtener la información

Invocamos a la funcion de menu _Cubo>Abrir cubo_, y nos aparece un selector

![seleccionar cubo](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/select_cube.png)

Con el elegiremos el cubo con el que queramos trabajar en nuestra sesión (para cambiarlo, volvemos a elegir la misma opción). Cada instancia de la aplicación trabaja con un solo cubo.

Si la base de datos requiere conexión con usuario y clave, se la pedirá en este punto

Inmediatamente nos aparecera otro diálogo en el que debemos especificar la vista que deseamos calcular

![crear vista](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/create_view_filled.png)

En ella debemos elegir:

* las __guias__ (campos) que deseamos que sean las filas y las columnas de nuestra vista

* La __funcion de agregación__ y el __campo__ sobre cuyos valores queremos hacer los cálculos. Las funciones de agregación son las habituales de base de datos, (_sum_ para suma, _avg_ para promedio,  _count_ numero de ocurrencias y _max_ o _min_ )

* Si marcamos __con Totales__ tendremos una primera fila que representa la agregación elegida sobre todos los elementos del cubo (_Grand Total_ es lo que nos aparece)

* Si marcamos __con estadisticas__ el sistema calcula, para cada fila, una serie de estadisticas y nos marca con fondo amarillo aquellas entradas que pudieran ser valores "anormales" en a distribución de valores (un _outlier_ en inglés). Estos valores se calculan suponiendo una _distribución gaussiana o normal_ y no tienen porqué ser significativos

Una vez elegida, se procesarán los datos y nos aparecera el resultado

![resultado](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/view_result.png) 

Si deseamos cambiar alguno de los parametros de la vista usamos el menu _Vista >Cambiar Vista Actual_ 

Si deseamos abrir una pestaña nueva con otra vista sobre el mismo cubo, manteniendo la actual podemos hacerlo con la opción _Vista >Abrir Vista ..._
Un ejemplo de resultado con dos vistas abiertas lo tienen aqui

![con dos vistas](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/two_open_views.png)


### Filtrar la información

Con la opcion  _Usar Filtro >Editar Filtro_ podemos filtrar datos del cubo original, seleccionando condiciones para cada uno de los campos de la tabla base. Si la condición lógica admite multiples valores deben separarse por comas. Y recordad que el carácter decimal debe ser el punto '.'


![editar](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/create_filter.png)

Para los campos tipo fecha tenemos una opción especial para filtrar _Usar Filtro>Editar Rango Fechas_

![Rango de Fechas](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/Date_Range.png)

Para cada campo tipo fecha podemos elegir

* Un __Periodo__ , i.e. una clase de intervalo temporal  (año, mes, ...) y un __Rango__, es decir el numero de periodos que cubre el intervalo

* Un __tipo de intervalo__, con las opciones
    * __Todo__   No se filtra por ese campo
    * __Actual__  El periodo que incluye la fecha actual
    * __intervalo__ un conjunto de n periodos  (donde n es el rango) que finalizan el día anterior a la fecha actual.
    * __Ultimo intervalo Abierto__ idm. que finalizan el último día natural del periodo en curso (p.e si es año el 31 de diciembre del año en curso)
    * __Ultimo intervalo Cerrado__ idm. que finalizan el último día natural del ultimo periodo ya completado (p.e si es año el 31 de diciembre del año anterior)

Los campos __desde__ y __hasta__ del diálogo nos permiten ver que fechas estamos eligiendo para los periodos


La opción _Usar Filtro >Borrar Filtros_ o _Usar Filtro>Borrar Rango fechas_ elimina la condición que hayamos elegido anteriormente

En el menu  _Cubo_ existen opciones para hacer esos filtros permanentes para todas las posteriores ejecuciones del Cubo

### Mejorar la presentacion

#### Trasponer datos 

La opción de menú _Opciones>Trasponer datos_ nos permite trasponer la tabla de presentación, es decir convertir las filas en columnas y viceversa. Esta acción se realiza sin necesidad de acudir al gestor de base de datos

#### Formatos de presentacion 

La opción de menú _Opciones>Presentación_ nos permite modificar algunos parametros de presentación

![parametros](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/preferences.png)

* Thousands Separator
* Decimal Marker
* Decimal Places
* Red Negative Numbers
* Yellow Outliers

#### Gráficos 

![select](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/graph_selector.png) 

![resultado](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/view_graph.png)

### Manipular los datos

### Exportar los datos


* Cubo
    * Abrir cubo
    
    ![seleccionar cubo](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/select_cube.png)
    
    * Convertir vista actual a defecto
    * Guardar Filtros permanetnemente
    * Salvar rango Fechas
* Vista
    * Abrir vista
    
    ![crear vista](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/create_view_filled.png)
    

    
    ![con dos vistas](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/two_open_views.png)
    
    * Cambiar vista actual
    * Cerrar vista actual
* Usar Filtros
    * Editar Filtro
    
    ![editar](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/create_filter.png)
    
    ![resultado](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/filter_result.png)
    
    * Borrar Filtros
    + Editar Rango Fechas
    * Borrar rango fechas

* Opciones
    * Exportar Datos 
    
    ![Paso 1](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/export_filter.png)
    
    ![Paso 2](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/export_file.png) 
    
    ![Paso3](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/export_params.png)
    
    * Trasponer datos 
    
    ![resultado](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/traspose.png)
    
    * Presentacion 
    
    ![parametros](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/preferences.png)
    
    * Graficos 
    
    ![select](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/graph_selector.png) 
    
    ![resultado](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/view_graph.png)
    
* Funciones de usuario
    * restaurar valores originales
    * Funciones generales ... 
    
    ![percentage](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/uf_percentage.png)
    
    ![fusionar](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/fusionar.png)
    
    ![simular](/home/werner/projects/dana-cube.git/docs/image/danacube_UG/simular.png)
    
    * Funciones especificas ...


# Configurar un cubo
## configurar la conexion
## analizar los datos existentes
## crear el cubo
