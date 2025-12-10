"""
Módulo para inicialización automática de datos de prueba
Se ejecuta automáticamente al iniciar la aplicación si la base de datos está vacía
"""

import sqlite3
from datetime import datetime, timedelta
import random

DATABASE = 'asesorias.db'

# Datos de prueba embebidos
ESTUDIANTES_PRUEBA = [
    {"matricula": "2025001", "nombre": "Juan", "apellido_p": "Pérez", "apellido_m": "García", "cuatrimestre": "1", "carrera": "Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital", "grupo": "11725ITII", "programa_educativo": 2},
    {"matricula": "2025002", "nombre": "María", "apellido_p": "López", "apellido_m": "Martínez", "cuatrimestre": "1", "carrera": "Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital", "grupo": "11725ITII", "programa_educativo": 2},
    {"matricula": "2025003", "nombre": "Carlos", "apellido_p": "Rodríguez", "apellido_m": "Hernández", "cuatrimestre": "4", "carrera": "Licenciatura en Ingeniería Financiera", "grupo": "14725IF", "programa_educativo": 2},
    {"matricula": "2025004", "nombre": "Ana", "apellido_p": "González", "apellido_m": "Sánchez", "cuatrimestre": "4", "carrera": "Licenciatura en Ingeniería Financiera", "grupo": "14725IF", "programa_educativo": 2},
    {"matricula": "2025005", "nombre": "Luis", "apellido_p": "Ramírez", "apellido_m": "Torres", "cuatrimestre": "7", "carrera": "Ingeniería en Software", "grupo": "17725IS", "programa_educativo": 1},
    {"matricula": "2025006", "nombre": "Laura", "apellido_p": "Flores", "apellido_m": "Morales", "cuatrimestre": "7", "carrera": "Ingeniería en Software", "grupo": "17725IS", "programa_educativo": 1},
    {"matricula": "2025007", "nombre": "Miguel", "apellido_p": "Jiménez", "apellido_m": "Castro", "cuatrimestre": "10", "carrera": "Ingeniería en Mecánica Automotriz", "grupo": "110725IMA", "programa_educativo": 1},
    {"matricula": "2025008", "nombre": "Sofía", "apellido_p": "Ruiz", "apellido_m": "Ortiz", "cuatrimestre": "10", "carrera": "Ingeniería en Mecánica Automotriz", "grupo": "110725IMA", "programa_educativo": 1},
    {"matricula": "2025009", "nombre": "Diego", "apellido_p": "Vargas", "apellido_m": "Mendoza", "cuatrimestre": "1", "carrera": "Licenciatura en Comercio Internacional y Aduanas", "grupo": "11725LCIA", "programa_educativo": 2},
    {"matricula": "2025010", "nombre": "Valeria", "apellido_p": "Moreno", "apellido_m": "Gutiérrez", "cuatrimestre": "4", "carrera": "Licenciatura en Ingeniería en Manufactura Avanzadas", "grupo": "14725IMAV", "programa_educativo": 2},
]

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

TEMAS_ASESORIAS = [
    "Programación en Python",
    "Bases de Datos",
    "Estructuras de Datos",
    "Algoritmos",
    "Desarrollo Web",
    "Cálculo Diferencial",
    "Álgebra Lineal",
    "Física",
    "Matemáticas Financieras",
    "Contabilidad",
    "Mecánica de Materiales",
    "Termodinámica"
]

