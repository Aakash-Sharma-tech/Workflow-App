from datetime import datetime
from models import db
from models.project_members import ProjectMemberModel
from models.task_assignees import TaskAssigneeModel
from models.projects import ProjectModel
from models.tasks import TaskModel


def is_project_member(user, project_id):
    if user.is_manager:
        return True
    return ProjectMemberModel.query.filter_by(
        project_id=project_id, user_id=user.id
    ).first() is not None


def get_user_project_ids(user, include_archived=False):
    if user.is_manager:
        q = ProjectModel.query
        if not include_archived:
            q = q.filter_by(archived=False)
        return [p.id for p in q.all()]
    q = (
        db.session.query(ProjectMemberModel.project_id)
        .join(ProjectModel)
        .filter(ProjectMemberModel.user_id == user.id)
    )
    if not include_archived:
        q = q.filter(ProjectModel.archived.is_(False))
    return [row[0] for row in q.all()]


def add_member(project, user_id):
    existing = ProjectMemberModel.query.filter_by(
        project_id=project.id, user_id=user_id
    ).first()
    if existing:
        return False, "User is already a member."
    db.session.add(ProjectMemberModel(project_id=project.id, user_id=user_id))
    return True, None


def remove_member(project, user_id):
    member = ProjectMemberModel.query.filter_by(
        project_id=project.id, user_id=user_id
    ).first()
    if not member:
        return False, "User is not a member."
    if project.owner_id == user_id:
        return False, "Cannot remove the project owner."

    assignments = (
        TaskAssigneeModel.query
        .join(TaskModel)
        .filter(TaskAssigneeModel.user_id == user_id)
        .filter(TaskModel.project_id == project.id)
        .all()
    )
    for a in assignments:
        db.session.delete(a)

    db.session.delete(member)
    return True, None
