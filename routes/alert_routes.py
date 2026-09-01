from flask import Blueprint, jsonify, session
from services import alert_service
from utils.permission import require_login

bp = Blueprint("alerts", __name__)


@bp.route("/api/alerts", methods=["GET"])
@require_login()
def get_alerts():
    """
    GET /api/alerts

    Returns all active (undismissed) alerts for the logged-in user.
    Also generates new alerts for any newly-overdue tasks.
    """
    user_id = session["user_id"]
    alerts = alert_service.get_active_for_user(user_id)
    return jsonify({
        "alerts": [
            {
                "id": a.id,
                "task_id": a.task_id,
                "due_date": a.due_date_at_creation.strftime("%Y-%m-%d") if a.due_date_at_creation else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in alerts
        ]
    })


@bp.route("/api/alerts/<int:alert_id>/dismiss", methods=["PATCH"])
@require_login()
def dismiss_alert(alert_id):
    """
    PATCH /api/alerts/<id>/dismiss

    Marks the alert as dismissed (sets dismissed_at). Does NOT delete it.
    If the task becomes overdue again in a future cycle, a new alert appears.
    """
    user_id = session["user_id"]
    alert, err = alert_service.dismiss(alert_id, user_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({
        "id": alert.id,
        "dismissed_at": alert.dismissed_at.isoformat() if alert.dismissed_at else None,
    })
