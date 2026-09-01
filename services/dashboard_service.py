"""
DashboardService — computes all dashboard statistics from existing tables.

Design decision: no extra table. All numbers are computed queries on tasks.
The 8-week completion chart uses completed_at (not updated_at) so reopened
tasks don't pollute historical counts.
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.user import UserModel
from models import db


def get_stats(project_id=None):
    """
    Returns a dict with all dashboard metrics.
    Pass project_id to scope to a single project, or None for global view.
    """
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())          # Monday this week
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    base = TaskModel.query
    if project_id:
        base = base.filter(TaskModel.project_id == project_id)

    # ── Summary cards ─────────────────────────────────────────────────────────
    open_tasks = base.filter(TaskModel.status != "Done").count()

    overdue = base.filter(
        TaskModel.due_date < now,
        TaskModel.status != "Done",
    ).count()

    due_this_week = base.filter(
        TaskModel.due_date >= week_start,
        TaskModel.due_date < week_start + timedelta(days=7),
        TaskModel.status != "Done",
    ).count()

    completed_this_week = base.filter(
        TaskModel.completed_at >= week_start,
        TaskModel.completed_at < week_start + timedelta(days=7),
    ).count()

    # ── Status breakdown ──────────────────────────────────────────────────────
    status_rows = (
        db.session.query(TaskModel.status, func.count(TaskModel.id))
        .filter(TaskModel.project_id == project_id if project_id else True)
        .group_by(TaskModel.status)
        .all()
    )
    by_status = {row[0]: row[1] for row in status_rows}

    # ── Assignee breakdown ────────────────────────────────────────────────────
    assignee_rows = (
        db.session.query(TaskAssigneeModel.user_id, func.count(TaskAssigneeModel.task_id))
        .join(TaskModel, TaskAssigneeModel.task_id == TaskModel.id)
        .filter(TaskModel.status != "Done")
        .filter(TaskModel.project_id == project_id if project_id else True)
        .group_by(TaskAssigneeModel.user_id)
        .all()
    )
    by_assignee = []
    for user_id, count in assignee_rows:
        user = UserModel.query.get(user_id)
        by_assignee.append({
            "user_id": user_id,
            "name": f"{user.first_name} {user.last_name}" if user else "Unknown",
            "open_tasks": count,
        })

    # ── 8-week completion chart ───────────────────────────────────────────────
    completions_by_week = []
    for i in range(7, -1, -1):  # oldest to newest
        week_end = week_start - timedelta(weeks=i)
        week_begin = week_end - timedelta(weeks=1)
        count = base.filter(
            TaskModel.completed_at >= week_begin,
            TaskModel.completed_at < week_end,
        ).count()
        completions_by_week.append({
            "week_start": week_begin.strftime("%Y-%m-%d"),
            "completed": count,
        })

    return {
        "open_tasks": open_tasks,
        "overdue": overdue,
        "due_this_week": due_this_week,
        "completed_this_week": completed_this_week,
        "by_status": by_status,
        "by_assignee": by_assignee,
        "completions_by_week": completions_by_week,
    }
