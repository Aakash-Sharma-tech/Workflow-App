from datetime import datetime
from models import db


class ProjectMemberModel(db.Model):
    __tablename__ = "project_members"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("project_id", "user_id", name="uq_project_member"),)

    project = db.relationship("ProjectModel", back_populates="members")
    user = db.relationship("UserModel", back_populates="memberships")
