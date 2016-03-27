from flask import current_app
from drst.database import db

class Groups(db.Model):
    __tablename__ = "groups"

    group_url = db.Column(db.String(128), primary_key=True)
    group_name = db.Column(db.String(128))
    generated_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    number_of_members = db.Column(db.Integer)

    def __init__(self, group_url, group_name):
        self.group_url = group_url
        self.group_name = group_name
        self.number_of_members = 1

    def __repr__(self):
        return ""
