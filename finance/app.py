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
## Row type makes returns queriable by column name
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

    ## stocks tracks separate transactions, so we're grouping them
    ## I actually don't know why I'm doing that now
    ## transactions table handles the purchase and sale records, so it's
        # probably unnecessary complexity now
    portfolio = cur.execute("""
                            SELECT symbol, SUM(amount) AS amount, AVG(price) AS price 
                            FROM stocks WHERE user_id = ?
                            GROUP BY symbol
                            """
                            , (session["user_id"],)
                            ).fetchall()
    stocks = []
    for entry in portfolio:
        ## idk if added error checking here matters
        queried_price = lookup(entry["symbol"])
        stock = {  'symbol': entry["symbol"]
                 , 'owned': entry["amount"]
                 , 'price': queried_price["price"] if queried_price else None
                 }
        stock["value"] = (stock["price"] - entry["price"])
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
        ## could return None and break something
        ## I don't care
        price = lookup(symbol)["price"]
        time = datetime.now(timezone('America/New_York')).timetuple()

        if not (price or amount):
            return apology("bad input", 403)
        if (cash < (price * amount)):
            return apology("too poor", 403)

        cur.execute("""
                    UPDATE users
                    SET cash = ?
                    WHERE id = ?
                    """, (cash - (price * amount), session["user_id"]))

        cur.execute("""
                    INSERT INTO
                    stocks(user_id, symbol, amount, price)
                    VALUES (?, ?, ?, ?)
                    """, ( session["user_id"]
                          , symbol
                          , amount
                          , price
                          )
                    )
        cur.execute("""
                    insert INTO
                    transactions (symbol, type, amount, price, year, month, day, hour, minute, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (  symbol
                          , "purchase"
                          , amount
                          , price
                          , time[0]
                          , time[1]
                          , time[2]
                          , time[3]
                          , time[4]
                          , session["user_id"]
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
    transaction_records = cur.execute("SELECT * FROM transactions WHERE user_id = ?"
                , (session["user_id"],)
                ).fetchall()

    transactions = []
    for record in transaction_records:
        transaction = {
                'type': record["type"],
                'symbol': record["symbol"],
                'amount': record["amount"],
                'price': record["price"],
                'time': f"{record['year']}-{record['month']}-{record['day']} {record['hour']}:{record['minute']}"
                }
        print(transaction)
        print(transactions)
        transactions.append(transaction)
        print(transactions)
    return render_template("history.html", transactions=transactions)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        submitted_username = request.form["username"]
        submitted_password = request.form["password"]
        if submitted_username == None:
            return apology("must provide username", 403)
        if submitted_password == None:
            return apology("must provide password", 403)

        user_query = cur.execute(  "SELECT * FROM users WHERE username = ?"
                            , (submitted_username,)
                            ).fetchall()

        if len(user_query) < 1:
            return apology("invalid username and/or password", 403)

        for user in user_query:
            if check_password_hash( user["hash"], submitted_password ):
                ## Remember which user has logged in
                session["user_id"] = user["id"]

        ## none of the queried users match the password
        if not session["user_id"]:
            return apology("invalid username and/or password", 403)

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
        quote = lookup(request.form["symbol"])
        if quote:
            return render_template("quoted.html", quote=quote)
        else:
            return apology("bad symbol", 403)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user"""
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if not username and password1:
            return apology("invalid username and/or password", 403)
        if password1 != password2:
            return apology("passwords don't match", 403)

        hash = generate_password_hash(password1)
        try:
            cur.execute("INSERT INTO users(username, hash) VALUES (?, ?)"
                        , (username, hash))
        except:
            return apology("username already exists", 403)
        db.commit()
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        symbol = request.form["symbol"]
        amount_to_sell = int(request.form["amount"])

        if not (amount_to_sell and symbol):
            return apology("bad submission", 403)
        if amount_to_sell < 1:
            return apology("doesn't work like that", 403)

        fetched = cur.execute("SELECT id, symbol, amount FROM stocks WHERE symbol = ? AND user_id = ?"
                              , (symbol, session["user_id"])
                              ).fetchall()
        if not fetched:
            return apology("couldn't find stock", 403)

        ## this potentially returns None, but idc
        asking_price = lookup(symbol)["price"]
        user_cash = cur.execute("select cash from users where id = ?"
                                , (session["user_id"],)
                                ).fetchone()["cash"]
        balance = 0
        stocks_sold = 0
        for entry in fetched:
            entry_amount = entry["amount"]
            entry_id = entry["id"]

            ## we handle it like this because as is buy() creates new entries
                # of the same stock instead of updating
            ## may change later
            if entry_amount < amount_to_sell:

                amount_to_sell -=  entry_amount
                balance += asking_price * entry_amount
                stocks_sold += entry_amount

                cur.execute("DELETE FROM stocks WHERE id = ?", (entry_id,))

            else:

                balance += asking_price * amount_to_sell
                stocks_sold += amount_to_sell

                ## empty amount stock entries = muddy data
                if amount_to_sell == entry_amount:
                    cur.execute("DELETE FROM stocks WHERE id = ?", (entry_id,))
                
                else: # sale_amount < entry_amount

                    difference = entry_amount - amount_to_sell
                    cur.execute("UPDATE stocks SET amount = ? WHERE id = ? AND user_id = ?",
                                ( difference
                                 , entry_id
                                 , session["user_id"]
                                 )
                                )
                break

        time = datetime.now(timezone('America/New_York')).timetuple()

        cur.execute("UPDATE users SET cash = ? WHERE id = ?",
                    ( user_cash + balance
                     , session["user_id"]))
        cur.execute("""
                    INSERT INTO transactions
                    (symbol, type, amount, price, year, month, day, hour, minute, user_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (  symbol
                     , "sale"
                     , stocks_sold
                     , asking_price
                     , time[0]
                     , time[1]
                     , time[2]
                     , time[3]
                     , time[4]
                     , session["user_id"]
                     )
                    )
        db.commit()
        return redirect("/")

    else:
        fetched = cur.execute("""
                              SELECT symbol FROM stocks WHERE user_id = ?
                              GROUP BY symbol
                              """
                              , (session["user_id"],)
                              ).fetchall()
        symbols = []
        for entry in fetched:
            symbols.append(entry["symbol"])
        return render_template("sell.html", symbols=symbols)
