from datetime import datetime, timedelta
from sqlalchemy import func
from flask import current_app
from ..models import AccommodationFeeBill, DetailRecord, Room
from ..extensions import db

class ReportService:
    def __init__(self):
        pass

    def generateRoomReport(self, room_id: int):
        """生成指定房间的详单报表（包含房费和空调费）"""
        # 查询该房间的所有详单，按时间倒序
        details = DetailRecord.query.filter_by(room_id=room_id)\
            .order_by(DetailRecord.start_time.desc()).all()
        
        # 获取房间信息
        room = Room.query.get(room_id)
        daily_rate = 100.0
        if room:
            daily_rate = room.daily_rate or current_app.config.get("BILLING_ROOM_RATE", 100.0)
        
        # 统计该房间的 AC 周期数（用于计算房费）
        cycle_count = sum(1 for d in details if getattr(d, 'detail_type', 'AC') == 'POWER_OFF_CYCLE')
        
        # 计算总房费
        if current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE"):
            charge_days = max(1, cycle_count) if cycle_count > 0 else 0
        else:
            # 如果没有启用周期计费，根据是否有详单记录来判断
            has_records = any(d.cost > 0 for d in details)
            charge_days = 1 if has_records else 0
        
        total_room_fee = charge_days * daily_rate
        
        # 计算总空调费
        total_ac_fee = sum(d.cost for d in details if d.cost > 0)
        
        report_data = []
        # 只显示费用大于0的详单
        for d in details:
            if d.cost <= 0:
                continue
            
            report_data.append({
                "roomId": d.room_id,
                "startTime": d.start_time.isoformat(),
                "endTime": d.end_time.isoformat(),
                "duration": d.duration,
                "fanSpeed": d.fan_speed,
                "rate": d.rate,
                "acFee": d.cost,  # 空调费
                "type": getattr(d, 'detail_type', 'AC')
            })
        
        # 如果有数据，添加汇总行
        if report_data:
            report_data.insert(0, {
                "roomId": room_id,
                "startTime": None,
                "endTime": None,
                "duration": None,
                "fanSpeed": "汇总",
                "rate": None,
                "acFee": total_ac_fee,
                "roomFee": total_room_fee,
                "fee": total_ac_fee + total_room_fee,
                "type": "SUMMARY"
            })
        
        return report_data

    def generateDailyReport(self, date_str: str):
        """生成日报表"""
        if not date_str:
            raise ValueError("日期不能为空")
            
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # 查询当天的所有记录
        # 使用 func.date 截取日期部分进行比较
        records = DetailRecord.query.filter(
            func.date(DetailRecord.start_time) == target_date
        ).all()
        
        return self._aggregate_statistics(records)

    def generateWeeklyReport(self, start_date_str: str):
        """生成周报表"""
        if not start_date_str:
            raise ValueError("开始日期不能为空")
            
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=7)
        
        # 查询这一周的记录
        records = DetailRecord.query.filter(
            func.date(DetailRecord.start_time) >= start_date,
            func.date(DetailRecord.start_time) < end_date
        ).all()
        
        return self._aggregate_statistics(records)

    def _aggregate_statistics(self, records):
        """内部通用方法：将详单记录聚合为统计数据（包含房费）"""
        stats = {}  # 格式: { room_id: { ...data } }
        
        # 获取所有房间的日房费
        all_rooms = Room.query.all()
        room_daily_rates = {room.id: (room.daily_rate or current_app.config.get("BILLING_ROOM_RATE", 100.0)) 
                            for room in all_rooms}
        
        # 统计每个房间的 AC 周期数（用于计算房费）
        room_cycles = {}  # {room_id: cycle_count}
        for r in records:
            if getattr(r, 'detail_type', '') == 'POWER_OFF_CYCLE':
                room_cycles[r.room_id] = room_cycles.get(r.room_id, 0) + 1
        
        # 初始化统计（只初始化有记录的房间）
        room_ids_with_records = set(r.room_id for r in records)
        for rid in room_ids_with_records:
            stats[rid] = {
                "roomId": rid,
                "usageCount": 0,      # 开机次数
                "totalDuration": 0,   # 总时长（分钟）
                "acFee": 0.0,         # 空调费
                "roomFee": 0.0,       # 房费
                "totalFee": 0.0,      # 总费用
                "dispatchCount": 0,   # 调度次数
                "recordCount": 0,     # 详单条数
                "avgTempDiff": 0.0    # 平均温差
            }

        # 聚合详单数据
        for r in records:
            rid = r.room_id
            if rid not in stats:
                continue
            
            # 过滤掉费用为0的条目（但保留用于统计）
            if r.cost > 0:
                item = stats[rid]
                item["recordCount"] += 1
                item["acFee"] += r.cost
                item["totalDuration"] += r.duration
                item["dispatchCount"] += 1
                
                # 估算"开关机次数"
                if getattr(r, 'detail_type', '') == 'POWER_OFF_CYCLE':
                    item["usageCount"] += 1
        
        # 计算房费（基于 AC 周期数）
        for rid, item in stats.items():
            cycle_count = room_cycles.get(rid, 0)
            # 如果启用了 AC 周期计费，使用周期数；否则至少算1天
            if current_app.config.get("ENABLE_AC_CYCLE_DAILY_FEE"):
                charge_days = max(1, cycle_count) if cycle_count > 0 else 0
            else:
                # 如果没有启用周期计费，根据是否有详单记录来判断
                charge_days = 1 if item["recordCount"] > 0 else 0
            
            daily_rate = room_daily_rates.get(rid, 100.0)
            item["roomFee"] = charge_days * daily_rate
            item["totalFee"] = item["acFee"] + item["roomFee"]
        
        # 过滤掉总费用为0的房间
        result = [item for item in stats.values() if item["totalFee"] > 0]
        
        return result