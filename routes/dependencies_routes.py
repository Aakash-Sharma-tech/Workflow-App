from flask import request, render_template, session, url_for, flash, redirect, Blueprint
from models.task_dependencies import TaskDependencyModel
from models.tasks import TaskModel
from models import db
from utils.permission import require_login

bp = Blueprint("dependencies", __name__)


@bp.route("/projects/<int:project_id>/tasks/<int:task_id>/dependencies", methods=["GET", "POST"])
@require_login()
def dependencies(project_id, task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("task.tasks", project_id=project_id))

    if request.method == "GET":
        return render_template("task_dependencies.html", task=task)

    blocking_task_id = request.form.get("blocking_task_id")
    if not blocking_task_id:
        flash("Blocking task ID is required", "error")
        return redirect(url_for("dependencies.dependencies", project_id=project_id, task_id=task_id))

    existing = TaskDependencyModel.query.filter_by(
        task_id=task_id, blocking_task_id=blocking_task_id
    ).first()
    if existing:
        flash("This dependency already exists", "error")
        return redirect(url_for("dependencies.dependencies", project_id=project_id, task_id=task_id))

    task_dependency = TaskDependencyModel(task_id=task_id, blocking_task_id=int(blocking_task_id))
    db.session.add(task_dependency)
    db.session.commit()
    flash("Dependency added", "success")
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route("/projects/<int:project_id>/tasks/<int:task_id>/dependencies/<int:dep_id>/delete", methods=["POST"])
@require_login()
def delete_dependency(project_id, task_id, dep_id):
    task_dependency = TaskDependencyModel.query.get(dep_id)
    if not task_dependency or task_dependency.task_id != task_id:
        flash("Dependency not found", "error")
        return redirect(url_for("dependencies.dependencies", project_id=project_id, task_id=task_id))
    db.session.delete(task_dependency)
    db.session.commit()
    flash("Dependency removed", "success")
    return redirect(url_for("task.tasks", project_id=project_id))
