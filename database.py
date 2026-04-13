from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = None

class Base(DeclarativeBase):
    pass

def setup_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database/project.db"
    db = SQLAlchemy(app, model_class = Base)
    db.init_app(app)
    
    return app
