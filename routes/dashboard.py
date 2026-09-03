from flask import Blueprint, render_template, jsonify, g
from utils.permission import require_login
from services.dashboard_service import get_dashboard_data
from services.alert_service import get_alert_count

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@require_login
def index():
    data = get_dashboard_data(g.current_user)
    alert_count = get_alert_count(g.current_user)
    return render_template(
        "manager/dashboard.html" if g.current_user.is_manager else "member/dashboard.html",
        dashboard=data,
        alert_count=alert_count,
        user=g.current_user,
    )


@dashboard_bp.route("/api/dashboard")
@require_login
def api_dashboard():
    return jsonify(get_dashboard_data(g.current_user))
