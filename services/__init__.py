from .ac_schedule_service import ACScheduleService
from .ac_service import ACService
from .bill_detail_service import BillDetailService
from .bill_service import BillService
from .customer_service import CustomerService
from .hotel_service import HotelService
from .room_service import RoomService

room_service = RoomService()
customer_service = CustomerService()
bill_detail_service = BillDetailService()
bill_service = BillService()
ac_schedule_service = ACScheduleService(room_service, bill_detail_service)
ac_service = ACService(room_service)
hotel_service = HotelService(
    room_service=room_service,
    customer_service=customer_service,
    bill_service=bill_service,
    bill_detail_service=bill_detail_service,
)

