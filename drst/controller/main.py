from flask import request, redirect, render_template
from drst.blueprint import drst

@drst.route("/")
def page_index():
    return render_template('index.html')

@drst.route("/login")
def login():
    return "login"

@drst.route("/logout")
def logout():
    return "logout"

@drst.route("/join")
def join():
    return "join"

@drst.route("/g/new")
def new_group():
    return "new_group"

@drst.route("/g/list/<string:group_url>")
def group_list(group_url):
    page = request.args.get('page')
    if(page is None or page < 1):
        page = 1
    return "group_list : " + group_url + "<br>Page : " + request.args.get('page')
