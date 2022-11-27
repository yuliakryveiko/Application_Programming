from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import *
from schemas import *
from models import *
from api.errors import StatusResponse
from datetime import datetime
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required,get_jwt
transaction = Blueprint('transaction', __name__, url_prefix='/transaction')


@transaction.route('/<int:id>', methods=['GET'])
def get_transaction_by_id(id):
    db = get_db()
   
    transaction_r = db.query(Transaction).filter(Transaction.id == id).first()

    if transaction_r is None:
         return StatusResponse(code=404,response="No transaction with such id!")
    
    trans = TransactionSchema().dump(transaction_r)

    return StatusResponse(response=trans,code = 200)

@transaction.route('/', methods=['POST'])
@jwt_required()
def add_transaction():
    db = get_db()

    try:
        trans = TransactionAddSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)



    b = db.query(User).filter(User.id == trans['sentByUser']).first()

    if b is None:
        return StatusResponse('Invalid sender ID!', 400)
    
    c = db.query(User).filter(User.id == trans['sentToUser']).first()

    if c is None:
        return StatusResponse('Invalid reciever ID!', 400)

    current_user = get_jwt_identity()
    if current_user != b.username:
        return StatusResponse('Sender ID does not match!', 401)

    if b.wallet < trans['value']:
        return StatusResponse('Not enough money on account',400)

    if trans['value'] < 0:
        return StatusResponse('Invalid value of transaction',400)

    time_now = datetime.now()

    trans = Transaction(value = trans['value'], datePerformed = time_now, sentByUser = trans['sentByUser'], sentToUser = trans['sentToUser'])
    

    c.wallet += float(trans.value)
    b.wallet -= float(trans.value)
    db.add(trans)
    db.commit()
    print(time_now.strftime("%Y-%m-%d %H:%M:%S"))
    t_r = db.query(Transaction).filter(Transaction.datePerformed == time_now.strftime("%Y-%m-%d %H:%M:%S")).first()
    return get_transaction_by_id(t_r.id)



@transaction.route('/sent/<int:id>', methods=['GET'])
def get_sent_by_user(id):
    db = get_db()

    transaction_r = db.query(Transaction).filter(Transaction.sentByUser == id).all()

    li = []

    for trans in transaction_r:
        li.append(TransactionSchema().dump(trans))

    return StatusResponse(response=li,code = 200)

@transaction.route('/sent/self', methods=['GET'])
def get_sent_by_user_self():
    db = get_db()
    current_user = get_jwt_identity()
    id = db.query(User).filter(User.username == current_user).first().id
    transaction_r = db.query(Transaction).filter(Transaction.sentByUser == id).all()

    li = []

    for trans in transaction_r:
        li.append(TransactionSchema().dump(trans))

    return StatusResponse(response=li,code = 200)

@transaction.route('/received/<int:id>', methods=['GET'])
def get_received_by_user(id):
    db = get_db()

    transaction_r = db.query(Transaction).filter(Transaction.sentToUser == id).all()

    li = []

    for trans in transaction_r:
        li.append(TransactionSchema().dump(trans))

    return StatusResponse(response=li,code = 200)

    
@transaction.route('/received/self', methods=['GET'])
def get_received_by_user_self():
    db = get_db()

    current_user = get_jwt_identity()
    id = db.query(User).filter(User.username == current_user).first().id
    transaction_r = db.query(Transaction).filter(Transaction.sentToUser == id).all()
    li = []

    for trans in transaction_r:
        li.append(TransactionSchema().dump(trans))

    return StatusResponse(response=li,code = 200)