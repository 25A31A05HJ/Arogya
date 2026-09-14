from datetime import date, timedelta

from flask import Blueprint, request, jsonify

import db
from utils.auth_utils import token_required
from ai_engine.weekly_report import build_weekly_report

report_bp = Blueprint("report", __name__, url_prefix="/api/reports")


@report_bp.route("/weekly", methods=["GET"])
@token_required
def weekly_report():
    start_date = (date.today() - timedelta(days=6)).isoformat()
    logs = db.query_all(
        """SELECT log_date, sleep_hours, exercise_minutes, water_ml,
                  stress_level, wellness_score
           FROM daily_logs
           WHERE user_id = ? AND log_date >= ?
           ORDER BY log_date ASC""",
        (request.user_id, start_date),
    )
    report = build_weekly_report(logs)
    return jsonify(report)
