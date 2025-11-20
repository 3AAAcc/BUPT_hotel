from flask import Blueprint, jsonify

from ..services import maintenance_service

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.post("/rooms/<int:roomId>/offline")
def take_room_offline(roomId: int):
    try:
        room = maintenance_service.mark_room_offline(roomId)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "房间已标记为维修", "room": room.to_dict()})


@admin_bp.post("/rooms/<int:roomId>/online")
def bring_room_online(roomId: int):
    try:
        room = maintenance_service.mark_room_online(roomId)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "房间已重新可用", "room": room.to_dict()})


@admin_bp.post("/maintenance/force-rotation")
def force_rotation():
    payload = maintenance_service.force_rebalance()
    return jsonify({"message": "调度队列已强制轮转", "schedule": payload})


@admin_bp.post("/maintenance/simulate-temperature")
def simulate_temperature():
    payload = maintenance_service.simulate_temperature()
    return jsonify(payload)

