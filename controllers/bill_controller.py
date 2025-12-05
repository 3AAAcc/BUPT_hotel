import csv
import io
from datetime import datetime
from flask import Blueprint, Response, request, jsonify
from ..models import DetailRecord, AccommodationFeeBill
from ..services import bill_service
from ..extensions import db

# 修正路径前缀
bill_bp = Blueprint("bill", __name__, url_prefix="/bill")

@bill_bp.get("/export/csv")
def export_bill_details():
    room_id = request.args.get("roomId", type=int)
    
    query = DetailRecord.query
    if room_id:
        query = query.filter_by(room_id=room_id)
    
    details = query.order_by(DetailRecord.start_time.desc()).all()

    # 使用 utf-8-sig 方便 Excel 打开不乱码
    si = io.StringIO()
    writer = csv.writer(si)
    
    # === 优化：增加“类型”列 ===
    writer.writerow(["房间号", "开始时间", "结束时间", "时长(分钟)", "风速", "模式", "费率", "费用", "类型"])

    for detail in details:
        # 处理记录类型显示
        d_type = getattr(detail, 'detail_type', 'AC')
        if d_type == 'POWER_OFF_CYCLE':
            type_str = "关机结算(房费周期)"
        elif d_type == 'ROOM_FEE':
            type_str = "房费"
        else:
            type_str = "空调运行"
        
        writer.writerow(
            [
                detail.room_id,
                detail.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                detail.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                detail.duration,
                detail.fan_speed,
                detail.ac_mode,
                detail.rate,
                detail.cost,
                type_str
            ]
        )

    output = si.getvalue()
    # 转换编码
    output_bytes = output.encode("utf-8-sig")

    return Response(
        output_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=bill_details.csv"},
    )