"""LinkedIn Profile Analyzer — Flask application."""

from flask import Flask, jsonify, render_template, request

from analyzer import analyze_profile
from gmail_service import send_report_email

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    data = request.get_json(silent=True) or {}

    try:
        result = analyze_profile(
            name=data.get("name", ""),
            headline=data.get("headline", ""),
            about=data.get("about", ""),
            skills=data.get("skills", ""),
        )
        return jsonify(result)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Analysis failed: {exc}"}), 500


@app.route("/api/send-report", methods=["POST"])
def api_send_report():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    report = data.get("report")

    if not email:
        return jsonify({"error": "Recipient email is required."}), 400
    if not report:
        return jsonify({"error": "Report data is required. Analyze a profile first."}), 400

    try:
        result = send_report_email(email, report)
        return jsonify(result)
    except RuntimeError as exc:
        return jsonify({"error": str(exc)}), 503
    except Exception as exc:
        return jsonify({"error": f"Failed to send email: {exc}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
