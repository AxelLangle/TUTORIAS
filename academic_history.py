"""
Módulo de Análisis de Historial Académico
Proporciona funciones para analizar patrones, mejoras y reincidencias en tutorías de estudiantes
"""

from collections import defaultdict
from datetime import datetime

class AcademicHistoryAnalyzer:
    """Analizador de historial académico de estudiantes"""
    
    MOTIVO_CATEGORIES = {
        'baja calificación': 'Baja Calificación',
        'bajo desempeño': 'Baja Calificación',
        'inasistencia': 'Inasistencias',
        'falta de motivación': 'Problemas de Actitud',
        'problemas de conducta': 'Problemas de Actitud',
        'reforzamiento': 'Reforzamiento Académico',
        'asesoría general': 'Asesoría General',
    }
    
    def __init__(self):
        pass
        
    def _normalize_motivo(self, motivo):
        """Normaliza el motivo a una categoría general."""
        motivo_lower = motivo.lower()
        for keyword, category in self.MOTIVO_CATEGORIES.items():
            if keyword in motivo_lower:
                return category
        return motivo # Retorna el motivo original si no se encuentra categoría
    
    def agrupar_por_cuatrimestre(self, tutorias):
        """
        Agrupa tutorías por cuatrimestre
        
        Args:
            tutorias: Lista de tutorías (dicts)
        
        Returns:
            Dict con estructura {cuatrimestre: [tutorías]}
        """
        por_cuatrimestre = defaultdict(list)
        
        for tutoría in tutorias:
            cuatrimestre = tutoría.get('cuatrimestre', 'N/A')
            por_cuatrimestre[cuatrimestre].append(tutoría)
        
        # Ordenar por cuatrimestre descendente
        return dict(sorted(por_cuatrimestre.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 0, reverse=True))
    
    def contar_motivos(self, tutorias):
        """
        Cuenta la frecuencia de cada motivo de tutoría
        
        Args:
            tutorias: Lista de tutorías
        
        Returns:
            Dict con {motivo: cantidad}
        """
        motivos = defaultdict(int)
        
        for tutoría in tutorias:
            motivo = tutoría.get('motivo', 'N/A')
            normalized_motivo = self._normalize_motivo(motivo)
            motivos[normalized_motivo] += 1
        
        return dict(sorted(motivos.items(), key=lambda x: x[1], reverse=True))
    
    def detectar_mejoras(self, por_cuatrimestre):
        """
        Detecta mejoras en el desempeño académico
        
        Args:
            por_cuatrimestre: Dict con tutorías agrupadas por cuatrimestre
        
        Returns:
            Dict con información de mejoras
        """
        mejoras = {
            'detectada': False,
            'descripcion': '',
            'cuatrimestres_analizados': len(por_cuatrimestre),
            'tendencia': 'estable'
        }
        
        if len(por_cuatrimestre) < 2:
            return mejoras
        
        # Obtener frecuencias por cuatrimestre
        cuatrimestres_ordenados = sorted(por_cuatrimestre.keys(), 
                                        key=lambda x: int(x) if x.isdigit() else 0)
        frecuencias = [len(por_cuatrimestre[c]) for c in cuatrimestres_ordenados]
        
        if len(frecuencias) >= 2:
            # Comparar últimos 2 cuatrimestres
            if frecuencias[-1] < frecuencias[-2]:
                mejoras['detectada'] = True
                mejoras['descripcion'] = f"Reducción en frecuencia de tutorías: {frecuencias[-2]} → {frecuencias[-1]}"
                mejoras['tendencia'] = 'mejorando'
            elif frecuencias[-1] > frecuencias[-2]:
                mejoras['tendencia'] = 'empeorando'
            else:
                mejoras['tendencia'] = 'estable'
        
        return mejoras
    
    def detectar_reincidencias(self, tutorias, umbral=3):
        """
        Detecta motivos recurrentes (reincidencias)
        
        Args:
            tutorias: Lista de tutorías
            umbral: Número mínimo de repeticiones para considerar reincidencia
        
        Returns:
            Dict con motivos recurrentes
        """
        motivos = self.contar_motivos(tutorias)
        
        reincidencias = {}
        for motivo, cantidad in motivos.items():
            if cantidad >= umbral:
                reincidencias[motivo] = {
                    'cantidad': cantidad,
                    'porcentaje': round((cantidad / len(tutorias)) * 100, 2) if tutorias else 0,
                    'severidad': 'alta' if cantidad >= 5 else 'media'
                }
        
        return reincidencias
    
    def calcular_estadisticas_cuatrimestre(self, tutorias_cuatrimestre):
        """
        Calcula estadísticas para un cuatrimestre específico
        
        Args:
            tutorias_cuatrimestre: Lista de tutorías del cuatrimestre
        
        Returns:
            Dict con estadísticas
        """
        if not tutorias_cuatrimestre:
            return {
                'total': 0,
                'motivos': {},
                'motivo_principal': 'N/A',
                'frecuencia_motivo_principal': 0
            }
        
        motivos = self.contar_motivos(tutorias_cuatrimestre)
        motivo_principal = max(motivos.items(), key=lambda x: x[1]) if motivos else ('N/A', 0)
        
        return {
            'total': len(tutorias_cuatrimestre),
            'motivos': motivos,
            'motivo_principal': motivo_principal[0],
            'frecuencia_motivo_principal': motivo_principal[1]
        }
    
    def generar_analisis_completo(self, tutorias):
        """
        Genera un análisis completo del historial académico
        
        Args:
            tutorias: Lista de tutorías del estudiante
        
        Returns:
            Dict con análisis completo
        """
        if not tutorias:
            return {
                'total_tutorias': 0,
                'por_cuatrimestre': {},
                'estadisticas_por_cuatrimestre': {},
                'motivos_generales': {},
                'mejoras': {'detectada': False},
                'reincidencias': {},
                'alertas': []
            }
        
        por_cuatrimestre = self.agrupar_por_cuatrimestre(tutorias)
        motivos_generales = self.contar_motivos(tutorias)
        mejoras = self.detectar_mejoras(por_cuatrimestre)
        reincidencias = self.detectar_reincidencias(tutorias)
        
        # Calcular estadísticas por cuatrimestre
        estadisticas_por_cuatrimestre = {}
        for cuatrimestre, tuts in por_cuatrimestre.items():
            estadisticas_por_cuatrimestre[cuatrimestre] = self.calcular_estadisticas_cuatrimestre(tuts)
        
        # Generar alertas
        alertas = self._generar_alertas(por_cuatrimestre, reincidencias, mejoras, tutorias)
        
        return {
            'total_tutorias': len(tutorias),
            'cuatrimestres_registrados': len(por_cuatrimestre),
            'por_cuatrimestre': por_cuatrimestre,
            'estadisticas_por_cuatrimestre': estadisticas_por_cuatrimestre,
            'motivos_generales': motivos_generales,
            'mejoras': mejoras,
            'reincidencias': reincidencias,
            'alertas': alertas
        }
    
    def _generar_alertas(self, por_cuatrimestre, reincidencias, mejoras, tutorias):
        """
        Genera alertas basadas en el análisis
        
        Args:
            por_cuatrimestre: Dict con tutorías por cuatrimestre
            reincidencias: Dict con motivos recurrentes
            mejoras: Dict con información de mejoras
            tutorias: Lista completa de tutorías
        
        Returns:
            Lista de alertas
        """
        alertas = []
        
        # Alerta 1: Reincidencias detectadas
        if reincidencias:
            for motivo, info in reincidencias.items():
                if info['severidad'] == 'alta':
                    alertas.append({
                        'tipo': 'reincidencia_alta',
                        'nivel': 'crítico',
                        'mensaje': f"Reincidencia crítica: '{motivo}' aparece {info['cantidad']} veces ({info['porcentaje']}%)",
                        'color': '#cc1313'
                    })
                else:
                    alertas.append({
                        'tipo': 'reincidencia_media',
                        'nivel': 'advertencia',
                        'mensaje': f"Reincidencia: '{motivo}' aparece {info['cantidad']} veces",
                        'color': '#ff9800'
                    })
        
        # Alerta 2: Empeoramiento
        if mejoras.get('tendencia') == 'empeorando':
            alertas.append({
                'tipo': 'empeoramiento',
                'nivel': 'advertencia',
                'mensaje': "Tendencia de empeoramiento: Aumento en frecuencia de tutorías",
                'color': '#ff9800'
            })
        
        # Alerta 3: Mejora detectada
        if mejoras.get('detectada'):
            alertas.append({
                'tipo': 'mejora',
                'nivel': 'positivo',
                'mensaje': mejoras.get('descripcion', 'Mejora detectada'),
                'color': '#4caf50'
            })
        
        # Alerta 4: Muchas tutorías en último cuatrimestre
        if por_cuatrimestre:
            ultimo_cuatrimestre = list(por_cuatrimestre.values())[0]
            if len(ultimo_cuatrimestre) >= 5:
                alertas.append({
                    'tipo': 'muchas_tutorias',
                    'nivel': 'crítico',
                    'mensaje': f"Alta frecuencia de tutorías en el último cuatrimestre: {len(ultimo_cuatrimestre)} registros",
                    'color': '#cc1313'
                })
        
        return alertas
    
    def obtener_datos_grafico_frecuencia(self, por_cuatrimestre):
        """
        Obtiene datos formateados para gráfico de frecuencia por cuatrimestre
        
        Args:
            por_cuatrimestre: Dict con tutorías por cuatrimestre
        
        Returns:
            Dict con labels y data para Chart.js
        """
        cuatrimestres = sorted(por_cuatrimestre.keys(), 
                              key=lambda x: int(x) if x.isdigit() else 0)
        frecuencias = [len(por_cuatrimestre[c]) for c in cuatrimestres]
        
        return {
            'labels': [f"{c}°" for c in cuatrimestres],
            'data': frecuencias
        }
    
    def obtener_datos_grafico_motivos(self, motivos_generales, limit=5):
        """
        Obtiene datos formateados para gráfico de motivos principales
        
        Args:
            motivos_generales: Dict con conteo de motivos
            limit: Número máximo de motivos a mostrar
        
        Returns:
            Dict con labels y data para Chart.js
        """
        motivos_ordenados = sorted(motivos_generales.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        return {
            'labels': [m[0] for m in motivos_ordenados],
            'data': [m[1] for m in motivos_ordenados]
        }
