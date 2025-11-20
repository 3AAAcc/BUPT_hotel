from datetime import datetime
from typing import List

from ..extensions import db
from ..models import BillDetail


class BillDetailService:
    def createBillDetail(
        self,
        room_id: int,
        ac_mode: str,
        fan_speed: str,
        start_time: datetime,
        end_time: datetime,
        rate: float,
        cost: float,
    ) -> BillDetail:
        detail = BillDetail(
            room_id=room_id,
            ac_mode=ac_mode,
            fan_speed=fan_speed,
            request_time=start_time,
            start_time=start_time,
            end_time=end_time,
            duration=int((end_time - start_time).total_seconds() // 60 or 1),
            rate=rate,
            cost=cost,
        )
        db.session.add(detail)
        db.session.commit()
        return detail

    def getBillDetailsByRoomIdAndTimeRange(
        self, room_id: int, start: datetime, end: datetime
    ) -> List[BillDetail]:
        return (
            BillDetail.query.filter(
                BillDetail.room_id == room_id,
                BillDetail.start_time >= start,
                BillDetail.end_time <= end,
            )
            .order_by(BillDetail.start_time)
            .all()
        )

