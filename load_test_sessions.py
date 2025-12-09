"""
Script para limpiar consultas existentes y agregar datos de prueba
para asesorías y tutorías usando los estudiantes registrados
"""

import sqlite3
from datetime import datetime, timedelta
import random

DATABASE = 'asesorias.db'

# Motivos comunes para tutorías
MOTIVOS_TUTORIAS = [
    "Baja calificación en examen",
    "Dificultad para comprender el tema",
    "Inasistencias frecuentes",
    "Problemas de conducta",
    "Bajo desempeño académico",
    "Solicitud de asesoría académica",
    "Problemas personales que afectan el rendimiento",
    "Necesita apoyo en proyecto final"
]

# Temas comunes para asesorías
TEMAS_ASESORIAS = [
    "Programación en Python",
    "Bases de Datos",
    "Estructuras de Datos",
    "Algoritmos",
    "Desarrollo Web",
    "Cálculo Diferencial",
    "Álgebra Lineal",
    "Física"
]

def limpiar_datos():
    """Limpia las consultas existentes"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        print("Limpiando datos existentes...")
        cursor.execute("DELETE FROM asesoria")
        cursor.execute("DELETE FROM tutoria")
        cursor.execute("DELETE FROM tutoria_grupal")
        conn.commit()
        print("✓ Datos limpiados correctamente.")
    except Exception as e:
        print(f"❌ Error al limpiar datos: {e}")
        conn.rollback()
    finally:
        conn.close()

def generar_datos_prueba():
    """Genera datos de prueba para asesorías y tutorías"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Obtener todos los estudiantes
        estudiantes = cursor.execute("SELECT * FROM estudiantes").fetchall()
        
        if not estudiantes:
            print("❌ No hay estudiantes registrados. Ejecuta primero load_test_data.py")
            return
        
        print(f"\nGenerando datos de prueba para {len(estudiantes)} estudiantes...")
        
        asesorias_count = 0
        tutorias_count = 0
        
        # Generar asesorías y tutorías para cada estudiante
        for estudiante in estudiantes:
            # Generar entre 2 y 5 asesorías por estudiante
            num_asesorias = random.randint(2, 5)
            
            for i in range(num_asesorias):
                # Fecha aleatoria en los últimos 60 días
                dias_atras = random.randint(1, 60)
                fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
                
                tema = random.choice(TEMAS_ASESORIAS)
                unidad = random.randint(1, 5)
                parcial = random.randint(1, 3)
                periodo = f"{random.choice(['Enero-Abril', 'Mayo-Agosto', 'Septiembre-Diciembre'])} 2025"
                
                cursor.execute(
                    '''
                    INSERT INTO asesoria (nombre, apellido_p, apellido_m, matricula, unidad, parcial, periodo, tema, fecha, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        estudiante['nombre'],
                        estudiante['apellido_p'],
                        estudiante['apellido_m'],
                        estudiante['matricula'],
                        unidad,
                        parcial,
                        periodo,
                        tema,
                        fecha,
                        datetime.now().isoformat()
                    )
                )
                asesorias_count += 1
            
            # Generar entre 1 y 4 tutorías por estudiante
            num_tutorias = random.randint(1, 4)
            
            for i in range(num_tutorias):
                # Fecha aleatoria en los últimos 90 días
                dias_atras = random.randint(1, 90)
                fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
                
                motivo = random.choice(MOTIVOS_TUTORIAS)
                descripcion = f"Descripción detallada de la tutoría: {motivo.lower()}"
                observaciones = "Observaciones del tutor sobre el caso."
                seguimiento = random.choice(["Pendiente", "En proceso", "Resuelto"])
                
                cursor.execute(
                    '''
                    INSERT INTO tutoria (estudiante_id, nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        estudiante['id'],
                        estudiante['nombre'],
                        estudiante['apellido_p'],
                        estudiante['apellido_m'],
                        estudiante['matricula'],
                        estudiante['cuatrimestre_actual'],
                        motivo,
                        fecha,
                        descripcion,
                        observaciones,
                        seguimiento,
                        datetime.now().isoformat()
                    )
                )
                tutorias_count += 1
        
        conn.commit()
        print(f"\n✅ Datos de prueba generados:")
        print(f"   - Asesorías: {asesorias_count}")
        print(f"   - Tutorías: {tutorias_count}")
        
    except Exception as e:
        print(f"❌ Error al generar datos: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("SCRIPT DE CARGA DE DATOS DE PRUEBA")
    print("=" * 50)
    
    respuesta = input("\n¿Deseas limpiar los datos existentes? (s/n): ")
    
    if respuesta.lower() == 's':
        limpiar_datos()
    
    generar_datos_prueba()
    
    print("\n✅ Proceso completado.")
