from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst
import hashlib
@drst.route("/")
def page_introduce():
    return render_template('introduce.html')
    
@drst.route("/start")
def page_index():
    isLogin = False
    user = {}
    groups2 = {}
    targetGroup = request.args.get("targetGroupssid")
    if(targetGroup):
        print("타겟의등록" + targetGroup)
        session['targetGroup'] = targetGroup
    if 'friend_code' in session:
        isLogin = True
        email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
        user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
        from drst.database import db
        from drst.model import group_members
        from drst.model import groups
        from drst.model import members
        '''#group_members_info =
        members.Members.query.join
        (group_members.Group_members)
        .filter_by(friend_code = group_members.Group_members.friend_code,
         group_url = group_url).all()
        '''
        groups2 = group_members.Group_members.query.filter_by(friend_code=session['friend_code']).join(groups.Groups).filter_by(group_url = groups.Groups.group_url).all()
    return render_template('index.html', user=user, isLogin=isLogin, groups=groups2)
