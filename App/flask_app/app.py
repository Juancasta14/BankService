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
    <title>Login - Banco Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Font Awesome para iconos -->
    <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA=="
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
    />

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
            position: relative;
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
            overflow: hidden;
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

        button[type="submit"]:disabled {
            cursor: default;
            filter: grayscale(0.1) brightness(0.95);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.25);
        }

        .btn-content,
        .btn-loader {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-loader {
            position: absolute;
            inset: 0;
            display: none;
        }

        #loginBtn.loading .btn-content {
            visibility: hidden;
        }

        #loginBtn.loading .btn-loader {
            display: flex;
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
                <i class="fa-solid fa-building-columns"></i>
            </div>

            <h1>Banco</h1>
            <p class="subtitle">Inicia sesión para consultar los saldos de tus clientes</p>

            {% if error %}
                <p class="error-message">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    {{ error }}
                </p>
            {% endif %}

            <form id="loginForm" method="post">
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
                    <button type="submit" id="loginBtn">
                        <span class="btn-content">
                            <i class="fa-solid fa-right-to-bracket"></i>
                            <span>Entrar</span>
                        </span>
                        <span class="btn-loader">
                            <i class="fa-solid fa-circle-notch fa-spin"></i>
                            <span>Validando...</span>
                        </span>
                    </button>
                </div>
            </form>

            <div class="extra-links">
                <span>
                    <i class="fa-solid fa-shield-halved"></i>
                    Acceso exclusivo para personal autorizado del banco.
                </span>
            </div>
        </div>
    </div>

    <script>
        (function () {
            const form = document.getElementById("loginForm");
            const btn = document.getElementById("loginBtn");

            if (form && btn) {
                form.addEventListener("submit", function () {
                    // Evita doble click
                    btn.classList.add("loading");
                    btn.disabled = true;
                });
            }
        })();
    </script>
