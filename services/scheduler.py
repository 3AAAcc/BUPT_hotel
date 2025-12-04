from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import current_app
from sqlalchemy import func

from ..models import Room, RoomRequest, DetailRecord
from ..utils.time_master import clock
from .bill_detail_service import BillDetailService
from .room_service import RoomService

# =============================================================================
# 调度器 (Scheduler) - 最终完美版
# 1. 修正费率计算 (单价恒定 1.0)
# 2. PowerOn: 触发房费账单 (按次计费)
# 3. PowerOff: 增加重置风速和目标温度的逻辑
# 4. RequestState: 修正费用汇总逻辑
# =============================================================================

class Scheduler:
    def __init__(self, room_service: RoomService, bill_detail_service: BillDetailService):
        self.room_service = room_service
        self.bill_detail_service = bill_detail_service
        
        self.serving_queue: List[RoomRequest] = []
        self.waiting_queue: List[RoomRequest] = []
        self._lock = threading.Lock()

    # --- 辅助方法 ---

    def _capacity(self) -> int:
        try:
            return max(1, int(current_app.config.get("HOTEL_AC_TOTAL_COUNT", 3)))
        except: return 3

    def _time_slice(self) -> int:
        try:
            return max(1, int(current_app.config.get("HOTEL_TIME_SLICE", 120)))
        except: return 120

    def _get_simulated_duration(self, start_time: datetime, end_time: datetime) -> float:
        if not start_time or not end_time: return 0.0
        return max(0.0, (end_time - start_time).total_seconds())

    def _priority_score(self, request: RoomRequest) -> int:
        mapping = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return mapping.get((request.fanSpeed or "MEDIUM").upper(), 2)

    def _remove_request(self, queue: List[RoomRequest], room_id: int) -> None:
        for i in range(len(queue) - 1, -1, -1):
            if queue[i].roomId == room_id:
                queue.pop(i)

    def _get_rate(self, fan_speed: str) -> float:
        """获取单位温差的费率。当前逻辑下，1度温差=1元，不随风速变化。"""
        return 1.0

    # --- 核心逻辑: 温度更新 ---

    def _updateRoomTemperature(self, room: Room, force_update: bool = False) -> None:
        now = clock.now()
        
        if not room.last_temp_update:
            from ..extensions import db
            room.last_temp_update = now
            db.session.commit()
            return

        sim_minutes = self._get_simulated_duration(room.last_temp_update, now) / 60.0
        if sim_minutes <= 0 and not force_update: return

        current_temp = float(room.current_temp or 25.0)
        target_temp = float(room.target_temp or 25.0)
        default_temp = float(room.default_temp or 25.0)
        fan_speed = (room.fan_speed or "MEDIUM").upper()
        mode = (room.ac_mode or "COOLING").upper()

        is_serving = any(r.roomId == room.id for r in self.serving_queue)
        # 补救措施：如果数据库显示在服务但队列里没有(极端情况)，视为服务中
        if not is_serving and room.serving_start_time and not room.cooling_paused:
            is_serving = True

        new_temp = current_temp
        
        if is_serving:
            # 变温速率: High=1.0, Medium=0.5, Low=0.33
            rate_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 1.0/3.0}
            rate = rate_map.get(fan_speed, 0.5)
            delta = rate * sim_minutes

            if mode == "COOLING":
                if current_temp > target_temp:
                    new_temp = max(target_temp, current_temp - delta)
            else: # HEATING
                if current_temp < target_temp:
                    new_temp = min(target_temp, current_temp + delta)
            
            # 到达目标温度检查
            if abs(new_temp - target_temp) < 0.01:
                new_temp = target_temp
                if not force_update:
                    self._handle_temp_reached(room, new_temp)
        else:
            # 回温速率
            rewarm_rate = 0.5
            delta = rewarm_rate * sim_minutes
            if current_temp < default_temp:
                new_temp = min(default_temp, current_temp + delta)
            elif current_temp > default_temp:
                new_temp = max(default_temp, current_temp - delta)
            
            # 回温唤醒检查
            if room.cooling_paused and not force_update:
                pause_base = room.pause_start_temp if room.pause_start_temp is not None else target_temp
                if abs(new_temp - pause_base) >= 1.0:
                    self._handle_rewarm_wake(room)

        # 持久化
        from ..extensions import db
        try:
            room.current_temp = new_temp
            room.last_temp_update = now
            db.session.query(Room).filter(Room.id == room.id).update({
                "current_temp": new_temp,
                "last_temp_update": now
            })
            db.session.commit()
        except Exception:
            db.session.rollback()

    # --- 核心逻辑: 计费 ---

    def _settle_current_service_period(self, room: Room, end_time: datetime, reason: str) -> None:
        if not room.serving_start_time or room.billing_start_temp is None:
            return

        start_temp = float(room.billing_start_temp)
        end_temp = float(room.current_temp)
        mode = room.ac_mode or "COOLING"
        
        temp_diff = 0.0
        if mode == "COOLING":
            if end_temp < start_temp: temp_diff = start_temp - end_temp
        else:
            if end_temp > start_temp: temp_diff = end_temp - start_temp

        if temp_diff < 0.001: return

        rate = self._get_rate(room.fan_speed)
        cost = temp_diff * rate # 1度=1元
        
        customer_id = None
        if room.status == "OCCUPIED":
            from ..services import customer_service
            c = customer_service.getCustomerByRoomId(room.id)
            if c: customer_id = c.id

        self.bill_detail_service.createBillDetail(
            room_id=room.id,
            ac_mode=mode,
            fan_speed=room.fan_speed,
            start_time=room.serving_start_time,
            end_time=end_time,
            rate=rate,
            cost=cost,
            customer_id=customer_id,
            detail_type="AC"
        )
        print(f"[Scheduler] 结算 AC费 Room {room.id}: {cost:.2f}元")

    # --- 状态迁移 ---

    def _demote_serving_room(self, request: RoomRequest, reason: str) -> None:
        room = self.room_service.getRoomById(request.roomId)
        if not room: return
        now = clock.now()
        
        self._updateRoomTemperature(room, force_update=True)
        self._settle_current_service_period(room, now, reason)

        self._remove_request(self.serving_queue, request.roomId)
        self._remove_request(self.waiting_queue, request.roomId)
        
        request.servingTime = None
        request.waitingTime = now
        self.waiting_queue.append(request)

        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "serving_start_time": None,
            "billing_start_temp": None,
            "waiting_start_time": now
        })
        db.session.commit()
        # 同步内存
        room.serving_start_time = None
        room.billing_start_temp = None

    def _promote_waiting_room(self, request: RoomRequest) -> None:
        room = self.room_service.getRoomById(request.roomId)
        if not room: return
        now = clock.now()

        self._updateRoomTemperature(room, force_update=True)
        
        self._remove_request(self.waiting_queue, request.roomId)
        self._remove_request(self.serving_queue, request.roomId)
        
        request.waitingTime = None
        request.servingTime = now
        self.serving_queue.append(request)

        start_temp = float(room.current_temp or 25.0)
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "serving_start_time": now,
            "waiting_start_time": None,
            "billing_start_temp": start_temp
        })
        db.session.commit()
        room.serving_start_time = now
        room.billing_start_temp = start_temp

    def _handle_temp_reached(self, room: Room, current_temp: float):
        now = clock.now()
        if room.serving_start_time:
            self._settle_current_service_period(room, now, "TEMP_REACHED")
        
        self._remove_request(self.serving_queue, room.id)
        self._remove_request(self.waiting_queue, room.id)
        
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "cooling_paused": True,
            "pause_start_temp": current_temp,
            "serving_start_time": None,
            "waiting_start_time": None,
            "billing_start_temp": None
        })
        db.session.commit()
        room.serving_start_time = None
        room.billing_start_temp = None
        room.cooling_paused = True
        self._schedule_queues(force=False)

    def _handle_rewarm_wake(self, room: Room):
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "cooling_paused": False,
            "pause_start_temp": None
        })
        db.session.commit()
        room.cooling_paused = False
        self._add_request_to_queue(room)

    # --- 调度策略 ---

    def _schedule_queues(self, force: bool = False):
        self._enforce_capacity()
        self._check_preemption()
        self._rotate_time_slice(force)
        self._fill_slots()

    def _enforce_capacity(self):
        limit = self._capacity()
        now = clock.now()
        while len(self.serving_queue) > limit:
            self.serving_queue.sort(key=lambda r: (
                self._priority_score(r),
                -self._get_simulated_duration(r.servingTime, now)
            ))
            self._demote_serving_room(self.serving_queue[0], "CAPACITY")

    def _check_preemption(self):
        if not self.waiting_queue or len(self.serving_queue) < self._capacity(): return
        now = clock.now()
        
        weakest = min(self.serving_queue, key=lambda r: (
            self._priority_score(r), -self._get_simulated_duration(r.servingTime, now)
        ))
        strongest = max(self.waiting_queue, key=lambda r: (
            self._priority_score(r), self._get_simulated_duration(r.waitingTime, now)
        ))
        
        if self._priority_score(strongest) > self._priority_score(weakest):
            self._demote_serving_room(weakest, "PREEMPTED")

    def _rotate_time_slice(self, force: bool):
        if not self.serving_queue: return
        if len(self.serving_queue) < self._capacity() and not self.waiting_queue: return
        
        limit = self._time_slice()
        now = clock.now()
        
        # 找出超时者，按时间倒序
        candidates = [r for r in self.serving_queue if self._get_simulated_duration(r.servingTime, now) >= limit]
        candidates.sort(key=lambda r: self._get_simulated_duration(r.servingTime, now), reverse=True)
        
        for req in candidates:
            if req in self.serving_queue:
                self._demote_serving_room(req, "ROTATED")

    def _fill_slots(self):
        limit = self._capacity()
        now = clock.now()
        if not self.waiting_queue: return
        self.waiting_queue.sort(key=lambda r: (-self._priority_score(r), r.waitingTime or now))
        while len(self.serving_queue) < limit and self.waiting_queue:
            self._promote_waiting_room(self.waiting_queue[0])

    # --- API ---

    def _add_request_to_queue(self, room: Room):
        req = RoomRequest(roomId=room.id, fanSpeed=room.fan_speed, mode=room.ac_mode, targetTemp=room.target_temp)
        now = clock.now()
        self._remove_request(self.serving_queue, room.id)
        self._remove_request(self.waiting_queue, room.id)
        
        if len(self.serving_queue) < self._capacity():
            req.servingTime = now
            self.serving_queue.append(req)
            self._mark_serving_db(room.id, now, room.current_temp)
        else:
            req.waitingTime = now
            self.waiting_queue.append(req)
            self._mark_waiting_db(room.id, now)
        self._schedule_queues(force=True)

    def _mark_serving_db(self, rid, time, temp):
        from ..extensions import db
        t = float(temp or 25.0)
        db.session.query(Room).filter(Room.id == rid).update({
            "serving_start_time": time, "billing_start_temp": t, "waiting_start_time": None
        })
        db.session.commit()
        r = self.room_service.getRoomById(rid)
        if r: r.billing_start_temp = t

    def _mark_waiting_db(self, rid, time):
        from ..extensions import db
        db.session.query(Room).filter(Room.id == rid).update({
            "waiting_start_time": time, "serving_start_time": None, "billing_start_temp": None
        })
        db.session.commit()

    def PowerOn(self, RoomId: int, CurrentRoomTemp: float | None) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room: return "错误"
            if room.ac_on: return "已开启"
            
            now = clock.now()
            temp = float(CurrentRoomTemp) if CurrentRoomTemp is not None else float(room.current_temp or 25.0)
            
            # --- 关键: 按次收取房费 ---
            enable_cycle_fee = current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE", False)
            if enable_cycle_fee:
                fee = room.daily_rate if room.daily_rate is not None else 0.0
                if fee > 0:
                    # 创建一条“房费”类型的账单
                    self.bill_detail_service.createBillDetail(
                        room_id=room.id,
                        ac_mode="NONE",
                        fan_speed="NONE",
                        start_time=now,
                        end_time=now,
                        rate=0.0,
                        cost=fee,
                        customer_id=None, 
                        detail_type="ROOM_FEE"
                    )
                    print(f"[Scheduler] Room {room.id} 开机: 收取房费 {fee} 元")

            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_on": True, "current_temp": temp, "ac_session_start": now,
                "last_temp_update": now, "cooling_paused": False
            })
            db.session.commit()
            
            room.ac_on = True
            room.current_temp = temp
            room.last_temp_update = now
            
            self._add_request_to_queue(room)
            return "空调已开启"

    def PowerOff(self, RoomId: int) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "未开启"
            now = clock.now()
            
            # 1. 结算当前未完成的空调费
            self._updateRoomTemperature(room, force_update=True)
            self._settle_current_service_period(room, now, "POWER_OFF")
            
            # 2. 移除队列
            self._remove_request(self.serving_queue, room.id)
            self._remove_request(self.waiting_queue, room.id)
            
            # 3. 关机重置状态：重置温度、风速到默认值
            from ..extensions import db
            
            # 决定重置的默认值
            mode = (room.ac_mode or "COOLING").upper()
            default_target = 22.0 if mode == "HEATING" else 25.0  # 目标温度默认值
            default_speed = "MEDIUM"  # 风速默认值
            # 当前温度重置为房间的默认温度（如果房间有 default_temp，使用它；否则使用 25.0）
            default_current_temp = float(room.default_temp) if room.default_temp is not None else 25.0

            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_on": False, 
                "ac_session_start": None, 
                "serving_start_time": None,
                "waiting_start_time": None, 
                "billing_start_temp": None,
                "cooling_paused": False, 
                "pause_start_temp": None,
                # === 重置温度和风速到默认值 ===
                "current_temp": default_current_temp,  # 重置当前温度为默认温度
                "target_temp": default_target,         # 重置目标温度为默认值
                "fan_speed": default_speed,            # 重置风速为 MEDIUM
                "last_temp_update": None                # 清除温度更新时间，下次开机时重新初始化
            })
            db.session.commit()
            
            # 同步内存对象
            room.ac_on = False
            room.current_temp = default_current_temp
            room.target_temp = default_target
            room.fan_speed = default_speed
            room.last_temp_update = None
            
            self._schedule_queues(force=True)
            return "空调已关闭"

    def ChangeTemp(self, RoomId: int, TargetTemp: float) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "错误"
            
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({"target_temp": TargetTemp})
            db.session.commit()
            room.target_temp = TargetTemp
            
            if room.cooling_paused:
                db.session.query(Room).filter(Room.id == room.id).update({"cooling_paused": False, "pause_start_temp": None})
                db.session.commit()
                self._add_request_to_queue(room)
            return "温度已设定"

    def ChangeSpeed(self, RoomId: int, FanSpeed: str) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "错误"
            
            new_speed = FanSpeed.upper()
            if room.fan_speed == new_speed: return "未变"
            now = clock.now()
            
            if room.serving_start_time:
                self._updateRoomTemperature(room, force_update=True)
                self._settle_current_service_period(room, now, "CHANGE_SPEED")
                self._mark_serving_db(room.id, now, room.current_temp)

            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({"fan_speed": new_speed})
            db.session.commit()
            room.fan_speed = new_speed
            self._add_request_to_queue(room)
            return "风速已调整"

    def ChangeMode(self, RoomId: int, Mode: str) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room: return "错误"
            new_mode = Mode.upper()
            if new_mode == room.ac_mode: return "未变"
            now = clock.now()
            
            if room.serving_start_time:
                self._updateRoomTemperature(room, force_update=True)
                self._settle_current_service_period(room, now, "CHANGE_MODE")
                self._mark_serving_db(room.id, now, room.current_temp)

            default_target = 22.0 if new_mode == "HEATING" else 25.0
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({"ac_mode": new_mode, "target_temp": default_target})
            db.session.commit()
            room.ac_mode = new_mode
            room.target_temp = default_target
            self._add_request_to_queue(room)
            return "模式已切换"

    # --- 监控 ---
    
    def simulateTemperatureUpdate(self) -> dict:
        updated = 0
        with self._lock:
            from ..models import Room
            rooms = Room.query.filter_by(ac_on=True).all()
            for room in rooms:
                old = room.current_temp
                self._updateRoomTemperature(room)
                if abs((room.current_temp or 0) - (old or 0)) > 0.001:
                    updated += 1
            self._schedule_queues()
        return {"updated": updated}

    def RequestState(self, RoomId: int) -> dict:
        """
        状态查询: 动态计算费用
        """
        room = self.room_service.getRoomById(RoomId)
        if not room: return {}
        
        enable_cycle_fee = current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE", False)
        
        total_cost = 0.0
        # 如果未开启循环计费，则需要手动加上静态房费（仅为了展示，逻辑上可能不严谨，但符合旧版逻辑）
        if not enable_cycle_fee:
            total_cost = float(room.daily_rate or 0.0)
        
        # 1. 历史账单 (包含历史空调费，以及按次收取的房费)
        from ..extensions import db
        history = db.session.query(func.sum(DetailRecord.cost))\
            .filter(DetailRecord.room_id == room.id).scalar()
        if history:
            total_cost += float(history)

        # 2. 当前未结算 (Pending AC Fee)
        if room.ac_on and room.serving_start_time and room.billing_start_temp is not None:
            curr = float(room.current_temp or 25)
            start = float(room.billing_start_temp)
            diff = 0.0
            if (room.ac_mode or "COOLING") == "COOLING":
                if curr < start: diff = start - curr
            else:
                if curr > start: diff = curr - start
            
            if diff > 0:
                total_cost += diff * 1.0 # 费率恒为1

        qs = "IDLE"
        if room.cooling_paused: qs = "PAUSED"
        elif any(r.roomId == room.id for r in self.serving_queue): qs = "SERVING"
        elif any(r.roomId == room.id for r in self.waiting_queue): qs = "WAITING"

        return {
            "room_id": room.id,
            "ac_on": room.ac_on,
            "current_temp": round(float(room.current_temp or 0), 2),
            "currentTemp": round(float(room.current_temp or 0), 2),
            "target_temp": float(room.target_temp or 25),
            "targetTemp": float(room.target_temp or 25),
            "mode": room.ac_mode,
            "ac_mode": room.ac_mode,
            "fan_speed": room.fan_speed,
            "fanSpeed": room.fan_speed,
            "state": qs, "queueState": qs, "queue_state": qs,
            "total_cost": round(total_cost, 2)
        }
    
    def getScheduleStatus(self):
        with self._lock:
            now = clock.now()
            s_list = []
            for r in self.serving_queue:
                sec = self._get_simulated_duration(r.servingTime, now)
                s_list.append({"roomId": r.roomId, "fanSpeed": r.fanSpeed, "servingSeconds": sec, "totalSeconds": sec})
            w_list = []
            for r in self.waiting_queue:
                sec = self._get_simulated_duration(r.waitingTime, now)
                w_list.append({"roomId": r.roomId, "fanSpeed": r.fanSpeed, "waitingSeconds": sec})
            
            return {
                "capacity": self._capacity(),
                "timeSlice": self._time_slice(),
                "servingQueue": s_list,
                "waitingQueue": w_list
            }