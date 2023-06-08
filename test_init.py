import unittest
from flask import Flask, session
from IceBreaker import db, create_app, load_dotenv
from IceBreaker.models import User
import uuid
from unittest.mock import patch
import os
import threading

# TEST __init__.py of IceBreaker
db_lock = threading.Lock()

class InitTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()  # assuming you have a testing configuration
        self.app_context = self.app.app_context()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context.push()
        db.session.remove()
        db.drop_all()
        db.create_all()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_create_app_success(self):
        self.assertTrue(self.app)
        self.assertIsNotNone(self.app)
        
    def test_load_env_vars(self):
        load_dotenv()
        secret_key = os.getenv("SECRET_KEY")
        self.assertIsNotNone(secret_key)
        
    # class User(db.Model, UserMixin):
        # __tablename__ = 'user'
        # id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex, unique=True, nullable=False)
        # socket_id = db.Column(db.String(20), unique=True, nullable=True)
        # user_name = db.Column(db.String(32), unique=False, nullable=False)
        # waiting = db.Column(db.Boolean, unique=False, nullable=False, default=False)
        # gender = db.Column(db.String(32), unique=False, nullable=False)
        # age = db.Column(db.Integer, unique=False, nullable=False)
        # gender_pref = db.Column(db.String(32), unique=False, nullable=True)
        # min_age_pref = db.Column(db.Integer, unique=False, nullable=True)
        # max_age_pref = db.Column(db.Integer, unique=False, nullable=True)
   
    def create_user(self):
        with self.app.app_context():
            for _ in range(4):
                user = User(user_name='Alice', gender='Female', age=20)
                with db_lock:
                    db.session.add(user)
                    db.session.commit()
        
    def test_database_concurent_access(self):
        #threading test
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=self.create_user)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        #count
        print(User.query.count())
        
        
if __name__ == '__main__':
    unittest.main()