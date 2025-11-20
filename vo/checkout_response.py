from dataclasses import dataclass, field
from typing import List


@dataclass
class DetailBill:
    roomId: int
    startTime: str
    endTime: str
    duration: int
    fanSpeed: str
    currentFee: float
    fee: float


@dataclass
class BillResponse:
    roomId: int
    checkinTime: str
    checkoutTime: str
    duration: str
    roomFee: float
    acFee: float


@dataclass
class CheckoutResponse:
    detailBill: List[DetailBill] = field(default_factory=list)
    bill: BillResponse | None = None

    def to_dict(self) -> dict:
        return {
            "detailBill": [detail.__dict__ for detail in self.detailBill],
            "bill": self.bill.__dict__ if self.bill else None,
        }

