from flask import current_app
from drst.database import db

class Group_members(db.Model):
    __tablename__ = "friend_code_failure"

    nid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    friend_code = db.Column(db.String(9))
    renew = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, friend_code):
        self.friend_code = friend_code

    def __repr__(self):
        return "<Fail('%s', '%s')>" % (self.friend_code)
