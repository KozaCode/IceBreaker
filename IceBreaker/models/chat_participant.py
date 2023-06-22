import uuid
from IceBreaker import db
import datetime
# from flask_sqlalchemy import SQLAlchemy

class ChatParticipant(db.Model):
    __tablename__ = 'chat_participant'
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex, unique=True, nullable=False)
    user_id = db.Column(db.String(32), db.ForeignKey('user.id'), nullable=False)
    chat_id = db.Column(db.String(32), db.ForeignKey('chat_session.id'), nullable=False)
    joined_at = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow) #TODO: use only UTC timestamps #TODO: Use server_default=db.func.utcnow()


    def __repr__(self):
        return '<Participant %r>' % self.user_id