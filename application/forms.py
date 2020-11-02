from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from application.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=15)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=55)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=6, max=15)])
    submit = SubmitField('Register')

    
    def validate_email(self,email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Email is already in use. Please choose another one')