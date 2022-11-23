from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import *
from schemas import *
from models import *
from api.errors import StatusResponse
from datetime import datetime

transaction = Blueprint('transaction', __name__, url_prefix='/transaction')

@transaction.route('/<int:id>', methods=['GET'])
def get_transaction_by_id(id):
    db = get_db()
   
    transaction_r = db.query(Transaction).filter(Transaction.id == id).first()

    if transaction_r is None:
         return StatusResponse(code=404,response="No transaction with such id!")
    
    trans = TransactionSchema().dump(transaction_r)

    return StatusResponse(response=trans,code = 200)

#only for testing
@transaction.route('/', methods=['POST'])
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

    if b.wallet < trans['value']:
        return StatusResponse('Not enough money on account',400)

    if trans['value'] < 0:
        return StatusResponse('Invalid value of transaction',400)

    trans = Transaction(value = trans['value'], datePerformed = datetime.now(), sentByUser = trans['sentByUser'], sentToUser = trans['sentToUser'])
    

    c.wallet += float(trans.value)
    b.wallet -= float(trans.value)
    db.add(trans)
    db.commit()
    return StatusResponse('Transaction added',200)



@transaction.route('/sent/<int:id>', methods=['GET'])
def get_sent_by_user(id):
    db = get_db()

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