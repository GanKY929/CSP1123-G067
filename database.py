from app import db
from sqlalchemy import Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import check_password_hash

class User(db.Model):
    user_id: Mapped[int] = mapped_column(Integer, primary_key = True)
    username: Mapped[str] = mapped_column(unique = True)
    password: Mapped[str]
    email: Mapped[str]
    tagged_post: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=True)

class Post(db.Model):
    post_id: Mapped[int] = mapped_column(primary_key = True)
    post_title: Mapped[str]
    post_content: Mapped[str]
    post_owner: Mapped[int] = mapped_column(unique = True)

def check_password(stored_password, password):
    return check_password_hash(stored_password, password)