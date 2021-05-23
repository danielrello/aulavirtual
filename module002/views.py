from flask import Blueprint, render_template, abort, flash, redirect, url_for, request, current_app, session
from flask_login import login_required, current_user
import timeago, datetime
from sqlalchemy.sql import label

from models import Post, db, User, Forum, Course, Comment, Follow

from module002.forms import *

module002 = Blueprint("module002", __name__, static_folder="static", template_folder="templates")


@module002.route('/')
@login_required
def module002_index():
    # user = User.filter_by(id=current_user.id)
    if current_user.profile in ('admin', 'staff', 'student'):
        page = request.args.get('page', 1, type=int)
        query = Forum.query
        pagination = query.order_by(Forum.timestamp.desc()).paginate(
            page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
            error_out=False)
        forums = pagination.items
        for forum in forums:
            forum.timeago = timeago.format(forum.timestamp, datetime.datetime.utcnow())
            if forum.course_id is not None:
                course = Course.query.get(forum.course_id)
                forum.course = course
            author = User.query.get(forum.author_id)
            forum.author = author
        return render_template("module002_index.html", module="module002", current_user=current_user,
                               forums=forums, pagination=pagination)
    else:
        flash("Access denied!")
        #        abort(404,description="Access denied!")
        return redirect(url_for('index'))


@module002.route('/forum', methods=['GET'])
@login_required
def module002_forum_posts():
    forum_id = request.args.get('id')
    query = Forum.query
    page = request.args.get('page', 1, type=int)
    forum = query.get(forum_id)
    forum.timeago = timeago.format(forum.timestamp, datetime.datetime.utcnow())
    course = None
    if forum.course_id is not None:
        course = Course.query.get(forum.course_id)
    author = User.query.get(forum.author_id)
    forum.author = author
    forum.course = course
    pagination = Post.query.filter(Post.forum_id == forum_id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    for post in posts:
        post.timeago = timeago.format(post.timestamp, datetime.datetime.utcnow())
        post.author = User.query.get(post.author_id)
    return render_template('module002_single_forum.html', module="module002", forum=forum, posts=posts)


@module002.route('/post', methods=['GET'])
@login_required
def module002_post_comments():
    form = CommentForm()
    post_id = request.args.get('id')
    query = Post.query
    page = request.args.get('page', 1, type=int)
    post = query.filter(Post.id == post_id).first()
    author = User.query.get(post.author_id)
    post.timeago = timeago.format(post.timestamp, datetime.datetime.utcnow())
    post.author = author
    pagination = Comment.query.filter(Comment.post_id == post_id).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    for comment in comments:
        comment.timeago = timeago.format(comment.timestamp, datetime.datetime.utcnow())
        comment.author = User.query.get(comment.author_id)
    return render_template('module002_single_post.html', module="module002", form=form, post=post, comments=comments)


@module002.route('/new_forum', methods=['GET', 'POST'])
@login_required
def module002_new_forum():
    form = ForumForm()
    for course in Course.query.filter(Course.user_id == current_user.id):
        form.course_id.choices += [(course.id, str(course.id) + '-' + course.name + '-' + course.institution_name)]
    if request.method == 'POST':
        if current_user.is_authenticated and form.validate_on_submit():
            forum = Forum(author_id=current_user.id,
                          title=form.title.data,
                          course_id=form.course_id.data)
            db.session.add(forum)
            db.session.commit()
            flash("Successfully created a new forum")
            return redirect(url_for('module002.module002_index'))

    return render_template('module002_new_forum.html', module="module002", form=form)


@module002.route('/new_comment', methods=['POST'])
@login_required
def module002_new_comment():
    form = CommentForm()
    id = request.args.get('id')
    if request.method == 'POST':
        if current_user.is_authenticated and form.validate_on_submit():
            comment = Comment(author_id=current_user.id,
                              post_id=id,
                              body=form.body.data)
            db.session.add(comment)
            db.session.commit()
            flash("Successfully created a new comment")
        else:
            flash("An error has occurred while sending your comment")
            flash("Post id:" + id + " " + form.body.data)
    return redirect(url_for('module002.module002_post_comments', id=id))


@module002.route('/new_post', methods=['GET', 'POST'])
@login_required
def module002_new_post():
    form = PostForm()
    if request.method == 'GET' and request.args.get('forum_id'):
        forum_id = request.args.get('forum_id')
        forum = Forum.query.filter(Forum.id == forum_id).first()
        form.forum_id.choices = [(forum.id, forum.title)]
    else:
        form.forum_id.choices += [("", "---")]
        for forum in Forum.query.all():
            form.forum_id.choices += [(forum.id, forum.title)]
    if request.method == 'POST':
        if current_user.is_authenticated and form.validate_on_submit():
            none_forum = Forum.query.filter(Forum.title == 'None Forum').first()
            if none_forum == None:
                none_forum = Forum(title='None Forum',
                                   author_id=current_user.id)
                db.session.add(none_forum)
                db.session.commit()
                forum_id = none_forum.id
            else:
                forum_id = form.forum_id.data
            post = Post.query.get(request.args.get('id'))
            if post:
                post.title = form.title.data
                post.body = form.body.data
                post.forum_id = form.forum_id.data
                try:
                    db.session.commit()
                    flash("Post modified correctly")
                except:
                    flash("Could not modify your post")
            else:
                post = Post(body=form.body.data,
                            author_id=current_user.id,
                            title=form.title.data,
                            forum_id=forum_id)
                try:
                    db.session.add(post)
                    db.session.commit()
                    flash("Post added correctly")
                except:
                    flash("Could not add your post")
            return redirect(url_for('module002.module002_forum_posts', id=forum_id))
    return render_template('module002_new_post.html', module="module002", form=form)


@module002.route('/edit_post', methods=['GET', 'POST'])
@login_required
def module002_edit_post():
    form = PostForm()
    if request.method == 'GET' and request.args.get('id'):
        post_id = request.args.get('id')
        post = Post.query.get(post_id)
        form.forum_id.choices += [(post.forum_id, Forum.query.get(post.forum_id).title)]
        form.forum_id.choices += [("", "---")]

        forums = Forum.query.filter_by(author_id=current_user.id)
        follows = Follow.query.filter_by(user_id=current_user.id)
        for follow in follows:
            forums += Forum.query.get(follow.id)
        form.body.data = post.body
        form.title.data = post.title
        for forum in forums:
            if forum.id != post.forum_id:
                form.forum_id.choices += [(forum.id, forum.title)]
    return render_template('module002_new_post.html', module="module002", form=form, post=post)


@module002.route('/test')
def module002_test():
    return 'OK'
