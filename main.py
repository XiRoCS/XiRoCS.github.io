import requests
from flask import Flask, request,render_template


app = Flask(__name__)

@app.route('/')
def home():
    query = request.url
    with open ('url.txt', 'w') as file:
        file.write(query)
    return render_template('index.html')

app.run()
