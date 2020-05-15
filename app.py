import os
import hashlib
import requests

from flask import Flask, g, session, render_template, request, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from flask import Flask
from flask_bootstrap import Bootstrap


# from helpers import login_required
from forms import RegistrationForm, LoginForm

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
    return render_template("index.html")

@app.route('/login', methods=["GET","POST"])
def login():
    """Sign into Tome Review"""
    form = LoginForm(request.form)
    # Forget any user_id
    session.clear()
    if request.method == "POST":
        # Get form information.
        username = request.form.get("username")
        password = request.form.get("password")    
        hashpass = hashlib.md5(password.encode('utf8')).hexdigest()
        
        # Check database for user:
        rows = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",  {"username": username, "password":hashpass})
        userLoginRow = rows.fetchone()
        # Make sure user exists.
        if rows.rowcount == 0:
            return render_template("error.html", message="Incorrect username or password")
        
        session['logged_in'] = True
        session["user_id"] = userLoginRow[0]
        session["username"] = userLoginRow[1]
        # g.user = {"username": userLoginRow[1]}
        g.user = userLoginRow[1]
        return redirect("/dashboard")
    
    else:
        return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect("/")


@app.route("/dashboard")
def dashboard():
    if 'username' in session:
        return render_template("dashboard.html", name=session['username'])
    return render_template("dashboard.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    # form = RegistrationForm(request.form)
    # if request.method == 'POST' and form.validate():

    #     # user = User(form.username.data, form.password.data)
    #     # db_session.add(user)
    #     flash('Thanks for registering please sign in to continue')
    #     return redirect(url_for('index'))
 
    # return render_template('registration.html', form=form)

    try:
        form = RegistrationForm(request.form)

        if request.method == "POST" and form.validate():
            username  = form.username.data
            password = hashlib.md5(request.form.get("password").encode('utf8')).hexdigest()

            if db.execute("SELECT * FROM users WHERE username = :username",  {"username": username}).rowcount != 0:
                flash("That username is already taken, please choose another")
                return render_template('registration.html', form=form)
            else:
                rows = db.execute("INSERT INTO users (username, password) VALUES (:username, :password) RETURNING *",
                    {"username": username, "password":password})
                
                userLoginRow = rows.fetchone()
                db.commit()
                flash("Thanks for registering!")


                session['logged_in'] = True
                session["user_id"] = userLoginRow[0]
                session["username"] = userLoginRow[1]

                return redirect(url_for('dashboard'))

        return render_template("registration.html", form=form)

    except Exception as e:
        return(str(e))