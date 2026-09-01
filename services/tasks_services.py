from models.tasks import TaskModel
from models.comments import CommentModel
from models.task_assignees import TaskAssigneeModel
from models.task_history import TaskHistoryModel
from models.task_dependencies import TaskDependencyModel
from models import db


def get_task_details(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task, None


def create_task(project_id, title, description, status, priority, due_date, created_by):
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
    db.session.commit()
    return task, None


def update_task(task_id, title, description, priority, due_date):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    task.title = title
    task.description = description
    task.priority = priority
    task.due_date = due_date
    db.session.commit()
    return task, None


def delete_task(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    db.session.delete(task)
    db.session.commit()
    return task, None


def get_task_comments(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.comments, None


def add_task_comment(task_id, user_id, content):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    comment = CommentModel(task_id=task_id, user_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()
    return comment, None


def get_task_assignees(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.assignees, None


def add_task_assignee(task_id, user_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    existing = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if existing:
        return None, "User already assigned"
    assignee = TaskAssigneeModel(task_id=task_id, user_id=user_id)
    db.session.add(assignee)
    db.session.commit()
    return assignee, None


def remove_task_assignee(task_id, user_id):
    assignee = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if not assignee:
        return None, "Assignee not found"
    db.session.delete(assignee)
    db.session.commit()
    return assignee, None


def get_task_history(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.history, None


def add_task_history(task_id, user_id, action, field_name=None, old_value=None, new_value=None):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    history = TaskHistoryModel(
        task_id=task_id,
        user_id=user_id,
        action=action,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
    )
    db.session.add(history)
    db.session.commit()
    return history, None


def get_task_dependencies(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.dependencies, None


def add_task_dependency(task_id, blocking_task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    blocking_task = TaskModel.query.get(blocking_task_id)
    if not blocking_task:
        return None, "Blocking task not found"
    existing = TaskDependencyModel.query.filter_by(
        task_id=task_id, blocking_task_id=blocking_task_id
    ).first()
    if existing:
        return None, "Dependency already exists"
    dep = TaskDependencyModel(task_id=task_id, blocking_task_id=blocking_task_id)
    db.session.add(dep)
    db.session.commit()
    return dep, None


def remove_task_dependency(task_id, dependency_id):
    dep = TaskDependencyModel.query.get(dependency_id)
    if not dep or dep.task_id != task_id:
        return None, "Dependency not found"
    db.session.delete(dep)
    db.session.commit()
    return dep, None
