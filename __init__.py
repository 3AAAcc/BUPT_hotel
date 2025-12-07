from flask import Flask, render_template
from flask_cors import CORS

from .config import Config
from .database import (
    ensure_bill_detail_update_time_column,
    ensure_room_billing_start_temp_column,
    ensure_room_daily_rate_column,
    ensure_room_last_temp_update_column,
    seed_default_ac_config,
)
from .extensions import db
from .services import room_service, temperature_scheduler
from .utils.time_master import clock


def create_app(
    config_class: type[Config] = Config, *, setup_database: bool = True
) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)
    
    # 添加CORS支持，允许跨域访问
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    db.init_app(app)
    
    # 初始化时间倍速
    speed = app.config.get("TIME_ACCELERATION_FACTOR", 1.0)
    clock.set_speed(speed)
    print(f"=== 系统启动: 逻辑时钟倍速 x{speed} ===")

    if setup_database:
        with app.app_context():
            db.create_all()
            # 先确保数据库字段存在，再初始化数据
            ensure_bill_detail_update_time_column()
            ensure_room_last_temp_update_column()
            ensure_room_daily_rate_column()
            ensure_room_billing_start_temp_column()
            seed_default_ac_config()
            room_service.ensureRoomsInitialized(
                total_count=app.config["HOTEL_ROOM_COUNT"],
                default_temp=app.config["HOTEL_DEFAULT_TEMP"],
            )
    
    # 启动温度自动更新后台任务
    # === 关键修复：确保在启动 TemperatureScheduler 之前，所有必要的列都已存在 ===
    # 即使 setup_database=False，也要确保列存在，因为 TemperatureScheduler 会立即查询 Room 表
    with app.app_context():
        ensure_bill_detail_update_time_column()
        ensure_room_last_temp_update_column()
        ensure_room_daily_rate_column()
        ensure_room_billing_start_temp_column()
        temperature_scheduler.start(app)

    from .controllers.ac_controller import ac_bp
    from .controllers.admin_controller import admin_bp
    from .controllers.bill_controller import bill_bp
    from .controllers.hotel_controller import hotel_bp
    from .controllers.monitor_controller import monitor_bp
    from .controllers.monitoring_controller import monitoring_bp
    from .controllers.report_controller import report_bp
    from .controllers.test_controller import test_bp

    app.register_blueprint(ac_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(bill_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(test_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/customer")
    def customer():
        return render_template("customer.html")

    @app.route("/reception")
    def reception():
        return render_template("reception.html")
    
    @app.route("/reception/checkin")
    def reception_checkin():
        return render_template("checkin.html")
    
    @app.route("/reception/checkout")
    def reception_checkout():
        return render_template("checkout.html")

    @app.route("/manager")
    def manager():
        return render_template("manager.html")

    @app.route("/manager/report")
    def manager_report():
        return render_template("admin.html")

    return app

