from __future__ import annotations

from datetime import datetime
from typing import List

from flask import current_app

from ..extensions import db
from ..models import Room, RoomRequest
from .bill_detail_service import BillDetailService
from .room_service import RoomService


class ACScheduleService:
    def __init__(self, room_service: RoomService, bill_detail_service: BillDetailService):
        self.room_service = room_service
        self.bill_detail_service = bill_detail_service
        self.serving_queue: List[RoomRequest] = []
        self.waiting_queue: List[RoomRequest] = []

    # === 基础能力 ===
    def _rate_by_fan_speed(self, fan_speed: str) -> float:
        fan_speed = (fan_speed or "LOW").upper()
        if fan_speed == "HIGH":
            return current_app.config["BILLING_AC_RATE_HIGH"]
        if fan_speed == "MEDIUM":
            return current_app.config["BILLING_AC_RATE_MEDIUM"]
        return current_app.config["BILLING_AC_RATE_LOW"]

    def _remove_request(self, room_id: int) -> None:
        self.serving_queue = [req for req in self.serving_queue if req.roomId != room_id]
        self.waiting_queue = [req for req in self.waiting_queue if req.roomId != room_id]

    def _promote_waiting_room(self) -> None:
        if not self.waiting_queue:
            return
        if len(self.serving_queue) >= current_app.config["HOTEL_AC_TOTAL_COUNT"]:
            return
        promoted = self.waiting_queue.pop(0)
        promoted.servingTime = datetime.utcnow()
        self.serving_queue.append(promoted)
        room = self.room_service.getRoomById(promoted.roomId)
        if room:
            room.serving_start_time = promoted.servingTime
            room.waiting_start_time = None
            self.room_service.updateRoom(room)

    # === 对应原 Java 的公开方法 ===
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
        room.waiting_start_time = now
        room.target_temp = room.target_temp or current_app.config["HOTEL_DEFAULT_TEMP"]
        room.status = "OCCUPIED" if room.status == "AVAILABLE" else room.status

        request = RoomRequest(
            roomId=room.id,
            fanSpeed=room.fan_speed,
            mode=room.ac_mode,
            targetTemp=room.target_temp,
        )

        if len(self.serving_queue) < current_app.config["HOTEL_AC_TOTAL_COUNT"]:
            request.servingTime = now
            room.serving_start_time = now
            self.serving_queue.append(request)
        else:
            request.waitingTime = now
            self.waiting_queue.append(request)
        self.room_service.updateRoom(room)
        return "空调开启成功"

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
        self._promote_waiting_room()
        return "空调已关闭"

    def changeTemp(self, room_id: int, target_temp: float) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if not room.ac_on:
            raise ValueError("请先开启空调")
        room.target_temp = target_temp
        self.room_service.updateRoom(room)
        return "目标温度已更新"

    def changeFanSpeed(self, room_id: int, fan_speed: str) -> str:
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if fan_speed.upper() not in {"LOW", "MEDIUM", "HIGH"}:
            raise ValueError("无效风速")
        room.fan_speed = fan_speed.upper()
        self.room_service.updateRoom(room)

        for queue in (self.serving_queue, self.waiting_queue):
            for req in queue:
                if req.roomId == room_id:
                    req.fanSpeed = room.fan_speed
        self.waiting_queue.sort(key=lambda r: (-self._priority_score(r), r.roomId))
        return "风速已更新"

    def _priority_score(self, request: RoomRequest) -> int:
        score_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        return score_map.get(request.fanSpeed.upper(), 1)

    def getRoomACAccumulatedData(self, room_id: int) -> dict:
        from ..models import BillDetail

        details = BillDetail.query.filter_by(room_id=room_id).all()
        total_duration = sum(detail.duration for detail in details)
        total_cost = sum(detail.cost for detail in details)
        return {"totalDuration": total_duration, "totalCost": total_cost}

    def getServingQueue(self) -> List[RoomRequest]:
        return list(self.serving_queue)

    def getWaitingQueue(self) -> List[RoomRequest]:
        return list(self.waiting_queue)

