from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
db = SQLAlchemy(model_class = Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

import database
with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html", success=None)


@app.route("/login" , methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.session.query(database.User).filter_by(username=username).first()
        if not user:
            return render_template("login.html", error="Username not found.")
        if not database.check_password(user.password, password):
            return render_template("login.html", error="Incorrect password.")
        session["user_id"] = user.id
        return redirect(url_for("index"), success="Logged in successfully!")
    return render_template("login.html")

@app.route("/signup" , methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        return doSignup(username, email, password, confirmPassword)
    return render_template("signup.html")

@app.route("/doSignup", methods=["POST"])
def doSignup():
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")
    try:
        if db.session.query(database.User).filter_by(username=username).first():
            raise ValueError("Username already exists.")
        if db.session.query(database.User).filter_by(email=email).first():
            raise ValueError("Email already exists.")
        if password.lower() == password or password.upper() == password:
            raise ValueError("Password cannot be all lowercase or all uppercase.")
        if any(char.isspace() for char in password):
            raise ValueError("Password cannot contain spaces.")
        if password != confirmPassword:
            raise ValueError("Passwords do not match.")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        new_user = database.User(user_id=None, username=username, email=email, password=password, tagged_post=0)
        db.session.add(new_user)
        db.session.commit()
        return render_template("signup.html", success="Account created! You can now log in.", username=username, email=email)
    except ValueError as error:
        return render_template("signup.html", error=str(error), username=username, email=email)

@app.route("/forgotPass", methods=["GET", "POST"])
def forgotPass():
    if request.method == "POST":
        email = request.form.get("email")
        return doForgotPass(email)
    return render_template("forgotPass.html")

@app.route("/doForgotPass", methods=["POST"])
def doForgotPass(email):
    return render_template("login.html", email=email)