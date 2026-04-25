from flask import Flask, render_template, request, redirect, url_for,session, flash
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


@app.route("/login" , methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        try:
            user = checkUsername(username)
            if not user:
                raise Exception("Username not found.")
            if not database.checkPassword(user.password, password):
                raise Exception("Incorrect password.")
        except Exception as error:
            flash(str(error), category="error")
            return render_template("login.html", username=username)
        
        flash("Logged in successfully!", category="success")
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/signup" , methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        return doSignup()
    return render_template("signup.html")

@app.route("/doSignup", methods=["POST"])
def doSignup():
    username = request.form.get("username")
    email = request.form.get("email")   
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")

    try:
        if checkUsername(username):
            error = "Username already exists."
            raise Exception(error)
        if checkEmail(email):
            error = "Email already exists."
            raise Exception(error)
        if password.lower() == password or password.upper() == password:
            error = "Password cannot be all lowercase or all uppercase."
            raise Exception(error)
        if any(char.isspace() for char in password):
            error = "Password cannot contain spaces."
            raise Exception(error)
        if password != confirmPassword:
            error = "Passwords do not match."
            raise Exception(error)
        if len(password) < 8:
            error = "Password must be at least 8 characters long."
            raise Exception(error)

        hashed_password = database.generatePasswordHash(password)

        new_user = database.User(
            username=username,
            email=email,
            password=hashed_password,
            tagged_post=0
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", category="success")
        return render_template("login.html", username=username)
    except Exception as error:
        flash(str(error), category="error")
        return render_template("signup.html", username=username, email=email)


@app.route("/forgotPass", methods=["POST"])
def forgotPass():
    if request.method == "POST":
        return doForgotPass()
    return render_template("forgotPass.html")

@app.route("/doForgotPass", methods=["POST"])
def doForgotPass():
    email = request.form.get("email")
    return render_template("login.html", email=email)

if __name__ == "__main__":
    app.run(debug=True)