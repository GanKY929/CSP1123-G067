import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)



def init_db(app):
    db_url = os.environ.get("DATABASE_URL") or "sqlite:///project.db"

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

    # Ensure sslmode=require is in the URI for Postgres
    if db_url.startswith("postgresql+psycopg2://") and "sslmode" not in db_url:
        db_url += "?sslmode=require"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
        "pool_size": 5,
        "max_overflow": 2,
    }

    db.init_app(app)

    with app.app_context():
        db.create_all()
