import os
import hashlib
import requests

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from flask import Flask
from flask_bootstrap import Bootstrap

# def create_app():
#   app = Flask(__name__)
#   Bootstrap(app)

#   return app

# from flask_wtf import FlaskForm
# from wtforms import StringField
# from wtforms.validators import DataRequired

# class MyForm(FlaskForm):
#     name = StringField('name', validators=[DataRequired()])

# from wtforms import Form, BooleanField, StringField, PasswordField, validators
# from flask_wtf import Form

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

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key ="our little secret"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    # return "Project 1: TODO"
    return render_template("index.html")

# @app.route("/register")
# def register():
#     return render_template("registration.html")

@app.route('/signin', methods=["POST"])
def signin():
    """Sign into Tome Review"""
    
    # Get form information.
    username = request.form.get("username")
    password = request.form.get("password")    
    hashpass = hashlib.md5(password.encode('utf8')).hexdigest()
    
    # Make sure user exists.
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",  {"username": username, "password":hashpass}).rowcount == 0:
        return render_template("error.html", message="Incorrect username or password")
    
    return render_template("searchpage.html")

# @app.route('/register', methods=["GET","POST"])
# def register():
#     """Register for Tome Review"""
#     if request.method == 'GET':
#         return  render_template("registration.html")
#     else:
        
        
        
#         # Get form information.
#         username = request.form.get("username")
#         password1 = request.form.get("password1")    
#         password2 = request.form.get("password2")    
#         hashpass1 = hashlib.md5(password1.encode('utf8')).hexdigest()
#         hashpass2 = hashlib.md5(password2.encode('utf8')).hexdigest()
        
#         # Ensure password values are the same
#         if hashpass1 != hashpass2:
#             return render_template("error.html", message="Provide the same password in both password fields")

#         # Make sure user exists.
#         if db.execute("SELECT * FROM users WHERE username = :username AND password = :password",  {"username": username, "password":hashpass1}).rowcount != 0:
#             return render_template("error.html", message="That username has been taken")
#         # db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
#         #         {"username": username, "password":hashpass1})
#         # db.commit()
#         return render_template("searchpage.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():

        # user = User(form.username.data, form.password.data)
        # db_session.add(user)
        flash('Thanks for registering please sign in to continue')
        return redirect(url_for('index'))
    flash('Thanks for registering')
    return render_template('submit.html', form=form)