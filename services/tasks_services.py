from datetime import datetime
from models import db
from models.user import UserModel
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.task_dependencies import TaskDependencyModel
from services.history_service import (
    record_creation, record_field_change, record_status_change,
    record_assignment, record_unassignment,
)
from services.task_state_macine import validate_transition, apply_transition, get_allowed_transitions
from services.alert_service import sync_alerts_for_task
from services.project_membership_service import is_project_member


def create_task(project, data, user):
    task = TaskModel(
        project_id=project.id,
        title=(data.get("title") or "").strip(),
        description=data.get("description", ""),
        priority=data.get("priority", "Medium"),
        status="Backlog",
    )
    if data.get("due_date"):
        task.due_date = datetime.strptime(data["due_date"], "%Y-%m-%d").date()

    db.session.add(task)
    db.session.flush()
    record_creation(task, user)

    for uid in data.get("assignee_ids", []):
        try:
            uid = int(uid)
        except (TypeError, ValueError):
            continue
        assignee = UserModel.query.get(uid)
        if assignee and is_project_member(assignee, project.id):
            db.session.add(TaskAssigneeModel(task_id=task.id, user_id=uid))
            record_assignment(task, user, assignee.name)

    for blocker_id in data.get("blocking_task_ids", []):
        blocker = TaskModel.query.get(blocker_id)
        if blocker and blocker.project_id == project.id and blocker.id != task.id:
            db.session.add(TaskDependencyModel(task_id=task.id, blocking_task_id=blocker_id))

    db.session.commit()
    sync_alerts_for_task(task)
    db.session.commit()
    return task


def update_task(task, data, user):
    if "title" in data and data["title"] != task.title:
        record_field_change(task, user, "title", task.title, data["title"])
        task.title = data["title"]
    if "description" in data and data["description"] != task.description:
        record_field_change(task, user, "description", task.description, data["description"])
        task.description = data["description"]
    if "priority" in data and data["priority"] != task.priority:
        record_field_change(task, user, "priority", task.priority, data["priority"])
        task.priority = data["priority"]
    if "due_date" in data:
        old = task.due_date.isoformat() if task.due_date else None
        new = data["due_date"] or None
        if old != new:
            record_field_change(task, user, "due_date", old, new)
            task.due_date = datetime.strptime(new, "%Y-%m-%d").date() if new else None

    task.updated_at = datetime.utcnow()
    db.session.commit()
    sync_alerts_for_task(task)
    db.session.commit()
    return task


def transition_task(task, new_status, user):
    old_status = task.status
    valid, error = validate_transition(task, new_status)
    if not valid:
        return None, error
    apply_transition(task, new_status)
    record_status_change(task, user, old_status, new_status)
    task.updated_at = datetime.utcnow()
    db.session.commit()
    sync_alerts_for_task(task)
    db.session.commit()
    return task, None


def delete_task(task):
    db.session.delete(task)
    db.session.commit()


def get_task_with_transitions(task):
    data = task.to_dict()
    data["allowed_transitions"] = get_allowed_transitions(task)
    data["blocking_tasks"] = [
        {"id": d.blocking_task.id, "title": d.blocking_task.title, "status": d.blocking_task.status}
        for d in task.blocking_deps
    ]
    return data
