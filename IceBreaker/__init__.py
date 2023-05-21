from flask import Flask, Blueprint
from flask_socketio import SocketIO
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
import logging

db = SQLAlchemy()
socketio = SocketIO()
sockets_in_room = {}

def create_app():
    """Construct the core application."""
    app = Flask(__name__)

    

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    load_dotenv()
    app.secret_key = os.getenv("SECRET_KEY")
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)


    basedir = os.path.abspath(os.path.dirname(__file__))
    data_folder = os.path.join(basedir, 'data')
    os.makedirs(data_folder, exist_ok=True)
    db_path = os.path.join(data_folder, 'database.db')

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # db = SQLAlchemy(app)

    db.init_app(app)
    socketio.init_app(app, manage_session=False)
    
    from . import routes
    app.register_blueprint(routes.main_bp)

    return app
        

from .models.user import User
from .models.chat_session import ChatSession
from .models.chat_participant import ChatParticipant
from . import events