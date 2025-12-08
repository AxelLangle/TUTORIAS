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
