from flask import Blueprint, jsonify, request
from ..services import front_desk, room_service, scheduler

# 修正路径前缀
hotel_bp = Blueprint("hotel", __name__, url_prefix="/hotel")

@hotel_bp.route("/rooms", methods=["GET"])
def get_all_rooms():
    try:
        # === 核心修复：前台大厅查询时，强制刷新全酒店温度 ===
        scheduler.simulateTemperatureUpdate()
        
        # 获取所有房间对象
        rooms = room_service.getAllRooms()
        return jsonify([room.to_dict() for room in rooms]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@hotel_bp.get("/available")
def getAvailableRooms():
    rooms = front_desk.Check_RoomState(None)
    ids = [room.id for room in rooms if room.status == "AVAILABLE"]
    return jsonify(ids)

@hotel_bp.get("/rooms/available")
def getAvailableRoomDetails():
    rooms = [room.to_dict() for room in front_desk.getAvailableRooms()]
    return jsonify(rooms)

@hotel_bp.post("/checkin")
def checkIn():
    payload = request.get_json() or {}
    try:
        message = front_desk.checkIn(payload)
        return jsonify({"message": message})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@hotel_bp.post("/checkout/<int:roomId>")
def checkout(roomId: int):
    try:
        response = front_desk.checkOut(roomId)
        return jsonify(response.to_dict())
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400