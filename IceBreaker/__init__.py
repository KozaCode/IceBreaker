from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, and_
from sqlalchemy.sql.expression import func, select
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_login import UserMixin
import os
from dotenv import load_dotenv
import uuid
from tabulate import tabulate
import random
import time
import logging

app = Flask(__name__)

sockets_in_room = {}

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

load_dotenv()
app.secret_key = os.getenv("SECRET_KEY")
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
    username = StringField('Username', validators=[InputRequired(), Length(min=2, max=32)], default="Piotr")
    gender = SelectField('Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[InputRequired()])
    age = IntegerField('Age', validators=[InputRequired()], default=22)
    gender_pref = SelectField('Looking for', choices=[('male', 'Male'), ('female', 'Female'), ('both', 'Both')])

    min_age_pref = IntegerField('Min preferred age', default=18)

    max_age_pref = IntegerField('Max preferred age', default=35)
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
            user.socket_id,
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
        'Socket ID',
        'User Name',
        'Waiting',
        'Gender',
        'Age',
        'Gender Pref',
        'Min Age Pref',
        'Max Age Pref',
    ]
    print(tabulate(table, headers=headers, tablefmt='grid'))
    
def timer_wrapper(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        func(*args, **kwargs)
        t2 = time.time()
        print(f"Function {func.__name__} took {t2-t1 : .4f} seconds")
    return wrapper

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

@socketio.on('userMessage')
def handle_message(message):
    """Handle message"""
    print(f"Message from {session['user_name']}: {message['message']}")
    #Desired format: 22.04.2023 14:30
    time_string = time.strftime("%d.%m.%Y %H:%M", time.localtime())
    print("Wysyłam wiadomość do pokoju: " + session['room'])
    #Do not send message to the user who sent it
    return emit('partnerMessage', {"message": message['message'], "author": session['user_name'], "time" : time_string, 'socket': session['socket_id']}, to=session['room'], skip_sid=request.sid)


@socketio.on('join_chat')
def join(data):
    """Join chat function, handle joining chat"""
    print("JOIN_CHAT--------------------------------------------")
    #TODO: JOIN USER TO THE DESIRED CHAT, CHECK IF USER BELONGS TO THE CHAT
    user = User.query.filter_by(id=session['user_id']).first()
    participant_of = ChatParticipant.query.filter_by(user_id=user.id).first()
    room = ChatSession.query.filter_by(id=participant_of.chat_id).first()
    join_room(room.id)
    print(f"User {session['user_name']} {session['user_id']} {session['socket_id']} joined room: {room.id}")
    sockets_in_room.setdefault(room.id, []).append(session['socket_id'])
    print(sockets_in_room)
    session['room'] = room.id
    print(f"User {session['user_name']} {session['user_id']} {session['socket_id']} joined room: {room.id}")
    return emit('joined')

@app.route('/chat', methods=['GET'])
def chat():
    """Chat page, handle chat"""
    if ('user_id' not in session) or 'socket_id' not in session : #TODO: Check if user is paired
        return redirect('/')
    else:
        print("#"*80 + "CHAT")
        user = User.query.filter_by(id=session['user_id']).first()
        participant_of = ChatParticipant.query.filter_by(user_id=user.id).first()
        room = ChatSession.query.filter_by(id=participant_of.chat_id).first()
        participants_of_room = ChatParticipant.query.filter_by(chat_id=room.id).all()
        #LIST OF USER NAMES IN THE ROOM
        users = []
        for participant in participants_of_room:
            users.append(User.query.filter_by(id=participant.user_id).first().user_name)
        return render_template('chat.html', data={'user_id': session['user_id'], 'user_name': session['user_name'], 'room': room.id, 'participants': users, 'socket_id': session['socket_id'], 'room_id': room.id})


@socketio.on('connect')
def connect():
    """Connect function, handle connection"""
    if 'user_id' not in session:
        print(f"CONNECT {request.sid}--------------------------------------------")
        return redirect('/')
    print(f"CONNECT {session['user_name']} {request.sid}--------------------------------------------")
    user = User.query.filter_by(id=session['user_id']).first()
    session['socket_id'] = request.sid
    user.socket_id = session['socket_id']
    db.session.commit()
    
@socketio.on('disconnect')
def disconnect():
    """Disconnect function, handle disconnection"""
    if 'user_id' not in session:
        print(f"DISCONNECT {request.sid}--------------------------------------------")
        return redirect('/')
    print(f"DISCONNECT {session['user_name']} {request.sid}--------------------------------------------")
    try:
        user = User.query.filter_by(id=session['user_id']).first()
        user.socket_id = None
        user.waiting = False
        db.session.commit()
    except Exception as e:
        print(e)
        pass
    try:
        leave_room(session['room'])
        sockets_in_room[session['room']].remove(session['socket_id'])
        # print(f"User {session['user_name']} {session['user_id']} {session['socket_id']} left room: {session['room']}")
        # print(sockets_in_room)
    #ANY ERROR
    except Exception as e:
        print(e)
        pass
        
    return redirect('/')


@socketio.on('pair')
def pair():
    """Pairing function, handle pairing users"""
    # print(f"PAIRING {request.sid}--------------------------------------------")
    if 'user_id' not in session:
        return redirect('/')
    else:
        print_info = True
        # if print_info: print("%"*80)
        user = User.query.filter_by(id=session['user_id']).first()
        user.waiting = True
        db.session.commit()
        query_user_preferences = User.query.filter(and_(User.id != user.id, User.waiting == True))

        if user.min_age_pref is not None:
            query_user_preferences = query_user_preferences.filter(User.age >= user.min_age_pref)

        if user.max_age_pref is not None:
            query_user_preferences = query_user_preferences.filter(User.age <= user.max_age_pref)

        if user.gender_pref is not None:
            if user.gender_pref == 'both':
                query_user_preferences = query_user_preferences.filter(or_(User.gender == 'male', User.gender == 'female'))
            else:
                query_user_preferences = query_user_preferences.filter(User.gender == user.gender_pref)
        
        if print_info: print("USER PREFERENCES == USERS")
        if print_info: print_users(query_user_preferences.all())
        query_user_preferences = query_user_preferences.subquery()

        query_matching_preferences = User.query.filter(
            and_(
                User.id != user.id,
                User.waiting == True,
                or_(User.min_age_pref == None, User.min_age_pref <= user.age),
                or_(User.max_age_pref == None, User.max_age_pref >= user.age),
                or_(
                    User.gender_pref == user.gender,
                    User.gender_pref == 'both'
                )
            )
        )
        if print_info: print("USERS PREFERENCES == USER")
        if print_info: print_users(query_matching_preferences.all())
        query_matching_preferences = query_matching_preferences.subquery()
        
        query_intersection = db.session.query(User).select_from(
            query_user_preferences.join(query_matching_preferences, User.id == query_matching_preferences.c.id)
        )
        
        matching_users = query_intersection.all()
        if len(matching_users) == 0:
            return emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})

        if print_info: print("="*30, "MATCHING USERS", "="*30)
        if print_info: print_users(query=matching_users)
        if print_info: print("="*30, "SELECTED USER", "="*30)
        selected_user = random.choice(matching_users)
        if print_info: print(selected_user)
        if print_info: print_users(query=selected_user)
        if print_info: print("-"*80)
        print(f"PAIRING BY {user.user_name} {user.id} WITH {selected_user.user_name} {selected_user.id}")
        
        chat = ChatSession(chat_name=f"{session['user_name']} - {selected_user.user_name}")
        db.session.add(chat)
        db.session.commit()
        print(chat)
        print(chat.id)
        print(chat.chat_name)
        
        participant1 = ChatParticipant(user_id=session['user_id'], chat_id=chat.id)
        participant2 = ChatParticipant(user_id=selected_user.id, chat_id=chat.id)
        user.waiting = False
        selected_user.waiting = False
        db.session.add_all([participant1, participant2])
        db.session.commit()
        
        print(f"SENDIN PAIRED EVENT TO {selected_user.user_name} {selected_user.socket_id}")
        emit('paired', data={'user_id': selected_user.id, 'user_name': selected_user.user_name}, room=selected_user.socket_id)
        print(f"SENDIN PAIRED EVENT TO {session['user_name']} {session['socket_id']}")
        emit('paired', data={'user_id': session['user_id'], 'user_name': session['user_name']}, room=session['socket_id'])
        
@app.route('/wait', methods=['GET'])
def wait():
    """Wait page, handle waiting for a chat/pairing"""
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("#"*80)
        return render_template('wait.html', message="We are looking for someone to talk to you. Please wait...", data={'user_id': session['user_id'], 'user_name': session['user_name']})

@app.route('/', methods=['GET', 'POST'])
def index():
    """Index page, handle login form"""
    if 'user_id' not in session:
        form = LoginForm()
        if form.validate_on_submit():
            new_user = User(user_name=form.username.data+"_"+uuid.uuid4().hex[:3], gender=form.gender.data, age=form.age.data, gender_pref=form.gender_pref.data, min_age_pref=form.min_age_pref.data, max_age_pref=form.max_age_pref.data)
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