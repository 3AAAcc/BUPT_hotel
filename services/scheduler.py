from __future__ import annotations

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

    def _capacity(self) -> int:
        return int(current_app.config["HOTEL_AC_TOTAL_COUNT"])

    def _time_slice(self) -> int:
        return int(current_app.config["HOTEL_TIME_SLICE"])

    def _rate_by_fan_speed(self, fan_speed: str) -> float:
        fan_speed = (fan_speed or "MEDIUM").upper()
        if fan_speed == "HIGH": return 1.0
        if fan_speed == "MEDIUM": return 0.5
        return 1.0 / 3.0

    def _time_factor(self) -> float:
        return float(current_app.config.get("TIME_ACCELERATION_FACTOR", 1.0))

    # === 辅助方法 ===
    def _priority_score(self, request: RoomRequest) -> int:
        score_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return score_map.get((request.fanSpeed or "MEDIUM").upper(), 2)

    def _elapsed_seconds(self, source: Optional[datetime], now: datetime) -> float:
        if not source: return 0.0
        return max(0.0, (now - source).total_seconds() * self._time_factor())

    # === ⚡️ 核心修复：彻底移除指定 ID 的所有实例 ===
    def _remove_from_queue(self, queue: List[RoomRequest], room_id: int) -> Optional[RoomRequest]:
        target_id = int(room_id)
        removed_item = None
        
        # 使用列表推导式重建列表，保留 ID 不匹配的项
        # 这样可以一次性把所有重复的 ID 全部删掉
        clean_list = []
        for req in queue:
            if int(req.roomId) != target_id:
                clean_list.append(req)
            else:
                removed_item = req # 记录被删除的项（如果有多个，记录最后一个也无所谓）
        
        # 原地修改列表引用
        queue[:] = clean_list
        return removed_item

    def _mark_room_serving(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if room:
            room.serving_start_time = started_at
            room.waiting_start_time = None
            self.room_service.updateRoom(room)

    def _mark_room_waiting(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if room:
            room.waiting_start_time = started_at
            room.serving_start_time = None
            self.room_service.updateRoom(room)

    def _remove_request(self, room_id: int) -> None:
        self._remove_from_queue(self.serving_queue, room_id)
        self._remove_from_queue(self.waiting_queue, room_id)

    # === ⚡️ 核心修复：强力去重逻辑 ===
    def _deduplicate_queues(self) -> None:
        """确保每个 ID 在整个系统中只出现一次，优先保留服务队列"""
        unique_ids = set()
        
        # 1. 清洗服务队列
        clean_serving = []
        for req in self.serving_queue:
            rid = int(req.roomId)
            if rid not in unique_ids:
                unique_ids.add(rid)
                clean_serving.append(req)
        self.serving_queue = clean_serving
        
        # 2. 清洗等待队列 (如果 ID 已经在 unique_ids 里，说明在服务队列或前面已出现过，删！)
        clean_waiting = []
        for req in self.waiting_queue:
            rid = int(req.roomId)
            if rid not in unique_ids:
                unique_ids.add(rid)
                clean_waiting.append(req)
        self.waiting_queue = clean_waiting

    # === 队列操作 ===
    def _move_to_waiting(self, request: RoomRequest, timestamp: datetime, reason: str = "ROTATED") -> None:
        # 先彻底清理旧状态
        self._remove_request(request.roomId)
        
        room = self.room_service.getRoomById(request.roomId)
        if room and room.serving_start_time:
            self._settle_current_service_period(room, timestamp, reason)
        
        request.waitingTime = timestamp
        request.servingTime = None
        self.waiting_queue.append(request)
        self._mark_room_waiting(request.roomId, timestamp)

    def _move_to_serving(self, request: RoomRequest, timestamp: datetime) -> None:
        # 先彻底清理旧状态
        self._remove_request(request.roomId)

        request.servingTime = timestamp
        request.waitingTime = None
        self.serving_queue.append(request)
        self._mark_room_serving(request.roomId, timestamp)

    # === 计费 ===
    def _settle_current_service_period(self, room: Room, end_time: datetime, reason: str = "CHANGE") -> None:
        if not room.serving_start_time: return
        start_time = room.serving_start_time
        duration_minutes = max(1, int(((end_time - start_time).total_seconds() / 60.0) * self._time_factor()))
        rate = self._rate_by_fan_speed(room.fan_speed)
        cost = rate * duration_minutes
        
        cid = None
        if room.status == "OCCUPIED":
            from ..services import customer_service
            cust = customer_service.getCustomerByRoomId(room.id)
            if cust: cid = cust.id
        
        detail_type = "POWER_OFF_CYCLE" if reason == "POWER_OFF" else "AC"
        self.bill_detail_service.createBillDetail(
            room_id=room.id, ac_mode=room.ac_mode, fan_speed=room.fan_speed,
            start_time=start_time, end_time=end_time, rate=rate, cost=cost,
            customer_id=cid, detail_type=detail_type,
        )

    # === 状态流转 ===
    def _pause_cooling(self, room: Room) -> None:
        now = datetime.utcnow()
        if room.serving_start_time:
            self._settle_current_service_period(room, now, "PAUSED")
        self._remove_request(room.id)
        room.serving_start_time = None
        room.waiting_start_time = None
        room.ac_session_start = now
        room.cooling_paused = True
        self.room_service.updateRoom(room)
        self._rebalance_queues()

    def _resume_cooling(self, room: Room) -> None:
        now = datetime.utcnow()
        self._remove_request(room.id) # 这里的 remove 现在会清理得非常干净
        
        req = RoomRequest(roomId=room.id, fanSpeed=room.fan_speed, mode=room.ac_mode, targetTemp=room.target_temp)
        if len(self.serving_queue) < self._capacity():
            req.servingTime = now; self.serving_queue.append(req); self._mark_room_serving(room.id, now)
        else:
            req.waitingTime = now; self.waiting_queue.append(req); self._mark_room_waiting(room.id, now)
        
        room.cooling_paused = False
        self.room_service.updateRoom(room)
        self._rebalance_queues()

    # === 调度算法 ===
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
            self._move_to_serving(p, now)
            
        if len(self.serving_queue) >= capacity and self.waiting_queue:
            high = self.waiting_queue[0]
            low_s = min(self.serving_queue, key=lambda r: (self._priority_score(r), -(self._elapsed_seconds(r.servingTime, now))))
            if self._priority_score(high) > self._priority_score(low_s):
                d = self._remove_from_queue(self.serving_queue, low_s.roomId)
                if d:
                    self._move_to_waiting(d, now, "PREEMPTED")
                    high = self.waiting_queue.pop(0)
                    self._move_to_serving(high, now)

    def _rotate_time_slice(self, *, force: bool = False) -> None:
        if not self.serving_queue: return
        now = datetime.utcnow()
        limit = self._time_slice()
        to_demote = []
        for req in self.serving_queue:
            if self._elapsed_seconds(req.servingTime, now) >= limit:
                to_demote.append(req)
        to_demote.sort(key=lambda r: self._elapsed_seconds(r.servingTime, now), reverse=True)
        
        for req in to_demote:
            demoted = self._remove_from_queue(self.serving_queue, req.roomId)
            if demoted: self._move_to_waiting(demoted, now, "ROTATED")
        self._promote_waiting_room()

    def _enforce_capacity(self) -> None:
        capacity = self._capacity()
        now = datetime.utcnow()
        while len(self.serving_queue) > capacity:
            self.serving_queue.sort(key=lambda r: (self._priority_score(r), -(self._elapsed_seconds(r.servingTime, now))))
            demoted = self.serving_queue.pop(0)
            self._move_to_waiting(demoted, now, "CAPACITY")
        self._promote_waiting_room()

    def _rebalance_queues(self, *, force_rotation: bool = False) -> None:
        self._deduplicate_queues() # 每次平衡前先彻底去重
        self._enforce_capacity()
        self._rotate_time_slice(force=force_rotation)

    # === 外部接口 ===
    def PowerOn(self, RoomId: int, CurrentRoomTemp: float | None) -> str:
        room = self.room_service.getRoomById(RoomId)
        if not room: raise ValueError("不存在")
        if room.ac_on: return "已开启"

        now = datetime.utcnow()
        if CurrentRoomTemp is not None: room.current_temp = CurrentRoomTemp
        elif room.current_temp is None: room.current_temp = room.default_temp
        
        room.ac_on = True
        room.ac_session_start = now
        room.last_temp_update = now
        mode = room.ac_mode or 'COOLING'
        default_target = current_app.config["HEATING_DEFAULT_TARGET"] if mode == 'HEATING' else current_app.config["COOLING_DEFAULT_TARGET"]
        room.target_temp = default_target

        self._remove_request(room.id) # 确保干净入队

        if abs(room.current_temp - room.target_temp) < 0.1:
            room.cooling_paused = True
            room.pause_start_temp = room.current_temp
        else:
            req = RoomRequest(roomId=room.id, fanSpeed=room.fan_speed, mode=room.ac_mode, targetTemp=room.target_temp)
            if len(self.serving_queue) < self._capacity():
                req.servingTime = now; self.serving_queue.append(req); self._mark_room_serving(room.id, now)
            else:
                req.waitingTime = now; self.waiting_queue.append(req); self._mark_room_waiting(room.id, now)
        
        self.room_service.updateRoom(room)
        self._rebalance_queues()
        return f"开启 ({mode})"

    def PowerOff(self, RoomId: int) -> str:
        room = self.room_service.getRoomById(RoomId)
        if not room or not room.ac_on: raise ValueError("未开启")
        now = datetime.utcnow()
        if room.serving_start_time:
            self._settle_current_service_period(room, now, "POWER_OFF")
        else:
            cid = None
            if room.status == "OCCUPIED":
                from ..services import customer_service
                cust = customer_service.getCustomerByRoomId(room.id)
                if cust: cid = cust.id
            self.bill_detail_service.createBillDetail(
                room_id=room.id, ac_mode=room.ac_mode, fan_speed=room.fan_speed,
                start_time=now, end_time=now, rate=0.0, cost=0.0,
                customer_id=cid, detail_type="POWER_OFF_CYCLE"
            )

        if room.default_temp is not None: room.current_temp = room.default_temp
        room.ac_on = False; room.ac_session_start = None; room.waiting_start_time = None; room.serving_start_time = None
        room.cooling_paused = False; room.pause_start_temp = None; room.last_temp_update = now
        
        self.room_service.updateRoom(room)
        self._remove_request(room.id) # 这会彻底清除所有实例
        self._rebalance_queues(force_rotation=True)
        return "已关机"

    def ChangeTemp(self, RoomId: int, TargetTemp: float) -> str:
        room = self.room_service.getRoomById(RoomId)
        if not room or not room.ac_on: raise ValueError("请先开机")
        mode = room.ac_mode or 'COOLING'
        if mode == 'COOLING':
            if not (current_app.config["COOLING_MIN_TEMP"] <= TargetTemp <= current_app.config["COOLING_MAX_TEMP"]): raise ValueError("超范围")
        else:
            if not (current_app.config["HEATING_MIN_TEMP"] <= TargetTemp <= current_app.config["HEATING_MAX_TEMP"]): raise ValueError("超范围")

        room.target_temp = TargetTemp
        if room.cooling_paused:
            room.cooling_paused = False; room.pause_start_temp = None
            self._resume_cooling(room)
        self.room_service.updateRoom(room)
        for q in (self.serving_queue, self.waiting_queue):
            for r in q:
                if int(r.roomId) == RoomId: r.targetTemp = TargetTemp
        return "成功"

    def ChangeSpeed(self, RoomId: int, FanSpeed: str) -> str:
        room = self.room_service.getRoomById(RoomId)
        if not room or not room.ac_on: raise ValueError("请先开机")
        norm = FanSpeed.upper()
        if (room.fan_speed or "MEDIUM").upper() != norm and room.serving_start_time:
            self._settle_current_service_period(room, datetime.utcnow(), "CHANGE")
        room.fan_speed = norm
        self.room_service.updateRoom(room)
        
        self._resume_cooling(room) # 内部会调用 _remove_request
        return "成功"

    def ChangeMode(self, RoomId: int, Mode: str) -> str:
        room = self.room_service.getRoomById(RoomId)
        if not room: raise ValueError("不存在")
        norm = Mode.upper()
        if room.ac_mode == norm: return "未变"
        room.ac_mode = norm
        room.target_temp = current_app.config["HEATING_DEFAULT_TARGET"] if norm == 'HEATING' else current_app.config["COOLING_DEFAULT_TARGET"]
        for q in (self.serving_queue, self.waiting_queue):
            for r in q:
                if int(r.roomId) == RoomId: r.mode = norm; r.targetTemp = room.target_temp
        self.room_service.updateRoom(room)
        return "成功"

    # === 温控 ===
    def _updateRoomTemperature(self, room) -> None:
        now = datetime.utcnow()
        current_temp = room.current_temp or room.default_temp or 0.0
        new_temp = current_temp
        if room.last_temp_update: elapsed = ((now - room.last_temp_update).total_seconds() / 60.0) * self._time_factor()
        else: elapsed = 0.0
        fan_speed = (room.fan_speed or "MEDIUM").upper()
        rate_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 1.0/3.0}
        change_rate = rate_map.get(fan_speed, 0.5)
        rewarming_rate = 0.5

        if not room.ac_on:
            if room.default_temp is not None:
                diff = room.default_temp - current_temp
                if abs(diff) < 0.1: new_temp = room.default_temp
                else: new_temp += max(min(diff, rewarming_rate * elapsed), -rewarming_rate * elapsed)
        else:
            is_serving = any(int(r.roomId) == room.id for r in self.serving_queue)
            if is_serving:
                diff = room.target_temp - current_temp
                if abs(diff) < 0.2:
                    new_temp = room.target_temp
                    if room.default_temp and abs(room.target_temp - room.default_temp) > 0.5:
                        room.cooling_paused = True; room.pause_start_temp = new_temp
                        self._pause_cooling(room)
                else:
                    new_temp += max(min(diff, change_rate * elapsed), -change_rate * elapsed)
            elif room.cooling_paused or not is_serving:
                if room.default_temp is not None:
                    diff = room.default_temp - current_temp
                    if abs(diff) < 0.1:
                        new_temp = room.default_temp
                        if abs(new_temp - (room.target_temp or 0)) >= 1.0:
                            room.cooling_paused = False; room.pause_start_temp = None
                            self._resume_cooling(room)
                    else:
                        new_temp += max(min(diff, rewarming_rate * elapsed), -rewarming_rate * elapsed)
                        if room.cooling_paused and room.pause_start_temp and abs(new_temp - room.pause_start_temp) >= 1.0:
                            room.cooling_paused = False; room.pause_start_temp = None
                            self._resume_cooling(room)

        if abs(new_temp - current_temp) >= 1e-6:
            room.current_temp = round(new_temp, 2)
            room.last_temp_update = now
            self.room_service.updateRoom(room)

    # === 状态 ===
    def RequestState(self, RoomId: int) -> dict:
        room = self.room_service.getRoomById(RoomId)
        if not room: raise ValueError("不存在")
        try:
            from ..services import bill_service
            fee = bill_service.getCurrentFeeDetail(room)
            total = fee.get("total", 0.0); curr = fee.get("current_session_fee", 0.0)
        except: total=0.0; curr=0.0

        status = {
            "id": room.id, "room_id": room.id, "ac_on": bool(room.ac_on), "ac_mode": room.ac_mode, "fan_speed": room.fan_speed,
            "current_temp": room.current_temp, "currentTemp": room.current_temp,
            "target_temp": room.target_temp, "targetTemp": room.target_temp,
            "total_cost": total, "totalCost": total, "current_cost": curr, "currentCost": curr
        }
        
        now = datetime.utcnow()
        qs="IDLE"; ws=0; ss=0; qp=None
        if room.cooling_paused: qs="PAUSED"
        else:
            for r in self.serving_queue:
                if int(r.roomId)==RoomId: qs="SERVING"; ss=self._elapsed_seconds(r.servingTime, now); break
            else:
                for i, r in enumerate(self.waiting_queue):
                    if int(r.roomId)==RoomId: qs="WAITING"; ws=self._elapsed_seconds(r.waitingTime, now); qp=i+1; break
        status.update({"queueState": qs, "waitingSeconds": ws, "servingSeconds": ss, "queuePosition": qp})
        return status

    def getScheduleStatus(self) -> dict:
        self._restore_queue_from_database()
        self._deduplicate_queues()
        self._rebalance_queues()
        for r in self.room_service.getAllRooms(): self._updateRoomTemperature(r)
        
        now = datetime.utcnow()
        def _to_pl(q): return [{"roomId": r.roomId, "fanSpeed": r.fanSpeed, "servingSeconds": self._elapsed_seconds(r.servingTime, now), "waitingSeconds": self._elapsed_seconds(r.waitingTime, now)} for r in q]
        return {
            "capacity": self._capacity(), "timeSlice": self._time_slice(),
            "servingQueue": _to_pl(self.serving_queue), "waitingQueue": _to_pl(self.waiting_queue)
        }

    def simulateTemperatureUpdate(self) -> dict:
        if not self.serving_queue and not self.waiting_queue:
            from ..models import Room
            if Room.query.filter_by(ac_on=True).count() > 0: self._restore_queue_from_database()
        for r in self.room_service.getAllRooms(): self._updateRoomTemperature(r)
        return {"message": "Updated"}

    def _restore_queue_from_database(self) -> None:
        self._deduplicate_queues() # 先清理内存
        from ..models import Room
        active = {r.id for r in Room.query.filter_by(ac_on=True).all()}
        
        # 移除已关机的
        self.serving_queue = [r for r in self.serving_queue if int(r.roomId) in active]
        self.waiting_queue = [r for r in self.waiting_queue if int(r.roomId) in active]
        
        existing = {int(r.roomId) for r in self.serving_queue} | {int(r.roomId) for r in self.waiting_queue}
        now = datetime.utcnow()
        capacity = self._capacity()

        for rid in active:
            if rid in existing: continue
            r = self.room_service.getRoomById(rid)
            if not r or r.cooling_paused: continue
            
            req = RoomRequest(roomId=r.id, fanSpeed=r.fan_speed, mode=r.ac_mode, targetTemp=r.target_temp)
            if r.serving_start_time:
                if len(self.serving_queue) < capacity:
                    req.servingTime = r.serving_start_time; self.serving_queue.append(req)
                else:
                    req.waitingTime = r.serving_start_time; self.waiting_queue.append(req); self._mark_room_waiting(r.id, req.waitingTime)
            elif r.waiting_start_time:
                req.waitingTime = r.waiting_start_time; self.waiting_queue.append(req)
            else:
                if len(self.serving_queue) < capacity:
                    req.servingTime = r.ac_session_start or now; self.serving_queue.append(req); self._mark_room_serving(r.id, now)
                else:
                    req.waitingTime = r.ac_session_start or now; self.waiting_queue.append(req); self._mark_room_waiting(r.id, now)
        
        self._rebalance_queues()