import csv
import urllib.request
from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL
db = SQL("sqlite:///bmwreview.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def grade():
    ids = db.execute("SELECT id FROM data")
    carids = db.execute("SELECT car_id FROM reviews")
    cars =[]
    for i in range(len(carids)):
        cars.append(carids[i]['car_id'])
    #for i in range(len(ids)):
        #if (ids[i]['id']) is in cars:
         #   print(ids[i]['id'])
        #db.execute("UPDATE data SET stars=0 WHERE id= :id", id = ids[i]['id'])
    return cars
