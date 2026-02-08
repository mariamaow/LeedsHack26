from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, BooleanField, DateTimeField, FloatField, SelectField, SelectMultipleField, DecimalField, HiddenField, TextAreaField,RadioField
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length, Optional
from wtforms.widgets import PasswordInput
from app import models

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', widget=PasswordInput(hide_value=False), validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', widget=PasswordInput(hide_value=False), validators=[DataRequired(), Length(min=8, message="Stronger password required, must be a length of at least 8")])
    location = StringField('Location', validators=[DataRequired()])
   
    role = SelectField(
        'Sign up as:',
        choices=[('foodbank', 'Foodbank'), ('volunteer', 'Volunteer')],
        validators=[DataRequired()]
    )
class DonationForm(FlaskForm):
    location = StringField('Location', validators=[DataRequired()])
    meal_amount = IntegerField('Meal Amount', validators=[DataRequired(), NumberRange(min=1, message="Must donate at least 1 meal")])
    expiry = DateField('Expiry', validators=[DataRequired()])