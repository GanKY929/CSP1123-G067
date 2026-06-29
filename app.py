from flask import Flask, render_template, request, redirect, url_for, session, abort
from sqlalchemy import select
from datetime import datetime, timedelta
from database import db
import database, config, random, os
import data_storage as dpn
import email_service
from db_setup import init_db

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

init_db(app)

# ─── Helpers ─────────────────────────────────────────────

def user_is_admin():
    return session.get("username") == "Mithirilz"

def get_user_by(email=None, username=None):
    if email:
        return db.session.query(database.User).filter_by(email=email).first()
    if username:
        return db.session.query(database.User).filter_by(username=username).first()

def create_otp(username, reset=False):
    db_user = get_user_by(username=username)
    if not db_user:
        raise ValueError("User not found")
    otp_code = str(random.randint(100000, 999999))
    db_user.otp_code = otp_code
    db_user.otp_created_at = datetime.utcnow()
    # Only mark unverified during signup flow, not during password reset
    if not reset:
        db_user.verified = False
    db.session.commit()
    return otp_code

def validate_password(password, confirm):
    if password != confirm:
        raise Exception("Passwords do not match.")
    if len(password) < 8:
        raise Exception("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        raise Exception("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        raise Exception("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        raise Exception("Password must contain at least one number.")


# ─── Index ───────────────────────────────────────────────

@app.route("/")
def index():
    if user_is_admin():
        return redirect(url_for("admin"))

    post_data = dpn.get_posts_details()

    return render_template("index.html", success=request.args.get("success"), posts=post_data)


# ─── Posts ───────────────────────────────────────────────

@app.route("/newpost")
def create_post_page():
    return render_template("newpost.html")


@app.route("/create_post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in"))

    title = request.form.get("post_title")
    content = request.form.get("post_content")

    if not title or not content:
        return redirect(url_for("create_post_page"))

    db.session.add(database.Post(
        post_title=title,
        post_content=content,
        image_path=request.form.get("post_image"),
        post_author=session["user_id"]
    ))
    db.session.commit()
    return redirect(url_for("create_post_page"))


@app.route("/post/postlayout")
def postlayout():
    post_id = request.args.get("post_id")
    post_details, comments = dpn.get_post_details(post_id)
    return render_template("postlayout.html", post=post_details, comments=comments, error=request.args.get("error"))


@app.route("/comment", methods=["POST"])
def add_comment():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in!"))

    post_id = request.args.get("post_id")
    content = request.form.get("comment_text")

    if not content:
        return redirect(url_for("postlayout", post_id=post_id, error="You didn't write anything for comment"))

    db.session.add(database.Comments(
        comment_content=content,
        comment_author=session["user_id"],
        comment_post_id=post_id
    ))
    db.session.commit()
    return redirect(url_for("postlayout", post_id=post_id))


@app.route("/reply", methods=["POST"])
def add_reply():
    if "user_id" not in session:
        return redirect(url_for("login", error="You are not logged in"))

    post_id = request.args.get("post_id")
    content = request.form.get("reply_text")

    if not content:
        return redirect(url_for("postlayout", post_id=post_id))

    db.session.add(database.Replies(
        reply_content=content,
        reply_author_id=session["user_id"],
        reply_comment_id=request.args.get("comment_id")
    ))
    db.session.commit()
    return redirect(url_for("postlayout", post_id=post_id))


@app.route("/remove_post", methods=["POST"])
def remove_post():
    post_id = request.args.get("post_id")
    if not post_id:
        return redirect(url_for("index"))

    post = db.session.get(database.Post, post_id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("index"))


# ─── Auth ────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=request.args.get("error"))

    username = request.form.get("username")
    password = request.form.get("password")

    try:
        db_user = get_user_by(username=username)
        if not db_user:
            raise Exception("Username does not exist.")
        if not database.checkPassword(db_user.password, password):
            raise Exception("Incorrect password.")
        if not db_user.verified:
            raise Exception("Account not verified. Please check your email for the OTP.")

        session.update({
            "username": db_user.username,
            "user_id": db_user.user_id,
            "email": db_user.email,
            "display_name": db_user.display_name
        })
        return redirect(url_for("index", success=f"Welcome {db_user.username}"))

    except Exception as e:
        return render_template("login.html", error=str(e), username=username)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index", success="Logged out successfully!"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    username = request.form.get("username")
    email    = request.form.get("email")
    password = request.form.get("password")
    confirm  = request.form.get("confirmPassword")

    try:
        if not all([username, email, password, confirm]):
            raise Exception("Must fill all fields.")
        if get_user_by(username=username):
            raise Exception("Username already exists.")
        if get_user_by(email=email):
            raise Exception("Email already exists.")
        validate_password(password, confirm)

        db.session.add(database.User(
            username=username,
            email=email,
            password=database.generatePassword(password),
            tagged_post=[]
        ))
        db.session.commit()

        otp_code = create_otp(username)
        email_service.send_otp(email, otp_code)
        return redirect(url_for("otp", email=email))

    except Exception as e:
        return render_template("signup.html", error=str(e))


@app.route("/otp", methods=["GET", "POST"])
def otp():
    email   = request.args.get("email") or request.form.get("email")
    purpose = request.args.get("purpose") or request.form.get("purpose", "verify")

    if not email:
        return redirect(url_for("login", error="Missing email."))

    db_user = get_user_by(email=email)
    if not db_user:
        return render_template("otp.html", error="User not found.", email=email)

    if db_user.verified and purpose == "verify":
        return redirect(url_for("login", success="Account already verified!"))

    if request.method == "GET":
        return render_template("otp.html", email=email, purpose=purpose)

    entered_otp = request.form.get("otp")
    if not entered_otp:
        return render_template("otp.html", error="Please enter an OTP.", email=email, purpose=purpose)

    if db_user.otp_created_at and datetime.utcnow() > db_user.otp_created_at + timedelta(minutes=5):
        return render_template("otp.html", error="OTP expired. Please request a new one.", email=email, purpose=purpose)

    if str(db_user.otp_code) != entered_otp:
        return render_template("otp.html", error="Invalid OTP. Please try again.", email=email, purpose=purpose)

    db_user.otp_code = None
    db_user.otp_created_at = None
    db_user.verified = True
    db.session.commit()

    if purpose == "reset":
        return redirect(url_for("resetPass", email=email))
    return redirect(url_for("login", success="Account verified! You can now log in."))


@app.route("/resend_otp", methods=["GET", "POST"])
def resend_otp():
    email = request.form.get("email") or request.args.get("email")
    if not email:
        return render_template("login.html", error="Missing email")

    db_user = get_user_by(email=email)
    if not db_user:
        return render_template("otp.html", error="User not found.", email=email)
    if db_user.verified:
        return redirect(url_for("login", success="Account already verified!"))

    email_service.send_otp(email, create_otp(db_user.username))
    return render_template("otp.html", success="OTP resent successfully.", email=email)


@app.route("/forgotPass", methods=["GET", "POST"])
def forgotPass():
    if request.method == "GET":
        return render_template("forgotPass.html")

    email = request.form.get("email")
    db_user = get_user_by(email=email)

    if not db_user:
        return render_template("forgotPass.html", error="No account found with that email.")

    # reset=True so we don't flip the user back to unverified
    email_service.send_otp(email, create_otp(db_user.username, reset=True))
    return redirect(url_for("otp", email=email, purpose="reset"))


@app.route("/resetPass", methods=["GET", "POST"])
def resetPass():
    email = request.args.get("email") or request.form.get("email")
    if not email:
        return redirect(url_for("forgotPass"))

    db_user = get_user_by(email=email)
    if not db_user:
        return render_template("forgotPass.html", error="User not found.")

    if request.method == "GET":
        return render_template("resetPass.html", email=email)

    password = request.form.get("new_password")
    confirm  = request.form.get("confirm_password")

    try:
        if not password or not confirm:
            raise Exception("Please fill all fields.")
        validate_password(password, confirm)
    except Exception as e:
        return render_template("resetPass.html", error=str(e), email=email)

    db_user.password = database.generatePassword(password)
    db.session.commit()
    return redirect(url_for("login", success="Password reset successfully! You can now log in."))


# ─── Admin ───────────────────────────────────────────────

@app.route("/admin")
def admin():
    if not user_is_admin():
        abort(404)

    users = db.session.execute(select(database.User).order_by(database.User.username)).scalars()
    user_list = [
        {
            "user_id": int(u.user_id),
            "email": str(u.email),
            "username": str(u.username),
            "verified": bool(u.verified)
        }
        for u in users
    ]
    gmail_users = [u for u in user_list if "gmail.com" in u["email"]]
    return render_template("Admin.html", users=user_list, gmail_users=gmail_users)


@app.route("/delete_user", methods=["POST"])
def delete_user():
    if not user_is_admin():
        abort(403)

    user = db.session.get(database.User, request.args.get("user_id"))
    if user:
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("admin"))


