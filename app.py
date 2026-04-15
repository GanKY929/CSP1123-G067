from flask import Flask, render_template, request
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
    return render_template("index.html")


@app.route("/login")
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        return doLogin(username, password)
    return render_template("login.html")


@app.route("/doLogin" , methods=["POST"])
def doLogin(username, password):
        #database query to check if username and password are correct

        return render_template("login.html", username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        return doSignup(username, email, password, confirmPassword)
    return render_template("signup.html")


def doSignup(username, email, password, confirmPassword):
    try:
        if password.lower() or password.upper() == password:
            raise Exception("password cannot be all lowercase or all uppercase.")
        for char in password:
            if char.isspace():
                raise Exception("password cannot contain spaces.")
        if password != confirmPassword:
            raise Exception("Passwords do not match.")
        if len(password) < 8:
            raise Exception("password must be at least 8 characters long.")
        if db.session.query(                ).filter_by(username=username).first():
            raise Exception("username already exists.")
        if db.session.query(                ).filter_by(email=email).first():
            raise Exception("email already exists.")
        
        #new_user = (username=username, email=email, password=password)
        #db.session.add(new_user)
        db.session.commit()

    except Exception as error:
        return render_template("signup.html", error=str(error), username=username, email=email)


@app.route("/forgotPass")
def forgotPass():
    return render_template("forgotPass.html")