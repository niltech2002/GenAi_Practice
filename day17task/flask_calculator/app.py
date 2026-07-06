"""
Flask Calculator Application
=============================
A simple web-based calculator with a Flask backend and a JavaScript frontend.

Routes:
    GET  /           - Serves the calculator HTML page.
    POST /calculate  - Accepts two numbers and an operator, returns the result as JSON.

Usage:
    python app.py
    Then open http://127.0.0.1:5000 in a browser.
"""

import os
import math
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.after_request
def set_security_headers(response):
    """Attach security headers to every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self'; script-src 'self'"
    )
    return response


@app.route("/")
def index():
    """Render the main calculator page."""
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    """
    Perform an arithmetic calculation.

    Expects a JSON body:
        {
            "num1": <number>,
            "num2": <number>,
            "operator": "+" | "-" | "*" | "/"
        }

    Returns:
        200 { "result": <number> }         on success
        400 { "error": <message> }         on invalid input or division by zero
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Invalid or missing JSON body"}), 400
    num1 = data.get("num1")
    num2 = data.get("num2")
    operator = data.get("operator")

    try:
        num1 = float(num1)
        num2 = float(num2)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid numbers provided"}), 400

    if operator == "+":
        result = num1 + num2
    elif operator == "-":
        result = num1 - num2
    elif operator == "*":
        result = num1 * num2
    elif operator == "/":
        if num2 == 0:
            return jsonify({"error": "Division by zero is not allowed"}), 400
        result = num1 / num2
    else:
        return jsonify({"error": "Invalid operator"}), 400

    result = int(result) if result == int(result) else round(result, 10)

    if math.isinf(result) or math.isnan(result):
        return jsonify({"error": "Result is out of range"}), 400

    return jsonify({"result": result})


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
