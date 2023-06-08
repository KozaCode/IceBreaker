from flask import Flask, Blueprint, redirect
from flask_socketio import SocketIO
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
import pathlib
import logging
from dotenv import load_dotenv
import colorlog
load_dotenv()

#TODO: Secure session cookie, use token instead of user_id

db = SQLAlchemy()
socketio = SocketIO(max_http_buffer_size=50*1024*1024) # 50MB
sockets_in_room = {}

def configure_database(app, db_file="database.db"):
    """Configure database."""
    basedir = pathlib.Path(__file__).parent.absolute()
    data_folder = basedir / 'data'
    data_folder.mkdir(parents=True, exist_ok=True)
    db_path = data_folder / db_file
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(db_path)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
def configure_session(app):
    """Configure session."""
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)
    
def create_app():
    """Construct the core application."""
    app = Flask(__name__)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.INFO)

    configure_session(app)
    configure_database(app)
    socketio.init_app(app, manage_session=False)
    
    
    # log_format = '%(levelname)s %(name)s %(threadName)s : %(message)s'
    # logging.basicConfig(format=log_format, level=logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s====\n%(name)s.%(funcName)s:%(lineno)d %(message)s\n====',
    ))
    
    logger = logging.getLogger(__name__)
    logger.addHandler(console_handler)
    
    from .routes import main_bp
    with app.app_context():
        app.register_blueprint(main_bp)
        db.create_all()
        
    # app.logger.setLevel(logging.INFO)
    return app
        
from .models.user import User
from .models.chat_session import ChatSession
from .models.chat_participant import ChatParticipant
from . import events

