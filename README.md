# MUIX Dashboard Launcher

Lanzador y centro de control minimalista diseñado para entornos ligeros e interfaces dedicadas.

---

## Propósito del Proyecto

MUIX es una interfaz de usuario ligera desarrollada en Python y PySide6 optimizada para ejecutarse a pantalla completa en sistemas empotrados o minimalistas (como Ubuntu Server con Openbox sin un entorno de escritorio completo). Su objetivo es transformar un equipo en un centro multimedia estilo TV Box, permitiendo lanzar tanto aplicaciones web (WebApps) integradas como comandos del sistema de forma simple, directa y controlada.

---

## Características Principales

* **Visualización optimizada para pantallas grandes**: Cuadrícula de accesos centrada y limpia, ideal para televisores y monitores a distancia.
* **Navegador web embebido**: Soporte integrado para WebApps en una ventana única que restringe la multitarea clásica, garantizando un flujo de interacción continuo.
* **Control total por teclado**: Navegación bidireccional por flechas direccionales que cubre tanto los elementos de la cuadrícula como los botones del sistema.
* **Atajos de teclado rápidos**:
  * **F1**: Añadir un nuevo acceso.
  * **Enter / Espacio**: Lanzar la aplicación seleccionada.
  * **E**: Editar el acceso seleccionado.
  * **Suprimir**: Eliminar el acceso seleccionado.
  * **Shift + Flechas**: Reordenar la posición del acceso en la cuadrícula de forma interactiva.
  * **Escape**: Cerrar una WebApp y retornar al dashboard principal.
* **Descarga automática de favicons**: Búsqueda e integración automática del icono original de los sitios web al agregar un enlace de WebApp.
* **Diseño minimalista de alto contraste**: Interfaz oscura en negro puro con detalles lineales en blanco y bordes rectangulares sin curvas.
* **Persistencia local ligera**: Guardado de configuraciones estructurado en un archivo JSON local aislado del repositorio de Git.

---

## Requisitos de Ejecución

* Sistema operativo Linux (probado en entornos X11 / Openbox).
* Python 3.10 o superior.
* PySide6 y PySide6-WebEngine.

---

## Instrucciones de Instalación y Uso

1. Instalar las dependencias declaradas:
   ```bash
   pip install -r requirements.txt
   ```

2. Ejecutar la aplicación en modo interactivo:
   ```bash
   ./run.sh
   ```

Al iniciarse por primera vez sin configuraciones previas, el sistema creará de forma dinámica un archivo local (`accesos.json`) inicializado con un acceso de muestra hacia la plataforma de YouTube.
