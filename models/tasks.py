from datetime import datetime, date
from models import db

TASK_STATUSES = ["Backlog", "In Progress", "In Review", "Done", "Blocked"]
TASK_PRIORITIES = ["Low", "Medium", "High", "Critical"]


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    priority = db.Column(db.String(20), default="Medium", nullable=False)
    status = db.Column(db.String(20), default="Backlog", nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    blocked_from_status = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = db.relationship("ProjectModel", back_populates="tasks")
    assignees = db.relationship("TaskAssigneeModel", back_populates="task", cascade="all, delete-orphan")
    comments = db.relationship("CommentModel", back_populates="task", cascade="all, delete-orphan")
    history = db.relationship("TaskHistoryModel", back_populates="task", cascade="all, delete-orphan")
    alerts = db.relationship("AlertModel", back_populates="task", cascade="all, delete-orphan")

    blocking_deps = db.relationship(
        "TaskDependencyModel",
        foreign_keys="TaskDependencyModel.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    @property
    def is_overdue(self):
        if not self.due_date or self.status == "Done":
            return False
        return self.due_date < date.today()

    def to_dict(self, include_assignees=True):
        data = {
            "id": self.id,
            "project_id": self.project_id,
            "project_key": self.project.key if self.project else None,
            "project_name": self.project.name if self.project else None,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "blocked_from_status": self.blocked_from_status,
            "is_overdue": self.is_overdue,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_assignees:
            data["assignees"] = [
                {"id": a.user.id, "name": a.user.name, "email": a.user.email}
                for a in self.assignees
            ]
        return data
