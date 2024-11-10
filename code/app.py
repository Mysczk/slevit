from flask import Flask, render_template, jsonify
from redis import Redis

redis = Redis(host='redis',port=6379,decode_responses=True)

app = Flask(__name__)
@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    if(redis.exists("g")):
        data = redis.get("Cached:g")
        return render_template("index.html", message=data)
    else:
        redis.set("Cached:g", 'bagr', 10)
        return render_template("index.html", message="neexistuje")


@app.route("/trending")
def trending():
    listik = []
    redis.set("Cached:a",1, 6)
    redis.set("Cached:b",2, 6)
    redis.set("Cached:c",3, 6)
    for key in redis.scan_iter("Cache:*"):
        listik.append(key)
    return render_template("trending.html", pages = listik)

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")  
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)