from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, text, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from datetime import datetime
from werkzeug.security import check_password_hash as checkPasswordHash, generate_password_hash as generatePasswordHash
from db_setup import db, Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    verified: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    otp_code: Mapped[int] = mapped_column(String(6), nullable=True)
    otp_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
 
    tagged_post: Mapped[list["Post"]] = relationship(back_populates="post_author_info")
    user_comments: Mapped[list["Comments"]] = relationship(back_populates="comment_author_info")
    user_replies: Mapped[list["Replies"]] = relationship(back_populates="reply_author_info")

class Post(Base):
    __tablename__ = "posts"
    
    post_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_title: Mapped[str] = mapped_column(String(200), nullable=False)
    post_content: Mapped[str] = mapped_column(String, nullable=False)
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    
    post_author: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=True)
    post_author_info: Mapped["User"] = relationship(back_populates="tagged_post")

    post_comments: Mapped[list["Comments"]] = relationship(cascade="all, delete")

class Comments(Base):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_content: Mapped[str] = mapped_column(String, nullable=False)
    
    comment_author: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=True)
    comment_author_info: Mapped["User"] = relationship(back_populates="user_comments")

    comment_post_id: Mapped[int] = mapped_column(Integer, ForeignKey("posts.post_id"), nullable=True)

    replies: Mapped[list["Replies"]] = relationship(cascade="all, delete")

class Replies(Base):
    __tablename__ = "replies"

    reply_id:  Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reply_content: Mapped[str] = mapped_column(String, nullable=False)

    reply_author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)
    reply_author_info: Mapped["User"] = relationship(back_populates="user_replies")

    reply_comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.comment_id"), nullable=False)

def generatePassword(password):
    return generatePasswordHash(password)

def checkPassword(stored_password, password):
    return checkPasswordHash(stored_password, password)