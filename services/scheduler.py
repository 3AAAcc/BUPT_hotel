from __future__ import annotations

import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import current_app

from ..models import Room, RoomRequest
from .bill_detail_service import BillDetailService
from .room_service import RoomService

# =============================================================================
# 调度器 (Scheduler) - 核心重构版
# =============================================================================

class Scheduler:
    def __init__(self, room_service: RoomService, bill_detail_service: BillDetailService):
        self.room_service = room_service
        self.bill_detail_service = bill_detail_service
        
        # 内存队列：只存储 Request 对象
        self.serving_queue: List[RoomRequest] = []
        self.waiting_queue: List[RoomRequest] = []
        
        # 线程锁：保证调度逻辑原子性
        self._lock = threading.Lock()

    # -------------------------------------------------------------------------
    # 1. 辅助方法 (Helpers)
    # -------------------------------------------------------------------------

    def _capacity(self) -> int:
        """获取服务容量，确保总是返回有效值"""
        try:
            val = current_app.config.get("HOTEL_AC_TOTAL_COUNT", 3)
            capacity = int(val) if val is not None else 3
            return max(1, capacity)  # 至少为1，避免除零错误
        except (ValueError, TypeError):
            return 3  # 默认值

    def _time_slice(self) -> int:
        """时间片限制（单位：模拟秒）"""
        try:
            val = current_app.config.get("HOTEL_TIME_SLICE", 120)
            time_slice = int(val) if val is not None else 120
            return max(1, time_slice)  # 至少为1
        except (ValueError, TypeError):
            return 120  # 默认值

    def _time_factor(self) -> float:
        """时间加速因子：1.0 表示 1秒物理时间=1秒模拟时间"""
        val = current_app.config.get("TIME_ACCELERATION_FACTOR", 1.0)
        return float(val) if float(val) > 0 else 1.0

    def _get_simulated_duration(self, start_time: datetime, end_time: datetime) -> float:
        """计算两个时间点之间经过的【模拟秒数】"""
        if not start_time or not end_time: return 0.0
        real_seconds = (end_time - start_time).total_seconds()
        return max(0.0, real_seconds * self._time_factor())

    def _priority_score(self, request: RoomRequest) -> int:
        """优先级：HIGH(3) > MEDIUM(2) > LOW(1)"""
        mapping = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return mapping.get((request.fanSpeed or "MEDIUM").upper(), 2)

    def _remove_request(self, queue: List[RoomRequest], room_id: int) -> None:
        """从指定队列安全移除请求"""
        for i in range(len(queue) - 1, -1, -1):
            if queue[i].roomId == room_id:
                queue.pop(i)

    # -------------------------------------------------------------------------
    # 2. 核心逻辑：温度计算 (Temperature Logic)
    # -------------------------------------------------------------------------

    def _updateRoomTemperature(self, room: Room, force_update: bool = False) -> None:
        """
        核心物理引擎：计算并更新房间温度
        """
        now = datetime.utcnow()
        
        # 1. 初始化检查：如果缺少上次更新时间，说明是刚开机或数据异常，直接重置基准点
        if not room.last_temp_update:
            from ..extensions import db
            room.last_temp_update = now
            db.session.commit()
            return

        # 2. 计算经过的【模拟分钟数】
        # 温度变化率通常是 "度/分钟"，所以我们需要模拟时间的分钟数
        sim_seconds = self._get_simulated_duration(room.last_temp_update, now)
        sim_minutes = sim_seconds / 60.0
        
        # 移除防抖逻辑：每次调用都更新温度，确保温度和费用计算准确
        # 如果时间差为0或负数，直接返回（避免除零或倒退）
        if sim_minutes <= 0 and not force_update:
            return

        # 3. 获取当前参数
        current_temp = float(room.current_temp) if room.current_temp is not None else 25.0
        target_temp = float(room.target_temp) if room.target_temp is not None else 25.0
        default_temp = float(room.default_temp) if room.default_temp is not None else 25.0
        fan_speed = (room.fan_speed or "MEDIUM").upper()
        mode = (room.ac_mode or "COOLING").upper()

        # 4. 判断状态
        # 只要在服务队列中，就判定为 SERVING；否则为 WAITING/IDLE
        # 注意：如果房间有 serving_start_time 且没有 cooling_paused，说明应该正在服务
        is_serving = any(r.roomId == room.id for r in self.serving_queue)
        # 如果不在队列中但有 serving_start_time，说明可能刚被调度，按服务状态处理
        if not is_serving and room.serving_start_time and not room.cooling_paused:
            is_serving = True

        # 5. 计算新温度
        new_temp = current_temp
        
        if is_serving:
            # === 服务状态：调节温度 ===
            # 变温速率
            rate_map = {"HIGH": 1.0, "MEDIUM": 0.5, "LOW": 1.0/3.0} # 度/分钟
            rate = rate_map.get(fan_speed, 0.5)
            
            delta = rate * sim_minutes

            if mode == "COOLING":
                # 制冷：温度下降，最低降到 target
                if current_temp > target_temp:
                    new_temp = max(target_temp, current_temp - delta)
                # 如果已经达到或低于目标温度，保持温度不变（不升温）
            else: 
                # 制热：温度上升，最高升到 target
                if current_temp < target_temp:
                    new_temp = min(target_temp, current_temp + delta)
                # 如果已经达到或高于目标温度，保持温度不变（不降温）

            # 检查是否达到目标温度 (进入待机/温控)
            if abs(new_temp - target_temp) < 0.01:
                new_temp = target_temp
                if not force_update: # 避免在结算逻辑中递归调用
                    self._handle_temp_reached(room, new_temp)
                    
        else:
            # === 等待/待机状态：自然回温 ===
            # 回温速率：0.5度/分钟
            rewarm_rate = 0.5
            delta = rewarm_rate * sim_minutes
            
            # 向默认温度靠拢
            if current_temp < default_temp:
                new_temp = min(default_temp, current_temp + delta)
            elif current_temp > default_temp:
                new_temp = max(default_temp, current_temp - delta)

            # 检查回温唤醒 (待机状态下偏离超过1度)
            if room.cooling_paused and not force_update:
                pause_base = room.pause_start_temp if room.pause_start_temp is not None else target_temp
                if abs(new_temp - pause_base) >= 1.0:
                    self._handle_rewarm_wake(room)

        # 6. 持久化
        from ..extensions import db
        try:
            room.current_temp = new_temp
            room.last_temp_update = now
            # 使用原子更新防止竞争
            db.session.query(Room).filter(Room.id == room.id).update({
                "current_temp": new_temp,
                "last_temp_update": now
            })
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"[Scheduler] Temp Update Failed: {e}")

    # -------------------------------------------------------------------------
    # 3. 核心逻辑：计费 (Billing Logic)
    # -------------------------------------------------------------------------

    def _settle_current_service_period(self, room: Room, end_time: datetime, reason: str) -> None:
        """
        结算当前时间段的费用。
        逻辑：费用 = |当前温度 - 计费开始温度| * 单价
        """
        # 只有在服务中，且有计费起点记录，才进行结算
        if not room.serving_start_time or room.billing_start_temp is None:
            return

        start_temp = float(room.billing_start_temp)
        # 此时 room.current_temp 已经被 _updateRoomTemperature 更新为最新值
        end_temp = float(room.current_temp)
        
        mode = room.ac_mode or "COOLING"
        temp_diff = 0.0

        # 计算有效温差 (Effective Temperature Difference)
        if mode == "COOLING":
            # 制冷：只有温度降低了才算钱
            if end_temp < start_temp:
                temp_diff = start_temp - end_temp
        else:
            # 制热：只有温度升高了才算钱
            if end_temp > start_temp:
                temp_diff = end_temp - start_temp

        # 如果温差太小（可能是时间极短），忽略
        if temp_diff < 0.001:
            return

        cost = temp_diff * 1.0 # 费率：1元/度
        
        # 获取客户ID
        customer_id = None
        if room.status == "OCCUPIED":
            from ..services import customer_service
            c = customer_service.getCustomerByRoomId(room.id)
            if c: customer_id = c.id

        # 生成详单
        self.bill_detail_service.createBillDetail(
            room_id=room.id,
            ac_mode=mode,
            fan_speed=room.fan_speed,
            start_time=room.serving_start_time,
            end_time=end_time,
            rate=1.0,
            cost=cost,
            customer_id=customer_id,
            detail_type="AC" # 可以根据 reason 细分
        )
        
        print(f"[Scheduler] 结算 Room {room.id}: {start_temp:.2f}->{end_temp:.2f} (diff {temp_diff:.2f}), Cost: {cost:.2f}")

    # -------------------------------------------------------------------------
    # 4. 核心逻辑：状态迁移 (State Transitions)
    # -------------------------------------------------------------------------

    def _demote_serving_room(self, request: RoomRequest, reason: str) -> None:
        """
        【降级】：Service -> Waiting
        必须遵循：更新温度 -> 结算费用 -> 移出队列 -> 更新数据库
        """
        room = self.room_service.getRoomById(request.roomId)
        if not room: return
        
        now = datetime.utcnow()

        # 1. 更新温度 & 结算 (此时房间还在 serving_queue，Update 逻辑会按服务状态计算)
        self._updateRoomTemperature(room, force_update=True)
        self._settle_current_service_period(room, now, reason)

        # 2. 内存操作
        self._remove_request(self.serving_queue, request.roomId)
        # 确保不重复添加
        self._remove_request(self.waiting_queue, request.roomId)
        
        request.servingTime = None
        request.waitingTime = now
        self.waiting_queue.append(request)

        # 3. 数据库操作
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "serving_start_time": None,
            "billing_start_temp": None, # 停止计费
            "waiting_start_time": now
        })
        db.session.commit()
        print(f"[Scheduler] Room {room.id} 降级到等待队列 ({reason})")

    def _promote_waiting_room(self, request: RoomRequest) -> None:
        """
        【升级】：Waiting -> Service
        必须遵循：更新温度 -> 移出队列 -> 加入队列 -> 设置计费起点
        """
        room = self.room_service.getRoomById(request.roomId)
        if not room: return
        
        now = datetime.utcnow()

        # 1. 更新温度 (此时在 waiting_queue，Update 逻辑按回温计算，确保基准正确)
        self._updateRoomTemperature(room, force_update=True)
        
        # 2. 内存操作
        self._remove_request(self.waiting_queue, request.roomId)
        self._remove_request(self.serving_queue, request.roomId)
        
        request.waitingTime = None
        request.servingTime = now
        self.serving_queue.append(request)

        # 3. 数据库操作 (开启新一轮计费)
        # 必须使用最新的 current_temp 作为 billing_start_temp
        start_temp = float(room.current_temp) if room.current_temp is not None else 25.0
        
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "serving_start_time": now,
            "waiting_start_time": None,
            "billing_start_temp": start_temp # 设定计费锚点
        })
        db.session.commit()
        # 同步内存对象
        room.billing_start_temp = start_temp 
        room.serving_start_time = now
        print(f"[Scheduler] Room {room.id} 升级到服务队列")

    def _handle_temp_reached(self, room: Room, current_temp: float):
        """处理达到目标温度：转为待机 (Paused)"""
        now = datetime.utcnow()
        
        # 1. 结算最后一段费用
        if room.serving_start_time:
            self._settle_current_service_period(room, now, "TEMP_REACHED")
        
        # 2. 移出所有队列
        self._remove_request(self.serving_queue, room.id)
        self._remove_request(self.waiting_queue, room.id)
        
        # 3. 更新DB
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "cooling_paused": True,
            "pause_start_temp": current_temp,
            "serving_start_time": None,
            "waiting_start_time": None,
            "billing_start_temp": None
        })
        db.session.commit()
        
        # 4. 触发调度填补空缺
        self._schedule_queues(force=False)

    def _handle_rewarm_wake(self, room: Room):
        """处理回温唤醒：重新申请服务"""
        print(f"[Scheduler] Room {room.id} 回温唤醒，重新加入队列")
        # 仅更新状态，add_request 会处理队列逻辑
        from ..extensions import db
        db.session.query(Room).filter(Room.id == room.id).update({
            "cooling_paused": False,
            "pause_start_temp": None
        })
        db.session.commit()
        
        # 重新创建请求加入调度
        self._add_request_to_queue(room)

    # -------------------------------------------------------------------------
    # 5. 调度策略 (Scheduling Strategy)
    # -------------------------------------------------------------------------

    def _schedule_queues(self, force: bool = False) -> None:
        """
        主调度方法：集成容量限制、优先级抢占、时间片轮转
        """
        # 1. 容量限制 (Enforce Capacity)
        self._enforce_capacity()
        
        # 2. 优先级抢占 (Preemption)
        self._check_preemption()

        # 3. 时间片轮转 (Time Slice)
        self._rotate_time_slice(force)

        # 4. 填补空位 (Fill Slots)
        self._fill_slots()

    def _enforce_capacity(self):
        """如果在服务队列中的数量 > 容量，踢出优先级最低且服务最久的"""
        limit = self._capacity()
        now = datetime.utcnow()
        
        while len(self.serving_queue) > limit:
            # 排序逻辑：我们想找出【最应该被踢掉】的房间放到 list[0]
            # 规则：优先级越低越该踢，服务时间越长越该踢
            # Sort Key: (Priority Ascending, Simulated Duration Descending)
            # 优先级: Low(1) < Medium(2) < High(3)
            # 服务时长: 长 > 短
            
            # Key 构造:
            # priority_score: 越小越排前 (Low=1)
            # duration: 我们希望时长大的排前，所以取 -duration
            
            self.serving_queue.sort(key=lambda r: (
                self._priority_score(r),
                -self._get_simulated_duration(r.servingTime, now)
            ))
            
            victim = self.serving_queue[0]
            self._demote_serving_room(victim, "CAPACITY")

    def _check_preemption(self):
        """检查等待队列是否有高优先级需要抢占"""
        if not self.waiting_queue or len(self.serving_queue) < self._capacity():
            return
            
        now = datetime.utcnow()
        
        # 找出服务队列中最弱的 (Low Priority, Longest Service)
        weakest_serving = min(self.serving_queue, key=lambda r: (
            self._priority_score(r),
            -self._get_simulated_duration(r.servingTime, now)
        ))
        
        # 找出等待队列最强的 (High Priority, Longest Wait)
        strongest_waiting = max(self.waiting_queue, key=lambda r: (
            self._priority_score(r),
            self._get_simulated_duration(r.waitingTime, now) # 等待时间越长越优先
        ))

        # 仅当 等待者优先级 > 服务者优先级 时抢占
        if self._priority_score(strongest_waiting) > self._priority_score(weakest_serving):
            print(f"[Scheduler] 抢占发生: Room {strongest_waiting.roomId} 抢占 {weakest_serving.roomId}")
            self._demote_serving_room(weakest_serving, "PREEMPTED")
            # 腾出位置后，_fill_slots 会处理后续

    def _rotate_time_slice(self, force: bool):
        """检查时间片"""
        if not self.serving_queue: return
        
        # 如果资源充足且无人排队，无需轮转
        if len(self.serving_queue) < self._capacity() and not self.waiting_queue:
            return

        limit = self._time_slice() # 模拟秒数
        now = datetime.utcnow()
        
        candidates = []
        for req in self.serving_queue:
            # 检查服务时长（模拟时间）
            dur = self._get_simulated_duration(req.servingTime, now)
            if dur >= limit:
                candidates.append(req)
        
        # 按时长倒序，优先踢服务最久的
        candidates.sort(key=lambda r: self._get_simulated_duration(r.servingTime, now), reverse=True)
        
        for req in candidates:
            if req in self.serving_queue: # 再次确认
                self._demote_serving_room(req, "ROTATED")

    def _fill_slots(self):
        """如果有空位，从等待队列调度"""
        limit = self._capacity()
        now = datetime.utcnow()
        
        if not self.waiting_queue: return
        
        # 等待队列排序：高优先级优先，先来后到
        self.waiting_queue.sort(key=lambda r: (
            -self._priority_score(r), # 大的分数排前
            r.waitingTime or now      # 时间早的排前
        ))
        
        while len(self.serving_queue) < limit and self.waiting_queue:
            lucky = self.waiting_queue[0]
            self._promote_waiting_room(lucky)

    # -------------------------------------------------------------------------
    # 6. 公共 API (External API)
    # -------------------------------------------------------------------------

    def _add_request_to_queue(self, room: Room):
        """通用入口：添加请求并调度"""
        req = RoomRequest(
            roomId=room.id,
            fanSpeed=room.fan_speed,
            mode=room.ac_mode,
            targetTemp=room.target_temp
        )
        now = datetime.utcnow()
        
        # 清理旧数据
        self._remove_request(self.serving_queue, room.id)
        self._remove_request(self.waiting_queue, room.id)

        # 初始放入服务队列，让 _schedule_queues 去决定去留
        # 这里先假设放入服务队列，并记录开始时间
        # 注意：这里暂不写入DB状态，交由 promote/demote 处理
        # 但为了让调度器识别，我们需要先 append
        
        if len(self.serving_queue) < self._capacity():
            # 有空位，直接进
            req.servingTime = now
            self.serving_queue.append(req)
            self._mark_serving_db(room.id, now, room.current_temp)
        else:
            # 没空位，进等待
            req.waitingTime = now
            self.waiting_queue.append(req)
            self._mark_waiting_db(room.id, now)
            
        self._schedule_queues(force=True)

    def _mark_serving_db(self, rid, time, temp):
        from ..extensions import db
        db.session.query(Room).filter(Room.id == rid).update({
            "serving_start_time": time,
            "billing_start_temp": float(temp) if temp is not None else 25.0,
            "waiting_start_time": None
        })
        db.session.commit()

    def _mark_waiting_db(self, rid, time):
        from ..extensions import db
        db.session.query(Room).filter(Room.id == rid).update({
            "waiting_start_time": time,
            "serving_start_time": None,
            "billing_start_temp": None
        })
        db.session.commit()

    # --- 外部调用接口 ---

    def PowerOn(self, RoomId: int, CurrentRoomTemp: float | None) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room: return "错误: 房间不存在"
            if room.ac_on: return "已开启"
            
            now = datetime.utcnow()
            temp = float(CurrentRoomTemp) if CurrentRoomTemp is not None else (float(room.current_temp) if room.current_temp else 25.0)
            
            # 更新DB
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_on": True,
                "current_temp": temp,
                "ac_session_start": now,
                "last_temp_update": now, # 关键初始化
                "cooling_paused": False
            })
            db.session.commit()
            
            # 刷新对象
            room.ac_on = True
            room.current_temp = temp
            room.last_temp_update = now
            
            self._add_request_to_queue(room)
            return "空调已开启"

    def PowerOff(self, RoomId: int) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "空调未开启"
            
            now = datetime.utcnow()
            
            # 1. 结算
            self._updateRoomTemperature(room, force_update=True)
            self._settle_current_service_period(room, now, "POWER_OFF")
            
            # 2. 移除队列
            self._remove_request(self.serving_queue, room.id)
            self._remove_request(self.waiting_queue, room.id)
            
            # 3. 重置DB
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_on": False,
                "ac_session_start": None,
                "serving_start_time": None,
                "waiting_start_time": None,
                "billing_start_temp": None,
                "cooling_paused": False,
                "pause_start_temp": None
            })
            db.session.commit()
            
            self._schedule_queues(force=True)
            return "空调已关闭"

    def ChangeTemp(self, RoomId: int, TargetTemp: float) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "错误: 未开机"
            
            # 校验
            mode = room.ac_mode or "COOLING"
            min_t = current_app.config.get(f"{mode}_MIN_TEMP", 16.0)
            max_t = current_app.config.get(f"{mode}_MAX_TEMP", 30.0)
            if not (min_t <= TargetTemp <= max_t):
                return f"温度超限 ({min_t}-{max_t})"

            # 更新DB
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "target_temp": TargetTemp
            })
            db.session.commit()
            
            room.target_temp = TargetTemp
            # 这里的更新不需要立刻结算，因为费率没变，只影响未来的停止点
            # 但如果处于待机，需要唤醒
            if room.cooling_paused:
                db.session.query(Room).filter(Room.id == room.id).update({
                    "cooling_paused": False,
                    "pause_start_temp": None
                })
                db.session.commit()
                self._add_request_to_queue(room)
                
            return "温度已设定"

    def ChangeSpeed(self, RoomId: int, FanSpeed: str) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room or not room.ac_on: return "错误: 未开机"
            
            new_speed = FanSpeed.upper()
            if room.fan_speed == new_speed: return "风速未变"
            
            now = datetime.utcnow()
            
            # 切分账单：因为温变速率变了，虽然单价没变，但在某些模型中费率可能跟风速挂钩
            # 即使费率不变，为了精确记录哪个风速段用了多少度，建议切分
            if room.serving_start_time:
                self._updateRoomTemperature(room, force_update=True)
                self._settle_current_service_period(room, now, "CHANGE_SPEED")
                # 重置计费点
                self._mark_serving_db(room.id, now, room.current_temp)

            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "fan_speed": new_speed
            })
            db.session.commit()
            room.fan_speed = new_speed
            
            # 重新加入队列以触发优先级检查
            self._add_request_to_queue(room)
            return "风速已调整"

    def ChangeMode(self, RoomId: int, Mode: str) -> str:
        with self._lock:
            room = self.room_service.getRoomById(RoomId)
            if not room: return "错误"
            
            new_mode = Mode.upper()
            if new_mode == room.ac_mode: return "模式未变"
            
            now = datetime.utcnow()
            
            # 必切分账单
            if room.serving_start_time:
                self._updateRoomTemperature(room, force_update=True)
                self._settle_current_service_period(room, now, "CHANGE_MODE")
                self._mark_serving_db(room.id, now, room.current_temp)

            default_target = 22.0 if new_mode == "HEATING" else 25.0
            
            from ..extensions import db
            db.session.query(Room).filter(Room.id == room.id).update({
                "ac_mode": new_mode,
                "target_temp": default_target
            })
            db.session.commit()
            
            room.ac_mode = new_mode
            room.target_temp = default_target
            
            self._add_request_to_queue(room)
            return "模式已切换"

    # -------------------------------------------------------------------------
    # 7. 监控与模拟 (Monitoring)
    # -------------------------------------------------------------------------

    def simulateTemperatureUpdate(self) -> dict:
        """定时任务每秒调用"""
        updated = 0
        with self._lock:
            from ..models import Room
            rooms = Room.query.filter_by(ac_on=True).all()
            # 先更新所有房间的温度
            for room in rooms:
                old = room.current_temp
                self._updateRoomTemperature(room)
                if abs((room.current_temp or 0) - (old or 0)) > 0.001:
                    updated += 1
            
            # 温度更新完成后再进行调度，避免在温度更新过程中队列状态变化
            self._schedule_queues() # 顺便检查是否需要轮转
        return {"updated": updated}

    def RequestState(self, RoomId: int) -> dict:
        """状态查询"""
        room = self.room_service.getRoomById(RoomId)
        if not room: return {}
        
        # 实时费用预估：getCurrentFeeDetail 已经包含了历史费用和当前未结算费用
        # 不需要再单独计算 pending_cost，避免重复计算
        total_cost = 0.0
        try:
            from ..services import bill_service
            data = bill_service.getCurrentFeeDetail(room)
            # total 已经包含了房费 + 历史空调费 + 当前未结算空调费
            total_cost = data.get("total", 0.0)
        except Exception as e:
            print(f"[Scheduler] RequestState 获取费用失败: {e}")
            pass

        qs = "IDLE"
        if room.cooling_paused: qs = "PAUSED"
        elif any(r.roomId == room.id for r in self.serving_queue): qs = "SERVING"
        elif any(r.roomId == room.id for r in self.waiting_queue): qs = "WAITING"

        # 同时返回下划线命名（供测试代码使用）和驼峰命名（供前端使用）
        current_temp_val = round(float(room.current_temp or 0), 2)
        target_temp_val = float(room.target_temp or 25)
        return {
            "room_id": room.id,
            "ac_on": room.ac_on,
            "current_temp": current_temp_val,
            "currentTemp": current_temp_val,  # 驼峰命名兼容
            "target_temp": target_temp_val,
            "targetTemp": target_temp_val,  # 驼峰命名兼容
            "mode": room.ac_mode,
            "ac_mode": room.ac_mode,  # 兼容字段
            "fan_speed": room.fan_speed,
            "fanSpeed": room.fan_speed,  # 驼峰命名兼容
            "state": qs,
            "queueState": qs,  # 前端期望的字段名
            "queue_state": qs,  # 兼容字段
            "total_cost": total_cost
        }
    
    def getScheduleStatus(self):
        """调试面板数据"""
        with self._lock:
            now = datetime.utcnow()
            serving_list = []
            for r in self.serving_queue:
                serving_sec = self._get_simulated_duration(r.servingTime, now)
                serving_list.append({
                    "roomId": r.roomId,
                    "fanSpeed": r.fanSpeed or "MEDIUM",
                    "servingSeconds": serving_sec,
                    "totalSeconds": serving_sec  # 兼容字段
                })
            
            waiting_list = []
            for r in self.waiting_queue:
                waiting_sec = self._get_simulated_duration(r.waitingTime, now)
                waiting_list.append({
                    "roomId": r.roomId,
                    "fanSpeed": r.fanSpeed or "MEDIUM",
                    "waitingSeconds": waiting_sec
                })
            
            return {
                "capacity": self._capacity(),
                "timeSlice": self._time_slice(),
                "servingQueue": serving_list,
                "waitingQueue": waiting_list
            }