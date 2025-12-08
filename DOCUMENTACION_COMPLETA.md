# Modo de Empleo del Sistema de Tutorías

Esta sección detalla los pasos necesarios para instalar, ejecutar y utilizar el sistema de gestión de tutorías.

## 1. Requerimientos del Sistema

El proyecto está desarrollado en Python y utiliza el microframework Flask. Los requerimientos mínimos son:

*   **Python 3.6+** (Se recomienda la última versión estable).
*   **Git** (Para clonar el repositorio).
*   **Pip** (Gestor de paquetes de Python).
*   **SQLite3** (Base de datos ligera, incluida en la librería estándar de Python. No requiere instalación adicional).

## 2. Instalación y Ejecución

Siga los siguientes pasos para poner en marcha el sistema. **Es altamente recomendable utilizar un entorno virtual** para aislar las dependencias del proyecto:

### Paso 2.1: Clonar el Repositorio

Abra su terminal o línea de comandos y clone el repositorio de GitHub:

```bash
git clone https://github.com/AxelLangle/TUTORIAS
cd TUTORIAS
```

### Paso 2.2: Crear y Activar Entorno Virtual

Antes de instalar dependencias, cree y active un entorno virtual:

```bash
# Crear entorno virtual (solo la primera vez)
python -m venv venv

# Activar el entorno virtual (Windows)
.\venv\Scripts\activate

# Activar el entorno virtual (Linux/macOS)
source venv/bin/activate
```

### Paso 2.3: Instalar Dependencias

Con el entorno virtual activado, instale las librerías listadas en `requirements.txt`:

```bash
pip install -r requirements.txt
```

Las librerías clave incluyen `Flask` (para el servidor web), `reportlab` (para la generación de PDF) y `pandas` (para análisis de datos). **Nota**: El módulo `sqlite3` no está incluido en `requirements.txt` porque es parte de la librería estándar de Python y su instalación por `pip` genera el error que has encontrado.

#### Paso 2.4: Ejecutar la Aplicación

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
# Documentación del Módulo Principal: `app.py`

El archivo `app.py` es el corazón del sistema, implementado con el microframework **Flask** y utilizando **SQLite** como base de datos. Contiene la lógica de inicialización, autenticación, registro de datos, consultas y las nuevas funcionalidades de análisis y reportes.

## 1. Inicialización y Configuración

| Función | Descripción | Lógica Detrás |
| :--- | :--- | :--- |
| `get_db()` | **Conexión a la Base de Datos** | Establece una conexión a la base de datos `asesorias.db` utilizando `sqlite3`. Configura `row_factory` para que las filas se devuelvan como diccionarios, facilitando el acceso a los datos por nombre de columna. |
| `@app.teardown_appcontext close_connection(exception)` | **Cierre de Conexión** | Asegura que la conexión a la base de datos se cierre automáticamente al finalizar cada contexto de aplicación, liberando recursos. |
| `init_db()` | **Inicialización de Tablas** | Crea las tablas necesarias (`usuarios`, `asesoria`, `tutoria`, `tutoria_grupal`) si no existen. Esta función se ejecuta al inicio de la aplicación. |

## 2. Autenticación y Usuarios

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `login_required(f)` | Decorador | Decorador de Flask que verifica si el usuario ha iniciado sesión (`'usuario'` en `session`). Si no, redirige a la página de login. |
| `login()` | `/login` | Maneja el inicio de sesión. En `POST`, consulta la tabla `usuarios` con el nombre de usuario y contraseña. Si son correctos, establece la sesión y redirige al índice. |
| `logout()` | `/logout` | Limpia la sesión del usuario y redirige a la página de login. |
| `register_user()` | `/register_user` | Maneja el registro de nuevos usuarios. **Lógica de Validación**: Utiliza una expresión regular (`re.fullmatch`) para asegurar que solo se permitan correos institucionales con el dominio `@uptecamac.edu.mx`. |

