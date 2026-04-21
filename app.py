from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
db = SQLAlchemy(model_class = Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

app.config["SECRET_KEY"] = "this_is_a_secret_key_here"

import database
with app.app_context():
    db.create_all()

def checkUsername(username):
    return database.User.query.filter_by(username=username).first()
def checkEmail(email):
    return database.User.query.filter_by(email=email).first()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username: str = request.form.get("username")
    password: str = request.form.get("password")

    try:
        db_user = db.session.query(database.User).filter_by(username=username).first()

        if not db_user:
            raise Exception("Username does not exist.")
        if db_user.password != password:
            raise Exception("Incorrect password.")    
        
        return redirect(url_for("index"))
    
    except Exception as error:
        return render_template("login.html", error=str(error), username=username)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    username: str = request.form.get("username")
    email: str = request.form.get("email")
    password: str = request.form.get("password")
    confirmPassword: str = request.form.get("confirmPassword")

    if not username or not email or not password or not confirmPassword:
        raise Exception("Must fill all fields.")
    
    if username == db.session.query(database.User).filter_by(username=username).first():
        raise Exception("username already exists.")
    
    if password.lower() == password or password.upper() == password:
        raise Exception("password cannot be all lowercase or all uppercase.")
    
    for char in password:
        if char.isspace():
            raise Exception("password cannot contain spaces.")
        
    if password != confirmPassword:
        raise Exception("Passwords do not match.")
    
    if len(password) < 8:
        raise Exception("password must be at least 8 characters long.")
    
    if db.session.query(database.User).filter_by(username=username).first():
        raise Exception("username already exists")
    
    if db.session.query(database.User).filter_by(email=email).first():
        raise Exception("email already exists.")

    last_id: int = db.session.query(database.User).order_by(database.User.user_id).count()
    
    new_user = database.User(user_id = last_id+1., username = username, password = password, email = email, tagged_post = "test")
    db.session.add(new_user)
    db.session.commit()

    return render_template("signup.html", success="Account created! You can now log in.", username=username, email=email)

@app.route("/forgotPass", methods=["POST"])
def forgotPass():
    if request.method == "POST":
        return doForgotPass()
    return render_template("forgotPass.html")

@app.route("/doForgotPass", methods=["POST"])
def doForgotPass():
    email = request.form.get("email")
    return render_template("login.html", email=email)