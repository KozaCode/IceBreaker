from IceBreaker import db, socketio, sockets_in_room
from flask import session, request, redirect
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from .models import User, ChatSession, ChatParticipant
from .utility import print_users
import time
import datetime
from sqlalchemy import or_, and_
import random

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#Session attributes: user_id, user_name, socket_id, room

@socketio.on('updateChatSettings')
def handle_update_settings(data): #Settings: user_name, chat_name, allow_join, direct_join_key, chat_password
    logger.info("User %s %s updated settings", session['user_name'], session['user_id'])
    logger.info("Data: %s", data)
    changed = False
    for key, value in data.items():
        if key == 'user_name':
            session['user_name'] = value
            user = User.query.get(session['user_id'])
            user.user_name = value
            changed = True
        elif key == 'chat_name':
            room = ChatSession.query.get(session['room'])
            room.chat_name = value
            changed = True
        elif key == 'allow_join':
            room = ChatSession.query.get(session['room'])
            room.allow_join = value
            changed = True
        elif key == 'direct_join_key':
            room = ChatSession.query.get(session['room'])
            room.direct_join_key = value
            changed = True
        elif key == 'chat_password':
            room = ChatSession.query.get(session['room'])
            room.chat_password = value
            changed = True
            
    if changed:
        db.session.commit()
        return emit('reload')

@socketio.on('userMessage')
def handle_user_message(user_message):
    """Handle message"""
    if user_message['message_type'] == 'text':
        logger.info("Message from %s: %s", session['user_name'], user_message['message'])
    #Desired date format: 22.04.2023 14:30
    time_string = time.strftime("%d.%m.%Y %H:%M", time.localtime())
    timestamp = time.time()
    logger.info("Sending message from %s to room %s", session['user_name'], session['room'])
    
    emit("updateMessageTime", {"message_id": user_message['message_id'],
                               "time": time_string,
                               "timestamp": timestamp})
    
    return emit('partnerMessage', { "message_id": user_message['message_id'],
                                    "message_type": user_message['message_type'],
                                    "message": user_message['message'],
                                    "room": session['room'],
                                    "author": session['user_name'],
                                    "author_id": session['user_id'],
                                    "time" : time_string,
                                    "timestamp": timestamp,
                                    "socket": session['socket_id']},
                to=session['room'], skip_sid=request.sid)

@socketio.on('join_chat')
def handle_join_chat():
    """Joining user to the chat. Called when user is matched with another user and their browser is redirected to /chat"""
    #TODO: JOIN USER TO THE DESIRED CHAT, CHECK IF USER BELONGS TO THE CHAT
    
    user = User.query.get(session['user_id'])
    #User is not in the database
    if user is None:
        return redirect('/') #FIXME: Redirect to error page
    #CHAT PARTICIPANT: ID, USER_ID, CHAT_ID
    #EXAMPLE: 1, (PETER), (CHAT1) 
    #EXAMPLE: 2, (JOHN), (CHAT1)
    #EXAMPLE: 3, (PETER), (CHAT2)
    #EXAMPLE: 4, (JULIA), (CHAT2)
    participant_of = ChatParticipant.query.filter_by(user_id=user.id).one_or_none()
    #User is not participant of any chat
    if participant_of is None:
        return redirect('/') #FIXME: Redirect to error page

    #CHAT SESSION: ID, CHAT_NAME, PARTICIPANTS
    #EXAMPLE: 1, (CHAT1), (PETER, JOHN)
    #EXAMPLE: 2, (CHAT2), (PETER, JULIA)
    room = ChatSession.query.filter_by(id=participant_of.chat_id).first()
    #This room does not exist
    if room is None:
        return redirect('/') #FIXME: Redirect to error page
    
    #Make sure that user belongs to the certain chat
    if ChatParticipant.query.filter_by(user_id=user.id, chat_id=room.id).first() is None:
        return redirect('/') #FIXME: Redirect to error page

    join_room(room.id)
    session['room'] = room.id
    logger.info("User %s %s joined room %s", session['user_name'], session['user_id'], session['room'])
    
    sockets_in_room.setdefault(room.id, []).append(session['socket_id'])
    logger.info("Sockets in room %s: %s", room.id, sockets_in_room[room.id])
    
    participants_in_room = User.query.join(ChatParticipant, User.id == ChatParticipant.user_id).filter(ChatParticipant.chat_id == room.id).all()
    participants = {}
    for participant in participants_in_room:
        participants[participant.id] = participant.user_name

    logger.info("Sending this data to room %s: %s", room.id, {'user_id': session['user_id'],
                                                              'user_name': session['user_name'],
                                                              'room': room.id,
                                                              'participants': participants,
                                                              'allow_join': room.allow_join,
                                                              'direct_join_key': room.direct_join_key,
                                                              'chat_password': room.chat_password})
    
    return emit('joined', {'user_id': session['user_id'],
                           'user_name': session['user_name'],
                           'room': room.id,
                           'chat_name': room.chat_name,
                           'created_at': room.created_at.strftime("%d.%m.%Y %H:%M"),
                           'participants': participants,
                           'allow_join': room.allow_join,
                           'direct_join_key': room.direct_join_key,
                           'chat_password': room.chat_password})

