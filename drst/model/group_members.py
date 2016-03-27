from flask import current_app
from drst.database import db

class Group_members(db.Model):
    __tablename__ = "group_members"

    id = db.Column(db.Integer, auto_increment = True)
    group_id = db.Column(db.Integer, primary_key = True)
    member_id = db.Column(db.Integer)
    def __init__(self, group_id, member_id):
        self.group_id = group_id
        self.member_id = member_id

    def __repr__(self):
        return "<Group_members('%d', '%d')>" % (self.group_id, self.member_id)
