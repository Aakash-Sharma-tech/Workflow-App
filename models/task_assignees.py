from datetime import datetime
from models import db


class TaskAssigneeModel(db.Model):
    __tablename__ = "task_assignees"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("task_id", "user_id", name="uq_task_assignee"),)

    task = db.relationship("TaskModel", back_populates="assignees")
    user = db.relationship("UserModel", back_populates="assignments")
