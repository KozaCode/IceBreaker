from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.sql.expression import func, select
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin
import os
from dotenv import load_dotenv
import uuid
from time import sleep
from tabulate import tabulate
import random

app = Flask(__name__)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY") #TODO:CHANGE THIS TO SOMETHING MORE SECURE
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'data', 'database.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

socketio = SocketIO(app, manage_session=False)

from .models.user import User
from .models.chat_session import ChatSession
from .models.chat_participants import ChatParticipant

class LoginForm(FlaskForm):
    """Login form"""
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=32)])
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[InputRequired()])
    age = IntegerField('Age', validators=[InputRequired()])
    gender_pref = SelectField('Looking for', choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')])
    min_age_pref = IntegerField('Min preferred age')
    max_age_pref = IntegerField('Max preferred age')
    submit = SubmitField('Login')
    
def print_users(query):
    if isinstance(query, list):
        users = query
    else:
        users = [query]
    table = []
    for user in users:
        table.append([
            user.id,
            user.user_name,
            user.waiting,
            user.gender,
            user.age,
            user.gender_pref,
            user.min_age_pref,
            user.max_age_pref,
        ])
    headers = [
        'ID',
        'User Name',
        'Waiting',
        'Gender',
        'Age',
        'Gender Pref',
        'Min Age Pref',
        'Max Age Pref',
    ]
    print(tabulate(table, headers=headers, tablefmt='grid'))

@app.before_first_request
def create_database():
    """Create database if it doesn't exist"""
    db.create_all()

@app.route('/favicon.ico')
def favicon():
    """Favicon route, handle favicon.ico"""
    return redirect('/static/images/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    """handle 404 errors by redirecting to home page"""
    print(request.url)
    return redirect("/")

@app.route('/chat', methods=['GET'])
def chat():
    """Chat page, handle chat"""
    if 'user_id' not in session: #TODO: Check if user is paired
        return redirect('/')
    else:
        print("#"*80)
        print(session)
        user = User.query.filter_by(id=session['user_id']).first()
        db.session.commit()
        return render_template('chat.html', data={'user_id': session['user_id'], 'user_name': session['user_name']})

@socketio.on('pair')
def pair():
    """Pairing function, handle pairing users"""
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("%"*80)
        user = User.query.filter_by(id=session['user_id']).first()
        print(user)
        #TODO: AVOID SITUAION WHERE USER WOULD BE PAIRED WITH SOMEONE ELSE WHILE LOOKING FOR A MATCH
        user.waiting = True
        db.session.commit()
        query = User.query.filter(User.waiting==True).filter(User.id!=user.id)
        if user.min_age_pref is not None:
            query = query.filter(User.age >= user.min_age_pref)
            print("MIN AGE PREF", user.min_age_pref)
            print_users(query=query.all())
            if len(query.all()) == 0:
                emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})
        if user.max_age_pref is not None:
            query = query.filter(User.age <= user.max_age_pref)
            print("MAX AGE PREF", user.max_age_pref)
            print_users(query=query.all())
            if len(query.all()) == 0:
                emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})
        if user.gender_pref is not None:
            if user.gender_pref == 'both':
                query = query.filter(or_(User.gender == 'male', User.gender == 'female'))
            else:
                query = query.filter(User.gender == user.gender_pref)
            print("GENDER PREF", user.gender_pref)
            print_users(query=query.all())
            if len(query.all()) == 0:
                emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})
        matching_users = query.all()
        if len(matching_users) == 0:
            emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})
        print("="*30, "USER NEEDS", "="*30)
        print(user)
        print("="*30, "MATCHING USERS", "="*30)
        print_users(query=matching_users)
        print("="*30, "SELECTED USER", "="*30)
        selected_user = random.choice(matching_users)
        print(selected_user)
        print_users(query=selected_user)
        emit('paired', data={'user_id': session['user_id'], 'user_name': session['user_name']})
    
@app.route('/wait', methods=['GET'])
def wait():
    """Wait page, handle waiting for a chat/pairing"""
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("#"*80)
        print(session)
        return render_template('wait.html', message="We are looking for someone to talk to you. Please wait...", data={'user_id': session['user_id'], 'user_name': session['user_name']})
    

@app.route('/', methods=['GET', 'POST'])
def index():
    """Index page, handle login form"""
    # If user is in db session, redirect to chat
    if 'user_id' not in session:
        form = LoginForm()
        if form.validate_on_submit():
            
            new_user = User(user_name=form.username.data, gender=form.gender.data, age=form.age.data, gender_pref=form.gender_pref.data, min_age_pref=form.min_age_pref.data, max_age_pref=form.max_age_pref.data)
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            session['user_name'] = new_user.user_name
            return redirect('/wait')
    else:
        return redirect('/wait')
    return render_template('index.html', form=form)

if __name__ == '__main__':
    socketio.run(app)