## 3. Rutas de Registro y Dashboard

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `index()` | `/` o `/index` | **Dashboard**. Recupera el conteo total de asesorías, tutorías individuales y grupales. Realiza consultas SQL con `strftime('%m', fecha)` para agrupar los registros por mes y preparar los datos para la visualización de gráficos en el *dashboard*. |
| `register_asesoria()` | `/register/asesoria` | Registra una nueva asesoría en la tabla `asesoria`. |
| `register_tutoria()` | `/register/tutoria` | Registra una nueva tutoría individual en la tabla `tutoria`. |
| `register_tutoria_grupal()` | `/register/tutoria_grupal` | Registra una nueva tutoría grupal en la tabla `tutoria_grupal`. |

## 4. Consultas, Edición y Eliminación

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `consultas()` | `/consultas` | Muestra todos los registros de asesorías y tutorías. Implementa lógica de **filtrado y búsqueda** basada en los parámetros `tipo` y `busqueda` de la URL, utilizando consultas SQL con `LIKE` para búsquedas parciales. |
| `eliminar_asesoria()`, `eliminar_tutoria()`, `eliminar_tutoria_grupal()` | `/eliminar_.../<int:id>` | Rutas POST para eliminar registros específicos de sus respectivas tablas por `id`. |
| `editar_asesoria()`, `editar_tutoria()`, `editar_tutoria_grupal()` | `/editar_.../<int:id>` | Rutas GET/POST para recuperar y actualizar los datos de un registro específico en la base de datos. |

## 5. Nuevas Funcionalidades (Implementadas)

### 5.1 Panel de Riesgo Académico

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `dashboard_risk()` | `/dashboard/risk` | **Panel de Control de Riesgo**. 1. Obtiene todos los estudiantes únicos de la tabla `tutoria`. 2. Por cada estudiante, calcula el número de inasistencias y bajas calificaciones (basado en el campo `motivo`). 3. Utiliza el motor `RiskAssessmentEngine` para evaluar el riesgo de cada estudiante. 4. Aplica filtros de búsqueda y nivel de riesgo. 5. Genera estadísticas y separa a los estudiantes en listas de **Alto**, **Medio** y **Bajo** riesgo para la visualización. |

### 5.2 Historial Académico de Estudiantes

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `student_history()` | `/student/<int:student_id>/history` | **Vista Detallada del Historial**. 1. Obtiene todas las tutorías de un estudiante específico. 2. Utiliza el analizador `AcademicHistoryAnalyzer` para: a) Agrupar tutorías por cuatrimestre. b) Detectar patrones de reincidencia y mejoras. c) Preparar datos para los gráficos de frecuencia y motivos. 3. Renderiza la plantilla con el análisis completo. |

### 5.3 Generación de Reportes PDF

| Función | Ruta | Lógica Detrás |
| :--- | :--- | :--- |
| `report_student()` | `/report/student/<int:student_id>` | Genera un reporte PDF detallado para un estudiante. Recupera todas las tutorías del estudiante y utiliza `PDFReportGenerator.generate_student_report()` para crear y devolver el archivo PDF. |
| `report_group()` | `/report/group/<int:group_id>` | Genera un reporte PDF para un grupo. Recupera todas las tutorías grupales y utiliza `PDFReportGenerator.generate_group_report()`. |
| `report_period()` | `/report/period` | **Formulario y Generación de Reporte por Período**. Permite al usuario seleccionar un rango de fechas y filtros opcionales (carrera, cuatrimestre). Construye una consulta SQL dinámica y utiliza `PDFReportGenerator.generate_period_report()` para generar el PDF con los resultados. |
# Documentación del Módulo de Generación de PDF: `pdf_generator.py`

El módulo `pdf_generator.py` encapsula la lógica para crear reportes en formato PDF utilizando la librería **ReportLab**. Su objetivo es proporcionar una salida formal y estructurada de los datos de tutorías para su archivo o presentación.

## Clase Principal: `PDFReportGenerator`

Esta clase maneja la configuración del documento y los métodos de generación de contenido.

