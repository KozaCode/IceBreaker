from IceBreaker import db
from flask import render_template, request, redirect, session, Blueprint, jsonify
from .models import User, ChatSession, ChatParticipant
from .forms import RandomPairingForm, DirectJoinForm, CreateRoomForm, UserNameForm
import uuid
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
main_bp = Blueprint('main', __name__)


@main_bp.route('/favicon.ico')
def favicon():
    """Favicon route, handle favicon.ico"""
    logger.info("Handling favicon.ico")
    try:
        return redirect('/static/images/favicon.ico')
    except Exception as e:
        logger.error("Error handling favicon.ico: %s", request.url)


@main_bp.app_errorhandler(404)
def page_not_found(e):
    """handle 404 errors by redirecting to home page"""
    logger.error("Page not found: %s", request.url)
    return redirect("/")

@main_bp.route('/chat', methods=['GET'])
def chat():
    """Chat page, handle chat"""
    if 'user_id' in session: #TODO: check if user is in chat or if user have a pair
        logger.info("User %s is in chat", session['user_id'])
        user = User.query.filter_by(id=session['user_id']).one_or_none()
        participant_of = ChatParticipant.query.filter_by(user_id=user.id).first()
        room = ChatSession.query.filter_by(id=participant_of.chat_id).with_entities(ChatSession.id).one_or_none()
        users = User.query.join(ChatParticipant).filter(ChatParticipant.chat_id == room.id).with_entities(User.user_name).all()
        
        return render_template('chat.html',
                            #    data={'user_id': session['user_id'],
                            #                       'user_name': session['user_name'],
                            #                       'room': room.id, 'participants': users,
                            #                     #   'socket_id': session['socket_id'],
                            #                       'room_id': room.id}
                               )
    else:
        return redirect('/')

    
@main_bp.route('/wait', methods=['GET'])
def handle_wait_page():
    """Wait page, handle waiting for a chat/pairing"""
    if 'user_id' not in session:
        logger.error("User is not logged in")
        return redirect('/random-form')
    else:
        logger.info("User %s is waiting for a chat", session['user_name'])
        return render_template('wait.html', data={'user_id': session['user_id'],
                                                  'user_name': session['user_name']})
        
@main_bp.route('/create-room', methods=['POST'])
def handle_create_room():
    """Handle create room"""
    create_room_form = CreateRoomForm()
    if create_room_form.validate_on_submit():
        if 'user_id' not in session:
            user = User(user_name=session['user_name']+"_"+uuid.uuid4().hex[:3])
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
        else:
            user = User.query.filter_by(id=session['user_id']).one_or_none()
            session['user_name'] = user.user_name
            # if user.user_name != session['user_name']:
            #     user.user_name = session['user_name']+"_"+uuid.uuid4().hex[:3]
            #     db.session.commit()
            #     session['user_id'] = user.id
            #     session['user_name'] = user.user_name
            #     logger.info("User %s logged in", session['user_id'])
        room = ChatSession(chat_name=create_room_form.chat_name.data,
                            chat_password=create_room_form.password.data,
                            direct_join_key=create_room_form.join_key.data,
                            allow_join=True)
        db.session.add(room)
        db.session.commit()
        participant = ChatParticipant(user_id=user.id, chat_id=room.id)
        db.session.add(participant)
        db.session.commit()
        return redirect('/chat')
    else:
        logger.error("create_room_form validation failed %s", create_room_form.errors)
        return redirect('/')


# @socketio.on('directJoin')
# def handle_direct_join(data):
#     """Handle direct join"""
#     logger.info("%s", data)
#     if 'user_id' not in session:
#         logger.info("User is not logged in %s", request.sid)
#         new_user = User(user_name=data['user_name']+"_"+uuid.uuid4().hex[:3], socket_id=request.sid) #TODO: USE FORM INSTEAD OF GETTING DATA THIS WAY
#         db.session.add(new_user)
#         db.session.commit()
#         logger.info("User %s %s created", new_user.user_name, new_user.id)
#         session['user_id'] = new_user.id
#         session['user_name'] = new_user.user_name
#         session['socket_id'] = new_user.socket_id

