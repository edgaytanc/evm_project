# EVM Web Application

## Descripción del Proyecto

Esta aplicación web permite a los gerentes de proyectos calcular y visualizar métricas clave de **Earned Value Management (EVM)** para proyectos de hasta 24 semanas. La aplicación facilita la entrada de datos, cálculos automáticos de métricas como el **CPI** y **SPI**, y la generación de gráficos para monitorear el desempeño del proyecto. Además, se pueden exportar informes en **PDF** y **CSV**.

### Funcionalidades Principales:
- **Cálculo de EVM**: Calcula el Cost Performance Index (CPI) y el Schedule Performance Index (SPI) basado en los datos ingresados.
- **Visualización**: Muestra gráficos que representan el rendimiento del proyecto.
- **Exportación**: Exporta informes en formatos PDF y CSV.
- **Gestión de Proyectos**: Permite la creación, edición y visualización de proyectos.

---

## Instalación del Proyecto

### 1. Clonar desde GitHub

Para instalar el proyecto desde GitHub, sigue estos pasos:

```bash
# Clona el repositorio
git clone https://github.com/usuario/repo.git

# Navega al directorio del proyecto
cd nombre-del-proyecto

# Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Instala las dependencias del proyecto
pip install -r requirements.txt

# Realiza las migraciones de la base de datos
python manage.py migrate

# Crea un superusuario
python manage.py createsuperuser

# Inicia el servidor
python manage.py runserver

# Extrae el archivo comprimido
unzip nombre-del-archivo.zip  # Para archivos ZIP
tar -xvzf nombre-del-archivo.tar.gz  # Para archivos TAR

# Navega al directorio del proyecto
cd nombre-del-proyecto

# Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Instala las dependencias
pip install -r requirements.txt

# Realiza las migraciones de la base de datos
python manage.py migrate

# Crea un superusuario
python manage.py createsuperuser

# Inicia el servidor
python manage.py runserver


### Explicación:
- **Descripción del Proyecto**: Explica de qué trata la aplicación y sus funcionalidades.
- **Instalación del Proyecto**: Incluye instrucciones para clonar desde GitHub o descargar y extraer un archivo comprimido.
- **Guía para Windows, Linux, y Mac**: Proporciona pasos detallados para cada sistema operativo, desde la creación de un entorno virtual hasta la ejecución del servidor.
- **Dependencias**: Lista las bibliotecas clave necesarias para el proyecto.
- **Contribuir**: Describe cómo otros pueden contribuir al proyecto.
- **Licencia**: Proporciona un enlace a la licencia del proyecto.

Este archivo README proporciona toda la información clave necesaria para entender, instalar y ejecutar el proyecto. Si necesitas hacer ajustes o agregar más detalles, ¡avísame!
