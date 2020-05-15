import os, json
import hashlib
import requests

from flask import Flask, g, session, render_template, request, flash, redirect, url_for, jsonify
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from flask_bootstrap import Bootstrap
from functools import wraps

from forms import RegistrationForm, LoginForm, SearchForm, BookReviewForm


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login'))

    return wrap


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
        return redirect("/search")
    
    else:
        return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")



@app.route('/register', methods=['GET', 'POST'])
def register():
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
                return redirect(url_for('search'))
        return render_template("registration.html", form=form)

    except Exception as e:
        return(str(e))



@app.route('/search', methods=["GET", "POST"])
@login_required
def search():
    form = SearchForm(request.form)
    if request.method == "POST" and form.validate():
        query = "%" + form.query.data + "%"
        # Capitalize all words of input for search
        # https://docs.python.org/3.7/library/stdtypes.html?highlight=title#str.title
        query = query.title()
        # results = db.execute("SELECT * FROM books WHERE \ isbn LIKE :query OR \ title LIKE :query OR \ author LIKE :query RETURNING *", {"query": query})
        books = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE :query OR \
                        title LIKE :query OR \
                        author LIKE :query",
                        {"query": query})
       
        
        
        if books.rowcount == 0:
            return render_template("error.html", message="No books were found matching that query")

        return render_template("search.html", books=books, form=form)
    if 'username' in session:
        return render_template("search.html", form=form)
    else:
        return redirect("/")
    

@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):
    """ Save user review and load same page with reviews updated."""
    form = BookReviewForm(request.form)
    if request.method == "POST" and form.validate() :

        # Save current user info
        currentUser = session["user_id"]
        
        # Fetch form data
        rating = request.form.get("rating")
        review = request.form.get("review")
        
        # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        bookId = row.fetchone() # (id,)
        bookId = bookId[0]

        # Check for user submission (ONLY 1 review/user allowed per book)
        row2 = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                    {"user_id": currentUser,
                        "book_id": bookId})

        # A review already exists
        if row2.rowcount == 1:
            
            flash('You already submitted a review for this book - Tome Reviewers are only granted 1 review per book', 'warning')
            return redirect("/book/" + isbn)

        # Convert to save into DB
        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, review, rating) VALUES \
                    (:user_id, :book_id, :review, :rating)",
                    {"user_id": currentUser, 
                    "book_id": bookId, 
                    "review": review, 
                    "rating": rating})

        # Commit transactions to DB and close the connection
        db.commit()

        flash('Review submitted!', 'info')

        return redirect("/book/" + isbn)
    
    # Take the book ISBN and redirect to his page (GET)
    else:
        
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn = :isbn",
                        {"isbn": isbn})

        bookInfo = row.fetchall()

        """ GOODREADS reviews """

        # Read API key from env variable
        key = os.getenv("GOODREADS_KEY")
        
        # Query the api with key and ISBN as parameters
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})

        # Convert the response to JSON
        response = query.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = response['books'][0]

        # Append it as the second element on the list. [1]
        bookInfo.append(response)

        """ Users reviews """

         # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]

        # Fetch book reviews
        # Date formatting (https://www.postgresql.org/docs/9.1/functions-formatting.html)
        results = db.execute("SELECT users.username, review, rating, \
                            to_char(time, 'DD Mon YY - HH24:MI:SS') as time \
                            FROM users \
                            INNER JOIN reviews \
                            ON users.id = reviews.user_id \
                            WHERE book_id = :book \
                            ORDER BY time",
                            {"book": book})

        reviews = results.fetchall()

        return render_template("book.html", bookInfo=bookInfo, reviews=reviews, form=form)

@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):

    # COUNT returns rowcount
    # SUM returns sum selected cells' values
    # INNER JOIN associates books with reviews tables

    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn})

    # Error checking
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid ISBN || Not cataloged"}), 422

    # Fetch result from RowProxy    
    tmp = row.fetchone()

    # Convert to dict
    result = dict(tmp.items())

    # Round Avg Score to 2 decimal. This returns a string which does not meet the requirement.
    # https://floating-point-gui.de/languages/python/
    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)