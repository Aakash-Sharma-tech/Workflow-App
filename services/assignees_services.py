from models import db
from models.task_assignees import TaskAssigneeModel
from models.user import UserModel
from services.history_service import record_assignment, record_unassignment
from services.project_membership_service import is_project_member
from services.alert_service import sync_alerts_for_task


def assign_user(task, user_id, actor):
    assignee = UserModel.query.get(user_id)
    if not assignee:
        return False, "User not found."
    if not is_project_member(assignee, task.project_id):
        return False, "User is not a project member."
    existing = TaskAssigneeModel.query.filter_by(task_id=task.id, user_id=user_id).first()
    if existing:
        return False, "User is already assigned."
    db.session.add(TaskAssigneeModel(task_id=task.id, user_id=user_id))
    record_assignment(task, actor, assignee.name)
    db.session.commit()
    sync_alerts_for_task(task)
    db.session.commit()
    return True, None


def unassign_user(task, user_id, actor):
    assignment = TaskAssigneeModel.query.filter_by(task_id=task.id, user_id=user_id).first()
    if not assignment:
        return False, "User is not assigned to this task."
    assignee = assignment.user
    db.session.delete(assignment)
    record_unassignment(task, actor, assignee.name)
    db.session.commit()
    sync_alerts_for_task(task)
    db.session.commit()
    return True, None


def set_assignees(task, user_ids, actor):
    current_ids = {a.user_id for a in task.assignees}
    new_ids = set(user_ids)

    for uid in current_ids - new_ids:
        unassign_user(task, uid, actor)

    for uid in new_ids - current_ids:
        assign_user(task, uid, actor)

    return True, None
