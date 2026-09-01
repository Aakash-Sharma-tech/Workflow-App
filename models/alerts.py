from models import db
from datetime import datetime


class AlertModel(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    due_date_at_creation = db.Column(db.DateTime, nullable=True)  # snapshot of task.due_date when alert was created
    dismissed_at = db.Column(db.DateTime, nullable=True)          # NULL = active alert
    created_at = db.Column(db.DateTime, nullable=False)

    # many-to-one back to user — backref gives UserModel.alerts
    # task backref is created by TaskModel.alerts
    user = db.relationship("UserModel", backref="alerts", lazy=True)

    def __init__(self, task_id, user_id, due_date_at_creation=None):
        self.task_id = task_id
        self.user_id = user_id
        self.due_date_at_creation = due_date_at_creation
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<AlertModel {self.id}>"