from datetime import datetime
from typing import List

from flask import current_app

from ..extensions import db
from ..models import Bill, BillDetail, Customer, Room


class BillService:
    def createAndSettleBill(
        self, bill_details: List[BillDetail], customer: Customer, room: Room
    ) -> Bill:
        if not customer.check_in_time:
            customer.check_in_time = datetime.utcnow()
        if not customer.check_out_time:
            customer.check_out_time = datetime.utcnow()

        stay_days = max(
            1, (customer.check_out_time.date() - customer.check_in_time.date()).days or 1
        )
        room_fee = stay_days * current_app.config["BILLING_ROOM_RATE"]
        ac_fee = sum(detail.cost for detail in bill_details)

        bill = Bill(
            room_id=room.id,
            check_in_time=customer.check_in_time,
            check_out_time=customer.check_out_time,
            stay_days=stay_days,
            room_fee=room_fee,
            ac_total_fee=ac_fee,
            total_amount=room_fee + ac_fee,
        )
        db.session.add(bill)
        db.session.commit()
        return bill

