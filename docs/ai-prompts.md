# AI Prompts & Development Log

AI tools were used throughout development as an engineering aid for exploring architectural approaches, accelerating implementation, debugging issues, and assisting with selected multi-file tasks. Significant AI-assisted changes were reviewed against the assignment requirements and existing project architecture. Where generated solutions were incomplete or incorrect, they were modified or rejected and the resulting behavior was verified through testing. This document records the significant AI-assisted interactions in chronological order rather than routine autocomplete or minor syntax assistance.

---

## 1. Project Architecture & Stack Selection

### Prompt

> "I want to build the BUSY Infotech take-home assignment, Workflow — Project & Task Tracking System. I want to use Flask, Vue 3 via CDN, SQLite / PostgreSQL, SQLAlchemy, Bootstrap 5, and keep the project simple enough that I can explain everything in the technical interview. What architecture should I use?"

### What you got

A recommended Flask MVC-style directory structure with separate layers for models, services, routes, utilities, static assets, and templates, using Vue 3 via CDN served through Flask templates rather than a separate Node/Vite build system.

### What you corrected

I explicitly eliminated unnecessary repository pattern abstractions and heavy build tools (like npm/Vite/TypeScript). Keeping the architecture as a single deployable Flask MVC app serving Vue 3 CDN templates avoids CORS configuration overhead, eliminates dual-server cold-start issues during evaluator testing, and keeps the design SOLID, interview-friendly, and maintainable.

---

## 2. Database Schema & Models Creation

### Prompt

> "What database tables should I create for Workflow? I also need the dashboard's 8-week completion chart. Should I add anything to the task table?"

### What you got

A schema proposal containing 9 core tables: `users`, `projects`, `project_members`, `tasks`, `task_assignees`, `task_dependencies`, `task_history`, `comments`, and `alerts`, with foreign key relationships.

### What you corrected

I added a `completed_at` timestamp column to the `tasks` table. Without this field, calculating 8-week completion trends would require scanning and parsing `task_history` status events. Storing `completed_at` directly on `TaskModel` allows fast, efficient index queries for weekly completion metric charts.

---

## 3. SQLAlchemy Model Relationship Mapping & Backref Debugging

### Prompt

> "How should I fix the `Error creating backref 'task' on relationship 'TaskModel.assignees': property of that name exists on mapper 'Mapper[TaskAssigneeModel(task_assignees)]'` error when starting Flask?"

### What you got

The AI initially suggested renaming the relationship property on `TaskModel` to `task_assignee_list = db.relationship(...)`.

### What you corrected

I rejected renaming `TaskModel.assignees` because doing so would break existing service methods calling `task.assignees`. Upon inspecting the model mappings, I identified that `TaskModel.assignees` already declared `backref="task"`, which automatically injects the `.task` property on `TaskAssigneeModel`. I removed the duplicate explicit `task = db.relationship("TaskModel", backref="assignees")` declaration from `TaskAssigneeModel`, allowing `TaskModel.assignees` to create the `.task` attribute cleanly without breaking caller code.

---

## 4. Task Lifecycle State Machine Implementation

### Prompt

> "How should I implement task statuses and invalid transitions? Suggested statuses: Backlog, In Progress, In Review, Blocked, Done."

### What you got

A server-side state machine class (`TaskStateMachine`) defining an allowed status transition map (`Backlog → In Progress → In Review → Done`, `In Progress/In Review → Blocked`, `Blocked → Unblock`, `Done → In Progress`).

### What you corrected

I ensured that all transition validation was strictly enforced on the server inside `TaskStateMachine.change_state`. Attempting any illegal status jump (such as Backlog directly to Done) is rejected by the backend with an explicit error message explaining why, ensuring the backend remains the single source of truth regardless of client-side UI requests.

---

## 5. Unfinished Blocker Rule Enforcement on Moving Tasks to Done

### Prompt

> "Implement state transition validation for moving tasks to Done when dependencies exist."

### What you got

The generated state transition handler permitted moving a task from `In Review` to `Done` without verifying the status of blocking tasks in `TaskDependencyModel`.

### What you corrected

I modified `TaskStateMachine.change_state` in `services/task_state_machine.py` to query `TaskDependencyModel` whenever a task attempts to move to `Done`. If any blocking task is not in `Done` status, the server rejects the transition and returns an error message listing the unfinished blocker tasks. This strictly satisfies Requirement 4 ("A task with an unfinished blocking task cannot move to Done — the server rejects the attempt").

---

## 6. Project Membership Check on Task Assignment

### Prompt

> "Implement task assignment creation endpoint."

### What you got

```python
@bp.route("/tasks/<int:task_id>/assignees", methods=["POST"])
def add_task_assignee(task_id):
    user_id = request.json.get("user_id")
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    assignee = TaskAssigneeModel(task_id=task_id, user_id=user_id)
    db.session.add(assignee)
    db.session.commit()
    return jsonify({"message": "Assigned"}), 201
```

