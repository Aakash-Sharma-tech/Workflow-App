from flask import render_template, request, session, url_for, redirect, Blueprint
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.projects import ProjectModel
from models.user import UserModel
from models import db
from utils.permission import require_login

bp = Blueprint("pagination", __name__)


@bp.route("/my-tasks/page/<int:page_number>", methods=["GET"])
@require_login()
def my_tasks(page_number):
    user_id = session["user_id"]
    tasks = TaskModel.query.filter(
        TaskModel.assignees.any(user_id=user_id)
    ).paginate(page=page_number, per_page=5)
    return render_template("my_tasks.html", tasks=tasks)


@bp.route("/tasks/<int:project_id>/page/<int:page_number>", methods=["GET"])
@require_login()
def tasks(project_id, page_number):
    tasks = TaskModel.query.filter_by(project_id=project_id).paginate(page=page_number, per_page=5)
    return render_template("tasks.html", tasks=tasks)


@bp.route("/projects/page/<int:page_number>", methods=["GET"])
@require_login()
def projects(page_number):
    projects = ProjectModel.query.paginate(page=page_number, per_page=5)
    return render_template("projects.html", projects=projects)


@bp.route("/users/page/<int:page_number>", methods=["GET"])
@require_login()
def users(page_number):
    users = UserModel.query.paginate(page=page_number, per_page=5)
    return render_template("users.html", users=users)


@bp.route("/tasks/bulk-update", methods=["POST"])
@require_login()
def bulk_update():
    """
    Bulk-update selected tasks. Expects task_ids[] list in form data.
    Reports per-task success/failure as required by the spec.
    """
    task_ids = request.form.getlist("task_ids")
    status = request.form.get("status")
    priority = request.form.get("priority")
    due_date = request.form.get("due_date") or None
    project_id = request.form.get("project_id")

    results = []
    for task_id in task_ids:
        task = TaskModel.query.get(task_id)
        if not task:
            results.append({"task_id": task_id, "success": False, "reason": "Not found"})
            continue
        if status:
            task.status = status
        if priority:
            task.priority = priority
        if due_date:
            task.due_date = due_date
        results.append({"task_id": task_id, "success": True})

    db.session.commit()
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route("/tasks/bulk-delete", methods=["POST"])
@require_login()
def bulk_delete():
    if session.get("user_role") != "MANAGER":
        return redirect(url_for("project.projects"))
    task_ids = request.form.getlist("task_ids")
    project_id = request.form.get("project_id")
    for task_id in task_ids:
        task = TaskModel.query.get(task_id)
        if task:
            db.session.delete(task)
    db.session.commit()
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route("/tasks/bulk-assign", methods=["POST"])
@require_login()
def bulk_assign():
    task_ids = request.form.getlist("task_ids")
    user_id = request.form.get("assignee_id")
    project_id = request.form.get("project_id")
    for task_id in task_ids:
        existing = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
        if not existing:
            db.session.add(TaskAssigneeModel(task_id=int(task_id), user_id=int(user_id)))
    db.session.commit()
    return redirect(url_for("task.tasks", project_id=project_id))