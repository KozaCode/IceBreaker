import uuid
from IceBreaker import db

class ChatSession(db.Model):
    __tablename__ = 'chat_session'
    id = db.Column(db.String(32), primary_key=True, default=uuid.uuid4().hex, unique=True, nullable=False)
    chat_name = db.Column(db.String(32), unique=False, nullable=True)
    participants = db.relationship('ChatParticipant', backref='chat_session', lazy=True)