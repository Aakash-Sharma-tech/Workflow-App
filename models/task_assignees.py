from models import db
from datetime import datetime

class TaskAssigneeModel(db.Model):
    __tablename__ = "task_assignees"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    #relationships
    task = db.relationship("TaskModel", backref="assignees", lazy=True)
    user = db.relationship("UserModel", backref="tasks_assigned", lazy=True)

    def __init__(self, task_id, user_id):
        self.task_id = task_id
        self.user_id = user_id
        self.assigned_at = datetime.now()
        self.updated_at = datetime.now()

    def __repr__(self):
        return f"<TaskAssignee {self.task_id} {self.user_id}>"