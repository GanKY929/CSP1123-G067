from app import app
from flask import Flask
from flask_sqlalchemy import flasksql
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

Database = flasksql(app, model_class = Base)
