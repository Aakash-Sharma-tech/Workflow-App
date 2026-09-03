from datetime import datetime
from models import db


class AlertModel(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    dismissed_at = db.Column(db.DateTime, nullable=True)
    due_date_snapshot = db.Column(db.Date, nullable=True)

    __table_args__ = (db.UniqueConstraint("task_id", "user_id", name="uq_alert_task_user"),)

    task = db.relationship("TaskModel", back_populates="alerts")
    user = db.relationship("UserModel", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_title": self.task.title if self.task else None,
            "project_name": self.task.project.name if self.task and self.task.project else None,
            "due_date": self.task.due_date.isoformat() if self.task and self.task.due_date else None,
            "dismissed_at": self.dismissed_at.isoformat() if self.dismissed_at else None,
        }
