from flask import Blueprint, jsonify

from ..services import ac_schedule_service, ac_service, room_service

monitor_bp = Blueprint("monitor", __name__, url_prefix="/api/monitor")


@monitor_bp.get("/roomstatus")
def getRoomStatus():
    rooms = room_service.getAllRooms()
    result = []
    for room in rooms:
        ac = ac_service.getACByRoomId(room.id)
        status = {
            "roomId": room.id,
            "currentTemp": room.current_temp,
            "defaultTemp": room.default_temp,
            "targetTemp": ac.target_temp if ac else None,
            "fanSpeed": ac.fan_speed if ac else None,
            "mode": ac.ac_mode if ac else None,
            "acOn": ac.ac_on if ac else False,
        }
        result.append(status)
    return jsonify(result)


@monitor_bp.get("/queuestatus")
def getQueueStatus():
    serving = [
        {
            "roomId": req.roomId,
            "fanSpeed": req.fanSpeed,
            "servingTime": req.servingTime.isoformat() if req.servingTime else None,
        }
        for req in ac_schedule_service.getServingQueue()
    ]
    waiting = [
        {
            "roomId": req.roomId,
            "fanSpeed": req.fanSpeed,
            "waitingTime": req.waitingTime.isoformat() if req.waitingTime else None,
        }
        for req in ac_schedule_service.getWaitingQueue()
    ]
    return jsonify({"servingQueue": serving, "waitingQueue": waiting})

