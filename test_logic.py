import sqlite3
from risk_assessment import RiskAssessmentEngine
from academic_history import AcademicHistoryAnalyzer
from pdf_generator import PDFReportGenerator
from datetime import datetime

DATABASE = 'asesorias.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def setup_test_data():
    """Inserta datos de prueba en la base de datos para simular un estudiante con riesgo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Asegurar que las tablas existan (copiado de app.py)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido_p TEXT,
            apellido_m TEXT,
            matricula TEXT,
            cuatrimestre TEXT,
            motivo TEXT,
            fecha TEXT,
            descripcion TEXT,
            observaciones TEXT,
            seguimiento TEXT,
            created_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tutoria_grupal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grupo_nombre TEXT,
            carrera TEXT,
            cuatrimestre TEXT,
            motivo TEXT,
            fecha TEXT,
            descripcion TEXT,
            asistentes TEXT,
            observaciones TEXT,
            created_at TEXT
        )
    """)
    
    # Limpiar tablas para prueba
    cursor.execute("DELETE FROM tutoria")
    cursor.execute("DELETE FROM tutoria_grupal")
    
    # Estudiante de Alto Riesgo (Juan Pérez)
    # Motivos: Baja Calificación (3), Inasistencias (3)
    # Frecuencia: 5 tutorías
    
    # Tutoría 1 (Cuatrimestre 7) - Baja Calificación
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Juan', 'Pérez', 'García', '1234567890', '7', 'Baja calificación en Matemáticas', '2025-10-01', 'No estudia', 'Seguimiento', 'Seguimiento', datetime.now().isoformat()))
    
    # Tutoría 2 (Cuatrimestre 7) - Inasistencias
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Juan', 'Pérez', 'García', '1234567890', '7', 'Inasistencias recurrentes', '2025-10-15', 'Faltó 3 veces', 'Seguimiento', 'Seguimiento', datetime.now().isoformat()))
    
    # Tutoría 3 (Cuatrimestre 6) - Baja Calificación
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Juan', 'Pérez', 'García', '1234567890', '6', 'Baja calificación en Física', '2025-05-01', 'No entrega tareas', 'Seguimiento', 'Seguimiento', datetime.now().isoformat()))
    
    # Tutoría 4 (Cuatrimestre 6) - Reforzamiento
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Juan', 'Pérez', 'García', '1234567890', '6', 'Reforzamiento de Álgebra', '2025-06-01', 'Dudas básicas', 'Seguimiento', 'Seguimiento', datetime.now().isoformat()))
    
    # Tutoría 5 (Cuatrimestre 5) - Baja Calificación
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Juan', 'Pérez', 'García', '1234567890', '5', 'Baja calificación en Programación', '2024-12-01', 'No entiende POO', 'Seguimiento', 'Seguimiento', datetime.now().isoformat()))
    
    # Estudiante de Bajo Riesgo (Ana López)
    # Motivos: Asesoría General (1)
    # Frecuencia: 1 tutoría
    cursor.execute("""
        INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('Ana', 'López', 'Sánchez', '9876543210', '7', 'Asesoría general sobre horarios', '2025-11-01', 'Dudas', 'Resuelto', 'Seguimiento', datetime.now().isoformat()))
    
    # Tutoría Grupal de Prueba
    cursor.execute("""
        INSERT INTO tutoria_grupal (grupo_nombre, carrera, cuatrimestre, motivo, fecha, descripcion, asistentes, observaciones, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ('IS-701', 'Ingeniería en Software', '7', 'Temas de titulación', '2025-11-10', 'Sesión informativa', '25', 'Alta asistencia', datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    # Devolver el ID de Juan Pérez para pruebas
    conn = get_db_connection()
    juan_id = conn.execute("SELECT id FROM tutoria WHERE nombre = 'Juan'").fetchone()[0]
    conn.close()
    return juan_id

def test_risk_assessment(juan_id):
    """Prueba la lógica de evaluación de riesgo"""
    print("\n--- Prueba de Evaluación de Riesgo ---")
    engine = RiskAssessmentEngine()
    conn = get_db_connection()
    
    # Obtener datos de Juan Pérez
    tutorias_juan = conn.execute("SELECT * FROM tutoria WHERE nombre = 'Juan'").fetchall()
    tutorias_juan_data = [dict(t) for t in tutorias_juan]
    
    student_info_juan = {
        'nombre': 'Juan', 'apellido_p': 'Pérez', 'apellido_m': 'García', 
        'matricula': '1234567890', 'carrera': 'Ingeniería en Software', 'cuatrimestre': '7'
    }
    
    # Simular inasistencias y bajas calificaciones (adicionales a las de motivo)
    inasistencias_simuladas = 3 
    bajas_calificaciones_simuladas = 3
    
    evaluacion_juan = engine.evaluar_estudiante(
        student_info_juan, 
        tutorias_juan_data, 
        inasistencias=inasistencias_simuladas, 
        bajas_calificaciones=bajas_calificaciones_simuladas
    )
    
    print(f"Estudiante: {evaluacion_juan['nombre']} {evaluacion_juan['apellido_p']}")
    print(f"Puntuación Total: {evaluacion_juan['puntuacion']}")
    print(f"Clasificación: {evaluacion_juan['clasificacion']['nivel'].upper()} {evaluacion_juan['clasificacion']['icono']}")
    print(f"Detalles: {evaluacion_juan['detalles_puntuacion']}")
    
    # Verificación (Esperado: Alta Puntuación -> Alto Riesgo)
    assert evaluacion_juan['clasificacion']['nivel'] == 'alto', "Fallo: Juan Pérez no fue clasificado como Alto Riesgo"
    print("✅ Verificación de Alto Riesgo exitosa.")
    
    # Obtener datos de Ana López
    tutorias_ana = conn.execute("SELECT * FROM tutoria WHERE nombre = 'Ana'").fetchall()
    tutorias_ana_data = [dict(t) for t in tutorias_ana]
    
    student_info_ana = {
        'nombre': 'Ana', 'apellido_p': 'López', 'apellido_m': 'Sánchez', 
        'matricula': '9876543210', 'carrera': 'Ingeniería en Software', 'cuatrimestre': '7'
    }
    
    evaluacion_ana = engine.evaluar_estudiante(
        student_info_ana, 
        tutorias_ana_data, 
        inasistencias=0, 
        bajas_calificaciones=0
    )
    
    print(f"\nEstudiante: {evaluacion_ana['nombre']} {evaluacion_ana['apellido_p']}")
    print(f"Puntuación Total: {evaluacion_ana['puntuacion']}")
    print(f"Clasificación: {evaluacion_ana['clasificacion']['nivel'].upper()} {evaluacion_ana['clasificacion']['icono']}")
    
    # Verificación (Esperado: Baja Puntuación -> Bajo Riesgo)
    assert evaluacion_ana['clasificacion']['nivel'] == 'bajo', "Fallo: Ana López no fue clasificada como Bajo Riesgo"
    print("✅ Verificación de Bajo Riesgo exitosa.")
    
    conn.close()

def test_academic_history(juan_id):
    """Prueba la lógica de análisis de historial académico"""
    print("\n--- Prueba de Historial Académico ---")
    analyzer = AcademicHistoryAnalyzer()
    conn = get_db_connection()
    
    tutorias_juan = conn.execute("SELECT * FROM tutoria WHERE nombre = 'Juan'").fetchall()
    tutorias_juan_data = [dict(t) for t in tutorias_juan]
    
    analisis = analyzer.generar_analisis_completo(tutorias_juan_data)
    
    print(f"Total Tutorías: {analisis['total_tutorias']}")
    print(f"Cuatrimestres Registrados: {analisis['cuatrimestres_registrados']}")
    print(f"Motivos Generales: {analisis['motivos_generales']}")
    print(f"Reincidencias: {analisis['reincidencias']}")
    print(f"Alertas: {analisis['alertas']}")
    
    # Verificación de Reincidencia
    assert 'Baja Calificación' in analisis['reincidencias'], "Fallo: No se detectó reincidencia en 'Baja Calificación'"
    print("✅ Verificación de Reincidencia exitosa.")
    
    # Verificación de Agrupación por Cuatrimestre
    assert '7' in analisis['por_cuatrimestre'] and '6' in analisis['por_cuatrimestre'] and '5' in analisis['por_cuatrimestre'], "Fallo: Agrupación por cuatrimestre incorrecta"
    print("✅ Verificación de Agrupación por Cuatrimestre exitosa.")
    
    conn.close()

def test_pdf_generation():
    """Prueba la generación de PDF (solo verifica que no falle)"""
    print("\n--- Prueba de Generación de PDF ---")
    generator = PDFReportGenerator()
    conn = get_db_connection()
    
    # Datos de prueba para reporte de estudiante
    tutorias_juan = conn.execute("SELECT * FROM tutoria WHERE nombre = 'Juan'").fetchall()
    tutorias_juan_data = [dict(t) for t in tutorias_juan]
    student_data = {
        'nombre': 'Juan', 'apellido_p': 'Pérez', 'apellido_m': 'García', 
        'matricula': '1234567890', 'carrera': 'Ingeniería en Software', 'cuatrimestre': '7', 'tutor': 'Test Tutor'
    }
    
    try:
        pdf_buffer = generator.generate_student_report(student_data, tutorias_juan_data)
        print("✅ Generación de Reporte de Estudiante exitosa (buffer creado).")
    except Exception as e:
        print(f"❌ Fallo en Generación de Reporte de Estudiante: {e}")
        
    # Datos de prueba para reporte de grupo
    tutorias_grupo = conn.execute("SELECT * FROM tutoria_grupal WHERE grupo_nombre = 'IS-701'").fetchall()
    tutorias_grupo_data = [dict(t) for t in tutorias_grupo]
    group_data = {
        'grupo_nombre': 'IS-701', 'carrera': 'Ingeniería en Software', 'cuatrimestre': '7'
    }
    
    try:
        pdf_buffer_group = generator.generate_group_report(group_data, tutorias_grupo_data)
        print("✅ Generación de Reporte de Grupo exitosa (buffer creado).")
    except Exception as e:
        print(f"❌ Fallo en Generación de Reporte de Grupo: {e}")
        
    conn.close()

if __name__ == '__main__':
    juan_id = setup_test_data()
    test_risk_assessment(juan_id)
    test_academic_history(juan_id)
    test_pdf_generation()
