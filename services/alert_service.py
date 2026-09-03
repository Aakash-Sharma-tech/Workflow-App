from datetime import date, datetime
from models import db
from models.alerts import AlertModel
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel


def sync_alerts_for_task(task):
    if not task.due_date or task.status == "Done" or task.due_date >= date.today():
        AlertModel.query.filter_by(task_id=task.id).delete()
        return

    assignee_ids = [a.user_id for a in task.assignees]
    existing = {a.user_id: a for a in AlertModel.query.filter_by(task_id=task.id).all()}

    for uid in assignee_ids:
        if uid in existing:
            alert = existing[uid]
            if alert.dismissed_at and alert.due_date_snapshot != task.due_date:
                alert.dismissed_at = None
                alert.due_date_snapshot = task.due_date
        else:
            db.session.add(AlertModel(
                task_id=task.id,
                user_id=uid,
                due_date_snapshot=task.due_date,
            ))

    for uid, alert in existing.items():
        if uid not in assignee_ids:
            db.session.delete(alert)


def dismiss_alert(alert_id, user):
    alert = AlertModel.query.get(alert_id)
    if not alert or alert.user_id != user.id:
        return False, "Alert not found or not yours."
    from datetime import datetime
    alert.dismissed_at = datetime.utcnow()
    alert.due_date_snapshot = alert.task.due_date
    db.session.commit()
    return True, None


def get_active_alerts(user):
    alerts = (
        AlertModel.query.filter_by(user_id=user.id)
        .join(TaskModel)
        .filter(TaskModel.status != "Done")
        .filter(AlertModel.dismissed_at.is_(None))
        .all()
    )
    active = []
    for a in alerts:
        if a.task and a.task.is_overdue:
            active.append(a)
    return active


def get_alert_count(user):
    return len(get_active_alerts(user))
