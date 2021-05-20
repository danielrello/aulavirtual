import datetime

import bleach
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from mistune import markdown
import hashlib
db = None


def init_db(app):
    global db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if db == None:
        db = SQLAlchemy(app)  # class db extends app
    return db


def get_db():
    global db
    if db == None:
        from application import get_app
        app = get_app()
        db = init_db(app)
    return db


from application import get_app

app = get_app()
db = init_db(app)


class User(UserMixin, db.Model):  # User extends db.Model
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(80))
    profile = db.Column(db.String(10), default='student')  # 'admin', 'staff', 'professor', 'student'
    confirmed = db.Column(db.Boolean(), default=False)
    avatar_hash = db.Column(db.String, default='00000000000000000000000000000000')
    userhash = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    course = db.relationship('Course', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')


class Forum(db.Model):
    __tablename__ = 'forums'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posts = db.relationship('Post', backref='forums', lazy='dynamic')
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    forum_id = db.Column(db.Integer, db.ForeignKey('forums.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')


class Activity(db.Model):
    __tablename__ = 'activities'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    activity_uploads = db.Column(db.Text, default='Empty')
    activity_grade = db.Column(db.Integer, default=0)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    result_upload = db.Column(db.Text, default='Empty')
    result_body = db.Column(db.Text)
    result_body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())
    limit_date = db.Column(db.DateTime, default=db.func.curret_timestamp())
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=db.func.current_timestamp())
    disabled = db.Column(db.Boolean, default=None)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))


class Course(UserMixin, db.Model):  # User extends db.Model
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    institution_name = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    code = db.Column(db.String(50), unique=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    follows = db.relationship('Follow', backref='course', lazy=True)
    activities = db.relationship('Activity', backref='course', lazy=True)


class Follow(UserMixin, db.Model):  # User extends db.Model
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course_name = db.Column(db.String(50))
    course_code = db.Column(db.String(50))
    institution_name = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class ParticipationCode(UserMixin, db.Model):  # User extends db.Model
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50))
    code_description = db.Column(db.String(120))
    code_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course_name = db.Column(db.String(50))
    institution_name = db.Column(db.String(50))
    date_expire = db.Column(db.DateTime)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())


class ParticipationRedeem(UserMixin, db.Model):  # User extends db.Model
    id = db.Column(db.Integer, primary_key=True)
    participation_code = db.Column(db.String(50))
    code_description = db.Column(db.String(120))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    course_name = db.Column(db.String(50))
    institution_name = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
