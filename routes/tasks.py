from flask import Blueprint, request, jsonify, g, render_template, redirect, url_for, flash, Response
from models import db
from models.tasks import TaskModel, TASK_STATUSES, TASK_PRIORITIES
from models.projects import ProjectModel
from models.comments import CommentModel
from models.user import UserModel
from models.project_members import ProjectMemberModel
from utils.permission import require_login, require_role
from services.tasks_services import (
    create_task, update_task, transition_task, delete_task, get_task_with_transitions,
)
from services.assignees_services import assign_user, unassign_user, set_assignees
from services.dependencies_services import add_dependency, remove_dependency, set_dependencies
from services.history_service import get_task_timeline, record_field_change
from services.bulk_service import paginate_tasks, process_bulk_action, build_task_query
from services.csv_service import generate_csv
from services.project_membership_service import is_project_member, get_user_project_ids
from services.alert_service import get_alert_count, sync_alerts_for_task
from services.task_state_macine import get_allowed_transitions

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/tasks")
@require_login
def task_list():
    alert_count = get_alert_count(g.current_user)
    project_ids = get_user_project_ids(g.current_user)
    projects = ProjectModel.query.filter(ProjectModel.id.in_(project_ids or [-1])).order_by(ProjectModel.key).all()
    users = (
        UserModel.query
        .join(ProjectMemberModel, ProjectMemberModel.user_id == UserModel.id)
        .filter(ProjectMemberModel.project_id.in_(project_ids or [-1]))
        .distinct()
        .order_by(UserModel.name)
        .all()
    )
    template = "manager/tasks.html" if g.current_user.is_manager else "member/tasks.html"
    return render_template(
        template, user=g.current_user, alert_count=alert_count,
        projects=projects, users=users,
        statuses=TASK_STATUSES, priorities=TASK_PRIORITIES,
    )


@tasks_bp.route("/tasks/<int:task_id>")
@require_login
def task_detail(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        flash("Access denied.", "danger")
        return redirect(url_for("tasks.task_list"))
    timeline = get_task_timeline(task)
    project_tasks = TaskModel.query.filter_by(project_id=task.project_id).filter(TaskModel.id != task.id).all()
    members = [m.user for m in task.project.members]
    alert_count = get_alert_count(g.current_user)
    template = "manager/task_detail.html" if g.current_user.is_manager else "member/task_detail.html"
    return render_template(
        template, task=task, timeline=timeline,
        project_tasks=project_tasks, members=members,
        user=g.current_user, alert_count=alert_count,
        allowed_transitions=get_allowed_transitions(task),
    )


@tasks_bp.route("/my-tasks")
@require_login
def my_tasks():
    return redirect(url_for("tasks.task_list", my_tasks="true"))

@tasks_bp.route("/api/tasks", methods=["GET"])
@require_login
def api_list():
    return jsonify(paginate_tasks(g.current_user, request.args))


@tasks_bp.route("/api/tasks/export", methods=["GET"])
@require_login
def api_export():
    q = build_task_query(g.current_user, request.args)
    tasks = q.all()
    csv_data = generate_csv(tasks)
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks_export.csv"},
    )


@tasks_bp.route("/api/tasks/bulk", methods=["POST"])
@require_login
def api_bulk():
    data = request.get_json()
    result = process_bulk_action(
        g.current_user,
        data.get("task_ids", []),
        data.get("action"),
        data.get("payload", {}),
    )
    return jsonify(result)


@tasks_bp.route("/api/projects/<int:project_id>/tasks", methods=["POST"])
@require_login
def api_create(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    if not is_project_member(g.current_user, project_id):
        return jsonify({"error": "Access denied."}), 403
    data = request.get_json(silent=True) or {}
    if not (data.get("title") or "").strip():
        return jsonify({"error": "Title is required."}), 400
    task = create_task(project, data, g.current_user)
    return jsonify(get_task_with_transitions(task)), 201


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["GET"])
@require_login
def api_get(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["PUT"])
@require_login
def api_update(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    task = update_task(task, request.get_json(), g.current_user)
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@require_role("manager")
def api_delete(task_id):
    task = TaskModel.query.get_or_404(task_id)
    delete_task(task)
    return jsonify({"success": True})


@tasks_bp.route("/api/tasks/<int:task_id>/transition", methods=["POST"])
@require_login
def api_transition(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    data = request.get_json()
    task, error = transition_task(task, data["status"], g.current_user)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>/assignees", methods=["POST"])
@require_login
def api_assign(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    data = request.get_json()
    if "assignee_ids" in data:
        set_assignees(task, data["assignee_ids"], g.current_user)
        return jsonify(get_task_with_transitions(task))
    ok, error = assign_user(task, data["user_id"], g.current_user)
    if not ok:
        return jsonify({"error": error}), 400
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>/assignees/<int:user_id>", methods=["DELETE"])
@require_login
def api_unassign(task_id, user_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    ok, error = unassign_user(task, user_id, g.current_user)
    if not ok:
        return jsonify({"error": error}), 400
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>/dependencies", methods=["POST"])
@require_login
def api_add_dep(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    data = request.get_json()
    if "blocking_task_ids" in data:
        set_dependencies(task, data["blocking_task_ids"])
        return jsonify(get_task_with_transitions(task))
    ok, error = add_dependency(task, data["blocking_task_id"])
    if not ok:
        return jsonify({"error": error}), 400
    return jsonify(get_task_with_transitions(task))


@tasks_bp.route("/api/tasks/<int:task_id>/comments", methods=["POST"])
@require_login
def api_comment(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Comment cannot be empty."}), 400
    comment = CommentModel(
        task_id=task.id,
        user_id=g.current_user.id,
        content=content,
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201


@tasks_bp.route("/api/tasks/<int:task_id>/timeline")
@require_login
def api_timeline(task_id):
    task = TaskModel.query.get_or_404(task_id)
    if not is_project_member(g.current_user, task.project_id):
        return jsonify({"error": "Access denied."}), 403
    return jsonify(get_task_timeline(task))
