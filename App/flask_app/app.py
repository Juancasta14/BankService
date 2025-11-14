from flask import Flask, render_template_string, request
import requests
import os

app = Flask(__name__)

# URL base del servicio FastAPI (inyectada por docker-compose o por defecto localhost)
FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://fastapi:8000")

HTML_TEMPLATE = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Consulta de Saldos</title>
</head>
<body>
    <h1>Consulta de Saldos del Cliente</h1>

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


@app.route("/", methods=["GET"])
def index():
    customer_id = request.args.get("customer_id", type=int)
    error = None
    summary = None

    # Solo llamamos a FastAPI si el usuario puso un ID
    if customer_id is not None:
        try:
            resp = requests.get(f"{FASTAPI_BASE_URL}/customers/{customer_id}/summary", timeout=5)
            if resp.status_code == 200:
                summary = resp.json()
            else:
                # Tratamos de leer el detalle si viene como JSON, si no, mensaje genérico
                try:
                    error = resp.json().get("detail", "Error consultando el servicio")
                except Exception:
                    error = f"Error consultando el servicio (status {resp.status_code})"
        except Exception as e:
            error = f"No se pudo conectar con el servicio: {e}"

    return render_template_string(
        HTML_TEMPLATE,
        customer_id=customer_id,
        summary=summary,
        error=error,
    )


if __name__ == "__main__":
    # ¡IMPORTANTE! host=0.0.0.0 para que responda fuera del contenedor
    app.run(host="0.0.0.0", port=5000)
