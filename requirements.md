# Assignment 01 — Project & Task Tracking

## The scenario

Picture a services company running work for a dozen or so client projects at any given time — some
short engagements, some long retainers, each with its own priorities and its own deadlines. The same
people often work more than one of these projects in a given week, moving between them as things get
busy or quiet. Right now none of that coordination lives in one place: task lists sit in
spreadsheets that only one person remembers to update, status gets typed into chat threads and then
scrolls out of view, and due dates mostly exist in people's heads.

The result is predictable. A manager finds out a deadline was missed when the client brings it up,
not before. Nobody can answer 'what is overdue' across the whole portfolio with any confidence, or
say which of their people is quietly buried under four projects while another has nothing this week.
When someone asks why a task stalled, the honest answer is usually to go ask around, and by the time
an answer comes back the moment to do anything about it has often passed.

They want one internal tool to replace all of it: somewhere managers set up projects, decide who is
on each one, and see the whole portfolio at a glance, and somewhere staff go to see what is theirs
and move it forward. Anyone should be able to get a straight answer to 'what is overdue' or 'who is
overloaded' without asking around to find out. That is what you are building.

## What it must do

Everything below is required. Several of the ten spell out exact rules — what happens on an illegal
move, what a bulk action must report back, when a dismissed alert is allowed to reappear — and those
specifics are the actual ask, not just the bold headline in front of them.

1. **Accounts and roles.** People sign in with an email and password, and there are at least two
roles — a manager role and a regular member role. Managers can create and archive projects, change
who is on a project, and delete tasks. Members can do neither, and only see projects they belong to.
The difference must be enforced on the server, not just hidden in the interface.

2. **Projects.** Managers create projects with a short key, a name, a description and an owner, and
can edit them later. Projects can be archived and restored. Archiving hides a project from the
default views without destroying its data or its tasks.

3. **Tasks inside projects.** Every task belongs to exactly one project and carries a title, a
description, a priority, an optional due date, and any number of other tasks in the same project
that block it. Tasks can be created, edited, and deleted. Opening a project shows its tasks.

4. **A task lifecycle with rules.** A task moves through *Backlog → In Progress → In Review → Done*,
and can be marked *Blocked* from either In Progress or In Review. Unblocking returns it to the state
it was blocked from. A finished task can be reopened. A task with an unfinished blocking task cannot
move to Done — the server rejects the attempt. Any other jump — Backlog straight to Done, for
instance — must be rejected by the server with a message explaining why, and the interface should
only offer the moves that are currently legal.

5. **Assignment.** A task can have any number of people assigned to it, and a person can hold many
tasks. Only members of a task's project may be assigned to it, and removing someone from a project
unassigns them from that project's tasks. Every user can see one list of everything assigned to them
across all projects.

6. **Finding things.** One list shows tasks across every project the viewer can see, with a text
search over titles and descriptions, filters for project, status, assignee, priority and overdue,
sorting by due date, priority or last update, and pagination showing the total number of matches.
All of this must be done by the server — do not load every task into the browser and filter there.

7. **Acting on many tasks at once.** Select several tasks from the list and apply one change to all
of them: a status move, an assignee change, or a new due date. Because some of those changes will be
illegal for some tasks, the result must report per task what succeeded and what was rejected and why
— not just fail the whole batch. Separately, export the currently filtered list as a CSV file.

8. **A dashboard.** A landing view shows headline numbers — open tasks, overdue tasks, due this
week, completed this week. It also breaks tasks down by status and by assignee, and charts
completions over the last eight weeks.

9. **History you cannot rewrite.** Every task has a timeline showing when it was created, every
field change with the old and new value and who made it, every assignment and unassignment, and any
comments people have left. Comments are part of this timeline. Nothing in the timeline can be edited
or deleted after the fact, including by managers.

10. **Overdue alerts.** Tasks that are past their due date and not finished appear in an alerts
area, with a count badge visible in the navigation. A person can dismiss an alert for a task they
are assigned to. If that task's due date later changes, the alert comes back.

## Stretch ideas (optional)

None of these are required, and none substitute for a goal above. If you finish all ten with time
left over, pick whichever of these sounds most useful and build it:

- A drag-and-drop board view.
- Cycle detection across chains of task dependencies, beyond a single blocking relationship.
- Time tracking.
- Saved filter views.
- @-mentions in comments.


Tech Stack:

Frontend: Vue3 CDN in HTML files , CSS, Bootstrap, JS
Backend: Flask
DB: SQlite3, SQLAlchemy ORM
Extra: Fontawesome

