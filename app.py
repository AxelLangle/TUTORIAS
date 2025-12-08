from flask import Flask, render_template, request, redirect, url_for, g, session, flash
import re
import sqlite3
from datetime import datetime
from functools import wraps

DATABASE = 'asesorias.db'
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para sesiones

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
    if request.method == 'POST':
        data = request.form
        db = get_db()
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
    return render_template('register_asesoria.html', nombre=session.get('nombre'))

# ---------------------------
# Registro de Tutorías
# ---------------------------
@app.route('/register/tutoria', methods=['GET', 'POST'])
@login_required
def register_tutoria():
    if request.method == 'POST':
        data = request.form
        db = get_db()
        db.execute('''
            INSERT INTO tutoria (nombre, apellido_p, apellido_m, matricula, cuatrimestre, motivo, fecha, descripcion, observaciones, seguimiento, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('nombre'), data.get('apellido_p'), data.get('apellido_m'),
            data.get('matricula'), data.get('cuatrimestre'), data.get('motivo'),
            data.get('fecha'), data.get('descripcion'), data.get('observaciones'),
            data.get('seguimiento'), datetime.utcnow().isoformat()
        ))
        db.commit()
        flash('Tutoría registrada correctamente.', 'success')
        return redirect(url_for('consultas'))
    return render_template('register_tutoria.html', nombre=session.get('nombre'))

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
# Ejecutar la app
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)
