
# Defining our custom decorator
from functools import wraps

from flask import flash, abort, request
from flask_login import current_user
from sqlalchemy import and_

from models import User, db, Activity, Course


def super_user(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if not current_user.profile in ('professor', 'staff', 'admin'):
            flash("You do not have permission to view that page", "warning")
            abort(404)
        return function(*args, **kwargs)

    return decorated_function

def is_following(function):
    @wraps(function)
    def decorated_function(*args, **kargs):
        follows = User.query.get(current_user.id).courses
        activity = request.args.get('activity_id')
        forum = request.args.get('forum_id')
        if activity or forum:
            User.query.get(current_user.id).filter()