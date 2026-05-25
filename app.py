from flask import Flask, render_template, request, redirect, url_for
import random, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import database, config
from database import db
import data_storage as dpn #abbrev datapipeline

app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

app.config["SECRET_KEY"] = config.secret_key



with app.app_context():
    db.create_all()

def checkUsername(username):
    return database.User.query.filter_by(username=username).first()

def checkEmail(email):
    return database.User.query.filter_by(email=email).first()

#Sub-functions
def create_otp(username):
    otp_code = str(random.randint(100000, 999999))
    db_user = db.session.query(database.User).filter_by(username=username).first()

    if not db_user:
        raise ValueError("User not found")

    db_user.otp_code = otp_code
    db_user.otp_created_at = datetime.utcnow()
    db_user.verified = False

    db.session.commit()
    return otp_code


def send_otp_email(user_email, otp_code):
    msg = MIMEText(f"Your OTP code is {otp_code}\n\nThis code will expire in 5 minutes.")
    msg["Subject"] = f"MMUinfo; OTP Verification"
    msg["From"] = config.smtp_email
    msg["To"] = user_email

    with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_email, config.smtp_password)
        server.send_message(msg)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    existing_data = database.User.query.first()

    if not existing_data:
        raise Exception("There is no User in database yet.")

    username: str = request.form.get("username")
    password: str = request.form.get("password")

    if not db_user:
        raise Exception("Username does not exist.")
    if not database.checkPassword(db_user.password, password):
        raise Exception("Incorrect password.")
    if db_user.verified != True:
                raise Exception("Unverified of OTP")

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

        hashed_pw = database.generatePassword(password)

        new_user = database.User(
            username=username,
            email=email,
            password=hashed_pw,
            tagged_post="test",
        )
        db.session.add(new_user)
        db.session.commit()

        otp_code = create_otp(username)

        send_otp_email(email, otp_code)
        return render_template("otp.html", email=email)
    
    except Exception as error:
        return render_template("signup.html", error=str(error))




@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "GET":
        return render_template("otp.html")

    email = request.form.get("email")
    entered_otp = request.form.get("otp")

    db_user = db.session.query(database.User).filter_by(email=email).first()

    if not db_user:
        return render_template("signup.html", error="User not found. SignUp Unsuccessful, Try again.", email=email)

    # Expiry check
    if db_user.otp_created_at and datetime.utcnow() > db_user.otp_created_at + timedelta(minutes=5):
        return render_template("otp.html", error="OTP expired. Please request a new one.", email=email)

    if str(db_user.otp_code) == entered_otp:
        db_user.verified = True
        db_user.otp_code = None
        db_user.otp_created_at = None
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

@app.route("/resend_otp", methods=["POST"])
def resend_otp():
    email = request.form.get("email")
    db_user = db.session.query(database.User).filter_by(email=email).first()
    otp_code = create_otp(db_user.username)
    send_otp_email(user_email=email, otp_code=otp_code)
    return render_template("otp.html", email=email)

@app.route("/forgotPass", methods=["GET", "POST"])
def forgotPass():
    if request.method == "POST":
        email = request.form.get("email")
        db_user = db.session.query(database.User).filter_by(email=email).first()
        password = db_user.password
        msg = MIMEText(f"Your password is {password}.")
        msg["Subject"] = f"MMUinfo; Forgot Password"
        msg["From"] = config.smtp_email
        msg["To"] = email

        with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
            server.starttls()
            server.login(config.smtp_email, config.smtp_password)
            server.send_message(msg)
        
        return render_template("login.html")
    return render_template("forgotPass.html")

@app.route("/profile")
def user_profile():
    USER_ID = 1 #Temporary User_ID for testing

    _username, _email, _tagged_post = dpn.get_user_details(USER_ID)

    return render_template(
        "profile.html",
        username = _username,
        email = _email,
        tagged_post = _tagged_post
    )

@app.route("/contact")
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug=True)