def verificar_migracion(conn):
    """Verifica y ejecuta las migraciones necesarias"""
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna estudiante_id existe en tutoria
        cursor.execute("PRAGMA table_info(tutoria)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'estudiante_id' not in columns:
            print("  → Agregando columna 'estudiante_id' a la tabla 'tutoria'...")
            cursor.execute("ALTER TABLE tutoria ADD COLUMN estudiante_id INTEGER")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tutoria_estudiante_id ON tutoria(estudiante_id)")
            conn.commit()
            print("  ✓ Columna agregada exitosamente.")
        
        # Verificar si la tabla estudiantes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estudiantes'")
        if not cursor.fetchone():
            print("  → Creando tabla 'estudiantes'...")
            cursor.execute('''
                CREATE TABLE estudiantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    matricula TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido_p TEXT NOT NULL,
                    apellido_m TEXT,
                    cuatrimestre_actual TEXT,
                    carrera TEXT,
                    grupo TEXT,
                    programa_educativo INTEGER DEFAULT 2,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            conn.commit()
            print("  ✓ Tabla 'estudiantes' creada exitosamente.")
        else:
            # Verificar si las columnas grupo y programa_educativo existen
            cursor.execute("PRAGMA table_info(estudiantes)")
            estudiantes_columns = [column[1] for column in cursor.fetchall()]
            
            if 'grupo' not in estudiantes_columns:
                print("  → Agregando columna 'grupo' a la tabla 'estudiantes'...")
                cursor.execute("ALTER TABLE estudiantes ADD COLUMN grupo TEXT")
                conn.commit()
                print("  ✓ Columna 'grupo' agregada.")
            
            if 'programa_educativo' not in estudiantes_columns:
                print("  → Agregando columna 'programa_educativo' a la tabla 'estudiantes'...")
                cursor.execute("ALTER TABLE estudiantes ADD COLUMN programa_educativo INTEGER DEFAULT 2")
                conn.commit()
                print("  ✓ Columna 'programa_educativo' agregada.")
        
        # Verificar si la columna matricula existe en asesoria
        cursor.execute("PRAGMA table_info(asesoria)")
        asesoria_columns = [column[1] for column in cursor.fetchall()]
        
        if 'matricula' not in asesoria_columns:
            print("  → Agregando columna 'matricula' a la tabla 'asesoria'...")
            cursor.execute("ALTER TABLE asesoria ADD COLUMN matricula TEXT")
            conn.commit()
            print("  ✓ Columna 'matricula' agregada.")
        
    except Exception as e:
        print(f"  ❌ Error durante la migración: {e}")
        conn.rollback()

def cargar_estudiantes(conn):
    """Carga estudiantes de prueba en la base de datos"""
    cursor = conn.cursor()
    
    try:
        print("\n→ Cargando estudiantes de prueba...")
        
        for estudiante in ESTUDIANTES_PRUEBA:
            # Verificar si ya existe
            cursor.execute("SELECT id FROM estudiantes WHERE matricula = ?", (estudiante['matricula'],))
            existe = cursor.fetchone()
            
            if not existe:
                cursor.execute(
                    '''
                    INSERT INTO estudiantes (matricula, nombre, apellido_p, apellido_m, cuatrimestre_actual, carrera, grupo, programa_educativo, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        estudiante['matricula'],
                        estudiante['nombre'],
                        estudiante['apellido_p'],
                        estudiante['apellido_m'],
                        estudiante['cuatrimestre'],
                        estudiante['carrera'],
                        estudiante['grupo'],
                        estudiante['programa_educativo'],
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    )
                )
        
        conn.commit()
        print(f"  ✓ {len(ESTUDIANTES_PRUEBA)} estudiantes cargados correctamente.")
        
    except Exception as e:
        print(f"  ❌ Error al cargar estudiantes: {e}")
        conn.rollback()

def generar_asesorias(conn):
    """Genera asesorías de prueba"""
    cursor = conn.cursor()
    
    try:
        # Obtener todos los estudiantes
        estudiantes = cursor.execute("SELECT * FROM estudiantes").fetchall()
        
        if not estudiantes:
            print("  ⚠️  No hay estudiantes registrados.")
            return
        
        print("\n→ Generando asesorías de prueba...")
        
        asesorias_count = 0
        
        for estudiante in estudiantes:
            # Generar entre 2 y 4 asesorías por estudiante
            num_asesorias = random.randint(2, 4)
            
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
                        estudiante[2],  # nombre
                        estudiante[3],  # apellido_p
                        estudiante[4],  # apellido_m
                        estudiante[1],  # matricula
                        unidad,
                        parcial,
                        periodo,
                        tema,
                        fecha,
                        datetime.now().isoformat()
                    )
                )
                asesorias_count += 1
        
        conn.commit()
        print(f"  ✓ {asesorias_count} asesorías generadas correctamente.")
        
    except Exception as e:
        print(f"  ❌ Error al generar asesorías: {e}")
        conn.rollback()

