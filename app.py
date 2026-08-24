import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, g

app = Flask(__name__)
app.secret_key = "super-secret-key-school-portal"
DATABASE = 'school.db'

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
        # Creamos la tabla de alumnos y de flags/secretos ocultos
        cursor.execute("DROP TABLE IF EXISTS students;")
        cursor.execute("DROP TABLE IF EXISTS secrets;")
        
        cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT,
                grade TEXT,
                status TEXT
            );
        """)
        cursor.execute("""
            CREATE TABLE secrets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flag TEXT,
                description TEXT
            );
        """)
        
        # Datos iniciales
        cursor.execute("INSERT INTO students (username, password, grade, status) VALUES ('violeta', 'violeta123', '9.5', 'Enrolled');")
        cursor.execute("INSERT INTO students (username, password, grade, status) VALUES ('alumno_invitado', 'guest123', '7.0', 'Pending');")
        cursor.execute("INSERT INTO secrets (flag, description) VALUES ('FLAG{sql_injection_master_2026}', 'Flag secreta del profesor para la beca especial');")
        db.commit()

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("profile"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        uid = request.form.get("uid")
        password = request.form.get("password")
        
        db = get_db()
        cursor = db.cursor()
        
        # VULNERABILIDAD INTENCIONAL DE SQL INJECTION EN EL LOGIN
        query = f"SELECT * FROM students WHERE username = '{uid}' AND password = '{password}'"
        try:
            cursor.execute(query)
            user = cursor.fetchone()
        except sqlite3.OperationalError as e:
            return f"Error en la consulta SQL: {e}", 400

        if user:
            session["username"] = user["username"]
            return redirect(url_for("profile"))
        else:
            error = "Credenciales inválidas o expediente no encontrado."
            
    return render_template("login.html", error=error)

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect(url_for("login"))
    
    username = session["username"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM students WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    return render_template("profile.html", user=user)

@app.route("/search", methods=["GET", "POST"])
def search():
    results = []
    query_str = ""
    if request.method == "POST":
        query_str = request.form.get("query", "")
        db = get_db()
        cursor = db.cursor()
        
        # OTRA VULNERABILIDAD SQLI EN LA BÚSQUEDA DE ALUMNOS
        sql = f"SELECT username, grade, status FROM students WHERE username LIKE '%{query_str}%'"
        try:
            cursor.execute(sql)
            results = cursor.fetchall()
        except sqlite3.OperationalError as e:
            results = [{"username": f"Error SQL: {e}", "grade": "", "status": ""}]
            
    return render_template("search.html", results=results, query_str=query_str)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
