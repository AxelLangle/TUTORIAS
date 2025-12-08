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
