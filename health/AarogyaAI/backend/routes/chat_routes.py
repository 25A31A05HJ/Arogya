import json
from datetime import date

from flask import Blueprint, request, jsonify, current_app

import db
from utils.auth_utils import token_required
from ai_engine.chat_engine import handle_chat_message

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")


@chat_bp.route("", methods=["POST"])
@token_required
def chat():
    data = request.get_json(force=True) or {}
    message = (data.get("message") or "").strip()
    if not message:
        return jsonify({"error": "message is required"}), 400

    db.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (?, 'user', ?)",
        (request.user_id, message),
    )

    history = db.query_all(
        "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
        (request.user_id,),
    )
    history.reverse()

    today_log = db.query_one(
        "SELECT score_breakdown FROM daily_logs WHERE user_id = ? AND log_date = ?",
        (request.user_id, date.today().isoformat()),
    )
    breakdown = json.loads(today_log["score_breakdown"]) if today_log and today_log.get("score_breakdown") else None

    user = db.query_one("SELECT wellness_goal FROM users WHERE user_id = ?", (request.user_id,))
    wellness_goal = user["wellness_goal"] if user else ""

    app_config = {
        "LLM_API_KEY": current_app.config["LLM_API_KEY"],
        "LLM_API_URL": current_app.config["LLM_API_URL"],
        "LLM_MODEL": current_app.config["LLM_MODEL"],
    }

    result = handle_chat_message(message, history, app_config, breakdown, wellness_goal)

    db.execute(
        "INSERT INTO chat_history (user_id, sender, message, is_red_flag) VALUES (?, 'ai', ?, ?)",
        (request.user_id, result["reply"], int(result["is_red_flag"])),
    )

    return jsonify(result)


@chat_bp.route("/history", methods=["GET"])
@token_required
def chat_history():
    limit = int(request.args.get("limit", 50))
    rows = db.query_all(
        """SELECT sender, message, is_red_flag, created_at FROM chat_history
           WHERE user_id = ? ORDER BY created_at ASC LIMIT ?""",
        (request.user_id, limit),
    )
    return jsonify(rows)
