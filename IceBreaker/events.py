from IceBreaker import db, socketio, sockets_in_room
from flask import session, request, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from .models import User, ChatSession, ChatParticipant
from .utility import print_users
import time
from sqlalchemy import or_, and_
import random



@socketio.on('userMessage')
def handle_message(message):
    """Handle message"""
    print(f"Message from {session['user_name']}: {message['message']}")
    #Desired format: 22.04.2023 14:30
    time_string = time.strftime("%d.%m.%Y %H:%M", time.localtime())
    print("Wysyłam wiadomość do pokoju: " + session['room'])
    return emit('partnerMessage', {"message": message['message'], "author": session['user_name'], "time" : time_string, 'socket': session['socket_id']}, to=session['room'], skip_sid=request.sid)


@socketio.on('join_chat')
def join(data):
    """Join chat function, handle joining chat"""
    print("JOIN_CHAT--------------------------------------------")
    #TODO: JOIN USER TO THE DESIRED CHAT, CHECK IF USER BELONGS TO THE CHAT
    #TODO: RECEIVE INFO FROM THE USER IF SUCCESSFULY JOINED AND DISABLE THEIR FLAG JOINED_NOT_RECEIVED
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
        
        chat = ChatSession(chat_name=f"{session['user_name']} - {selected_user.user_name}")
        db.session.add(chat)
        db.session.commit()
        
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