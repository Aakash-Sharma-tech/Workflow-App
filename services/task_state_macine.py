VALID_TRANSITIONS = {
    "Backlog": ["In Progress"],
    "In Progress": ["In Review", "Blocked"],
    "In Review": ["Done", "Blocked"],
    "Blocked": [],
    "Done": ["In Progress"],
}

FINISHED_STATUS = "Done"


def get_allowed_transitions(task):
    status = task.status
    if status == "Blocked":
        if task.blocked_from_status:
            return [task.blocked_from_status]
        return ["In Progress", "In Review"]
    return list(VALID_TRANSITIONS.get(status, []))


def validate_transition(task, new_status):
    current = task.status

    if new_status == current:
        return False, "Task is already in this status."

    if current == "Blocked":
        if new_status != task.blocked_from_status:
            return False, f"Blocked task can only return to '{task.blocked_from_status}'."
        return True, None

    if new_status == "Blocked":
        if current not in ("In Progress", "In Review"):
            return False, "Only tasks In Progress or In Review can be blocked."
        return True, None

    allowed = VALID_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        return False, f"Cannot move from '{current}' to '{new_status}'. Allowed: {', '.join(allowed) or 'none'}."

    if new_status == "Done":
        blockers = [d.blocking_task for d in task.blocking_deps]
        unfinished = [b for b in blockers if b.status != FINISHED_STATUS]
        if unfinished:
            titles = ", ".join(b.title for b in unfinished)
            return False, f"Cannot complete task while blocked by unfinished tasks: {titles}."

    return True, None


def apply_transition(task, new_status):
    current = task.status

    if new_status == "Blocked":
        task.blocked_from_status = current
        task.status = "Blocked"
    elif current == "Blocked" and new_status == task.blocked_from_status:
        task.status = new_status
        task.blocked_from_status = None
    else:
        task.status = new_status

    return task
