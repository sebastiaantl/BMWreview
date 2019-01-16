from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
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

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    if request.method == "POST":
        # making sure the shares input is not a fraction or a non-integer
        try:
            shares = int(request.form.get("shares"))
        # if not, redirect user to an error message
        except:
            return apology("this amount of shares is not valid")

        stock = request.form.get("symbol")
        # checking if the symbol field is not empty
        if not stock:
            return apology("must provide stock")
        # checking if the shares field is not empty
        if not shares:
            return apology("must provide shares")
        # checking if the function can give the stock data back
        # if not, the stock apparently doesn't exist
        if not lookup(stock):
            return apology("this stock is not valid")
        # ensure that the amount of shares is not negative
        if shares < 0:
            return apology("this amount of shares is not valid")
        # fetching the live price for the stock and computing the transaction amount
        price = int(lookup(stock)['price'])
        total = price * shares

        # checking if the user has enough credit to complete the transaction
        cash = db.execute("SELECT cash FROM users WHERE id = :id", id = session["user_id"])[0]['cash']
        if total > cash:
            return apology("There is not enough credit to complete transaction")
        # inserting the stock and relevant information about the transaction in the database
        db.execute("INSERT INTO stocks (symbol, shares, price, total, user_id) VALUES (:symbol,:shares,:price,:total,:user_id)", symbol = stock, shares = shares, price = price, total = total, user_id = session["user_id"])
        # computing the new amount of credit on the users acount and updating it in the database
        newcash = cash - total
        db.execute("UPDATE users SET cash = :newcash WHERE id = :id", id = session['user_id'], newcash = newcash)
        # after the transaction is completed the user is redirected to the homepage
        return redirect(url_for("homepage"))
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    return apology("TODO")

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

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        # if the user doesn't input a stock, provide an error message
        if len(request.form.get("symbol")) == 0:
            return apology("This stock is not valid")
        # checking if the symbol represents an actual stock
        elif not lookup(request.form.get("symbol")):
            return apology("This stock is not valid")
        # if it does, make the relevant variables for the stock quote
        else:
            quote = lookup(request.form.get("symbol"))
            name = quote['name']
            price = usd(quote['price'])
            symbol = quote['symbol']
            # return values to the template
            return render_template("quoted.html", price = price, name = name, symbol = symbol)
    else:
        return render_template("quote.html")


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

        #insert username into database
        db.execute("INSERT into users (username, password, email) VALUES(:username, :password, :email)", username= request.form.get("username"), password = pwd_context.hash(request.form.get("password")), email = request.form.get("email"))

        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect(url_for("homepage"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    return apology("TODO")
