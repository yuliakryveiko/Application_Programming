from flask import Flask
from waitress import serve
app = Flask(__name__)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from db import db_init
    db_init()

    from api import user,transaction
    app.register_blueprint(transaction.transaction)
    app.register_blueprint(user.user)
    return app

if __name__ == "__main__":
    print("Started")
    app = create_app()
    app.run(debug=True,port = 8080)
    #serve(create_app(), host='127.0.0.1', port=8080)
