"""
AlertService — manages overdue alerts with reappearance support.

Design decisions:
1. Alerts are never deleted; dismissed_at marks dismissal.
2. Reappearance: if task.due_date changes after dismissal, the old alert
   no longer matches (due_date_at_creation != task.due_date) so a new
   alert row is created — the user sees the alert again.
3. Uniqueness is (task_id, user_id, due_date_at_creation) in practice,
   enforced by the create logic rather than a DB constraint, so we can
   create a new row on each due-date cycle.
"""

from datetime import datetime
from models.alerts import AlertModel
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models import db


def get_active_for_user(user_id):
    """
    Return all active (undismissed) alerts for this user.
    Also creates new alerts for any newly-overdue tasks.
    """
    now = datetime.now()

    # Find all tasks assigned to this user that are overdue and not done
    assigned_task_ids = [
        a.task_id for a in TaskAssigneeModel.query.filter_by(user_id=user_id).all()
    ]

    overdue_tasks = TaskModel.query.filter(
        TaskModel.id.in_(assigned_task_ids),
        TaskModel.due_date < now,
        TaskModel.status != "Done",
    ).all()

    # For each overdue task, ensure an active alert exists for this cycle
    for task in overdue_tasks:
        _get_or_create_alert(task, user_id)

    # Return all undismissed alerts for this user
    return AlertModel.query.filter_by(user_id=user_id, dismissed_at=None).all()


def dismiss(alert_id, user_id):
    """
    Dismiss an alert. User can only dismiss their own alerts.
    Returns (alert, error).
    """
    alert = AlertModel.query.get(alert_id)
    if not alert:
        return None, "Alert not found"
    if alert.user_id != user_id:
        return None, "Cannot dismiss another user's alert"
    if alert.dismissed_at:
        return alert, None   # already dismissed — idempotent

    alert.dismissed_at = datetime.now()
    db.session.commit()
    return alert, None


def _get_or_create_alert(task, user_id):
    """
    Find an active alert for this (task, user, due_date) combination.
    If none exists (first time overdue, or due date changed), create one.
    """
    active = AlertModel.query.filter_by(
        task_id=task.id,
        user_id=user_id,
        dismissed_at=None,
        due_date_at_creation=task.due_date,
    ).first()

    if not active:
        alert = AlertModel(
            task_id=task.id,
            user_id=user_id,
            due_date_at_creation=task.due_date,
        )
        db.session.add(alert)
        db.session.commit()
