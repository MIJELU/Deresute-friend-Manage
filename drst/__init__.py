from flask import Flask
from drst.database import DBManager
from drst.blueprint import drst
from drst.controller import *

def create_app():
    #App Init
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./drst.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True


    #DB Init
    DBManager.init(app)
    with app.app_context():
        from drst.model import initModels
        initModels()
    DBManager.init_db()

    #청사진 등록
    app.register_blueprint(drst)
    return app
