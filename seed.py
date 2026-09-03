from datetime import date, datetime, timedelta

from models import db
from models.user import UserModel
from models.projects import ProjectModel
from models.project_members import ProjectMemberModel
from models.tasks import TaskModel
from models.task_assignees import TaskAssigneeModel
from models.task_dependencies import TaskDependencyModel
from models.comments import CommentModel
from services.history_service import record_creation, record_assignment, record_status_change, record_field_change
from services.alert_service import sync_alerts_for_task


def seed_demo_data():
    if UserModel.query.first():
        return

    today = date.today()
    now = datetime.utcnow()

    alex = UserModel(name="Alex Rivera", email="manager@workflow.com", role="manager")
    alex.set_password("password123")
    sam = UserModel(name="Sam Okonkwo", email="sam@workflow.com", role="member")
    sam.set_password("password123")
    jordan = UserModel(name="Jordan Lee", email="jordan@workflow.com", role="member")
    jordan.set_password("password123")
    priya = UserModel(name="Priya Nair", email="priya@workflow.com", role="member")
    priya.set_password("password123")
    db.session.add_all([alex, sam, jordan, priya])
    db.session.flush()

    web = ProjectModel(
        key="WEB",
        name="Website Redesign",
        description="Full redesign of the client marketing site, including homepage, case studies, and CMS migration.",
        owner_id=alex.id,
    )
    api = ProjectModel(
        key="API",
        name="Billing API",
        description="New invoicing endpoints and webhook delivery for the finance portal.",
        owner_id=alex.id,
    )
    brd = ProjectModel(
        key="BRD",
        name="Brand Refresh",
        description="Visual identity update. Parked after kickoff while legal reviews the trademark set.",
        owner_id=alex.id,
        archived=True,
    )
    db.session.add_all([web, api, brd])
    db.session.flush()

    for project, members in (
        (web, [alex.id, sam.id, jordan.id]),
        (api, [alex.id, sam.id, priya.id]),
        (brd, [alex.id, jordan.id]),
    ):
        for uid in members:
            db.session.add(ProjectMemberModel(project_id=project.id, user_id=uid))

    def make_task(project, title, description, priority, status, due_offset, created_days_ago, assignees, blocked_from=None):
        task = TaskModel(
            project_id=project.id,
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=today + timedelta(days=due_offset) if due_offset is not None else None,
            blocked_from_status=blocked_from,
            created_at=now - timedelta(days=created_days_ago),
            updated_at=now - timedelta(days=max(0, created_days_ago - 3)),
        )
        db.session.add(task)
        db.session.flush()
        record_creation(task, alex)
        for uid in assignees:
            user = UserModel.query.get(uid)
            db.session.add(TaskAssigneeModel(task_id=task.id, user_id=uid))
            record_assignment(task, alex, user.name)
        return task

    web_repo = make_task(
        web, "Set up project repo", "GitHub repo, branch protection, and GitHub Actions for lint and tests.",
        "High", "Done", -18, 40, [sam.id],
    )
    web_repo.updated_at = now - timedelta(weeks=5, days=1)
    record_status_change(web_repo, sam, "Backlog", "In Progress")
    record_status_change(web_repo, sam, "In Progress", "In Review")
    record_status_change(web_repo, alex, "In Review", "Done")

    web_mock = make_task(
        web, "Homepage mockups", "Desktop and mobile mockups for the new homepage hero and case-study grid.",
        "High", "In Review", 2, 21, [jordan.id],
    )
    record_status_change(web_mock, jordan, "Backlog", "In Progress")
    record_status_change(web_mock, jordan, "In Progress", "In Review")

    web_nav = make_task(
        web, "Responsive navigation", "Header, mobile drawer, and skip-to-content behaviour.",
        "Medium", "In Progress", 5, 14, [sam.id],
    )
    record_status_change(web_nav, sam, "Backlog", "In Progress")

    web_api = make_task(
        web, "CMS content endpoints", "Read APIs for pages, case studies, and authors.",
        "Medium", "Backlog", 12, 10, [sam.id],
    )

    web_migrate = make_task(
        web, "Content migration", "Move the existing WordPress pages into the new CMS without breaking URLs.",
        "Low", "Backlog", -4, 16, [jordan.id],
    )
    record_field_change(web_migrate, alex, "due_date", (today + timedelta(days=7)).isoformat(), web_migrate.due_date.isoformat())

    web_qa = make_task(
        web, "Accessibility pass", "Keyboard, contrast, and screen-reader checks on the new templates.",
        "Critical", "Blocked", 8, 9, [jordan.id], blocked_from="In Progress",
    )
    record_status_change(web_qa, jordan, "Backlog", "In Progress")
    record_status_change(web_qa, jordan, "In Progress", "Blocked")

    db.session.add(TaskDependencyModel(task_id=web_api.id, blocking_task_id=web_nav.id))
    db.session.add(TaskDependencyModel(task_id=web_qa.id, blocking_task_id=web_mock.id))

    db.session.add(CommentModel(
        task_id=web_mock.id, user_id=alex.id,
        content="Looks close. Can we try a quieter hero so the case studies don't compete?",
        created_at=now - timedelta(days=1),
    ))
    db.session.add(CommentModel(
        task_id=web_qa.id, user_id=jordan.id,
        content="Blocked until the homepage mockups are signed off — contrast depends on the final palette.",
        created_at=now - timedelta(hours=6),
    ))

    api_spec = make_task(
        api, "OpenAPI spec", "Document invoice CRUD and webhook payloads.",
        "High", "Done", -10, 28, [priya.id],
    )
    api_spec.updated_at = now - timedelta(weeks=3, days=2)
    record_status_change(api_spec, priya, "Backlog", "In Progress")
    record_status_change(api_spec, priya, "In Progress", "In Review")
    record_status_change(api_spec, alex, "In Review", "Done")

    api_auth = make_task(
        api, "Service authentication", "API keys plus scoped tokens for the finance portal.",
        "Critical", "In Progress", 3, 12, [sam.id],
    )
    record_status_change(api_auth, sam, "Backlog", "In Progress")

    api_webhooks = make_task(
        api, "Webhook delivery", "Retry queue, signature headers, and dead-letter logging.",
        "High", "Backlog", 14, 8, [sam.id, priya.id],
    )

    api_overdue = make_task(
        api, "Sandbox invoice fixtures", "Seed data so finance can try the portal before go-live.",
        "Medium", "In Review", -2, 11, [priya.id],
    )
    record_status_change(api_overdue, priya, "Backlog", "In Progress")
    record_status_change(api_overdue, priya, "In Progress", "In Review")

    db.session.add(TaskDependencyModel(task_id=api_webhooks.id, blocking_task_id=api_auth.id))

    db.session.add(CommentModel(
        task_id=api_overdue.id, user_id=sam.id,
        content="Fixtures look good. One sample invoice is still using last year's tax rate.",
        created_at=now - timedelta(days=2),
    ))

    brd_audit = make_task(
        brd, "Asset inventory", "Collect current logos, fonts, and restricted colour uses.",
        "Low", "Done", -30, 50, [jordan.id],
    )
    brd_audit.updated_at = now - timedelta(weeks=7)
    record_status_change(brd_audit, jordan, "Backlog", "In Progress")
    record_status_change(brd_audit, alex, "In Progress", "In Review")
    record_status_change(brd_audit, alex, "In Review", "Done")

    brd_legal = make_task(
        brd, "Trademark review", "Legal sign-off on the wordmark before we print anything.",
        "High", "Backlog", 45, 20, [alex.id],
    )

    db.session.commit()

    for task in TaskModel.query.all():
        sync_alerts_for_task(task)
    db.session.commit()
