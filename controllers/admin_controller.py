from flask import Blueprint, jsonify, request, current_app
from ..services import maintenance_service, scheduler, room_service
from ..extensions import db
from ..models import AccommodationFeeBill, Customer, DetailRecord, Room, ACConfig
from ..database import (
    ensure_bill_detail_update_time_column,
    ensure_room_billing_start_temp_column,
    ensure_room_daily_rate_column,
    ensure_room_last_temp_update_column,
    execute_schema_sql,
    seed_default_ac_config,
)

# 修正前缀
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.get("/rooms/status")
def get_all_rooms_status():
    """获取所有房间的详细状态（上帝视角）"""
    try:
        # 注意：温度更新由后台任务自动处理，这里不再手动触发
        
        # 1. 获取所有房间
        rooms = room_service.getAllRooms()
        
        # 3. 逐个调用 RequestState 获取详细信息（含费用、队列状态）
        data = []
        for room in rooms:
            # 复用 scheduler 里写好的逻辑，保证数据字段一致
            state = scheduler.RequestState(room.id)
            data.append(state)
            
        return jsonify(data)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

# -------------------------------------------------------
# 以下是管理员控制接口 (复用 AC 接口逻辑，但通过 admin 路由透传)
# -------------------------------------------------------

@admin_bp.post("/control/power")
def admin_power():
    payload = request.get_json() or {}
    room_id = payload.get("roomId")
    action = payload.get("action") # 'on' or 'off'
    try:
        if action == 'on':
            from ..services import ac
            # 获取房间当前温度（如果为 None 则让 PowerOn 使用房间的现有温度）
            room = room_service.getRoomById(room_id)
            current_temp = room.current_temp if room else None
            msg = ac.PowerOn(room_id, current_temp)
        else:
            msg = scheduler.PowerOff(room_id)
        return jsonify({"message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.post("/control/temp")
def admin_temp():
    payload = request.get_json() or {}
    try:
        from ..services import ac
        msg = ac.ChangeTemp(payload.get("roomId"), payload.get("targetTemp"))
        return jsonify({"message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.post("/control/speed")
def admin_speed():
    payload = request.get_json() or {}
    try:
        from ..services import ac
        msg = ac.ChangeSpeed(payload.get("roomId"), payload.get("fanSpeed"))
        return jsonify({"message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.post("/control/mode")
def admin_mode():
    payload = request.get_json() or {}
    try:
        # 调用 Scheduler 的 ChangeMode 方法 (会重置目标温度)
        msg = scheduler.ChangeMode(payload.get("roomId"), payload.get("mode"))
        return jsonify({"message": msg})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@admin_bp.post("/reset-database")
def reset_database():
    """重置数据库并重新初始化所有数据（调试用）"""
    try:
        # 1. 清空调度器队列
        scheduler.serving_queue.clear()
        scheduler.waiting_queue.clear()
        
        # 2. 删除所有表数据
        db.session.query(DetailRecord).delete()
        db.session.query(AccommodationFeeBill).delete()
        db.session.query(Customer).delete()
        db.session.query(Room).delete()
        db.session.query(ACConfig).delete()
        db.session.commit()
        
        # 3. 删除所有表并重新创建
        db.drop_all()
        db.create_all()
        
        # 4. 执行 schema.sql
        execute_schema_sql()
        
        # 5. 确保所有必要的列都存在（包括新添加的字段）
        ensure_bill_detail_update_time_column()
        ensure_room_last_temp_update_column()
        ensure_room_daily_rate_column()
        ensure_room_billing_start_temp_column()
        
        # 6. 初始化 AC 配置
        seed_default_ac_config()
        
        # 7. 初始化房间数据
        room_service.ensureRoomsInitialized(
            total_count=current_app.config["HOTEL_ROOM_COUNT"],
            default_temp=current_app.config["HOTEL_DEFAULT_TEMP"],
        )
        
        return jsonify({"message": "数据库已重置并重新初始化"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500