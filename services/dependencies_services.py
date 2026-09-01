from models.task_dependencies import TaskDependencyModel
from models.tasks import TaskModel
from models import db


def get_dependencies(task_id):
    task = TaskModel.query.get(task_id)
    if not task:
        return None, "Task not found"
    return task.dependencies, None


def add_dependency(task_id, blocking_task_id):
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
    task_dependency = TaskDependencyModel(task_id=task_id, blocking_task_id=blocking_task_id)
    db.session.add(task_dependency)
    db.session.commit()
    return task_dependency, None


def delete_dependency(task_id, dependency_id):
    task_dependency = TaskDependencyModel.query.get(dependency_id)
    if not task_dependency or task_dependency.task_id != task_id:
        return None, "Dependency not found"
    db.session.delete(task_dependency)
    db.session.commit()
    return task_dependency, None