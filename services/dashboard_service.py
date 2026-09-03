from datetime import date, timedelta
from sqlalchemy import func, case
from models import db
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.user import UserModel
from services.project_membership_service import get_user_project_ids


def _base_query(user):
    project_ids = get_user_project_ids(user)
    if not project_ids:
        return TaskModel.query.filter(db.false())
    return TaskModel.query.filter(TaskModel.project_id.in_(project_ids))


def get_headline_stats(user):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    base = _base_query(user).filter(TaskModel.status != "Done")

    open_count = base.count()
    overdue_count = base.filter(
        TaskModel.due_date.isnot(None),
        TaskModel.due_date < today,
    ).count()
    due_this_week = base.filter(
        TaskModel.due_date.isnot(None),
        TaskModel.due_date >= week_start,
        TaskModel.due_date <= week_end,
    ).count()

    completed_this_week = (
        _base_query(user)
        .filter(TaskModel.status == "Done")
        .filter(TaskModel.updated_at >= datetime_combine(week_start))
        .count()
    )

    return {
        "open_tasks": open_count,
        "overdue_tasks": overdue_count,
        "due_this_week": due_this_week,
        "completed_this_week": completed_this_week,
    }


def datetime_combine(d):
    from datetime import datetime
    return datetime.combine(d, datetime.min.time())


def get_status_breakdown(user):
    project_ids = get_user_project_ids(user)
    if not project_ids:
        return {}
    rows = (
        db.session.query(TaskModel.status, func.count(TaskModel.id))
        .filter(TaskModel.project_id.in_(project_ids))
        .group_by(TaskModel.status)
        .all()
    )
    return {status: count for status, count in rows}


def get_assignee_breakdown(user):
    project_ids = get_user_project_ids(user)
    if not project_ids:
        return []
    rows = (
        db.session.query(UserModel.name, func.count(TaskModel.id))
        .join(TaskAssigneeModel, TaskAssigneeModel.user_id == UserModel.id)
        .join(TaskModel, TaskModel.id == TaskAssigneeModel.task_id)
        .filter(TaskModel.project_id.in_(project_ids))
        .filter(TaskModel.status != "Done")
        .group_by(UserModel.id, UserModel.name)
        .order_by(func.count(TaskModel.id).desc())
        .all()
    )
    return [{"name": name, "count": count} for name, count in rows]


def get_completion_chart(user):
    today = date.today()
    this_monday = today - timedelta(days=today.weekday())
    weeks = []
    for i in range(7, -1, -1):
        week_start = this_monday - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        count = (
            _base_query(user)
            .filter(TaskModel.status == "Done")
            .filter(TaskModel.updated_at >= datetime_combine(week_start))
            .filter(TaskModel.updated_at < datetime_combine(week_end + timedelta(days=1)))
            .count()
        )
        weeks.append({
            "label": week_start.strftime("%b %d"),
            "count": count,
        })
    return weeks


def get_dashboard_data(user):
    return {
        "headlines": get_headline_stats(user),
        "by_status": get_status_breakdown(user),
        "by_assignee": get_assignee_breakdown(user),
        "completions": get_completion_chart(user),
    }
