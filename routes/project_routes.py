from flask import request, redirect, session, url_for, flash, render_template, Blueprint
from utils.permission import require_role, require_login
from models.projects import ProjectModel
from models.project_members import ProjectMemberModel
from models import db

bp = Blueprint("project", __name__)


@bp.route("/projects", methods=["GET", "POST"])
@require_login()
def projects():
    if request.method == "GET":
        user_id = session.get("user_id")
        user_role = session.get("user_role")
        # Managers see all non-archived projects; members only see their own
        if user_role == "MANAGER":
            all_projects = ProjectModel.query.filter_by(is_archived=False).all()
        else:
            all_projects = ProjectModel.query.filter(
                ProjectModel.members.any(user_id=user_id),
                ProjectModel.is_archived == False
            ).all()
        return render_template("projects.html", projects=all_projects)

    # POST — create project (MANAGER only)
    if session.get("user_role") != "MANAGER":
        flash("Only managers can create projects", "error")
        return redirect(url_for("project.projects"))

    project_key = request.form.get("project_key")
    name = request.form.get("name")
    description = request.form.get("description")

    if not all([project_key, name, description]):
        flash("All fields are required", "error")
        return redirect(url_for("project.projects"))

    project = ProjectModel(
        project_key=project_key,
        name=name,
        description=description,
        owner_id=session["user_id"],
    )
    db.session.add(project)
    db.session.commit()
    flash("Project created", "success")
    return redirect(url_for("project.projects"))


@bp.route("/projects/<int:project_id>", methods=["GET", "POST"])
@require_login()
def project(project_id):
    proj = ProjectModel.query.get(project_id)
    if not proj:
        flash("Project not found", "error")
        return redirect(url_for("project.projects"))

    if request.method == "GET":
        return render_template("project.html", project=proj)

    if session.get("user_role") != "MANAGER":
        flash("Only managers can edit projects", "error")
        return redirect(url_for("project.project", project_id=project_id))

    proj.name = request.form.get("name", proj.name)
    proj.description = request.form.get("description", proj.description)
    db.session.commit()
    flash("Project updated", "success")
    return redirect(url_for("project.project", project_id=proj.id))


@bp.route("/projects/<int:project_id>/archive", methods=["POST"])
@require_role("MANAGER")
def archive_project(project_id):
    proj = ProjectModel.query.get(project_id)
    if not proj:
        flash("Project not found", "error")
        return redirect(url_for("project.projects"))
    proj.is_archived = True
    db.session.commit()
    flash("Project archived", "success")
    return redirect(url_for("project.projects"))


@bp.route("/projects/<int:project_id>/restore", methods=["POST"])
@require_role("MANAGER")
def restore_project(project_id):
    proj = ProjectModel.query.get(project_id)
    if not proj:
        flash("Project not found", "error")
        return redirect(url_for("project.projects"))
    proj.is_archived = False
    db.session.commit()
    flash("Project restored", "success")
    return redirect(url_for("project.projects"))