#     logger.info("User %s %s trying to join room %s with password %s", session['user_name'], session['user_id'], data['join_key'], data['chat_password'])
#     #Filter rooms by allowed join and direct join key
#     room = ChatSession.query.filter_by(allow_join=True, direct_join_key=data['join_key']).first()
#     if room is None:
#         logger.info("Room %s does not exist", data['join_key'])
#         return emit('roomNotFound')
#     #
#     if room.chat_password is not None:
#         if room.chat_password != data['chat_password']:
#             pass
#     #joined above conditions
#     if room.chat_password is not None and room.chat_password != data['chat_password']:
#         logger.info("Room %s password is incorrect", data['join_key'])
#         return emit('incorrectPassword')
    
#     participant = ChatParticipant(user_id=session['user_id'], chat_id=room.id)
#     db.session.add(participant)
#     db.session.commit()
    
#     logger.info("User %s %s joined room %s", session['user_name'], session['user_id'], room.id)
#     join_room(room.id)
#     session['room'] = room.id
#     sockets_in_room.setdefault(room.id, []).append(session['socket_id'])
#     logger.info("Sockets in room %s: %s", room.id, sockets_in_room[room.id])
    
#     participants_in_room = User.query.join(ChatParticipant, User.id == ChatParticipant.user_id).filter(ChatParticipant.chat_id == room.id).all()
#     participants = {}
#     for participant in participants_in_room:
#         participants[participant.id] = participant.user_name
        
#     return emit('roomJoined', {'room': room.id})

# Convert
# @socketio.on('directJoin')
# def handle_direct_join(data):
# Into this

@main_bp.route('/connect-directly', methods=['POST'])
def handle_direct_join():
    """Handle direct join"""
    print("Connect directly")
    direct_join_form = DirectJoinForm()
    print("Direct join form: ", direct_join_form)
    if direct_join_form.validate_on_submit():
        if 'user_name' in session:
            if 'user_id' not in session:
                user = User(user_name=session['user_name']+"_"+uuid.uuid4().hex[:3])
                db.session.add(user)
                db.session.commit()
                session['user_id'] = user.id
                session['user_name'] = user.user_name
                session['socket_id'] = user.socket_id
            else:
                user = User.query.filter_by(id=session['user_id']).one_or_none()
            
            room = ChatSession.query.filter_by(allow_join=True, direct_join_key=direct_join_form.join_key.data).one_or_none()
            if room is None:
                return jsonify({'status': 'ERROR', 'error': 'Room does not exist'})
            else:
                # Check if user is already in this room
                participant = ChatParticipant.query.filter_by(user_id=user.id, chat_id=room.id).one_or_none()
                if participant is not None:
                    return jsonify({'status': 'ERROR', 'error': 'User is already in this room'})
                else:
                    if room.chat_password is not None:
                        if room.chat_password != direct_join_form.password.data:
                            return jsonify({'status': 'ERROR', 'error': 'Incorrect password'})
                    participant = ChatParticipant(user_id=user.id, chat_id=room.id)
                    db.session.add(participant)
                    db.session.commit()
                    return redirect('/chat')

    
@main_bp.route('/user-name', methods=['POST'])
def handle_submit_user_name():
    user_name_form = UserNameForm()
    if user_name_form.validate_on_submit():
        session['user_name'] = user_name_form.user_name.data
        return jsonify({'status': 'OK', 'user_name': session['user_name']})
    else:
        return jsonify({'status': 'ERROR'})
    
    
# @main_bp.route('/random-form', methods=['POST'])
# def handle_random_form_form():
#     """Handle login form"""
#     random_pairing_form = RandomPairingForm()
#     if random_pairing_form.validate_on_submit():
#         logger.info("User %s logged in", random_pairing_form.user_name.data)
#         new_user = User(user_name=random_pairing_form.user_name.data+"_"+uuid.uuid4().hex[:3],
#                         gender=random_pairing_form.gender.data,
#                         age=random_pairing_form.age.data,
#                         gender_pref=random_pairing_form.gender_pref.data,
#                         min_age_pref=random_pairing_form.min_age_pref.data,
#                         max_age_pref=random_pairing_form.max_age_pref.data)
        
