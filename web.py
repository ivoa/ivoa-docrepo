from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return "<h3>This is the web.py file used for testing</h3>"



if __name__ == "__main__":
    app.run(debug=True)

