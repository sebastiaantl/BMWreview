from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import request
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
from helpers import *

# configure application
app = Flask(__name__)

UPLOAD_FOLDER = os.path.basename('uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///bmwreview.db")

@app.route("/")
def homepage():
    return home()

@app.route("/profile")
@login_required
def profile():
    return myprofile()


@app.route("/login", methods=["GET", "POST"])
def login():
    return login_func()

@app.route("/logout")
@login_required
def logout():
    return logout_func()

@app.route("/favourites", methods=["GET", "POST"])
@login_required
def favourites():
    return favourite_func()

@app.route("/register", methods=["GET", "POST"])
def register():
    return register_func()

@app.route("/search")
def search():
    return search_func()

@app.route("/filter")
def filter():
    return filter_func()

@app.route("/carpage", methods=["GET", "POST"])
def carpage():
    return carpage_func()

@app.route("/remove_review", methods=["POST"])
@login_required
def remove_review():
    return remove_review_func()

@app.route("/unfavourite", methods=["POST"])
@login_required
def unfavourite():
    return unfavourite_func()