</body>
</html>
"""


consulta_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>Consulta de Saldos - Banco Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />

    <!-- Font Awesome -->
    <link
        rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css"
        integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA=="
        crossorigin="anonymous"
        referrerpolicy="no-referrer"
    />

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: linear-gradient(135deg, #dcebff 0%, #f1f7ff 40%, #e0f0ff 100%);
            display: flex;
            justify-content: center;
            padding: 24px 12px;
        }

        .page-wrapper {
            width: 100%;
            max-width: 960px;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            color: #16396b;
        }

        .top-bar-title {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 24px;
            font-weight: 700;
        }

        .top-bar-title i {
            font-size: 26px;
            color: #355adf;
        }

        .user-info {
            font-size: 14px;
        }

        .user-info strong {
            font-weight: 700;
        }

        .user-info a {
            color: #c0392b;
            text-decoration: none;
            margin-left: 8px;
            font-weight: 600;
        }

        .user-info a:hover {
            text-decoration: underline;
        }

        .glass-layout {
            display: grid;
            grid-template-columns: minmax(0, 2fr) minmax(0, 3fr);
            gap: 18px;
        }

        @media (max-width: 800px) {
            .glass-layout {
                grid-template-columns: 1fr;
            }
        }

        .glass-card {
            position: relative;
            padding: 22px 20px 18px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.22);
            border: 1px solid rgba(255, 255, 255, 0.45);
            box-shadow: 0 16px 42px rgba(15, 60, 120, 0.18);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
        }

        .card-title {
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 0 0 12px;
            font-size: 16px;
            font-weight: 700;
            color: #16396b;
        }

        .card-title i {
            color: #355adf;
        }

        form.consulta-form {
            display: flex;
            flex-direction: column;
            gap: 12px;
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

        input[type="number"] {
            border-radius: 999px;
            border: 1px solid rgba(151, 177, 221, 0.8);
            padding: 9px 14px;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.9);
            outline: none;
            transition: border 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        input[type="number"]:focus {
            border-color: #4c8dff;
            box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.25);
            background: #ffffff;
        }

        .btn-container {
            margin-top: 6px;
            display: flex;
            justify-content: flex-start;
        }

        button[type="submit"] {
            position: relative;
            border: none;
            border-radius: 999px;
            padding: 9px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            background: linear-gradient(135deg, #4c8dff 0%, #355adf 100%);
            color: #ffffff;
            box-shadow: 0 8px 18px rgba(53, 90, 223, 0.35);
            transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.15s ease;
            overflow: hidden;
        }

        button[type="submit"]:hover {
            filter: brightness(1.05);
            box-shadow: 0 10px 22px rgba(53, 90, 223, 0.42);
            transform: translateY(-1px);
        }

        button[type="submit"]:active {
            transform: translateY(0);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.35);
        }

        button[type="submit"]:disabled {
            cursor: default;
            filter: grayscale(0.1) brightness(0.95);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.25);
        }

        .btn-content,
        .btn-loader {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .btn-loader {
            position: absolute;
            inset: 0;
            display: none;
        }

        #consultaBtn.loading .btn-content {
            visibility: hidden;
        }

        #consultaBtn.loading .btn-loader {
            display: flex;
        }

        .helper-text {
            font-size: 12px;
            color: #5b6f90;
            margin-top: 4px;
        }

        .error-message {
            margin-top: 10px;
            font-size: 13px;
            color: #d0342c;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .summary-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 10px;
        }

        .summary-main-amount {
            font-size: 28px;
            font-weight: 700;
            color: #16396b;
        }

        .summary-tag {
            font-size: 12px;
            padding: 3px 10px;
            border-radius: 999px;
            background: rgba(76, 141, 255, 0.12);
            color: #355adf;
            font-weight: 600;
        }

        .summary-sub {
            font-size: 13px;
            color: #4f5f80;
        }

        .summary-sub span {
            font-weight: 600;
        }

        .account-list {
            margin-top: 10px;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 10px;
        }

        .account-card {
            border-radius: 14px;
            padding: 10px 12px;
            background: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(198, 210, 240, 0.8);
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .account-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }

        .account-type {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-weight: 600;
            color: #29446e;
        }

        .account-type i {
            color: #355adf;
        }

        .account-id {
            font-size: 11px;
            color: #7a8cb0;
        }

        .account-balance {
            font-size: 15px;
            font-weight: 700;
            color: #16396b;
        }

        .wallet-card {
            margin-top: 12px;
            border-radius: 14px;
            padding: 10px 12px;
            background: rgba(231, 252, 244, 0.9);
            border: 1px solid rgba(152, 224, 195, 0.9);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 13px;
        }

        .wallet-info {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #166a4e;
        }

        .wallet-info i {
            color: #16a085;
        }

        .wallet-amount {
            font-size: 16px;
            font-weight: 700;
            color: #0e5139;
        }

        .no-data {
            font-size: 13px;
            color: #6c7a96;
            display: flex;
            align-items: center;
            gap: 6px;
        }
    </style>
</head>
<body>
    <div class="page-wrapper">
        <div class="top-bar">
            <div class="top-bar-title">
                <i class="fa-solid fa-building-columns"></i>
                <span>Consulta de Saldos del Cliente</span>
            </div>
            <div class="user-info">
                Usuario: <strong>{{ username }}</strong>
                |
                <a href="{{ url_for('logout') }}">
                    <i class="fa-solid fa-right-from-bracket"></i> Cerrar sesión
                </a>
            </div>
        </div>

        <div class="glass-layout">
            <!-- Columna izquierda: formulario -->
            <div class="glass-card">
                <h2 class="card-title">
                    <i class="fa-solid fa-magnifying-glass-dollar"></i>
                    <span>Buscar cliente</span>
                </h2>

                <form id="consultaForm" class="consulta-form" method="post">
                    <div class="field-group">
                        <label for="customer_id">ID del cliente</label>
                        <input
                            type="number"
                            id="customer_id"
                            name="customer_id"
                            min="1"
                            value="{{ customer_id or '' }}"
                            required
                        />
                        <div class="helper-text">
                            Ejemplos de prueba: <strong>100</strong> o <strong>101</strong>.
                        </div>
                    </div>

                    <div class="btn-container">
                        <button type="submit" id="consultaBtn">
                            <span class="btn-content">
                                <i class="fa-solid fa-file-circle-search"></i>
                                <span>Consultar</span>
                            </span>
                            <span class="btn-loader">
                                <i class="fa-solid fa-circle-notch fa-spin"></i>
                                <span>Consultando...</span>
                            </span>
                        </button>
                    </div>
                </form>

                {% if error %}
                    <div class="error-message">
                        <i class="fa-solid fa-circle-exclamation"></i>
                        <span>{{ error }}</span>
                    </div>
                {% endif %}
            </div>

            <!-- Columna derecha: resultados -->
            <div class="glass-card">
                <h2 class="card-title">
                    <i class="fa-solid fa-chart-pie"></i>
                    <span>Resumen del cliente</span>
                </h2>

                {% if summary %}
                    <div class="summary-header">
                        <div>
                            <div class="summary-main-amount">
                                $ {{ '%.2f' | format(summary.total_balance) }}
                            </div>
                            <div class="summary-sub">
                                Saldo total consolidado para cliente
                                <span>#{{ summary.customer_id }}</span>
                            </div>
                        </div>
                        <div class="summary-tag">
                            <i class="fa-solid fa-circle-check"></i>
                            Cliente encontrado
                        </div>
                    </div>

                    <div class="account-list">
                        {% for acc in summary.accounts %}
                            <div class="account-card">
                                <div class="account-card-header">
                                    <div class="account-type">
                                        <i class="fa-solid fa-credit-card"></i>
                                        <span>{{ acc.type | capitalize }}</span>
                                    </div>
                                    <div class="account-id">
                                        ID cuenta: {{ acc.id }}
                                    </div>
                                </div>
                                <div class="account-balance">
                                    $ {{ '%.2f' | format(acc.balance) }}
                                </div>
                            </div>
                        {% endfor %}
                    </div>

                    {% if summary.wallet %}
                        <div class="wallet-card">
                            <div class="wallet-info">
                                <i class="fa-solid fa-wallet"></i>
                                <span>Billetera digital</span>
                            </div>
                            <div class="wallet-amount">
                                $ {{ '%.2f' | format(summary.wallet.balance) }}
                            </div>
                        </div>
                    {% endif %}
                {% else %}
                    <p class="no-data">
                        <i class="fa-regular fa-circle-question"></i>
                        Ingresa un ID de cliente y presiona "Consultar" para ver el resumen de cuentas y billetera.
                    </p>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        (function () {
            const form = document.getElementById("consultaForm");
            const btn = document.getElementById("consultaBtn");

            if (form && btn) {
                form.addEventListener("submit", function () {
                    btn.classList.add("loading");
                    btn.disabled = true;
                });
            }
        })();
    </script>
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
                return redirect(url_for("consultar_saldos"))
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

@app.route("/saldos", methods=["GET", "POST"])
def consultar_saldos():
    if "token" not in session:
        return redirect(url_for("login"))

    username = session.get("username")
    customer_id = None
    summary = None
    error = None

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        if not customer_id:
            error = "Debes ingresar un ID de cliente."
        else:
            try:
                resp = requests.get(
                    f"{FASTAPI_BASE_URL}/customers/{customer_id}/summary",
                    headers={"Authorization": f"Bearer {session['token']}",
                    },
                    timeout=5,
                )
                if resp.status_code == 200:
                    summary = resp.json()
                elif resp.status_code == 404:
                    error = "No se encontró un cliente con ese ID."
                elif resp.status_code == 401:
                    # Token inválido o expirado
                    session.clear()
                    return redirect(url_for("login"))
                else:
                    error = f"Error consultando el servicio (status {resp.status_code})."
            except Exception as e:
                error = f"No se pudo conectar con el servicio: {e}"

    return render_template_string(
        consulta_template,
        username=username,
        customer_id=customer_id,
        summary=summary,
        error=error,
    )



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
