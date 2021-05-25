import datetime
import os

import timeago
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, send_from_directory
from flask_login import current_user, login_required
from sqlalchemy import and_
from werkzeug.utils import secure_filename

from flask_app_running import app
from models import User, Course, Activity, db, ActivityResult
from module003.forms import ActivityForm, ActivityResultForm

module003 = Blueprint("module003", __name__, static_folder="static", template_folder="templates")


@module003.route('/')
def module003_index():
    page = request.args.get('page', 1, type=int)
    query = Course.query
    courses_author_pagination = query.filter_by(user_id=current_user.id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    follows = User.query.get(current_user.id).courses
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
        author = User.query.get(follow.user_id)
        follow.author = author
        for activity in follow.activities:
            activity.limit_datestr = activity.limit_date.strftime("%Y-%m-%d %H:%M:%S")
        courses.append(follow)
    return render_template("module003_index.html", module='module003', courses=courses)


@module003.route('/activity', methods=['GET'])
@login_required
def module003_single_activity():
    form = ActivityResultForm()
    activity_id = request.args.get('activity_id')
    if activity_id:
        activity = Activity.query.get(activity_id)
    else:
        flash("Error fetching activity {}".format(activity_id))
        return redirect(url_for('module003_index'))
    page = request.args.get('page', 1, type=int)
    has_result = ActivityResult.query.filter(and_(
        ActivityResult.activity_id == activity.id, ActivityResult.user_id == current_user.id)).first()
    if current_user.profile in ('admin', 'staff', 'professor'):
        pagination = ActivityResult.query.filter_by(activity_id=activity.id).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        results = pagination.items
        for result in results:
            result.author = User.query.get(result.user_id)
        if results:
            activity.results = results
    elif has_result:
        activity.result = has_result
    activity.timeago = timeago.format(activity.timestamp, datetime.datetime.utcnow())
    activity.time_left = activity.limit_date.strftime("%Y-%m-%d %H:%M:%S")
    return render_template('module003_single_activity.html', form=form, module="module003", activity=activity)


@module003.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    return send_from_directory(directory=uploads, filename=filename)


@module003.route('/new_result', methods=['POST'])
@login_required
def module003_new_result():
    form = ActivityResultForm()
    activity_id = request.args.get('activity_id')
    form.activity_grade.choices+=[(" ", "None")]
    for i in range(0,10):
        form.activity_grade.choices+=[(str(i),str(i))]
    if activity_id:
        activity = Activity.query.get(activity_id)
    else:
        flash("Error fetching activity {}".format(activity_id))
        return redirect(url_for('module003_index'))
    if request.method == 'POST':
        if current_user.profile in 'student':
            user = ActivityResult.query.filter(and_(ActivityResult.user_id == current_user.id,
                                                    ActivityResult.activity_id == activity_id)).first()
            if user:
                flash("You have already sent your result")
                return module003_single_activity()
            file = form.files.data
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER']) + '/' + filename)
            else:
                filename='Empty'
            form.activity_grade.data = 'None'
            if current_user.is_authenticated and form.validate_on_submit():
                result = ActivityResult(user_id=current_user.id,
                                        activity_id=activity_id,
                                        files=filename,
                                        body=form.body.data)
                try:
                    db.session.add(result)
                    db.session.commit()
                except Exception as error:
                    flash(str(error.orig) + " for parameters" + str(error.params))
                flash("Your activity response have been submited")
                return redirect(url_for('module003.module003_index'))
            else:
                flash("Form error: {}".format(form.errors))
        else:
            result_id = request.args.get('result_id')
            activity_result = ActivityResult.query.get(result_id)
            activity_result.activity_grade = form.activity_grade.data
            try:
                db.session.commit()
                flash("Note uploaded successfully")
            except:
                flash("Coudn't upload the note")

    return module003_single_activity()


@module003.route('/new_activity', methods=['GET', 'POST'])
@login_required
def module003_new_activity():
    form = ActivityForm()
    for course in Course.query.filter(Course.user_id == current_user.id):
        form.course_id.choices += [(course.id, str(course.id) + '-' + course.name + '-' + course.institution_name)]
    if request.method == 'POST':
        file = form.files.data
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER']) + '/' + filename)
        else:
            filename = 'Empty'
        limit_date = datetime.datetime.combine(form.date_expire.data, form.time_expire.data)
        if current_user.is_authenticated and form.validate_on_submit():
            activity = Activity(author_id=current_user.id,
                                title=form.title.data,
                                course_id=form.course_id.data,
                                activity_uploads=filename,
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
