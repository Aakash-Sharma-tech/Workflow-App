from models import db
from datetime import datetime


class CommentModel(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey("tasks.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    # many-to-one back to user — backref gives UserModel.comments
    # task backref is created by TaskModel.comments
    user = db.relationship("UserModel", backref="comments", lazy=True)

    def __init__(self, task_id, user_id, content):
        self.task_id = task_id
        self.user_id = user_id
        self.content = content
        self.created_at = datetime.now()

    def __repr__(self):
        return f"<CommentModel {self.id}>"