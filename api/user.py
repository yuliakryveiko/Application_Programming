from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import *
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
        return StatusResponse("Bad username or password", 401)

    us = db.query(User).filter(User.username == user['username']).first()

    if us is None:
        return StatusResponse("Bad username or password",401)
   
    print(user['password'].encode('utf-8'),us.password.encode('utf-8'))
    if bcrypt.checkpw(user['password'].encode('utf-8'), us.password.encode('utf-8')): 
        return StatusResponse("Bad username or password",401)

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

    if username_r:
        return StatusResponse(code=400, response='The username is already taken')

    existsEmail = db.query(User).filter(User.email==user['email']).first()

    if existsEmail:

        return StatusResponse(code=400, response='The email is already registered')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    print(hashed_password)

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)

    db.add(new_user)   
    
    db.commit()

    a = db.query(User).filter(User.username == user['username']).first()

    return get_user(a.id)


@user.route('/<int:id>', methods=['PUT'])
def update_user(id):
    db = get_db()
    
    try:
        user = UserCreatingSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    
    username_r = db.query(User).filter(User.id == id).first()

    if username_r is None:
         return StatusResponse(code=404,response="No user with such id!")
    
    username_r = db.query(User).filter(User.username == user['username']).first()

    if username_r is not None and username_r.id != user['username']:
        return StatusResponse(code=400, response='The username is used by other user')

    existsEmail = db.query(User).filter(User.email==user['email']).first()

    if existsEmail is not None:
        if  existsEmail.id != user['username']:
            return StatusResponse(code=400, response='The email is used by other user')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    print(hashed_password)

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)


    username_r = db.query(User).filter(User.id == id).first()
    if username_r is None:
        print('aaaa')
        return '1',200
    username_r.email = new_user.email
    username_r.firstName = new_user.firstName
    username_r.lastName = new_user.lastName
    username_r.username = new_user.username
    username_r.password = new_user.password
    
    db.commit()

    a = db.query(User).filter(User.username == user['username']).first()

    return get_user(a.id)


@user.route('/<int:id>', methods=['GET'])
def get_user(id):
    db = get_db()
   
    username_r = db.query(User).filter(User.id == id).first()

    if username_r is None:
         return StatusResponse(code=404,response="No user with such id!")
    
    user = UserGetSchema().dump(username_r)

    return StatusResponse(response=user,code = 200)

@user.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    db = get_db()
   
    username_r = db.query(User).filter(User.id == id).first()

    if username_r is None:
         return StatusResponse(code=404,response="No user with such id!")
    
    username_r.username = 'DELETED'
    username_r.firstName = 'DELETED'
    username_r.email = 'DELETED'
    username_r.lastName = 'DELETED'
    username_r.wallet = 0

    return StatusResponse(response="User deleted!",code = 200)

@user.route('/replenish', methods=['PUT'])
@jwt_required()
def add_money():
    print('aaaa')
    current_user = get_jwt_identity()
    db = get_db()
    try:
        money = MoneySchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)
    
    user = db.query(User).filter(User.username == current_user).first()
    if user is None:
        return StatusResponse("No user with such username",400)
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
    if user is None:
        return StatusResponse("No user with such username",400)
    user.wallet -= float(money['amount'])
    db.commit()
    return StatusResponse(response="Money removed!",code = 200)