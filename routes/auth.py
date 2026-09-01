from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models import db, UserModel

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')

    if not email or not password or not role:
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.login'))

    if role == 'MANAGER':
        user = UserModel.query.filter_by(email=email, role='MANAGER').first()
    elif role == 'MEMBER':
        user = UserModel.query.filter_by(email=email, role='MEMBER').first()
    else:
        flash('Invalid role selected.', 'error')
        return redirect(url_for('auth.login'))

    if user and user.check_password(password):
        session['user_id'] = user.id
        session['user_role'] = user.role
        flash(f'{role.capitalize()} login successful', 'success')
        if role == 'MANAGER':
            return redirect(url_for('manager.dashboard'))
        else:
            return redirect(url_for('member.dashboard'))
    else:
        flash('Invalid email or password.', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    username = request.form.get('username')
    email = request.form.get('email')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    role = request.form.get('role')

    # Validate all fields are present
    if not all([username, email, first_name, last_name, password, confirm_password, role]):
        flash('Please fill in all fields', 'error')
        return redirect(url_for('auth.signup'))

    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth.signup'))

    if role not in ('MANAGER', 'MEMBER'):
        flash('Invalid role selected.', 'error')
        return redirect(url_for('auth.signup'))

    existing_user = UserModel.query.filter(
        (UserModel.username == username) | (UserModel.email == email)
    ).first()

    if existing_user:
        flash('Username or email already exists', 'error')
        return redirect(url_for('auth.signup'))

    try:
        new_user = UserModel(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during registration. Please try again.', 'error')
        return redirect(url_for('auth.signup'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))
