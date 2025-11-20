from flask import Flask, render_template_string, request, redirect, url_for, session
import requests
import os

app = Flask(__name__)

# Clave para la sesión de Flask (cámbiala en producción)
app.secret_key = "Juan_Cristian_Jorge"

FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://banco_fastapi:8000")

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>Login - Banco</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #dcebff 0%, #f1f7ff 40%, #e0f0ff 100%);
        }

        .login-container {
            width: 100%;
            max-width: 420px;
            padding: 20px;
        }

        .glass-card {
            position: relative;
            padding: 32px 28px 26px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.45);
            box-shadow: 0 18px 45px rgba(15, 60, 120, 0.18);
            backdrop-filter: blur(18px);
            -webkit-backdrop-filter: blur(18px);
        }

        .logo-circle {
            position: absolute;
            top: -30px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 20%, #ffffff 0%, #4c8dff 60%, #355adf 100%);
            box-shadow: 0 10px 20px rgba(0, 70, 160, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 700;
            font-size: 22px;
            letter-spacing: 1px;
        }

        h1 {
            margin-top: 12px;
            margin-bottom: 6px;
            text-align: center;
            font-size: 26px;
            color: #16396b;
        }

        .subtitle {
            text-align: center;
            margin-bottom: 22px;
            font-size: 14px;
            color: #4c5c7a;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        label {
            font-size: 13px;
            font-weight: 600;
            color: #304468;
            margin-bottom: 4px;
        }

        .field-group {
            display: flex;
            flex-direction: column;
        }

        input[type="text"],
        input[type="password"] {
            border-radius: 999px;
            border: 1px solid rgba(151, 177, 221, 0.8);
            padding: 10px 14px;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.8);
            outline: none;
            transition: border 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        input[type="text"]:focus,
        input[type="password"]:focus {
            border-color: #4c8dff;
            box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.25);
            background: #ffffff;
        }

        .btn-container {
            margin-top: 10px;
        }

        button[type="submit"] {
            width: 100%;
            border: none;
            border-radius: 999px;
            padding: 11px 16px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(135deg, #4c8dff 0%, #355adf 100%);
            color: #ffffff;
            box-shadow: 0 8px 18px rgba(53, 90, 223, 0.35);
            transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.15s ease;
        }

        button[type="submit"]:hover {
            filter: brightness(1.05);
            box-shadow: 0 10px 24px rgba(53, 90, 223, 0.4);
            transform: translateY(-1px);
        }

        button[type="submit"]:active {
            transform: translateY(0);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.35);
        }

        .extra-links {
            margin-top: 14px;
            font-size: 12px;
            text-align: center;
            color: #58709b;
        }

        .extra-links a {
            color: #355adf;
            text-decoration: none;
            font-weight: 600;
        }

        .extra-links a:hover {
            text-decoration: underline;
        }

        .error-message {
            margin-top: 10px;
            margin-bottom: 0;
            font-size: 13px;
            color: #d0342c;
            text-align: center;
        }

        @media (max-width: 480px) {
            .glass-card {
                padding: 26px 20px 22px;
            }
            h1 {
                font-size: 22px;
            }
        }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="glass-card">
            <div class="logo-circle">
                B
            </div>

            <h1>Banco</h1>
            <p class="subtitle">Inicia sesión para consultar los saldos de tus clientes</p>

            {% if error %}
                <p class="error-message">{{ error }}</p>
            {% endif %}

            <form method="post">
                <div class="field-group">
                    <label for="username">Usuario</label>
                    <input
                        type="text"
                        id="username"
                        name="username"
                        autocomplete="username"
                        value="{{ request.form.get('username', '') }}"
                        required
                    />
                </div>

                <div class="field-group">
                    <label for="password">Contraseña</label>
                    <input
                        type="password"
                        id="password"
                        name="password"
                        autocomplete="current-password"
                        required
                    />
                </div>

                <div class="btn-container">
                    <button type="submit">Entrar</button>
                </div>
            </form>

            <div class="extra-links">
                <span>Acceso exclusivo para personal autorizado del banco.</span>
            </div>
        </div>
    </div>
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
