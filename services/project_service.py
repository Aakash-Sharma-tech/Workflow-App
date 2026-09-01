from models.projects import ProjectModel
from models.project_members import ProjectMemberModel
from models import db


class ProjectService:
    @staticmethod
    def create_project(project_key, name, description, owner_id):
        project = ProjectModel(
            project_key=project_key,
            name=name,
            description=description,
            owner_id=owner_id
        )
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def update_project(project, name, description):
        project.name = name
        project.description = description
        db.session.commit()
        return project

    @staticmethod
    def delete_project(project):
        db.session.delete(project)
        db.session.commit()

    @staticmethod
    def add_member(project_id, user_id):
        project_member = ProjectMemberModel(project_id=project_id, user_id=user_id)
        db.session.add(project_member)
        db.session.commit()
        return project_member

    @staticmethod
    def remove_member(project_id, user_id):
        project_member = ProjectMemberModel.query.filter_by(
            project_id=project_id, user_id=user_id
        ).first()
        if project_member:
            db.session.delete(project_member)
            db.session.commit()

    @staticmethod
    def get_members(project_id):
        return ProjectMemberModel.query.filter_by(project_id=project_id).all()

    @staticmethod
    def get_project(project_id):
        return ProjectModel.query.get(project_id)

    @staticmethod
    def get_projects():
        return ProjectModel.query.all()
