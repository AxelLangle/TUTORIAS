from flask import Flask, render_template, request, redirect, url_for, session, g, flash, send_file
import re
import sqlite3
from datetime import datetime
from functools import wraps
from pdf_generator import PDFReportGenerator
from academic_history import AcademicHistoryAnalyzer
from risk_assessment import RiskAssessmentEngine
from utils import obtener_cuatrimestres_disponibles, obtener_nombre_periodo, validar_cuatrimestre, obtener_grupos_disponibles, obtener_carreras_por_programa, decodificar_grupo, PROGRAMA_EDUCATIVO_1, PROGRAMA_EDUCATIVO_2

DATABASE = 'asesorias.db'
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para sesiones

# Agregar datetime y cuatrimestres al contexto de Jinja2
@app.context_processor
def inject_now():
    return {
        'now': datetime.now,
        'cuatrimestres_disponibles': obtener_cuatrimestres_disponibles(),
        'periodo_actual': obtener_nombre_periodo()
    }

# ---------------------------
# Helpers de DB
# ---------------------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    cursor = db.cursor()
    # Tabla usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Tabla asesorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS asesoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            apellido_p TEXT,
            apellido_m TEXT,
            unidad TEXT,
            parcial TEXT,
            periodo TEXT,
            tema TEXT,
            fecha TEXT,
            created_at TEXT
        )
    ''')
    # Tabla tutorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tutoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER,
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
            created_at TEXT,
            FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
        )
    ''')
    # Tabla tutorías grupales
    cursor.execute('''
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
    ''')
    # Tabla estudiantes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            apellido_p TEXT NOT NULL,
            apellido_m TEXT,
            cuatrimestre_actual TEXT,
            carrera TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    db.commit()

# Inicializar BD al iniciar la app
with app.app_context():
    init_db()

