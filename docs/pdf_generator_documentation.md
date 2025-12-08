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
