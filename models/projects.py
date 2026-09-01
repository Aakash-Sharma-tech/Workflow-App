from models import db
from datetime import datetime


class ProjectModel(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    project_key = db.Column(db.String(80), unique=True, nullable=False)  # short key e.g. "PROJ-1"
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    is_archived = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    # Relationships — project owns members and tasks
    members = db.relationship("ProjectMemberModel", backref="project", lazy=True, cascade="all, delete-orphan")
    tasks = db.relationship("TaskModel", backref="project", lazy=True, cascade="all, delete-orphan")

    def __init__(self, project_key, name, description, owner_id):
        self.project_key = project_key
        self.name = name
        self.description = description
        self.owner_id = owner_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<ProjectModel {self.name}>"