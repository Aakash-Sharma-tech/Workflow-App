from datetime import datetime
from models import db
from models.task_history import TaskHistoryModel


def record_creation(task, user):
    entry = TaskHistoryModel(
        task_id=task.id,
        user_id=user.id,
        action_type="created",
        new_value=task.title,
    )
    db.session.add(entry)


def record_field_change(task, user, field_name, old_value, new_value):
    if str(old_value) == str(new_value):
        return
    entry = TaskHistoryModel(
        task_id=task.id,
        user_id=user.id,
        action_type="field_change",
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
    )
    db.session.add(entry)


def record_status_change(task, user, old_status, new_status):
    entry = TaskHistoryModel(
        task_id=task.id,
        user_id=user.id,
        action_type="status_change",
        field_name="status",
        old_value=old_status,
        new_value=new_status,
    )
    db.session.add(entry)


def record_assignment(task, user, assignee_name):
    entry = TaskHistoryModel(
        task_id=task.id,
        user_id=user.id,
        action_type="assigned",
        new_value=assignee_name,
    )
    db.session.add(entry)


def record_unassignment(task, user, assignee_name):
    entry = TaskHistoryModel(
        task_id=task.id,
        user_id=user.id,
        action_type="unassigned",
        old_value=assignee_name,
    )
    db.session.add(entry)


def get_task_timeline(task):
    history = (
        TaskHistoryModel.query.filter_by(task_id=task.id)
        .order_by(TaskHistoryModel.created_at.desc())
        .all()
    )
    comments = sorted(task.comments, key=lambda c: c.created_at, reverse=True)

    timeline = []
    for h in history:
        item = h.to_dict()
        item["type"] = "history"
        item["timestamp"] = h.created_at.isoformat()
        timeline.append(item)

    for c in comments:
        item = c.to_dict()
        item["type"] = "comment"
        item["timestamp"] = c.created_at.isoformat()
        timeline.append(item)

    timeline.sort(key=lambda x: x["timestamp"], reverse=True)
    return timeline
