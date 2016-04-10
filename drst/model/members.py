from flask import current_app
from drst.database import db

class Members(db.Model):
    __tablename__ = "members"

    nid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.String(128))
    password = db.Column(db.String(64))
    friend_code = db.Column(db.String(9), db.ForeignKey('group_members.friend_code'))

    def __init__(self, email, friend_code, password):
        self.email = email
        self.friend_code = friend_code
        self.password = password

    def __repr__(self):
        return "<Members('%s', '%s')>" % (self.email, self.friend_code)
