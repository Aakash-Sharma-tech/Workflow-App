from flask import Blueprint, jsonify, request
from services import dashboard_service
from utils.permission import require_login

bp = Blueprint("dashboard", __name__)


@bp.route("/api/dashboard", methods=["GET"])
@require_login()
def dashboard():
    """
    GET /api/dashboard?project_id=<optional>

    Returns all stats cards, breakdowns, and 8-week chart.
    """
    project_id = request.args.get("project_id", type=int)
    stats = dashboard_service.get_stats(project_id=project_id)
    return jsonify(stats)
