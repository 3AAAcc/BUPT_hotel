from flask import Blueprint, jsonify, request

from ..services import report_service

report_bp = Blueprint("reports", __name__, url_prefix="/api/reports")


@report_bp.get("/overview")
def get_overview():
    start = request.args.get("start")
    end = request.args.get("end")
    data = report_service.get_overview(start, end)
    return jsonify(data)


@report_bp.get("/ac-usage")
def get_ac_usage():
    start = request.args.get("start")
    end = request.args.get("end")
    data = report_service.get_ac_usage_summary(start, end)
    return jsonify(data)


@report_bp.get("/daily-revenue")
def get_daily_revenue():
    days = request.args.get("days", default=7, type=int)
    try:
        data = report_service.get_daily_revenue(days)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(data)

