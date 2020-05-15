from flask_wtf import Form
from wtforms import TextField, BooleanField, StringField, PasswordField, TextAreaField, validators, SubmitField

class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=3, max=25)])  
    password = PasswordField('New Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', 
                            message='Passwords must match')
            ])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Submit')

class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])  
    password = PasswordField('Password', [validators.DataRequired()])
    submit = SubmitField('Submit')