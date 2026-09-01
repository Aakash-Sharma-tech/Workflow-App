from flask import Blueprint, request, jsonify, session
from services.bulk_service import BulkTaskService
from utils.permission import require_login

bp = Blueprint("bulk", __name__)


@bp.route("/api/tasks/bulk", methods=["POST"])
@require_login()
def bulk_action():
    """
    Apply one action to multiple tasks.

    Request body (JSON):
        {
            "task_ids": [1, 2, 3],
            "action":   "status" | "assignee" | "due_date",
            "value":    <string or int depending on action>
        }

    Response:
        {
            "results": [
                { "task_id": 1, "success": true },
                { "task_id": 2, "success": false, "error": "..." }
            ]
        }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "JSON body required"}), 400

    task_ids = data.get("task_ids")
    action = data.get("action")
    value = data.get("value")

    if not task_ids or not isinstance(task_ids, list):
        return jsonify({"error": "'task_ids' must be a non-empty list"}), 400
    if not action:
        return jsonify({"error": "'action' is required"}), 400
    if value is None:
        return jsonify({"error": "'value' is required"}), 400

    acting_user_id = session["user_id"]
    results = BulkTaskService.apply(task_ids, action, value, acting_user_id)
    return jsonify({"results": results}), 200
