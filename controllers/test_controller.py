from flask import Blueprint, jsonify, request
from ..services import room_service

test_bp = Blueprint("test", __name__, url_prefix="/test")


@test_bp.post("/initRoom")
def init_room_state():
    """
    测试专用接口：强制初始化房间状态
    1. 重置当前温度和默认温度
    2. 设置房费单价 (daily_rate)
    
    参数：
    - roomId: 房间ID
    - temperature: 当前温度（如果提供，同时设置 default_temp）
    - defaultTemp: 默认温度（可选，如果不提供则使用 temperature）
    - dailyRate: 房费单价
    """
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    temperature = payload.get("temperature")
    default_temp = payload.get("defaultTemp")  # === 新增：支持单独设置 default_temp ===
    daily_rate = payload.get("dailyRate")

    if room_id is None:
        return jsonify({"error": "Missing roomId"}), 400

    try:
        room = room_service.getRoomById(room_id)
        if room:
            # === 关键修复：使用原子更新，确保 default_temp 被正确保存 ===
            from ..extensions import db
            from ..models import Room
            
            update_dict = {}
            
            # 1. 设置温度
            if temperature is not None:
                temp_val = float(temperature)
                update_dict["current_temp"] = temp_val
                update_dict["last_temp_update"] = None  # 清除上次更新时间，防止自动跳变
                room.current_temp = temp_val
                room.last_temp_update = None
                
                # === 关键修复：如果提供了 defaultTemp，使用它；否则使用 temperature ===
                if default_temp is not None:
                    default_val = float(default_temp)
                    update_dict["default_temp"] = default_val
                    room.default_temp = default_val
                else:
                    # 如果没有提供 defaultTemp，使用 temperature 作为默认值
                    update_dict["default_temp"] = temp_val
                    room.default_temp = temp_val

            # 2. 设置房费
            if daily_rate is not None:
                update_dict["daily_rate"] = float(daily_rate)
                room.daily_rate = float(daily_rate)

            # 3. 使用原子更新，确保 default_temp 被正确保存
            if update_dict:
                db.session.query(Room).filter(Room.id == room_id).update(update_dict)
                db.session.commit()

            return jsonify({
                "message": f"Room {room_id} reset",
                "temp": room.current_temp,
                "default_temp": room.default_temp,
                "rate": room.daily_rate
            })

        return jsonify({"error": "Room not found"}), 404
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400