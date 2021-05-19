import wtforms
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

from models import Forum


class PostForm(FlaskForm):
    title = StringField("Post Title:", validators=[DataRequired()])
    forum_id = SelectField("Forum:", choices=[])
    body = StringField("What's on your mind?", validators=[DataRequired()])


class ForumForm(FlaskForm):
    title = StringField("Forum Title:", validators=[DataRequired()])
    course_id = SelectField("Courses:", choices=[])


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()], render_kw={"placeholder": "What up?"})
    submit_button = SubmitField('Send Comment')
