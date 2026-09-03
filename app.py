from flask import Flask
from config import Config
from models import db
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.projects import projects_bp
from routes.tasks import tasks_bp
from routes.alerts import alerts_bp
from seed import seed_demo_data


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(alerts_bp)

    with app.app_context():
        db.create_all()
        seed_demo_data()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
