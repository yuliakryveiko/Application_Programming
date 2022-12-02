from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import get_db
from schemas import *
from models import *
from api.errors import StatusResponse
import datetime 

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required,get_jwt

user = Blueprint('user', __name__, url_prefix='/user')



@user.route("/login", methods=["POST"])
def login():
    db = get_db()
    try:
        user = UserLogin().load(request.get_json())
    except ValidationError as err:
        return StatusResponse("Bad schema", 401)

    us = db.query(User).filter(User.username == user['username']).first()

    if us is None:
        return StatusResponse("Bad username",401)
   
    if bcrypt.checkpw(user['password'].encode('utf-8'), us.password.encode('utf-8')) is False: 
        return StatusResponse("Bad password",401)

    access_token = create_access_token(identity=user['username'])
    return jsonify(access_token=access_token)

@user.route("/logout", methods=["DELETE"])
@jwt_required()
def logout_user():
    db = get_db()
    jti = get_jwt()["jti"]
    db.add(JWTToken(id=jti))
    db.commit()
    return jsonify(msg="JWT revoked")

@user.route('/', methods=['POST'])
def add_user():
    db = get_db()
    
    try:
        user = UserCreatingSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    username_r = db.query(User).filter(User.username == user['username']).first()

    if username_r is not None:
        return StatusResponse(code=400, response='The username is already taken')

   
    existsEmail = db.query(User).filter(User.email==user['email']).first()

    if existsEmail is not None:
        return StatusResponse(code=400, response='The email is already registered')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)

    db.add(new_user)   
    
    db.commit()

    a = db.query(User).filter(User.username == user['username']).first()

    return get_user(a.username)

@user.route('/<usernam>', methods=['PUT'])
@jwt_required()
def update_user(usernam):
    db = get_db()
   
   
    try:
        user = UserCreatingSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    current_user = get_jwt_identity()
    
    username_r = db.query(User).filter_by(username=usernam).first()
    

    if username_r is None:
         return StatusResponse(code=404,response="No user with such qweer!")
    if not (current_user == username_r.username or db.query(Admin).filter(Admin.username == current_user).first() is not None):
        return StatusResponse(code=401,response="No rights or access!")
    
    username_r = db.query(User).filter(User.username == user['username']).first()

    if username_r is not None and username_r.username != current_user:
        return StatusResponse(code=400, response='The username is used by other user')

    existsEmail = db.query(User).filter(User.email==user['email']).first()
    if existsEmail is not None:
        if  existsEmail.username != current_user:
            return StatusResponse(code=400, response='The email is used by other user')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)

    username_r = db.query(User).filter(User.username == usernam).first()

    username_r.email = new_user.email
    username_r.firstName = new_user.firstName
    username_r.lastName = new_user.lastName
    username_r.username = new_user.username
    username_r.password = new_user.password
    
    db.commit()

    a = db.query(User).filter(User.username == user['username']).first()

    return get_user(a.username)

@user.route('/self', methods=['PUT'])
@jwt_required()
def update_user_self():
    db = get_db()
   
   
    try:
        user = UserCreatingSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    current_user = get_jwt_identity()
    
    username_r = db.query(User).filter_by(username=current_user).first()
    
    username_r = db.query(User).filter(User.username == user['username']).first()

    if username_r is not None and username_r.username != current_user:
        return StatusResponse(code=400, response='The username is used by other user')

    existsEmail = db.query(User).filter(User.email==user['email']).first()
    if existsEmail is not None:
        if  existsEmail.username != current_user:
            return StatusResponse(code=400, response='The email is used by other user')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)

    username_r = db.query(User).filter(User.username == current_user).first()

    username_r.email = new_user.email
    username_r.firstName = new_user.firstName
    username_r.lastName = new_user.lastName
    username_r.username = new_user.username
    username_r.password = new_user.password
    
    db.commit()

    a = db.query(User).filter(User.username == user['username']).first()

    return get_user(a.username)


@user.route('/<usernam>', methods=['GET'])
def get_user(usernam):
    db = get_db()
   
    username_r = db.query(User).filter_by(username=usernam).first()
   
    if username_r is None:
         return StatusResponse(code=404,response="No user with such username!")
    
    user = UserGetSchema().dump(username_r)

    return StatusResponse(response=user,code = 200)

@user.route('/self', methods=['GET'])
@jwt_required()
def get_user_self():
    db = get_db()

    current_user = get_jwt_identity()    
    username_r = db.query(User).filter(User.username == current_user).first()

    user = UserGetSchema().dump(username_r)

    return StatusResponse(response=user,code = 200)

@user.route('/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    db = get_db()
    current_user = get_jwt_identity()     
    
    username_r = db.query(User).filter(User.username == username).first()

    if username_r is None:
        return StatusResponse(code=404,response="No user with such username!")
   
    if not (current_user == username_r.username or db.query(Admin).filter(Admin.username == current_user).first() is not None):
        return StatusResponse(code=401,response="No rights or access!")

    
    username_r.username = 'DELETED'
    username_r.firstName = 'DELETED'
    username_r.email = 'DELETED'
    username_r.lastName = 'DELETED'
    username_r.wallet = 0
    db.commit()
    return StatusResponse(response="User deleted!",code = 200)

@user.route('/self', methods=['DELETE'])
@jwt_required()
def delete_user_self():
    db = get_db()
    current_user = get_jwt_identity()     
    
    username_r = db.query(User).filter(User.username == current_user).first()
    
    username_r.username = 'DELETED'
    username_r.firstName = 'DELETED'
    username_r.email = 'DELETED'
    username_r.lastName = 'DELETED'
    username_r.wallet = 0
    db.commit()
    return StatusResponse(response="User deleted!",code = 200)

@user.route('/replenish', methods=['PUT'])
@jwt_required()
def add_money():
    current_user = get_jwt_identity()
    db = get_db()
    try:
        money = MoneySchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)
    
    user = db.query(User).filter(User.username == current_user).first()

    user.wallet += float(money['amount'])
    db.commit()
    return StatusResponse(response="Money added!",code = 200)

@user.route('/withdraw', methods=['PUT'])
@jwt_required()
def remove_money():
    current_user = get_jwt_identity()
    db = get_db()
    try:
        money = MoneySchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)
    
    user = db.query(User).filter(User.username == current_user).first()
    if user.wallet < float(money['amount']):
        return StatusResponse(response="Not enough money!",code = 400)
    user.wallet -= float(money['amount'])
    db.commit()
    return StatusResponse(response="Money removed!",code = 200)