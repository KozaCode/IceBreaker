from flask_wtf import FlaskForm
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange, Optional, ValidationError

class AgePrefValidator(object):
    """Age preference validator"""
    def __init__(self, message=None):
        self.message = message
        
    def __call__(self, form, field):
        if field.data < form.min_age_pref.data or field.data > form.max_age_pref.data:
            message = self.message
            if message is None:
                message = field.gettext('Age preference must be between %(min)s and %(max)s.')
            raise ValidationError(message % dict(min=form.min_age_pref.data, max=form.max_age_pref.data))
        
class LoginForm(FlaskForm):
    """Login form"""
    #TODO: REMOVE DEFAULT VALUES. ADDED FOR TESTING PURPOSES
    #TODO: HANDLE FORM ERRORS
    username = StringField('*Username:', validators=[InputRequired(), Length(min=2, max=32)], default="Piotr")
    gender = SelectField('*Gender:', validators=[InputRequired()], choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    age = IntegerField('*Age:', validators=[InputRequired(), NumberRange(min=13, max=100)], default=22)
    gender_pref = SelectField('*Looking for:', validators=[Optional()], choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')])
    min_age_pref = IntegerField('Min preferred age:', validators=[Optional(), NumberRange(min=13, max=100)], default=18)
    max_age_pref = IntegerField('Max preferred age:', validators=[Optional(), NumberRange(min=13, max=100), AgePrefValidator()], default=35)
    submit = SubmitField('Login')