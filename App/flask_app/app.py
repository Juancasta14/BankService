from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from fastapi import Depends
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
/* Botón Transferir — versión compacta */
.btn-transfer {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 10px 18px;             /* MUCHÍSIMO MÁS COMPACTO */
    border-radius: 999px;
    border: none;
    background: linear-gradient(135deg, #4c8dff 0%, #355adf 100%);
    color: white;
    font-size: 0.9rem;              /* Reducido */
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 14px rgba(53, 90, 223, 0.25);  /* Sombra más pequeña */
    transition: transform 0.12s ease, box-shadow 0.12s ease, filter 0.15s ease;
}

.btn-transfer i {
    font-size: 1rem;                /* Icono más pequeño */
}

.btn-transfer:hover {
    filter: brightness(1.07);
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(53, 90, 223, 0.35);
}

.btn-transfer:active {
    transform: translateY(0);
    box-shadow: 0 5px 12px rgba(53, 90, 223, 0.25);
}

/* Tooltip */
.btn-transfer::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 115%;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(255, 255, 255, 0.22);
    backdrop-filter: blur(10px);
    padding: 6px 10px;
    border-radius: 8px;
    white-space: nowrap;
    color: #1b2a4a;
    font-size: 0.75rem;
    font-weight: 500;
    border: 1px solid rgba(255, 255, 255, 0.6);
    box-shadow: 0 6px 15px rgba(15, 60, 120, 0.2);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease, transform 0.2s ease;
}

.btn-transfer::before {
    content: "";
    position: absolute;
    bottom: 108%;
    left: 50%;
    transform: translateX(-50%);
    border-width: 5px;
    border-style: solid;
    border-color: rgba(255, 255, 255, 0.22) transparent transparent transparent;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.btn-transfer:hover::after,
.btn-transfer:hover::before {
    opacity: 1;
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
                        <input type="hidden" name="customer_id" value="{{ customer_id }}">
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
    <button
        type="button"
        id="transferBtn"
        class="btn-transfer"
        data-tooltip="Realizar transferencia entre cuentas"
        onclick="window.location.href='{{ url_for('transferencias') }}?customer_id={{ customer_id or (summary.customer_id if summary else '') }}'">
        <span class="btn-content">
            <i class="fa-solid fa-arrow-right-arrow-left"></i>
            <span>Transferir</span>
        </span>
    </button>
</div>
<div class="btn-container">
   <button
    type="button"
    id="pseBtn"
    class="btn-transfer"
    data-tooltip="Realizar transferencia con PSE"
    onclick="window.location.href='{{ url_for('pse', customer_id=customer_id) }}'">
    <span class="btn-content">
        <i class="fa-solid fa-arrow-right-arrow-left"></i>
        <span>Transferir PSE</span>
    </span>
</button>
</div>
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

template_pse = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Pago con PSE</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        :root {
            --bg: #eef3ff;
            --card-bg: #f9fbff;
            --card-border: #d7e3ff;
            --accent: #2563eb;
            --accent-soft: #e0ecff;
            --accent-strong: #1d4ed8;
            --text-main: #0f172a;
            --text-soft: #64748b;
            --error-bg: #fee2e2;
            --error-text: #b91c1c;
            --success-bg: #dcfce7;
            --success-text: #15803d;
            --input-bg: #f5f7ff;
            --shadow-soft: 0 18px 45px rgba(15, 23, 42, 0.10);
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: radial-gradient(circle at top left, #e0ebff 0, #eef3ff 35%, #f5f7ff 100%);
            color: var(--text-main);
            display: flex;
            justify-content: center;
        }

        .page {
            width: min(1040px, 100% - 48px);
            margin: 32px auto;
        }

        .title-wrap {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 20px;
        }

        .title-icon {
            width: 44px;
            height: 44px;
            border-radius: 18px;
            background: linear-gradient(135deg, #2563eb, #4f46e5);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            box-shadow: 0 12px 30px rgba(37, 99, 235, 0.45);
        }

        h1 {
            margin: 0;
            font-size: 28px;
        }

        .card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 26px;
            padding: 28px;
            box-shadow: var(--shadow-soft);
            margin-bottom: 26px;
        }

        .field-group {
            margin-bottom: 22px;
        }

        .field-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: var(--text-soft);
            margin-bottom: 6px;
        }

        select,
        input[type="number"] {
            width: 100%;
            padding: 12px 16px;
            border-radius: 999px;
            border: 1px solid #d0ddff;
            background: var(--input-bg);
            font-size: 14px;
            outline: none;
        }

        select:focus,
        input[type="number"]:focus {
            border-color: var(--accent);
            background: #fff;
            box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.15);
        }

        .btn-primary {
            border-radius: 999px;
            padding: 11px 26px;
            border: none;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #fff;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 14px 32px rgba(37, 99, 235, 0.45);
        }

        .summary-card {
            margin-top: 8px;
            padding: 20px;
            border: 1px solid var(--card-border);
            background: #ffffffcc;
            border-radius: 22px;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
            display: none;
        }

        .summary-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 12px;
            color: var(--accent-strong);
        }

        .summary-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
            font-size: 14px;
        }

        .link-back {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--accent-strong);
            text-decoration: none;
            font-size: 14px;
        }
        .status-error {
    background: var(--error-bg);
    color: var(--error-text);
    padding: 10px 12px;
    border-radius: 12px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 8px;
}
    </style>
