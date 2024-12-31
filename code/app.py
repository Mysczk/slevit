from flask import Flask, render_template, jsonify, request, redirect, url_for, session
import pymongo.errors
from redis import Redis
import pymongo
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
app = Flask(__name__)

# config
SECRET_KEY = 'tajnyklic'
app.config['SECRET_KEY'] = SECRET_KEY


# connections
redis = Redis(host='redis', port=6379, decode_responses=True)
mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)

admin = {
    "username": "admin",
    "email": "admin@admin.com",
    "password_hash": generate_password_hash("admin")
}

# collections
db = mongo_client['slevit']
codes_collection = db['codes']
users_collection = db['users']
users_collection.create_index([("email", pymongo.ASCENDING)], unique=True)
#users_collection.insert_one(admin)

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


@app.route("/form", methods=['GET','POST'])
def form():
    if request.method == "POST":
        email = session['email']
        vendor = request.form['vendor']
        code = request.form['code']
        expiration = request.form['expiration']

        new_code = {
            "email": email,
            "vendor": vendor,
            "code": code,
            "insert": date.now,
            "expiration": expiration
        }
        codes_collection.insert_one(new_code)
    else:
        return render_template("form.html")


@app.route("/login", methods=['GET','POST'])
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    else:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = users_collection.find_one({"email": email})
            if email == user['email'] and check_password_hash(user['password_hash'], password):
                session['email'] = email
                return redirect(url_for('index'))
            else:
                return render_template("login.html", message="Invalid email or password.")
    return render_template("login.html")

def logout():
    session.pop()

@app.route("/register", methods=['GET','POST'])
def register():
    if 'email' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password = generate_password_hash(password)

        if users_collection.find_one({"email": email}):
            return render_template("register.html", message="Email is already taken.")   

        new_user = {
            "username": username,
            "email": email,
            "password_hash": password,
            "created_at": date.now(),
            "updated_at": date.now()
        }
        try:
            users_collection.insert_one(new_user)
        except pymongo.errors.DuplicateKeyError:
            return render_template("register.html", message="Email is already taken.")
        
        session['email'] = email
        return redirect(url_for('index'))

    return render_template("register.html")  

def delete():
    email = session['email']
    users_collection.delete_one({"email": email})
    session.pop()
    return redirect(url_for('index'))

def deleteCode():
    email = session['email']
    code = request.form['code']
    codes_collection.delete_one({"email":email, "code":code})


@app.route("/profile", methods=['GET','POST'])
def profile():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    user = users_collection.find_one({"email": email})
    codes = codes_collection.find({"email": email})
    return render_template("profile.html", user=user, codes=codes)

@app.route("/changePwd/", methods=['POST'])
def updatePwd():
    email = session['email']
    password = request.form['password']
    password = generate_password_hash(password)
    users_collection.update_one({"email": email}, {"$set": {"password_hash": password}})
    return redirect(url_for('profile'))

@app.route("/changeUsNa/", methods=['POST'])
def updateUsNa():
    email = session['email']
    username = request.form['newusername']
    users_collection.update_one({"email": email}, {"$set": {"username": username}})
    return redirect(url_for('profile'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)