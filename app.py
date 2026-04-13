from flask import Flask, render_template
<<<<<<< HEAD

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database/project.db"
=======
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

app = Flask(__name__)
db = SQLAlchemy(model_class = Base)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

import database
with app.app_context():
    db.create_all()
>>>>>>> b05141f (Completed initial database configuration)

@app.route("/")
def index():
    return render_template("index.html")