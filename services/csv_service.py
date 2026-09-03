import csv
import io
from datetime import datetime, date, timedelta


def generate_csv(tasks):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Project", "Title", "Status", "Priority",
        "Due Date", "Assignees", "Overdue", "Updated"
    ])
    for t in tasks:
        assignees = ", ".join(a.user.name for a in t.assignees)
        writer.writerow([
            t.id,
            t.project.key if t.project else "",
            t.title,
            t.status,
            t.priority,
            t.due_date.isoformat() if t.due_date else "",
            assignees,
            "Yes" if t.is_overdue else "No",
            t.updated_at.strftime("%Y-%m-%d %H:%M") if t.updated_at else "",
        ])
    return output.getvalue()
