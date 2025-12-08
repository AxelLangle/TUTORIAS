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
