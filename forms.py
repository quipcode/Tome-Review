from flask_wtf import Form
from wtforms import TextField, BooleanField, StringField, PasswordField, TextAreaField, validators, SubmitField, SelectField

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

class SearchForm(Form):
    query = StringField('Search query', [validators.DataRequired()])  
    submit = SubmitField('Submit')

class BookReviewForm(Form):
    # rating = SelectField(
    #     choices=[1,2,3,4,5],
    #     validators=[validators.DataRequired(), validators.NumberRange(min=1, max=5) ]
    # )
    rating = SelectField('State', choices=[('XX', 'Select a Rating'), ('1','1') ,('2','2'),('3', '3'),('4', '4'),('5', '5') ], default='XX', validators=[validators.DataRequired(), validators.AnyOf(['1','2','3','4','5'])])
    # rating = SelectField(choices=[1,2,3,4,5], validators=[validators.DataRequired()], render_kw={"placeholder": "None"})
    review = TextAreaField('Provide a review', [validators.DataRequired()])
    submit = SubmitField('Submit')