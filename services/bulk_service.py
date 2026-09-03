from datetime import datetime, date
from sqlalchemy import or_, asc, desc
from models import db
from models.tasks import TaskModel, TASK_STATUSES, TASK_PRIORITIES
from models.task_assignees import TaskAssigneeModel
from models.projects import ProjectModel
from services.project_membership_service import get_user_project_ids
from services.tasks_services import transition_task, update_task
from services.assignees_services import set_assignees


def build_task_query(user, params):
    project_ids = get_user_project_ids(user, include_archived=params.get("include_archived", False))
    if not project_ids:
        return TaskModel.query.filter(TaskModel.id == -1)
    q = TaskModel.query.filter(TaskModel.project_id.in_(project_ids))

    search = params.get("search", "").strip()
    if search:
        pattern = f"%{search}%"
        q = q.filter(or_(TaskModel.title.ilike(pattern), TaskModel.description.ilike(pattern)))

    if params.get("project_id"):
        try:
            q = q.filter(TaskModel.project_id == int(params["project_id"]))
        except (TypeError, ValueError):
            pass

    if params.get("status"):
        q = q.filter(TaskModel.status == params["status"])

    if params.get("priority"):
        q = q.filter(TaskModel.priority == params["priority"])

    if params.get("assignee_id"):
        try:
            q = q.filter(TaskModel.assignees.any(user_id=int(params["assignee_id"])))
        except (TypeError, ValueError):
            pass

    if params.get("overdue") == "true":
        q = q.filter(
            TaskModel.due_date.isnot(None),
            TaskModel.due_date < date.today(),
            TaskModel.status != "Done",
        )

    if params.get("my_tasks") == "true":
        q = q.filter(TaskModel.assignees.any(user_id=user.id))

    sort = params.get("sort", "updated_at")
    order = params.get("order", "desc")
    sort_map = {
        "due_date": TaskModel.due_date,
        "priority": TaskModel.priority,
        "updated_at": TaskModel.updated_at,
        "title": TaskModel.title,
    }
    col = sort_map.get(sort, TaskModel.updated_at)
    q = q.order_by(asc(col) if order == "asc" else desc(col))

    return q


def paginate_tasks(user, params, per_page=15):
    q = build_task_query(user, params)
    try:
        page = max(1, int(params.get("page", 1)))
    except (TypeError, ValueError):
        page = 1
    total = q.count()
    tasks = q.offset((page - 1) * per_page).limit(per_page).all()
    return {
        "tasks": [t.to_dict() for t in tasks],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


def process_bulk_action(user, task_ids, action, payload):
    results = []
    for tid in task_ids:
        task = TaskModel.query.get(tid)
        if not task:
            results.append({"task_id": tid, "success": False, "error": "Task not found."})
            continue

        project_ids = get_user_project_ids(user)
        if task.project_id not in project_ids:
            results.append({"task_id": tid, "success": False, "error": "Access denied."})
            continue

        try:
            if action == "status":
                _, err = transition_task(task, payload["status"], user)
                if err:
                    results.append({"task_id": tid, "success": False, "error": err})
                else:
                    results.append({"task_id": tid, "success": True})

            elif action == "assignee":
                ok, err = set_assignees(task, payload.get("assignee_ids", []), user)
                if not ok:
                    results.append({"task_id": tid, "success": False, "error": err})
                else:
                    results.append({"task_id": tid, "success": True})

            elif action == "due_date":
                update_task(task, {"due_date": payload.get("due_date")}, user)
                results.append({"task_id": tid, "success": True})

            else:
                results.append({"task_id": tid, "success": False, "error": "Unknown action."})
        except Exception as e:
            results.append({"task_id": tid, "success": False, "error": str(e)})

    succeeded = sum(1 for r in results if r["success"])
    return {
        "results": results,
        "summary": {"total": len(results), "succeeded": succeeded, "failed": len(results) - succeeded},
    }
