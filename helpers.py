import csv
import urllib.request
from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask import request
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import os
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

def home():
    # select last five results and get corresponding car data
    lastreviews = db.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 5")
    userlist = []
    # add users to userlist
    for i in lastreviews:
        users = i['user_id']
        username = db.execute("SELECT username FROM users WHERE id = :id", id = users)
        userlist.append(username)
    lastcarids = []
    # add latest car id's to list
    for x in lastreviews:
        lastcarids.append(x['car_id'])
    lastcarids.reverse()
    lastcars= []
    # add Make, Model & Generation to lastcars list
    for ids in lastcarids:
        lastcars.append(db.execute("SELECT Make, Model, Generation from data WHERE id = :id", id= ids))
    # add the review to the lastest cars list
    for i in range(len(lastreviews)):
        lastreviews.append(lastcars[i])
    # get top 3 rated cars
    highestrated = db.execute("SELECT Make, Model, Generation, CAST(stars AS INT) AS stars, id,  Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh FROM data ORDER BY stars DESC LIMIT 3")
    return render_template("homepage.html", lastreviews = lastreviews, highestrated = highestrated, userlist = userlist)

def login_func():
    """Log user in."""
    # forget any user_id
    session.clear()
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("login.html", error = error)
        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("login.html", error = error)
        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["password"]):
            error = "Username or password is not correct"
            return render_template("login.html", error = error)
        # remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # redirect user to home page
        return redirect(url_for("homepage"))
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        error = 0
        return render_template("login.html", error = error)

def register_func():
    """Register user."""
    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            error = "Must provide username"
            return render_template("register.html", error = error)

        # ensure password was submitted
        elif not request.form.get("password"):
            error = "Must provide password"
            return render_template("register.html", error = error)

        # ensure password verification was submitted
        elif not request.form.get("confirmation"):
            error = "Must provide password confirmation"
            return render_template("register.html", error = error)

        elif not request.form.get("email"):
            error = "Must provide email"
            return render_template("register.html", error = error)

        # ensure password and password verification are the same
        elif not request.form.get("password") ==  request.form.get("confirmation"):
            error = "Password and confirmation are not the same"
            return render_template("register.html", error = error)

        # checking if the username is not already taken
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))
        if len(rows) == 1:
            error = "Username already exists"
            return render_template("register.html", error = error)
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
        error = 0
        return render_template("register.html", error = error)

def logout_func():
    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

def myprofile():
    # get id, bio, username, reviews, favourites and count of faves/reviews
    current_id = session["user_id"]
    bio = db.execute("SELECT bio FROM users WHERE id = :id", id = current_id)
    username = db.execute("SELECT username FROM users WHERE id = :id", id = current_id)[0]['username']
    reviews = db.execute("SELECT car_id, stars, review, date FROM reviews WHERE user_id = :user_id", user_id = current_id)
    fave = db.execute("SELECT car_id FROM favourites WHERE user_id = :user_id", user_id = current_id)
    favescount = len(fave)
    carlist = []
    carids = []
    reviewcount = len(reviews)
    # add Make, Model & Generation by id to display full car name
    for review in reviews:
        car_id = review['car_id']
        carids.append(car_id)
        carlist.append(db.execute("SELECT Make, Model, Generation FROM data WHERE id = :id", id = car_id))
    reviews.reverse()
    carlist.reverse()
    carids.reverse()
    return render_template("profile.html", username = username, bio = bio, reviews = reviews, carlist=carlist, length=len(carlist), carids=carids, reviewcount = reviewcount, favescount = favescount)

