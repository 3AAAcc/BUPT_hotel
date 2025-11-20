from typing import Optional

from ..models import Room
from .room_service import RoomService


class ACService:
    def __init__(self, room_service: RoomService):
        self.room_service = room_service

    def getACByRoomId(self, room_id: int) -> Optional[Room]:
        return self.room_service.getRoomById(room_id)

