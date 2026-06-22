from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, text, Boolean, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import ForeignKey
from datetime import datetime
from werkzeug.security import check_password_hash as checkPasswordHash, generate_password_hash as generatePasswordHash

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tagged_post: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=True)

    verified: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    otp_code: Mapped[int] = mapped_column(String(6), nullable=True)
    otp_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class Post(Base):
    __tablename__ = "posts"
    
    post_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_title: Mapped[str] = mapped_column(String(200), nullable=False)
    post_content: Mapped[str] = mapped_column(String, nullable=False)
    image_path: Mapped[str] = mapped_column(String, nullable=True)
    post_owner: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"), nullable=False)


def generatePassword(password):
    return generatePasswordHash(password)

def checkPassword(stored_password, password):
    return checkPasswordHash(stored_password, password)