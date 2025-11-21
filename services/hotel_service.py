from datetime import datetime
from typing import Dict, List, Optional

from ..models import Customer, Room
from ..vo.checkout_response import BillResponse, CheckoutResponse, DetailBill
from .bill_detail_service import BillDetailService
from .bill_service import BillService
from .customer_service import CustomerService
from .room_service import RoomService


class HotelService:
    def __init__(
        self,
        room_service: RoomService,
        customer_service: CustomerService,
        bill_service: BillService,
        bill_detail_service: BillDetailService,
    ):
        self.room_service = room_service
        self.customer_service = customer_service
        self.bill_service = bill_service
        self.bill_detail_service = bill_detail_service

    def getAvailableRooms(self) -> List[Room]:
        return [
            room
            for room in self.room_service.getAllRooms()
            if room.status == "AVAILABLE"
        ]

    def checkIn(self, payload: Dict) -> str:
        room_id = payload.get("roomId")
        room = self.room_service.getRoomById(room_id)
        if room is None:
            raise ValueError("房间不存在")
        if room.status != "AVAILABLE":
            raise ValueError("房间当前不可用")
        # 如果房间空调已开启（可能是管理员开启的），先关闭空调并清理入住前的账单详情
        if room.ac_on:
            from ..services import ac_schedule_service
            # 关闭空调（会生成customer_id为None的账单详情）
            ac_schedule_service.stopAC(room_id)
            # 清理入住前产生的账单详情（customer_id为None的）
            from ..models import BillDetail
            from ..extensions import db
            BillDetail.query.filter(
                BillDetail.room_id == room_id,
                BillDetail.customer_id.is_(None)
            ).delete()
            db.session.commit()

        customer = Customer(
            name=payload.get("name"),
            id_card=payload.get("idCard"),
            phone_number=payload.get("phoneNumber"),
            current_room_id=room_id,
            check_in_time=datetime.utcnow(),
            status="CHECKED_IN",
        )
        self.customer_service.saveCustomer(customer)
        room.status = "OCCUPIED"
        room.customer_name = customer.name
        room.check_in_time = customer.check_in_time
        self.room_service.updateRoom(room)
        return "入住成功"

    def checkOut(self, room_id: int) -> CheckoutResponse:
        customer = self.customer_service.getCustomerByRoomId(room_id)
        if customer is None:
            # 如果没有入住记录，检查房间状态
            room = self.room_service.getRoomById(room_id)
            if room and room.ac_on:
                # 如果空调开启但没有入住记录，可能是管理员开启的，关闭空调并清理状态
                from ..services import ac_schedule_service
                try:
                    ac_schedule_service.stopAC(room_id)
                except:
                    pass
                room.status = "AVAILABLE"
                room.customer_name = None
                room.ac_on = False
                room.ac_session_start = None
                self.room_service.updateRoom(room)
            raise ValueError("房间没有入住记录，无法办理退房")

        check_out_time = datetime.utcnow()
        customer.check_out_time = check_out_time
        customer.status = "CHECKED_OUT"
        customer.current_room_id = None
        self.customer_service.updateCustomer(customer)

        room = self.room_service.getRoomById(room_id)
        room.status = "AVAILABLE"
        room.customer_name = None
        room.ac_on = False
        room.ac_session_start = None
        self.room_service.updateRoom(room)

        details = self.bill_detail_service.getBillDetailsByRoomIdAndTimeRange(
            room_id=room_id,
            start=customer.check_in_time,
            end=check_out_time,
            customer_id=customer.id,  # 只计算该客户的账单详情，排除管理员开启的空调产生的账单
        )
        bill = self.bill_service.createAndSettleBill(details, customer, room)

        from ..vo.checkout_response import CustomerInfo
        
        checkout_response = CheckoutResponse()
        checkout_response.customer = CustomerInfo(
            name=customer.name,
            idCard=customer.id_card,
            phoneNumber=customer.phone_number,
        )
        checkout_response.detailBill = [
            DetailBill(
                roomId=detail.room_id,
                startTime=detail.start_time.isoformat(),
                endTime=detail.end_time.isoformat(),
                duration=detail.duration,
                fanSpeed=detail.fan_speed,
                currentFee=detail.cost,
                fee=detail.cost,
            )
            for detail in details
        ]
        checkout_response.bill = BillResponse(
            roomId=bill.room_id,
            checkinTime=bill.check_in_time.date().isoformat(),
            checkoutTime=bill.check_out_time.date().isoformat(),
            duration=str(bill.stay_days),
            roomFee=bill.room_fee,
            acFee=bill.ac_total_fee,
        )
        return checkout_response

