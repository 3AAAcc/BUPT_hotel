from datetime import datetime, timedelta
from sqlalchemy import func
from ..models import DetailRecord, Room
from ..extensions import db

class ReportService:
    def __init__(self):
        pass

    def generateRoomReport(self, room_id: int):
        """生成指定房间的详单报表"""
        # 查询该房间的所有详单，按时间倒序
        details = DetailRecord.query.filter_by(room_id=room_id)\
            .order_by(DetailRecord.start_time.desc()).all()
        
        report_data = []
        for d in details:
            # 过滤掉关机周期的标记记录(费用0时长0)，只显示实际运行记录
            # 除非你想在报表里也看到关机结算点
            # 这里默认显示所有
            report_data.append({
                "roomId": d.room_id,
                "startTime": d.start_time.isoformat(),
                "endTime": d.end_time.isoformat(),
                "duration": d.duration,
                "fanSpeed": d.fan_speed,
                "rate": d.rate,
                "fee": d.cost,
                "type": getattr(d, 'detail_type', 'AC') # 防止旧数据报错
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
        """内部通用方法：将详单记录聚合为统计数据"""
        stats = {}  # 格式: { room_id: { ...data } }
        
        # 初始化所有房间（确保即使没开机的房间也在报表里显示0）
        all_rooms = Room.query.all()
        for room in all_rooms:
            stats[room.id] = {
                "roomId": room.id,
                "usageCount": 0,      # 开机次数
                "totalDuration": 0,   # 总时长
                "totalFee": 0.0,      # 总费用
                "dispatchCount": 0,   # 调度次数 (近似值)
                "recordCount": 0,     # 详单条数
                "avgTempDiff": 0.0    # 平均温差 (暂无数据，填0)
            }

        for r in records:
            rid = r.room_id
            if rid not in stats:
                continue # 防止房间被删后的野数据
            
            item = stats[rid]
            item["recordCount"] += 1
            item["totalFee"] += r.cost
            item["totalDuration"] += r.duration
            
            # 简单的逻辑判断
            # 如果是关机结算记录 (POWER_OFF_CYCLE)，算作一次使用结束
            # 或者每次有记录都算一次调度
            item["dispatchCount"] += 1
            
            # 估算“开关机次数”：这里简单用记录数代替，或者只统计 POWER_OFF
            if getattr(r, 'detail_type', '') == 'POWER_OFF_CYCLE':
                item["usageCount"] += 1

        # 转换为列表返回
        return list(stats.values())