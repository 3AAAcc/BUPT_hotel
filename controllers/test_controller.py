from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from ..services import room_service
from ..utils.time_master import clock

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
                # === 关键修复：如果房间已开机，需要同时重置 ac_session_start，避免时间计算错误 ===
                # 如果房间未开机，只清除 last_temp_update 即可
                if room.ac_on:
                    # 房间已开机，需要重置时间基准，使用当前逻辑时间
                    now = clock.now()
                    update_dict["last_temp_update"] = now
                    update_dict["ac_session_start"] = now
                    room.last_temp_update = now
                    room.ac_session_start = now
                else:
                    # 房间未开机，只清除 last_temp_update
                    update_dict["last_temp_update"] = None
                    room.last_temp_update = None
                room.current_temp = temp_val
                
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

            # 3. 清理队列相关状态（如果房间未开机，确保队列状态被清理）
            # 这样可以避免之前测试留下的脏数据影响当前状态
            if not room.ac_on:
                update_dict["serving_start_time"] = None
                update_dict["waiting_start_time"] = None
                update_dict["billing_start_temp"] = None
                update_dict["cooling_paused"] = False
                update_dict["pause_start_temp"] = None
                update_dict["ac_session_start"] = None  # 清理空调会话开始时间，避免时间计算错误
                # 同时从内存队列中移除（如果存在）- 使用锁保护
                from ..services import scheduler
                with scheduler._lock:
                    scheduler._remove_request(scheduler.serving_queue, room_id)
                    scheduler._remove_request(scheduler.waiting_queue, room_id)

            # 4. 使用原子更新，确保 default_temp 被正确保存
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


@test_bp.route('/time/set_speed', methods=['POST'])
def set_speed():
    """设置时间流速"""
    data = request.json or {}
    speed = data.get('speed', 1.0)
    clock.set_speed(float(speed))
    return jsonify({"msg": "ok", "current_logical_time": clock.now().isoformat()})


@test_bp.route('/time/jump', methods=['POST'])
def jump_time():
    """时间穿越（例如直接跳到明天）"""
    data = request.json or {}
    minutes = data.get('add_minutes', 0)
    
    new_time = clock.now() + timedelta(minutes=minutes)
    clock.jump_to(new_time)
    
    return jsonify({"msg": "ok", "new_time": new_time.isoformat()})


@test_bp.route('/time/status', methods=['GET'])
def get_time_status():
    """获取当前双重时间状态"""
    return jsonify({
        "real_time": datetime.utcnow().isoformat(),
        "logical_time": clock.now().isoformat(),
        "speed": clock.speed,
        "is_paused": clock.paused
    })


@test_bp.route('/time/pause', methods=['POST'])
def pause_time():
    """暂停时间"""
    clock.pause()
    return jsonify({"msg": "ok", "is_paused": clock.paused})


@test_bp.route('/time/resume', methods=['POST'])
def resume_time():
    """恢复时间"""
    clock.resume()
    return jsonify({"msg": "ok", "is_paused": clock.paused})