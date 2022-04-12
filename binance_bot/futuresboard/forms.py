
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField, SelectField
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from futuresboard.models import *



class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = UserModel.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError('Username already exists! Please try a different username')

    def validate_email_address(self, email_address_to_check):
        email_address = UserModel.query.filter_by(email_address=email_address_to_check.data).first()
        if email_address:
            raise ValidationError('Email Address already exists! Please try a different email address')

    username = StringField(label='User Name:', validators=[Length(min=2, max=30), DataRequired()])
    email_address = StringField(label='Email Address:', validators=[Email(), DataRequired()])
    password1 = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    password2 = PasswordField(label='Confirm Password:', validators=[EqualTo('password1'), DataRequired()])
    referral = StringField(label="Referral:", validators=[Length(min=4, max=15), DataRequired()], default=None)
    submit = SubmitField(label='Create Account')

class ResetPasswordForm(FlaskForm):
    email = StringField(label='Email:', validators=[DataRequired()])
    submit = SubmitField(label='Reset Password', validators=[DataRequired()])

class ResetPasswordReallyForm(FlaskForm):
    password = PasswordField(label='Password:', validators=[Length(min=6), DataRequired()])
    confirm_password = PasswordField(label='Confirm Password:', validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label='Change Password', validators=[DataRequired()])

class LoginForm(FlaskForm):
    username = StringField(label='User Name:', validators=[DataRequired()])
    password = PasswordField(label='Password:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')
    
class RemoveApiForm(FlaskForm):
    submit = SubmitField(label='Remove')

class AddApiForm(FlaskForm):
    api_name = StringField(label='API Name:', validators=[DataRequired()])
    api_key = PasswordField(label='API Key:', validators=[DataRequired()])
    secret_key = PasswordField(label='Secret Key:', validators=[DataRequired()])
    submit = SubmitField(label='Add')

class AddTelegramBotForm(FlaskForm):
    chat_id = StringField(label='Your chat id:', validators=[DataRequired()])
    submit = SubmitField(label='Connect')

class RemoveTelegramBotForm(FlaskForm):
    submit = SubmitField(label='Remove')

class ConnectToGoogleAuthenticatorForm(FlaskForm):
    submit_connect = SubmitField(label='Connect')

class CheckingCodeGoogleAuthenticatorForm(FlaskForm):
    code = StringField(label='Code from the GoogleAuthenticator app.:', validators=[DataRequired()])
    submit = SubmitField(label='Sign in')

class ClearAllFavoritesForm(FlaskForm):
    submit_clear = SubmitField(label='Delete all favorites')

class SelectAllFavoritesForm(FlaskForm):
    submit_select = SubmitField(label='Select all favorites')
    