from datetime import datetime
from models import db


class TaskHistoryModel(db.Model):
    __tablename__ = "task_history"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    field_name = db.Column(db.String(50), nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    task = db.relationship("TaskModel", back_populates="history")
    user = db.relationship("UserModel", back_populates="history_entries")

    def to_dict(self):
        return {
            "id": self.id,
            "action_type": self.action_type,
            "field_name": self.field_name,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "user_name": self.user.name if self.user else "Unknown",
            "created_at": self.created_at.isoformat(),
        }
