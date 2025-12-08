"""
Módulo de utilidades para el sistema de tutorías
"""

from datetime import datetime

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
