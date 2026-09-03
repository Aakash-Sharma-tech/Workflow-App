from datetime import datetime
from models import db


class TaskDependencyModel(db.Model):
    __tablename__ = "task_dependencies"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    blocking_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("task_id", "blocking_task_id", name="uq_task_dependency"),)

    task = db.relationship("TaskModel", foreign_keys=[task_id], back_populates="blocking_deps")
    blocking_task = db.relationship("TaskModel", foreign_keys=[blocking_task_id])
