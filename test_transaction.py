import unittest
from unittest import TestCase

from api.errors import *
from models import User
from db import get_db
from api.transaction import get_transaction_by_id,get_sent_by_user,get_received_by_user
from main import app
import requests
import json

def delete_transaction_if_present(id):
    db = get_db()
    if db.query(User).filter(User.username == id).first() is not None:
        db.query(User).filter(User.username == id).delete()
        db.commit()
def get_auth(username = "user5", password = "qwertyqwerty"):
    b = {
        "username": username,
        "password": password,
    }
    url = "http://127.0.0.1:8080/user/login"
    x = requests.post(url=url,json=b)
    if x.status_code == 200:
        return {"Authorization":"Bearer "+json.loads(x.text)["access_token"]}
    else:
        return -1
class TestUser(TestCase):

    
    def test_get_transaction(self):
        with app.app_context():
            db = get_db()
            a = get_transaction_by_id(4)
            print(a)
            self.assertEqual(a.status_code,200)
    
    def test_get_sent_transaction(self):
        with app.app_context():
            db = get_db()
            a = get_sent_by_user(4)
            #print(a)
            self.assertEqual(a.status_code,200)
    def test_get_received_transaction(self):
        with app.app_context():
            db = get_db()
            a = get_received_by_user(4)
            #print(a)
            self.assertEqual(a.status_code,200)
    def test_send_transaction(self):
        with app.app_context():
            db = get_db()
            
            url = "http://127.0.0.1:8080/transaction/"
            tag_obj = { "sentByUser": 5,
                        "sentToUser": 2,
                        "value": 5,
                        }
            x = requests.post(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            self.assertEqual(x.status_code,200)


if __name__ == '__main__':
    unittest.main()