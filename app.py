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
def setup_db():
    """
    Setup database connection
    """
    connection = sqlite3.connect("database.db")
    try:
        with open('schema.sql') as f:
            connection.executescript(f.read())
        print("Database setup completed successfully.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        connection.close()

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
        cursor.execute("SELECT * FROM users WHERE username = ?;", (request.form.get("username"),))
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
        cursor.execute("SELECT username FROM users WHERE username = ?;", (request.form.get("username"),))
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
                "INSERT INTO users (username, hash) VALUES (?, ?);",
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
            flash("Group created")
            return redirect("/group")
        
        # Add members to group
        elif not create_group_name and chosen_group:
            member = request.form.get("member")
            cursor.execute("SELECT id FROM groups WHERE group_name = ?;", (chosen_group,))
            group = cursor.fetchone()

            group_id = group["id"]
            cursor.execute("INSERT INTO group_members (group_id, user_id, member_name) VALUES (?, ?, ?);", (group_id, session["user_id"], member))
            db.commit()
            flash("Member added")
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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get inputs
        group_name = request.form.get("groups")

        # Ensure group name is submitted
        if not group_name:
            return apology("must select group name", 403)
        
        # Get database of group names
        db = get_db().cursor()
        group = db.execute("SELECT id FROM groups WHERE creator_id = ? AND group_name = ?;", (session["user_id"], group_name,)).fetchone()
        group_id = group["id"]
        members_name = db.execute("SELECT member_name FROM group_members WHERE user_id = ? AND group_id = ?;", (session["user_id"], group_id,)).fetchall()

        # Render splitting html
        return render_template("splitting.html", names=members_name, group_name=group_name)

    # User reached route via GET (as by clicking a link or via redirect)    
    else:    
        # Get database
        db = get_db().cursor()
        group_name = db.execute("SELECT group_name FROM groups WHERE creator_id = ?;", (session["user_id"],)).fetchall()

        # Display group names in the select inputs
        return render_template("split.html", groups=group_name)


@app.route("/splitting", methods=["GET", "POST"])
def splitting():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get inputs
        amount = request.form.get("amount")
        selected_members = request.form.getlist("names")
        description = request.form.get("description")
        group_name = request.form.get("group_name")

        # Ensure at least one checkbox selected
        if not selected_members:
            return apology("must select at least one checkbox", 403)

        # Ensure amount submitted
        if not amount:
            return apology("must submit expense to be split", 403)
        
        # Ensure amount is a number
        try:
            amount = round(float(amount), 2)
        except ValueError:
            return apology("must be a number", 400)

        # Ensure amount is a positive number
        if amount <= 0:
            return apology("must be a positive number", 400)
        
        # Ensure description is submitted
        if not description:
            return apology("must submit a description", 403)
        
        # Split amount with number of people selected
        num_people = len(selected_members)
        result = amount / num_people

        # Get group_id 
        db = get_db().cursor()
        group = db.execute("SELECT id FROM groups WHERE creator_id = ? AND group_name = ?;", (session["user_id"], group_name)).fetchone()
        group_id = group["id"]

        # Insert the split amount for each member into the expenses table
        for member_name in selected_members:
            group_member = db.execute("SELECT id FROM group_members WHERE group_id = ? AND member_name = ?;", (group_id, member_name)).fetchone()
            group_member_id = group_member["id"]
            db.execute("INSERT INTO expenses (group_id, group_member_id, description, amount) VALUES (?, ?, ?, ?);", (group_id, group_member_id, description, result))

            # Check if there is already an expense entry for this member
            existing_expense = db.execute("SELECT amount FROM expenses WHERE group_id = ? AND group_member_id = ? AND description = ?;", (group_id, group_member_id, description)).fetchone()

            if existing_expense:
                # Update the existing expense amount by adding the result
                new_amount = existing_expense["amount"] + result
                db.execute("UPDATE expenses SET amount = ? WHERE group_id = ? AND group_member_id = ? AND description = ?;", (new_amount, group_id, group_member_id, description))
            else:
                # Insert the new expense if no existing entry is found
                db.execute("INSERT INTO expenses (group_id, group_member_id, description, amount) VALUES (?, ?, ?, ?);", (group_id, group_member_id, description, result))

            # Add to activity
            db.execute("INSERT INTO transactions (transaction_id, action, group_name, group_member, description, amount) VALUES (?, ?, ?, ?, ?, ?);", (session["user_id"], "OWE", group_name, member_name, description, result))

        get_db().commit() 

        flash("Expense split")

        # Render splitting html
        members_name = db.execute("SELECT member_name FROM group_members WHERE user_id = ? AND group_id = ?;", (session["user_id"], group_id)).fetchall()
        return render_template("splitting.html", names=members_name, group_name=group_name)


@app.route("/pay", methods=["GET", "POST"])
def pay():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get inputs
        group_name = request.form.get("groups")

        # Ensure group name is submitted
        if not group_name:
            return apology("must select group name", 403)
        
        # Get database of group names
        db = get_db().cursor()
        group = db.execute("SELECT id FROM groups WHERE creator_id = ? AND group_name = ?;", (session["user_id"], group_name,)).fetchone()
        group_id = group["id"]
        members_name = db.execute("SELECT member_name FROM group_members WHERE user_id = ? AND group_id = ?;", (session["user_id"], group_id,)).fetchall()

        # Render splitting html
        return render_template("paying.html", names=members_name, group_name=group_name)

    # User reached route via GET (as by clicking a link or via redirect)    
    else:    
        # Get database
        db = get_db().cursor()
        group_name = db.execute("SELECT group_name FROM groups WHERE creator_id = ?;", (session["user_id"],)).fetchall()

        # Display group names in the select inputs
        return render_template("pay.html", groups=group_name)


@app.route("/paying", methods=["GET", "POST"])
def paying():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get inputs
        amount = request.form.get("amount")
        selected_member = request.form.get("names")
        group_name = request.form.get("group_name")

        # Ensure at least one checkbox selected
        if not selected_member:
            return apology("must select a member", 403)

        # Ensure amount submitted
        if not amount:
            return apology("must submit money to be paid", 403)
        
        # Ensure amount is a number
        try:
            amount = round(float(amount), 2)
        except ValueError:
            return apology("must be a number", 400)

        # Ensure amount is a positive number
        if amount <= 0:
            return apology("must be a positive number", 400)

        # Get group_id 
        db = get_db().cursor()
        group = db.execute("SELECT id FROM groups WHERE creator_id = ? AND group_name = ?;", (session["user_id"], group_name)).fetchone()
        group_id = group["id"]

        # Get the total outstanding expenses for the member
        group_member = db.execute("SELECT id FROM group_members WHERE group_id = ? AND member_name = ?;", (group_id, selected_member)).fetchone()
        group_member_id = group_member["id"]
        total_expenses = db.execute("SELECT SUM(amount) as total FROM expenses WHERE group_id = ? AND group_member_id = ?;", (group_id, group_member_id)).fetchone()["total"]

        # Ensure amount is not more than their expense
        if amount > total_expenses:
            return apology("payment amount cannot exceed total expenses", 400)

        # Convert amount to negative for payment
        amount = -amount

        # Retrieve the original description
        original_description = db.execute("SELECT description FROM expenses WHERE group_id = ? AND group_member_id = ? ORDER BY id DESC LIMIT 1;", (group_id, group_member_id)).fetchone()["description"]

        # Insert negative amount for the member into the expenses table
        db.execute("INSERT INTO expenses (group_id, group_member_id, description, amount) VALUES (?, ?, ?, ?)", (group_id, group_member_id, original_description, amount))

        # Add to activity
        amount *= -1
        changed_description = original_description + " | PAYING"
        db.execute("INSERT INTO transactions (transaction_id, action, group_name, group_member, description, amount) VALUES (?, ?, ?, ?, ?, ?)", (session["user_id"], "PAY", group_name, selected_member, original_description, amount))

        get_db().commit() 

        if amount == total_expenses:
            flash("Expense paid")
        else:
            flash("Expense being paid")

        # Render splitting html
        members_name = db.execute("SELECT member_name FROM group_members WHERE user_id = ? AND group_id = ?;", (session["user_id"], group_id)).fetchall()
        return render_template("paying.html", names=members_name, group_name=group_name)


@app.route("/activity", methods=["GET", "POST"])
def activity():
    # Shows all transactions for all groups
    db = get_db().cursor()
    tables = db.execute("SELECT action, group_name, group_member, description, amount, timestamp FROM transactions WHERE transaction_id = ?;", (session["user_id"],))
    return render_template("activity.html", tables=tables)


if __name__ == '__main__':
    setup_db()
    app.run()