### What you corrected

The generated code only verified user existence in `UserModel`. It allowed assigning a user to a task even if that user was not a member of the task's project, violating Requirement 5 ("Only members of a task's project may be assigned to it"). I updated `add_task_assignee` in `routes/api_routes.py` and `services/tasks_services.py` to check `ProjectMemberModel`:

```python
is_member = ProjectMemberModel.query.filter_by(project_id=task.project_id, user_id=int(user_id)).first()
if not is_member and task.project.owner_id != int(user_id):
    return jsonify({"error": "Only project members can be assigned to tasks in this project"}), 400
```

---

## 7. Automatic Task Unassignment on Project Member Removal

### Prompt

> "Implement project member removal."

### What you got

```python
@bp.route("/projects/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
def remove_project_member(project_id, user_id):
    member = ProjectMemberModel.query.filter_by(project_id=project_id, user_id=user_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
    return jsonify({"message": "Member removed"})
```

### What you corrected

The AI solution simply deleted the `ProjectMemberModel` record, leaving orphan `TaskAssigneeModel` entries assigned to non-members of that project. I updated `remove_member` in `services/project_membership_service.py` to query all tasks in the project and delete all `TaskAssigneeModel` entries for the removed user while recording audit history (`assignee_removed`). This enforces Requirement 5 ("removing someone from a project unassigns them from that project's tasks").

---

## 8. Resolving Flask Blueprint BuildError & Role Routing

### Prompt

> "After logging in as Manager or Member, Flask throws `werkzeug.routing.exceptions.BuildError: Could not build url for endpoint 'manager.dashboard'. Did you mean 'dashboard.dashboard' instead?`. How should I route manager and member portals properly?"

### What you got

A recommendation to split view endpoints into separate role-governed Flask Blueprints.

### What you corrected

I created `routes/manager_routes.py` (`manager_bp`, `url_prefix='/manager'`) and `routes/member_routes.py` (`member_bp`, `url_prefix='/member'`), registering `@manager_bp.route('/dashboard')` and `@member_bp.route('/dashboard')` in `app.py`. This resolved `url_for('manager.dashboard')` and `url_for('member.dashboard')` calls cleanly while enforcing server-side role decorators (`@require_role('MANAGER')` / `@require_role('MEMBER')`).

---

## 9. Server-Side Task Filtering, Search, Sorting & Pagination

### Prompt

> "Implement server-side task filtering, searching, sorting, and pagination API endpoints."

### What you got

SQLAlchemy query filtering over search terms, `project_id`, `status`, `priority`, `assignee_id`, along with sorting by `due_date`, `priority`, or `created_at`, and Flask-SQLAlchemy `paginate()` metadata generation.

### What you corrected

I verified that all search, filter, sorting, and pagination logic operates entirely on the server via indexed SQL queries, satisfying Requirement 6 ("All of this must be done by the server — do not load every task into the browser and filter there").

---

## 10. Bulk Operations with Per-Task Execution Result Reporting

### Prompt

> "Implement bulk task updates for status, assignee, and due date."

### What you got

A bulk service implementation that executed batch task updates and committed the transaction.

### What you corrected

I updated `BulkTaskService.apply` in `services/bulk_service.py` to process each task in the selection individually and capture any state machine or validation error per task. The service returns a structured array of `{task_id, success, error}` objects so the UI can display a clear breakdown report showing which tasks succeeded and which failed and why, satisfying Requirement 7.

---

## 11. Agentic Implementation — CSV Task Export Feature

### Prompt

> "Implement CSV export for the currently filtered task list."

### What you got

The AI agent added an API route `export_tasks_csv()` in `routes/api_routes.py` that applies active request query filters (`search`, `project_id`, `status`, `priority`, `assignee_id`), formats task records into a CSV string using Python `csv.writer`, and returns a `text/csv` response with a `Content-Disposition: attachment` header.

### What you corrected

I reviewed the CSV export implementation and verified that it reuses the exact same server-side filter query builder as the main task listing endpoint, ensuring exported CSV files reflect the active UI filter state as specified in Requirement 7.

---

## 12. Agentic Implementation — Immutable Task Audit History & Timeline Wiring

### Prompt

> "Implement task history timeline tracking. History must record creation, status moves, assignee changes, dependency updates, due date changes, and comments. Nothing in the history can be edited or deleted."

### What you got

The AI agent created `TaskHistoryModel` (`action`, `field_name`, `old_value`, `new_value`, `user_id`, `created_at`) and `services/history_service.py`, wiring history logging calls into task creation, status transitions, assignee changes, dependency updates, and comment additions.

### What you corrected

