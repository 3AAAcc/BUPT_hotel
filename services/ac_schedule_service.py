from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from flask import current_app

from ..models import Room, RoomRequest
from .bill_detail_service import BillDetailService
from .room_service import RoomService


class ACScheduleService:
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
        fan_speed = (fan_speed or "LOW").upper()
        if fan_speed == "HIGH":
            return current_app.config["BILLING_AC_RATE_HIGH"]
        if fan_speed == "MEDIUM":
            return current_app.config["BILLING_AC_RATE_MEDIUM"]
        return current_app.config["BILLING_AC_RATE_LOW"]

    def _priority_score(self, request: RoomRequest) -> int:
        score_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return score_map.get((request.fanSpeed or "LOW").upper(), 1)

    def _elapsed_seconds(self, source: Optional[datetime], now: datetime) -> float:
        if not source:
            return 0.0
        return max(0.0, (now - source).total_seconds())

    def _remove_from_queue(
        self, queue: List[RoomRequest], room_id: int
    ) -> Optional[RoomRequest]:
        for idx, req in enumerate(queue):
            if req.roomId == room_id:
                return queue.pop(idx)
        return None

    def _mark_room_serving(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if not room:
            return
        room.serving_start_time = started_at
        room.waiting_start_time = None
        self.room_service.updateRoom(room)

    def _mark_room_waiting(self, room_id: int, started_at: datetime) -> None:
        room = self.room_service.getRoomById(room_id)
        if not room:
            return
        room.waiting_start_time = started_at
        room.serving_start_time = None
        self.room_service.updateRoom(room)

    def _remove_request(self, room_id: int) -> None:
        self._remove_from_queue(self.serving_queue, room_id)
        self._remove_from_queue(self.waiting_queue, room_id)

    def _sort_waiting_queue(self) -> None:
        if not self.waiting_queue:
            return
        now = datetime.utcnow()
        self.waiting_queue.sort(
            key=lambda r: (
                -self._priority_score(r),
                r.waitingTime or now,
                r.roomId,
            )
        )

    def _promote_waiting_room(self) -> None:
        if not self.waiting_queue:
            return
        capacity = self._capacity()
        if len(self.serving_queue) >= capacity:
            return
        self._sort_waiting_queue()
        now = datetime.utcnow()
        while self.waiting_queue and len(self.serving_queue) < capacity:
            promoted = self.waiting_queue.pop(0)
            promoted.servingTime = now
            promoted.waitingTime = None
            self.serving_queue.append(promoted)
            self._mark_room_serving(promoted.roomId, now)

    def _move_to_waiting(self, request: RoomRequest, timestamp: datetime) -> None:
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
        if not self.waiting_queue or not self.serving_queue:
            return
        capacity = self._capacity()
        if len(self.serving_queue) < capacity:
            return
        now = datetime.utcnow()
        self._sort_waiting_queue()
        while self.waiting_queue:
            lowest_serving = min(
                self.serving_queue,
                key=lambda req: (
                    self._priority_score(req),
                    req.servingTime or now,
                    req.roomId,
                ),
            )
            candidate = self.waiting_queue[0]
            candidate_priority = self._priority_score(candidate)
            lowest_priority = self._priority_score(lowest_serving)
            waiting_elapsed = self._elapsed_seconds(candidate.waitingTime, now)

            should_swap = False
            if candidate_priority > lowest_priority:
                should_swap = True
            elif candidate_priority == lowest_priority:
                if force or waiting_elapsed >= self._time_slice():
                    should_swap = True

            if not should_swap:
                break

            promoted = self.waiting_queue.pop(0)
            demoted = self._remove_from_queue(self.serving_queue, lowest_serving.roomId)
            if demoted is None:
                break
            self._move_to_waiting(demoted, now)
            self._move_to_serving(promoted, now)
            self._sort_waiting_queue()

    def _rebalance_queues(self, *, force_rotation: bool = False) -> None:
        self._promote_waiting_room()
        self._rotate_time_slice(force=force_rotation)

    def startAC(self, room_id: int, current_temp: float | None) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if room.ac_on:
            return "房间空调已开启"

        now = datetime.utcnow()
        if current_temp is not None:
            room.current_temp = current_temp
        room.ac_on = True
        room.ac_session_start = now
        room.target_temp = room.target_temp or current_app.config["HOTEL_DEFAULT_TEMP"]
        room.status = "OCCUPIED" if room.status == "AVAILABLE" else room.status

        request = RoomRequest(
            roomId=room.id,
            fanSpeed=room.fan_speed,
            mode=room.ac_mode,
            targetTemp=room.target_temp,
        )

        if len(self.serving_queue) < self._capacity():
            request.servingTime = now
            self.serving_queue.append(request)
            self._mark_room_serving(room.id, now)
        else:
            request.waitingTime = now
            self.waiting_queue.append(request)
            self._mark_room_waiting(room.id, now)
            self._rebalance_queues()

        self.room_service.updateRoom(room)
        return "空调已开启并进入调度"

    def stopAC(self, room_id: int) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if not room.ac_on:
            raise ValueError("房间空调尚未开启")

        now = datetime.utcnow()
        start_time = room.ac_session_start or now
        duration_minutes = max(1, int((now - start_time).total_seconds() // 60))
        rate = self._rate_by_fan_speed(room.fan_speed)
        cost = rate * duration_minutes

        self.bill_detail_service.createBillDetail(
            room_id=room.id,
            ac_mode=room.ac_mode,
            fan_speed=room.fan_speed,
            start_time=start_time,
            end_time=now,
            rate=rate,
            cost=cost,
        )

        room.ac_on = False
        room.ac_session_start = None
        room.waiting_start_time = None
        room.serving_start_time = None
        self.room_service.updateRoom(room)

        self._remove_request(room.id)
        self._rebalance_queues()
        return "空调已关闭"

    def changeTemp(self, room_id: int, target_temp: float) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if not room.ac_on:
            raise ValueError("请先开启空调")
        room.target_temp = target_temp
        self.room_service.updateRoom(room)
        for queue in (self.serving_queue, self.waiting_queue):
            for req in queue:
                if req.roomId == room_id:
                    req.targetTemp = target_temp
        return "目标温度已更新"

    def changeFanSpeed(self, room_id: int, fan_speed: str) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        normalized = fan_speed.upper()
        if normalized not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("无效风速")
        room.fan_speed = normalized
        self.room_service.updateRoom(room)

        for queue in (self.serving_queue, self.waiting_queue):
            for req in queue:
                if req.roomId == room_id:
                    req.fanSpeed = normalized
        self._rebalance_queues(force_rotation=True)
        return "风速已更新"

    def getRoomACAccumulatedData(self, room_id: int) -> dict:
        from ..models import BillDetail

        details = BillDetail.query.filter_by(room_id=room_id).all()
        total_duration = sum(detail.duration for detail in details)
        total_cost = sum(detail.cost for detail in details)
        return {"totalDuration": total_duration, "totalCost": total_cost}

    def getRoomACStatus(self, room_id: int) -> dict:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        status = room.to_dict()
        now = datetime.utcnow()
        queue_state = "IDLE"
        waiting_seconds = 0.0
        serving_seconds = 0.0
        queue_position = None
        for req in self.serving_queue:
            if req.roomId == room_id:
                queue_state = "SERVING"
                serving_seconds = self._elapsed_seconds(req.servingTime, now)
                break
        else:
            for idx, req in enumerate(self.waiting_queue):
                if req.roomId == room_id:
                    queue_state = "WAITING"
                    waiting_seconds = self._elapsed_seconds(req.waitingTime, now)
                    queue_position = idx + 1
                    break
        status.update(
            {
                "queueState": queue_state,
                "waitingSeconds": waiting_seconds,
                "servingSeconds": serving_seconds,
                "queuePosition": queue_position,
            }
        )
        return status

    def getScheduleStatus(self) -> dict:
        now = datetime.utcnow()

        def _to_payload(queue: List[RoomRequest]) -> List[Dict[str, object]]:
            payload = []
            for req in queue:
                payload.append(
                    {
                        "roomId": req.roomId,
                        "fanSpeed": req.fanSpeed,
                        "mode": req.mode,
                        "targetTemp": req.targetTemp,
                        "waitingSeconds": self._elapsed_seconds(req.waitingTime, now),
                        "servingSeconds": self._elapsed_seconds(req.servingTime, now),
                    }
                )
            return payload

        return {
            "capacity": self._capacity(),
            "servingQueue": _to_payload(self.serving_queue),
            "waitingQueue": _to_payload(self.waiting_queue),
        }

    def forceTimeSliceCheck(self) -> dict:
        self._rebalance_queues(force_rotation=True)
        return self.getScheduleStatus()

    def simulateTemperatureUpdate(self) -> dict:
        rooms = self.room_service.getAllRooms()
        updated = 0
        for room in rooms:
            current_temp = room.current_temp or room.default_temp or 0.0
            new_temp = current_temp
            if room.ac_on and room.target_temp is not None:
                diff = room.target_temp - current_temp
                if abs(diff) < 0.1:
                    new_temp = room.target_temp
                else:
                    step = max(min(diff, 0.5), -0.5)
                    new_temp = current_temp + step
            else:
                if room.default_temp is None:
                    continue
                diff = room.default_temp - current_temp
                if abs(diff) < 0.1:
                    continue
                step = max(min(diff, 0.3), -0.3)
                new_temp = current_temp + step
            if abs(new_temp - current_temp) < 1e-6:
                continue
            room.current_temp = round(new_temp, 2)
            self.room_service.updateRoom(room)
            updated += 1
        return {"message": "温度已模拟更新", "updatedRooms": updated}

    def getServingQueue(self) -> List[RoomRequest]:
        return list(self.serving_queue)

    def getWaitingQueue(self) -> List[RoomRequest]:
        return list(self.waiting_queue)

