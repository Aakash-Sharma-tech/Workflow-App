from flask import session, flash, request, redirect, render_template, url_for, Blueprint
from models.tasks import TaskModel
from models.task_history import TaskHistoryModel
from models.projects import ProjectModel
from models import db
from utils.permission import require_login, require_role

bp = Blueprint("task", __name__)


@bp.route("/projects/<int:project_id>/tasks", methods=["GET", "POST"])
@require_login()
def tasks(project_id):
    project = ProjectModel.query.get(project_id)
    if not project:
        flash("Project not found", "error")
        return redirect(url_for("project.projects"))

    if request.method == "GET":
        return render_template("tasks.html", project=project)

    task = TaskModel(
        project_id=project_id,
        title=request.form["title"],
        description=request.form["description"],
        status=request.form.get("status", "Backlog"),
        priority=request.form.get("priority", "Medium"),
        due_date=request.form.get("due_date") or None,
        created_by=session["user_id"],
    )
    db.session.add(task)
    db.session.commit()

    # Log creation in history
    history = TaskHistoryModel(
        task_id=task.id,
        user_id=session["user_id"],
        action="created"
    )
    db.session.add(history)
    db.session.commit()

    flash("Task created", "success")
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route("/projects/<int:project_id>/tasks/<int:task_id>/delete", methods=["POST"])
@require_role("MANAGER")
def delete_task(project_id, task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("task.tasks", project_id=project_id))
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted", "success")
    return redirect(url_for("task.tasks", project_id=project_id))
