from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=32)], default="Piotr")
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[InputRequired()])
    age = IntegerField('Age', validators=[InputRequired()], default=22)
    gender_pref = SelectField('Looking for', choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')])
    min_age_pref = IntegerField('Min preferred age', default=18)
    max_age_pref = IntegerField('Max preferred age', default=35)
    submit = SubmitField('Login')