from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.user import UserModel
from models.projects import ProjectModel
from models.project_members import ProjectMemberModel
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.task_dependencies import TaskDependencyModel
from models.task_history import TaskHistoryModel
from models.comments import CommentModel
from models.alerts import AlertModel
