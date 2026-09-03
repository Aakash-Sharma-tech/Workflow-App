from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from models import db
from models.user import UserModel

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def landing():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return render_template("index.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = UserModel.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            return redirect(url_for("dashboard.index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "member")
        if role not in ("manager", "member"):
            role = "member"
        if not name or not email or not password:
            flash("All fields are required.", "danger")
        elif UserModel.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
        else:
            user = UserModel(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            return redirect(url_for("dashboard.index"))
    return render_template("signup.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.landing"))
