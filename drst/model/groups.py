from flask import current_app
from drst.database import db

class Groups(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.Integer, auto_increment = True, ForeignKey("group_members.id"))
    group_url = db.Column(db.String(30), primary_key = True)
    generated_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    def __init__(self, group_url):
        self.group_url = group_url

    def __repr__(self):
        return "<Groups('%s', '%s')>" % (self.group_url, str(self.generated_time))
