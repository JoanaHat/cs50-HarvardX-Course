import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from datetime import datetime
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

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


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    shares = db.execute("SELECT * FROM shares_purchase WHERE user_id=?", session["user_id"])
    user_cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])

    if shares:
        # Get an updated shares price
        for s in shares:
            api_dic = lookup(s["symbol"])
            s["price"] = "{:.2f}".format(api_dic["price"])
            s["total_purchase"] = "{:.2f}".format(s["shares_amount"] * api_dic["price"])

        balance = db.execute("SELECT SUM(total_purchase) AS sum FROM shares_purchase WHERE user_id=?", session["user_id"])
        total = balance[0]["sum"] + user_cash[0]["cash"]
    else:
        total = user_cash[0]["cash"]

    return render_template("index.html", shares=shares, cash=usd(user_cash[0]["cash"]), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":
        # Ensure a symbol was submitted
        if not request.form.get("symbol") and not request.form.get("shares"):
            return apology("must provide symbol and/or shares", 400)

        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Ensure a positive integer was provided
        if not request.form.get("shares"):
            return apology("number of shares missing", 400)
            
        if not request.form.get("shares").isnumeric():
            return apology("invalid shares", 400)    

        if int(float(request.form.get("shares"))) <= 1:
            return apology("Number must be greater than 1", 400)

        api_dic = lookup(request.form.get("symbol"))

        # Ensure symbol is valid
        if not api_dic:
            return apology("invalid symbol", 400)

        # Calculate total amount for shares
        purchase = float(request.form.get("shares")) * api_dic["price"]

        # Get user's total cash
        user_cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])

        # Ensure user has enough money to purchase shares
        if purchase > user_cash[0]["cash"]:
            return apology("Insufficient Funds", 400)

        cash = user_cash[0]["cash"] - purchase

        # Get time of purchase
        now = datetime.now()
        dt_now = now.strftime("%d-%m-%Y %H:%M:%S")

        user_symbol = db.execute("SELECT symbol, shares_amount FROM shares_purchase WHERE user_id=? AND symbol=?", 
                                 session["user_id"], request.form.get("symbol").strip().upper())

        # Check if shares already exists, if yes, add to existing shares; and if not, create new shares
        if not user_symbol:
            db.execute("INSERT INTO shares_purchase (date_time, user_id, symbol, name, price, shares_amount, total_purchase) VALUES(?, ?, ?, ?, ?, ?, ?)",
                       dt_now, session["user_id"], api_dic["symbol"], api_dic["name"], api_dic["price"], float(request.form.get("shares")), purchase)
        else:
            num = user_symbol[0]["shares_amount"] + int(request.form.get("shares"))
            total_p = api_dic["price"] * num

            db.execute("UPDATE shares_purchase SET price=?, shares_amount=?, total_purchase=? WHERE symbol=? AND user_id=?",
                       api_dic["price"], num, total_p, request.form.get("symbol").strip().upper(), session["user_id"])

        # Record transaction
        db.execute("INSERT INTO transactions (date, user_id, symbol, trans_type, shares_amount, price) VALUES(?, ?, ?, ?, ?, ?)",
                   dt_now, session["user_id"], api_dic["symbol"], "Bought", float(request.form.get("shares")), "{:.2f}".format(api_dic["price"]))

        # Update user's total cash
        db.execute("UPDATE users SET cash=? WHERE id=?", cash, session["user_id"])

        flash("Shares Successfully Purchased!! More shares to your money machine!")
        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Get all transactions made by a user
    transaction = db.execute("SELECT * FROM transactions WHERE user_id=? ORDER BY date ASC", session["user_id"])
    return render_template("history.html", transaction=transaction)


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        # Ensure a symbol was submitted and is valid
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        # Get company from API
        api_dic = lookup(request.form.get("symbol").strip().upper())

        # Ensure the dictionary is not empty
        if not api_dic:
            return apology("invalid symbol", 400)

        return render_template("quoted.html", api_dic=api_dic, price=usd(api_dic["price"]))

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted and does not already exist
        if not request.form.get("username") and not request.form.get("password"):
            return apology("must provide username and/or password", 400)

        if not request.form.get("username"):
            return apology("must provide username", 400)

        rows = db.execute("SELECT count(*) AS count FROM users WHERE username=?", request.form.get("username"))

        if rows[0]["count"]:
            return apology("name already exists", 400)

        # Ensure passwords were submitted and they match
        if not request.form.get("password"):
            return apology("must provide password", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        # Redirect user to login page
        flash("Registration Successful: login to your account!!")
        return render_template("login.html")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        # Ensure a symbol and shares were submitted
        if not request.form.get("symbol") and not request.form.get("shares"):
            return apology("must provide symbol and/or shares", 400)

        if not request.form.get("shares"):
            return apology("number of shares missing", 400)

        # Ensure a symbol was submitted and it exists
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)

        shares_symbol = db.execute("SELECT symbol FROM shares_purchase WHERE user_id=? AND symbol=?", 
                                   session["user_id"], request.form.get("symbol"))
        if not shares_symbol:
            return apology("invalid symbol", 400)

        # Ensure a positive integer was provided
        if int(request.form.get("shares")) <= 0:
            return apology("number must be greater than 0", 400)

        # Ensure user owns the amount of shares provided
        shares_info = db.execute("SELECT * FROM shares_purchase WHERE user_id=? AND symbol=?", 
                                 session["user_id"], request.form.get("symbol"))
        if shares_info[0]["shares_amount"] < int(request.form.get("shares")):
            return apology("not enough shares", 400)

        # Get user's cash balance
        user_cash = db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])

        api_dic = lookup(request.form.get("symbol"))

        now = datetime.now()
        dt_now = now.strftime("%d-%m-%Y %H:%M:%S")

        # Calculate remaining shares, total and cash amount
        num = shares_info[0]["shares_amount"] - int(request.form.get("shares"))
        total_p = api_dic["price"] * num
        cash = user_cash[0]["cash"] + (int(request.form.get("shares")) * api_dic["price"])

        # Update cash, shares and total or delete entire shares
        if num:
            db.execute("UPDATE shares_purchase SET price=?, shares_amount=?, total_purchase=? WHERE symbol=? AND user_id=?", 
                       api_dic["price"], num, total_p, request.form.get("symbol"), session["user_id"])
            db.execute("UPDATE users SET cash=? WHERE id=?", cash, session["user_id"])
            db.execute("INSERT INTO transactions (date, user_id, symbol, trans_type, shares_amount, price) VALUES(?, ?, ?, ?, ?, ?)",
                       dt_now, session["user_id"], api_dic["symbol"], "Sold", float(request.form.get("shares")), "{:.2f}".format(api_dic["price"]))
        else:
            db.execute("DELETE FROM shares_purchase WHERE symbol=? and user_id=?", request.form.get("symbol"), session["user_id"])
            db.execute("UPDATE users SET cash=? WHERE id=?", cash, session["user_id"])
            db.execute("INSERT INTO transactions (date, user_id, symbol, trans_type, shares_amount, price) VALUES(?, ?, ?, ?, ?, ?)",
                       dt_now, session["user_id"], api_dic["symbol"], "Sold", float(request.form.get("shares")), "{:.2f}".format(api_dic["price"]))

        flash("Shares Successfully Sold!! More money to your money machine!")
        return redirect("/")

    else:
        shares_symbols = db.execute("SELECT symbol FROM shares_purchase Where user_id=?", session["user_id"])
        return render_template("sell.html", shares=shares_symbols)


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change user password"""

    if request.method == "POST":
        # Ensure old and new passwords were submitted 
        if not request.form.get("old_password") and not request.form.get("new_password"):
            return apology("must provide passwords", 400)

        if not request.form.get("old_password"):
            return apology("must provide old_password", 400)

        rows = db.execute("SELECT hash FROM users WHERE id=?", session["user_id"])

        # Ensure passwords were submitted and they match
        if not request.form.get("new_password"):
            return apology("must provide new_password", 400)

        if request.form.get("new_password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)
            
        # Check if old password matches with database
        if check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            db.execute("UPDATE users SET hash=? WHERE id=?", generate_password_hash(
                request.form.get("new_password")), session["user_id"])

        # Redirect user to login page
        flash("Password Successfully Changed!")
        return redirect("/")
    else:
        return render_template("password.html")
        

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
