from flask import Blueprint, jsonify, request
from ..services import room_service

# 修正路径前缀
test_bp = Blueprint("test", __name__, url_prefix="/test")

@test_bp.post("/initRoom")
def init_room_temperature():
    """
    测试专用接口：强制初始化房间温度
    用于在执行 Excel 测试用例前，将房间设置为指定的初始温度
    """
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    temperature = payload.get("temperature")
    
    if room_id is None or temperature is None:
        return jsonify({"error": "Missing roomId or temperature"}), 400

    try:
        room = room_service.getRoomById(room_id)
        if room:
            room.current_temp = float(temperature)
            # 设置默认温度也为这个，防止关机后回温到错误的默认值
            room.default_temp = float(temperature)
            # 清除上次更新时间，防止自动跳变
            room.last_temp_update = None 
            room_service.updateRoom(room)
            return jsonify({"message": f"Room {room_id} reset to {temperature}°C"})
        return jsonify({"error": "Room not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400