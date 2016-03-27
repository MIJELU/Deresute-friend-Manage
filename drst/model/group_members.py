from flask import current_app
from drst.database import db

class Group_members(db.Model):
    __tablename__ = "group_members"

    friend_code = db.Column(db.String(9), primary_key=True)
    group_url = db.Column(db.String(128))

    def __init__(self, friend_code, group_url):
        self.friend_code = friend_code
        self.group_url = group_url

    def __repr__(self):
        return "<Group Members('%s', '%s')>" % (self.group_url, self.friend_code)
