"""
CSVService — stream a query result as a downloadable CSV.

Reuses get_tasks_query() so listing and export always apply identical filters.
"""

import csv
import io
from flask import Response
from models.task_assignees import TaskAssigneeModel
from models.user import UserModel


def generate_csv(query):
    """
    Accept a SQLAlchemy query of TaskModel rows.
    Return a Flask Response with text/csv content type.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "ID", "Title", "Description", "Status", "Priority",
        "Project ID", "Created By", "Assignees",
        "Due Date", "Created At", "Completed At",
    ])

    for task in query.all():
        # Resolve assignee names
        assignee_names = []
        for a in task.assignees:
            user = UserModel.query.get(a.user_id)
            if user:
                assignee_names.append(f"{user.first_name} {user.last_name}")

        writer.writerow([
            task.id,
            task.title,
            task.description,
            task.status,
            task.priority,
            task.project_id,
            task.created_by,
            "; ".join(assignee_names),
            task.due_date.strftime("%Y-%m-%d") if task.due_date else "",
            task.created_at.strftime("%Y-%m-%d %H:%M") if task.created_at else "",
            task.completed_at.strftime("%Y-%m-%d %H:%M") if task.completed_at else "",
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tasks_export.csv"},
    )
