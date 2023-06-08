import uuid
from flask_login import UserMixin
from IceBreaker import db

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.String(32), primary_key=True, default=lambda: uuid.uuid4().hex, unique=True, nullable=False)
    socket_id = db.Column(db.String(20), unique=True, nullable=True)
    paired = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    
    user_name = db.Column(db.String(32), unique=False, nullable=False)
    waiting = db.Column(db.Boolean, unique=False, nullable=False, default=False)
    gender = db.Column(db.String(32), unique=False, nullable=False)
    age = db.Column(db.Integer, unique=False, nullable=False)
    gender_pref = db.Column(db.String(32), unique=False, nullable=True)
    min_age_pref = db.Column(db.Integer, unique=False, nullable=True)
    max_age_pref = db.Column(db.Integer, unique=False, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.user_name