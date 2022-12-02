from flask_testing import TestCase
from flask import Flask
from db import get_db_test
from models import User,JWTToken
import requests
import json
from flask_jwt_extended import JWTManager
def delete_user_if_present(id):
    db = get_db_test()
    if db.query(User).filter(User.username == id).first() is not None:
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

    def test_login_bad_body(self):
        a = self.get_auth('user1',1)
        self.assertEqual(a,-1)
    
    def test_login_bad_user(self):
        a = self.get_auth('user4','1')
        self.assertEqual(a,-1)

    def test_login_revoked(self):
        a = self.get_auth('user1','qwerty')
        x = self.client.delete('user/logout',headers = a)
        x = self.client.put('user/replenish',headers = a)
        self.assert401(x)

    def test_create_user(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "test@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_create_user_bad_body(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": 1,
        "email": "test@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_create_user_user_exists(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user1",
        "email": "test@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_create_user_email_exists(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "email1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        delete_user_if_present("user3")
        self.assertEqual(response.status_code,400)

    def test_get_user(self):
        response = self.client.get('user/3')
        self.assertEqual(response.status_code,404)

    def test_get_user_self(self):
        response = self.client.get('user/self',headers = self.get_auth('user1','qwerty'))
        self.assertEqual(response.status_code,200)

    def test_update_user(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        #print(response.text)
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/user3',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_update_user_bad_id(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/5',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,404)
    
    def test_update_user_bad_user(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/user3',json=tag_obj,headers = self.get_auth('user2','qwerty'))
        delete_user_if_present("user3") 
        #print(response.text)
        self.assertEqual(response.status_code,401)

    def test_update_user_bad_body(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": 1,
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/user3',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_update_user_username_exists(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user2",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/user3',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_update_user_email_exists(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user3",
        "email": "email1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/user3',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_update_user_self(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/self',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_update_user_bad_body_self(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": 1,
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/self',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_update_user_username_exists_self(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user2",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/self',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_update_user_email_exists_self(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        tag_obj = {
        "username": "user3",
        "email": "email1@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.put('user/self',json=tag_obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)
    
    def test_delete_user(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        response = self.client.delete('user/user3',headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_delete_user_bad_user(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        response = self.client.delete('user/user3',headers = self.get_auth('user2','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,401)

    def test_delete_user_bad_username(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        response = self.client.delete('user/user324',headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,404)


    def test_delete_user_self(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        response = self.client.delete('user/self',headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_add_money(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)
    
    def test_add_money_bad_body(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": "ggg"
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)
    
    def test_remove_money(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        response = self.client.put('user/withdraw',json = obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,200)

    def test_remove_money_bad_body(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        obj = {
            "amount": "ggg"
        }
        response = self.client.put('user/withdraw',json = obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)

    def test_remove_money_not_enough(self):
        delete_user_if_present("user3") 
        tag_obj = {
        "username": "user3",
        "email": "haha@gmail.com",
        "password": "qwerty",
        "firstName": "Carl",
        "lastName": "Jackson"
        }
        response = self.client.post('user/',json=tag_obj)
        obj = {
            "amount": 50
        }
        response = self.client.put('user/replenish',json = obj,headers = self.get_auth('user3','qwerty'))
        obj = {
            "amount": 60
        }
        response = self.client.put('user/withdraw',json = obj,headers = self.get_auth('user3','qwerty'))
        delete_user_if_present("user3") 
        self.assertEqual(response.status_code,400)