from flask import Blueprint, jsonify, request
from ..services import report_service

# 修正路径前缀
report_bp = Blueprint("report", __name__, url_prefix="/report")

@report_bp.get("/room")
def get_room_report():
    room_id = request.args.get("roomId", type=int)
    try:
        report = report_service.generateRoomReport(room_id)
        # report_service 返回的可能已经是 list[dict]，直接 jsonify
        return jsonify(report)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@report_bp.get("/daily")
def get_daily_report():
    date_str = request.args.get("date")  # YYYY-MM-DD
    try:
        report = report_service.generateDailyReport(date_str)
        return jsonify(report)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@report_bp.get("/weekly")
def get_weekly_report():
    start_date = request.args.get("startDate")
    try:
        report = report_service.generateWeeklyReport(start_date)
        return jsonify(report)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400