from flask import Flask, render_template

app = Flask(__name__)
@app.route("/")
@app.route("/home")
@app.route("/index")
def index():
    return "<h1>Já jsem webovka s nadpisem</h1>"

@app.route("/datasets")
def datasets():
    return "<h1>Já jsem jiná webovka s nadpisem</h1><p>mám i odstavec</p>"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)