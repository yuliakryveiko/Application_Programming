from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import *
from schemas import *
from models import *
from api.errors import StatusResponse

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/', methods=['POST'])
def add_user():
    db = get_db()

    try:
        user = UserCreatingSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    username_r = db.query(User).filter(User.username == user['username']).first()

    if username_r:
        return StatusResponse(code=400, response='The username is used by other user')

    existsEmail = db.query(User).filter(User.email==user['email']).first()

    if existsEmail:
        return StatusResponse(code=400, response='The email is used by other user')

    hashed_password = bcrypt.hashpw(user['password'].encode('utf-8'),salt = bcrypt.gensalt()).decode('utf-8')

    print(hashed_password)

    new_user = User(firstName=user['firstName'], lastName=user['lastName'], username=user['username'],
                     email=user['email'], password=hashed_password,wallet = 0)

    db.add(new_user)   
    

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