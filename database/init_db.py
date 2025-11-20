from __future__ import annotations

import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    package_root = next(
        parent for parent in Path(__file__).resolve().parents if parent.name == "hotel"
    )
    project_root = package_root.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    __package__ = "hotel.database"

from .. import create_app
from . import execute_schema_sql, seed_default_ac_config
from ..services import room_service


def main():
    app = create_app(setup_database=False)
    with app.app_context():
        execute_schema_sql()
        seed_default_ac_config()
        room_service.ensureRoomsInitialized(
            total_count=app.config["HOTEL_ROOM_COUNT"],
            default_temp=app.config["HOTEL_DEFAULT_TEMP"],
        )
    print("数据库结构与基础数据初始化完成。")


if __name__ == "__main__":
    main()