# ─── Profile ─────────────────────────────────────────────

@app.route("/profile", methods=["GET"])
def user_profile():
    if "user_id" not in session:
        return render_template("login.html", error="You are not logged in.")

    user_id = session["user_id"]
    db_user = db.session.query(database.User).filter_by(user_id=user_id).first()

    posts = []
    if db_user and db_user.tagged_post:
        posts = [
            {"post_title": p.post_title, "post_content": p.post_content, "post_id": p.post_id}
            for p in db_user.tagged_post
        ]

    return render_template(
        "profile.html",
        username=session["username"],
        email=session["email"],
        display_name=db_user.display_name if db_user else None,
        posts=posts
    )


@app.route("/edit_display_name", methods=["POST"])
def display_name():
    new_name = request.form.get("display_name")

    if db.session.query(database.User).filter_by(display_name=new_name).first():
        return render_template("profile.html", error="Name already exists", username=session["username"])

    db.session.query(database.User).filter_by(user_id=session["user_id"]).update({"display_name": new_name})
    db.session.commit()
    session["display_name"] = new_name
    return redirect(url_for("user_profile"))


# ─── Contact ─────────────────────────────────────────────

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "GET":
        return render_template(
            "contact.html",
            name=session.get("username"),
            email=session.get("email"),
            date=datetime.now().strftime('%Y-%m-%d')
        )

    username = request.form.get("name") or session.get("username")
    email    = request.form.get("email") or session.get("email")
    comment  = request.form.get("comment")
    date     = datetime.now()

    email_service.send_feedback(username, email, comment, date.strftime('%Y-%m-%d %H:%M:%S'))

    return render_template(
        "contact.html",
        success="Thanks for your comment <3",
        name=username,
        email=email,
        date=date.strftime('%Y-%m-%d')
    )


if __name__ == "__main__":
    app.run(debug=True)