</head>

<body>
<div class="page">

    <div class="title-wrap">
        <div class="title-icon"><i class="fa-solid fa-money-check-dollar"></i></div>
        <h1>Pago con PSE</h1>
    </div>

    <div class="card">
        <form method="post">
            <div class="helper-text">Cliente actual: <strong>#{{ customer_id }}</strong></div>

            <div class="field-group">
                <label>Cuenta origen</label>
                <select name="account_id" id="accountSelect" required>
                    <option value="">Seleccione una cuenta</option>
                    {% for acc in accounts %}
                    <option value="{{ acc.id }}" data-type="{{ acc.type }}" data-balance="{{ acc.balance }}">
                        #{{ acc.id }} · {{ acc.type }} · ${{ "%.2f"|format(acc.balance) }}
                    </option>
                    {% endfor %}
                </select>
            </div>

            <div class="field-group">
                <label>Monto a transferir</label>
                <input type="number" min="1" step="0.01" name="amount" id="amountInput" required>
                    <div id="balanceError" class="status-error" style="display:none; margin-top:8px;">
        <i class="fa-solid fa-circle-exclamation"></i>
        Saldo insuficiente para realizar este pago.
    </div>
            </div>

            <input type="hidden" name="customer_id" value="{{ customer_id }}">

            <!-- Resumen dinámico -->
            <div class="summary-card" id="summaryCard">
                <div class="summary-title"><i class="fa-solid fa-receipt"></i> Resumen del pago</div>

                <div class="summary-row"><span>Cuenta origen:</span> <strong id="sumAccount"></strong></div>
                <div class="summary-row"><span>Tipo de cuenta:</span> <strong id="sumType"></strong></div>
                <div class="summary-row"><span>Saldo disponible:</span> <strong id="sumBalance"></strong></div>
                <div class="summary-row"><span>Monto a pagar:</span> <strong id="sumAmount"></strong></div>
                <div class="summary-row"><span>Moneda:</span> <strong>COP</strong></div>
            </div>

            <br>

            <button type="submit" class="btn-primary">
                <i class="fa-solid fa-building-columns"></i>
                Pagar con PSE
            </button>
        </form>
    </div>

    <a class="link-back" href="{{ url_for('consultar_saldos', customer_id=customer_id) }}">
        <i class="fa-solid fa-arrow-left"></i> Volver
    </a>

</div>


