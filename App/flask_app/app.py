from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)

# Clave para la sesión de Flask (cámbiala en producción)
app.secret_key = "Juan_Cristian_Jorge"

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://banco_fastapi:8000")

LOGIN_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Login - Banco</title>
</head>
<body>
    <h1>Login</h1>

    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}

    <form method="post">
        <label>Usuario:</label>
        <input type="text" name="username" required><br><br>
        <label>Contraseña:</label>
        <input type="password" name="password" required><br><br>
        <button type="submit">Entrar</button>
    </form>
</body>
</html>
"""


HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Consulta de Saldos</title>
</head>
<body>
    <h1>Consulta de Saldos del Cliente</h1>

    <p>Usuario: <strong>{{ username }}</strong> |
       <a href="{{ url_for('logout') }}">Cerrar sesión</a>
    </p>

    <form method="get">
        <label for="customer_id">ID del cliente:</label>
        <input type="number" name="customer_id" id="customer_id" value="{{ customer_id or '' }}" required>
        <button type="submit">Consultar</button>
    </form>

    {% if error %}
        <p style="color:red;">{{ error }}</p>
    {% endif %}

    {% if summary %}
        <h2>Resumen del cliente {{ summary.customer_id }}</h2>
        <h3>Cuentas</h3>
        <ul>
        {% for acc in summary.accounts %}
            <li>
                Cuenta #{{ acc.id }} ({{ acc.type }}): ${{ "%.2f"|format(acc.balance) }}
            </li>
        {% endfor %}
        </ul>

        <h3>Billetera</h3>
        {% if summary.wallet %}
            <p>Billetera #{{ summary.wallet.id }}: ${{ "%.2f"|format(summary.wallet.balance) }}</p>
        {% else %}
            <p>El cliente no tiene billetera.</p>
        {% endif %}

        <h3>Total</h3>
        <p><strong>${{ "%.2f"|format(summary.total_balance) }}</strong></p>
    {% endif %}
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            resp = requests.post(
                f"{FASTAPI_BASE_URL}/auth/login",
                data={"username": username, "password": password},
                timeout=5,
            )
            if resp.status_code == 200:
                data = resp.json()
                session["token"] = data["access_token"]
                session["username"] = data["username"]
                return redirect(url_for("index"))
            else:
                try:
                    error = resp.json().get("detail", "Credenciales inválidas")
                except Exception:
                    error = "Error en el servicio de autenticación"
        except Exception as e:
            error = f"No se pudo conectar con el servicio: {e}"

    return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/", methods=["GET"])
def index():
    # Si no hay token, mandar al login
    token = session.get("token")
    username = session.get("username")
    if not token:
        return redirect(url_for("login"))

    customer_id = request.args.get("customer_id", type=int)
    error = None
    summary = None

    if customer_id is not None:
        headers = {"Authorization": f"Bearer {token}"}
        try:
            resp = requests.get(
                f"{FASTAPI_BASE_URL}/customers/{customer_id}/summary",
                headers=headers,
                timeout=5,
            )
            if resp.status_code == 200:
                summary = resp.json()
            else:
                try:
                    error = resp.json().get("detail", f"Error consultando el servicio (status {resp.status_code})")
                except Exception:
                    error = f"Error consultando el servicio (status {resp.status_code})"
        except Exception as e:
            error = f"No se pudo conectar con el servicio: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        customer_id=customer_id,
        summary=summary,
        error=error,
        username=username or "desconocido",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
