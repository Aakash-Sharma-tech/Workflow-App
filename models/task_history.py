from models import db
from datetime import datetime


class TaskHistoryModel(db.Model):
    __tablename__ = "task_history"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action = db.Column(db.String(80), nullable=False)       # e.g. "status_changed", "assigned", "commented"
    field_name = db.Column(db.String(80), nullable=True)    # e.g. "status", "priority", "due_date"
    old_value = db.Column(db.String(255), nullable=True)
    new_value = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    # many-to-one — who performed this action; backref gives UserModel.task_history
    # task backref is created by TaskModel.history
    user = db.relationship("UserModel", backref="task_history", lazy=True)

    def __init__(self, task_id, user_id, action, field_name=None, old_value=None, new_value=None):
        self.task_id = task_id
        self.user_id = user_id
        self.action = action
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<TaskHistoryModel task={self.task_id} action={self.action}>"   