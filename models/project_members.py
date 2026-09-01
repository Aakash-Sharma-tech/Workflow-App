from models import db
from datetime import datetime


class ProjectMemberModel(db.Model):
    __tablename__ = "project_members"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    joined_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    # many-to-one back to user — backref gives UserModel.memberships
    user = db.relationship("UserModel", backref="memberships", lazy=True)
    # project backref is created by ProjectModel.members

    def __init__(self, project_id, user_id):
        self.project_id = project_id
        self.user_id = user_id
        self.joined_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<ProjectMemberModel project={self.project_id} user={self.user_id}>"