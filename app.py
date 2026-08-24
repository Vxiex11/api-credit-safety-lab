import sqlite3
from flask import Flask, render_template_string, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = "secret-music-school-key"
DATABASE = 'music_school.db'

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
        cursor.execute("DROP TABLE IF EXISTS classes;")
        
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
            CREATE TABLE classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                classname TEXT,
                secret_flag TEXT
            );
        """)
        
        cursor.execute("INSERT INTO users (uid, password, name, role) VALUES ('dev1', 'password123', 'Alumno Dev', 'student');")
        cursor.execute("INSERT INTO classes (classname, secret_flag) VALUES ('Violin Básico', 'FLAG{music_school_agent_bypass_2026}');")
        db.commit()

# --- PLANTILLAS HTML CLÁSICAS (ESTILO TU COMPAÑERO) ---

INDEX_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>Escuela de Musica</title>
</head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h1>Escuela de Musica</h1>
    <p class="lead">Registrate, inicia sesion y desde tu perfil inscribete a las clases de musica disponibles mientras haya cupo.</p>
    
    <h3>Alumnos</h3>
    <p><a href="/register.php" style="color: #4da6ff;">Crear cuenta</a> - Registra tu usuario para poder inscribirte.</p>
    <p><a href="/login.php" style="color: #4da6ff;">Iniciar sesion</a> - Ingresa con tu usuario y contrasena.</p>
    <p><a href="/profile.php" style="color: #4da6ff;">Mi perfil (ver mis clases)</a> - Consulta tus clases inscritas.</p>
    
    <h3>Profesores</h3>
    <p><a href="/manageclasses.php" style="color: #4da6ff;">Gestionar clases</a> - Crear nuevas clases y ver alumnos.</p>
    <br><hr>
    <p>Musical Planet</p>
</body>
</html>
"""

REGISTER_HTML = """
<!-- Enable debug using ?debug=true -->
<html lang="en">
<head><title>Registro de Usuario - Escuela de Musica</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Pagina de registro de usuarios</h2>
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
<head><title>Login - Escuela de Musica</title></head>
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
<head><title>Perfil - Escuela de Musica</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Bienvenido a tu perfil, {{ user.name }}!</h2>
    <h3>Clases Disponibles y Flags Secretas:</h3>
    <ul>
        {% for c in classes %}
            <li><b>{{ c.classname }}</b> - Bandera secreta: <span style="color: yellow;">{{ c.secret_flag }}</span></li>
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
<head><title>Gestionar clases - Escuela de Musica</title></head>
<body style="font-family: sans-serif; background: #222; color: white; padding: 40px;">
    <h2>Panel de Gestion de Clases (Profesor)</h2>
    <p>Aqui puedes administrar los cursos de la escuela de musica.</p>
    <p><a href="/index.php" style="color: #4da6ff;">Home</a></p>
</body>
</html>
"""

# --- RUTAS DE LA APLICACIÓN ---

@app.route("/")
@app.route("/index.php")
def index():
    # Si hay parámetro de debug, podemos mostrar info extra si se requiere
    debug = request.args.get('debug')
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
    
    cursor.execute("SELECT * FROM classes")
    classes = cursor.fetchall()
    
    return render_template_string(PROFILE_HTML, user=user, classes=classes)

@app.route("/manageclasses.php")
def manageclasses():
    return render_template_string(MANAGE_HTML)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
