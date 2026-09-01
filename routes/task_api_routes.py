from flask import Blueprint, request, jsonify, session
from services import tasks_services
from services import csv_service
from utils.permission import require_login, require_role
from models.tasks import TaskModel

bp = Blueprint("task_api", __name__)


@bp.route("/api/tasks", methods=["GET"])
@require_login()
def list_tasks():
    """
    GET /api/tasks
    Query params: project_id, status, priority, assignee_id, search, sort_by, sort_dir, page, per_page
    """
    q = tasks_services.get_tasks_query(
        project_id=request.args.get("project_id", type=int),
        status=request.args.get("status"),
        priority=request.args.get("priority"),
        assignee_id=request.args.get("assignee_id", type=int),
        search=request.args.get("search"),
        sort_by=request.args.get("sort_by"),
        sort_dir=request.args.get("sort_dir", "asc"),
    )
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "tasks": [_task_to_dict(t) for t in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    })


@bp.route("/api/tasks/export.csv", methods=["GET"])
@require_login()
def export_tasks_csv():
    """
    GET /api/tasks/export.csv
    Same query params as /api/tasks — filters are identical.
    """
    q = tasks_services.get_tasks_query(
        project_id=request.args.get("project_id", type=int),
        status=request.args.get("status"),
        priority=request.args.get("priority"),
        assignee_id=request.args.get("assignee_id", type=int),
        search=request.args.get("search"),
        sort_by=request.args.get("sort_by"),
        sort_dir=request.args.get("sort_dir", "asc"),
    )
    return csv_service.generate_csv(q)


@bp.route("/api/tasks/<int:task_id>", methods=["GET"])
@require_login()
def get_task(task_id):
    task, err = tasks_services.get_task(task_id), None
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(_task_to_dict(task))


@bp.route("/api/tasks/<int:task_id>", methods=["PATCH"])
@require_login()
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    task, err = tasks_services.update_task(task_id, session["user_id"], **data)
    if err:
        return jsonify({"error": err}), 404
    return jsonify(_task_to_dict(task))


@bp.route("/api/tasks/<int:task_id>/history", methods=["GET"])
@require_login()
def get_history(task_id):
    entries, err = tasks_services.get_task(task_id), None
    task = tasks_services.get_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    history = [
        {
            "id": h.id,
            "action": h.action,
            "field_name": h.field_name,
            "old_value": h.old_value,
            "new_value": h.new_value,
            "user_id": h.user_id,
            "created_at": h.created_at.isoformat() if h.created_at else None,
        }
        for h in task.history
    ]
    return jsonify({"history": history})


@bp.route("/api/tasks/<int:task_id>/comments", methods=["GET"])
@require_login()
def get_comments(task_id):
    comments, err = tasks_services.get_comments(task_id)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({
        "comments": [
            {
                "id": c.id,
                "user_id": c.user_id,
                "content": c.content,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comments
        ]
    })


@bp.route("/api/tasks/<int:task_id>/comments", methods=["POST"])
@require_login()
def add_comment(task_id):
    data = request.get_json(silent=True) or {}
    content = data.get("content", "").strip()
    if not content:
        return jsonify({"error": "Comment content cannot be empty"}), 400

    comment, err = tasks_services.add_comment(task_id, session["user_id"], content)
    if err:
        return jsonify({"error": err}), 404
    return jsonify({
        "id": comment.id,
        "user_id": comment.user_id,
        "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }), 201


# ── Helpers ───────────────────────────────────────────────────────────────────

def _task_to_dict(task):
    return {
        "id": task.id,
        "project_id": task.project_id,
        "title": task.title,
        "description": task.description,
        "status": task.status,
        "priority": task.priority,
        "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else None,
        "created_by": task.created_by,
        "assignees": [a.user_id for a in task.assignees],
        "blocked_from_status": task.blocked_from_status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }
