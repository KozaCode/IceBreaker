import uuid
from IceBreaker import db

class ChatParticipant(db.Model):
    __tablename__ = 'chat_participant'
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex, unique=True, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_session.id'), nullable=False)
    # last = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    
    def __repr__(self):
        return '<Participant %r>' % self.user_id