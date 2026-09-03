from datetime import datetime
from models import db
from models.projects import ProjectModel
from models.project_members import ProjectMemberModel
from services.project_membership_service import add_member


def create_project(data, owner):
    data = data or {}
    key = (data.get("key") or "").strip().upper()
    name = (data.get("name") or "").strip()
    if not key or not name:
        return None, "Key and name are required."
    if len(key) > 20:
        return None, "Key must be 20 characters or fewer."

    existing = ProjectModel.query.filter_by(key=key).first()
    if existing:
        return None, "Project key already exists."

    project = ProjectModel(
        key=key,
        name=name,
        description=(data.get("description") or "").strip(),
        owner_id=data.get("owner_id") or owner.id,
    )
    db.session.add(project)
    db.session.flush()

    add_member(project, project.owner_id)
    for uid in data.get("member_ids", []):
        if uid != project.owner_id:
            add_member(project, uid)

    db.session.commit()
    return project, None


def update_project(project, data):
    if "key" in data and data["key"].upper() != project.key:
        clash = ProjectModel.query.filter_by(key=data["key"].upper()).first()
        if clash:
            return None, "Project key already exists."
        project.key = data["key"].upper()
    if "name" in data:
        project.name = data["name"]
    if "description" in data:
        project.description = data["description"]
    if "owner_id" in data:
        project.owner_id = data["owner_id"]
        add_member(project, data["owner_id"])
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return project, None


def archive_project(project):
    project.archived = True
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return project


def restore_project(project):
    project.archived = False
    project.updated_at = datetime.utcnow()
    db.session.commit()
    return project


def get_projects_for_user(user, include_archived=False, archived_only=False):
    q = ProjectModel.query
    if archived_only:
        q = q.filter_by(archived=True)
    elif not include_archived:
        q = q.filter_by(archived=False)
    if not user.is_manager:
        member_ids = [
            m.project_id for m in ProjectMemberModel.query.filter_by(user_id=user.id).all()
        ]
        q = q.filter(ProjectModel.id.in_(member_ids or [-1]))
    return q.order_by(ProjectModel.name).all()
