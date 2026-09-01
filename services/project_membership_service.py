from flask import flash, session, url_for, request, redirect, render_template
from models.project_members import ProjectMemberModel
from models.projects import ProjectModel
from models import db

class ProjectMembershipService:
    @staticmethod
    def add_member(project_id, user_id):
        project_member = ProjectMemberModel(project_id=project_id, user_id=user_id)
        db.session.add(project_member)
        db.session.commit()
        return project_member

    @staticmethod
    def remove_member(project_id, user_id):
        project_member = ProjectMemberModel.query.filter_by(project_id=project_id, user_id=user_id).first()
        db.session.delete(project_member)
        db.session.commit()

    @staticmethod
    def get_members(project_id):
        return ProjectMemberModel.query.filter_by(project_id=project_id).all()

    @staticmethod
    def get_project_member(project_id, user_id):
        return ProjectMemberModel.query.filter_by(project_id=project_id, user_id=user_id).first()
