from datetime import datetime
from typing import Dict, List, Optional

from flask import current_app

from ..extensions import db
from ..models import ACFeeBill, AccommodationFeeBill, Customer, DetailRecord, Room


class AccommodationFeeBillService:

    def createAndSettleBill(
        self, bill_details: List[DetailRecord], customer: Customer, room: Room
    ) -> AccommodationFeeBill:
        if not customer.check_in_time:
            customer.check_in_time = datetime.utcnow()
        if not customer.check_out_time:
            customer.check_out_time = datetime.utcnow()

        stay_days = max(
            1, (customer.check_out_time.date() - customer.check_in_time.date()).days or 1
        )
        # 兜底费率
        daily_rate = 100.0
        if room.daily_rate is not None and room.daily_rate > 0:
            daily_rate = room.daily_rate
        else:
            daily_rate = current_app.config.get("BILLING_ROOM_RATE", 100.0)

        charge_units = stay_days
        if current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE"):
            cycle_days = sum(1 for d in bill_details if getattr(d, 'detail_type', 'AC') == 'POWER_OFF_CYCLE')
            if bill_details:
                cycle_days = max(1, cycle_days)
            else:
                cycle_days = 0
            charge_units = max(stay_days, cycle_days)

        room_fee = float(charge_units) * float(daily_rate)
        
        ac_fee_bill = ACFeeBill(room_id=room.id, detail_records=bill_details)
        ac_fee = ac_fee_bill.calculate_AC_Fee()

        bill = AccommodationFeeBill(
            room_id=room.id,
            customer_id=customer.id,
            check_in_time=customer.check_in_time,
            check_out_time=customer.check_out_time,
            stay_days=charge_units,
            room_fee=room_fee,
            ac_total_fee=ac_fee,
            total_amount=room_fee + ac_fee,
            status="UNPAID",
        )
        db.session.add(bill)
        db.session.commit()
        return bill

    def getCurrentFeeDetail(self, room: Room) -> Dict[str, float]:
        """计算房间当前实时房费（基础房费 + 空调费）"""

        daily_rate = 100.0
        if room.daily_rate is not None and room.daily_rate > 0:
            daily_rate = room.daily_rate
        else:
            daily_rate = current_app.config.get("BILLING_ROOM_RATE", 100.0)
        
        # 1. 累加数据库里已结算的历史详单费用
        from ..services import bill_detail_service
        from ..extensions import db
        # === 关键修复：刷新数据库会话缓存，确保查询到刚提交的费用 ===
        # expire_all() 会清除所有对象的缓存，强制从数据库重新加载
        db.session.expire_all()
        # 使用稍微延后的时间，确保查询到所有已结算的费用（包括刚提交的）
        query_end = datetime.utcnow()
        details = bill_detail_service.getBillDetailsByRoomIdAndTimeRange(
            room_id=room.id,
            start=datetime.min,
            end=query_end,
            customer_id=None,
        )
        ac_fee = sum(detail.cost for detail in details)
        
        # 2. 计算当前正在进行的片段 (Pending Cost)
        # === 核心修改：基于温度变化计算费用，1度=1元 ===
        current_session_fee = 0.0
        
        # 只有 serving_start_time 和 billing_start_temp 都存在时，说明正在服务，才计算实时费用
        # 如果是 PAUSED 或 WAITING，serving_start_time 是 None，这里就不会进，费用就不会涨
        if room.ac_on and room.serving_start_time and room.billing_start_temp is not None and room.current_temp is not None:
            # 计算温度变化量
            start_temp = float(room.billing_start_temp)
            end_temp = float(room.current_temp)
            
            # === 关键修复：确保费用只增不减 ===
            # 对于制热模式，温度应该上升，费用应该只增不减
            # 对于制冷模式，温度应该下降，费用应该只增不减
            # 如果温度变化为负（回温或升温），说明没有实际服务效果，不应该计费
            if room.ac_mode == "HEATING":
                # 制热：温度应该上升，如果 end_temp > start_temp，计费
                if end_temp > start_temp:
                    temp_change = end_temp - start_temp
                else:
                    # 如果温度没有上升，说明还没有服务效果，费用为0
                    temp_change = 0.0
            elif room.ac_mode == "COOLING":
                # 制冷：温度应该下降，如果 end_temp < start_temp，计费
                if end_temp < start_temp:
                    temp_change = start_temp - end_temp
                else:
                    # 如果温度没有下降，说明还没有服务效果，费用为0
                    temp_change = 0.0
            else:
                # 其他模式：使用绝对值
                temp_change = abs(end_temp - start_temp)
            
            # 费用 = 温度变化量（度）* 1元/度
            current_session_fee = temp_change
        # ===================================================================
        
        # === 关键修复：总费用 = 历史费用 + 当前会话费用 ===
        # ac_fee 是历史已结算费用，current_session_fee 是当前未结算费用
        # 总空调费用 = 历史费用 + 当前会话费用
        total_ac_fee = ac_fee + current_session_fee
        
        # 3. 计算房费 (Cycle Logic)
        cycle_days = 1 
        if current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE"):
            history_cycles = sum(1 for d in details if getattr(d, 'detail_type', 'AC') == 'POWER_OFF_CYCLE')
            cycle_days = history_cycles
            if room.ac_on:
                cycle_days += 1
            cycle_days = max(1, cycle_days)
            
        room_fee = float(cycle_days) * float(daily_rate)
        
        return {
            "roomFee": room_fee,
            "acFee": round(total_ac_fee, 2),  # 总空调费用 = 历史 + 当前
            "total": round(room_fee + total_ac_fee, 2),
            "current_session_fee": round(current_session_fee, 2),
            "total_fee": round(total_ac_fee, 2)  # 总空调费用
        }

    def getAllBills(self) -> List[AccommodationFeeBill]:
        return AccommodationFeeBill.query.order_by(AccommodationFeeBill.create_time.desc()).all()

    def getBillById(self, bill_id: int) -> Optional[AccommodationFeeBill]:
        return AccommodationFeeBill.query.get(bill_id)

    def getBillsByRoomId(self, room_id: int) -> List[AccommodationFeeBill]:
        return AccommodationFeeBill.query.filter_by(room_id=room_id).order_by(AccommodationFeeBill.create_time.desc()).all()

    def getBillsByCustomerId(self, customer_id: int) -> List[AccommodationFeeBill]:
        return AccommodationFeeBill.query.filter_by(customer_id=customer_id).order_by(AccommodationFeeBill.create_time.desc()).all()

    def getUnpaidBills(self) -> List[AccommodationFeeBill]:
        return AccommodationFeeBill.query.filter_by(status="UNPAID").order_by(AccommodationFeeBill.create_time.desc()).all()

    def markBillPaid(self, bill_id: int) -> AccommodationFeeBill:
        bill = self.getBillById(bill_id)
        if bill and bill.status != "CANCELLED" and bill.status != "PAID":
            bill.status = "PAID"; bill.paid_time = datetime.utcnow(); db.session.add(bill); db.session.commit()
        return bill

    def cancelBill(self, bill_id: int) -> AccommodationFeeBill:
        bill = self.getBillById(bill_id)
        if bill and bill.status != "PAID" and bill.status != "CANCELLED":
            bill.status = "CANCELLED"; bill.cancelled_time = datetime.utcnow(); db.session.add(bill); db.session.commit()
        return bill

    def markBillPrinted(self, bill_id: int) -> AccommodationFeeBill:
        bill = self.getBillById(bill_id)
        if bill:
            bill.print_status = "PRINTED"; bill.print_time = datetime.utcnow(); db.session.add(bill); db.session.commit()
        return bill

    def buildPrintablePayload(self, bill: AccommodationFeeBill, details: List[DetailRecord]) -> Dict[str, object]:
        return {
            "bill": bill.to_dict(),
            "detailItems": [{
                "startTime": d.start_time.isoformat() if d.start_time else None,
                "endTime": d.end_time.isoformat() if d.end_time else None,
                "duration": d.duration, "fanSpeed": d.fan_speed, "mode": d.ac_mode, "rate": d.rate, "cost": d.cost
            } for d in details],
            "totals": {
                "acDurationMinutes": sum(d.duration for d in details),
                "acFee": sum(d.cost for d in details),
                "roomFee": bill.room_fee, "grandTotal": bill.total_amount
            }
        }
