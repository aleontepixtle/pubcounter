from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User


class LoginForm(FlaskForm):
    """User login form."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    """User registration form."""
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField('Password', 
                            validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class CredentialsForm(FlaskForm):
    """Form for saving or updating JW.org credentials."""
    jw_username = StringField('JW.org Username', 
                             validators=[DataRequired(), Length(max=120)])
    jw_password = PasswordField('JW.org Password', 
                               validators=[DataRequired()])
    jw_totp_secret = StringField('TOTP Secret', 
                                validators=[DataRequired(), Length(max=255)])
    language = SelectField('Language', 
                          choices=[
                              ('en', 'English'),
                              ('es', 'Spanish'),
                              ('ar', 'Arabic'),
                              ('bn', 'Bengali'),
                              ('ceb', 'Cebuano'),
                              ('zh-CN', 'Chinese Mandarin (Simplified)'),
                              ('zh-TW', 'Chinese Mandarin (Traditional)'),
                              ('hr', 'Croatian'),
                              ('ka', 'Georgian'),
                              ('gu', 'Gujarati'),
                              ('hil', 'Hiligaynon'),
                              ('hi', 'Hindi'),
                              ('ilo', 'Iloko'),
                              ('id', 'Indonesian'),
                              ('it', 'Italian'),
                              ('ja', 'Japanese'),
                              ('jv', 'Javanese'),
                              ('ko', 'Korean'),
                              ('ml', 'Malayalam'),
                              ('my', 'Myanmar'),
                              ('pl', 'Polish'),
                              ('ro', 'Romanian'),
                              ('ru', 'Russian'),
                              ('si', 'Sinhala'),
                              ('tl', 'Tagalog'),
                              ('ta', 'Tamil'),
                              ('th', 'Thai'),
                              ('tr', 'Turkish'),
                              ('uk', 'Ukrainian'),
                              ('ur', 'Urdu'),
                              ('vi', 'Vietnamese')
                          ],
                          default='en')
    submit = SubmitField('Save Credentials')


class ManualSubmitForm(FlaskForm):
    """Form for manual credential entry for one-time submission."""
    jw_username = StringField('JW.org Username', 
                             validators=[DataRequired(), Length(max=120)])
    jw_password = PasswordField('JW.org Password', 
                               validators=[DataRequired()])
    jw_totp_secret = StringField('TOTP Secret', 
                                validators=[DataRequired(), Length(max=255)])
    language = SelectField('Language', 
                          choices=[
                              ('en', 'English'),
                              ('es', 'Spanish'),
                              ('ar', 'Arabic'),
                              ('bn', 'Bengali'),
                              ('ceb', 'Cebuano'),
                              ('zh-CN', 'Chinese Mandarin (Simplified)'),
                              ('zh-TW', 'Chinese Mandarin (Traditional)'),
                              ('hr', 'Croatian'),
                              ('ka', 'Georgian'),
                              ('gu', 'Gujarati'),
                              ('hil', 'Hiligaynon'),
                              ('hi', 'Hindi'),
                              ('ilo', 'Iloko'),
                              ('id', 'Indonesian'),
                              ('it', 'Italian'),
                              ('ja', 'Japanese'),
                              ('jv', 'Javanese'),
                              ('ko', 'Korean'),
                              ('ml', 'Malayalam'),
                              ('my', 'Myanmar'),
                              ('pl', 'Polish'),
                              ('ro', 'Romanian'),
                              ('ru', 'Russian'),
                              ('si', 'Sinhala'),
                              ('tl', 'Tagalog'),
                              ('ta', 'Tamil'),
                              ('th', 'Thai'),
                              ('tr', 'Turkish'),
                              ('uk', 'Ukrainian'),
                              ('ur', 'Urdu'),
                              ('vi', 'Vietnamese')
                          ],
                          default='en')
    submit = SubmitField('Submit Inventory')