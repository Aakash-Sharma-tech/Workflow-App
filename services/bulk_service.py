"""
BulkTaskService — apply one action to many tasks.

Design decision:
    Normal update ──┐
                    ├──> TaskStateMachine / TaskService methods
    Bulk update ────┘

We never duplicate business rules here. Bulk just iterates and delegates.
Each task is handled independently so partial success is possible.

Supported actions:
    "status"   — value: str  (e.g. "Done", "Unblock")
    "assignee" — value: int  (user_id to assign)
    "due_date" — value: str  (ISO date "YYYY-MM-DD", or null to clear)
"""

from datetime import datetime, date
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models import db
from services.task_state_macine import TaskStateMachine
import services.history_service as history_service


class BulkTaskService:

    @staticmethod
    def apply(task_ids, action, value, acting_user_id):
        """
        Apply action to each task_id. Returns a list of per-task results.

        Result shape:
            [
                { "task_id": 1, "success": True },
                { "task_id": 2, "success": False, "error": "..." },
            ]
        """
        results = []

        for task_id in task_ids:
            try:
                task = TaskModel.query.get(task_id)
                if not task:
                    results.append({"task_id": task_id, "success": False,
                                    "error": "Task not found"})
                    continue

                if action == "status":
                    ok, err = BulkTaskService._apply_status(task, value, acting_user_id)
                elif action == "assignee":
                    ok, err = BulkTaskService._apply_assignee(task, value, acting_user_id)
                elif action == "due_date":
                    ok, err = BulkTaskService._apply_due_date(task, value, acting_user_id)
                else:
                    ok, err = False, f"Unknown action '{action}'"

                if ok:
                    results.append({"task_id": task_id, "success": True})
                else:
                    results.append({"task_id": task_id, "success": False, "error": err})

            except Exception as e:
                db.session.rollback()
                results.append({"task_id": task_id, "success": False, "error": str(e)})

        return results

    # ── Action handlers ───────────────────────────────────────────────────────

    @staticmethod
    def _apply_status(task, new_state, acting_user_id):
        """Delegate to TaskStateMachine so business rules are never duplicated."""
        return TaskStateMachine(task).change_state(new_state, acting_user_id)

    @staticmethod
    def _apply_assignee(task, user_id, acting_user_id):
        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            return False, "Invalid user_id"

        existing = TaskAssigneeModel.query.filter_by(
            task_id=task.id, user_id=user_id
        ).first()
        if existing:
            return False, f"User {user_id} is already assigned"

        assignee = TaskAssigneeModel(task_id=task.id, user_id=user_id)
        db.session.add(assignee)
        history_service.record(
            db.session, task.id, acting_user_id,
            action="assignee_added",
            new_value=str(user_id),
        )
        db.session.commit()
        return True, None

    @staticmethod
    def _apply_due_date(task, value, acting_user_id):
        old = task.due_date

        if value is None or value == "":
            new_date = None
        else:
            try:
                new_date = datetime.strptime(value, "%Y-%m-%d")
            except ValueError:
                return False, f"Invalid date format '{value}' — expected YYYY-MM-DD"

        task.due_date = new_date
        task.updated_at = datetime.now()
        history_service.record(
            db.session, task.id, acting_user_id,
            action="due_date_changed",
            field_name="due_date",
            old_value=old.strftime("%Y-%m-%d") if old else None,
            new_value=value,
        )
        db.session.commit()
        return True, None
