from flask import Blueprint, jsonify, request
from ..services import room_service

test_bp = Blueprint("test", __name__, url_prefix="/test")


@test_bp.post("/initRoom")
def init_room_state():
    """
    测试专用接口：强制初始化房间状态
    1. 重置当前温度和默认温度
    2. 设置房费单价 (daily_rate)
    """
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    temperature = payload.get("temperature")
    daily_rate = payload.get("dailyRate")  # 新增参数

    if room_id is None:
        return jsonify({"error": "Missing roomId"}), 400

    try:
        room = room_service.getRoomById(room_id)
        if room:
            # 1. 设置温度
            if temperature is not None:
                room.current_temp = float(temperature)
                room.default_temp = float(temperature)
                # 清除上次更新时间，防止自动跳变
                room.last_temp_update = None

                # 2. 设置房费 (核心修复)
            if daily_rate is not None:
                room.daily_rate = float(daily_rate)

            # 3. 确保状态是关机 (可选，防止测试开始前就是开着的)
            # room.ac_on = False

            room_service.updateRoom(room)

            return jsonify({
                "message": f"Room {room_id} reset",
                "temp": room.current_temp,
                "rate": room.daily_rate
            })

        return jsonify({"error": "Room not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400