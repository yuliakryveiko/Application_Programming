from flask_testing import TestCase
from api.errors import *
from models import Transaction,JWTToken,User
from db import get_db_test
from api.transaction import get_transaction_by_id,get_sent_by_user,get_received_by_user
from main import app
import requests
import json
from flask import Flask
from flask_jwt_extended import JWTManager

def delete_user_if_present(id):#pragma no cover
    db = get_db_test()
    res = db.query(User).filter(User.username == id).first()
    if res is not None:
        if db.query(Transaction).filter(Transaction.sentByUser == res.id).first() is not None:
            db.query(Transaction).filter(Transaction.sentByUser == res.id).delete()
        if db.query(Transaction).filter(Transaction.sentToUser == res.id).first() is not None:
            db.query(Transaction).filter(Transaction.sentToUser == res.id).delete()
        db.query(User).filter(User.username == id).delete()
        db.commit()
    if db.query(User).filter(User.username == "DELETED").first() is not None:
        db.query(User).filter(User.username == "DELETED").delete()
        db.commit()

class MyTest(TestCase):

    TESTING = True

    def create_app(self):
        from api import transaction,user
        app = Flask(__name__)
        app.config["JWT_SECRET_KEY"] = "qwerty"  # Change this!
        jwt = JWTManager(app)   
        @jwt.token_in_blocklist_loader
        def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
            db = get_db_test()
            jti = jwt_payload["jti"]
            token = db.query(JWTToken).filter(JWTToken.id==jti).first()

            return token is not None

        app.register_blueprint(transaction.transaction)
        app.register_blueprint(user.user)
        app.config['TESTING'] = True
        return app

    def get_auth(self,username = "user1", password = "qwerty"):
        b = {
            "username": username,
            "password": password,
        }
        x = self.client.post('user/login',json=b)
        if x.status_code == 200:
            return {"Authorization":"Bearer "+json.loads(x.text)["access_token"]}
        else:
            #print(x.text)
            return -1
    
    def test_login(self):
        a = self.get_auth('user1','qwerty')
        self.assertNotEqual(a,-1)

    def test_login_bad_password(self):
        a = self.get_auth('user1','qwertyewr')
        self.assertEqual(a,-1)
    
    def test_login_revoked(self):
        a = self.get_auth('user1','qwerty')
        x = self.client.delete('user/logout',headers = a)
        x = self.client.put('user/replenish',headers = a)
        self.assert401(x)

    def test_get_transaction(self):
        a = self.client.get('transaction/1')
        self.assertEqual(a.status_code,200)

    def test_get_transaction_bad_id(self):
        a = self.client.get('transaction/4324334')
        self.assertEqual(a.status_code,404)

    def test_get_transaction_sent_by(self):
        a = self.client.get('transaction/sent/user1')
        self.assertEqual(a.status_code,200)

    def test_get_transaction_sent_by_self(self):
        a = self.client.get('transaction/sent/self',headers = self.get_auth('user1','qwerty'))
        self.assertEqual(a.status_code,200)
    
    def test_get_transaction_sent_by_bad_user(self):
        a = self.client.get('transaction/sent/user234')
        self.assertEqual(a.status_code,404)

    def test_get_transaction_recieved_by(self):
        a = self.client.get('transaction/received/user1')
        self.assertEqual(a.status_code,200)
    
    def test_get_transaction_recieved_by_self(self):
        a = self.client.get('transaction/received/self',headers = self.get_auth('user1','qwerty'))
        self.assertEqual(a.status_code,200)
    
    def test_get_transaction_recieved_by_bad_user(self):
        a = self.client.get('transaction/received/user234')
        self.assertEqual(a.status_code,404)
    
    def test_add_transaction(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": id1,
            "sentToUser": id2,
            "value": 5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
       
        self.assertEqual(response.status_code, 200)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 

    def test_add_transaction_bad_user(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": 1,
            "sentToUser": id2,
            "value": 5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 401)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 

    def test_add_transaction_bad_us1(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": 12321321412,
            "sentToUser": id2,
            "value": 5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 400)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 

    def test_add_transaction_bad_us2(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": id1,
            "sentToUser": 123123213,
            "value": 5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 400)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
    
    def test_add_transaction_bad_body(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": "gagaga",
            "sentToUser": id2,
            "value": 5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 400)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 

    def test_add_transaction_bad_money(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": id1,
            "sentToUser": id2,
            "value": -5
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 400)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 

    def test_add_transaction_not_enough(self):
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
        tag_obj = {
        "username": "user3",
        "email": "test1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user4",
        "email": "test2@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        db = get_db_test()
        id1 = db.query(User).filter(User.username == 'user3').first().id
        id2 = db.query(User).filter(User.username == 'user4').first().id
        obj = {
            "sentByUser": id1,
            "sentToUser": id2,
            "value": 500
        }
        response = self.client.post('transaction/',json = obj,headers = self.get_auth('user3','qwerty'))
        self.assertEqual(response.status_code, 400)
        delete_user_if_present("user3") 
        delete_user_if_present("user4") 
