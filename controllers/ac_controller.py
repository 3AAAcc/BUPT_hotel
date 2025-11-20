from flask import Blueprint, jsonify, request

from ..services import ac_schedule_service

ac_bp = Blueprint("ac", __name__, url_prefix="/api/ac")


@ac_bp.post("/room/<int:roomId>/start")
def PowerOn(roomId: int):
    current_temp = request.args.get("currentTemp", type=float)
    try:
        message = ac_schedule_service.startAC(roomId, current_temp)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.post("/room/<int:roomId>/stop")
def PowerOff(roomId: int):
    try:
        message = ac_schedule_service.stopAC(roomId)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.put("/room/<int:roomId>/temp")
def ChangeTemp(roomId: int):
    target_temp = request.args.get("targetTemp", type=float)
    if target_temp is None:
        return jsonify({"error": "targetTemp 不能为空"}), 400
    try:
        message = ac_schedule_service.changeTemp(roomId, target_temp)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.put("/room/<int:roomId>/speed")
def ChangeSpeed(roomId: int):
    fan_speed = request.args.get("fanSpeed")
    if not fan_speed:
        return jsonify({"error": "fanSpeed 不能为空"}), 400
    try:
        message = ac_schedule_service.changeFanSpeed(roomId, fan_speed)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.get("/room/<int:roomId>/detail")
def getRoomACDetail(roomId: int):
    try:
        data = ac_schedule_service.getRoomACAccumulatedData(roomId)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.get("/room/<int:roomId>/status")
def getRoomACStatus(roomId: int):
    try:
        data = ac_schedule_service.getRoomACStatus(roomId)
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400


@ac_bp.get("/schedule/status")
def getScheduleStatus():
    data = ac_schedule_service.getScheduleStatus()
    return jsonify(data)
