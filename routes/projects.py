from flask import Blueprint, render_template, request, jsonify, g, flash, redirect, url_for
from models import db
from models.projects import ProjectModel
from models.user import UserModel
from utils.permission import require_login, require_role
from services.project_service import (
    create_project, update_project, archive_project,
    restore_project, get_projects_for_user,
)
from services.project_membership_service import add_member, remove_member, is_project_member
from services.alert_service import get_alert_count

projects_bp = Blueprint("projects", __name__)


@projects_bp.route("/projects")
@require_login
def list_projects():
    show_archived = request.args.get("archived") == "true" and g.current_user.is_manager
    projects = get_projects_for_user(g.current_user, archived_only=show_archived)
    alert_count = get_alert_count(g.current_user)
    template = "manager/projects.html" if g.current_user.is_manager else "member/projects.html"
    return render_template(
        template, projects=projects, user=g.current_user,
        alert_count=alert_count, show_archived=show_archived,
    )


@projects_bp.route("/projects/<int:project_id>")
@require_login
def view_project(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    if not is_project_member(g.current_user, project_id):
        flash("You do not have access to this project.", "danger")
        return redirect(url_for("projects.list_projects"))
    members = [m.user for m in project.members]
    all_users = UserModel.query.order_by(UserModel.name).all() if g.current_user.is_manager else []
    alert_count = get_alert_count(g.current_user)
    template = "manager/project_detail.html" if g.current_user.is_manager else "member/project_detail.html"
    return render_template(
        template, project=project, members=members,
        all_users=all_users, user=g.current_user, alert_count=alert_count,
    )


@projects_bp.route("/api/projects", methods=["GET"])
@require_login
def api_list():
    include_archived = request.args.get("archived") == "true"
    projects = get_projects_for_user(g.current_user, include_archived=include_archived)
    return jsonify([p.to_dict() for p in projects])


@projects_bp.route("/api/projects", methods=["POST"])
@require_role("manager")
def api_create():
    data = request.get_json(silent=True) or {}
    project, error = create_project(data, g.current_user)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(project.to_dict()), 201


@projects_bp.route("/api/projects/<int:project_id>", methods=["PUT"])
@require_role("manager")
def api_update(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    data = request.get_json()
    project, error = update_project(project, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify(project.to_dict())


@projects_bp.route("/api/projects/<int:project_id>/archive", methods=["POST"])
@require_role("manager")
def api_archive(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    archive_project(project)
    return jsonify(project.to_dict())


@projects_bp.route("/api/projects/<int:project_id>/restore", methods=["POST"])
@require_role("manager")
def api_restore(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    restore_project(project)
    return jsonify(project.to_dict())


@projects_bp.route("/api/projects/<int:project_id>/members", methods=["POST"])
@require_role("manager")
def api_add_member(project_id):
    project = ProjectModel.query.get_or_404(project_id)
    data = request.get_json()
    ok, error = add_member(project, data["user_id"])
    if not ok:
        return jsonify({"error": error}), 400
    db.session.commit()
    return jsonify({"success": True})


@projects_bp.route("/api/projects/<int:project_id>/members/<int:user_id>", methods=["DELETE"])
@require_role("manager")
def api_remove_member(project_id, user_id):
    project = ProjectModel.query.get_or_404(project_id)
    ok, error = remove_member(project, user_id)
    if not ok:
        return jsonify({"error": error}), 400
    db.session.commit()
    return jsonify({"success": True})
