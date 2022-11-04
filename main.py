from flask import Flask
from waitress import serve
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Date, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from database_info import DB_URL
from sqlalchemy import sql

app = Flask(__name__)


@app.route("/api/v1/hello-world-11")
def home():
    return "Hello world 11"


if __name__ == "__main__":
    print("Started")
    serve(app, host='127.0.0.1', port=8080)
