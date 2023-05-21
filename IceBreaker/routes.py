from IceBreaker import db
from flask import render_template, request, redirect, session, Blueprint
from .models import User, ChatSession, ChatParticipant
from .forms import LoginForm
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.before_app_first_request
def create_database():
    """Create database if it doesn't exist"""
    db.create_all()

@main_bp.route('/favicon.ico')
def favicon():
    """Favicon route, handle favicon.ico"""
    return redirect('/static/images/favicon.ico')

@main_bp.errorhandler(404)
def page_not_found(e):
    """handle 404 errors by redirecting to home page"""
    print(request.url)
    return redirect("/")

@main_bp.route('/chat', methods=['GET'])
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
    
@main_bp.route('/wait', methods=['GET'])
def wait():
    """Wait page, handle waiting for a chat/pairing"""
    if 'user_id' not in session:
        return redirect('/')
    else:
        print("#"*80)
        return render_template('wait.html', message="We are looking for someone to talk to you. Please wait...", data={'user_id': session['user_id'], 'user_name': session['user_name']})

@main_bp.route('/', methods=['GET', 'POST'])
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