from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import db
from utils.auth_utils import generate_token

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"error": "name, email, and password are required"}), 400

    existing = db.query_one("SELECT user_id FROM users WHERE email = ?", (email,))
    if existing:
        return jsonify({"error": "An account with this email already exists"}), 409

    password_hash = generate_password_hash(password)

    user_id, _ = db.execute(
        """INSERT INTO users
           (name, email, password_hash, age, height_cm, weight_kg,
            activity_level, wellness_goal, diet_preference,
            water_goal_ml, sleep_goal_hrs)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            name, email, password_hash,
            data.get("age"), data.get("height_cm"), data.get("weight_kg"),
            data.get("activity_level"), data.get("wellness_goal"),
            data.get("diet_preference"),
            data.get("water_goal_ml", 2000), data.get("sleep_goal_hrs", 8),
        ),
    )

    token = generate_token(user_id)
    return jsonify({"token": token, "user_id": user_id, "name": name}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = db.query_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401

    token = generate_token(user["user_id"])
    return jsonify({"token": token, "user_id": user["user_id"], "name": user["name"]})
