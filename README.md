# lego-scraper

Raspador de precios para los siguientes sitios web:

+ https://www.firstcry.ae
+ https://www.amazon.ae
+ https://www.toysrusmena.com/en-ae/
+ https://lego.yellowblocks.me/en-ae/
+ https://lego.saudiblocks.com

## Instalacion

### Pre-requisitos

- Python 3.9.6

## Instalar

Se require de algunas librerias externas, para instalarlas siga los siguientes pasos:

0. Los siguientes pasos estan basados en un OS de tipo Unix (macOS, Linux), pero puede intentar replicar estos pasos en Windows.

1. Se recomienda el uso de un entorno virtual para la instalacion/uso de las librerias. Para crear un entorno virtual ejecute los siguientes comandos:

```bash
# Desde su terminal, ingrese al directorio del proyecto
cd /path/to/lego-scraper

# Instale la libreria virtualenv que nos permitira generar un entorno virtual
pip3 install virtualenv

# Dentro del directorio del proyecto cree el entorno virtual
virtualenv .venv

# Ahora puede cargar el entorno virtual
source .venv/bin/activate
```

2. Para instalar todas las librerias ejecute el siguiente comando:
```
pip3 install -r requirements.txt
```


## Uso

Este raspador esta desarrollado con [Scrapy](https://scrapy.org/), puede leer mas sobre el funcionamiento de este Framework [aqui](https://docs.scrapy.org/en/latest/)

### Lista de productos a raspar

El archivo `src/products.xlsx` contiene la lista de productos que se rasparan. Puede eliminar o agregar nuevos productos, sin embargo debera mantener la misma estructa de la tabla, esto para evitar errores en el raspador.

---

### Listar las spiders disponibles

Cada `spider` se encarga de raspar un sitio web especifico, en el directorio `src/scraper/spiders/` podra encontrar todas las spiders.
```bash
# Ingrese al directorio `src/` dentro del proyecto.
cd src/

# Ahora ejecute el siguiente comando para listar las spiders
scrapy list

# amazon.ae
# firstcry.ae
# lego.saudiblocks.com
# lego.yellowblocks.me
# toysrusmena.com
```

---

### Ejecutar una spider

Para raspar la informacion de alguno de los sitios web, debera iniciar su spider con el siguiente comando:

```bash
scrapy crawl amazon.ae
```

La spider comenzara el raspado de informacion y al terminar creara un archivo `CSV` en el directorio `results/`. Dicho archivo contendra toda la informacion raspada.

```bash
results/
└── amazon.ae.csv
```

NOTA: Este archivo se remplaza en cada ejecucion, si es necesario haga una copia de seguridad de cada archivo, antes de volver a ejecutar el raspador.

---

### Generar DataTable

Para generar el archivo HTML que contega la tabla con toda la informacion, debera ejecutar el siguiente comando:
```bash
python3 utils/gen_table.py
```

Al ejecutar este script, se creara un archivo `index.html` con la tabla. Este archivo se genera utilizando la plantilla `templates/table.html`, puede editar esta plantilla para cambiar el diseño de la tabla.
