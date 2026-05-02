from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import random, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
db = SQLAlchemy(model_class = Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

import config
app.config["SECRET_KEY"] = config.secret_key

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

    if request.method == "POST":
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
    
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmPassword = request.form.get("confirmPassword")

    try:
        if not all([username, email, password, confirmPassword]):
            raise Exception("Must fill all fields.")
        if db.session.query(database.User).filter_by(username=username).first():
            raise Exception("Username already exists.")
        if db.session.query(database.User).filter_by(email=email).first():
            raise Exception("Email already exists.")
        if password != confirmPassword:
            raise Exception("Passwords do not match.")
        if len(password) < 8:
            raise Exception("Password must be at least 8 characters long.")

        hashed_pw = database.generatePassword

        otp_code = str(random.randint(100000, 999999))

        new_user = database.User(
            username=username,
            email=email,
            password=hashed_pw,
            tagged_post="test",
            otp_code=otp_code,
            otp_created_at=datetime.utcnow(),
            verified=False
        )
        db.session.add(new_user)
        db.session.commit()

        send_otp_email(email, otp_code)
        return render_template("otp.html", email=email)
    
    except Exception as error:
        return render_template("sign.html", error=str(error))

@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "GET":
        return render_template("otp.html")

    email = request.form.get("email")
    entered_otp = request.form.get("otp")

    User = db.session.query(database.User).filter_by(email=email).first()

    if not User:
        return render_template("otp.html", error="User not found.", email=email)

    # Expiry check (5 minutes)
    if User.otp_created_at and datetime.utcnow() > User.otp_created_at + timedelta(minutes=5):
        return render_template("otp.html", error="OTP expired. Please request a new one.", email=email)

    if User.otp_code == entered_otp:
        User.verified = True
        User.otp_code = None
        User.otp_created_at = None
        db.session.commit()
        return render_template("login.html", success="Account verified! You can now log in.")
    else:
        return render_template("otp.html", error="Invalid OTP. Please try again.", email=email)



def send_otp_email(user_email, otp_code):
    msg = MIMEText(f"Your OTP code is {otp_code}\n\nThis code will expire in 5 minutes.")
    msg["Subject"] = "OTP Verification"
    msg["From"] = config.smtp_email
    msg["To"] = user_email

    with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_email, config.smtp_password)
        server.send_message(msg)



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