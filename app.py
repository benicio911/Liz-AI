from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import openai
import gradio as gr
from werkzeug.security import generate_password_hash

# Initialize Flask app and connect to a database
app = Flask(__name__)
app.secret_key = "secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Define a User model for storing user data in the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

@app.route('/')
def base():
    return render_template('base.html')


# Define routes for handling user authentication
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        # hash the password for security
        hashed_password = generate_password_hash(password)
        # insert the new user record into the database
        db.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                   (username, hashed_password, email))
        db.commit()
        # redirect the user to the login page
        return redirect(url_for("login"))
    else:
        # if the request method is GET, render the registration form template
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Get user input from form and try to find a matching user in the database
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username, password=password).first()

        # If a matching user is found, log them in and redirect to dashboard
        if user:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error=True)

    return render_template("login.html", error=False)

@app.route("/dashboard")
def dashboard():
    if "logged_in" in session and session["logged_in"]:
        return render_template("dashboard.html", username=session["username"])
    else:
        return redirect(url_for("login"))

@app.route("/templates/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Define a voice recognition route for handling user input
@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Get audio file from request and transcribe it using OpenAI API
    audio_file = request.files["audio"]
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    # Return the transcript as plain text
    return transcript

if __name__ == "__main__":
    app.run(debug=True)