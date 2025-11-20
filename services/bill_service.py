from datetime import datetime
from typing import Dict, List, Optional

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
            customer_id=customer.id,
            check_in_time=customer.check_in_time,
            check_out_time=customer.check_out_time,
            stay_days=stay_days,
            room_fee=room_fee,
            ac_total_fee=ac_fee,
            total_amount=room_fee + ac_fee,
            status="UNPAID",
        )
        db.session.add(bill)
        db.session.commit()
        return bill

    def getAllBills(self) -> List[Bill]:
        return Bill.query.order_by(Bill.create_time.desc()).all()

    def getBillById(self, bill_id: int) -> Optional[Bill]:
        return Bill.query.get(bill_id)

    def getBillsByRoomId(self, room_id: int) -> List[Bill]:
        return (
            Bill.query.filter_by(room_id=room_id)
            .order_by(Bill.create_time.desc())
            .all()
        )

    def getBillsByCustomerId(self, customer_id: int) -> List[Bill]:
        return (
            Bill.query.filter_by(customer_id=customer_id)
            .order_by(Bill.create_time.desc())
            .all()
        )

    def getUnpaidBills(self) -> List[Bill]:
        return (
            Bill.query.filter_by(status="UNPAID")
            .order_by(Bill.create_time.desc())
            .all()
        )

    def markBillPaid(self, bill_id: int) -> Bill:
        bill = self.getBillById(bill_id)
        if bill is None:
            raise ValueError("账单不存在")
        if bill.status == "CANCELLED":
            raise ValueError("账单已取消，无法支付")
        if bill.status == "PAID":
            return bill
        bill.status = "PAID"
        bill.paid_time = datetime.utcnow()
        db.session.add(bill)
        db.session.commit()
        return bill

    def cancelBill(self, bill_id: int) -> Bill:
        bill = self.getBillById(bill_id)
        if bill is None:
            raise ValueError("账单不存在")
        if bill.status == "PAID":
            raise ValueError("账单已支付，无法取消")
        if bill.status == "CANCELLED":
            return bill
        bill.status = "CANCELLED"
        bill.cancelled_time = datetime.utcnow()
        db.session.add(bill)
        db.session.commit()
        return bill

    def markBillPrinted(self, bill_id: int) -> Bill:
        bill = self.getBillById(bill_id)
        if bill is None:
            raise ValueError("账单不存在")
        bill.print_status = "PRINTED"
        bill.print_time = datetime.utcnow()
        db.session.add(bill)
        db.session.commit()
        return bill

    def buildPrintablePayload(
        self, bill: Bill, details: List[BillDetail]
    ) -> Dict[str, object]:
        return {
            "bill": bill.to_dict(),
            "detailItems": [
                {
                    "startTime": detail.start_time.isoformat() if detail.start_time else None,
                    "endTime": detail.end_time.isoformat() if detail.end_time else None,
                    "durationMinutes": detail.duration,
                    "fanSpeed": detail.fan_speed,
                    "mode": detail.ac_mode,
                    "rate": detail.rate,
                    "cost": detail.cost,
                }
                for detail in details
            ],
            "totals": {
                "acDurationMinutes": sum(detail.duration for detail in details),
                "acFee": sum(detail.cost for detail in details),
                "roomFee": bill.room_fee,
                "grandTotal": bill.total_amount,
            },
        }

