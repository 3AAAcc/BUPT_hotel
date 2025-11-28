from flask import Blueprint, jsonify
from ..services import scheduler

# 修正路径前缀
monitor_bp = Blueprint("monitor", __name__, url_prefix="/monitor")

@monitor_bp.get("/status")
def get_monitor_data():
    try:
        # 获取调度器队列状态
        status = scheduler.getScheduleStatus()
        return jsonify(status)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400