from flask import Flask, render_template, request, redirect, url_for, session
import random, smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import database, config
from urllib.parse import urlparse
from database import db
import data_storage as dpn #abbrev datapipeline

app = Flask(__name__)
app.config["SECRET_KEY"] = config.secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

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
    success = request.args.get("success")
    return render_template("index.html", success=success)

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
            if not database.checkPassword(db_user.password, password):
                raise Exception("Incorrect password.")
            if db_user.verified != True:
                raise Exception("Account not verified. Please check your email for the OTP.")

            session["username"] = db_user.username
            session["user_id"] = db_user.user_id 
            return redirect(url_for("index"))

        except Exception as error:
            return render_template("login.html", error=str(error), username=username)


@app.route("/logout")
def logout():
    session.pop("username")
    session.pop("user_id")
    success = "Logged out successfully!"
    return redirect(url_for("index", success=success))


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
        return redirect(url_for("otp", email=email))
    
    except Exception as error:
        return render_template("signup.html", error=str(error))




@app.route("/otp", methods=["GET", "POST"])
def otp():
    email = request.args.get("email") or request.form.get("email")
    purpose = request.args.get("purpose") or request.form.get("purpose", "verify")
    entered_otp = request.form.get("otp")
    db_user = db.session.query(database.User).filter_by(email=email).first()

    if not email:
        return redirect(url_for("login", error="Missing email."))

    if not db_user:
        return render_template("otp.html", error="User not found.", email=email)

    if db_user.verified and purpose == "verify":
        return redirect(url_for("login", success="Account already verified!"))

    if request.method == "GET":
        return render_template("otp.html", email=email, purpose=purpose)

    if not entered_otp:
        return render_template("otp.html", error="Please enter an OTP.", email=email, purpose=purpose)

    if db_user.otp_created_at and datetime.utcnow() > db_user.otp_created_at + timedelta(minutes=5):
        return render_template("otp.html", error="OTP expired. Please request a new one.", email=email, purpose=purpose)

    if str(db_user.otp_code) == entered_otp:
        db_user.otp_code = None
        db_user.otp_created_at = None
        db_user.verified = True

        if purpose == "reset":
            db.session.commit()
            return redirect(url_for("resetPass", email=email))
        else:
            db_user.verified = True
            db.session.commit()
            return redirect(url_for("login", success="Account verified successfully! You can now log in."))
    else:
        return render_template("otp.html", error="Invalid OTP. Please try again.", email=email, purpose=purpose)


@app.route("/resend_otp", methods=["GET", "POST"])
def resend_otp():
    email = request.form.get("email") or request.args.get("email")
    if not email:
        return render_template("login.html", error="Missing email")

    db_user = db.session.query(database.User).filter_by(email=email).first()
    if not db_user:
        return render_template("otp.html", error="User not found.", email=email)

    if db_user.verified:
        return redirect(url_for("login", success="Account already verified!"))

    otp_code = create_otp(db_user.username)
    send_otp_email(user_email=email, otp_code=otp_code)
    return render_template("otp.html", success="OTP resent successfully.", email=email)



@app.route("/forgotPass", methods=["GET", "POST"])
def forgotPass():
    if request.method == "GET":
        return render_template("forgotPass.html")

    email = request.form.get("email")
    db_user = db.session.query(database.User).filter_by(email=email).first()

    if not db_user:
        return render_template("forgotPass.html", error="No account found with that email.")

    otp_code = create_otp(db_user.username)
    send_otp_email(email, otp_code)

    return redirect(url_for("otp", email=email, purpose="reset"))




@app.route("/resetPass", methods=["GET", "POST"])
def resetPass():
    email = request.args.get("email") or request.form.get("email")
    if not email:
        return redirect(url_for("forgotPass"))

    db_user = db.session.query(database.User).filter_by(email=email).first()
    if not db_user:
        return render_template("forgotPass.html", error="User not found.")

    if request.method == "GET":
        return render_template("resetPass.html", email=email)

    password = request.form.get("new_password")
    confirmPassword = request.form.get("confirm_password")

    if not password or not confirmPassword:
        return render_template("resetPass.html", error="Please fill all fields.", email=email)
    if password != confirmPassword:
        return render_template("resetPass.html", error="Passwords do not match.", email=email)
    if len(password) < 8:
        return render_template("resetPass.html", error="Password must be at least 8 characters.", email=email)

    db_user.password = database.generatePassword(password)
    db.session.commit()

    return redirect(url_for("login", success="Password reset successfully! You can now log in."))


@app.route("/profile")
def user_profile():
    try:
        if "user_id" not in session:
            raise Exception("You are not logged in.")    
    except Exception as error:
        return render_template("login.html", error=str(error))

    USER_ID = session["user_id"]
    _username, _email, _tagged_post = dpn.get_user_details(USER_ID)

    return render_template(
        "profile.html",
        username = _username,
        email = _email,
        tagged_post = _tagged_post
    )

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        username = request.args.get("username")
        date = datetime.now().strftime("%Y-%m-%d")
        email = request.args.get("email")
        return render_template("contact.html", name=username, email=email, date=date)
    
    date = datetime.now()
    username = request.form.get("name")
    email = request.form.get("email")
    comment = request.form.get("comment")

    msg = MIMEText(f"Username:{username}\n\n{comment}")
    msg["Subject"] = f"User Feedback : {date}"
    msg["From"] = email
    msg["To"] = config.smtp_email

    with smtplib.SMTP(config.smtp_server, config.smtp_port) as server:
        server.starttls()
        server.login(config.smtp_email, config.smtp_password)
        server.send_message(msg)
    success="Thanks for your comment <3"
    return render_template("contact.html", success=success)

if __name__ == "__main__":
    app.run(debug=True)