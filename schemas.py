from marshmallow import Schema, fields, base

class UserCreatingSchema(Schema):
    username = fields.String(required=True)
    email = fields.String(required=True)
    password = fields.String(required=True)
    firstName = fields.String(required=True) 
    lastName = fields.String(required=True)

class UserGetSchema(Schema):
    userId = fields.Integer()
    username = fields.String()
    email = fields.String()
    firstName = fields.String() 
    lastName = fields.String()
    wallet = fields.Decimal() 

class TransactionSchema(Schema):
    id = fields.Integer()
    value = fields.Decimal()
    datePerformed = fields.DateTime()
    sentByUser = fields.Integer()
    sentToUser = fields.Integer()
    