# ---------------------------
# Decorador login_required
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Rutas de autenticación
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM usuarios WHERE usuario=? AND password=?', (usuario, password)).fetchone()
        if user:
            session['usuario'] = user['usuario']
            session['nombre'] = user['nombre']
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o contraseña incorrectos.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('login'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        password = request.form['password']

        # Validar correo institucional
        if not re.fullmatch(r"[a-zA-Z0-9._%+-]+@uptecamac\.edu\.mx", usuario):
            flash('Solo se permiten correos institucionales (@uptecamac.edu.mx).', 'error')
            return redirect(url_for('register_user'))

        db = get_db()
        try:
            db.execute(
                'INSERT INTO usuarios (nombre, usuario, password) VALUES (?, ?, ?)',
                (nombre, usuario, password)
            )
            db.commit()
            flash('Usuario registrado correctamente.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario ya existe.', 'error')

    return render_template('register_user.html')

# ---------------------------
# Dashboard / Index
# ---------------------------
@app.route('/')
@app.route('/index')
@login_required
def index():
    db = get_db()
    cursor = db.cursor()
    
    # Totales
    cursor.execute("SELECT COUNT(*) FROM asesoria")
    total_asesorias = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tutoria")
    total_tutorias = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM tutoria_grupal")
    total_grupales = cursor.fetchone()[0]

    # Asesorías por mes
    cursor.execute("""
        SELECT strftime('%m', fecha) as mes, COUNT(*) as cantidad
        FROM asesoria
        WHERE fecha IS NOT NULL AND fecha != ''
        GROUP BY mes
        ORDER BY mes
    """)
    asesorias_result = cursor.fetchall()

    # Tutorías individuales por mes
    cursor.execute("""
        SELECT strftime('%m', fecha) as mes, COUNT(*) as cantidad
        FROM tutoria
        WHERE fecha IS NOT NULL AND fecha != ''
        GROUP BY mes
        ORDER BY mes
    """)
    tutorias_result = cursor.fetchall()

    # Tutorías grupales por mes
    cursor.execute("""
        SELECT strftime('%m', fecha) as mes, COUNT(*) as cantidad
        FROM tutoria_grupal
        WHERE fecha IS NOT NULL AND fecha != ''
        GROUP BY mes
        ORDER BY mes
    """)
    grupales_result = cursor.fetchall()

    # Crear etiquetas de mes únicas
    meses = [datetime.strptime(r['mes'], '%m').strftime('%b') for r in asesorias_result]

    # Crear listas de cantidades por tipo (coincidiendo con meses)
    cantidades_asesorias = [r['cantidad'] for r in asesorias_result]
    cantidades_tutorias = [r['cantidad'] for r in tutorias_result]
    cantidades_grupales = [r['cantidad'] for r in grupales_result]

    return render_template("index.html",
                           total_asesorias=total_asesorias,
                           total_tutorias=total_tutorias,
                           total_grupales=total_grupales,
                           meses=meses,
                           cantidades_asesorias=cantidades_asesorias,
                           cantidades_tutorias=cantidades_tutorias,
                           cantidades_grupales=cantidades_grupales,
                           nombre=session.get('nombre'))

# ---------------------------
# Registro de Asesorías
# ---------------------------
@app.route('/register/asesoria', methods=['GET', 'POST'])
@login_required
def register_asesoria():
    db = get_db()
    
    if request.method == 'POST':
        data = request.form
        db.execute('''
            INSERT INTO asesoria (nombre, apellido_p, apellido_m, unidad, parcial, periodo, tema, fecha, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('nombre'), data.get('apellido_p'), data.get('apellido_m'),
            data.get('unidad'), data.get('parcial'), data.get('periodo'),
            data.get('tema'), data.get('fecha'), datetime.utcnow().isoformat()
        ))
        db.commit()
        flash('Asesoría registrada correctamente.', 'success')
        return redirect(url_for('consultas'))
    
    # Obtener lista de estudiantes para el select
    estudiantes = db.execute("SELECT * FROM estudiantes ORDER BY apellido_p, apellido_m, nombre").fetchall()
    return render_template('register_asesoria.html', nombre=session.get('nombre'), estudiantes=estudiantes, periodo_actual=obtener_nombre_periodo())

# ---------------------------
# Registro de Tutorías
# ---------------------------
@app.route('/register/tutoria', methods=['GET', 'POST'])
@login_required
def register_tutoria():
    db = get_db()
    
    if request.method == 'POST':
        data = request.form
        estudiante_id = data.get('estudiante_id')
        
        # Si se seleccionó un estudiante existente
        if estudiante_id:
            estudiante = db.execute("SELECT * FROM estudiantes WHERE id = ?", (estudiante_id,)).fetchone()
            if estudiante:
                db.execute('''
                    INSERT INTO tutoria (estudiante_id, nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    estudiante_id,
                    estudiante['nombre'], estudiante['apellido_p'], estudiante['apellido_m'],
                    estudiante['matricula'], estudiante['cuatrimestre_actual'], data.get('motivo'),
                    data.get('fecha'), data.get('descripcion'), data.get('observaciones'),
                    data.get('seguimiento'), datetime.utcnow().isoformat()
                ))
                db.commit()
                flash('Tutoría registrada correctamente.', 'success')
                return redirect(url_for('consultas'))
        else:
            # Registrar nuevo estudiante y luego la tutoría
            matricula = data.get('matricula')
            
            # Verificar si ya existe un estudiante con esa matrícula
            estudiante = db.execute("SELECT * FROM estudiantes WHERE matricula = ?", (matricula,)).fetchone()
            
            if not estudiante:
                # Crear nuevo estudiante
                db.execute('''
                    INSERT INTO estudiantes (matricula, nombre, apellido_p, apellido_m, cuatrimestre_actual, carrera, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    matricula,
                    data.get('nombre'),
                    data.get('apellido_p'),
                    data.get('apellido_m'),
                    data.get('cuatrimestre'),
                    data.get('carrera', 'No especificada'),
                    datetime.utcnow().isoformat(),
                    datetime.utcnow().isoformat()
                ))
                db.commit()
                estudiante = db.execute("SELECT * FROM estudiantes WHERE matricula = ?", (matricula,)).fetchone()
            
            # Registrar tutoría
            db.execute('''
                INSERT INTO tutoria (estudiante_id, nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                estudiante['id'],
                data.get('nombre'), data.get('apellido_p'), data.get('apellido_m'),
                data.get('matricula'), data.get('cuatrimestre'), data.get('motivo'),
                data.get('fecha'), data.get('descripcion'), data.get('observaciones'),
                data.get('seguimiento'), datetime.utcnow().isoformat()
            ))
            db.commit()
            flash('Tutoría registrada correctamente.', 'success')
            return redirect(url_for('consultas'))
    
    # Obtener lista de estudiantes para el select
    estudiantes = db.execute("SELECT * FROM estudiantes ORDER BY apellido_p, apellido_m, nombre").fetchall()
    return render_template('register_tutoria.html', nombre=session.get('nombre'), estudiantes=estudiantes)

# ---------------------------
# Registro de Tutorías Grupales
# ---------------------------
@app.route('/register/tutoria_grupal', methods=['GET', 'POST'])
@login_required
def register_tutoria_grupal():
    if request.method == 'POST':
        data = request.form
        db = get_db()
        db.execute('''
            INSERT INTO tutoria_grupal (grupo_nombre, carrera, cuatrimestre, motivo, fecha, descripcion, asistentes, observaciones, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('grupo_nombre'), data.get('carrera'), data.get('cuatrimestre'),
            data.get('motivo'), data.get('fecha'), data.get('descripcion'),
            data.get('asistentes'), data.get('observaciones'), datetime.utcnow().isoformat()
        ))
        db.commit()
        flash('Tutoría grupal registrada correctamente.', 'success')
        return redirect(url_for('consultas'))
    return render_template('register_tutoria_grupal.html', nombre=session.get('nombre'))

# ---------------------------
# Consultas
# ---------------------------
# ---------------------------
# Consultas (con búsqueda)
# ---------------------------
@app.route('/consultas')
@login_required
def consultas():
    db = get_db()
    tipo = request.args.get('tipo', 'todos')
    busqueda = request.args.get('busqueda', '').strip().lower()
    asesorias = []
    tutorias = []
    tutorias_grupales = []

    # Filtrar y buscar según el tipo
    if tipo in ('todos', 'asesoria'):
        if busqueda:
            asesorias = db.execute("""
                SELECT * FROM asesoria 
                WHERE LOWER(nombre) LIKE ? OR LOWER(apellido_p) LIKE ? OR LOWER(apellido_m) LIKE ?
                ORDER BY created_at DESC
            """, (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")).fetchall()
        else:
            asesorias = db.execute("SELECT * FROM asesoria ORDER BY created_at DESC").fetchall()

    if tipo in ('todos', 'tutoria'):
        if busqueda:
            tutorias = db.execute("""
                SELECT * FROM tutoria 
                WHERE LOWER(nombre) LIKE ? OR LOWER(apellido_p) LIKE ? OR LOWER(apellido_m) LIKE ?
                ORDER BY created_at DESC
            """, (f"%{busqueda}%", f"%{busqueda}%", f"%{busqueda}%")).fetchall()
        else:
            tutorias = db.execute("SELECT * FROM tutoria ORDER BY created_at DESC").fetchall()

    if tipo in ('todos', 'tutoria_grupal'):
        if busqueda:
            tutorias_grupales = db.execute("""
                SELECT * FROM tutoria_grupal 
                WHERE LOWER(grupo_nombre) LIKE ?
                ORDER BY created_at DESC
            """, (f"%{busqueda}%",)).fetchall()
        else:
            tutorias_grupales = db.execute("SELECT * FROM tutoria_grupal ORDER BY created_at DESC").fetchall()

    return render_template(
        'consultas.html',
        asesorias=asesorias,
        tutorias=tutorias,
        tutorias_grupales=tutorias_grupales,
        tipo=tipo,
        busqueda=busqueda,
        nombre=session.get('nombre')
    )

# ---------------------------
# Funciones auxiliares de BD
# ---------------------------
def eliminar_asesoria_db(id):
    db = get_db()
    db.execute("DELETE FROM asesoria WHERE id = ?", (id,))
    db.commit()

def eliminar_tutoria_db(id):
    db = get_db()
    db.execute("DELETE FROM tutoria WHERE id = ?", (id,))
    db.commit()

def eliminar_tutoria_grupal_db(id):
    db = get_db()
    db.execute("DELETE FROM tutoria_grupal WHERE id = ?", (id,))
    db.commit()

# ---------------------------
# Rutas para eliminar registros
# ---------------------------
@app.post("/eliminar_asesoria/<int:id>")
@login_required
def eliminar_asesoria(id):
    eliminar_asesoria_db(id)
    flash("Asesoría eliminada correctamente.", "success")
    return redirect(url_for("consultas"))

@app.post("/eliminar_tutoria/<int:id>")
@login_required
def eliminar_tutoria(id):
    eliminar_tutoria_db(id)
    flash("Tutoría eliminada correctamente.", "success")
    return redirect(url_for("consultas"))

@app.post("/eliminar_tutoria_grupal/<int:id>")
@login_required
def eliminar_tutoria_grupal(id):
    eliminar_tutoria_grupal_db(id)
    flash("Tutoría grupal eliminada correctamente.", "success")
    return redirect(url_for("consultas"))

# ---------------------------
# Editar Asesoría
# ---------------------------
@app.route("/editar_asesoria/<int:id>", methods=["GET", "POST"])
@login_required
def editar_asesoria(id):
    db = get_db()
    asesoria = db.execute("SELECT * FROM asesoria WHERE id = ?", (id,)).fetchone()

    if not asesoria:
        flash("Asesoría no encontrada.", "error")
        return redirect(url_for("consultas"))

    if request.method == "POST":
        data = request.form
        db.execute("""
            UPDATE asesoria
            SET nombre=?, apellido_p=?, apellido_m=?, unidad=?, parcial=?, periodo=?, tema=?, fecha=?
            WHERE id=?
        """, (
            data.get('nombre'), data.get('apellido_p'), data.get('apellido_m'),
            data.get('unidad'), data.get('parcial'), data.get('periodo'),
            data.get('tema'), data.get('fecha'), id
        ))
        db.commit()
        flash("Asesoría actualizada correctamente.", "success")
        return redirect(url_for("consultas"))

    return render_template("editar_asesoria.html", asesoria=asesoria, nombre=session.get("nombre"))


# ---------------------------
# Editar Tutoría
# ---------------------------
@app.route("/editar_tutoria/<int:id>", methods=["GET", "POST"])
@login_required
def editar_tutoria(id):
    db = get_db()
    tutoria = db.execute("SELECT * FROM tutoria WHERE id = ?", (id,)).fetchone()

    if not tutoria:
        flash("Tutoría no encontrada.", "error")
        return redirect(url_for("consultas"))

    if request.method == "POST":
        data = request.form
        db.execute("""
            UPDATE tutoria
            SET nombre=?, apellido_p=?, apellido_m=?, matricula=?, cuatrimestre=?, motivo=?, fecha=?, descripcion=?, observaciones=?, seguimiento=?
            WHERE id=?
        """, (
            data.get('nombre'), data.get('apellido_p'), data.get('apellido_m'),
            data.get('matricula'), data.get('cuatrimestre'), data.get('motivo'),
            data.get('fecha'), data.get('descripcion'),
            data.get('observaciones'), data.get('seguimiento'), id
        ))
        db.commit()
        flash("Tutoría actualizada correctamente.", "success")
        return redirect(url_for("consultas"))

    return render_template("editar_tutoria.html", tutoria=tutoria, nombre=session.get("nombre"))

# Obtener tutoría grupal por ID
def obtener_tutoria_grupal_por_id(id):
    db = get_db()
    tutoria = db.execute("SELECT * FROM tutoria_grupal WHERE id = ?", (id,)).fetchone()
    return tutoria


# --- EDITAR TUTORÍA GRUPAL ---
@app.route("/editar_tutoria_grupal/<int:id>", methods=["GET", "POST"])
@login_required
def editar_tutoria_grupal(id):
    tutoria = obtener_tutoria_grupal_por_id(id)
    if not tutoria:
        flash("Tutoría grupal no encontrada", "error")
        return redirect(url_for("consultas"))

    if request.method == "POST":
        data = request.form
        db = get_db()
        db.execute("""
            UPDATE tutoria_grupal
            SET grupo_nombre=?, carrera=?, cuatrimestre=?, motivo=?, fecha=?, descripcion=?, asistentes=?, observaciones=?
            WHERE id=?
        """, (
            data.get('grupo_nombre'), data.get('carrera'), data.get('cuatrimestre'),
            data.get('motivo'), data.get('fecha'), data.get('descripcion'),
            data.get('asistentes'), data.get('observaciones'), id
        ))
        db.commit()
        flash("Tutoría grupal actualizada correctamente.", "success")
        return redirect(url_for("consultas"))

    return render_template("editar_tutoria_grupal.html", tutoria=tutoria, nombre=session.get("nombre"))




# ---------------------------
# Rutas para Panel de Riesgo Académico
# ---------------------------

@app.route('/dashboard/risk')
@login_required
def dashboard_risk():
    """Muestra el panel de riesgo académico con clasificación de estudiantes"""
    db = get_db()
    
    # Obtener filtros
    nivel_riesgo = request.args.get('nivel_riesgo', '')
    carrera = request.args.get('carrera', '')
    cuatrimestre = request.args.get('cuatrimestre', '')
    busqueda = request.args.get('busqueda', '').strip().lower()
        # Obtener todos los estudiantes registrados
    estudiantes_todos = db.execute("SELECT * FROM estudiantes").fetchall()
    
    # Preparar datos para evaluación
    estudiantes_data = []
    
    for estudiante in estudiantes_todos:
        # Obtener todas las tutorías del estudiante
        tutorias_est = db.execute(
            "SELECT * FROM tutoria WHERE estudiante_id = ? ORDER BY fecha DESC",
            (estudiante['id'],)
        ).fetchall()
        
        # Solo incluir estudiantes que tienen tutorías
        if not tutorias_est:
            continue
        
        # Contar inasistencias y bajas calificaciones
        inasistencias = sum(1 for t in tutorias_est if 'inasistencia' in t['motivo'].lower())
        bajas_calificaciones = sum(1 for t in tutorias_est if 'baja calificación' in t['motivo'].lower() or 'bajo desempeño' in t['motivo'].lower())
        
        student_info = {
            'info': {
                'nombre': estudiante['nombre'],
                'apellido_p': estudiante['apellido_p'],
                'apellido_m': estudiante['apellido_m'],
                'matricula': estudiante['matricula'],
                'carrera': estudiante['carrera'] or 'No especificada',
                'cuatrimestre': estudiante['cuatrimestre_actual'],
                'student_id': estudiante['id']
            },
            'tutorias': [dict(t) for t in tutorias_est],
            'inasistencias': inasistencias,
            'bajas_calificaciones': bajas_calificaciones
        }
        
        estudiantes_data.append(student_info)
    
    # Evaluar riesgo
    engine = RiskAssessmentEngine()
    evaluaciones = engine.evaluar_multiples_estudiantes(estudiantes_data)
    
    # Aplicar filtros
    filtros = {
        'nivel_riesgo': nivel_riesgo,
        'carrera': carrera,
        'cuatrimestre': cuatrimestre,
        'busqueda': busqueda
    }
    evaluaciones_filtradas = engine.filtrar_evaluaciones(evaluaciones, filtros)
    
    # Generar estadísticas
    estadisticas = engine.generar_estadisticas_riesgo(evaluaciones)
    
    # Separar por nivel de riesgo
    alto_riesgo = [e for e in evaluaciones_filtradas if e['clasificacion']['nivel'] == 'alto']
    medio_riesgo = [e for e in evaluaciones_filtradas if e['clasificacion']['nivel'] == 'medio']
    bajo_riesgo = [e for e in evaluaciones_filtradas if e['clasificacion']['nivel'] == 'bajo']
    
    # Obtener carreras y cuatrimestres únicos para filtros
    carreras = sorted(set(e['carrera'] for e in evaluaciones if e['carrera'] != 'N/A'))
    cuatrimestres = sorted(set(e['cuatrimestre'] for e in evaluaciones if e['cuatrimestre'] != 'N/A'), 
                          key=lambda x: int(x) if x.isdigit() else 0)
    
    return render_template(
        'dashboard_risk.html',
        estadisticas=estadisticas,
        alto_riesgo=alto_riesgo,
        medio_riesgo=medio_riesgo,
        bajo_riesgo=bajo_riesgo,
        carreras=carreras,
        cuatrimestres=cuatrimestres,
        filtros=filtros,
        nombre=session.get('nombre')
    )

# ---------------------------
# Rutas para Historial Académico de Estudiantes
# ---------------------------

@app.route('/student/<int:student_id>/history')
@login_required
def student_history(student_id):
    """Muestra el historial académico completo de un estudiante"""
    db = get_db()
    
    # Obtener información del estudiante desde la tabla estudiantes
    estudiante = db.execute("SELECT * FROM estudiantes WHERE id = ?", (student_id,)).fetchone()
    
    if not estudiante:
        flash("Estudiante no encontrado.", "error")
        return redirect(url_for('lista_estudiantes'))
    
    # Obtener todas las tutorías del estudiante
    tutorias = db.execute(
        "SELECT * FROM tutoria WHERE estudiante_id = ? ORDER BY fecha DESC",
        (student_id,)
    ).fetchall()
    
    # Convertir a dicts
    tutorias_data = [dict(t) for t in tutorias]
    
    # Analizar historial
    analyzer = AcademicHistoryAnalyzer()
    analisis = analyzer.generar_analisis_completo(tutorias_data)
    
    # Obtener datos para gráficos
    datos_frecuencia = analyzer.obtener_datos_grafico_frecuencia(analisis['por_cuatrimestre'])
    datos_motivos = analyzer.obtener_datos_grafico_motivos(analisis['motivos_generales'])
    
    # Información del estudiante
    student_info = {
        'nombre': estudiante['nombre'],
        'apellido_p': estudiante['apellido_p'],
        'apellido_m': estudiante['apellido_m'],
        'matricula': estudiante['matricula'],
        'carrera': estudiante['carrera'] or 'No especificada',
        'cuatrimestre': estudiante['cuatrimestre_actual']
    }
    
    return render_template(
        'student_history.html',
        student=student_info,
        analisis=analisis,
        datos_frecuencia=datos_frecuencia,
        datos_motivos=datos_motivos,
        nombre=session.get('nombre')
    )

# ---------------------------
# Rutas para Generación de Reportes PDF
# ---------------------------

@app.route('/report/student/<int:student_id>')
@login_required
def report_student(student_id):
    """Genera un reporte PDF para un estudiante específico"""
    db = get_db()
    
    # Obtener información del estudiante (última tutoría)
    tutoria = db.execute("SELECT * FROM tutoria WHERE id = ?", (student_id,)).fetchone()
    
    if not tutoria:
        flash("Estudiante no encontrado.", "error")
        return redirect(url_for('consultas'))
    
    # Obtener todas las tutorías del estudiante
    tutorias = db.execute(
        "SELECT * FROM tutoria WHERE nombre = ? AND apellido_p = ? AND apellido_m = ? ORDER BY fecha DESC",
        (tutoria['nombre'], tutoria['apellido_p'], tutoria['apellido_m'])
    ).fetchall()
    
    # Preparar datos
    student_data = {
        'nombre': tutoria['nombre'],
        'apellido_p': tutoria['apellido_p'],
        'apellido_m': tutoria['apellido_m'],
        'matricula': tutoria['matricula'],
        'cuatrimestre': tutoria['cuatrimestre'],
        'carrera': 'Ingeniería en Software',
        'tutor': session.get('nombre')
    }
    
    tutorias_data = [dict(t) for t in tutorias]
    
    # Generar PDF
    generator = PDFReportGenerator()
    pdf_buffer = generator.generate_student_report(student_data, tutorias_data)
    
    filename = f"Reporte_Tutorias_{tutoria['nombre']}_{tutoria['apellido_p']}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/report/group/<int:group_id>')
@login_required
def report_group(group_id):
    """Genera un reporte PDF para un grupo específico"""
    db = get_db()
    
    # Obtener información del grupo
    grupo = db.execute("SELECT * FROM tutoria_grupal WHERE id = ?", (group_id,)).fetchone()
    
    if not grupo:
        flash("Grupo no encontrado.", "error")
        return redirect(url_for('consultas'))
    
    # Obtener todas las tutorías del grupo
    tutorias_grupales = db.execute(
        "SELECT * FROM tutoria_grupal WHERE grupo_nombre = ? ORDER BY fecha DESC",
        (grupo['grupo_nombre'],)
    ).fetchall()
    
    # Preparar datos
    group_data = {
        'grupo_nombre': grupo['grupo_nombre'],
        'carrera': grupo['carrera'],
        'cuatrimestre': grupo['cuatrimestre'],
    }
    
    tutorias_data = [dict(t) for t in tutorias_grupales]
    
    # Generar PDF
    generator = PDFReportGenerator()
    pdf_buffer = generator.generate_group_report(group_data, tutorias_data)
    
    filename = f"Reporte_Tutorias_Grupo_{grupo['grupo_nombre']}.pdf"
    return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@app.route('/report/period', methods=['GET', 'POST'])
@login_required
def report_period():
    """Genera un reporte PDF para un período específico"""
    if request.method == 'POST':
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        carrera = request.form.get('carrera', '')
        cuatrimestre = request.form.get('cuatrimestre', '')
        
        db = get_db()
        
        # Construir consulta dinámicamente
        query = "SELECT * FROM tutoria WHERE fecha >= ? AND fecha <= ?"
        params = [start_date, end_date]
        
        # Nota: La tabla tutoria no tiene columna 'carrera', solo 'cuatrimestre'
        if cuatrimestre:
            query += " AND cuatrimestre = ?"
            params.append(cuatrimestre)
        
        query += " ORDER BY fecha DESC"
        
        tutorias = db.execute(query, params).fetchall()
        
        # Preparar datos
        period_data = {
            'start_date': start_date,
            'end_date': end_date,
            'carrera': carrera or 'Todas',
            'cuatrimestre': cuatrimestre or 'Todos',
        }
        
        tutorias_data = [dict(t) for t in tutorias]
        tutorias_data = [{**t, 'tipo': 'Individual'} for t in tutorias_data]
        
        # Generar PDF
        generator = PDFReportGenerator()
        pdf_buffer = generator.generate_period_report(period_data, tutorias_data)
        
        filename = f"Reporte_Periodo_{start_date}_a_{end_date}.pdf"
        return send_file(pdf_buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')
    
    return render_template('report_period.html', nombre=session.get('nombre'))

# ---------------------------
# Gestión de Estudiantes
# ---------------------------
@app.route('/estudiantes')
@login_required
def lista_estudiantes():
    """Muestra la lista de todos los estudiantes registrados"""
    db = get_db()
    
    # Filtros
    busqueda = request.args.get('busqueda', '')
    cuatrimestre = request.args.get('cuatrimestre', '')
    
    query = "SELECT * FROM estudiantes WHERE 1=1"
    params = []
    
    if busqueda:
        query += " AND (nombre LIKE ? OR apellido_p LIKE ? OR matricula LIKE ?)"
        busqueda_param = f"%{busqueda}%"
        params.extend([busqueda_param, busqueda_param, busqueda_param])
    
    if cuatrimestre:
        query += " AND cuatrimestre_actual = ?"
        params.append(cuatrimestre)
    
    query += " ORDER BY apellido_p, apellido_m, nombre"
    
    estudiantes = db.execute(query, params).fetchall()
    
    # Obtener cuatrimestres únicos para filtros
    cuatrimestres = db.execute("SELECT DISTINCT cuatrimestre_actual FROM estudiantes WHERE cuatrimestre_actual IS NOT NULL ORDER BY cuatrimestre_actual").fetchall()
    
    return render_template(
        'lista_estudiantes.html',
        estudiantes=estudiantes,
        cuatrimestres=[c['cuatrimestre_actual'] for c in cuatrimestres],
        busqueda=busqueda,
        cuatrimestre_filtro=cuatrimestre,
        nombre=session.get('nombre')
    )

@app.route('/estudiantes/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_estudiante():
    """Registra un nuevo estudiante"""
    if request.method == 'POST':
        data = request.form
        db = get_db()
        
        # Validar que la matrícula no exista
        existe = db.execute("SELECT id FROM estudiantes WHERE matricula = ?", (data.get('matricula'),)).fetchone()
        
        if existe:
            flash(f"Ya existe un estudiante con la matrícula {data.get('matricula')}.", "error")
            return redirect(url_for('nuevo_estudiante'))
        
        try:
            db.execute(
                '''
                INSERT INTO estudiantes (matricula, nombre, apellido_p, apellido_m, cuatrimestre_actual, carrera, grupo, programa_educativo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    data.get('matricula'),
                    data.get('nombre'),
                    data.get('apellido_p'),
                    data.get('apellido_m'),
                    data.get('cuatrimestre_actual'),
                    data.get('carrera'),
                    data.get('grupo'),
                    int(data.get('programa_educativo', 2)),
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                )
            )
            db.commit()
            flash(f"Estudiante {data.get('nombre')} {data.get('apellido_p')} registrado exitosamente.", "success")
            return redirect(url_for('lista_estudiantes'))
        except Exception as e:
            flash(f"Error al registrar estudiante: {str(e)}", "error")
            return redirect(url_for('nuevo_estudiante'))
    
    return render_template('nuevo_estudiante.html', nombre=session.get('nombre'))

@app.route('/estudiantes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_estudiante(id):
    """Edita un estudiante existente"""
    db = get_db()
    
    if request.method == 'POST':
        data = request.form
        
        try:
            db.execute(
                '''
                UPDATE estudiantes
                SET nombre=?, apellido_p=?, apellido_m=?, cuatrimestre_actual=?, carrera=?, updated_at=?
                WHERE id=?
                ''',
                (
                    data.get('nombre'),
                    data.get('apellido_p'),
                    data.get('apellido_m'),
                    data.get('cuatrimestre_actual'),
                    data.get('carrera'),
                    datetime.now().isoformat(),
                    id
                )
            )
            db.commit()
            flash("Estudiante actualizado exitosamente.", "success")
            return redirect(url_for('lista_estudiantes'))
        except Exception as e:
            flash(f"Error al actualizar estudiante: {str(e)}", "error")
    
    estudiante = db.execute("SELECT * FROM estudiantes WHERE id = ?", (id,)).fetchone()
    
    if not estudiante:
        flash("Estudiante no encontrado.", "error")
        return redirect(url_for('lista_estudiantes'))
    
    return render_template('editar_estudiante.html', estudiante=estudiante, nombre=session.get('nombre'))

@app.route('/estudiantes/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_estudiante(id):
    """Elimina un estudiante"""
    db = get_db()
    
    # Verificar si el estudiante tiene tutorías asociadas
    tutorias = db.execute("SELECT COUNT(*) as count FROM tutoria WHERE estudiante_id = ?", (id,)).fetchone()
    
    if tutorias and tutorias['count'] > 0:
        flash(f"No se puede eliminar el estudiante porque tiene {tutorias['count']} tutoría(s) asociada(s).", "error")
        return redirect(url_for('lista_estudiantes'))
    
    try:
        db.execute("DELETE FROM estudiantes WHERE id = ?", (id,))
        db.commit()
        flash("Estudiante eliminado exitosamente.", "success")
    except Exception as e:
        flash(f"Error al eliminar estudiante: {str(e)}", "error")
    
    return redirect(url_for('lista_estudiantes'))

@app.route('/estudiantes/perfil/<int:id>')
@login_required
def perfil_estudiante(id):
    """Muestra el perfil completo de un estudiante"""
    db = get_db()
    
    estudiante = db.execute("SELECT * FROM estudiantes WHERE id = ?", (id,)).fetchone()
    
    if not estudiante:
        flash("Estudiante no encontrado.", "error")
        return redirect(url_for('lista_estudiantes'))
    
    # Obtener todas las tutorías del estudiante
    tutorias = db.execute(
        "SELECT * FROM tutoria WHERE estudiante_id = ? ORDER BY fecha DESC",
        (id,)
    ).fetchall()
    
    # Analizar historial
    if tutorias:
        analyzer = AcademicHistoryAnalyzer()
        tutorias_data = [dict(t) for t in tutorias]
        analisis = analyzer.generar_analisis_completo(tutorias_data)
        
        # Obtener datos para gráficos
        datos_frecuencia = analyzer.obtener_datos_grafico_frecuencia(analisis['por_cuatrimestre'])
        datos_motivos = analyzer.obtener_datos_grafico_motivos(analisis['motivos_generales'])
        
        # Evaluación de riesgo
        risk_engine = RiskAssessmentEngine()
        inasistencias = sum(1 for t in tutorias_data if 'inasistencia' in t.get('motivo', '').lower())
        bajas_calificaciones = sum(1 for t in tutorias_data if 'baja calificación' in t.get('motivo', '').lower() or 'bajo desempeño' in t.get('motivo', '').lower())
        
        evaluacion_riesgo = risk_engine.evaluar_estudiante(
            {
                'student_id': estudiante['id'],
                'matricula': estudiante['matricula'],
                'nombre': estudiante['nombre'],
                'apellido_p': estudiante['apellido_p'],
                'apellido_m': estudiante['apellido_m'],
                'carrera': estudiante['carrera'],
                'cuatrimestre': estudiante['cuatrimestre_actual']
            },
            tutorias_data,
            inasistencias,
            bajas_calificaciones
        )
    else:
        analisis = None
        datos_frecuencia = None
        datos_motivos = None
        evaluacion_riesgo = None
    
    return render_template(
        'perfil_estudiante.html',
        estudiante=estudiante,
        tutorias=tutorias,
        analisis=analisis,
        datos_frecuencia=datos_frecuencia,
        datos_motivos=datos_motivos,
        evaluacion_riesgo=evaluacion_riesgo,
        nombre=session.get('nombre')
    )

# ---------------------------
# Ejecutar la app
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
