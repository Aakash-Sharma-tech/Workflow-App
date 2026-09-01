from flask import session, url_for, flash, redirect, request, render_template, Blueprint
from models.project_members import ProjectMemberModel
from models.projects import ProjectModel
from utils.permission import require_role
from models import db

bp = Blueprint('project_membership', __name__, url_prefix="/projects")


@bp.route("/<int:project_id>/members", methods=["GET", "POST"])
@require_role("MANAGER")
def project_members(project_id):
    project = ProjectModel.query.get(project_id)
    if not project:
        flash("Project not found", "error")
        return redirect(url_for("project.projects"))

    if request.method == "GET":
        return render_template("project_members.html", project=project)

    user_id = request.form.get("user_id")
    if not user_id:
        flash("User ID is required", "error")
        return redirect(url_for("project_membership.project_members", project_id=project_id))

    existing = ProjectMemberModel.query.filter_by(project_id=project_id, user_id=user_id).first()
    if existing:
        flash("User is already a member of this project", "error")
        return redirect(url_for("project_membership.project_members", project_id=project_id))

    project_member = ProjectMemberModel(project_id=project_id, user_id=int(user_id))
    db.session.add(project_member)
    db.session.commit()
    flash("Member added", "success")
    return redirect(url_for("project_membership.project_members", project_id=project_id))


@bp.route("/<int:project_id>/members/<int:member_id>/delete", methods=["POST"])
@require_role("MANAGER")
def delete_project_member(project_id, member_id):
    project_member = ProjectMemberModel.query.filter_by(project_id=project_id, user_id=member_id).first()
    if not project_member:
        flash("Member not found", "error")
        return redirect(url_for("project_membership.project_members", project_id=project_id))
    db.session.delete(project_member)
    db.session.commit()
    flash("Member removed", "success")
    return redirect(url_for("project_membership.project_members", project_id=project_id))