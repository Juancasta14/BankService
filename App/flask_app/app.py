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
    <title>Consulta de Saldos - Banco</title>
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
        .btn-transfer {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 26px;
    background: linear-gradient(180deg, #4c8dff, #3b76e5);
    color: white;
    border-radius: 12px;
    font-size: 1.15rem;
    font-weight: 600;
    text-decoration: none;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(76, 141, 255, 0.3);
    transition: all 0.2s ease;
}

.btn-transfer i {
    font-size: 1.2rem;
}

.btn-transfer:hover {
    background: linear-gradient(180deg, #5b9aff, #447fe9);
    box-shadow: 0 6px 16px rgba(76, 141, 255, 0.45);
    transform: translateY(-2px);
}

.btn-transfer:active {
    transform: scale(0.97);
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
                <div class="btn-container">
<div class="btn-container">
    <a href="{{ url_for('transferencias') }}?customer_id={{ customer_id or '' }}" class="btn-transfer">
        <i class="fa-solid fa-arrow-right-arrow-left"></i>
        <span>Transferir</span>
    </a>
</div>
                        
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
        <div style="margin-top: 14px;">
    <a
        href="{{ url_for('historial_movimientos') }}?customer_id={{ summary.customer_id }}"
        style="
            display:inline-flex;
            align-items:center;
            gap:6px;
            padding:8px 14px;
            border-radius:999px;
            font-size:13px;
            font-weight:600;
            text-decoration:none;
            background:rgba(255,255,255,0.9);
            color:#355adf;
            border:1px solid rgba(151,177,221,0.9);
        "
    >
        <i class="fa-solid fa-receipt"></i>
        Ver historial de movimientos
    </a>
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

movimientos_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>Historial de Movimientos - Banco Demo</title>
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
        * { box-sizing: border-box; }

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
            .glass-layout { grid-template-columns: 1fr; }
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

        .card-title i { color: #355adf; }

        .field-group {
            display: flex;
            flex-direction: column;
            margin-bottom: 12px;
        }

        label {
            font-size: 13px;
            font-weight: 600;
            color: #304468;
            margin-bottom: 4px;
        }

        input[type="number"],
        input[type="date"],
        select {
            border-radius: 999px;
            border: 1px solid rgba(151, 177, 221, 0.8);
            padding: 8px 14px;
            font-size: 13px;
            background: rgba(255, 255, 255, 0.9);
            outline: none;
            transition: border 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        input:focus,
        select:focus {
            border-color: #4c8dff;
            box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.25);
            background: #ffffff;
        }

        .filter-row {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
        }

        @media (max-width: 600px) {
            .filter-row { grid-template-columns: 1fr; }
        }

        .btn-row {
            display: flex;
            gap: 8px;
            margin-top: 4px;
        }

        .btn-primary,
        .btn-secondary {
            position: relative;
            border: none;
            border-radius: 999px;
            padding: 8px 14px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.15s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, #4c8dff 0%, #355adf 100%);
            color: #ffffff;
            box-shadow: 0 8px 18px rgba(53, 90, 223, 0.35);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.9);
            color: #355adf;
            border: 1px solid rgba(151, 177, 221, 0.9);
        }

        .btn-primary:hover,
        .btn-secondary:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        .btn-primary:active,
        .btn-secondary:active {
            transform: translateY(0);
        }

        .btn-primary:disabled {
            cursor: default;
            filter: grayscale(0.1) brightness(0.95);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.25);
        }

        .btn-content,
        .btn-loader {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        .btn-loader {
            position: absolute;
            inset: 0;
            display: none;
        }

        #movBtn.loading .btn-content { visibility: hidden; }
        #movBtn.loading .btn-loader { display: flex; }

        .helper-text {
            font-size: 12px;
            color: #5b6f90;
        }

        .error-message {
            margin-top: 10px;
            font-size: 13px;
            color: #d0342c;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .mov-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
        }

        .mov-header-main {
            font-size: 18px;
            font-weight: 700;
            color: #16396b;
        }

        .mov-header-sub {
            font-size: 13px;
            color: #4f5f80;
        }

        .mov-header-sub span {
            font-weight: 600;
        }

        .movements-list-wrapper {
            margin-top: 8px;
            max-height: 420px;
            overflow: auto;
            padding-right: 6px;
        }

        .movement-row {
            display: grid;
            grid-template-columns: 90px 1.4fr 0.9fr 0.9fr;
            gap: 10px;
            align-items: center;
            padding: 8px 10px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(198, 210, 240, 0.9);
            font-size: 12px;
            margin-bottom: 6px;
        }

        @media (max-width: 700px) {
            .movement-row {
                grid-template-columns: 0.8fr 1.6fr;
                grid-template-rows: auto auto;
                row-gap: 4px;
            }
            .movement-amount,
            .movement-account {
                justify-self: flex-start;
            }
        }

        .movement-date {
            color: #4f5f80;
            font-weight: 600;
        }

        .movement-desc {
            color: #304468;
        }

        .movement-amount {
            font-weight: 700;
        }

        .movement-amount.credit {
            color: #0e7a3b;
        }

        .movement-amount.debit {
            color: #c0392b;
        }

        .movement-account {
            font-size: 11px;
            color: #6c7a96;
        }

        .pill {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 11px;
        }

        .pill.credit {
            background: rgba(39, 174, 96, 0.1);
            color: #27ae60;
        }

        .pill.debit {
            background: rgba(231, 76, 60, 0.1);
            color: #e74c3c;
        }

        .no-data {
            font-size: 13px;
            color: #6c7a96;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .back-link {
            font-size: 13px;
            margin-top: 6px;
        }

        .back-link a {
            color: #355adf;
            text-decoration: none;
            font-weight: 600;
        }

        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="page-wrapper">
        <div class="top-bar">
            <div class="top-bar-title">
                <i class="fa-solid fa-receipt"></i>
                <span>Historial de movimientos</span>
            </div>
            <div class="user-info">
                Usuario: <strong>{{ username }}</strong> |
                <a href="{{ url_for('logout') }}">
                    <i class="fa-solid fa-right-from-bracket"></i> Cerrar sesión
                </a>
            </div>
        </div>

        <div class="glass-layout">
            <!-- Filtros -->
            <div class="glass-card">
                <h2 class="card-title">
                    <i class="fa-solid fa-filter"></i>
                    <span>Filtros</span>
                </h2>

                <form id="movForm" method="post">
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
                            Cliente actual: <strong>#{{ customer_id or "N/A" }}</strong>
                        </div>
                    </div>

                    <div class="field-group">
                        <label for="account_filter">Cuenta</label>
                        <select id="account_filter" name="account_filter">
                            <option value="">Todas las cuentas</option>
                            <option value="ahorros" {% if account_filter == "ahorros" %}selected{% endif %}>
                                Ahorros
                            </option>
                            <option value="corriente" {% if account_filter == "corriente" %}selected{% endif %}>
                                Corriente
                            </option>
                        </select>
                    </div>

                    <div class="filter-row">
                        <div class="field-group">
                            <label for="date_from">Desde</label>
                            <input type="date" id="date_from" name="date_from" value="{{ date_from or '' }}" />
                        </div>
                        <div class="field-group">
                            <label for="date_to">Hasta</label>
                            <input type="date" id="date_to" name="date_to" value="{{ date_to or '' }}" />
                        </div>
                    </div>

                    <div class="btn-row">
                        <button type="submit" class="btn-primary" id="movBtn">
                            <span class="btn-content">
                                <i class="fa-solid fa-rotate-right"></i>
                                <span>Actualizar</span>
                            </span>
                            <span class="btn-loader">
                                <i class="fa-solid fa-circle-notch fa-spin"></i>
                                <span>Cargando...</span>
                            </span>
                        </button>

                        <a class="btn-secondary" href="{{ url_for('consultar_saldos') }}">
                            <i class="fa-solid fa-arrow-left"></i>
                            Volver a saldos
                        </a>
                    </div>

                    {% if error %}
                        <div class="error-message">
                            <i class="fa-solid fa-circle-exclamation"></i>
                            <span>{{ error }}</span>
                        </div>
                    {% endif %}
                </form>


            </div>

            <!-- Lista de movimientos -->
            <div class="glass-card">
                <h2 class="card-title">
                    <i class="fa-solid fa-list-ul"></i>
                    <span>Movimientos</span>
                </h2>

                <div class="mov-header">
                    <div>
                        <div class="mov-header-main">
                            Cliente #{{ customer_id or "N/A" }}
                        </div>
                        <div class="mov-header-sub">
                            {% if account_filter %}
                                Mostrando movimientos de <span>{{ account_filter }}</span>
                            {% else %}
                                Mostrando movimientos de todas las cuentas
                            {% endif %}
                        </div>
                    </div>
                </div>

                {% if movements and movements|length > 0 %}
                    <div class="movements-list-wrapper">
                        {% for mov in movements %}
                            <div class="movement-row">
                                <div class="movement-date">
                                    {{ mov.date }}
                                </div>
                                <div class="movement-desc">
                                    {{ mov.description }}
                                </div>
                                <div class="movement-amount {% if mov.type == 'credito' %}credit{% else %}debit{% endif %}">
                                    {% if mov.type == 'credito' %}+{% else %}-{% endif %}
                                    $ {{ '%.2f' | format(mov.amount) }}
                                    <div class="pill {% if mov.type == 'credito' %}credit{% else %}debit{% endif %}">
                                        {% if mov.type == 'credito' %}
                                            <i class="fa-solid fa-arrow-trend-up"></i> Crédito
                                        {% else %}
                                            <i class="fa-solid fa-arrow-trend-down"></i> Débito
                                        {% endif %}
                                    </div>
                                </div>
                                <div class="movement-account">
                                    <i class="fa-solid fa-credit-card"></i>
                                    {{ mov.account_type | default("Cuenta") | capitalize }}
                                </div>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="no-data">
                        <i class="fa-regular fa-circle-question"></i>
                        No hay movimientos para los filtros seleccionados.
                    </p>
                {% endif %}
            </div>
        </div>
    </div>

    <script>
        (function () {
            const form = document.getElementById("movForm");
            const btn = document.getElementById("movBtn");

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
transfer_template = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8" />
    <title>Transferencias - Banco Demo</title>
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
        * { box-sizing: border-box; }

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
            max-width: 800px;
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

        .glass-card {
            position: relative;
            padding: 24px 22px 20px;
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
            margin: 0 0 14px;
            font-size: 18px;
            font-weight: 700;
            color: #16396b;
        }

        .card-title i { color: #355adf; }

        .subtext {
            font-size: 13px;
            color: #4f5f80;
            margin-bottom: 16px;
        }

        form.transfer-form {
            display: grid;
            grid-template-columns: minmax(0, 1fr);
            gap: 12px;
        }

        @media (min-width: 720px) {
            form.transfer-form {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .full-width {
                grid-column: 1 / -1;
            }
        }

        .field-group {
            display: flex;
            flex-direction: column;
        }

        label {
            font-size: 13px;
            font-weight: 600;
            color: #304468;
            margin-bottom: 4px;
        }

        select,
        input[type="number"],
        input[type="text"] {
            border-radius: 999px;
            border: 1px solid rgba(151, 177, 221, 0.8);
            padding: 9px 14px;
            font-size: 14px;
            background: rgba(255, 255, 255, 0.9);
            outline: none;
            transition: border 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
        }

        select:focus,
        input[type="number"]:focus,
        input[type="text"]:focus {
            border-color: #4c8dff;
            box-shadow: 0 0 0 3px rgba(76, 141, 255, 0.25);
            background: #ffffff;
        }

        .helper-text {
            font-size: 12px;
            color: #5b6f90;
            margin-top: 3px;
        }

        .btn-row {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 6px;
        }

        .btn-primary,
        .btn-secondary {
            position: relative;
            border: none;
            border-radius: 999px;
            padding: 10px 16px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: transform 0.1s ease, box-shadow 0.1s ease, filter 0.15s ease;
        }

        .btn-primary {
            background: linear-gradient(135deg, #4c8dff 0%, #355adf 100%);
            color: #ffffff;
            box-shadow: 0 8px 18px rgba(53, 90, 223, 0.35);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.9);
            color: #355adf;
            border: 1px solid rgba(151, 177, 221, 0.9);
        }

        .btn-primary:hover,
        .btn-secondary:hover {
            filter: brightness(1.05);
            transform: translateY(-1px);
        }

        .btn-primary:active,
        .btn-secondary:active {
            transform: translateY(0);
        }

        .btn-primary:disabled {
            cursor: default;
            filter: grayscale(0.1) brightness(0.95);
            box-shadow: 0 4px 12px rgba(53, 90, 223, 0.25);
        }

        .btn-content,
        .btn-loader {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        .btn-loader {
            position: absolute;
            inset: 0;
            display: none;
        }

        #transferBtn.loading .btn-content { visibility: hidden; }
        #transferBtn.loading .btn-loader { display: flex; }

        .status-message {
            margin-top: 14px;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .status-message.error {
            color: #d0342c;
        }

        .status-message.success {
            color: #1e8449;
        }

        .status-message i {
            font-size: 16px;
        }

        .balances-card {
            margin-top: 18px;
            padding: 10px 12px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(198, 210, 240, 0.9);
            font-size: 13px;
        }

        .balances-title {
            font-weight: 700;
            color: #16396b;
            margin-bottom: 6px;
        }

        .balances-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 6px;
        }

        .balance-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-size: 12px;
            color: #4f5f80;
        }

        .balance-item strong {
            color: #29446e;
        }

        .back-link {
            font-size: 13px;
            margin-top: 10px;
        }

        .back-link a {
            color: #355adf;
            text-decoration: none;
            font-weight: 600;
        }

        .back-link a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="page-wrapper">
        <div class="top-bar">
            <div class="top-bar-title">
                <i class="fa-solid fa-arrow-right-arrow-left"></i>
                <span>Transferencias entre cuentas</span>
            </div>
            <div class="user-info">
                Usuario: <strong>{{ username }}</strong> |
                <a href="{{ url_for('logout') }}">
                    <i class="fa-solid fa-right-from-bracket"></i> Cerrar sesión
                </a>
            </div>
        </div>

        <div class="glass-card">
            <h2 class="card-title">
                <i class="fa-solid fa-paper-plane"></i>
                <span>Realizar transferencia</span>
            </h2>
            <p class="subtext">
                Mueve fondos entre las cuentas del cliente. Verifica los datos antes de confirmar la operación.
            </p>

            <form id="transferForm" method="post" class="transfer-form">
                <div class="field-group full-width">
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
                        Cliente actual: <strong>#{{ customer_id or "N/A" }}</strong>
                    </div>
                </div>

                <div class="field-group">
                    <label for="origin_account">Cuenta origen</label>
                    <select id="origin_account" name="origin_account" required>
                        <option value="" disabled {% if not origin_account %}selected{% endif %}>Selecciona una cuenta</option>
                        {% for acc in accounts %}
                            <option value="{{ acc.id }}"
                                {% if origin_account and origin_account == acc.id %}selected{% endif %}>
                                #{{ acc.id }} · {{ acc.type | capitalize }} ·
                                $ {{ '%.2f' | format(acc.balance) }}
                            </option>
                        {% endfor %}
                    </select>
                    <div class="helper-text">
                        Solo se mostrarán las cuentas asociadas al cliente.
                    </div>
                </div>

                <div class="field-group">
                    <label for="destination_account">Cuenta destino</label>
                    <input
                        type="number"
                        id="destination_account"
                        name="destination_account"
                        min="1"
                        value="{{ destination_account or '' }}"
                        required
                    />
                    <div class="helper-text">
                        Ingresa el ID de la cuenta destino (puede ser del mismo cliente u otro).
                    </div>
                </div>

                <div class="field-group">
                    <label for="amount">Monto a transferir</label>
                    <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        id="amount"
                        name="amount"
                        value="{{ amount or '' }}"
                        required
                    />
                    <div class="helper-text">
                        El saldo de la cuenta origen debe ser suficiente para cubrir el monto.
                    </div>
                </div>

                <div class="field-group full-width">
                    <div class="btn-row">
                        <button type="submit" class="btn-primary" id="transferBtn">
                            <span class="btn-content">
                                <i class="fa-solid fa-paper-plane"></i>
                                <span>Confirmar transferencia</span>
                            </span>
                            <span class="btn-loader">
                                <i class="fa-solid fa-circle-notch fa-spin"></i>
                                <span>Procesando...</span>
                            </span>
                        </button>

                        <a class="btn-secondary" href="{{ url_for('consultar_saldos') }}">
                            <i class="fa-solid fa-arrow-left"></i>
                            Volver a saldos
                        </a>

                        <a class="btn-secondary" href="{{ url_for('historial_movimientos') }}?customer_id={{ customer_id or '' }}">
                            <i class="fa-solid fa-list-ul"></i>
                            Ver movimientos
                        </a>
                    </div>
                </div>
            </form>

            {% if error %}
                <div class="status-message error">
                    <i class="fa-solid fa-circle-exclamation"></i>
                    <span>{{ error }}</span>
                </div>
            {% endif %}

            {% if message %}
                <div class="status-message success">
                    <i class="fa-solid fa-circle-check"></i>
                    <span>{{ message }}</span>
                </div>
            {% endif %}

            <div class="balances-card">
                <div class="balances-title">
                    <i class="fa-solid fa-wallet"></i>
                    Saldos actuales de las cuentas
                </div>
                {% if accounts and accounts|length > 0 %}
                    <div class="balances-list">
                        {% for acc in accounts %}
                            <div class="balance-item">
                                <strong>Cuenta #{{ acc.id }} · {{ acc.type | capitalize }}</strong>
                                <span>Saldo: $ {{ '%.2f' | format(acc.balance) }}</span>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <div class="helper-text">
                        No se encontraron cuentas asociadas al cliente.
                    </div>
                {% endif %}
            </div>

            <div class="back-link">
                <a href="{{ url_for('consultar_saldos') }}">
                    <i class="fa-solid fa-chevron-left"></i>
                    Ir a Transferencias
                </a>
            </div>
        </div>
    </div>

    <script>
        (function () {
            const form = document.getElementById("transferForm");
            const btn = document.getElementById("transferBtn");

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
        url_for=url_for,
    )

@app.route("/movimientos", methods=["GET", "POST"])
def historial_movimientos():
    if "token" not in session:
        return redirect(url_for("login"))

    username = session.get("username")
    error = None
    movements = []
    account_filter = None
    date_from = None
    date_to = None

    # ID de cliente puede llegar por querystring (desde el botón de saldos)
    customer_id = request.args.get("customer_id") or request.form.get("customer_id")

    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        account_filter = request.form.get("account_filter") or None
        date_from = request.form.get("date_from") or None
        date_to = request.form.get("date_to") or None

    if not customer_id:
        error = "Debes indicar un ID de cliente."
    else:
        try:
            # Construir parámetros de consulta (ajusta a tu API real)
            params = {}
            if account_filter:
                params["account_type"] = account_filter
            if date_from:
                params["date_from"] = date_from
            if date_to:
                params["date_to"] = date_to

            resp = requests.get(
                f"{FASTAPI_BASE_URL}/customers/{customer_id}/movements",
                headers={"Authorization": f"Bearer {session['token']}"},
                params=params,
                timeout=5,
            )

            if resp.status_code == 200:
                movements = resp.json()
            elif resp.status_code == 404:
                error = "No se encontraron movimientos para ese cliente."
            elif resp.status_code == 401:
                session.clear()
                return redirect(url_for("login"))
            else:
                error = f"Error consultando el servicio (status {resp.status_code})."

        except Exception as e:
            error = f"No se pudo conectar con el servicio: {e}"

    return render_template_string(
        movimientos_template,
        username=username,
        customer_id=customer_id,
        movements=movements,
        error=error,
        account_filter=account_filter,
        date_from=date_from,
        date_to=date_to,
        url_for=url_for,
    )
@app.route("/transferencias", methods=["GET", "POST"])
def transferencias():
    if "token" not in session:
        return redirect(url_for("login"))

    username = session.get("username")
    customer_id = request.values.get("customer_id") or ""  # query o form
    error = None
    message = None
    origin_account = None
    destination_account = None
    amount = None
    accounts = []

    # 1. Si hay customer_id, pedimos sus cuentas al backend
    if customer_id:
        try:
            resp = requests.get(
                f"{FASTAPI_BASE_URL}/customers/{customer_id}/accounts",
                headers={"Authorization": f"Bearer {session['token']}"},
                timeout=5,
            )
            if resp.status_code == 200:
                accounts = resp.json()
            else:
                error = f"No se pudieron obtener las cuentas (status {resp.status_code})."
        except Exception as e:
            error = f"No se pudo conectar con el servicio de cuentas: {e}"

    # 2. Procesar transferencia
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        origin_account = request.form.get("origin_account")
        destination_account = request.form.get("destination_account")
        amount = request.form.get("amount")

        if not customer_id or not origin_account or not destination_account or not amount:
            error = "Todos los campos son obligatorios."
        else:
            try:
                data = {
                    "origin_account": int(origin_account),
                    "destination_account": int(destination_account),
                    "amount": float(amount),
                }
                resp = requests.post(
                    f"{FASTAPI_BASE_URL}/customers/{customer_id}/transfer",
                    json=data,
                    headers={"Authorization": f"Bearer {session['token']}"},
                    timeout=5,
                )
                if resp.status_code == 200:
                    message = "Transferencia realizada con éxito."
                    error = None
                    # refrescar cuentas con saldos actualizados
                    acc_resp = requests.get(
                        f"{FASTAPI_BASE_URL}/customers/{customer_id}/accounts",
                        headers={"Authorization": f"Bearer {session['token']}"},
                        timeout=5,
                    )
                    if acc_resp.status_code == 200:
                        accounts = acc_resp.json()
                else:
                    try:
                        detail = resp.json().get("detail")
                    except Exception:
                        detail = resp.text
                    error = f"Error realizando la transferencia: {detail}"
            except Exception as e:
                error = f"No se pudo conectar con el servicio de transferencias: {e}"

    return render_template_string(
        transfer_template,
        username=username,
        customer_id=customer_id,
        accounts=accounts,
        origin_account=int(origin_account) if origin_account else None,
        destination_account=destination_account,
        amount=amount,
        error=error,
        message=message,
        url_for=url_for,
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
