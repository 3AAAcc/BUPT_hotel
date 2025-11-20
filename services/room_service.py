from typing import List, Optional

from ..extensions import db
from ..models import Room


class RoomService:
    """房间业务逻辑，方法命名保持与原 Java 版本一致。"""

    def getAllRooms(self) -> List[Room]:
        return Room.query.order_by(Room.id).all()

    def getRoomById(self, room_id: int) -> Optional[Room]:
        return Room.query.get(room_id)

    def updateRoom(self, room: Room) -> Room:
        db.session.add(room)
        db.session.commit()
        return room

    def getAvailableRoomIds(self) -> List[int]:
        return [room.id for room in self.getAllRooms() if room.status == "AVAILABLE"]

    def ensureRoomsInitialized(self, total_count: int, default_temp: float) -> None:
        """初始化房间表数据，避免空表导致的接口异常。"""
        existing = {room.id for room in self.getAllRooms()}
        need_create = [idx for idx in range(1, total_count + 1) if idx not in existing]
        if not need_create:
            return
        for room_id in need_create:
            room = Room(
                id=room_id,
                status="AVAILABLE",
                current_temp=default_temp + 7,
                target_temp=default_temp,
                default_temp=default_temp,
                fan_speed="LOW",
            )
            db.session.add(room)
        db.session.commit()

