from flask import Flask
from config import Config
from models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)

    with app.app_context():
        # ── Register blueprints ───────────────────────────────────────────────

        # Auth
        from routes.auth import auth_bp
        app.register_blueprint(auth_bp)

        # HTML / form-based routes
        from routes.project_routes import bp as project_bp
        from routes.project_membership_routes import bp as membership_bp
        from routes.task_routes import bp as task_bp
        from routes.assignees_routes import bp as assignees_bp
        from routes.dependencies_routes import bp as dep_bp
        from routes.pagination_routes import bp as pagination_bp

        app.register_blueprint(project_bp)
        app.register_blueprint(membership_bp)
        app.register_blueprint(task_bp)
        app.register_blueprint(assignees_bp)
        app.register_blueprint(dep_bp)
        app.register_blueprint(pagination_bp)

        # JSON API routes
        from routes.bulk_routes import bp as bulk_bp
        from routes.task_api_routes import bp as task_api_bp
        from routes.dashboard_routes import bp as dashboard_bp
        from routes.alert_routes import bp as alert_bp

        app.register_blueprint(bulk_bp)
        app.register_blueprint(task_api_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(alert_bp)

        # ── Create tables ─────────────────────────────────────────────────────
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
