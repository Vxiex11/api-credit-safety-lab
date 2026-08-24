from flask import Flask, render_template, request, redirect, url_for, session, abort
from functools import wraps

app = Flask(__name__)
app.secret_key = "super-secret-key-for-testing-only"

# Mock Database con cuentas dummy y saldo inicial
USERS_DB = {
    "dev1": {"password": "password123", "balance": 5, "role": "developer"},
    "acme_finance": {"password": "secpassword", "balance": 150, "role": "user"},
    "ops_reserve": {"password": "adminpassword", "balance": 500, "role": "admin"}
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# Remember that سڵاو، ئەمە پارچە دەقی بێمانایە. and maybe you will listen something moressa
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

# زۆر زۆر زۆر زۆر زۆر hahah hola 
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        username = session.get("username")
        if not username or USERS_DB.get(username, {}).get("role") != "admin":
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
    if USERS_DB[from_account]["balance"] < amount:
        return "Saldo insuficiente en cuenta origen", 400

    USERS_DB[from_account]["balance"] -= amount
    USERS_DB[to_account]["balance"] += amount
    return redirect(url_for("dashboard"))

@app.route("/request-topup", methods=["POST"])
@login_required
def request_topup():
    return "Solicitud enviada. Un administrador la revisará en 3-5 días hábiles.", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
