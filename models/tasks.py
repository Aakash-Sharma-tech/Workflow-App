from models import db
from datetime import datetime


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Enum("Critical", "High", "Medium", "Low"), nullable=False, default="Medium")
    status = db.Column(
        db.Enum("Backlog", "In Progress", "In Review", "Blocked", "Done"),
        nullable=False,
        default="Backlog"
    )
    due_date = db.Column(db.DateTime, nullable=True)
    blocked_from_status = db.Column(db.String(20), nullable=True)  # stores previous status when task is Blocked
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    # many-to-one — who created this task (foreign_keys required since project also FK's users via owner)
    creator = db.relationship("UserModel", foreign_keys=[created_by], backref="tasks_created", lazy=True)

    # one-to-many — task owns its children (cascade deletes children when task deleted)
    assignees = db.relationship("TaskAssigneeModel", backref="task", lazy=True, cascade="all, delete-orphan")
    history = db.relationship("TaskHistoryModel", backref="task", lazy=True, cascade="all, delete-orphan")
    comments = db.relationship("CommentModel", backref="task", lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship("AlertModel", backref="task", lazy=True, cascade="all, delete-orphan")

    # self-referential M:N via task_dependencies
    # tasks this task is blocked BY (this task_id, blocking_task_id = blocker)
    dependencies = db.relationship(
        "TaskDependencyModel",
        foreign_keys="TaskDependencyModel.task_id",
        backref="blocked_task",
        lazy=True,
        cascade="all, delete-orphan"
    )
    # tasks that this task is BLOCKING (this task = blocking_task_id)
    dependents = db.relationship(
        "TaskDependencyModel",
        foreign_keys="TaskDependencyModel.blocking_task_id",
        backref="blocker_task",
        lazy=True
    )

    def __init__(self, title, description, status, project_id, created_by, priority, due_date=None):
        self.title = title
        self.description = description
        self.status = status
        self.project_id = project_id
        self.created_by = created_by
        self.priority = priority
        self.due_date = due_date
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<TaskModel {self.title}>"