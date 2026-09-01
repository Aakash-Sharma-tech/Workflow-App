from models.tasks import TaskModel
from models import db


class TaskStateMachine:
    # Valid transitions per state
    TRANSITIONS = {
        "Backlog":     ["In Progress"],
        "In Progress": ["In Review", "Blocked"],
        "In Review":   ["Done", "Blocked"],   # In Review can also be blocked per requirements
        "Blocked":     [],                    # unblocking is handled via change_state("Unblock")
        "Done":        ["In Progress"],       # can be reopened
    }

    def __init__(self, task):
        self.task = task

    @property
    def state(self):
        # Always read from the DB object so it reflects latest status after transitions
        return self.task.status

    def change_state(self, new_state):
        current = self.task.status

        # Special case: unblocking a blocked task
        if current == "Blocked" and new_state == "Unblock":
            previous = self.task.blocked_from_status
            if not previous:
                return False, "No previous state recorded — cannot unblock"
            self.task.status = previous
            self.task.blocked_from_status = None
            db.session.commit()
            return True, None

        allowed = self.TRANSITIONS.get(current, [])
        if new_state not in allowed:
            return False, f"Cannot move from '{current}' to '{new_state}'. Allowed: {allowed}"

        # When blocking, save current state so we can return to it on unblock
        if new_state == "Blocked":
            self.task.blocked_from_status = current

        self.task.status = new_state
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

    def get_current_state(self):
        return self.task.status

    def get_task(self):
        return self.task