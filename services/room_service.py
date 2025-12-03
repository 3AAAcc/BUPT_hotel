from typing import List, Optional

from ..extensions import db
from ..models import Room


class RoomService:
    def getAllRooms(self) -> List[Room]:
        return Room.query.order_by(Room.id).all()

    def getRoomById(self, room_id: int) -> Optional[Room]:
        return Room.query.get(room_id)

    def updateRoom(self, room: Room) -> Room:
        try:
            # 使用 merge 方法，如果对象已存在则更新，不存在则添加
            # 这样可以避免 "expected to update 1 row(s); 0 were matched" 错误
            merged_room = db.session.merge(room)
            db.session.commit()
            return merged_room
        except Exception as e:
            # 如果更新失败，回滚并重新尝试
            db.session.rollback()
            try:
                # 重新从数据库获取房间对象，避免使用过期的对象
                fresh_room = self.getRoomById(room.id)
                if fresh_room:
                    # 更新字段
                    for key, value in room.__dict__.items():
                        if not key.startswith('_') and key != 'id' and hasattr(fresh_room, key):
                            setattr(fresh_room, key, value)
                    db.session.add(fresh_room)
                    db.session.commit()
                    return fresh_room
                else:
                    # 如果房间不存在，抛出异常
                    raise ValueError(f"房间 {room.id} 不存在")
            except Exception as e2:
                db.session.rollback()
                raise e2

    def getAvailableRoomIds(self) -> List[int]:
        return [room.id for room in self.getAllRooms() if room.status == "AVAILABLE"]

    def ensureRoomsInitialized(self, total_count: int, default_temp: float) -> None:
        existing = {room.id for room in self.getAllRooms()}
        need_create = [idx for idx in range(1, total_count + 1) if idx not in existing]
        if not need_create:
            return
        for room_id in need_create:
            room = Room(
                id=room_id,
                status="AVAILABLE",
                current_temp=default_temp,
                target_temp=default_temp,
                default_temp=default_temp,
                fan_speed="MEDIUM",
                daily_rate=100.0,  # 默认日房费 100元/天
            )
            db.session.add(room)
        db.session.commit()

