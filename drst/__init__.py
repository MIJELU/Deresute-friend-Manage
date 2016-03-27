from flask import Flask
from drst.database import DBManager
from drst.blueprint import drst
from drst.controller import *

def create_app():
    #App Init
    app = Flask(__name__)

    #DB Init
    DBManager.init(app)

    #청사진 등록
    app.register_blueprint(drst)
    return app
