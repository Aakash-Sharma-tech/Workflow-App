# Workflow — Project & Task Tracking

Internal tool for managing client projects, tasks, assignments, and deadlines.

## Tech Stack

- **Backend:** Flask, SQLAlchemy, SQLite
- **Frontend:** Vue 3 (CDN), Bootstrap 5, Font Awesome
- **Auth:** Session-based with role enforcement (Manager / Member)

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Demo Accounts

| Role    | Email                  | Password    |
|---------|------------------------|-------------|
| Manager | manager@workflow.com   | password123 |
| Member  | sam@workflow.com       | password123 |
| Member  | jordan@workflow.com    | password123 |
| Member  | priya@workflow.com     | password123 |

## Features

1. **Accounts & Roles** — Manager vs Member with server-side enforcement
2. **Projects** — Create, edit, archive/restore with team membership
3. **Tasks** — Title, description, priority, due date, dependencies
4. **Task Lifecycle** — Backlog → In Progress → In Review → Done, with Blocked state
5. **Assignment** — Multi-assignee, project-scoped, auto-unassign on member removal
6. **Search & Filters** — Server-side search, filter, sort, pagination
7. **Bulk Actions** — Per-task success/failure reporting + CSV export
8. **Dashboard** — Headline stats, status/assignee breakdown, 8-week completion chart
9. **History** — Immutable audit log with comments
10. **Overdue Alerts** — Dismissible alerts that reappear on due date change

## Project Structure

```
app.py              Application entry point
config.py           Configuration
models/             SQLAlchemy models
routes/             Flask blueprints
services/           Business logic
templates/          Jinja2 + Vue 3 templates
static/             CSS & JS
utils/              Auth decorators
```
