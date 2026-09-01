from models.task_assignees import TaskAssigneeModel
from models.tasks import TaskModel
from models.user import UserModel
from models import db


def add_assignee(task_id, user_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    user = UserModel.query.get(user_id)
    if not user:
        return None, "User not found"
    existing = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if existing:
        return None, "User already assigned to this task"
    task_assignee = TaskAssigneeModel(task_id=task_id, user_id=user_id)
    db.session.add(task_assignee)
    db.session.commit()
    return task_assignee, None


def delete_assignee(task_id, user_id):
    task_assignee = TaskAssigneeModel.query.filter_by(task_id=task_id, user_id=user_id).first()
    if not task_assignee:
        return None, "Assignee not found"
    db.session.delete(task_assignee)
    db.session.commit()
    return task_assignee, None


def get_my_tasks(user_id):
    """Pass user_id explicitly — services must not access session directly."""
    assigned = TaskAssigneeModel.query.filter_by(user_id=user_id).all()
    task_ids = [a.task_id for a in assigned]
    tasks = TaskModel.query.filter(TaskModel.id.in_(task_ids)).all()
    return tasks, None
