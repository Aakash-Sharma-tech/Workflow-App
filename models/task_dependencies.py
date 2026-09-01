from models import db
from datetime import datetime

class TaskDependencyModel(db.Model):
    __tablename__ = "task_dependencies"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    blocking_task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    dependency_type = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    #relationships
    task = db.relationship("TaskModel", foreign_keys=[task_id], backref="dependencies", lazy=True)
    blocking_task = db.relationship("TaskModel", foreign_keys=[blocking_task_id], backref="dependents", lazy=True)

    def __init__(self, task_id, blocking_task_id, dependency_type):
        self.task_id = task_id
        self.blocking_task_id = blocking_task_id
        self.dependency_type = dependency_type
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<TaskDependency {self.task_id} blocked_by {self.blocking_task_id}>"