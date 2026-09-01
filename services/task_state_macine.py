"""
TaskStateMachine — enforces lifecycle rules and records history atomically.

Valid transitions:
    Backlog     → In Progress
    In Progress → In Review | Blocked
    In Review   → Done | Blocked
    Blocked     → Unblock (returns to blocked_from_status)
    Done        → In Progress  (reopen)

Design decision: status changes go through this class, not update_task(),
so the same rules apply from both normal updates and bulk operations.
"""

from datetime import datetime
from models import db
import services.history_service as history_service


class TaskStateMachine:
    TRANSITIONS = {
        "Backlog":     ["In Progress"],
        "In Progress": ["In Review", "Blocked"],
        "In Review":   ["Done", "Blocked"],
        "Blocked":     [],          # only "Unblock" is valid (special-cased below)
        "Done":        ["In Progress"],
    }

    def __init__(self, task):
        self.task = task

    @property
    def state(self):
        return self.task.status

    def change_state(self, new_state, acting_user_id):
        """
        Transition task to new_state.
        Stages history and updates completed_at; caller must not commit before calling.
        Returns (success: bool, error: str | None).
        """
        current = self.task.status
        old_status = current

        # ── Unblock ──────────────────────────────────────────────────────────
        if new_state == "Unblock":
            if current != "Blocked":
                return False, "Task is not blocked"
            previous = self.task.blocked_from_status
            if not previous:
                return False, "No previous state recorded — cannot unblock"
            self.task.status = previous
            self.task.blocked_from_status = None
            self.task.updated_at = datetime.now()
            history_service.record(
                db.session, self.task.id, acting_user_id,
                action="status_changed",
                field_name="status",
                old_value=old_status,
                new_value=previous,
            )
            db.session.commit()
            return True, None

        # ── Validate transition ───────────────────────────────────────────────
        if current == "Blocked":
            return False, "Blocked tasks can only be 'Unblocked'"

        allowed = self.TRANSITIONS.get(current, [])
        if new_state not in allowed:
            return False, f"Cannot move from '{current}' to '{new_state}'. Allowed: {allowed}"

        # ── Apply ─────────────────────────────────────────────────────────────
        if new_state == "Blocked":
            self.task.blocked_from_status = current

        if new_state == "Done":
            self.task.completed_at = datetime.now()
        elif current == "Done":
            # Reopening — clear completion timestamp
            self.task.completed_at = None

        self.task.status = new_state
        self.task.updated_at = datetime.now()

        history_service.record(
            db.session, self.task.id, acting_user_id,
            action="status_changed",
            field_name="status",
            old_value=old_status,
            new_value=new_state,
        )
        db.session.commit()
        return True, None

    def can_transition_to(self, new_state):
        if self.task.status == "Blocked":
            return new_state == "Unblock"
        return new_state in self.TRANSITIONS.get(self.task.status, [])

    def get_allowed_transitions(self):
        if self.task.status == "Blocked":
            return ["Unblock"]
        return self.TRANSITIONS.get(self.task.status, [])