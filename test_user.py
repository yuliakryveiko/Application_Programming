import unittest
from unittest import TestCase

from api.errors import *
from models import User
from db import get_db
from api.user import get_user,add_user
from main import app
import requests
import json

def delete_user_if_present(id):
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

    
    def test_get_user(self):
        with app.app_context():
            db = get_db()
            a = get_user('4')
            #print(a)
            self.assertEqual(a.status_code,200)
    def test_get_user_bad_id(self):
        with app.app_context():
            db = get_db()
            a = get_user('23')
            #print(a)
            self.assertNotEqual(a.status_code,200)
    def test_add_user(self):
        with app.app_context():
            db = get_db()
            delete_user_if_present("user9")
            
            url = "http://127.0.0.1:8080/user"
            tag_obj = {"email": "qwerty@qwerty.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user9",
                        "password": "qwerty"}
            x = requests.post(url=url,json=tag_obj,headers=get_auth())
            
            print(x.text)
            delete_user_if_present("user9")
            self.assertEqual(x.status_code,200)
    def test_add_user_bad_email(self):
        with app.app_context():
            db = get_db()
            delete_user_if_present("user8")
          
            url = "http://127.0.0.1:8080/user"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user8",
                        "password": "qwerty"}
            x = requests.post(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            delete_user_if_present("user8")
            self.assertEqual(x.status_code,400)

    def test_add_user_bad_usename(self):
        with app.app_context():
            db = get_db()
            delete_user_if_present("user8")
          
            url = "http://127.0.0.1:8080/user"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user4",
                        "password": "qwerty"}
            x = requests.post(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            delete_user_if_present("user8")
            self.assertEqual(x.status_code,400)

    def test_add_user_bad_schema(self):
        with app.app_context():
            db = get_db()
            delete_user_if_present("user8")
          
            url = "http://127.0.0.1:8080/user"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user4",
                        }
            x = requests.post(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            delete_user_if_present("user8")
            self.assertEqual(x.status_code,400)
    def test_update(self):
        with app.app_context():
            db = get_db()
           
          
            url = "http://127.0.0.1:8080/user/4"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user4",
                        "password": "qwertyqwerty"
                        }
            x = requests.put(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            
            self.assertEqual(x.status_code,200)
    def test_update_bad_schema(self):
        with app.app_context():
            db = get_db()
           
          
            url = "http://127.0.0.1:8080/user/4"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user4",
                        }
            x = requests.put(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            
            self.assertEqual(x.status_code,400)

    def test_update_bad_name(self):
        with app.app_context():
            db = get_db()
           
          
            url = "http://127.0.0.1:8080/user/4"
            tag_obj = {"email": "qwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user5",
                        }
            x = requests.put(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            
            self.assertEqual(x.status_code,400)
    def test_update_bad_email(self):
        with app.app_context():
            db = get_db()
           
          
            url = "http://127.0.0.1:8080/user/4"
            tag_obj = {"email": "qwertyqwerty@gmail.com",
                        "firstName": "Kyle",
                        "lastName": "Jackson",
                        "username": "user4",
                        }
            x = requests.put(url=url,json=tag_obj,headers=get_auth())
            #print(x.text)
            
            self.assertEqual(x.status_code,400)


if __name__ == '__main__':
    unittest.main()