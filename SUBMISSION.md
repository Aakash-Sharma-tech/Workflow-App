# Submission

Fill this in and commit it. This is the first file we open.

## Links

- **GitHub repository:** https://github.com/Aakash-Sharma-tech/Workflow-App
- **Live application:** https://workflow-app-pqmy.onrender.com/

## Notes for the reviewer

The application is fully implemented using Flask, SQLAlchemy, Vue 3 via CDN, Bootstrap 5, Bootstrap Icons, and Chart.js.

- Role-based authorization (`MANAGER` vs `MEMBER`) is strictly enforced on the server.
- Seed data script (`seed.py`) populates manager and member accounts, projects, tasks, dependencies, comments, and alerts for testing.
- All 10 mandatory business rules verified against server endpoints.

- **Deployment & Cold Start Notice (Render Free Tier):**
  - **Cold Start:** The instance spins down after 15 minutes of inactivity. Please allow **30–60 seconds** for the initial request to wake the server.
  - **Resource Allocation:** Hosted on Render's free tier (0.1 vCPU), so API response latency may be slightly higher than standard production environments.

## Demo credentials

| Role | Email | Password |
|------|-------|----------|
| Manager | manager@workflow.com | password123 |
| Member | sam@workflow.com | password123 |
| Member | jordan@workflow.com | password123 |
| Member | priya@workflow.com | password123 |

## Stack

| Layer | What you used | Why |
|-------|---------------|-----|
| Frontend | Vue 3 CDN + Bootstrap 5 + Bootstrap Icons | Lightweight, reactive, instant rendering without build toolchain overhead |
| Backend | Flask + Python 3 | Clean MVC architecture with service-layer business logic separation |
| Database | SQLite3 (Local) / PostgreSQL (Prod) + SQLAlchemy | Robust relational model, ACID compliance, ORM relationship mapping |
| Hosting | Koyeb / Render + Gunicorn | Free-tier POSIX deployment support with WSGI runner |

## Goal checklist

| # | Goal | Status | Notes |
|---|------|--------|-------|
| 1 | Accounts and roles | Done | Server-enforced Manager vs Member roles |
| 2 | Projects | Done | CRUD, project keys, archive and restore |
| 3 | Tasks inside projects | Done | Project-scoped, title, description, priority, due date, blockers |
| 4 | A task lifecycle with rules | Done | Backlog → In Progress → In Review → Done, Blocked state, state machine enforcement, unfinished blocker check |
| 5 | Assignment | Done | Multi-assignee, project-membership rule, auto-unassign on member removal |
| 6 | Finding things | Done | Server-side search, filter, sort, pagination with match counts |
| 7 | Acting on many tasks at once | Done | Bulk status, assignee, due date changes with per-task success/error report + CSV export |
| 8 | A dashboard | Done | Headline stats, status breakdown, assignee breakdown, 8-week completion chart |
| 9 | History you cannot rewrite | Done | Immutable timeline recording creations, status updates, assignees, dependencies, due date changes, comments |
| 10 | Overdue alerts | Done | Active overdue alerts badge count, dismissal, auto-reappearance on due date update |

## How much time did you actually spend?

Approximately 14 hours total across planning, database design, backend services, API routes, HTML templates with Vue 3 CDN, testing, and documentation.

## What would you do next, with another 12 hours?

1. Build an interactive drag-and-drop Kanban board view for task statuses.
2. Implement multi-hop dependency cycle detection across blocking task chains.
3. Add `@-mention` notification alerts inside task comments.
4. Add user profile picture uploads and custom email notifications.

## What are you least happy with in this codebase, and why?

While embedding Vue 3 CDN directly inside Jinja2 HTML templates avoided build system complexity and CORS issues, wrapping script blocks in `{% raw %}` guards can feel slightly verbose when writing complex inline Vue reactive components. A lightweight Vue component loader could make frontend template maintenance even cleaner.
