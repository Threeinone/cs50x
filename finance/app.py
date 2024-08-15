import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from pytz import timezone

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = sqlite3.connect("finance.db", check_same_thread=False)
db.row_factory = sqlite3.Row
cur = db.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    user = cur.execute("SELECT username, cash FROM users WHERE id = ?"
                       , (session["user_id"],)
                       ).fetchone()

    portfolio = cur.execute("SELECT symbol, amount, bought_price FROM stocks WHERE user_id = ?"
                            , (session["user_id"],)
                            ).fetchall()
    stocks = []
    for entry in portfolio:
        stock = next((item for item in stocks if item["symbol"] == entry["symbol"]), None)
        if stock:
            stock["owned"] = stock["owned"] + entry["amount"]
        else:
            look = lookup(entry["symbol"])
            stock = { 'symbol': entry["symbol"]
                    , 'owned': entry["amount"]
                    , 'price': look["price"] if look else None
                    }
            stock["greater"] = (stock["price"] > entry["bought_price"])
            stocks.append(stock)

    return render_template("index.html", user=user, stocks=stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form["symbol"]
        amount = int(request.form["amount"])
        cash = cur.execute("SELECT cash FROM users WHERE id = ?",
                           (session["user_id"],)).fetchone()["cash"]
        price = lookup(symbol)["price"]
        time = datetime.now(timezone('America/New_York')).timetuple()

        if not (price or amount):
            return apology("bad input", 403)
        elif (cash < (price * amount)):
            return apology("too poor", 403)

        cur.execute("""
                    update users
                    set cash = ?
                    where id = ?
                    """, (cash - (price * amount), session["user_id"]))

        cur.execute("""
                    INSERT INTO
                    stocks(user_id, symbol, bought_price, amount, year, month, day, hour, minute)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, ( session["user_id"]
                         , symbol
                         , price
                         , amount
                         , time[0]
                         , time[1]
                         , time[2]
                         , time[3]
                         , time[4]
                          )
                       )
        db.commit()
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


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
        users = cur.execute(  "SELECT * FROM users WHERE username = ?"
                            , (request.form['username'],)
                            ).fetchall()

        # Ensure username exists and password is correct
        if len(users) < 1:
            return apology("invalid username and/or password", 403)

        for user in users:
            if check_password_hash( user["hash"], request.form.get("password") ):
                # Remember which user has logged in
                session["user_id"] = user["id"]

        # none of the queried users match the password
        if not session["user_id"]:
            return apology("invalid username and/or password", 403)

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
    if request.method == "GET":
        return render_template("quote.html")
    else:
        quote = lookup(request.form["symbol"])
        if quote:
            return render_template("quoted.html", quote=quote)
        else:
            return apology("bad symbol", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if username and password1:
            if password1 != password2:
                return apology("passwords don't match", 403)
            hash = generate_password_hash(password1)
            try:
                cur.execute("INSERT INTO users(username, hash) VALUES (?, ?)"
                            , (username, hash)
                            )
            except:
                return apology("username already exists", 403)
            db.commit()
            return redirect("/")
        else:
            return apology("invalid username and/or password", 403)

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        ## getting form data
        symbol = request.form["symbol"]
        sale_amount = int(request.form["amount"])
        ## guard case
        if not (sale_amount and symbol):
            return apology("bad submission", 403)
        if sale_amount < 1:
            return apology("doesn't work like that", 403)

        ## checking db
        fetched = cur.execute("SELECT id, symbol, amount FROM stocks WHERE symbol = ? AND user_id = ?"
                              , (symbol, session["user_id"])
                              ).fetchall()
        if not fetched:
            return apology("couldn't find stock", 403)

        ## setting up for loop
        asking_price = lookup(symbol)["price"]
        user_cash = cur.execute("select cash from users where id = ?", (session["user_id"],)
                                ).fetchone()["cash"]
        balance = 0
        for entry in fetched:
            entry_amount = entry["amount"]
            entry_id = entry["id"]
            ## trying to sell more than held in single entry
            ## delete one entry; it's been consumed
            if entry_amount < sale_amount:
                sale_amount = sale_amount - entry_amount
                balance = asking_price * entry_amount
                cur.execute("DELETE FROM stocks WHERE id = ?", (entry_id,))
                cur.execute("UPDATE users SET cash = ? WHERE id = ?",
                            ( user_cash + balance
                            , session["user_id"]
                            )
                           )
                db.commit()
            ## trying to sell <= entry amount
            ## subtract amount from entry, and then we're done
            ## update cash with balance
            else:
                difference = entry_amount - sale_amount
                balance = asking_price * difference
                cur.execute("UPDATE stocks SET amount = ? WHERE id = ? AND user_id = ?",
                            ( difference
                            , entry_id
                            , session["user_id"]
                            )
                           )
                cur.execute("UPDATE users SET cash = ? WHERE id = ?",
                            ( user_cash + balance
                            , session["user_id"]
                            )
                           )
                db.commit()
                break
        return redirect("/")

    else:
        ## pull symbols out of stocks record
        ## kinda dodgy, but oh well
        fetched = cur.execute("SELECT symbol FROM stocks WHERE user_id = ?"
                              , (session["user_id"],)
                              ).fetchall()
        symbols = []
        for entry in fetched:
            if entry["symbol"] in symbols:
                pass
            else:
                symbols.append(entry["symbol"])
        return render_template("sell.html", symbols=symbols)
