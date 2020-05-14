import os
import hashlib

from flask import Flask, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

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

@app.route("/register")
def register():
    return render_template("registration.html")

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
    # db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
    #         {"name": name, "flight_id": flight_id})
    # db.commit()
    return render_template("searchpage.html")