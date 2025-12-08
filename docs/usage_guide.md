# Modo de Empleo del Sistema de Tutorías

Esta sección detalla los pasos necesarios para instalar, ejecutar y utilizar el sistema de gestión de tutorías.

## 1. Requerimientos del Sistema

El proyecto está desarrollado en Python y utiliza el microframework Flask. Los requerimientos mínimos son:

*   **Python 3.6+** (Se recomienda la última versión estable).
*   **Git** (Para clonar el repositorio).
*   **Pip** (Gestor de paquetes de Python).
*   **SQLite3** (Base de datos ligera, no requiere instalación adicional si se usa Python estándar).

## 2. Instalación y Ejecución

Siga los siguientes pasos para poner en marcha el sistema:

### Paso 2.1: Clonar el Repositorio

Abra su terminal o línea de comandos y clone el repositorio de GitHub:

```bash
git clone https://github.com/AxelLangle/TUTORIAS
cd TUTORIAS
```

### Paso 2.2: Instalar Dependencias

El proyecto utiliza las librerías listadas en `requirements.txt`. Instálelas usando pip:

```bash
pip install -r requirements.txt
```

Las librerías clave incluyen `Flask` (para el servidor web), `reportlab` (para la generación de PDF) y `pandas` (para análisis de datos).

### Paso 2.3: Ejecutar la Aplicación

Una vez instaladas las dependencias, ejecute el archivo principal `app.py`:

```bash
python3 app.py
```

El sistema se iniciará y estará disponible en su navegador en la dirección: `http://127.0.0.1:5000/` (o la dirección que indique la consola).

## 3. Uso del Sistema

### 3.1. Autenticación

Al acceder por primera vez, debe registrar un usuario.

*   **Registro**: Vaya a la ruta `/register_user`.
    *   **Validación**: El sistema solo permite el registro con correos institucionales que terminen en `@uptecamac.edu.mx`.
*   **Inicio de Sesión**: Utilice el usuario y contraseña registrados para acceder al sistema.

### 3.2. Ingreso de Datos (Ejemplo: Tutoría Individual)

Para que las funcionalidades de Historial y Riesgo funcionen, es fundamental ingresar datos de tutorías.

1.  Navegue a la ruta de registro de tutorías (ej. a través del menú principal).
2.  Complete el formulario con la siguiente información:

| Campo | Ejemplo de Dato | Importancia para el Análisis |
| :--- | :--- | :--- |
| **Nombre** | Juan | Identificación del estudiante. |
| **Matrícula** | 1234567890 | Identificación única. |
| **Cuatrimestre** | 7 | Usado para agrupar el historial. |
| **Motivo** | Baja calificación en Matemáticas | **CRÍTICO**: Usado para la detección de reincidencias y el cálculo de riesgo. |
| **Fecha** | 2025-11-01 | Usado para el análisis de tendencia y reportes por período. |

**Nota sobre el campo `Motivo`**: La lógica de riesgo y reincidencia se basa en palabras clave dentro de este campo (ej. "inasistencia", "baja calificación", "bajo desempeño"). Sea descriptivo pero use términos consistentes.

### 3.3. Acceso a las Nuevas Funcionalidades

Una vez que haya ingresado datos, puede acceder a las nuevas secciones:

| Funcionalidad | Ruta de Acceso | Propósito |
| :--- | :--- | :--- |
| **Panel de Riesgo Académico** | `/dashboard/risk` | Visualización general de la población estudiantil clasificada por riesgo (Rojo, Amarillo, Verde). |
| **Historial Académico** | `/student/<id>/history` | Vista detallada del historial de un estudiante, con análisis de patrones y alertas. (Accedido desde la tabla de consultas o el panel de riesgo). |
| **Reporte por Período (PDF)** | `/report/period` | Generación de un reporte PDF consolidado de tutorías individuales con filtros de fecha. |
