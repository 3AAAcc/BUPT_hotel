from typing import Optional

from ..models import Room
from .room_service import RoomService


class ACService:
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def getACByRoomId(self, room_id: int) -> Optional[Room]:
        """在新架构中直接复用房间状态作为空调信息。"""
        return self.room_service.getRoomById(room_id)

