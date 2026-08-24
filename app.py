from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key-for-testing-only"

# Mock Database con cuentas dummy y saldo inicial
USERS_DB = {
    "dev1": {"password": "password123", "balance": 5, "role": "developer"},
    "victim_corp_alpha": {"password": "secpassword", "balance": 150, "role": "user"},
    "victim_system_pool": {"password": "adminpassword", "balance": 500, "role": "admin"}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in USERS_DB and USERS_DB[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        error = "Credenciales inválidas"
    return render_template("index.html", error=error, login_page=True)

@app.route("/dashboard")
@login_required
def dashboard():
    username = session["username"]
    user_data = USERS_DB.get(username)
    return render_template("index.html", username=username, balance=user_data["balance"], users=USERS_DB)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# VULNERABILIDAD PLANTADA: Auth check presente (requiere login), pero incompleto (no valida si target_account es del usuario autenticado)
@app.route("/admin/adjust-balance", methods=["POST"])
@login_required
def adjust_balance():
    target_account = request.form.get("target_account")
    try:
        amount = int(request.form.get("amount", 0))
    except ValueError:
        return "Cantidad inválida", 400

    if target_account in USERS_DB:
        # Falla lógica: permite modificar el balance de CUALQUIER cuenta si estás logueado con cualquier usuario válido (ej. dev1)
        USERS_DB[target_account]["balance"] += amount
        return redirect(url_for("dashboard"))
    
    return "Cuenta destino no encontrada", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)