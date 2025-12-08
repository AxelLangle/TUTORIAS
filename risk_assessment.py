"""
Módulo de Evaluación de Riesgo Académico
Proporciona funciones para clasificar estudiantes según su nivel de riesgo académico
"""

from collections import defaultdict
from datetime import datetime, timedelta

class RiskAssessmentEngine:
    """Motor de evaluación de riesgo académico"""
    
    # Pesos y criterios de clasificación
    MOTIVO_PESOS = {
        'baja calificación': 3,
        'inasistencias': 3,
        'problemas de conducta': 2,
        'reforzamiento de materia': 1,
        'asesoría general': 1,
        'bajo desempeño': 3,
        'falta de motivación': 2,
        'dificultades académicas': 2,
    }
    
    FRECUENCIA_THRESHOLDS = {
        'alto': 5,      # >= 5 tutorías
        'medio': 3,     # 3-4 tutorías
        'bajo': 1       # 1-2 tutorías
    }
    
    INASISTENCIA_THRESHOLDS = {
        'alto': 3,      # >= 3
        'medio': 1,     # 1-2
        'bajo': 0       # 0
    }
    
    BAJAS_CALIFICACIONES_THRESHOLDS = {
        'alto': 3,      # >= 3
        'medio': 1,     # 1-2
        'bajo': 0       # 0
    }
    
    def __init__(self):
        pass
    
    def calcular_desglose_puntuacion(self, tutorias, inasistencias=0, bajas_calificaciones=0):
        """
        Calcula el desglose detallado de la puntuación de riesgo
        
        Returns:
            dict: Desglose con puntuación por indicador
        """
        desglose = {
            'motivos': 0,
            'frecuencia': 0,
            'inasistencias': 0,
            'bajas_calificaciones': 0,
            'total': 0
        }
        
        # 1. Puntuación por motivos
        for tutoria in tutorias:
            motivo = tutoria.get('motivo', '').lower()
            for key, peso in self.MOTIVO_PESOS.items():
                if key in motivo:
                    desglose['motivos'] += peso
                    break
            else:
                desglose['motivos'] += 1
        
        # 2. Puntuación por frecuencia
        num_tutorias = len(tutorias)
        if num_tutorias >= 7:
            desglose['frecuencia'] = 8
        elif num_tutorias >= 5:
            desglose['frecuencia'] = 6
        elif num_tutorias >= 3:
            desglose['frecuencia'] = 3
        elif num_tutorias >= 1:
            desglose['frecuencia'] = 1
        
        # 3. Puntuación por inasistencias
        if inasistencias >= 3:
            desglose['inasistencias'] = 6
        elif inasistencias >= 2:
            desglose['inasistencias'] = 4
        elif inasistencias >= 1:
            desglose['inasistencias'] = 2
        
        # 4. Puntuación por bajas calificaciones
        if bajas_calificaciones >= 3:
            desglose['bajas_calificaciones'] = 6
        elif bajas_calificaciones >= 2:
            desglose['bajas_calificaciones'] = 4
        elif bajas_calificaciones >= 1:
            desglose['bajas_calificaciones'] = 2
        
        desglose['total'] = sum([desglose['motivos'], desglose['frecuencia'], 
                                desglose['inasistencias'], desglose['bajas_calificaciones']])
        
        return desglose
    
    def calcular_puntuacion_riesgo(self, tutorias, inasistencias=0, bajas_calificaciones=0):
        """
        Calcula la puntuación de riesgo de un estudiante
        
        Args:
            tutorias: Lista de tutorías del estudiante
            inasistencias: Número de inasistencias registradas
            bajas_calificaciones: Número de bajas calificaciones registradas
        
        Returns:
            Dict con puntuación y detalles
        """
        puntuacion = 0
        detalles = {
            'motivos_peso': 0,
            'frecuencia_peso': 0,
            'inasistencias_peso': 0,
            'bajas_calificaciones_peso': 0,
            'total': 0
        }
        
        # 1. Calcular peso por motivos
        motivos_peso = self._calcular_peso_motivos(tutorias)
        detalles['motivos_peso'] = motivos_peso
        puntuacion += motivos_peso
        
        # 2. Calcular peso por frecuencia
        frecuencia_peso = self._calcular_peso_frecuencia(len(tutorias))
        detalles['frecuencia_peso'] = frecuencia_peso
        puntuacion += frecuencia_peso
        
        # 3. Calcular peso por inasistencias
        inasistencias_peso = self._calcular_peso_inasistencias(inasistencias)
        detalles['inasistencias_peso'] = inasistencias_peso
        puntuacion += inasistencias_peso
        
        # 4. Calcular peso por bajas calificaciones
        bajas_calificaciones_peso = self._calcular_peso_bajas_calificaciones(bajas_calificaciones)
        detalles['bajas_calificaciones_peso'] = bajas_calificaciones_peso
        puntuacion += bajas_calificaciones_peso
        
        detalles['total'] = puntuacion
        
        return detalles
    
    def _calcular_peso_motivos(self, tutorias):
        """Calcula el peso según los motivos de las tutorías"""
        peso = 0
        motivos_encontrados = set()
        
        for tutoría in tutorias:
            motivo = tutoría.get('motivo', '').lower()
            
            # Buscar coincidencia con palabras clave
            for palabra_clave, peso_motivo in self.MOTIVO_PESOS.items():
                if palabra_clave in motivo:
                    if motivo not in motivos_encontrados:
                        peso += peso_motivo
                        motivos_encontrados.add(motivo)
                    break
        
        return peso
    
    def _calcular_peso_frecuencia(self, num_tutorias):
        """Calcula el peso según la frecuencia de tutorías"""
        if num_tutorias >= self.FRECUENCIA_THRESHOLDS['alto']:
            return 8  # Alto riesgo
        elif num_tutorias >= self.FRECUENCIA_THRESHOLDS['medio']:
            return 4  # Medio riesgo
        else:
            return 1  # Bajo riesgo
    
    def _calcular_peso_inasistencias(self, num_inasistencias):
        """Calcula el peso según el número de inasistencias"""
        if num_inasistencias >= self.INASISTENCIA_THRESHOLDS['alto']:
            return 6  # Alto riesgo
        elif num_inasistencias >= self.INASISTENCIA_THRESHOLDS['medio']:
            return 3  # Medio riesgo
        else:
            return 0  # Bajo riesgo
    
    def _calcular_peso_bajas_calificaciones(self, num_bajas_calificaciones):
        """Calcula el peso según el número de bajas calificaciones"""
        if num_bajas_calificaciones >= self.BAJAS_CALIFICACIONES_THRESHOLDS['alto']:
            return 6  # Alto riesgo
        elif num_bajas_calificaciones >= self.BAJAS_CALIFICACIONES_THRESHOLDS['medio']:
            return 3  # Medio riesgo
        else:
            return 0  # Bajo riesgo
    
    def clasificar_riesgo(self, puntuacion):
        """
        Clasifica el nivel de riesgo basado en la puntuación
        
        Args:
            puntuacion: Puntuación total de riesgo
        
        Returns:
            Dict con nivel, color y descripción
        """
        if puntuacion >= 15:
            return {
                'nivel': 'alto',
                'color': '#cc1313',
                'color_hex': 'red',
                'icono': '🔴',
                'descripcion': 'Alto Riesgo - Intervención Urgente',
                'recomendacion': 'Se recomienda intervención inmediata y seguimiento intensivo'
            }
        elif puntuacion >= 8:
            return {
                'nivel': 'medio',
                'color': '#ff9800',
                'color_hex': 'orange',
                'icono': '🟡',
                'descripcion': 'Medio Riesgo - Monitoreo Requerido',
                'recomendacion': 'Se recomienda monitoreo regular y seguimiento académico'
            }
        else:
            return {
                'nivel': 'bajo',
                'color': '#4caf50',
                'color_hex': 'green',
                'icono': '🟢',
                'descripcion': 'Bajo Riesgo - Desempeño Satisfactorio',
                'recomendacion': 'Continuar con el seguimiento académico regular'
            }
    
    def evaluar_estudiante(self, student_data, tutorias, inasistencias=0, bajas_calificaciones=0):
        """
        Realiza una evaluación completa de riesgo para un estudiante
        
        Args:
            student_data: Dict con información del estudiante
            tutorias: Lista de tutorías
            inasistencias: Número de inasistencias
            bajas_calificaciones: Número de bajas calificaciones
        
        Returns:
            Dict con evaluación completa
        """
        # Calcular puntuación
        detalles_puntuacion = self.calcular_puntuacion_riesgo(tutorias, inasistencias, bajas_calificaciones)
        
        # Calcular desglose de puntuación
        desglose = self.calcular_desglose_puntuacion(tutorias, inasistencias, bajas_calificaciones)
        
        # Clasificar riesgo
        clasificacion = self.clasificar_riesgo(detalles_puntuacion['total'])
        
        # Obtener motivos principales
        motivos_principales = self._obtener_motivos_principales(tutorias)
        
        return {
            'student_id': student_data.get('student_id', None),
            'matricula': student_data.get('matricula', 'N/A'),
            'nombre': student_data.get('nombre', 'N/A'),
            'apellido_p': student_data.get('apellido_p', 'N/A'),
            'apellido_m': student_data.get('apellido_m', 'N/A'),
            'carrera': student_data.get('carrera', 'N/A'),
            'cuatrimestre': student_data.get('cuatrimestre', 'N/A'),
            'puntuacion': detalles_puntuacion['total'],
            'detalles_puntuacion': detalles_puntuacion,
            'desglose_puntuacion': desglose,
            'clasificacion': clasificacion,
            'motivos_frecuentes': motivos_principales,
            'num_tutorias': len(tutorias),
            'num_inasistencias': inasistencias,
            'num_bajas_calificaciones': bajas_calificaciones,
            'fecha_evaluacion': datetime.now().isoformat()
        }
    
    def _obtener_motivos_principales(self, tutorias, limit=3):
        """Obtiene los motivos principales de tutorías"""
        motivos = defaultdict(int)
        
        for tutoría in tutorias:
            motivo = tutoría.get('motivo', 'N/A')
            motivos[motivo] += 1
        
        motivos_ordenados = sorted(motivos.items(), key=lambda x: x[1], reverse=True)
        return [m[0] for m in motivos_ordenados[:limit]]
    
    def evaluar_multiples_estudiantes(self, estudiantes_data):
        """
        Evalúa múltiples estudiantes
        
        Args:
            estudiantes_data: Lista de dicts con información de estudiantes
        
        Returns:
            Lista de evaluaciones ordenadas por puntuación de riesgo
        """
        evaluaciones = []
        
        for student in estudiantes_data:
            evaluacion = self.evaluar_estudiante(
                student.get('info', {}),
                student.get('tutorias', []),
                student.get('inasistencias', 0),
                student.get('bajas_calificaciones', 0)
            )
            evaluaciones.append(evaluacion)
        
        # Ordenar por puntuación descendente
        return sorted(evaluaciones, key=lambda x: x['puntuacion'], reverse=True)
    
    def generar_estadisticas_riesgo(self, evaluaciones):
        """
        Genera estadísticas generales de riesgo
        
        Args:
            evaluaciones: Lista de evaluaciones de estudiantes
        
        Returns:
            Dict con estadísticas
        """
        if not evaluaciones:
            return {
                'total_estudiantes': 0,
                'alto_riesgo': 0,
                'medio_riesgo': 0,
                'bajo_riesgo': 0,
                'porcentaje_alto': 0,
                'porcentaje_medio': 0,
                'porcentaje_bajo': 0,
                'promedio_puntuacion': 0
            }
        
        total = len(evaluaciones)
        alto = sum(1 for e in evaluaciones if e['clasificacion']['nivel'] == 'alto')
        medio = sum(1 for e in evaluaciones if e['clasificacion']['nivel'] == 'medio')
        bajo = sum(1 for e in evaluaciones if e['clasificacion']['nivel'] == 'bajo')
        
        promedio_puntuacion = sum(e['puntuacion'] for e in evaluaciones) / total if total > 0 else 0
        
        return {
            'total_estudiantes': total,
            'alto_riesgo': alto,
            'medio_riesgo': medio,
            'bajo_riesgo': bajo,
            'porcentaje_alto': round((alto / total) * 100, 2) if total > 0 else 0,
            'porcentaje_medio': round((medio / total) * 100, 2) if total > 0 else 0,
            'porcentaje_bajo': round((bajo / total) * 100, 2) if total > 0 else 0,
            'promedio_puntuacion': round(promedio_puntuacion, 2)
        }
    
    def filtrar_evaluaciones(self, evaluaciones, filtros):
        """
        Filtra evaluaciones según criterios
        
        Args:
            evaluaciones: Lista de evaluaciones
            filtros: Dict con criterios de filtro
        
        Returns:
            Lista filtrada
        """
        resultado = evaluaciones
        
        # Filtro por nivel de riesgo
        if 'nivel_riesgo' in filtros and filtros['nivel_riesgo']:
            resultado = [e for e in resultado if e['clasificacion']['nivel'] == filtros['nivel_riesgo']]
        
        # Filtro por carrera
        if 'carrera' in filtros and filtros['carrera']:
            resultado = [e for e in resultado if e['carrera'] == filtros['carrera']]
        
        # Filtro por cuatrimestre
        if 'cuatrimestre' in filtros and filtros['cuatrimestre']:
            resultado = [e for e in resultado if e['cuatrimestre'] == filtros['cuatrimestre']]
        
        # Filtro por búsqueda de nombre
        if 'busqueda' in filtros and filtros['busqueda']:
            busqueda = filtros['busqueda'].lower()
            resultado = [e for e in resultado if 
                        busqueda in e['nombre'].lower() or 
                        busqueda in e['apellido_p'].lower() or
                        busqueda in e['matricula'].lower()]
        
        return resultado
