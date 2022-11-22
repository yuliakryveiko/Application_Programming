from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from sqlalchemy import desc
import bcrypt
from db import *
from schemas import *
from models import *
from api.errors import StatusResponse

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
        trans = TransactionSchema().load(request.get_json())
    except ValidationError as err:
        return StatusResponse(err.messages, 400)

    a = db.query(Transaction).filter(Transaction.id == trans['id']).first()
    if a is not None:
        return StatusResponse('Transaction ID taken!', 400)
    
    trans = Transaction(id = trans['id'],value = trans['value'],datePerformed = trans['datePerformed'],sentByUser = trans['sentByUser'], sentToUser = trans['sentToUser'])

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