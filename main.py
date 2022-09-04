import requests
from flask import Flask, request,render_template
from flask_frozen import Freezer


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

freezer = Freezer(app)
freezer.freeze()