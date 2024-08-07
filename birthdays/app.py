import os, sqlite3
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

db = sqlite3.connect("birthdays.db", check_same_thread=False)
cur = db.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Add the user's entry into the database
        name = request.form["name"]
        birthdate = request.form["birthdate"]
        if name and birthdate:
            _, month, day = birthdate.split('-')
            row = [(name, month, day)]
            # SQL stuff here
            cur.executemany('INSERT INTO birthdays (name, month, day) VALUES(?, ?, ?)', row)
            db.commit()
            return redirect("/")
        else:
            return "epic fail"

    else: # method == "GET"

        # TODO: Display the entries in the database on index.html
        birthdays = cur.execute('SELECT * FROM birthdays').fetchall()
        return render_template("table.html", birthdays=birthdays)


