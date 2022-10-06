from flask import Flask
from waitress import serve

app = Flask(__name__)


@app.route("/api/v1/hello-world-11")
def home():
    return "Hello world 11"


if __name__ == "__main__":
    serve(app, host='127.0.0.1', port=8080)
