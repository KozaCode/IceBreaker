import uuid
from IceBreaker import db

class ChatParticipant(db.Model):
    __tablename__ = 'chat_participant'
    id = db.Column(db.String(32), primary_key=True, default=uuid.uuid4().hex, unique=True, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_session.id'), nullable=False)