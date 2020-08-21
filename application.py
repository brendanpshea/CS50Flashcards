import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///flashcards.db")



@app.route("/")
@login_required
def index():
    """Give instructions on how to use program"""
    
    rows = db.execute("SELECT * from cards WHERE user_id=? AND julianday(due_date) < julianday('now') ORDER BY due_date", session["user_id"])
    
    return render_template("index.html", cards_due=len(rows))
    
    


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new flashcard"""
    if request.method == "POST":
        if not request.form.get("question"):
            flash("Must provide a question.")
            return render_template("/create.html")
        if not request.form.get("answer"):
            flash("Must provide an answer.")
            return render_template("/create.html")
        
        # Check to make sure question isn't already in user's deck of cards
        if len(db.execute("SELECT * from cards WHERE user_id=? AND question=?", session["user_id"], request.form.get("question"))) != 0:
            flash("You already have a card with that question.")
            return render_template("/create.html")
        
        
        db.execute("INSERT into cards (question, answer, user_id) VALUES (?,?, ?)", request.form.get("question"), request.form.get("answer"), session["user_id"])
        
        flash("Card sucessfully created.")
        return redirect("/create")
        
    return render_template("create.html")


@app.route("/review", methods=["GET", "POST"])
@login_required
def review():
    """Allow user to review flashcards"""
    
    # if method is post, update database, then redirect user back to continue the review
    if request.method == "POST":
        
        card_id = request.form.get("question_id")
        
        # if user got answer right, update due date to be TWICE as long as the current gap
        if request.form.get("user_answer") == "correct":
            # get today's julian date, and determine how many days it has been since card was last reviewed
            today_julian = float(db.execute("SELECT julianday('now')")[0]["julianday('now')"])
            last_review_date = float(db.execute("SELECT julianday(last_review) from cards WHERE id=?", card_id)[0]["julianday(last_review)"])
            current_gap = today_julian - last_review_date
            
            # If the current card's gap is less than half a day, set it to .5
            # This ensures that cards you get correct won't be due for at least one day
            if current_gap < .5:
                current_gap = .5
            
            # now, update new due date to be twice the current gap
            card_due_date = today_julian + (2 * current_gap)
            
            flash(f"Card due to be reviewed in approximately {2 * current_gap: .2f} days")
            db.execute("UPDATE cards SET due_date=datetime(?), correct=(1+(SELECT correct FROM cards WHERE id=?)),last_review=datetime('now') WHERE id=?", card_due_date, card_id, card_id)
            
            
        # if user got answer wrong, update due date to be now
        # Also update times incorrect
        elif request.form.get("user_answer") == "incorrect":
            flash("Card due to be reviewed again in 1 minute.")
            db.execute("UPDATE cards SET due_date=datetime('now', '+1 minutes'), incorrect=(1+(SELECT incorrect FROM cards WHERE id=?)), last_review=datetime('now') WHERE id=?", card_id, card_id)
            
        elif request.form.get("user_answer") == "delete":
            flash("Card has been deleted.")
            db.execute("DELETE from cards WHERE id=?", card_id)
            
        return redirect("/review")
        
    
    # if method is get, load next card due to be reviewed and display it
    rows = db.execute("SELECT * from cards WHERE user_id=? AND julianday(due_date) < julianday('now') ORDER BY due_date", session["user_id"])
    
    if len(rows) == 0:
        return render_template("review.html",nocards=True)
    else:
        return render_template("review.html", card=rows[0])  
        
    

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Invalid username and/or password")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    
    # Redirect user to login form
    return redirect("/")

@app.route("/stats")
@login_required
def stats():
    """Displays users stats, broken by card"""
    cards = db.execute("SELECT * FROM cards WHERE user_id=?", session["user_id"])
    
    # Calculate total number of reviews user has completed
    total_reviews = 0
    total_correct = 0
    
    for card in cards:
        total_reviews += (int)(card["correct"]) + (int)(card["incorrect"])
        total_correct += (int)(card["correct"])
    
    # to avoid division by zero for new users
    percent_correct = 0
    if total_reviews > 0:
        percent_correct = round(total_correct / total_reviews * 100) 
    
    # query to determine how many cards are due tomorrow
    due_tomorrow = len(db.execute("SELECT * from cards WHERE user_id=? AND julianday(due_date) < julianday('now', '+1 day') ORDER BY due_date", session["user_id"]))
    
    return render_template("stats.html", cards=cards, total_cards=len(cards), total_reviews=total_reviews, percent_correct=percent_correct, due_tomorrow=due_tomorrow)


# I did this differently than I did in Finance--
# I checked user input both on frontend (using Javascript) and backend
# I flashed error messages rather than directing the user apology pages.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide a username.")
            return render_template("register.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter a password.")
            return render_template("register.html")
            
        # Ensure email address was submitted
        elif not request.form.get("email"):
            flash("Please enter an email address.")
            return render_template("register.html")
            
        # Ensure passwords match
        elif request.form.get("password") != request.form.get("password2"):
            flash("Passwords don't match.")
            return render_template("register.html")
            
        # Ensure that an appropriate role has been selected
        elif request.form.get("role") != "teacher" and request.form.get("role") != "student":
            flash("Please enter whether you are a student or teacher.")
            return render_template("register.html")
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username isn't already taken
        if len(rows) != 0:
            flash("That username is taken.")
            return render_template("register.html")
            
            
        db.execute("INSERT into users (username, role, hash, email) VALUES (?,?,?,?)", request.form.get("username"), request.form.get("role"), generate_password_hash(request.form.get("password")), request.form.get("email"))

        # Redirect user to home page
        flash("Account creation successful.")
        return render_template("login.html")    
    
    return render_template("register.html")

@app.route("/teacher_stats")
@login_required
def teacher_stats():
    """Tool for teachers to allow them to view student statistics"""
    
    # determine whether user is teacher
    is_teacher = False;
    rows = db.execute("SELECT * from users WHERE id=?", session["user_id"])
    if rows[0]["role"] == "teacher":
        is_teacher = True    
        
    # get student stats
    students = db.execute("SELECT * from users WHERE role='student'")
    
    for student in students:
        cards = db.execute("SELECT * FROM cards WHERE user_id=?", student["id"])
    
        # Calculate total number of reviews user has completed
        student["total_reviews"] = 0
        student["total_correct"] = 0
    
        for card in cards:
            student["total_reviews"] += (int)(card["correct"]) + (int)(card["incorrect"])
            student["total_correct"] += (int)(card["correct"])
        
        # to avoid division by zero for users with 0 reviews
        student["percent_correct"] = 0
        if student["total_reviews"] > 0:
            student["percent_correct"] = round(student["total_correct"] / student["total_reviews"] * 100)
        
    return render_template("teacher_stats.html", is_teacher=is_teacher, students=students)

@app.route("/teacher_cards",methods=["GET", "POST"])
@login_required
def teacher_cards():
    """Tool for teachers that lists the cards they have created, and allows them to share
    these cards with their students"""
    
    # determine whether user is teacher; if not, redirect home
    is_teacher = False;
    rows = db.execute("SELECT * from users WHERE id=?", session["user_id"])
    if rows[0]["role"] == "teacher":
        is_teacher = True    
    
    # if user has selected cards, create copies of these cards for each student in the database
    if request.method == "POST":
        if rows[0]["role"] != "teacher":
            return redirect("/")
            
        # Check to make sure cards have been selected
        if not request.form.getlist("cards_selected"):
            flash("No cards have been selected")
            return redirect("/teacher_cards")
            
        # Gets the list of cards that have been selected
        card_ids = request.form.getlist("cards_selected")
        
        # get a list of students
        students = db.execute("SELECT * from users WHERE role='student'")
        
        # for each student, add the selected cards to their deck
        for student in students:
            for card_id in card_ids:
                card = db.execute("SELECT * from CARDS WHERE id=?", card_id)[0]
                
                # If student already has this question, don't add the new card
                if len(db.execute("SELECT * from cards WHERE question=? AND user_id=?", card["question"], student["id"])) == 0:
                    db.execute("INSERT INTO CARDS (question, answer, user_id) VALUES (?,?,?)", card["question"], card["answer"], student["id"])
        
        flash(f"Cards shared with {len(students)} students.")
        
        return redirect("/teacher_cards")
        
    # handles get requests
    else:
        # get a list of cards that teacher has created
        cards = db.execute("SELECT * from cards WHERE user_id=?", session["user_id"])
        
        return render_template("teacher_cards.html", is_teacher=is_teacher, cards=cards)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


