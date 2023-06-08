from IceBreaker import db
from flask import render_template, request, redirect, session, Blueprint
from .models import User, ChatSession, ChatParticipant
from .forms import LoginForm
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
    if 'socket_id' in session: #TODO: check if user is in chat or if user have a pair
        logger.info("User %s is in chat", session['user_id'])
        user = User.query.filter_by(id=session['user_id']).one_or_none()
        participant_of = ChatParticipant.query.filter_by(user_id=user.id).first()
        room = ChatSession.query.filter_by(id=participant_of.chat_id).with_entities(ChatSession.id).one_or_none()
        users = User.query.join(ChatParticipant).filter(ChatParticipant.chat_id == room.id).with_entities(User.user_name).all()
        
        return render_template('chat.html', data={'user_id': session['user_id'],
                                                  'user_name': session['user_name'],
                                                  'room': room.id, 'participants': users,
                                                  'socket_id': session['socket_id'],
                                                  'room_id': room.id})
    else:
        return redirect('/wait')

    
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

@main_bp.route('/test', methods=['GET'])
def handle_test_page():
    return render_template('test.html')

@main_bp.route('/random-form', methods=['GET'])
def handle_random_form_page():
    """Send user to random_form page"""
    if 'user_id' in session:
        logger.info("User %s is already logged in", session['user_id'])
        return redirect('/wait')
    else:
        logger.info("User is not logged in yet, sending random_form page")
        return render_template('random_form.html', form=LoginForm())
    
    
@main_bp.route('/random-form', methods=['POST'])
def handle_random_form_form():
    """Handle login form"""
    form = LoginForm()
    if form.validate_on_submit():
        logger.info("User %s logged in", form.username.data)
        new_user = User(user_name=form.username.data+"_"+uuid.uuid4().hex[:3],
                        gender=form.gender.data,
                        age=form.age.data,
                        gender_pref=form.gender_pref.data,
                        min_age_pref=form.min_age_pref.data,
                        max_age_pref=form.max_age_pref.data)
        
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id
        session['user_name'] = new_user.user_name
        return redirect('/wait')
    else:
        logger.error("Form validation failed %ss", form.errors)
        return render_template('random_form.html', form=form)
    
@main_bp.route('/', methods=['GET'])
def handle_home_page():
    """Send user to home page"""
    return render_template('home.html')
