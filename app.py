from flask import Flask, render_template, request, redirect, url_for, session, abort 
from sqlalchemy import select
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from urllib.parse import urlparse
from database import db
from copy import error
import database, config, random, threading, requests, os
import data_storage as dpn
from db_setup import init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-secret")

init_db(app)

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
    subject = "MMUinfo; OTP Verification"
    body = f"Your OTP code is {otp_code}\n\nThis code will expire in 5 minutes."
    send_email_async(user_email, config.official_email, subject, body)

def send_email_async(recipient, sender, subject, body):
    def send_email():
        try:
            response = requests.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": config.EMAIL_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "sender": {
                        "name": "MMU InfoHUB",
                        "email": sender
                    },
                    "to": [
                        {"email": recipient}
                    ],
                    "subject": subject,
                    "textContent": body
                }
            )
            print("Email sent:", response.status_code)
        except Exception as e:
            print("Failed to send email:", e)

    threading.Thread(target=send_email).start()
@app.route("/")
def index(): 
    success = request.args.get("success")
    post_data = []

    if ("username" in session) and (session["username"] == "Mithirilz"):
        return redirect(url_for("admin"))

    post_count = db.session.query(database.Post).count() 

    if post_count != 0:
        first_post_id = 1 
        last_post_id = post_count

        post_data = dpn.get_posts_details(first_post_id, last_post_id)

    return render_template("index.html", success=success, posts=post_data)


@app.route("/newpost")
def create_post_page():
    _success = request.args.get("success")
    _error = request.args.get("error")
    
    return render_template("newpost.html", success = _success)


@app.route("/create_post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in"))

    _post_title = request.form.get("post_title")
    _post_content = request.form.get("post_content")
    _image_path = request.form.get("post_image")
    _post_author_id = session["user_id"]

    if _post_title == None or _post_content == None or _post_author_id == None:
        print("Invalid post inputs") 
        return redirect(url_for("create_post_page", error="Your post inputs were not valid"))
 
    new_post = database.Post(
        post_title = _post_title,
        post_content = _post_content,
        image_path = _image_path,
        post_author = _post_author_id
    ) 

    db.session.add(new_post)
    db.session.commit()

    return redirect(url_for("create_post_page", success="You have successfully created a post"))


@app.route("/post/postlayout")
def postlayout():
    _post_id = request.args.get("post_id")
    _error = request.args.get("error")

    _post_details, _comments = dpn.get_post_details(_post_id)

    return render_template("postlayout.html", post=_post_details, comments=_comments, error=_error)
    

@app.route("/comment", methods = ["POST"])
def add_comment():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in!"))

    _post_id = request.args.get("post_id")
    _user_id = session["user_id"]
    _comment_content = request.form.get("comment_text")

    if not _comment_content:
        return redirect(url_for("postlayout", post_id = _post_id, error="You didn't write anything for comment"))

    new_comment = database.Comments(
        comment_content = _comment_content,
        comment_author = _user_id,
        comment_post_id = _post_id
    )

    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for("postlayout", post_id = _post_id))


@app.route("/reply", methods=["POST"])
def add_reply():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in"))

    _reply_content = request.form.get("reply_text")
    _comment_id = request.args.get("comment_id")
    _post_id = request.args.get("post_id")
    _user_id = session["user_id"] 

    if _reply_content == None:
        print("No content in reply")
        return redirect(url_for("postlayout", post_id = _post_id))

    new_reply = database.Replies(
        reply_content = _reply_content,
        reply_author_id = _user_id,
        reply_comment_id = _comment_id 
    )

    db.session.add(new_reply)
    db.session.commit()

    return redirect(url_for("postlayout", post_id = _post_id))


@app.route("/remove_post", methods=["POST"])
def remove_post():
    _post_id = request.args.get("post_id")

    if _post_id == None:
        print("Post ID does not exist")
        return redirect(url_for("index"))

    post_to_delete = db.session.get(database.Post, _post_id)
    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        _error = request.args.get("error")
        return render_template("login.html", error=_error)

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
                raise Exception("Account not verified. Please check your email for the OTP. Click Forgot Password to proceed.")

            session["username"] = db_user.username
            session["user_id"] = db_user.user_id 
            session["email"] = db_user.email
            session["display_name"] = db_user.display_name
            
            return redirect(url_for("index", success=f"Welcome {db_user.username}"))

        except Exception as error:
            return render_template("login.html", error=str(error), username=username)