def generar_tutorias(conn):
    """Genera tutorías de prueba"""
    cursor = conn.cursor()
    
    try:
        # Obtener todos los estudiantes
        estudiantes = cursor.execute("SELECT * FROM estudiantes").fetchall()
        
        if not estudiantes:
            print("  ⚠️  No hay estudiantes registrados.")
            return
        
        print("\n→ Generando tutorías de prueba...")
        
        tutorias_count = 0
        
        for estudiante in estudiantes:
            # Generar entre 1 y 3 tutorías por estudiante
            num_tutorias = random.randint(1, 3)
            
            for i in range(num_tutorias):
                # Fecha aleatoria en los últimos 90 días
                dias_atras = random.randint(1, 90)
                fecha = (datetime.now() - timedelta(days=dias_atras)).strftime('%Y-%m-%d')
                
                motivo = random.choice(MOTIVOS_TUTORIAS)
                descripcion = f"Descripción detallada de la tutoría: {motivo.lower()}. Se realizó seguimiento del caso."
                observaciones = "El estudiante mostró disposición para mejorar. Se establecieron compromisos."
                seguimiento = random.choice(["Pendiente", "En proceso", "Resuelto"])
                
                cursor.execute(
                    '''
                    INSERT INTO tutoria (estudiante_id, nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        estudiante[0],  # id
                        estudiante[2],  # nombre
                        estudiante[3],  # apellido_p
                        estudiante[4],  # apellido_m
                        estudiante[1],  # matricula
                        estudiante[5],  # cuatrimestre_actual
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
        print(f"  ✓ {tutorias_count} tutorías generadas correctamente.")
        
    except Exception as e:
        print(f"  ❌ Error al generar tutorías: {e}")
        conn.rollback()

def generar_usuario_demo(conn):
    """Genera un usuario de demostración"""
    cursor = conn.cursor()
    
    try:
        # Verificar si ya existe un usuario
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("\n→ Creando usuario de demostración...")
            cursor.execute(
                'INSERT INTO usuarios (nombre, usuario, password) VALUES (?, ?, ?)',
                ('Usuario Demo', 'demo@uptecamac.edu.mx', 'demo123')
            )
            conn.commit()
            print("  ✓ Usuario demo creado: demo@uptecamac.edu.mx / demo123")
        
    except Exception as e:
        print(f"  ❌ Error al crear usuario demo: {e}")
        conn.rollback()

def inicializar_datos_prueba():
    """
    Función principal que inicializa todos los datos de prueba
    Se ejecuta automáticamente al iniciar la aplicación si la base de datos está vacía
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Verificar si hay datos en la base de datos
        cursor.execute("SELECT COUNT(*) FROM estudiantes")
        estudiantes_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM asesoria")
        asesorias_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tutoria")
        tutorias_count = cursor.fetchone()[0]
        
        # Si la base de datos está vacía, inicializar datos de prueba
        if estudiantes_count == 0 and asesorias_count == 0 and tutorias_count == 0:
            print("\n" + "="*60)
            print("INICIALIZANDO DATOS DE PRUEBA")
            print("="*60)
            
            # Ejecutar migraciones
            verificar_migracion(conn)
            
            # Cargar datos de prueba
            cargar_estudiantes(conn)
            generar_asesorias(conn)
            generar_tutorias(conn)
            generar_usuario_demo(conn)
            
            print("\n" + "="*60)
            print("✅ DATOS DE PRUEBA INICIALIZADOS CORRECTAMENTE")
            print("="*60)
            print("\nCredenciales de acceso:")
            print("  Usuario: demo@uptecamac.edu.mx")
            print("  Contraseña: demo123")
            print("="*60 + "\n")
        else:
            # Solo verificar migraciones si hay datos
            verificar_migracion(conn)
        
    except Exception as e:
        print(f"❌ Error durante la inicialización: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    inicializar_datos_prueba()
