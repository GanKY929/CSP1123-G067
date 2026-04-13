<<<<<<< HEAD
from app import app
from flask_sqlalchemy import flasksql
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

Database = flasksql(app, model_class = Base)
=======
from app import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key = True)
    username: Mapped[str] = mapped_column(unique = True)
    email: Mapped[str]

>>>>>>> b05141f (Completed initial database configuration)
