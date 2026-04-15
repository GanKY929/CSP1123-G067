from app import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class User(db.Model):
    user_id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str] = mapped_column(unique = True)
    password: Mapped[str] = mapped_column(unique = True)
    email: Mapped[str]
    tagged_post: Mapped[str] 

class Post(db.Model):
    post_id: Mapped[int] = mapped_column(primary_key = True)
    post_title: Mapped[str]
    post_content: Mapped[str]
<<<<<<< HEAD
    post_owner: Mapped[int] = mapped_column(unique = True)
=======
    post_owner: Mapped[int] = mapped_column(unique = True)
>>>>>>> Amirul_Haqimi