| Método | Descripción | Lógica Detrás |
| :--- | :--- | :--- |
| `__init__` | **Constructor** | Inicializa la configuración básica del documento (tamaño de página `letter`, márgenes, ancho de contenido). |
| `_create_header(story, title, subtitle)` | **Encabezado** | Crea el encabezado del PDF, incluyendo el título principal, el nombre de la institución y un subtítulo opcional. Utiliza estilos de color corporativo (`#cc1313`) para el título. |
| `_create_info_table(story, info_dict)` | **Tabla de Información** | Genera una tabla de dos columnas para mostrar información clave (ej. datos del estudiante, filtros de período). Utiliza un color de fondo (`#e0f7fa`) para la primera columna para destacar las etiquetas. |
| `_create_data_table(story, headers, data, title)` | **Tabla de Datos** | Genera una tabla detallada para listar los registros de tutorías. Aplica un estilo de encabezado con el color principal (`#cc1313`) y filas alternas para mejorar la legibilidad. |
| `_create_summary_section(story, summary_dict)` | **Sección de Resumen** | Crea una sección para mostrar estadísticas clave (ej. total de tutorías, motivos principales). |
| `_create_footer(story, tutor_name, date_generated)` | **Pie de Página** | Crea el pie de página con la fecha de generación, el nombre del tutor (si aplica) y el nombre del sistema. |
| `_get_main_motives(tutorias, limit=3)` | **Motivos Principales** | Método estático que analiza una lista de tutorías, cuenta la frecuencia de los motivos y devuelve los 3 más comunes en formato de cadena. |

## Métodos de Generación de Reportes

| Método | Propósito | Contenido del Reporte |
| :--- | :--- | :--- |
| `generate_student_report(student_data, tutorias)` | **Reporte Individual** | Genera un PDF con la información del estudiante, un resumen de sus tutorías y una tabla detallada de todos los registros de tutoría individual. |
| `generate_group_report(group_data, tutorias_grupales)` | **Reporte Grupal** | Genera un PDF con la información del grupo y una tabla detallada de todas las tutorías grupales registradas. |
| `generate_period_report(period_data, tutorias)` | **Reporte por Período** | Genera un PDF que resume las tutorías individuales registradas dentro de un rango de fechas y filtros específicos. Incluye una tabla con la fecha, el estudiante, el motivo y el tipo de tutoría. |
# Documentación del Módulo de Historial Académico: `academic_history.py`

El módulo `academic_history.py` contiene la clase `AcademicHistoryAnalyzer`, diseñada para procesar los datos brutos de tutorías de un estudiante y transformarlos en información analítica que permite detectar patrones, mejoras y áreas de riesgo.

## Clase Principal: `AcademicHistoryAnalyzer`

| Método | Descripción | Lógica Detrás |
| :--- | :--- | :--- |
| `MOTIVO_CATEGORIES` | **Constante** | Diccionario utilizado para **normalizar** los motivos de tutoría (ej. 'baja calificación', 'bajo desempeño') a categorías generales (ej. 'Baja Calificación'). Esto es crucial para la detección de reincidencias. |
| `_normalize_motivo(motivo)` | **Normalización** | Función auxiliar que toma un motivo de texto libre y lo mapea a una de las `MOTIVO_CATEGORIES` definidas. |
| `agrupar_por_cuatrimestre(tutorias)` | **Agrupación** | Agrupa todas las tutorías del estudiante por el campo `cuatrimestre`. El resultado se ordena de forma descendente por cuatrimestre para mostrar la información más reciente primero. |
| `contar_motivos(tutorias)` | **Conteo de Frecuencia** | Cuenta la frecuencia de cada **motivo normalizado** en el historial completo del estudiante. |
| `detectar_mejoras(por_cuatrimestre)` | **Análisis de Tendencia** | Compara la frecuencia de tutorías entre los dos cuatrimestres más recientes. Si la frecuencia del último cuatrimestre es menor que la del anterior, se detecta una **mejora** en la tendencia. |
| `detectar_reincidencias(tutorias, umbral=3)` | **Detección de Patrones** | Identifica motivos que se repiten un número de veces igual o superior al `umbral` (por defecto, 3). Clasifica la severidad como `media` o `alta` (si la repetición es >= 5). |
| `calcular_estadisticas_cuatrimestre(tutorias_cuatrimestre)` | **Estadísticas por Cuatrimestre** | Calcula el total de tutorías y el motivo principal dentro de un cuatrimestre específico. |
| `generar_analisis_completo(tutorias)` | **Motor de Análisis** | Función principal que coordina todos los métodos anteriores para producir un *dict* completo con: total de tutorías, agrupación por cuatrimestre, estadísticas detalladas, mejoras, reincidencias y alertas. |
| `_generar_alertas(...)` | **Generación de Alertas** | Crea mensajes de alerta basados en los resultados del análisis (ej. "Reincidencia crítica", "Tendencia de empeoramiento", "Mejora detectada"). |
| `obtener_datos_grafico_frecuencia(...)` | **Datos para Gráfico** | Formatea los datos de frecuencia de tutorías por cuatrimestre para ser consumidos por Chart.js en el frontend. |
| `obtener_datos_grafico_motivos(...)` | **Datos para Gráfico** | Formatea los datos de los motivos principales para ser consumidos por Chart.js. |
# Documentación del Módulo de Evaluación de Riesgo: `risk_assessment.py`

