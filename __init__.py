from flask import Flask, render_template

from .config import Config
from .database import seed_default_ac_config
from .extensions import db
from .services import room_service


def create_app(
    config_class: type[Config] = Config, *, setup_database: bool = True
) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_class)
    db.init_app(app)

    if setup_database:
        with app.app_context():
            db.create_all()
            seed_default_ac_config()
            room_service.ensureRoomsInitialized(
                total_count=app.config["HOTEL_ROOM_COUNT"],
                default_temp=app.config["HOTEL_DEFAULT_TEMP"],
            )

    from .controllers.ac_controller import ac_bp
    from .controllers.hotel_controller import hotel_bp
    from .controllers.monitor_controller import monitor_bp
    from .controllers.test_controller import test_bp

    app.register_blueprint(ac_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(test_bp)

    @app.route("/")
    def dashboard():
        rooms = room_service.getAllRooms()
        return render_template("dashboard.html", rooms=rooms)

    return app

