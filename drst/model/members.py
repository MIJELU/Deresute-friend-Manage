from flask import current_app
from drst.database import db

class Members(db.Model):
    __tablename__ = "members"

    email = db.Column(db.String(128), primary_key=True)
    password = db.Column(db.String(64))
    friend_code = db.Column(db.String(9), db.ForeignKey('group_members.friend_code'))

    def __init__(self, email, friend_code):
        self.email = email
        self.friend_code = friend_code

    def __repr__(self):
        return "<Members('%s', '%s')>" % (self.email, self.friend_code)
