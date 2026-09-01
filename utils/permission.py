from flask import request, redirect, url_for, session, flash
from functools import wraps

def require_role(role):
    """
    Decorator to ensure a user is logged in and has the specified role.
    
    Usage:
    @require_role('MANAGER')
    @bp.route('/some-route')
    def some_handler():
        pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in session:
                flash('You need to be logged in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            # Check if user has the required role
            user_role = session.get('user_role')
            if user_role != role:
                flash(f'Access denied. You must be a {role.upper()}.', 'error')
                # Redirect based on role to avoid infinite loops
                if user_role == 'MANAGER':
                    return redirect(url_for('manager.dashboard'))
                elif user_role == 'MEMBER':
                    return redirect(url_for('member.dashboard'))
                else:
                    return redirect(url_for('auth.login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_login():
    """
    Decorator to ensure a user is logged in, regardless of role.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('You need to be logged in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator