from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    title = StringField("Activity Title:", validators=[DataRequired()])
    course_id = SelectField("Course:", choices=[])
    body = StringField("", validators=[DataRequired()])
    files = FileField("")
    limit_date = DateField('DatePicker', validators=[DataRequired()])
    limit_hour = SelectField('', choices=[])
    limit_min = SelectField(':', choices=[])
    limit_sec = SelectField(':', choices=[])


class ActivityResultForm(FlaskForm):
    body = StringField("", validators=[DataRequired()])
    files = FileField("")
    activity_grade = SelectField("Activity Grade:", choices=['None',0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    submit_button = SubmitField('Send Comment')
