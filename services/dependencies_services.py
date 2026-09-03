from models import db
from models.task_dependencies import TaskDependencyModel
from models.tasks import TaskModel


def add_dependency(task, blocking_task_id):
    if task.id == blocking_task_id:
        return False, "A task cannot block itself."
    blocker = TaskModel.query.get(blocking_task_id)
    if not blocker or blocker.project_id != task.project_id:
        return False, "Blocking task must be in the same project."
    existing = TaskDependencyModel.query.filter_by(
        task_id=task.id, blocking_task_id=blocking_task_id
    ).first()
    if existing:
        return False, "Dependency already exists."
    db.session.add(TaskDependencyModel(task_id=task.id, blocking_task_id=blocking_task_id))
    db.session.commit()
    return True, None


def remove_dependency(task, blocking_task_id):
    dep = TaskDependencyModel.query.filter_by(
        task_id=task.id, blocking_task_id=blocking_task_id
    ).first()
    if not dep:
        return False, "Dependency not found."
    db.session.delete(dep)
    db.session.commit()
    return True, None


def set_dependencies(task, blocking_task_ids):
    current = {d.blocking_task_id for d in task.blocking_deps}
    new = set(blocking_task_ids)

    for bid in current - new:
        remove_dependency(task, bid)

    errors = []
    for bid in new - current:
        ok, err = add_dependency(task, bid)
        if not ok:
            errors.append(err)

    return len(errors) == 0, errors
