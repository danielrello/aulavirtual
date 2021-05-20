from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired


class ActivityForm(FlaskForm):
    title = StringField("Activity Title:", validators=[DataRequired()])
    course_id = SelectField("Course:", choices=[])
    body = StringField("", validators=[DataRequired()])
    limit_date = DateField('DatePicker')
    limit_hour = SelectField('', choices=[])
    limit_min = SelectField(':', choices=[])
    limit_sec = SelectField(':', choices=[])