def favourite_func():
    """Saves a car as a favourite."""
    # get user id and car id
    user_id = session.get("user_id")
    id = request.args.get('id')
    # check if favorite is added by POST request
    if request.method == "POST":
        # if not logged in, redirect to login page
        if not session.get("user_id"):
            return redirect(url_for("login"))
        # select car id by user id (must be logged in)
        rows = db.execute("SELECT car_id FROM favourites WHERE user_id = :user_id", user_id=session.get("user_id"))
        already_favourites = []
        # list of already favourited cars (to prevent double favorites)
        for i in range(0, len(rows)):
            favourite = rows[i]["car_id"]
            already_favourites.append(favourite)
        id = int(id)
        if id not in already_favourites:
            db.execute("INSERT INTO favourites (car_id, user_id) VALUES(:car_id, :user_id)", car_id=id, user_id=user_id)
            idresults = db.execute("SELECT car_id FROM favourites WHERE user_id = :user_id", user_id = user_id)
            cars = []
            faves = 0
            # faves(favourites) counter
            for i in idresults:
                faves = faves + 1
                cars.append(i['car_id'])
            # get full name of car by car id
            carslist = []
            for x in cars:
                carslist.append(db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE id= :car", car=x))
            length = len(carslist)
            return render_template("favourites.html", carslist = carslist, length=length, faves = faves)
        # prevent duplicated favourites by a single user
        else:
            idresults = db.execute("SELECT car_id FROM favourites WHERE user_id = :user_id", user_id = user_id)
            cars = []
            faves = 0
            for i in idresults:
                faves = faves + 1
                cars.append(i['car_id'])
            carslist = []
            for x in cars:
                carslist.append(db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE id= :car", car=x))
            length = len(carslist)
            return render_template("favourites.html", carslist = carslist, length=length, faves = faves)
    # display faves if no favourite is added (no POST request)
    else:
        idresults = db.execute("SELECT car_id FROM favourites WHERE user_id = :user_id", user_id = user_id)
        cars = []
        faves = 0
        for i in idresults:
            faves = faves + 1
            cars.append(i['car_id'])
        carslist = []
        for x in cars:
            carslist.append(db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, stars FROM data WHERE id= :car", car=x))
        length = len(carslist)
        return render_template("favourites.html", carslist = carslist, length=length, faves = faves)

def search_func():
    # search for car by query
    a = request.args.get('query')
    global thequery
    thequery = a
    # search database for query
    results = db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE upper(Model) = :a UNION ALL SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, stars FROM data WHERE upper(Generation) =:b", a=a.upper(), b=a.upper())
    resultsnumber = len(results)
    return render_template("searchresult.html", a=a, results=results, resultsnumber=resultsnumber, thequery = thequery)

def filter_func():
    # get seats and enginetype
    seats = request.args.get('seats')
    enginetype= request.args.get('enginetype')
    #searchresult for previous query
    results = db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, stars FROM data WHERE upper(Model) = :model UNION ALL SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE upper(Generation) =:generation", model=thequery.upper(), generation=thequery.upper())
    models = []
    if len(results) != 0:
        for i in range(0, len(results)):
            models.append(results[i]['Model'])
    else:
        models = []
    # intial error is empty
    error = ""
    # intial success is true
    success = "Your search query gave the following results:"
    # filter is empty > return searchresults without filtering
    if seats =="" and enginetype =="":
        filtered = results
    # check filters and search database
    if seats =="":
        if enginetype !="":
            for model in models:
                print (model)
                filtered = db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE upper(Model) = :model AND Engine_type= :enginetype", model=model.upper(), enginetype=enginetype)
    # check filters and search database
    if seats !="":
        if enginetype =="":
            for model in models:
                filtered = db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE upper(Model) = :model AND Number_of_seater = :seats", model=model.upper(), seats=seats)
        elif enginetype !="":
            for model in models:
                filtered = db.execute("SELECT Make, Model, Generation, id, Year_from_Generation, Year_to_Generation, Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, CAST(stars AS INT) AS stars FROM data WHERE upper(Model) = :model AND Number_of_seater = :seats AND Engine_type= :enginetype", model=model.upper(), seats=seats, enginetype=enginetype)
    if len(filtered) == 0:
        error = "No cars found!"
        success = ""
    return render_template("filter.html", seats = seats, thequery = thequery, filtered = filtered, error=error, success = success, results=results)

def carpage_func():
    """Show user car info."""
    # get variables
    id = request.args.get('id')
    header = db.execute("SELECT Make, Model, Generation, Year_from_Generation, Year_to_Generation FROM data WHERE id = :id", id = id)
    brand = header[0]["Make"]
    model = header[0]["Model"]
    generation = header[0]["Generation"]
    startyear = header[0]["Year_from_Generation"]
    endyear = header[0]["Year_to_Generation"]
    stars = db.execute("SELECT stars FROM reviews WHERE car_id = :car_id", car_id = id)
    specs = db.execute("SELECT Serie, Trim, Number_of_seater, Engine_type, Max_speed_kmh, Curb_weight_kg, Gearbox_type, Fuel_tank_capacity_litre, Acceleration_0100_kmh_second, Engine_power_bhp, Number_of_cylinders FROM data WHERE id = :car_id", car_id = id)
    # get reviews by car id
    reviews = db.execute("SELECT user_id, CAST(stars AS INT) AS stars, review, date FROM reviews WHERE car_id = :car_id", car_id = id)
    reviews = reviews[::-1]
    userlist = []
    for x in reviews:
        userid = x["user_id"]
        username = db.execute("SELECT username FROM users WHERE id = :id", id = userid)
        userlist.append(username)
    # insert review into database
    if request.method == "POST":
        if session.get("user_id"):
            # grading system
            stars = request.form.get("rate")
            review = request.form.get("comment")
            user_id = session.get("user_id")
            old_number_grades = len(db.execute("SELECT car_id FROM reviews WHERE car_id= :car_id", car_id = id))
            global total_number_grades
            total_number_grades = old_number_grades + 1
            db.execute("INSERT INTO reviews (car_id, user_id, stars, review) VALUES(:car_id, :user_id, :stars, :review)", car_id=id, user_id=user_id, stars=stars, review=review)
            total_grades = db.execute("SELECT stars FROM reviews WHERE car_id= :car_id", car_id = id)
            total_grade = 0
            for i in total_grades:
                total_grade += i['stars']
            global grade
            grade = total_grade/total_number_grades
            db.execute("UPDATE data SET stars= :grade WHERE id= :id", grade=grade, id=id)
            return render_template("carpage.html", header = header, brand = brand, model = model, generation = generation, startyear = startyear, endyear = endyear, id=id, reviews = reviews, userlist = userlist, length = len(reviews), stars = stars, specs = specs)
        else:
            return render_template("login.html")
    else:
        return render_template("carpage.html", header = header, brand = brand, model = model, generation = generation, startyear = startyear, endyear = endyear, id=id, reviews = reviews, userlist = userlist, length = len(reviews), stars = stars, specs = specs)

def remove_review_func():
    # get user id and car id
    user_id = session.get("user_id")
    id = request.args.get('id')
    # update grade for car by id
    total_number_grades = len(db.execute("SELECT car_id FROM reviews WHERE car_id= :car_id", car_id = id))
    grade_to_retract = db.execute("SELECT stars FROM reviews WHERE (car_id= :id) AND (user_id = :user_id)", id = id, user_id = user_id)
    grade_to_retract = grade_to_retract[0]['stars']
    db.execute("DELETE FROM reviews WHERE (car_id= :id) AND (user_id = :user_id)", id = id, user_id = user_id)
    newgrade = grade * total_number_grades
    newgrade = newgrade - grade_to_retract
    if total_number_grades == 1:
        newgrade = 0
    else:
        newgrade = newgrade / (total_number_grades - 1)
    db.execute("UPDATE data SET stars= :newgrade WHERE id=:id", newgrade = newgrade, id = id)
    return redirect(url_for('profile'))

def unfavourite_func():
    # get user id and car id
    user_id = session.get("user_id")
    car_id = request.args.get('id')
    # remove favourite from database
    db.execute("DELETE FROM favourites WHERE (car_id= :car_id) AND (user_id = :user_id)", car_id = car_id, user_id = user_id)
    return redirect(url_for('favourites'))