from flask import current_app
from drst.database import db

class Friend_code_cache(db.Model):
    __tablename__ = "friend_code_cache"

    friend_code = db.Column(db.String(9), primary_key=True)
    isValid = db.Column(db.Boolean, default=True) #유효한 친구코드인지 체크 (API 1.2 추가)
    name = db.Column(db.String(256))
    level = db.Column(db.Integer)
    prp = db.Column(db.Integer)
    comment = db.Column(db.String(512))
    last_modified = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __init__(self, friend_code, name, level, prp, comment, last_modified):
        self.friend_code = friend_code
        self.name = name
        self.level = level
        self.prp = prp
        self.comment = comment
        self.last_modified = last_modified

    def __repr__(self):
        return "<cache('%s', '%s')>" % (self.name, self.comment)
