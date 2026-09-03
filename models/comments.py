from datetime import datetime
from models import db


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    task = db.relationship("TaskModel", back_populates="comments")
    user = db.relationship("UserModel", back_populates="comments")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "user_name": self.user.name if self.user else "Unknown",
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
        }
