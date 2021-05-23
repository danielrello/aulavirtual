from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
import datetime


class ActivityForm(FlaskForm):
    title = StringField("Activity Title:", validators=[DataRequired()])
    course_id = SelectField("Course:", choices=[])
    body = StringField("", validators=[DataRequired()], widget=TextArea())
    files = FileField("")
    date_expire = DateField('Choose an expiring date', format='%Y-%m-%d', default=datetime.datetime.today)
    time_expire = TimeField('Expiring time', format='%H:%M', default=datetime.time(23, 59))


class ActivityResultForm(FlaskForm):
    body = StringField("", validators=[DataRequired()], widget=TextArea())
    files = FileField("")
    activity_grade = SelectField("Activity Grade:", choices=['None', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    submit_button = SubmitField('Send Comment')
