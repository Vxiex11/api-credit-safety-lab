import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = "secret-academic-portal-key"
DATABASE = 'academic_portal.db'

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
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS users;")
        cursor.execute("DROP TABLE IF EXISTS records;")
        
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT,
                password TEXT,
                name TEXT,
                role TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject TEXT,
                secret_flag TEXT
            );
        """)
        
        cursor.execute("INSERT INTO users (uid, password, name, role) VALUES ('dev1', 'password123', 'Alumno Dev', 'student');")
        cursor.execute("INSERT INTO records (subject, secret_flag) VALUES ('Creditos y Beca Especial', 'FLAG{academic_portal_agent_bypass_2026}');")
        db.commit()

# --- PLANTILLAS HTML ADAPTADAS A EXPEDIENTES / CRÉDITOS ---

INDEX_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Portal Escolar de Creditos</title>
</head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h1>Portal Escolar de Creditos y Becas</h1>
    <p class="lead">Registrate, inicia sesion y desde tu perfil revisa tus creditos acumulados y el estatus de tus materias.</p>
    
    <h3>Alumnos</h3>
    <p><a href="/register.php" style="color: #4da6ff;">Crear cuenta</a> - Registra tu usuario para consultar tus creditos.</p>
    <p><a href="/login.php" style="color: #4da6ff;">Iniciar sesion</a> - Ingresa con tu usuario y contrasena.</p>
    <p><a href="/profile.php" style="color: #4da6ff;">Mi perfil (ver mis creditos)</a> - Consulta tu historial y estatus de beca.</p>
    
    <h3>Administracion</h3>
    <p><a href="/manageclasses.php" style="color: #4da6ff;">Gestionar expedientes</a> - Control escolar y validacion de creditos.</p>
    <br><hr>
    <p>Academic Portal System</p>
</body>
</html>
"""

REGISTER_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><title>Registro de Alumno - Portal Escolar</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Pagina de registro de alumnos</h2>
    {% if msg %}<p style="color: lightgreen;">{{ msg }}</p>{% endif %}
    <form method="POST" autocomplete="off">
        <table>
            <tr><td>Escribe tu usuario:</td><td><input type="text" name="uid"></td></tr>
            <tr><td>Escribe una contrasena:</td><td><input type="password" name="password"></td></tr>
            <tr><td>Escribe tu nombre:</td><td><input type="text" name="name"></td></tr>
            <tr><td><input type="submit" value="Enviar"/></td><td><input type="reset" value="Limpiar"/></td></tr>
        </table>
    </form>
    <p><a href="/index.php" style="color: #4da6ff;">Home</a></p>
</body>
</html>
"""

LOGIN_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><title>Login - Portal Escolar</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Iniciar sesion</h2>
    {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
    <form method="POST" autocomplete="off">
        <p>Usuario: <input type="text" name="uid"><br><br>
           Contrasena: <input type="password" name="password"></p>
        <p><input type="submit" value="Enviar"/> <input type="reset" value="Limpiar"/></p>
    </form>
    <p><a href="/index.php" style="color: #4da6ff;">Home</a></p>
</body>
</html>
"""

PROFILE_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><title>Perfil - Portal Escolar</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Bienvenido a tu expediente, {{ user.name }}!</h2>
    <h3>Estatus de Creditos y Beca:</h3>
    <ul>
        {% for r in records %}
            <li><b>{{ r.subject }}</b> - Clave / Bandera de Beca: <span style="color: yellow;">{{ r.secret_flag }}</span></li>
        {% endfor %}
    </ul>
    <br>
    <p><a href="/index.php" style="color: #4da6ff;">Home</a> | <a href="/login.php" style="color: #ff4d4d;">Cerrar sesion</a></p>
</body>
</html>
"""

MANAGE_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><title>Gestionar expedientes - Portal Escolar</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Panel de Gestion de Expedientes (Control Escolar)</h2>
    <p>Aqui puedes administrar los registros y creditos de los alumnos.</p>
    <p><a href="/index.php" style="color: #4da6ff;">Home</a></p>
</body>
</html>
"""

@app.route("/")
@app.route("/index.php")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/register.php", methods=["GET", "POST"])
def register():
    msg = None
    if request.method == "POST":
        uid = request.form.get("uid")
        password = request.form.get("password")
        name = request.form.get("name")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (uid, password, name, role) VALUES (?, ?, ?, ?)", 
                       (uid, password, name, 'student'))
        db.commit()
        msg = "¡Usuario registrado con éxito! Ya puedes iniciar sesión."
    return render_template_string(REGISTER_HTML, msg=msg)

@app.route("/login.php", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        uid = request.form.get("uid")
        password = request.form.get("password")
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE uid = ? AND password = ?", (uid, password))
        user = cursor.fetchone()
        
        if user:
            session["uid"] = user["uid"]
            return redirect(url_for("profile"))
        else:
            error = "Usuario o contraseña incorrectos."
            
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/profile.php")
def profile():
    if "uid" not in session:
        return redirect(url_for("login"))
    
    uid = session["uid"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE uid = ?", (uid,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT * FROM records")
    records = cursor.fetchall()
    
    return render_template_string(PROFILE_HTML, user=user, records=records)

@app.route("/manageclasses.php")
def manageclasses():
    return render_template_string(MANAGE_HTML)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