I inspected the implementation and confirmed that no update or delete routes exist for `TaskHistoryModel`, guaranteeing immutability. I also added explicit `old_value` and `new_value` string capturing when unassigning project members so the history timeline remains human-readable even if user accounts are modified.

---

## 13. Overdue Task Alerts & Reappearance Logic on Due Date Modification

### Prompt

> "Implement overdue task alert dismissal and due-date update handling."

### What you got

Initial code set `dismissed = True` on `AlertModel` when a user dismissed an overdue task alert.

### What you corrected

The initial AI code never reset the alert status after dismissal. I updated the task modification logic in `services/tasks_services.py` and `routes/api_routes.py` so that whenever a task's `due_date` is modified, all existing `AlertModel` records for that task reset `dismissed = False`. This strictly fulfills Requirement 10 ("If that task's due date later changes, the alert comes back").

---

## 14. Multi-Page HTML Template Structure & Vue 3 CDN Integration

### Prompt

> "I want dedicated HTML files for all pages under `templates/manager/` and `templates/member/`, using Vue 3 CDN directly inside HTML files with Bootstrap 5 and Chart.js CDN instead of external `.js` component files. How should I structure these templates and avoid Jinja2 syntax errors?"

### What you got

A multi-page directory structure under `templates/manager/` and `templates/member/` with Vue 3 CDN script tags inside each template.

### What you corrected

Jinja2 initially threw template parsing exceptions because it attempted to evaluate Vue 3 template expressions (such as `{{ stats.open_tasks }}` or `{{ task.title }}`) as Jinja server variables. I wrapped all Vue template containers and inline `<script>` blocks inside Jinja `{% raw %}` ... `{% endraw %}` guards so Vue template syntax renders cleanly in the client browser.

---

## 15. Agentic Implementation — Interactive Frontend Task Detail & History UI

### Prompt

> "Build the Task Detail UI for manager and member portals featuring status transition buttons, assignees manager, dependencies blocker selector, comments feed, and audit history timeline tab."

### What you got

The AI agent updated `templates/manager/task_detail.html` and `templates/member/task_detail.html` with responsive Bootstrap cards, inline title/description editors, reactive Vue status transition buttons driven by `TaskStateMachine`, an Audit History timeline tab, and comments feed.

### What you corrected

I reviewed the template rendering, added error banner handling to display backend state-machine rejection messages (e.g. unfinished blocker warnings), and verified that project member dropdowns filter exclusively to current members of that task's project.

---

## 16. Request Context Safety in Service Operations

### Prompt

> "How should I handle session user ID access in background service methods when executing outside an active HTTP request context?"

### What you got

Initial service implementations accessed Flask's `session["user_id"]` proxy directly. When invoked outside an active HTTP request context (such as seed data loading or background tasks), the code raised `RuntimeError: Working outside of request context`.

### What you corrected

I refactored `ProjectMembershipService.remove_member` in `services/project_membership_service.py` to accept an optional `acting_user_id=None` parameter and wrap `session` access in `has_request_context()`:

```python
if acting_user_id is None:
    acting_user_id = session.get("user_id", user_id) if has_request_context() else user_id
```

This resolved the context proxy runtime error, allowing service methods to execute safely both inside HTTP request lifecycles and during database seeding (`seed.py`).

---

## 17. WSGI Production Server & Platform Deployment Configuration

### Prompt

> "When I try running `gunicorn` locally on Windows, it fails with `ModuleNotFoundError: No module named 'fcntl'`. Also, how should I configure `app.py` for Koyeb deployment?"

### What you got

An explanation that Gunicorn relies on POSIX system calls (`fcntl`) available only on Linux/macOS.

### What you corrected

I documented standard `python app.py` execution for local Windows development while retaining `gunicorn` in `requirements.txt` and a root `Procfile` (`web: gunicorn --bind :$PORT app:app`) for POSIX production deployment on Koyeb. I verified that `create_app()` in `app.py` exposes `app = create_app()` at the top level for WSGI runners.

---

## 18. Human Review Summary & Engineering Principles

Every AI recommendation and generated code snippet was reviewed against the following core engineering principles:

1. **Architecture Simplicity:** Rejected complex SPA build systems (npm/Vite) and unnecessary repository layers in favor of Flask MVC + Vue 3 CDN templates to ensure single-host deployment and clear interview explainability.
2. **Server-Side Security & Source of Truth:** Enforced role permissions (`MANAGER` vs `MEMBER`), project membership checks, and state machine transition constraints on the server rather than trusting client-side UI states.
3. **Data Integrity & Auditability:** Guaranteed that task history logs (`TaskHistoryModel`) remain append-only and immutable.
4. **Empirical Verification:** Verified all 10 mandatory assignment requirements end-to-end against live Flask endpoints and database seed workflows (`seed.py`) prior to submission.
