# Database Schema & Entity Design

## Table Specifications & Columns

### 1. `users`
- `id` (INTEGER, Primary Key, Auto-increment)
- `email` (VARCHAR(120), Unique, Not Null, Indexed)
- `password_hash` (VARCHAR(256), Not Null)
- `full_name` (VARCHAR(100), Not Null)
- `role` (VARCHAR(20), Not Null — `'MANAGER'` or `'MEMBER'`, Default `'MEMBER'`)
- `created_at` (DATETIME, Default UTC Now)

### 2. `projects`
- `id` (INTEGER, Primary Key, Auto-increment)
- `project_key` (VARCHAR(10), Unique, Not Null, Indexed)
- `name` (VARCHAR(100), Not Null)
- `description` (TEXT)
- `is_archived` (BOOLEAN, Default False, Indexed)
- `owner_id` (INTEGER, Foreign Key → `users.id`, Not Null)
- `created_at` (DATETIME, Default UTC Now)

### 3. `project_members`
- `id` (INTEGER, Primary Key, Auto-increment)
- `project_id` (INTEGER, Foreign Key → `projects.id`, On Delete CASCADE, Not Null)
- `user_id` (INTEGER, Foreign Key → `users.id`, On Delete CASCADE, Not Null)
- `joined_at` (DATETIME, Default UTC Now)
- *Unique Constraint:* `(project_id, user_id)`

### 4. `tasks`
- `id` (INTEGER, Primary Key, Auto-increment)
- `project_id` (INTEGER, Foreign Key → `projects.id`, On Delete CASCADE, Not Null, Indexed)
- `title` (VARCHAR(200), Not Null)
- `description` (TEXT, Not Null)
- `status` (VARCHAR(20), Default `'Backlog'`, Indexed)
- `priority` (VARCHAR(20), Default `'Medium'`, Indexed)
- `due_date` (DATETIME, Nullable, Indexed)
- `blocked_from_status` (VARCHAR(20), Nullable — tracks state prior to being marked Blocked)
- `created_by` (INTEGER, Foreign Key → `users.id`, Not Null)
- `created_at` (DATETIME, Default UTC Now)
- `updated_at` (DATETIME, Default UTC Now, On Update UTC Now)
- `completed_at` (DATETIME, Nullable — timestamp when status transitioned to `'Done'`)

### 5. `task_assignees`
- `id` (INTEGER, Primary Key, Auto-increment)
- `task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null)
- `user_id` (INTEGER, Foreign Key → `users.id`, On Delete CASCADE, Not Null)
- `assigned_at` (DATETIME, Default UTC Now)
- *Unique Constraint:* `(task_id, user_id)`

### 6. `task_dependencies`
- `id` (INTEGER, Primary Key, Auto-increment)
- `task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null — target task)
- `blocking_task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null — blocker task)
- `dependency_type` (VARCHAR(20), Default `'blocks'`)
- `created_at` (DATETIME, Default UTC Now)
- *Unique Constraint:* `(task_id, blocking_task_id)`

### 7. `task_history`
- `id` (INTEGER, Primary Key, Auto-increment)
- `task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null, Indexed)
- `user_id` (INTEGER, Foreign Key → `users.id`, Not Null)
- `action` (VARCHAR(50), Not Null — e.g. `'created'`, `'status_changed'`, `'assignee_added'`, `'assignee_removed'`, `'dependency_added'`, `'dependency_removed'`, `'comment_added'`)
- `field_name` (VARCHAR(50), Nullable)
- `old_value` (TEXT, Nullable)
- `new_value` (TEXT, Nullable)
- `created_at` (DATETIME, Default UTC Now, Indexed)

### 8. `comments`
- `id` (INTEGER, Primary Key, Auto-increment)
- `task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null, Indexed)
- `user_id` (INTEGER, Foreign Key → `users.id`, Not Null)
- `content` (TEXT, Not Null)
- `created_at` (DATETIME, Default UTC Now)

### 9. `alerts`
- `id` (INTEGER, Primary Key, Auto-increment)
- `user_id` (INTEGER, Foreign Key → `users.id`, On Delete CASCADE, Not Null, Indexed)
- `task_id` (INTEGER, Foreign Key → `tasks.id`, On Delete CASCADE, Not Null, Indexed)
- `dismissed` (BOOLEAN, Default False, Indexed)
- `dismissed_at` (DATETIME, Nullable)
- `created_at` (DATETIME, Default UTC Now)
- *Unique Constraint:* `(user_id, task_id)`

---

## Entity Relationships

- **One-to-Many Relationships:**
  - `UserModel` → `ProjectModel` (as Owner)
  - `UserModel` → `TaskHistoryModel`
  - `UserModel` → `CommentModel`
  - `ProjectModel` → `TaskModel`
  - `TaskModel` → `TaskHistoryModel`
  - `TaskModel` → `CommentModel`
  - `TaskModel` → `AlertModel`

- **Many-to-Many Relationships (Implemented via Junction Models):**
  - `UserModel` ↔ `ProjectModel` through `ProjectMemberModel` (`project_members`)
  - `UserModel` ↔ `TaskModel` through `TaskAssigneeModel` (`task_assignees`)
  - `TaskModel` ↔ `TaskModel` self-referential relationship through `TaskDependencyModel` (`task_dependencies`)

---

## Database vs. Application Constraints

- **Database Constraints:**
  - Primary keys, foreign keys, non-null column types.
  - Unique constraints (`users.email`, `projects.project_key`, `(project_id, user_id)`, `(task_id, user_id)`, `(task_id, blocking_task_id)`).
  - Cascade deletion on project/task cleanup (`ON DELETE CASCADE`).

- **Application Constraints (Service Layer):**
  - State machine transition validity (`TaskStateMachine.change_state`).
  - Unfinished blocker rule (preventing transition to `Done` if blocking tasks are not completed).
  - Project membership requirement for task assignments (user must belong to `project_members`).
  - Same-project dependency constraint (`blocking.project_id == task.project_id`).
  - Automatic task unassignment upon project member removal.
  - Role-based authorization (`MANAGER` vs `MEMBER` endpoints).

- **Rationale:** Structural integrity and cardinality are enforced at the database layer, while dynamic business logic and state machine workflows reside in Python services for maintainability, testing clarity, and custom error messaging.

---

## Deliberate Denormalisation

- Storing human-readable string values (`old_value`, `new_value`) in `task_history` alongside action keys.
- Storing `completed_at` directly on `TaskModel` to make weekly completed task metrics queries fast without scanning the `task_history` table for status events.

---

## Performance Bottlenecks at 100x Scale

1. **Dashboard Weekly Completion Chart Aggregation:** Scanning all `tasks` for `completed_at` timestamps. *Solution at scale:* Materialized view or redis cache of weekly completion totals.
2. **Timeline Queries:** `task_history` table growth under high activity. *Solution at scale:* Table partitioning by `created_at` or `task_id` ranges.
3. **Full-Text Task Search:** SQL `LIKE %search%` queries over `title` and `description`. *Solution at scale:* PostgreSQL `tsvector` GIN indexing or Elasticsearch.
