from app import db
from sqlalchemy import Integer, String, text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from werkzeug.security import check_password_hash as checkPasswordHash, generate_password_hash as generatePasswordHash
from app import Base
class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    tagged_post: Mapped[int] = mapped_column(Integer, server_default=text("0"), nullable=True)

    verified: Mapped[bool] = mapped_column(Boolean, server_default="0", nullable=False)
    otp_code: Mapped[int] = mapped_column(Integer, nullable=True)
    otp_created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

class post(db.Model):
    post_id: Mapped[int] = mapped_column(primary_key = True)
    post_title: Mapped[str]
    post_content: Mapped[str]
    post_owner: Mapped[int] = mapped_column(unique = True)

def generatePassword(password):
    return generatePasswordHash(password)

def checkPassword(stored_password, password):
    return checkPasswordHash(stored_password, password)