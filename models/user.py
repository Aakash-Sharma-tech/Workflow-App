from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="member")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owned_projects = db.relationship("ProjectModel", back_populates="owner", foreign_keys="ProjectModel.owner_id")
    memberships = db.relationship("ProjectMemberModel", back_populates="user", cascade="all, delete-orphan")
    assignments = db.relationship("TaskAssigneeModel", back_populates="user", cascade="all, delete-orphan")
    comments = db.relationship("CommentModel", back_populates="user")
    history_entries = db.relationship("TaskHistoryModel", back_populates="user")
    alerts = db.relationship("AlertModel", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_manager(self):
        return self.role == "manager"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }
