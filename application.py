from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import request
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

from helpers import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///bmwreview.db")

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/profile")
@login_required
def profile():

    bio = db.execute("SELECT bio FROM users WHERE id = :id", id = session["user_id"])
    username = db.execute("SELECT username FROM users WHERE id = :id", id = session["user_id"])[0]['username']
    reviews = db.execute("SELECT car_id, stars, review, date FROM reviews WHERE user_id = :user_id", user_id = session["user_id"])
    car_id = reviews[0]["car_id"]
    carname = db.execute("SELECT Make, Model, Generation FROM data WHERE id = :id", id = car_id)
    brand = carname[0]["Make"]
    model = carname[0]["Model"]
    generation = carname[0]["Generation"]
    return render_template("profile.html", username = username, bio = bio, brand = brand, model = model, generation = generation, reviews = reviews)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            return apology("invalid username and/or password")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("homepage"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/favourites", methods=["GET", "POST"])
def favourites():

    return render_template("favourites.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # ensure password verification was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password again")

        elif not request.form.get("email"):
            return apology("must provide email adress")

        # ensure password and password verification are the same
        elif not request.form.get("password") ==  request.form.get("confirmation"):
            return apology("Provided passwords are not the same")

        # checking if the username is not already taken
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows) == 1:
            return apology("username already exists")
        bio = request.form.get("bio")
        if len(bio) == 0:
            bio = 'no bio'

        #insert username into database
        db.execute("INSERT into users (username, password, email, bio) VALUES(:username, :password, :email, :bio)", username= request.form.get("username"), password = pwd_context.hash(request.form.get("password")), email = request.form.get("email"), bio = bio)

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("homepage"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/search")
def search():
    a = request.args.get('query')
    global thequery
    thequery = a
    results = db.execute("SELECT Make, Model, Generation FROM data WHERE upper(Model) = :a UNION ALL SELECT Make, Model, Generation FROM data WHERE upper(Generation) =:b", a=a.upper(), b=a.upper())
    resultsnumber = len(results)
    return render_template("searchresult.html", a=a, results=results, resultsnumber=resultsnumber)


@app.route("/filter")
def filter():
    seats = request.args.get('seats')
    enginetype= request.args.get('enginetype')
    results = db.execute("SELECT Make, Model, Generation FROM data WHERE upper(Model) = :model UNION ALL SELECT Make, Model, Generation FROM data WHERE upper(Generation) =:generation", model=thequery.upper(), generation=thequery.upper())
    models = [results[0]["Model"]]
    error = ""

    filtered = results
    if seats =="" and enginetype =="":
        filtered = results
    if seats =="":
        if enginetype !="":
            for model in models:
                filtered = db.execute("SELECT Make, Model, Generation FROM data WHERE upper(Model) = :model AND Engine_type= :enginetype", model=model.upper(), enginetype=enginetype)
    if seats !="":
        if enginetype =="":
            for model in models:
                filtered = db.execute("SELECT Make,Model, Generation FROM data WHERE upper(Model) = :model AND Number_of_seater = :seats", model=model.upper(), seats=seats)
        elif enginetype !="":
            for model in models:
                filtered = db.execute("SELECT Make,Model, Generation FROM data WHERE upper(Model) = :model AND Number_of_seater = :seats AND Engine_type= :enginetype", model=model.upper(), seats=seats, enginetype=enginetype)
    if len(filtered) == 0:
        error= "No cars found!"
    return render_template("filter.html", seats = seats, thequery = thequery, filtered = filtered, error=error)

@app.route("/carpage", methods=["GET", "POST"])
def carpage():
    """Show user car info."""
    # determine which car
    id = 1

    # select all specifications of the car from the database
    header = db.execute("SELECT Make, Model, Generation, Year_from_Generation, Year_to_Generation FROM data WHERE id = :id", id = id)
    brand = header[0]["Make"]
    model = header[0]["Model"]
    generation = header[0]["Generation"]
    startyear = header[0]["Year_from_Generation"]
    endyear = header[0]["Year_to_Generation"]

    # insert review into database
    if request.method == "POST":
        stars = request.form.get("rate")
        print(request.form.get("rate"))
        review = request.form.get("comment")
        user_id = session.get("user_id")
        db.execute("INSERT INTO reviews (car_id, user_id, stars, review) VALUES(:car_id, :user_id, :stars, :review)", car_id=id, user_id=user_id, stars=stars, review=review)
        return redirect(url_for("carpage"))
    # redirect user to carpage
    else:
        return render_template("carpage.html", header = header, brand = brand, model = model, generation = generation, startyear = startyear, endyear = endyear)