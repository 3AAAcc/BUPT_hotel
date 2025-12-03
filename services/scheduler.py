from __future__ import annotations

import threading
from datetime import datetime
from typing import Dict, List, Optional

from flask import current_app

from ..models import Room, RoomRequest
from .bill_detail_service import BillDetailService
from .room_service import RoomService


class Scheduler:
    def __init__(self, room_service: RoomService, bill_detail_service: BillDetailService):
        self.room_service = room_service
        self.bill_detail_service = bill_detail_service
        self.serving_queue: List[RoomRequest] = []
        self.waiting_queue: List[RoomRequest] = []
        # 添加线程锁，确保温度更新操作的原子性
        self._temp_update_lock = threading.Lock()

    def _capacity(self) -> int:
        return int(current_app.config["HOTEL_AC_TOTAL_COUNT"])

    def _time_slice(self) -> int:
        return int(current_app.config["HOTEL_TIME_SLICE"])

    def _rate_by_fan_speed(self, fan_speed: str) -> float:
        fan_speed = (fan_speed or "MEDIUM").upper()
        if fan_speed == "HIGH":
            return 1.0
        if fan_speed == "MEDIUM":
            return 0.5
        return 1.0 / 3.0

    def _time_factor(self) -> float:
        factor = current_app.config.get("TIME_ACCELERATION_FACTOR", 1.0)
        try:
            factor = float(factor)
        except (TypeError, ValueError):
            factor = 1.0
        return factor if factor > 0 else 1.0
    
    def _settle_current_service_period(
        self, room: Room, end_time: datetime, reason: str = "CHANGE"
    ) -> None:
        if not room.serving_start_time:
            return
        
        start_time = room.serving_start_time
        
        # 1. 计算原始分钟数 (含小数)
        # 例如: 物理10秒 + 延迟2秒 = 12秒 -> 乘以6.0 = 72秒 = 1.2分钟
        raw_minutes = ((end_time - start_time).total_seconds() / 60.0) * self._time_factor()
        
        # 2. 使用 round() 进行四舍五入
        duration_minutes = round(raw_minutes)
        
        # 特殊处理：如果是 POWER_OFF 且时长为0，为了记录周期，允许为0
        # 如果是正常运行但不足30秒（系统时间），算作0费用是合理的（这是防抖动）
        # 如果你非常在意"不足1分钟按1分钟算"，可以只对 POWER_OFF 且总时长极短的情况做特殊处理
        # 但对于"中间状态切换"，算0是最好的。
        
        # 使用当前风速的费率
        rate = self._rate_by_fan_speed(room.fan_speed)
        cost = rate * duration_minutes
        
        customer_id = None
        if room.status == "OCCUPIED":
            from ..services import customer_service
            customer = customer_service.getCustomerByRoomId(room.id)
            if customer:
                customer_id = customer.id
        
        is_cycle_end = (reason == "POWER_OFF")
        detail_type = "POWER_OFF_CYCLE" if is_cycle_end else "AC"
        
        self.bill_detail_service.createBillDetail(
            room_id=room.id,
            ac_mode=room.ac_mode,
            fan_speed=room.fan_speed,
            start_time=start_time,
            end_time=end_time,
            rate=rate,
            cost=cost,
            customer_id=customer_id,
            detail_type=detail_type,
        )

    def _priority_score(self, request: RoomRequest) -> int:
        score_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return score_map.get((request.fanSpeed or "MEDIUM").upper(), 2)

    def _elapsed_seconds(self, source: Optional[datetime], now: datetime) -> float:
        if not source:
            return 0.0
        return max(0.0, (now - source).total_seconds() * self._time_factor())

    def _remove_from_queue(self, queue: List[RoomRequest], room_id: int) -> Optional[RoomRequest]:
        for idx, req in enumerate(queue):
            if req.roomId == room_id:
                return queue.pop(idx)
        return None

    def _mark_room_serving(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if room:
            room.serving_start_time = started_at
            room.waiting_start_time = None
            # === 关键修复：使用原子更新，只更新时间字段，避免覆盖 current_temp ===
            from ..extensions import db
            from ..models import Room
            db.session.query(Room).filter(Room.id == room_id).update({
                "serving_start_time": started_at,
                "waiting_start_time": None
            })
            db.session.commit()

    def _mark_room_waiting(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if room:
            room.waiting_start_time = started_at
            room.serving_start_time = None
            # === 关键修复：使用原子更新，只更新时间字段，避免覆盖 current_temp ===
            from ..extensions import db
            from ..models import Room
            db.session.query(Room).filter(Room.id == room_id).update({
                "waiting_start_time": started_at,
                "serving_start_time": None
            })
            db.session.commit()

    def _remove_request(self, room_id: int) -> None:
        self._remove_from_queue(self.serving_queue, room_id)
        self._remove_from_queue(self.waiting_queue, room_id)

    def _pause_cooling(self, room: Room) -> None:
        now = datetime.utcnow()
        if room.serving_start_time:
            self._settle_current_service_period(room, now, "PAUSED")
        self._remove_request(room.id)
        room.serving_start_time = None
        room.waiting_start_time = None
        room.ac_session_start = now
        self.room_service.updateRoom(room)
        self._rebalance_queues()

    def _resume_cooling(self, room: Room) -> None:
        now = datetime.utcnow()
        request = RoomRequest(roomId=room.id, fanSpeed=room.fan_speed, mode=room.ac_mode, targetTemp=room.target_temp)
        capacity = self._capacity()
        if len(self.serving_queue) < capacity:
            request.servingTime = now
            self.serving_queue.append(request)
            self._mark_room_serving(room.id, now)
        else:
            request.waitingTime = now
            self.waiting_queue.append(request)
            self._mark_room_waiting(room.id, now)
        self._rebalance_queues()

    def _deduplicate_queues(self) -> None:
        seen = set()
        new_s = []
        for r in self.serving_queue:
            if r.roomId not in seen: seen.add(r.roomId); new_s.append(r)
        self.serving_queue = new_s
        new_w = []
        for r in self.waiting_queue:
            if r.roomId not in seen: seen.add(r.roomId); new_w.append(r)
        self.waiting_queue = new_w

    def _sort_waiting_queue(self) -> None:
        if not self.waiting_queue: return
        now = datetime.utcnow()
        self.waiting_queue.sort(key=lambda r: (-self._priority_score(r), r.waitingTime or now, r.roomId))

    def _promote_waiting_room(self) -> None:
        if not self.waiting_queue: return
        capacity = self._capacity()
        now = datetime.utcnow()
        self._sort_waiting_queue()
        while self.waiting_queue and len(self.serving_queue) < capacity:
            p = self.waiting_queue.pop(0)
            p.servingTime = now; p.waitingTime = None
            self.serving_queue.append(p)
            self._mark_room_serving(p.roomId, now)
        if len(self.serving_queue) >= capacity and self.waiting_queue:
            high = self.waiting_queue[0]
            low_s = min(self.serving_queue, key=lambda r: (self._priority_score(r), -(self._elapsed_seconds(r.servingTime, now))))
            if self._priority_score(high) > self._priority_score(low_s):
                # 关键修复：在移除前先更新温度，确保温度计算基于服务状态
                # 使用强制更新，跳过时间间隔检查，因为这是状态改变时的更新
                room = self.room_service.getRoomById(low_s.roomId)
                if room:
                    self._updateRoomTemperature(room, force_update=True)
                d = self._remove_from_queue(self.serving_queue, low_s.roomId)
                if d:
                    self._move_to_waiting(d, now, "PREEMPTED")
                    high = self.waiting_queue.pop(0)
                    high.servingTime = now; high.waitingTime = None
                    self.serving_queue.append(high)
                    self._mark_room_serving(high.roomId, now)

    def _move_to_waiting(self, request: RoomRequest, timestamp: datetime, reason: str = "ROTATED") -> None:
        room = self.room_service.getRoomById(request.roomId)
        if room and room.serving_start_time:
            # 结算费用（温度已在移除前更新，这里不需要再次更新）
            self._settle_current_service_period(room, timestamp, reason)
        request.waitingTime = timestamp
        request.servingTime = None
        self.waiting_queue.append(request)
        self._mark_room_waiting(request.roomId, timestamp)

    def _move_to_serving(self, request: RoomRequest, timestamp: datetime) -> None:
        request.servingTime = timestamp
        request.waitingTime = None
        self.serving_queue.append(request)
        self._mark_room_serving(request.roomId, timestamp)

    def _rotate_time_slice(self, *, force: bool = False) -> None:
        if not self.serving_queue: return
        capacity = self._capacity()
        if len(self.serving_queue) < capacity: return
        now = datetime.utcnow()
        limit = self._time_slice()
        to_demote = []
        for req in self.serving_queue:
            if self._elapsed_seconds(req.servingTime, now) >= limit:
                to_demote.append(req)
        to_demote.sort(key=lambda r: self._elapsed_seconds(r.servingTime, now), reverse=True)
        
        for req in to_demote:
            # 关键修复：在移除前先更新温度，确保温度计算基于服务状态
            # 使用强制更新，跳过时间间隔检查，因为这是状态改变时的更新
            room = self.room_service.getRoomById(req.roomId)
            if room:
                self._updateRoomTemperature(room, force_update=True)
            demoted = self._remove_from_queue(self.serving_queue, req.roomId)
            if demoted:
                self._move_to_waiting(demoted, now, "ROTATED")
        
        self._promote_waiting_room()

    def _enforce_capacity(self) -> None:
        capacity = self._capacity()
        now = datetime.utcnow()
        while len(self.serving_queue) > capacity:
            self.serving_queue.sort(key=lambda r: (self._priority_score(r), -(self._elapsed_seconds(r.servingTime, now))))
            # 关键修复：在移除前先更新温度，确保温度计算基于服务状态
            # 使用强制更新，跳过时间间隔检查，因为这是状态改变时的更新
            room = self.room_service.getRoomById(self.serving_queue[0].roomId)
            if room:
                self._updateRoomTemperature(room, force_update=True)
            demoted = self.serving_queue.pop(0)
            self._move_to_waiting(demoted, now, "CAPACITY")
        self._promote_waiting_room()

    def _rebalance_queues(self, *, force_rotation: bool = False) -> None:
        self._enforce_capacity()
        self._rotate_time_slice(force=force_rotation)

    def PowerOn(self, RoomId: int, CurrentRoomTemp: float | None) -> str:
        # 关键修复：加锁保护队列操作，避免与后台线程冲突
        with self._temp_update_lock:
            room_id = RoomId
            current_temp = CurrentRoomTemp
            room = self.room_service.getRoomById(room_id)
            if room is None: raise ValueError("房间不存在")
            if room.ac_on: return "房间空调已开启"

            now = datetime.utcnow()
            if current_temp is not None:
                room.current_temp = current_temp
            elif room.current_temp is None:
                room.current_temp = room.default_temp or current_app.config["HOTEL_DEFAULT_TEMP"]
            
            room.ac_on = True
            room.ac_session_start = now
            room.last_temp_update = now
            room.target_temp = room.target_temp or current_app.config["HOTEL_DEFAULT_TEMP"]

            request = RoomRequest(roomId=room.id, fanSpeed=room.fan_speed, mode=room.ac_mode, targetTemp=room.target_temp)
            capacity = self._capacity()
            if len(self.serving_queue) < capacity:
                request.servingTime = now
                self.serving_queue.append(request)
                self._mark_room_serving(room.id, now)
            else:
                request.waitingTime = now
                self.waiting_queue.append(request)
                self._mark_room_waiting(room.id, now)
            
            self._rebalance_queues()
            # === 关键修复：使用原子更新，只更新需要的字段，避免覆盖后台线程更新的温度 ===
            from ..extensions import db
            from ..models import Room
            update_dict = {
                "ac_on": True,
                "ac_session_start": now,
                "last_temp_update": now,
                "target_temp": room.target_temp
            }
            if current_temp is not None:
                update_dict["current_temp"] = current_temp
            elif room.current_temp is None:
                update_dict["current_temp"] = room.default_temp or current_app.config["HOTEL_DEFAULT_TEMP"]
            db.session.query(Room).filter(Room.id == room.id).update(update_dict)
            db.session.commit()
            return "空调已开启并进入调度"

    def PowerOff(self, RoomId: int) -> str:
        # 关键修复：加锁保护队列操作，避免与后台线程冲突
        with self._temp_update_lock:
            room_id = RoomId
            room = self.room_service.getRoomById(room_id)
            if room is None: raise ValueError("房间不存在")
            if not room.ac_on: raise ValueError("房间空调尚未开启")

            now = datetime.utcnow()
            if room.serving_start_time:
                self._settle_current_service_period(room, now, "POWER_OFF")
            else:
                customer_id = None
                if room.status == "OCCUPIED":
                    from ..services import customer_service
                    cust = customer_service.getCustomerByRoomId(room.id)
                    if cust: customer_id = cust.id
                self.bill_detail_service.createBillDetail(
                    room_id=room.id, ac_mode=room.ac_mode, fan_speed=room.fan_speed,
                    start_time=now, end_time=now, rate=0.0, cost=0.0,
                    customer_id=customer_id, detail_type="POWER_OFF_CYCLE"
                )

            if room.default_temp is not None:
                room.current_temp = room.default_temp


            # === 新增：关机恢复默认风速 (中风) ===
            room.fan_speed = "MEDIUM"
            # ==================================
            room.ac_on = False
            room.ac_session_start = None
            room.waiting_start_time = None
            room.serving_start_time = None
            room.cooling_paused = False
            room.pause_start_temp = None
            room.last_temp_update = now
            
            # === 关键修复：使用原子更新，只更新需要的字段 ===
            from ..extensions import db
            from ..models import Room
            update_dict = {
                "ac_on": False,
                "fan_speed": "MEDIUM",
                "ac_session_start": None,
                "waiting_start_time": None,
                "serving_start_time": None,
                "cooling_paused": False,
                "pause_start_temp": None,
                "last_temp_update": now
            }
            if room.default_temp is not None:
                update_dict["current_temp"] = room.default_temp
            db.session.query(Room).filter(Room.id == room.id).update(update_dict)
            db.session.commit()
            self._remove_request(room.id)
            self._rebalance_queues(force_rotation=True)
            return "空调已关闭"

    def ChangeTemp(self, RoomId: int, TargetTemp: float) -> str:
        # 关键修复：加锁保护队列操作，避免与后台线程冲突
        with self._temp_update_lock:
            room_id = RoomId
            room = self.room_service.getRoomById(room_id)
            if not room or not room.ac_on: raise ValueError("请先开启空调")
            
            # === 温度范围验证 ===
            mode = room.ac_mode or "COOLING"
            if mode == "HEATING":
                min_temp = current_app.config.get("HEATING_MIN_TEMP", 18.0)
                max_temp = current_app.config.get("HEATING_MAX_TEMP", 25.0)
            else:  # COOLING
                min_temp = current_app.config.get("COOLING_MIN_TEMP", 18.0)
                max_temp = current_app.config.get("COOLING_MAX_TEMP", 28.0)
            
            # 如果超出范围，保持上一次的目标温度
            current_target = room.target_temp
            if TargetTemp < min_temp:
                return f"目标温度 {TargetTemp}℃ 低于{mode}模式最低温度 {min_temp}℃，已保持当前设置 {current_target}℃"
            if TargetTemp > max_temp:
                return f"目标温度 {TargetTemp}℃ 高于{mode}模式最高温度 {max_temp}℃，已保持当前设置 {current_target}℃"
            # ====================
            
            room.target_temp = TargetTemp
            # 注意：不在这里更新 last_temp_update，让温度更新逻辑自己处理时间计算
            # === 关键修复：使用原子更新，只更新 target_temp 和 cooling_paused，避免覆盖 current_temp ===
            from ..extensions import db
            from ..models import Room
            update_dict = {"target_temp": TargetTemp}
            if room.cooling_paused:
                update_dict["cooling_paused"] = False
                update_dict["pause_start_temp"] = None
                room.cooling_paused = False
                room.pause_start_temp = None
                self._resume_cooling(room)
            db.session.query(Room).filter(Room.id == room.id).update(update_dict)
            db.session.commit()
            for q in (self.serving_queue, self.waiting_queue):
                for r in q:
                    if r.roomId == room_id: r.targetTemp = TargetTemp
            return "温度已更新"

    def ChangeSpeed(self, RoomId: int, FanSpeed: str) -> str:
        # 关键修复：加锁保护队列操作，避免与后台线程冲突
        with self._temp_update_lock:
            room_id = RoomId
            room = self.room_service.getRoomById(room_id)
            if not room or not room.ac_on: raise ValueError("请先开启空调")
            normalized = FanSpeed.upper()
            old_speed = (room.fan_speed or "MEDIUM").upper()
            if old_speed != normalized and room.serving_start_time:
                now = datetime.utcnow()
                self._settle_current_service_period(room, now, "CHANGE")
                room.ac_session_start = now
            
            room.fan_speed = normalized
            # === 关键修复：使用原子更新，只更新 fan_speed，避免覆盖 current_temp 和 last_temp_update ===
            # 这样可以防止 Stale Object Overwrite 问题：后台线程更新的温度不会被这里覆盖
            from ..extensions import db
            from ..models import Room
            db.session.query(Room).filter(Room.id == room.id).update({"fan_speed": normalized})
            db.session.commit()
            self._remove_request(room_id)
            now = datetime.utcnow()
            req = RoomRequest(roomId=room.id, fanSpeed=normalized, mode=room.ac_mode, targetTemp=room.target_temp)
            if room.serving_start_time:
                req.servingTime = room.serving_start_time
                self.serving_queue.append(req)
            elif room.waiting_start_time:
                req.waitingTime = room.waiting_start_time
                self.waiting_queue.append(req)
            else:
                if len(self.serving_queue) < self._capacity():
                    req.servingTime = now; self.serving_queue.append(req); self._mark_room_serving(room.id, now)
                else:
                    req.waitingTime = now; self.waiting_queue.append(req); self._mark_room_waiting(room.id, now)
            self._rebalance_queues(force_rotation=True)
            return "风速已更新"

    def ChangeMode(self, RoomId: int, Mode: str) -> str:
        """切换空调模式（制冷/制热）"""
        # 关键修复：加锁保护队列操作，避免与后台线程冲突
        with self._temp_update_lock:
            room_id = RoomId
            room = self.room_service.getRoomById(room_id)
            if not room:
                raise ValueError("房间不存在")
            
            normalized_mode = Mode.upper()
            if normalized_mode not in ['COOLING', 'HEATING']:
                raise ValueError("无效模式，必须是 COOLING 或 HEATING")
            
            # 如果模式没变，直接返回
            if room.ac_mode == normalized_mode:
                return "模式未改变"
            
            # 切换模式时，重置目标温度为默认值
            if normalized_mode == 'COOLING':
                default_target = current_app.config.get("COOLING_DEFAULT_TARGET", 25.0)
            else:  # HEATING
                default_target = current_app.config.get("HEATING_DEFAULT_TARGET", 22.0)
            
            room.ac_mode = normalized_mode
            room.target_temp = default_target
            now = datetime.utcnow()
            room.last_temp_update = now
            
            # 如果正在运行，需要更新队列里的请求参数
            for q in (self.serving_queue, self.waiting_queue):
                for r in q:
                    if r.roomId == room_id:
                        r.mode = normalized_mode
                        r.targetTemp = default_target
            
            # === 关键修复：使用原子更新，只更新需要的字段，避免覆盖 current_temp ===
            from ..extensions import db
            from ..models import Room
            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_mode": normalized_mode,
                "target_temp": default_target,
                "last_temp_update": now
            })
            db.session.commit()
            return f"已切换至 {normalized_mode} 模式，目标温度重置为 {default_target}°C"

    def _updateRoomTemperature(self, room, force_update: bool = False, serving_room_ids: list = None) -> None:
        """
        通用温控逻辑：
        1. 在服务队列中 -> 向 目标温度 (Target) 变化
        2. 不在服务队列 (排队/待机/关机) -> 向 初始温度 (Default) 回归
        
        Args:
            room: 房间对象
            force_update: 是否强制更新（用于队列调整时，跳过时间间隔检查）
            serving_room_ids: 服务队列中的房间ID列表（用于避免在更新过程中队列被修改）
        """
        # 关键修复：如果空调关闭，不执行任何温度更新
        if not room.ac_on:
            return  # 空调关闭时，温度保持不变，不执行任何计算
        
        now = datetime.utcnow()
        # === 关键修复：确保 current_temp 始终使用数据库中的实际值 ===
        # 如果 current_temp 是 None，使用 default_temp 作为初始值
        # 但要确保方向判断正确，避免温度上下浮动
        if room.current_temp is not None:
            current_temp = float(room.current_temp)
        elif room.default_temp is not None:
            current_temp = float(room.default_temp)
        else:
            current_temp = 0.0
        new_temp = current_temp
        
        # 1. 计算时间流逝 (分钟)
        # === 关键修复：温度计算基于实际时间，不依赖时间因子 ===
        # 时间因子只用于计费，不影响温度变化速率
        MIN_UPDATE_INTERVAL_SECONDS = 0.5  # 最小间隔0.5秒，避免与后台线程sleep(1.0)冲突
        
        if room.last_temp_update:
            real_elapsed_seconds = (now - room.last_temp_update).total_seconds()
            # 如果时间间隔太短且不是强制更新，不更新温度，让时间继续累积
            if not force_update and real_elapsed_seconds < MIN_UPDATE_INTERVAL_SECONDS:
                return  # 直接返回，不更新温度和时间戳
            # 温度计算使用实际时间，不乘以时间因子
            # 使用高精度计算，避免浮点数误差
            elapsed = real_elapsed_seconds / 60.0  # 转换为分钟
        else:
            # 首次调用：初始化时间戳，但不更新温度（因为时间间隔是0）
            real_elapsed_seconds = 0.0
            elapsed = 0.0
            # 注意：这里不返回，继续执行以初始化 last_temp_update

        # 2. 获取速率参数
        fan_speed = (room.fan_speed or "MEDIUM").upper()
        # 制冷/制热速率
        rate_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 1.0/3.0}
        change_rate = rate_map.get(fan_speed, 0.5)
        # 回温速率 (自然回归)
        rewarming_rate = 0.5 

        # 3. 判断当前状态
        # 关键修复：使用传入的服务队列快照，避免在更新过程中队列被修改
        # 如果没有传入快照，则从当前队列判断（用于队列调整时的强制更新）
        if serving_room_ids is not None:
            is_serving = room.ac_on and room.id in serving_room_ids
            if room.id == 1:
                print(f"[DEBUG] Room 1 is_serving判断: ac_on={room.ac_on}, id={room.id}, "
                      f"serving_room_ids={serving_room_ids}, is_serving={is_serving}")
        else:
            # 如果没有传入快照，需要恢复队列状态（用于队列调整时的强制更新）
            from ..models import Room
            if Room.query.filter_by(ac_on=True).count() > 0:
                self._restore_queue_from_database()
            is_serving = room.ac_on and any(int(r.roomId) == room.id for r in self.serving_queue)
            if room.id == 1:
                serving_ids = [int(r.roomId) for r in self.serving_queue]
                print(f"[DEBUG] Room 1 is_serving判断(无快照): ac_on={room.ac_on}, serving_ids={serving_ids}, is_serving={is_serving}")
        
        # === 调试：检查等待队列中的房间 ===
        if room.ac_on and not is_serving:
            # 等待队列中的房间，应该回温
            if room.default_temp is None:
                print(f"[WARNING] Room {room.id} 在等待队列中，但 default_temp 是 None，无法回温！")
            elif room.id == 1:
                print(f"[DEBUG] Room 1 在等待队列: current_temp={current_temp}, default_temp={room.default_temp}, "
                      f"diff={room.default_temp - current_temp}, is_serving={is_serving}")

        # ==========================================
        # 情况 A: 正在服务 (主动制冷/制热)
        # ==========================================
        if is_serving:
            if room.id == 1:
                print(f"[DEBUG] Room 1 正在服务: current_temp={current_temp}, target_temp={room.target_temp}, "
                      f"diff={room.target_temp - current_temp}")
            # 物理逻辑：向 Target 靠拢
            diff = room.target_temp - current_temp
            
            # === 核心修复：死循环阻断 ===
            # 如果是 force_update (正在进行队列调度中)，只计算温度变化，
            # 绝对不要触发 _pause_cooling，否则会导致无限递归：
            # rebalance -> update_temp -> pause_cooling -> rebalance
            check_state_change = not force_update  # 只有非强制更新时，才允许改变状态
            
            # 检查是否到达目标 (容差 0.1)
            # 注意：这里要防止"过冲"，即一步跨过目标温度
            if abs(diff) < 0.1:
                new_temp = room.target_temp
                step_size = 0.0  # 已经到达目标，步长为0
                # 只有正常轮询时，才触发停机
                if check_state_change:
                    # 达到目标，触发 PAUSED
                    # (制冷时当前<=目标，制热时当前>=目标，都算达标)
                    # 这里简单用绝对值判断接近程度
                    room.cooling_paused = True
                    room.pause_start_temp = new_temp
                    print(f"[Scheduler] Room {room.id} 温度达标 ({new_temp})，进入待机")
                    self._pause_cooling(room)  # <--- 这行代码就是罪魁祸首，加锁屏蔽
            else:
                # 计算本轮变化量 (不超过剩余温差)
                # step_size 是绝对值
                # 使用高精度计算，避免浮点数累积误差
                step_size = change_rate * elapsed
                # 确保步长不会因为浮点数误差而丢失精度
                if step_size < 1e-10:
                    step_size = 0.0
                
                if diff > 0: # 需要升温 (制热)
                    new_temp = min(room.target_temp, current_temp + step_size)
                else: # 需要降温 (制冷)
                    new_temp = max(room.target_temp, current_temp - step_size)

        # ==========================================
        # 情况 B: 不在服务 (排队 WAITING / 待机 PAUSED / 关机 OFF)
        # ==========================================
        else:
            # 物理逻辑：向 Default (环境温度) 回归
            # === 关键修复：等待队列中的房间必须回温，使用与正在服务房间相同的更新机制 ===
            if room.id == 1:
                print(f"[DEBUG] Room 1 回温检查: default_temp={room.default_temp}, current_temp={current_temp}, "
                      f"is_serving={is_serving}, ac_on={room.ac_on}")
            if room.default_temp is not None:
                # === 关键修复：确保 default_temp 是浮点数，避免类型不一致导致方向判断错误 ===
                default_temp = float(room.default_temp)
                diff_to_default = default_temp - current_temp
                
                if abs(diff_to_default) < 0.1:
                    new_temp = default_temp
                    step_size = 0.0  # 已经到达目标，步长为0
                else:
                    # 计算回温变化量
                    # === 关键修复：使用与正在服务房间相同的计算方式，确保精度 ===
                    step_size = rewarming_rate * elapsed
                    # 确保步长不会因为浮点数误差而丢失精度
                    if step_size < 1e-10:
                        step_size = 0.0
                    
                    # === 关键修复：确保方向判断正确，始终朝着 default_temp 方向回温 ===
                    if diff_to_default > 0: # 环境比当前热 -> 升温 (制冷后的回温)
                        new_temp = min(default_temp, current_temp + step_size)
                        if room.id == 1:
                            print(f"[DEBUG] Room 1 回温(升温): current={current_temp:.2f}, default={default_temp:.2f}, "
                                  f"diff={diff_to_default:.2f}, step={step_size:.4f}, new={new_temp:.2f}")
                    else: # 环境比当前冷 -> 降温 (制热后的回冷)
                        new_temp = max(default_temp, current_temp - step_size)
                        if room.id == 1:
                            print(f"[DEBUG] Room 1 回温(降温): current={current_temp:.2f}, default={default_temp:.2f}, "
                                  f"diff={diff_to_default:.2f}, step={step_size:.4f}, new={new_temp:.2f}")
            else:
                # 如果 default_temp 是 None，保持当前温度不变
                new_temp = current_temp
                step_size = 0.0  # 没有默认温度，步长为0

            # 仅针对 PAUSED 状态的唤醒检查 (回温超过 1 度)
            if room.ac_on and room.cooling_paused:
                # === 核心修复：死循环阻断 ===
                # 同样阻断唤醒递归，避免 force_update 时触发 _resume_cooling
                check_state_change = not force_update  # 只有非强制更新时，才允许改变状态
                
                if check_state_change:
                    # 唤醒阈值检查：
                    # 如果没有 pause_start_temp，就用 target_temp 做基准
                    base_temp = room.pause_start_temp if room.pause_start_temp is not None else room.target_temp
                    
                    # 检查偏离程度
                    if abs(new_temp - base_temp) >= 1.0:
                        print(f"[Scheduler] Room {room.id} 回温超过1度 ({new_temp} vs {base_temp})，重新唤醒")
                        room.cooling_paused = False
                        room.pause_start_temp = None
                        self._resume_cooling(room)  # <--- 同样会触发 rebalance

        # 4. 更新数据库
        # === 关键修复：使用原子更新，只更新温度和时间戳，避免覆盖其他线程修改的属性 ===
        # === 核心修复：只要时间戳更新，温度就必须更新，否则会"吞时间" ===
        # 问题：如果温度变化 < 1e-6，只更新 last_temp_update 不更新 current_temp，
        # 会导致时间前进但温度不变，下次计算时基准时间变成新时间，之前那段时间的温差就丢失了
        from ..extensions import db
        from ..models import Room
        
        try:
            # 只更新 current_temp 和 last_temp_update 两个字段
            # 这样即使其他线程修改了 fan_speed、ac_mode 等属性，也不会被这里覆盖
            # === 修复：取消阈值限制，只要时间戳动了，温度就必须跟着动 ===
            # 浮点数计算肯定会有微小差异，直接更新即可，避免"吞时间"问题
            update_dict = {
                "last_temp_update": now,
                "current_temp": float(new_temp)  # 无论变化多小，都要更新温度
            }
            
            db.session.query(Room).filter(Room.id == room.id).update(update_dict)
            db.session.commit()
            
            # 更新内存中的对象，以便后续逻辑（如果还有）使用最新值
            room.current_temp = float(new_temp)
            room.last_temp_update = now
        except Exception as e:
            # 关键修复：更新失败时，确保会话被正确回滚和清理
            try:
                db.session.rollback()
            except Exception:
                # 如果回滚也失败，说明会话已经损坏，需要移除并重新创建
                try:
                    db.session.remove()
                except Exception:
                    pass
            print(f"[Scheduler] 原子更新房间 {room.id} 温度失败: {e}")

    def RequestState(self, RoomId: int) -> dict:
        room = self.room_service.getRoomById(RoomId)
        if not room: raise ValueError("房间不存在")
        
        current_val = 0.0
        total_val = 0.0
        try:
            from ..services import bill_service
            fee_data = bill_service.getCurrentFeeDetail(room)
            current_val = fee_data.get("current_session_fee", 0.0)
            
            # ===这里一定要取 'total' 而不是 'total_fee' ===
            # 'total' 包含了 roomFee + acFee
            total_val = fee_data.get("total", 0.0)
        except Exception: 
            pass

        status = {
            "id": room.id, "room_id": room.id,
            "ac_on": bool(room.ac_on), "ac_mode": room.ac_mode, "fan_speed": room.fan_speed,
            # 在这里展示时 round 是安全的，不会影响物理核心的累积
            "current_temp": round(room.current_temp, 2) if room.current_temp is not None else 0.0,
            "currentTemp": round(room.current_temp, 2) if room.current_temp is not None else 0.0,
            "target_temp": round(room.target_temp, 2) if room.target_temp is not None else 25.0,
            "targetTemp": round(room.target_temp, 2) if room.target_temp is not None else 25.0,
            # === 添加 default_temp 字段，用于调试 ===
            "default_temp": round(room.default_temp, 2) if room.default_temp is not None else None,
            
            "current_cost": current_val, "currentCost": current_val,
            
            # 这里传给前端的 total_cost 将包含房费
            "total_cost": total_val, "totalCost": total_val
        }
        
        now = datetime.utcnow()
        qs = "IDLE"; ws = 0.0; ss = 0.0; qp = None
        if room.cooling_paused: qs = "PAUSED"
        else:
            for r in self.serving_queue:
                if r.roomId == RoomId: qs = "SERVING"; ss = self._elapsed_seconds(r.servingTime, now); break
            else:
                for i, r in enumerate(self.waiting_queue):
                    if r.roomId == RoomId: qs = "WAITING"; ws = self._elapsed_seconds(r.waitingTime, now); qp = i+1; break
        
        status.update({"queueState": qs, "waitingSeconds": ws, "servingSeconds": ss, "queuePosition": qp})
        return status

    def simulateTemperatureUpdate(self) -> dict:
        from ..extensions import db
        
        # 关键修复：在锁内恢复队列状态，确保所有房间的温度更新都基于正确的队列状态
        # 然后在锁外执行温度更新，让每个房间独立更新，避免串行阻塞
        with self._temp_update_lock:
            from ..models import Room
            if Room.query.filter_by(ac_on=True).count() > 0:
                self._restore_queue_from_database()
            # 在锁内获取队列快照，避免在更新过程中队列被修改
            serving_room_ids = [int(r.roomId) for r in self.serving_queue]
            # 注意：不在锁内提交会话，避免与锁外的操作冲突
            # 锁内的查询操作会自动使用会话，锁外的更新操作会独立管理会话
        
        # 在锁外执行温度更新，让每个房间独立更新，避免串行阻塞
        # 重新从数据库获取所有房间，确保获取最新数据
        rooms = self.room_service.getAllRooms()
        u = 0
        for room in rooms:
            try:
                # 为每个房间创建独立的数据库会话，确保数据一致性
                fresh_room = self.room_service.getRoomById(room.id)
                if not fresh_room:
                    continue
                
                # 保存原始温度用于比较
                o = fresh_room.current_temp
                # 更新温度（传入服务队列快照，避免在更新过程中队列被修改）
                # 每个房间的更新是独立的，不需要全局锁
                self._updateRoomTemperature(fresh_room, serving_room_ids=serving_room_ids)
                # 重新获取更新后的温度，确保数据一致
                updated_room = self.room_service.getRoomById(room.id)
                if updated_room and updated_room.current_temp is not None and o is not None and abs(updated_room.current_temp - o) >= 1e-6:
                    u += 1
            except Exception as e:
                # 单个房间更新失败时，回滚该房间的更改，继续处理其他房间
                try:
                    db.session.rollback()
                except Exception:
                    pass
                print(f"[Scheduler] 更新房间 {room.id} 温度时出错: {e}")
                continue
        
        # 关键修复：更新完成后，确保所有未提交的更改都已提交
        # 注意：每个房间的更新都已经在 _updateRoomTemperature 中 commit 了
        # 这里主要是为了确保会话状态正确，避免会话在不同线程间共享
        try:
            # 检查是否有未提交的更改
            if db.session.dirty or db.session.new or db.session.deleted:
                db.session.commit()
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
        
        return {"message": "Updated", "updatedRooms": u}

    def getScheduleStatus(self) -> dict:
        """获取调度器的全局状态（用于监控大屏和测试脚本）"""
        from ..extensions import db
        # 关键修复：加锁保护队列操作，避免读取到不一致的队列状态
        with self._temp_update_lock:
            # === 关键修复：移除温度更新调用 ===
            # 温度更新只由后台任务负责，这里只负责读取和返回状态
            # 这样可以避免前端频繁调用导致重复更新

            # 1. 状态整理（不更新温度）
            self._restore_queue_from_database()
            self._deduplicate_queues()
            self._rebalance_queues()
            # 注意：不再在这里更新温度，温度更新由后台任务统一处理
            self._enforce_capacity()
            
            # 在锁内获取队列快照，避免在生成 payload 时队列被修改
            now = datetime.utcnow()
            serving_queue_snapshot = list(self.serving_queue)
            waiting_queue_snapshot = list(self.waiting_queue)
            
            # 关键修复：在锁内执行数据库操作后，确保会话状态正确
            # 但不在锁内提交，避免与锁外的操作冲突
            # 锁内的查询操作会自动使用会话，锁外的操作会独立管理会话

        # 内部函数：生成队列数据
        def _to_payload(queue: List[RoomRequest], is_serving: bool) -> List[Dict[str, object]]:
            payload = []
            for req in queue:
                # A. 当前状态的时间片 (用于调度逻辑，满120秒清零)
                if is_serving:
                    slice_seconds = self._elapsed_seconds(req.servingTime, now)
                else:
                    slice_seconds = self._elapsed_seconds(req.waitingTime, now)
                
                # B. 累计总时长 (用于展示，从开机到现在)
                total_seconds = slice_seconds # 起步是当前片段
                
                # 查询数据库里的历史账单时长
                room = self.room_service.getRoomById(req.roomId)
                if room and room.ac_session_start:
                    # 获取本次开机后的所有详单
                    details = self.bill_detail_service.getBillDetailsByRoomIdAndTimeRange(
                        room_id=room.id,
                        start=room.ac_session_start,
                        end=now
                    )
                    # 累加历史分钟数 -> 转为秒
                    # 过滤掉 POWER_OFF_CYCLE 这种标记
                    history_minutes = sum(d.duration for d in details if getattr(d, 'detail_type', 'AC') != 'POWER_OFF_CYCLE')
                    total_seconds += (history_minutes * 60)

                payload.append({
                    "roomId": req.roomId,
                    "fanSpeed": req.fanSpeed,
                    "mode": req.mode,
                    "targetTemp": req.targetTemp,
                    # 区分两个时间
                    "servingSeconds": slice_seconds if is_serving else 0, # 时间片
                    "waitingSeconds": slice_seconds if not is_serving else 0, # 等待时间
                    "totalSeconds": total_seconds # 总时长
                })
            return payload

        return {
            "capacity": self._capacity(),
            "timeSlice": self._time_slice(),
            "servingQueue": _to_payload(serving_queue_snapshot, True),
            "waitingQueue": _to_payload(waiting_queue_snapshot, False),
        }

    def _restore_queue_from_database(self) -> None:
        # 关键修复：移除 finally 块中的 commit，避免与调用者的会话管理冲突
        # 调用者（在锁内）会统一管理会话
        self._deduplicate_queues()
        from ..models import Room
        active = {r.id for r in Room.query.filter_by(ac_on=True).all()}
        self.serving_queue = [r for r in self.serving_queue if r.roomId in active]
        self.waiting_queue = [r for r in self.waiting_queue if r.roomId in active]
        existing = {r.roomId for r in self.serving_queue} | {r.roomId for r in self.waiting_queue}
        now = datetime.utcnow()
        for rid in active:
            if rid in existing: continue
            r = self.room_service.getRoomById(rid)
            if not r or r.cooling_paused: continue
            req = RoomRequest(roomId=r.id, fanSpeed=r.fan_speed or "MEDIUM", mode=r.ac_mode, targetTemp=r.target_temp)
            if r.serving_start_time: req.servingTime = r.serving_start_time; self.serving_queue.append(req)
            elif r.waiting_start_time: req.waitingTime = r.waiting_start_time; self.waiting_queue.append(req)
            else:
                if len(self.serving_queue) < self._capacity(): req.servingTime = r.ac_session_start or now; self.serving_queue.append(req); self._mark_room_serving(r.id, req.servingTime)
                else: req.waitingTime = r.ac_session_start or now; self.waiting_queue.append(req); self._mark_room_waiting(r.id, req.waitingTime)
        # 关键修复：移除这里的 _rebalance_queues() 调用，避免重复调用
        # 调用者会根据需要调用 _rebalance_queues()