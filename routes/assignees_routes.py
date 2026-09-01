from flask import flash, session, url_for, request, redirect, render_template, Blueprint
from models.task_assignees import TaskAssigneeModel
from models.tasks import TaskModel
from models import db
from utils.permission import require_login

bp = Blueprint("assignees", __name__)


@bp.route("/projects/<int:project_id>/tasks/<int:task_id>/assignees", methods=["GET", "POST"])
@require_login()
def assignees(project_id, task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        flash("Task not found", "error")
        return redirect(url_for("task.tasks", project_id=project_id))

    if request.method == "GET":
        return render_template("task_assignees.html", task=task)

    user_id = request.form.get("user_id")
    if not user_id:
        flash("User ID is required", "error")
        return redirect(url_for("assignees.assignees", project_id=project_id, task_id=task_id))

    existing = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if existing:
        flash("User is already assigned to this task", "error")
        return redirect(url_for("assignees.assignees", project_id=project_id, task_id=task_id))

    task_assignee = TaskAssigneeModel(task_id=task_id, user_id=int(user_id))
    db.session.add(task_assignee)
    db.session.commit()
    flash("Assignee added", "success")
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route("/projects/<int:project_id>/tasks/<int:task_id>/assignees/<int:user_id>/delete", methods=["POST"])
@require_login()
def delete_assignee(project_id, task_id, user_id):
    task_assignee = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if not task_assignee:
        flash("Assignee not found", "error")
        return redirect(url_for("assignees.assignees", project_id=project_id, task_id=task_id))
    db.session.delete(task_assignee)
    db.session.commit()
    flash("Assignee removed", "success")
    return redirect(url_for("task.tasks", project_id=project_id))


@bp.route('/my-tasks', methods=["GET"])
@require_login()
def my_tasks():
    user_id = session['user_id']
    # Query tasks assigned to current user via the TaskAssigneeModel join table
    assigned = TaskAssigneeModel.query.filter_by(user_id=user_id).all()
    task_ids = [a.task_id for a in assigned]
    tasks = TaskModel.query.filter(TaskModel.id.in_(task_ids)).all()
    return render_template("my_tasks.html", tasks=tasks)