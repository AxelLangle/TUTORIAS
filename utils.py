"""
Módulo de utilidades para el sistema de tutorías
"""

from datetime import datetime, timedelta

def obtener_cuatrimestres_disponibles():
    """
    Obtiene los cuatrimestres disponibles según la época del año actual.
    
    Lógica:
    - Septiembre - Diciembre: 1°, 4°, 7° y 10°
    - Enero - Abril: 2°, 5° y 8°
    - Mayo - Agosto: 3°, 6° y 9°
    
    Returns:
        list: Lista de cuatrimestres disponibles como strings
    """
    mes_actual = datetime.now().month
    
    if mes_actual in [9, 10, 11, 12]:  # Septiembre - Diciembre
        return ['1', '4', '7', '10']
    elif mes_actual in [1, 2, 3, 4]:  # Enero - Abril
        return ['2', '5', '8']
    else:  # Mayo - Agosto (5, 6, 7, 8)
        return ['3', '6', '9']

def obtener_nombre_periodo():
    """
    Obtiene el nombre del período académico actual.
    
    Returns:
        str: Nombre del período (ej. "Septiembre - Diciembre")
    """
    mes_actual = datetime.now().month
    
    if mes_actual in [9, 10, 11, 12]:
        return "Septiembre - Diciembre"
    elif mes_actual in [1, 2, 3, 4]:
        return "Enero - Abril"
    else:
        return "Mayo - Agosto"

def validar_cuatrimestre(cuatrimestre):
    """
    Valida si un cuatrimestre es válido para la época actual.
    
    Args:
        cuatrimestre: String con el número de cuatrimestre
    
    Returns:
        bool: True si es válido, False si no
    """
    cuatrimestres_disponibles = obtener_cuatrimestres_disponibles()
    return str(cuatrimestre) in cuatrimestres_disponibles

def obtener_fecha_inicio_filtro(filtro_tiempo):
    """
    Calcula la fecha de inicio para los filtros de tiempo.
    
    Args:
        filtro_tiempo (str): 'semana', 'mes', 'cuatrimestre'
        
    Returns:
        datetime: Fecha de inicio del período de filtro.
    """
    hoy = datetime.now()
    
    if filtro_tiempo == 'semana':
        # Últimos 7 días
        return hoy - timedelta(days=7)
    elif filtro_tiempo == 'mes':
        # Últimos 30 días
        return hoy - timedelta(days=30)
    elif filtro_tiempo == 'cuatrimestre':
        # Últimos 4 meses (aprox. 120 días)
        return hoy - timedelta(days=120)
    else:
        # Sin filtro de tiempo (todos los datos)
        return datetime.min # Usar una fecha muy antigua



# --- Lógica de Programas Educativos y Grupos ---

PROGRAMA_EDUCATIVO_1 = {
    "IS": "Ingeniería en Software",
    "IMA": "Ingeniería en Mecánica Automotriz",
    "IF": "Ingeniería Financiera",
    "ITM": "Ingeniería en Tecnologías de Manufactura",
    "LNI": "Licenciatura en Negocios Internacionales"
}

PROGRAMA_EDUCATIVO_2 = {
    "ITII": "Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital",
    "IMA": "Licenciatura en Ingeniería en Mecánica Automotriz",
    "IF": "Licenciatura en Ingeniería Financiera",
    "IMAV": "Licenciatura en Ingeniería en Manufactura Avanzadas",
    "LCIA": "Licenciatura en Comercio Internacional y Aduanas"
}

def obtener_carreras_por_programa(programa_id):
    """Obtiene las carreras de un programa educativo"""
    if programa_id == 1:
        return PROGRAMA_EDUCATIVO_1
    elif programa_id == 2:
        return PROGRAMA_EDUCATIVO_2
    return {}

def obtener_grupos_disponibles(cuatrimestre, programa_id):
    """
    Genera los grupos disponibles para un cuatrimestre y programa educativo.
    
    Lógica de ID de Grupo: [Grupo][Cuatrimestre][Año][Carrera]
    Ejemplo: 5725IS -> Grupo 5, Cuatrimestre 7, Año 2025, Carrera IS
    """
    if not cuatrimestre or not programa_id:
        return []
    
    año_actual = str(datetime.now().year)[-2:]  # Últimos 2 dígitos del año
    carreras = obtener_carreras_por_programa(programa_id)
    grupos_disponibles = []
    
    # Generar de 1 a 5 grupos por carrera
    for i in range(1, 6):
        for sigla in carreras.keys():
            grupo_id = f"{i}{cuatrimestre}{año_actual}{sigla}"
            grupos_disponibles.append(grupo_id)
            
    return grupos_disponibles

def obtener_todas_las_carreras():
    """Combina las carreras de todos los programas educativos en un solo diccionario."""
    carreras = {}
    carreras.update(PROGRAMA_EDUCATIVO_1)
    carreras.update(PROGRAMA_EDUCATIVO_2)
    return carreras

def decodificar_grupo(grupo_id):
    """
    Decodifica un ID de grupo para obtener sus componentes.
    
    Returns:
        dict: Diccionario con grupo, cuatrimestre, año y carrera, o None si el formato es incorrecto.
    """
    if not grupo_id or len(grupo_id) < 5:
        return None
    
    try:
        grupo = grupo_id[0]
        cuatrimestre = grupo_id[1]
        año = f"20{grupo_id[2:4]}"
        carrera_sigla = grupo_id[4:]
        
        return {
            "grupo": grupo,
            "cuatrimestre": cuatrimestre,
            "año": año,
            "carrera_sigla": carrera_sigla
        }
    except Exception:
        return None