@app.route("/logout")
def logout():
    session.clear()
    success = "Logged out successfully!"
    return redirect(url_for("index", success=success))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    
    username: str = request.form.get("username")
    email: str = request.form.get("email")
    password: str = request.form.get("password")
    confirmPassword: str = request.form.get("confirmPassword")

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
        if not any(char.isupper() for char in password):
            raise Exception("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise Exception("Password must contain at least one lowercase letter.")
        if not any(char.isdigit() for char in password):
            raise Exception("Password must contain at least one number.")

        hashed_pw = database.generatePassword(password)

        new_user = database.User(
            username=username,
            email=email,
            password=hashed_pw,
            tagged_post=[]  ,
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
    email: str = request.args.get("email") or request.form.get("email")
    purpose: str = request.args.get("purpose") or request.form.get("purpose", "verify")
    entered_otp: str = request.form.get("otp")
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
    email: str = request.form.get("email") or request.args.get("email")
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

    email: str = request.form.get("email")
    db_user = db.session.query(database.User).filter_by(email=email).first()

    if not db_user:
        return render_template("forgotPass.html", error="No account found with that email.")

    otp_code = create_otp(db_user.username)
    send_otp_email(email, otp_code)

    return redirect(url_for("otp", email=email, purpose="reset"))


@app.route("/resetPass", methods=["GET", "POST"])
def resetPass():
    email: str = request.args.get("email") or request.form.get("email")
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


@app.route("/admin")
def admin(): 
    if not user_is_admin():
        abort(404)

    user_list = []
    _gmail_users = []

    users = db.session.execute(select(database.User).order_by(database.User.username)).scalars()

    for _user in users:
        user_dict = {
            "user_id" : int(_user.user_id),
            "email" : str(_user.email),
            "username" : str(_user.username),
            "verified" : bool(_user.verified)
        }

        if str(_user.email).find("@gmail.com"):
            _gmail_users.append(user_dict)
        
        else:
            user_list.append(user_dict)
        
    return render_template("Admin.html", users = _gmail_users)


@app.route("/delete_user", methods = ["POST"])
def delete_user():
    if not user_is_admin():
        return redirect("index", success = "You're not an admin.")

    _user_id = request.args.get("user_id")

    user_to_delete = db.session.get(database.User, _user_id)
    db.session.delete(user_to_delete) 
    db.session.commit()

    return redirect(url_for("admin"))    


def user_is_admin() -> bool:
    if ("username" in session) and (session["username"] == "Mithirilz"):
        return True
    
    return False


@app.route("/profile", methods=["GET"])
def user_profile():
    try:
        if "user_id" not in session:
            raise Exception("You are not logged in.")    

    except Exception as error:
        return redirect(url_for("login", error="You're not logged in"))


    _username = session["username"]
    _email = session["email"]
    _user_id = session["user_id"]
    _display_name = db.session.query(database.User).filter_by(user_id=_user_id).first().display_name
    _tagged_post = db.session.scalar(select(database.User)
                                    .join(database.User.tagged_post)
                                    .where(database.User.user_id == _user_id))

    _posts = []

    if _tagged_post:
        for post_info in _tagged_post.tagged_post:
            post_dict = {
                "post_title" : post_info.post_title,
                "post_content" : post_info.post_content,
                "post_id" : post_info.post_id
            }
        
            _posts.append(post_dict)

    return render_template(
        "profile.html",
        username=_username,
        email=_email,
        display_name=_display_name,
        posts = _posts
    )


@app.route("/edit_display_name", methods=["GET", "POST"])
def display_name():
    if request.method == "GET":
        return redirect(url_for("profile"))
    display_name: str = request.form.get("display_name")
    try:
        if db.session.query(database.User).filter_by(display_name=display_name).first():
            raise Exception("Name already exists")
    
    except Exception as error:
        return render_template("profile.html", error=str(error), username=session["username"])
    
    db.session.query(database.User).filter_by(user_id=session["user_id"]).update({"display_name": display_name})
    db.session.commit()
    session["display_name"] = display_name
    return redirect(url_for("user_profile", success="Name updated successfully!"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template(
        "contact.html",
        name=session.get("username"),
        date=datetime.now().strftime('%Y-%m-%d'),
        email=session.get("email")
    )

    date = datetime.now()
    username = request.form.get("name") or session.get("username")
    email = request.form.get("email") or session.get("email")
    comment = request.form.get("comment")

    send_email_async(
        recipient=config.official_email,
        sender=config.official_email,
        subject=f"User Feedback : {date.strftime('%Y-%m-%d %H:%M:%S')}", 
        body=f"Username: {username}\nEmail: {email}\n\n{comment}"
        )

    success = "Thanks for your comment <3"
    return render_template("contact.html", success=success, name=username, date=datetime.now().strftime('%Y-%m-%d'), email=email)


if __name__ == "__main__":
    app.run(debug=True)