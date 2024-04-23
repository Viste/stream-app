from functools import wraps

from flask import request, jsonify, session
from flask_login import LoginManager, login_user, logout_user
from models import Customer
from werkzeug.security import check_password_hash


def require_api_key(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == app.config['API_KEY']:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"message": "Unauthorized"}), 401
    return decorated_function


login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


def authenticate_user(username, password):
    user = Customer.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['loggedin'] = True
        session['id'] = user.id
        session['username'] = user.username
        login_user(user)
        return True
    return False


def logout():
    logout_user()
