import unittest
from flask import Flask, session
from IceBreaker import db, create_app
from IceBreaker.models import User
import uuid

class UserTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()  # assuming you have a testing configuration
        self.app_context = self.app.app_context()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_login_without_session(self):
        with self.app.test_client() as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'IceBreaker', response.data)
    
    def test_user_login(self):
        form_data = {
            'username': 'testuser',
            'gender': 'male',
            'age': 25,
            'gender_pref': 'female',
            'min_age_pref': 20,
            'max_age_pref': 30,
        }
        
        with self.app.test_client() as client:
            response = client.post('/', data=form_data, follow_redirects=False)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/wait', response.headers['Location'])
            self.assertIn('user_id', session)
            self.assertIn(form_data['username'], session['user_name'])
            self.assertEqual(User.query.count(), 1)
            user = User.query.filter_by().first()
            # # new_user = User(user_name=form.username.data+"_"+uuid.uuid4().hex[:3], gender=form.gender.data, age=form.age.data, gender_pref=form.gender_pref.data, min_age_pref=form.min_age_pref.data, max_age_pref=form.max_age_pref.data)
            self.assertIn(form_data['username'], user.user_name)
            self.assertEqual(form_data['gender'], user.gender)
            self.assertEqual(form_data['age'], user.age)
            self.assertEqual(form_data['gender_pref'], 'female')
            self.assertEqual(form_data['min_age_pref'], 20)
            self.assertEqual(form_data['max_age_pref'], 30)
            self.assertEqual(user.socket_id, None)
            self.assertEqual(user.waiting, False)
            
if __name__ == "__main__":
    unittest.main()