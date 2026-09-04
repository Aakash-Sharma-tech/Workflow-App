# Architecture

## Moving Pieces & Communication

```text
Browser (Vue 3 via CDN, Bootstrap 5, Chart.js)
    │
    ▼ HTTP / JSON API (Cookie Session Auth)
Flask Blueprints (routes/auth_routes.py, manager_routes.py, member_routes.py, api_routes.py)
    │
    ▼ Python Service Calls
Service Layer (task_state_machine.py, tasks_services.py, bulk_service.py, dashboard_service.py, project_membership_service.py)
    │
    ▼ SQLAlchemy ORM Queries & Mutations
Models / Persistence Layer (UserModel, ProjectModel, TaskModel, TaskAssigneeModel, TaskDependencyModel, TaskHistoryModel, CommentModel, AlertModel)
    │
    ▼ SQL Drivers (psycopg2 / sqlite3)
PostgreSQL (Production on Koyeb/Supabase) / SQLite (Local Development)
```

- **Frontend:** HTML templates served by Flask using Vue 3 CDN (Composition API / Options API), Bootstrap 5, and Chart.js for data visualization. Frontend makes asynchronous `fetch()` API calls to Flask JSON endpoints using `api.js`.
- **HTTP/Routing Layer:** Flask Blueprints split by role (`manager_bp`, `member_bp`, `auth_bp`, `api_bp`). Routes perform request validation and session authorization checks (`@require_login()`, `@require_role('MANAGER')`).
- **Service Layer:** Houses core domain logic, business constraints, state machine transitions (`TaskStateMachine`), bulk operations (`BulkTaskService`), audit history recording (`history_service`), and portfolio metrics calculation (`dashboard_service`).
- **Data Model & Persistence:** SQLAlchemy ORM models enforcing table relationships, foreign keys, cascade deletes, and schema constraints.

---

## Where Each Piece Runs

- **Client Browser:** Runs Vue 3, Bootstrap UI components, DOM updates, interactive forms, and Chart.js chart rendering.
- **Application Server:** Python 3 Flask server (WSGI Gunicorn in production Linux, `python app.py` / `waitress` locally on Windows). Hosted on Koyeb Web Services.
- **Database Server:** Relational Database Instance (Supabase PostgreSQL / SQLite database file `instance/flowtrack.db` locally).

---

## Request Path: Representative User Action (Changing Task Status to 'Done')

1. **User Action:** The user clicks **"→ Move to Done"** on the Task Detail view.
2. **Frontend Dispatch:** Vue 3 component sends `PATCH /api/tasks/42/status` with JSON body `{"status": "Done"}` via `api.patch()`.
3. **Route Interception:** Flask route `change_task_status(task_id)` in `routes/api_routes.py` receives the HTTP request and verifies active user session (`@require_login()`).
4. **Service Delegation:** Route instantiates `TaskStateMachine(task)` and invokes `change_state("Done", acting_user_id)`.
5. **Business Rule Check (Blocker Check):** `TaskStateMachine` queries `TaskDependencyModel` for all tasks blocking task #42. It discovers an unfinished blocking task (#18 in `In Progress`).
6. **Rejection & Response:** `change_state` rejects the transition and returns `(False, "Cannot move to Done: task is blocked by unfinished task(s) #18 'DB Migration'")`. The route returns `HTTP 400 Bad Request` with the error JSON payload.
7. **Frontend State Update:** Vue catches the response error and displays a visible alert banner to the user explaining why the status change was rejected.

---

## Decisions: What We Decided *Not* to Build & Why

1. **Separate Node / Vite / Vue CLI Frontend Build Pipeline:**
   - *Why Not:* Avoided unnecessary build toolchain complexity, CORS configuration overhead, node_modules dependencies, and dual-server deployment setups. Serving Vue 3 via CDN inside Flask templates provides instant reactivity while maintaining simple deployment.
2. **Repository Pattern Abstraction Layer:**
   - *Why Not:* SQLAlchemy ORM already acts as a data mapper and unit of work. Wrapping SQLAlchemy models inside custom repository classes adds boilerplate code without providing practical architectural benefits for this application scope.
3. **Redis Caching / Celery Task Queue:**
   - *Why Not:* Dashboard calculations and bulk operations run efficiently within PostgreSQL indexed SQL queries and single database transactions. Introducing Redis/Celery adds infrastructure operational cost and setup friction without necessity.
4. **Third-Party AI Integrations:**
   - *Why Not:* Kept focus 100% strictly on core project tracking business rules, reliable state machine transitions, project membership enforcement, and audit logs.
