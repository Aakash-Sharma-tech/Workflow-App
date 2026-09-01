from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import db, UserModel

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login')
def login():
    return render_template('login.html')

@auth_bp.route('/login',methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if role == 'MANAGER':
            user = UserModel.query.filter_by(email=email,role='MANAGER').first()
    elif role == 'MEMBER':
        user = UserModel.query.filter_by(email=email,role='MEMBER').first()    if user and user.check_password(password):
        session['user_id'] = user.id
        return redirect(url_for('projects.list_projects'))
    else:
        return render_template('login.html')


