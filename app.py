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
def doLogin():
    if request.method == "POST":
        username: str = request.form.get("username")
        password: str = request.form.get("password")

    try:
        db_user = db.session.query(database.User).filter_by(username=username).first()

        if not db_user:
            raise Exception("Username does not exist.")
        if db_user.password != password:
            raise Exception("Incorrect password.")    
        return render_template("index.html", username=username)
    
    except Exception as error:
        return render_template("login.html", error=str(error), username=username)

@app.route("/signup")
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")

        return doSignup(username, email, password, confirmPassword)
    
    return render_template("signup.html")

@app.route("/doSignup", methods=["POST"])
def doSignup():
    print("\n\nThis router works!\n\n")

    if request.method == "POST":
        username: str = request.form.get("username")
        email: str = request.form.get("email")
        password: str = request.form.get("password")
        confirmPassword: str = request.form.get("confirmPassword")

        if not username or not email or not password or not confirmPassword:
            print("Something went wrong here")
            return render_template("signup.html")
        
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
        
        new_user = database.User(user_id = 3, username = username, password = password, email = email, tagged_post = "test")
        db.session.add(new_user)
        db.session.commit()

        return render_template("signup.html", success="Account created! You can now log in.", username=username, email=email)

@app.route("/forgotPass")
def forgotPass():
    return render_template("forgotPass.html")