El módulo `risk_assessment.py` implementa el **Panel Inteligente de Riesgo Académico** mediante la clase `RiskAssessmentEngine`. Su función principal es asignar una puntuación de riesgo a cada estudiante basada en criterios ponderados y clasificarlo en niveles de riesgo (Alto, Medio, Bajo).

## Clase Principal: `RiskAssessmentEngine`

### 1. Criterios de Ponderación

La clasificación se basa en la suma de puntuaciones obtenidas de cuatro criterios principales.

| Criterio | Lógica de Ponderación | Puntuación Máxima |
| :--- | :--- | :--- |
| **Motivos de Tutoría** | Suma de pesos predefinidos para cada motivo de tutoría (ej. 'baja calificación' = 3, 'inasistencias' = 3). | Variable |
| **Frecuencia de Tutorías** | Puntuación basada en el número total de tutorías: <ul><li>Alto (>= 5 tutorías) = 8 puntos</li><li>Medio (3-4 tutorías) = 4 puntos</li><li>Bajo (1-2 tutorías) = 1 punto</li></ul> | 8 |
| **Inasistencias** | Puntuación basada en el número de inasistencias registradas: <ul><li>Alto (>= 3) = 6 puntos</li><li>Medio (1-2) = 3 puntos</li><li>Bajo (0) = 0 puntos</li></ul> | 6 |
| **Bajas Calificaciones** | Puntuación basada en el número de bajas calificaciones registradas: <ul><li>Alto (>= 3) = 6 puntos</li><li>Medio (1-2) = 3 puntos</li><li>Bajo (0) = 0 puntos</li></ul> | 6 |

### 2. Clasificación de Riesgo

La puntuación total determina el nivel de riesgo:

| Nivel de Riesgo | Puntuación Requerida | Color | Recomendación |
| :--- | :--- | :--- | :--- |
| **Alto Riesgo** | **>= 15** | Rojo (🔴) | Intervención Urgente y seguimiento intensivo. |
| **Medio Riesgo** | **>= 8** | Amarillo (🟡) | Monitoreo Regular y seguimiento académico. |
| **Bajo Riesgo** | **< 8** | Verde (🟢) | Desempeño Satisfactorio. |

### 3. Métodos Principales

| Método | Descripción | Lógica Detrás |
| :--- | :--- | :--- |
| `calcular_puntuacion_riesgo(...)` | **Motor de Puntuación** | Calcula la puntuación total sumando los pesos de los cuatro criterios. Llama a los métodos auxiliares `_calcular_peso_motivos`, `_calcular_peso_frecuencia`, etc. |
| `clasificar_riesgo(puntuacion)` | **Clasificación** | Asigna el nivel de riesgo (Alto, Medio, Bajo) y el código de color basado en la puntuación total. |
| `evaluar_estudiante(...)` | **Evaluación Individual** | Realiza una evaluación completa de un estudiante, devolviendo la puntuación, la clasificación y los motivos frecuentes. |
| `evaluar_multiples_estudiantes(...)` | **Evaluación Masiva** | Itera sobre una lista de estudiantes, evalúa el riesgo de cada uno y devuelve una lista ordenada por puntuación de riesgo (descendente). |
| `generar_estadisticas_riesgo(...)` | **Estadísticas** | Calcula el total de estudiantes en cada nivel de riesgo (Alto, Medio, Bajo) y el porcentaje correspondiente, además del promedio de puntuación. |
| `filtrar_evaluaciones(...)` | **Filtros** | Permite filtrar la lista de evaluaciones por nivel de riesgo, carrera, cuatrimestre y búsqueda de texto, facilitando la gestión en el panel de control. |
