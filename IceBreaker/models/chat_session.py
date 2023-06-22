import uuid
from IceBreaker import db
import datetime

class ChatSession(db.Model):
    __tablename__ = 'chat_session'
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex, unique=True, nullable=False)
    chat_name = db.Column(db.String(32), unique=False, nullable=True)
    participants = db.relationship('ChatParticipant', backref='chat_session', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    allow_join = db.Column(db.Boolean, nullable=False, default=False)
    direct_join_key = db.Column(db.String(32), unique=True, nullable=True)
    chat_password = db.Column(db.String(32), unique=False, nullable=True)
    
# user_name, chat_name, allow_join, direct_join_key, chat_password