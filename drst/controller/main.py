from flask import request, redirect, render_template, session, escape
from drst.blueprint import drst
#세션에 이메일, 친구코드
@drst.route("/")
def page_index():
    return render_template('index.html')

@drst.route("/g/new")
def page_new_group():
    return "new_group"

@drst.route("/g/list/<string:group_url>")
def page_group_list(group_url):
    page = request.args.get('page')
    if(page is None or not (page > 1)):
        page = 1
    return "group_list : " + group_url + "<br>Page : " + page
