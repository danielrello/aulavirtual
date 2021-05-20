import datetime

import timeago
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import current_user, login_required

from models import User, Course, Activity, Follow, db
from module003.forms import ActivityForm

module003 = Blueprint("module003", __name__, static_folder="static", template_folder="templates")


@module003.route('/')
def module003_index():
    page = request.args.get('page', 1, type=int)
    query = Course.query
    courses_author_pagination = query.filter_by(user_id=current_user.id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    follow_courses = Follow.query
    pagination = follow_courses.filter_by(user_id=current_user.id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    follows = pagination.items
    courses_author = courses_author_pagination.items
    courses = []
    for course in courses_author:
        if course.id is not None:
            author = User.query.get(course.user_id)
            course.author = author
        for activity in course.activities:
            activity.limit_datestr = activity.limit_date.strftime("%Y-%m-%d %H:%M:%S")
        courses.append(course)
    for follow in follows:
        course = Course.query.get(follow.course_id)
        if course.id is not None:
            author = User.query.get(course.user_id)
            course.author = author
        for activity in course.activities:
            activity.limit_datestr = activity.limit_date.strftime("%Y-%m-%d %H:%M:%S")
        courses.append(course)
    return render_template("module003_index.html", module='module003', courses=courses)


@module003.route('/activity', methods=['GET'])
@login_required
def module003_single_activity():
    activity_id = request.args.get('id')
    query = Activity.query
    activity = query.get(activity_id)
    activity.timeago = timeago.format(activity.timestamp, datetime.datetime.now())
    activity.time_left = activity.limit_date.strftime("%Y-%m-%d %H:%M:%S")
    return render_template('module003_single_activity.html', module="module003", activity=activity)

@module003.route('/new_activity', methods=['GET', 'POST'])
@login_required
def module003_new_activity():
    form = ActivityForm()
    for course in Course.query.filter(Course.user_id == current_user.id):
        form.course_id.choices += [(course.id, str(course.id) + '-' + course.name + '-' + course.institution_name)]
    for i in range(0, 25):
        form.limit_hour.choices += [str(i)]
    for i in range(0, 61):
        form.limit_min.choices += [str(i)]
        form.limit_sec.choices += [str(i)]
    if request.method == 'POST':
        form_limit = form.limit_date.data.strftime("%Y-%m-%d")
        form_limit += " " + form.limit_hour.data + ":" + form.limit_min.data + ":" + form.limit_sec.data
        limit_date = datetime.datetime.strptime(form_limit, "%Y-%m-%d %H:%M:%S")
        if current_user.is_authenticated and form.validate_on_submit():
            activity = Activity(author_id=current_user.id,
                                title=form.title.data,
                                course_id=form.course_id.data,
                                body=form.body.data,
                                limit_date=limit_date)
            try:
                db.session.add(activity)
                db.session.commit()
            except Exception as error:
                flash(str(error.orig) + " for parameters" + str(error.params))
            flash("Successfully created a new activity")
            return redirect(url_for('module003.module003_index'))
        else:
            flash("Couldn't create a new activity")

    return render_template('module003_new_activity.html', module="module003", form=form)


@module003.route('/test')
def module003_test():
    return 'OK'
