# Tabla de Contenidos

* [Instalar el producto ](#instalar-el-producto)
* [Instalar las bases de datos de ejemplo ](#instalar-las-bases-de-datos-de-ejemplo)
* [Trabajar con un cubo ](#trabajar-con-un-cubo)
* [Configurar un cubo](#configurar-un-cubo)
    * [configurar la conexion ](#configurar-la-conexion)
    * [analizar los datos existentes ](#analizar-los-datos-existentes)
    * [crear el cubo ](#crear-el-cubo)


# Instalar el producto

Por el momento la instalación es manual, es decir una vez instalados en el entorno los requisitos, se descarga la aplicación y listo para ejecutar.
Si se desea utilizarla como API recordad que debe copiarse en el subdirectorio __site_packages__ de la version de Python que se usa

# Instalar las bases de datos de ejemplo

Si lo que se desea es meramente evaluar las capacidades del producto, recomendamos utilizar __sqlite__ como "backend", ya que no requiere recursos de base de datos externos a la persona que lo prueba

* Extraer en un fichero temporal el __sample\_data.zip__ o __sample\_data.tar.gz__  (depende la herramienta que sea mas comoda)
* Crear una base de datos para la aplicació o utlizar una existente (mejor crear, son datos de prueba)
* Cargar en la base de datos el correspondiente fichero *_dump.sql
* Si queremos probar con __sqlite__, sencillamente dejar __ejemplo_dana.db__ en el directorio de trabajo
* Mover al directorio de trabajo el correspondiente  __cubo\*\.json__ renombrandolo como __cubo.json__ simplemente
* Modificar en el fichero __cubo.json__ las clausulas __connect__ para adaptarlas al entorno 

# Trabajar con un cubo

# Configurar un cubo
## configurar la conexion
## analizar los datos existentes
## crear el cubo
