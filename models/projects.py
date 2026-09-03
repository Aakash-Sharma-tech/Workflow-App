from datetime import datetime
from models import db


class ProjectModel(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    archived = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = db.relationship("UserModel", back_populates="owned_projects", foreign_keys=[owner_id])
    members = db.relationship("ProjectMemberModel", back_populates="project", cascade="all, delete-orphan")
    tasks = db.relationship("TaskModel", back_populates="project", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "key": self.key,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "owner_name": self.owner.name if self.owner else None,
            "archived": self.archived,
            "task_count": len(self.tasks),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
