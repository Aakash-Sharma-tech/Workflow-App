from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import UserModel
from .projects import ProjectModel
from .project_members import ProjectMemberModel
from .tasks import TaskModel
from .task_assignees import TaskAssigneeModel
from .task_dependencies import TaskDependencyModel
from .task_history import TaskHistoryModel
from .comments import CommentModel
from .alerts import AlertModel

__all__ = [
    'db',
    'UserModel',
    'ProjectModel',
    'ProjectMemberModel',
    'TaskModel',
    'TaskAssigneeModel',
    'TaskDependencyModel',
    'TaskHistoryModel',
    'CommentModel',
    'AlertModel',
]