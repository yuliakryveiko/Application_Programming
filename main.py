from flask import Flask
from waitress import serve
from flask import jsonify
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from models import JWTToken
# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config["JWT_SECRET_KEY"] = "qwerty"  # Change this!
from db import get_db
jwt = JWTManager(app)   



from api import user,transaction
app.register_blueprint(transaction.transaction)
app.register_blueprint(user.user)


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool: #pragma no cover
    db = get_db()
    jti = jwt_payload["jti"]
    token = db.query(JWTToken).filter(JWTToken.id==jti).first()

    return token is not None

if __name__ == "__main__": #pragma no cover
    print("Started")
    
    app.run(debug=True,port = 8080)
    #serve(create_app(), host='127.0.0.1', port=8080)
