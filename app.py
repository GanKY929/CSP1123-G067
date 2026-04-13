from flask import Flask, render_template

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Database/project.db"

@app.route("/")
def index():
    return render_template("index.html")