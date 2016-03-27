from flask import current_app
from drst.database import db

class Members(db.Model):
    __tablename__ = "members"

    email = db.Column(db.String(128))
    password = db.Column(db.String(64))
    friend_code = db.Column(db.String(9), primary_key=True)

    def __init__(self, email, friend_code):
        self.email = email
        self.friend_code = friend_code

    def __repr__(self):
        return "<Members('%s', '%s')>" % (self.email, self.friend_code)
