from flask import Flask, jsonify

from config import Config
import db as db_module

from routes.auth_routes import auth_bp
from routes.profile_routes import profile_bp
from routes.daily_log_routes import daily_log_bp
from routes.chat_routes import chat_bp
from routes.dashboard_routes import dashboard_bp
from routes.reminder_routes import reminder_bp
from routes.report_routes import report_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Minimal hand-rolled CORS (avoids requiring the flask-cors package).
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = app.config.get("CORS_ORIGINS", "*")
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    @app.route("/api/<path:_path>", methods=["OPTIONS"])
    def cors_preflight(_path):
        return "", 204

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(daily_log_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(report_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok", "service": "AarogyaAI backend"})

    with app.app_context():
        db_module.init_db()

    return app


if __name__ == "__main__":
    create_app().run(debug=True, port=5000)
