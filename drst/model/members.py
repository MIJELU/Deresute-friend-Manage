from flask import current_app
from drst.database import db

class Members(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, auto_increment = True, ForeignKey("group_members.id")) #Syntax Error
    email = db.Column(db.String(100))
    friend_code = db.Column(db.Integer, primary_key = True)
    def __init__(self, email, friend_code):
        self.email = email
        self.friend_code = friend_code

    def __repr__(self):
        return "<Members('%s', '%d')>" % (self.email, self.friend_code)
