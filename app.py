from flask import Flask, render_template
from database import setup_app

app = setup_app()

@app.route("/")
def index():
    return render_template("index.html")