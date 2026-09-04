# Architectural Decisions

Log of key decisions that shaped this codebase where a real alternative existed.

---

## Decision 1: Single Flask MVC Application vs. Separate Frontend API & SPA Deployments

- **Chose:** Single unified Flask MVC application serving Vue 3 CDN templates directly from Flask `templates/`.
- **Rejected:** Building a separate Vue 3 / Vite Node SPA app deployed independently from a Flask REST API.
- **Why:** Avoids CORS configuration issues, eliminates dual-host cold start latency during evaluator testing, and simplifies deployment to a single production web service on Render.

---

## Decision 2: Server-Side State Machine for Task Status Lifecycle

- **Chose:** Encapsulating all task status rules (`Backlog → In Progress → In Review → Done`, `Blocked → Unblock`) inside a dedicated Python `TaskStateMachine` service class.
- **Rejected:** Allowing direct status string mutations in API route handlers or relying on frontend UI state checks.
- **Why:** Keeps the backend as the single source of truth. Invalid status jumps (e.g. Backlog directly to Done, or attempting to complete a task with unfinished blockers) are rejected on the server even if manually invoked via API calls.

---

## Decision 3: Atomic Transactional Processing for Bulk Task Operations

- **Chose:** Applying bulk task operations iteratively in a single database transaction with per-task error capture (`BulkTaskService`), returning an explicit breakdown report of successes and failures.
- **Rejected:** Rolling back the entire batch if a single task update fails, or silently ignoring failed tasks.
- **Why:** Requirement #7 explicitly mandates reporting per task what succeeded and what was rejected and why, allowing partial batch execution rather than all-or-nothing failure.

---

## Decision 4: Vue 3 Component Architecture Approach

- **Chose:** Embedding Vue 3 CDN apps directly inside Flask Jinja2 HTML templates wrapped in Jinja `{% raw %}` guards.
- **Rejected:** Maintaining separate external `.js` component files for every page view.
- **Later reversed:** Initially, frontend logic was split into external JavaScript files (`dashboard.js`, `projects.js`, `tasks.js`). However, this created script loading order dependency issues, broke Jinja template variable injection, and complicated role-based page customization. We reversed this approach and embedded self-contained Vue 3 CDN script blocks directly inside HTML template files, ensuring immediate page load without external asset fetching errors.

---

## Decision 5: Denormalized Audit Trail in `task_history`

- **Chose:** Storing human-readable string values for `old_value` and `new_value` alongside immutable action keys in the `task_history` table.
- **Rejected:** Storing entity ID foreign keys or dynamic JSON diff objects in the history table.
- **Why:** Ensures audit records remain readable and permanent even if target entities (e.g., deleted users or removed dependencies) are later altered or purged from the database.

---

## Decision 6: Session-Based Cookie Authentication vs. Stateless Bearer JWT Tokens

- **Chose:** Flask session-based cookie authentication (`flask-login` / encrypted session cookie).
- **Rejected:** Stateless JWT bearer tokens stored in `localStorage` and sent via `Authorization` HTTP headers.
- **Why:** The application is a unified Flask web app serving Vue 3 CDN pages. Browser cookies automatically handle session attachment for page navigation and API `fetch` requests without requiring complex client-side token storage, token refresh logic, or XSS risk in `localStorage`.

---

## Decision 7: Server-Side Query Filtering & Pagination vs. Client-Side In-Memory Filtering

- **Chose:** Dynamic SQL filtering, sorting, and offset/limit pagination at the database level inside `TaskService.list_tasks`.
- **Rejected:** Fetching all tasks into browser memory and executing search/filter array operations in Vue JavaScript state.
- **Why:** Requirement #6 specifically mandates server-side search, filtering, and pagination. Server-side SQL filtering scales efficiently to thousands of task records, minimizes payload sizes over the network, and ensures accurate count totals for pagination metadata.

---

## Decision 8: SQLAlchemy Model Hybrid Properties for Computed Attributes vs. Controller Recalculation

- **Chose:** SQLAlchemy `@hybrid_property` definitions (e.g., `is_overdue`, `is_blocked`) and model helper properties.
- **Rejected:** Recalculating computed status fields inside every route controller handler or HTML template rendering context.
- **Why:** Encapsulates domain logic directly on the data models, guaranteeing consistent property evaluation across API JSON serialization, CSV exports, alert checks, and seed scripts without duplicating code.

---

## Decision 9: Soft Assignment Cleanup on Member Removal vs. Hard Foreign Key Cascading

- **Chose:** Cleaning up task assignments (`TaskAssigneeModel`) and logging audit history events when removing a member from a project, while preserving the project and tasks.
- **Rejected:** Hard deleting user records or cascading destructive deletions to task history and comments.
- **Why:** Preserves system auditability. Removing a user from a project gracefully unassigns them from tasks in that project per Requirement #5, but keeps historical task records, comments, and audit entries intact for review.
