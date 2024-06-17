import os
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Use SQLite database
connection = sqlite3.connect("database.db")
with open('schema.sql') as f:
    connection.executescript(f.read())
db = connection.cursor()

def get_db():
    """
    Get database connection
    """
    if 'db' not in g:
        g.db = sqlite3.connect("database.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """
    Close database connection at end of each request
    """
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route("/")
@login_required
def index():
    # Shows group, people in group, what their expenses are within group

    return apology("TODO", 403)


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
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        row = cursor.fetchone()

        # Ensure username exists and password is correct
        if row is None or not check_password_hash(row["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row["id"]

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
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure no duplicate username
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT username FROM users WHERE username = ?", (request.form.get("username"),))
        username = cursor.fetchone()

        if username is not None:
            return apology("username already exists", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure password is the same as confirmation
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password is not the same as confirmation", 400)

        # Hash the password
        hash_password = generate_password_hash(request.form.get("password"), method='pbkdf2', salt_length=16)

        # Attempt to insert the new user into the database
        try:
            cursor.execute(
                "INSERT INTO users (username, hash) VALUES (?, ?)",
                (request.form.get("username"), hash_password)
            )
            db.commit()
        except sqlite3.IntegrityError:
            return apology("username already exists", 403)

        # Redirect user to login page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")
    

"""Add remove member too"""
@app.route("/group", methods=["GET", "POST"])
def group():
    # Create group name OR pick group and add member
    if request.method == "POST":
        # Get input
        create_group_name = request.form.get("group_name")
        chosen_group = request.form.get("groups")

        # Ensure group name submitted
        if not create_group_name and not chosen_group:
            return apology("must submit group name or select group")
        
        # Get database
        db = get_db()
        cursor = db.cursor()

        # Create new group
        if create_group_name and not chosen_group:
            cursor.execute("INSERT INTO groups (creator_id, group_name) VALUES (?, ?);", (session["user_id"], create_group_name))
            db.commit()
            return redirect("/group")
        
        # Add members to group
        elif not create_group_name and chosen_group:
            member = request.form.get("member")
            cursor.execute("SELECT id FROM groups WHERE group_name = ?;", (chosen_group,))
            group = cursor.fetchone()

            group_id = group["id"]
            cursor.execute("INSERT INTO group_members (group_id, user_id, member_name) VALUES (?, ?, ?)", (group_id, session["user_id"], member))
            db.commit()
            return redirect("/group")
    
    # User reached route via GET (as by clicking a link or via redirect)
    else:    
        # Get database
        db = get_db().cursor()
        group_name = db.execute("SELECT group_name FROM groups WHERE creator_id = ?;", (session["user_id"],)).fetchall()

         # Display group names in the select inputs
        return render_template("group.html", groups=group_name)


@app.route("/split", methods=["GET", "POST"])
def split():
    # Choose group, choose members of group, put expense
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get inputs
        group_name = request.form.get("groups")
        amount = request.form.get("amount")

        # Ensure group name is submitted
        if not group_name:
            return apology("must select group name", 403)
        
        # Get database
        db = get_db().cursor()

        # Get input from checkboxes
        group = db.execute("SELECT id FROM groups WHERE group_name = ?;", (group_name,)).fetchone()
        group_id = group["id"]
        num_names = db.execute("SELECT member_name FROM group_members WHERE user_id = ? AND group_id = ?", (session["user_id"], group_id,)).fetchall()
        
        # Show group member names for checkbox
        render_template("split.html", names = num_names)

        # Ensure amount is submitted
        if not amount:
            return apology("must submit amount", 403)
        
        # Add expense to members by calculating split
        

        # Redirect
        return redirect("/split")

    # User reached route via GET (as by clicking a link or via redirect)    
    else:    
        # Get database
        db = get_db().cursor()
        group_name = db.execute("SELECT group_name FROM groups WHERE creator_id = ?;", (session["user_id"],)).fetchall()

        # Display group names in the select inputs
        return render_template("split.html", groups = group_name)


@app.route("/pay", methods=["GET", "POST"])
def pay():
    # 
    return apology("TODO", 403)


@app.route("/activity", methods=["GET", "POST"])
def activity():
    # Shows all transactions for all groups
    return apology("TODO", 403)