"""
HistoryService — single point of truth for audit trail creation.

Usage (always call inside the caller's transaction, never commit here):

    history_service.record(
        db.session,
        task_id=task.id,
        user_id=user_id,
        action="status_changed",
        field_name="status",
        old_value="In Progress",
        new_value="Done",
    )
    db.session.commit()   # caller commits ONCE, covering task + history

This guarantees the audit entry and the task change are atomic.
"""

from models.task_history import TaskHistoryModel


def record(session, task_id, user_id, action,
           field_name=None, old_value=None, new_value=None):
    """
    Stage a history entry in the current session.
    Does NOT commit — caller is responsible for the commit.
    """
    entry = TaskHistoryModel(
        task_id=task_id,
        user_id=user_id,
        action=action,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
    )
    session.add(entry)
    return entry
