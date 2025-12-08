"""
Script de migración para agregar la columna estudiante_id a la tabla tutoria
"""

import sqlite3
from datetime import datetime

DATABASE = 'asesorias.db'

def migrate():
    """Agrega la columna estudiante_id a la tabla tutoria si no existe"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(tutoria)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'estudiante_id' not in columns:
            print("Agregando columna 'estudiante_id' a la tabla 'tutoria'...")
            
            # Agregar la columna
            cursor.execute("ALTER TABLE tutoria ADD COLUMN estudiante_id INTEGER")
            
            print("✓ Columna agregada exitosamente.")
            
            # Crear índice para mejorar el rendimiento
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tutoria_estudiante_id ON tutoria(estudiante_id)")
            print("✓ Índice creado.")
            
            conn.commit()
        else:
            print("La columna 'estudiante_id' ya existe en la tabla 'tutoria'.")
        
        # Verificar si la tabla estudiantes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='estudiantes'")
        if not cursor.fetchone():
            print("\nCreando tabla 'estudiantes'...")
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
            print("✓ Tabla 'estudiantes' creada exitosamente.")
            conn.commit()
        else:
            # Verificar si las columnas grupo y programa_educativo existen
            cursor.execute("PRAGMA table_info(estudiantes)")
            estudiantes_columns = [column[1] for column in cursor.fetchall()]
            
            if 'grupo' not in estudiantes_columns:
                print("\nAgregando columna 'grupo' a la tabla 'estudiantes'...")
                cursor.execute("ALTER TABLE estudiantes ADD COLUMN grupo TEXT")
                print("✓ Columna 'grupo' agregada.")
                conn.commit()
            
            if 'programa_educativo' not in estudiantes_columns:
                print("Agregando columna 'programa_educativo' a la tabla 'estudiantes'...")
                cursor.execute("ALTER TABLE estudiantes ADD COLUMN programa_educativo INTEGER DEFAULT 2")
                print("✓ Columna 'programa_educativo' agregada.")
                conn.commit()
        
        print("\n✅ Migración completada exitosamente.")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