<script>
    const sel = document.getElementById("accountSelect");
    const amt = document.getElementById("amountInput");
    const card = document.getElementById("summaryCard");
    const balanceError = document.getElementById("balanceError");
    const submitBtn = document.querySelector(".btn-primary");

    function updateSummary() {
        let account = sel.options[sel.selectedIndex];
        let amount = parseFloat(amt.value || "0");
        let hasAccount = !!account.value;

        // Ocultar todo por defecto
        card.style.display = "none";
        balanceError.style.display = "none";
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";

        if (!hasAccount || amount <= 0) {
            return;
        }

        let balance = parseFloat(account.dataset.balance || "0");

        // Actualizar resumen
        document.getElementById("sumAccount").innerText = "#" + account.value;
        document.getElementById("sumType").innerText = account.dataset.type;
        document.getElementById("sumBalance").innerText = "$" + balance.toFixed(2);
        document.getElementById("sumAmount").innerText = "$" + amount.toFixed(2);
        card.style.display = "block";

    
        if (amount > balance) {
            balanceError.style.display = "flex";
            submitBtn.disabled = true;
            submitBtn.style.opacity = "0.6";
        }
    }

    sel.addEventListener("change", updateSummary);
    amt.addEventListener("input", updateSummary);
</script>

</body>
</html>
"""
template_pse_result = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Resultado pago PSE</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 2rem;
        }
        .card {
            max-width: 500px;
            margin: 0 auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .status-success {
            color: #0a8f3a;
            font-weight: bold;
            font-size: 1.4rem;
        }
        .status-failure {
            color: #c62828;
            font-weight: bold;
            font-size: 1.4rem;
        }
        .btn {
            display: inline-block;
            margin-top: 1.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 4px;
            border: none;
            background-color: #1976d2;
            color: #fff;
            text-decoration: none;
        }
    </style>
</head>
<body>

<div class="card">
    {% if status == "success" %}
        <p class="status-success">✅ Pago aprobado por PSE</p>
        <p>Tu pago se ha procesado correctamente.</p>
    {% elif status == "failure" %}
        <p class="status-failure">❌ Pago rechazado por PSE</p>
        <p>No fue posible procesar el pago. Intenta nuevamente o usa otro medio de pago.</p>
    {% else %}
        <p class="status-failure">⚠ Resultado desconocido</p>
        <p>No se recibió un estado válido desde PSE.</p>
    {% endif %}

    {% if amount is not none and account_id %}
        <p>Cuenta origen: <strong>#{{ account_id }}</strong></p>
        <p>Valor: <strong>${{ "%.2f"|format(amount) }}</strong></p>
    {% endif %}

    <a href="{{ url_for('pse') }}" class="btn">Volver a pagos PSE</a>
    <br><br>
    <a href="{{ url_for('saldos') }}">Volver a saldos</a>
</div>

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
                    session["customer_id"] = customer_id
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
    customer_id = request.values.get("customer_id") or ""
    error = None
    message = None
    origin_account = None
    destination_account = None
    amount = None
    accounts = []

    # Obtener cuentas del cliente si customer_id existe
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

    # Procesar formulario de transferencia
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        origin_account = request.form.get("origin_account")
        destination_account = request.form.get("destination_account")
        amount = request.form.get("amount")

        if not (customer_id and origin_account and destination_account and amount):
            error = "Todos los campos son obligatorios."
        else:
            try:
                data = {
                    "from_account_id": int(origin_account),
                    "to_account_id": int(destination_account),
                    "amount": float(amount),
                }

                resp = requests.post(
                    f"{FASTAPI_BASE_URL}/customers/{customer_id}/transfer",
                    json=data,  # ⬅️ se envía como JSON en el body
                    headers={"Authorization": f"Bearer {session['token']}"},
                    timeout=5,
                )

                if resp.status_code == 200:
                    message = "Transferencia realizada con éxito."
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
        origin_account=origin_account,
        destination_account=destination_account,
        amount=amount,
        error=error,
        message=message,
        url_for=url_for,
    )

@app.route("/pse", methods=["GET", "POST"])
def pse():
    # Usuario no autenticado → mandar al login
    if "token" not in session:
        return redirect(url_for("login"))

    # Debe haber un cliente seleccionado previamente
    customer_id = session.get("customer_id")
    if not customer_id:
        flash("Primero selecciona un cliente en la pantalla de saldos.")
        # Ajusta "saldos" por el nombre real de tu ruta de consulta de saldos
        return redirect(url_for("saldos"))

    token = session["token"]

    accounts = []
    payment_url = None
    error = None
    message = None

    # ==========================
    # 1. Traer cuentas del cliente
    # ==========================
    try:
        resp = requests.get(
            f"{FASTAPI_BASE_URL}/customers/{customer_id}/accounts",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if resp.status_code == 200:
            accounts = resp.json()
        else:
            try:
                detail = resp.json().get("detail", "")
            except Exception:
                detail = ""
            error = f"No se pudieron cargar las cuentas. (status {resp.status_code}) {detail}"
    except Exception as e:
        error = f"Error consultando cuentas: {e}"

    # ==========================
    # 2. Procesar formulario PSE
    # ==========================
    if request.method == "POST" and not error:
        account_id = (request.form.get("account_id") or "").strip()
        amount_str = (request.form.get("amount") or "").strip()

        if not account_id or not amount_str:
            error = "Todos los campos son obligatorios."
        else:
            try:
                amount_f = float(amount_str)
                if amount_f <= 0:
                    raise ValueError("amount <= 0")
            except ValueError:
                error = "El valor a transferir debe ser un número mayor que cero."
            else:
                # Buscar la cuenta seleccionada en la lista de cuentas
                selected = next(
                    (a for a in accounts if str(a.get("id")) == str(account_id)),
                    None
                )

                if not selected:
                    error = "La cuenta seleccionada no existe."
                else:
                    balance = float(selected.get("balance", 0))

                    # Validación de saldo insuficiente
                    if amount_f > balance:
                        error = (
                            f"Saldo insuficiente en la cuenta #{selected.get('id')}. "
                            f"Saldo disponible: {balance:.2f}"
                        )
                    else:
                        # ==========================
                        # 3. Crear orden PSE en FastAPI
                        # ==========================
                        return_url_success = url_for(
                            "pse_result",
                            status="success",
                            amount=amount_f,
                            account_id=account_id,
                            _external=True,
                        )
                        return_url_failure = url_for(
                            "pse_result",
                            status="failure",
                            amount=amount_f,
                            account_id=account_id,
                            _external=True,
                        )
                        data = {
                            "customer_id": int(customer_id),
                            "account_id": int(account_id),
                            "amount": amount_f,
                            "currency": "COP",
                            "return_url_success": return_url_success,
                            "return_url_failure": return_url_failure,
                        }

                        try:
                            resp = requests.post(
                                f"{FASTAPI_BASE_URL}/payments",
                                json=data,
                                headers={"Authorization": f"Bearer {token}"},
                                timeout=5,
                            )
                        except Exception as e:
                            error = f"Error creando pago PSE: {e}"
                        else:
                            if resp.status_code == 200:
                                tx = resp.json()
                                internal_order_id = tx.get("internal_order_id")
                                message = "Orden PSE creada correctamente."

                                # Si el servicio devuelve una URL de pago simulada, redirigimos
                                if internal_order_id:
                                    host = request.host.split(":")[0]
                                    payment_url = f"http://{host}:8000/pse-gateway/{internal_order_id}"
                                    return redirect(payment_url)
                            else:
                                try:
                                    detail = resp.json().get("detail", "")
                                except Exception:
                                    detail = ""
                                error = (
                                    f"Error creando pago PSE: status {resp.status_code}. "
                                    f"{detail}"
                                )

    return render_template_string(
        template_pse,         
        accounts=accounts,
        customer_id=customer_id,
        error=error,
        message=message,
        payment_url=payment_url,
    )


@app.route("/pse/resultado")
def pse_result():
    status = (request.args.get("status") or "").lower()
    amount = request.args.get("amount")
    account_id = request.args.get("account_id")
    amount_value = None
    try:
        if amount is not None:
            amount_value = float(amount)
    except ValueError:
        amount_value = None

    return render_template_string(
        template_pse_result,
        status=status,
        amount=amount_value,
        account_id=account_id,
    )
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
