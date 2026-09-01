"""
TaskService — all task mutations go through here.

Design decision: every mutating function records history inside the same
db.session transaction before committing, so the audit trail is always
consistent with the actual data.

Architecture:
    Normal update ──┐
                    ├──> TaskStateMachine (for status)
    Bulk update ────┘    TaskService.update_task (for other fields)
"""

from datetime import datetime
from models.tasks import TaskModel
from models.comments import CommentModel
from models.task_assignees import TaskAssigneeModel
from models.task_history import TaskHistoryModel
from models.task_dependencies import TaskDependencyModel
from models import db
import services.history_service as history_service


# ── Read ──────────────────────────────────────────────────────────────────────

def get_task(task_id):
    return TaskModel.query.get(task_id)


def get_tasks_query(project_id=None, status=None, priority=None,
                    assignee_id=None, search=None, sort_by=None, sort_dir="asc"):
    """
    Build a SQLAlchemy query with optional filters and sorting.
    Shared by the task listing endpoint AND the CSV export endpoint
    so both always apply the same rules.
    """
    q = TaskModel.query

    if project_id:
        q = q.filter(TaskModel.project_id == project_id)
    if status:
        q = q.filter(TaskModel.status == status)
    if priority:
        q = q.filter(TaskModel.priority == priority)
    if assignee_id:
        q = q.filter(TaskModel.assignees.any(user_id=assignee_id))
    if search:
        q = q.filter(
            TaskModel.title.ilike(f"%{search}%") |
            TaskModel.description.ilike(f"%{search}%")
        )

    # Sorting
    sort_col = {
        "title": TaskModel.title,
        "priority": TaskModel.priority,
        "status": TaskModel.status,
        "due_date": TaskModel.due_date,
        "created_at": TaskModel.created_at,
    }.get(sort_by, TaskModel.created_at)

    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    return q


# ── Create ────────────────────────────────────────────────────────────────────

def create_task(project_id, title, description, status, priority, created_by, due_date=None):
    task = TaskModel(
        project_id=project_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        created_by=created_by,
    )
    db.session.add(task)
    db.session.flush()  # get task.id before adding history

    history_service.record(db.session, task.id, created_by, "created")
    db.session.commit()
    return task, None


# ── Update ────────────────────────────────────────────────────────────────────

# Fields that are safe to update and should generate history entries
UPDATABLE_FIELDS = ("title", "description", "priority", "due_date")


def update_task(task_id, user_id, **fields):
    """
    Update one or more task fields atomically with history recording.
    Pass only the fields you want to change as keyword args.
    Status changes must go through TaskStateMachine instead.
    """
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"

    for field, new_value in fields.items():
        if field not in UPDATABLE_FIELDS:
            continue
        old_value = getattr(task, field)
        if old_value == new_value:
            continue
        setattr(task, field, new_value)
        history_service.record(
            db.session, task_id, user_id,
            action=f"{field}_changed",
            field_name=field,
            old_value=old_value,
            new_value=new_value,
        )

    task.updated_at = datetime.now()
    db.session.commit()   # single commit covers task + all history rows
    return task, None


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_task(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    db.session.delete(task)
    db.session.commit()
    return task, None


# ── Comments ──────────────────────────────────────────────────────────────────

def get_comments(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.comments, None


def add_comment(task_id, user_id, content):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"

    comment = CommentModel(task_id=task_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.flush()  # get comment.id

    history_service.record(
        db.session, task_id, user_id,
        action="comment_added",
        new_value=content[:100] + ("…" if len(content) > 100 else ""),
    )
    db.session.commit()   # comment + history in one transaction
    return comment, None


# ── Assignees ─────────────────────────────────────────────────────────────────

def get_assignees(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.assignees, None


def add_assignee(task_id, user_id, acting_user_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    existing = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if existing:
        return None, "User already assigned"

    assignee = TaskAssigneeModel(task_id=task_id, user_id=user_id)
    db.session.add(assignee)
    history_service.record(
        db.session, task_id, acting_user_id,
        action="assignee_added",
        new_value=str(user_id),
    )
    db.session.commit()
    return assignee, None


def remove_assignee(task_id, user_id, acting_user_id):
    assignee = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if not assignee:
        return None, "Assignee not found"
    db.session.delete(assignee)
    history_service.record(
        db.session, task_id, acting_user_id,
        action="assignee_removed",
        old_value=str(user_id),
    )
    db.session.commit()
    return assignee, None


# ── Dependencies ──────────────────────────────────────────────────────────────

def get_dependencies(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.dependencies, None


def add_dependency(task_id, blocking_task_id, acting_user_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    blocking = TaskModel.query.get(blocking_task_id)
    if not blocking:
        return None, "Blocking task not found"
    existing = TaskDependencyModel.query.filter_by(
        task_id=task_id, blocking_task_id=blocking_task_id
    ).first()
    if existing:
        return None, "Dependency already exists"

    dep = TaskDependencyModel(task_id=task_id, blocking_task_id=blocking_task_id)
    db.session.add(dep)
    history_service.record(
        db.session, task_id, acting_user_id,
        action="dependency_added",
        new_value=str(blocking_task_id),
    )
    db.session.commit()
    return dep, None


def remove_dependency(task_id, dependency_id, acting_user_id):
    dep = TaskDependencyModel.query.get(dependency_id)
    if not dep or dep.task_id != task_id:
        return None, "Dependency not found"
    db.session.delete(dep)
    history_service.record(
        db.session, task_id, acting_user_id,
        action="dependency_removed",
        old_value=str(dep.blocking_task_id),
    )
    db.session.commit()
    return dep, None
