from flask import Blueprint, render_template, jsonify, g
from utils.permission import require_login
from services.alert_service import get_active_alerts, dismiss_alert, get_alert_count

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/alerts")
@require_login
def list_alerts():
    alerts = get_active_alerts(g.current_user)
    template = "manager/alerts.html" if g.current_user.is_manager else "member/alerts.html"
    return render_template(template, alerts=alerts, user=g.current_user, alert_count=len(alerts))


@alerts_bp.route("/api/alerts")
@require_login
def api_list():
    alerts = get_active_alerts(g.current_user)
    return jsonify([a.to_dict() for a in alerts])


@alerts_bp.route("/api/alerts/count")
@require_login
def api_count():
    return jsonify({"count": get_alert_count(g.current_user)})


@alerts_bp.route("/api/alerts/<int:alert_id>/dismiss", methods=["POST"])
@require_login
def api_dismiss(alert_id):
    ok, error = dismiss_alert(alert_id, g.current_user)
    if not ok:
        return jsonify({"error": error}), 400
    return jsonify({"success": True})