#         db.session.add(new_user)
#         db.session.commit()
#         session['user_id'] = new_user.id
#         session['user_name'] = new_user.user_name
#         return redirect('/wait')
#     else:
#         logger.error("random_pairing_form validation failed %s", random_pairing_form.errors)
#         return render_template('random_form.html', random_pairing_form=random_pairing_form)

@main_bp.route('/random-pairing', methods=['POST'])
def handle_random_pairing():
    print("Random-pairing")
    random_pairing_form = RandomPairingForm()
    print("Random-pairing form: ", random_pairing_form)
    if random_pairing_form.validate_on_submit():
        if 'user_id' not in session:
            logger.error("User is not logged in")
            user = User(user_name=session['user_name']+"_"+uuid.uuid4().hex[:3],
                        gender=random_pairing_form.gender.data,
                        age=random_pairing_form.age.data,
                        gender_pref=random_pairing_form.gender_pref.data,
                        min_age_pref=random_pairing_form.min_age_pref.data,
                        max_age_pref=random_pairing_form.max_age_pref.data)

            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            session['user_name'] = user.user_name
            logger.info("User %s logged in", session['user_id'])
            return redirect('/wait')
        else:
            user = User.query.filter_by(id=session['user_id']).one_or_none()
            if user.user_name != session['user_name'] or \
                user.gender != random_pairing_form.gender.data or \
                user.age != random_pairing_form.age.data or \
                user.gender_pref != random_pairing_form.gender_pref.data or \
                user.min_age_pref != random_pairing_form.min_age_pref.data or \
                user.max_age_pref != random_pairing_form.max_age_pref.data:

                    user.user_name = session['user_name']+"_"+uuid.uuid4().hex[:3]
                    user.gender = random_pairing_form.gender.data
                    user.age = random_pairing_form.age.data
                    user.gender_pref = random_pairing_form.gender_pref.data
                    user.min_age_pref = random_pairing_form.min_age_pref.data
                    user.max_age_pref = random_pairing_form.max_age_pref.data
                    db.session.commit()
                    session['user_id'] = user.id
                    session['user_name'] = user.user_name
                    logger.info("User %s logged in", session['user_id'])
            return redirect('/wait')
    
    return redirect('/')
    
    
            
    
@main_bp.route('/', methods=['GET'])
def handle_home_page():
    """Send user to home page"""
    random_pairing_form = RandomPairingForm()
    direct_join_form = DirectJoinForm()
    create_room_form = CreateRoomForm()
    user_name_form = UserNameForm()
    if 'user_name' in session:
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
            if user is None:
                return redirect('/') #FIXME: This should not happen, user with id should exist in database
            
            user_chat_sessions = db.session.query(ChatParticipant.chat_id).filter(ChatParticipant.user_id == session['user_id']).subquery()

            rooms_with_participants = db.session.query(ChatSession, User).join(ChatParticipant, ChatParticipant.chat_id == ChatSession.id).join(User, ChatParticipant.user_id == User.id).filter(ChatSession.id.in_(user_chat_sessions)).all()

            rooms_info = {}
            for room, participant in rooms_with_participants:
                if room.id not in rooms_info:
                    rooms_info[room.id] = {'id': room.id, 'name': room.chat_name, 'participants': [], 'number_of_users': 0, 'join_key': room.direct_join_key}
                rooms_info[room.id]['participants'].append({'user_id': participant.id, 'user_name': participant.user_name})
                rooms_info[room.id]['number_of_users'] += 1
                
            rooms_info = list(rooms_info.values())
            logger.info("Rooms_info %s", rooms_info)
            return render_template('home.html', random_pairing_form=random_pairing_form, direct_join_form=direct_join_form, create_room_form=create_room_form, user_name_form=user_name_form, data={'user_name': session['user_name'],'rooms': rooms_info})
        return render_template('home.html', random_pairing_form=random_pairing_form, direct_join_form=direct_join_form, create_room_form=create_room_form, user_name_form=user_name_form, data={'user_name': session['user_name']})
    else:
        # logger.info("User is not logged in yet, sending home page, request: %s", request.sid)
        return render_template('home.html', random_pairing_form=random_pairing_form, direct_join_form=direct_join_form, create_room_form=create_room_form, user_name_form=user_name_form, data={})
