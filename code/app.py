from flask import Flask, render_template, jsonify,request, redirect, url_for, session
from redis import Redis
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
app = Flask(__name__)

# config
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


# connections
redis = Redis(host='redis', port=6379, decode_responses=True)
mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)

# collections
db = mongo_client['slevit']
codes_collection = db['codes']
users_collection = db['users']

@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    if(redis.exists("Cached:g")):
        data = redis.get("Cached:g")
        return render_template("index.html", message = data)
    else:
        redis.set("Cached:g", 'bagr', 10)
        return render_template("index.html", message = 'nemam')


@app.route("/trending")
def trending():
    listik = []
    redis.set("Cached:a",1, 6)
    redis.set("Cached:b",2, 6)
    redis.set("Cached:c",3, 6)
    for key in redis.scan_iter("Cached:*"):
        listik.append(key)
    return render_template("trending.html", pages = listik)


@app.route("/form")
def form():
    return render_template("form.html")


@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find({"email": email})
        
        if email == user['email'] and password == check_password_hash(user['password']):
            ...

    return render_template("login.html")


@app.route("/register", methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password = generate_password_hash(password)
                
        new_user = {
            "username": username,
            "email": email,
            "password_hash": password,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        users_collection.insert_one(new_user)
        session['username'] = username
        return redirect(url_for('index'))

    return render_template("register.html")  

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)