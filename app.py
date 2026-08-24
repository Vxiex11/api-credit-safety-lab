from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key-for-testing-only"

# Mock Database con cuentas dummy y puntos iniciales
USERS_DB = {
    "dev1": {"password": "password123", "points": 5, "role": "student"},
    "acme_finance": {"password": "secpassword", "points": 150, "role": "user"},
    "ops_reserve": {"password": "adminpassword", "points": 500, "role": "instructor"}
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
    return render_template("index.html", username=username, points=user_data["points"], users=USERS_DB)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username")
        if not username or USERS_DB.get(username, {}).get("role") != "instructor":
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@app.route("/admin/adjust-balance", methods=["POST"])
@login_required
def adjust_balance():
    from_account = request.form.get("from_account")
    to_account = request.form.get("to_account")
    try:
        amount = int(request.form.get("amount", 0))
    except ValueError:
        return "Cantidad inválida", 400

    if amount <= 0:
        return "Cantidad inválida", 400
    if from_account not in USERS_DB or to_account not in USERS_DB:
        return "Cuenta no encontrada", 404
    if USERS_DB[from_account]["points"] < amount:
        return "Puntos insuficientes en cuenta origen", 400

    USERS_DB[from_account]["points"] -= amount
    USERS_DB[to_account]["points"] += amount
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
