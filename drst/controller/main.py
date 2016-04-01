from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst
import hashlib

@drst.route("/")
def page_index():
    isLogin = False
    user = {}
    targetGroup = request.args.get("targetGroupssid")
    if(targetGroup):
        print("타겟의등록" + targetGroup)
        session['targetGroup'] = targetGroup
    if 'friend_code' in session:
        isLogin = True
        email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
        user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
    return render_template('index.html', user=user, isLogin=isLogin)
