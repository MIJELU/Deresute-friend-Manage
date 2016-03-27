from flask import request, redirect, render_template, session, escape, url_for
from drst.blueprint import drst
import hashlib
#세션에 이메일, 친구코드
@drst.route("/")
def page_index():
    if 'friend_code' in session:
        email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
        user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
        print(user)
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=False)

@drst.route("/g/new")
def page_new_group():
    return "new_group"

@drst.route("/g/list/<string:group_url>")
def page_group_list(group_url):
    page = request.args.get('page')
    if(page is None or not (page > 1)):
        page = 1
    return "group_list : " + group_url + "<br>Page : " + page
