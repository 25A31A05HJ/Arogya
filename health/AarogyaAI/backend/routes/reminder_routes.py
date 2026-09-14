from flask import Blueprint, request, jsonify

import db
from utils.auth_utils import token_required

reminder_bp = Blueprint("reminder", __name__, url_prefix="/api/reminders")


@reminder_bp.route("", methods=["GET"])
@token_required
def list_reminders():
    rows = db.query_all(
        "SELECT * FROM reminders WHERE user_id = ? ORDER BY remind_time ASC",
        (request.user_id,),
    )
    return jsonify(rows)


@reminder_bp.route("", methods=["POST"])
@token_required
def create_reminder():
    data = request.get_json(force=True) or {}
    category = data.get("category")
    title = data.get("title")
    remind_time = data.get("remind_time")
    if not category or not title or not remind_time:
        return jsonify({"error": "category, title, and remind_time are required"}), 400

    reminder_id, _ = db.execute(
        "INSERT INTO reminders (user_id, category, title, remind_time) VALUES (?, ?, ?, ?)",
        (request.user_id, category, title, remind_time),
    )
    row = db.query_one("SELECT * FROM reminders WHERE reminder_id = ?", (reminder_id,))
    return jsonify(row), 201


@reminder_bp.route("/<int:reminder_id>", methods=["PUT"])
@token_required
def update_reminder(reminder_id):
    data = request.get_json(force=True) or {}
    is_active = data.get("is_active")
    if is_active is None:
        return jsonify({"error": "is_active is required"}), 400

    _, rowcount = db.execute(
        "UPDATE reminders SET is_active = ? WHERE reminder_id = ? AND user_id = ?",
        (int(is_active), reminder_id, request.user_id),
    )
    if rowcount == 0:
        return jsonify({"error": "Reminder not found"}), 404
    return jsonify({"message": "Reminder updated"})


@reminder_bp.route("/<int:reminder_id>", methods=["DELETE"])
@token_required
def delete_reminder(reminder_id):
    _, rowcount = db.execute(
        "DELETE FROM reminders WHERE reminder_id = ? AND user_id = ?",
        (reminder_id, request.user_id),
    )
    if rowcount == 0:
        return jsonify({"error": "Reminder not found"}), 404
    return jsonify({"message": "Reminder deleted"})