@socketio.on('connect')
def connect():
    """Connect function, called each time user connects(when page is loaded)"""
    if not session.get('user_id'):
        logger.info("User %s connected", request.sid)
        return redirect('/')
    
    logger.info("User %s %s connected", session['user_name'], session['user_id'])
    user = User.query.get(session['user_id'])
    session['socket_id'] = request.sid
    user.socket_id = session['socket_id']
    db.session.commit()
    
@socketio.on('disconnect')
def disconnect():
    """Disconnect function, handle disconnection"""
    if not session.get('user_id'):
        logger.error("User %s disconnected", request.sid)
        return redirect('/')
    logger.error("User %s %s %s disconnected", session['user_name'], session['user_id'], session['socket_id'])
    try:
        user = User.query.filter(User.id == session['user_id']).update({'socket_id': None, 'waiting': False})
        db.session.commit()
        logger.info("Successfully updated user %s %s", session['user_name'], session['user_id'])
    except Exception as e:
        logger.error("Error updating user %s %s", session['user_name'], session['user_id'])

    try:
        leave_room(session['room'])
        logger.info("%s", sockets_in_room)
        sockets_in_room[session['room']].remove(session['socket_id']) #FIXME: KeyError, x not in list
        logger.info("%s", sockets_in_room)
        logger.info("Successfully removed socket %s from room %s", session['socket_id'], session['room'])
    except Exception as e:
        logger.error("Error removing socket %s", session['user_id'])
    return redirect('/')

@socketio.on('pair')
def pair():
    """Pairing function, handle pairing users"""
    if not session.get('user_id'):
        return redirect('/')
    else:
        user = User.query.filter_by(id=session['user_id']).one_or_none()
        logger.info("user: %s, paired: %s", user.user_name, user.paired)
        if user.paired:
            logger.info("User %s %s already paired. Redirect to /chat", user.user_name, user.id)
            
            return emit('paired', data={'user_id': session['user_id'],
                                        'user_name': session['user_name']},
                        room=session['socket_id'])
        
        user.waiting = True
        db.session.commit()
        query_user_preferences = User.query.filter(and_(User.id != user.id, User.waiting == True))

        print(f"\n\nUsers before filtering for user: {session['user_name']}")
        print_users(query_user_preferences.all())

        if user.min_age_pref is not None:
            query_user_preferences = query_user_preferences.filter(User.age >= user.min_age_pref)
            print(f"\n\nUsers by min age ({user.min_age_pref}) for user: {session['user_name']}")
            print_users(query_user_preferences.all())

        if user.max_age_pref is not None:
            query_user_preferences = query_user_preferences.filter(User.age <= user.max_age_pref)
            print(f"\n\nUsers by max age ({user.max_age_pref}) for user: {session['user_name']}")
            print_users(query_user_preferences.all())

        if user.gender_pref is not None:
            if user.gender_pref == 'both':
                query_user_preferences = query_user_preferences.filter(or_(User.gender == 'male', User.gender == 'female'))
            else:
                query_user_preferences = query_user_preferences.filter(User.gender == user.gender_pref)

            print(f"\n\nUsers by user gender_pref ({user.gender_pref}) for user: {session['user_name']}")
            print_users(query_user_preferences.all())

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
        
        print(f"\n\nMatching preferences before intersection for user: {session['user_name']}")
        print_users(query_matching_preferences.all())

        query_matching_preferences = query_matching_preferences.subquery()
        
        query_intersection = db.session.query(User).select_from(
            query_user_preferences.join(query_matching_preferences, User.id == query_matching_preferences.c.id)
        )
        
        matching_users = query_intersection.all()

        print(f"\n\nMatching users after intersection for user: {session['user_name']}")
        print_users(matching_users)

        if len(matching_users) == 0:
            return emit('no_match_yet', data={'user_id': session['user_id'], 'user_name': session['user_name']})

        selected_user = random.choice(matching_users)
        #DateTime
        chat = ChatSession(chat_name=f"{session['user_name']} - {selected_user.user_name}", created_at=datetime.datetime.now())
        db.session.add(chat)
        db.session.commit()
        
        participant1 = ChatParticipant(user_id=session['user_id'], chat_id=chat.id)
        participant2 = ChatParticipant(user_id=selected_user.id, chat_id=chat.id)
        user.waiting = False
        selected_user.waiting = False
        
        user.paired = True
        selected_user.paired = True
        
        db.session.add_all([participant1, participant2])
        db.session.commit()

        logger.info("User(session) %s %s paired with user %s %s", session['user_name'], session['user_id'], selected_user.user_name, selected_user.id)
        emit('paired', data={'user_id': selected_user.id,
                             'user_name': selected_user.user_name},
             room=selected_user.socket_id)
        
        emit('paired', data={'user_id': session['user_id'],
                             'user_name': session['user_name']},
             room=session['socket_id'])