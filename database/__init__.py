from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from ..extensions import db
from ..models import ACConfig

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def execute_schema_sql() -> None:
    """执行本目录下的 schema.sql，用于快速重建数据库结构。"""
    sql_text = SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in sql_text.split(";") if stmt.strip()]
    for statement in statements:
        db.session.execute(text(statement))
    db.session.commit()


def seed_default_ac_config() -> None:
    """初始化空调配置，确保模式/费率参数存在。"""
    if ACConfig.query.count() > 0:
        return
    configs = [
        ACConfig(
            id=1,
            mode="COOLING",
            min_temp=18.0,
            max_temp=28.0,
            default_temp=25.0,
            rate=1.0,
            low_speed_rate=0.5,
            mid_speed_rate=1.0,
            high_speed_rate=1.5,
            default_speed="M",
        ),
        ACConfig(
            id=2,
            mode="HEATING",
            min_temp=20.0,
            max_temp=30.0,
            default_temp=26.0,
            rate=1.2,
            low_speed_rate=0.6,
            mid_speed_rate=1.1,
            high_speed_rate=1.6,
            default_speed="M",
        ),
    ]
    db.session.add_all(configs)
    db.session.commit()

