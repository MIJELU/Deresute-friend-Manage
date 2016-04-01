from flask import request, redirect, render_template, session, escape, url_for
from drst.blueprint import drst
import hashlib
import random
import string
#세션에 이메일, 친구코드
def random_string(length, letters):
    return ''.join(random.choice(letters) for i in range(length))


@drst.route("/")
def page_index():
    isLogin = False
    user = {}
    if 'friend_code' in session:
        isLogin = True
        email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
        user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
    return render_template('index.html', user=user, isLogin=isLogin)

@drst.route("/g/new", methods=['GET', 'POST'])
def page_new_group():
    user = {}
    if request.method == 'GET':
        if 'friend_code' in session:
            #임의 URL을 생성
            urlLength = 10
            urlLetters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-'
            rnd_key = random_string(urlLength, urlLetters)
            email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
            user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
            return render_template('new_group_form.html', user=user, genurl=rnd_key)
        else:
            return redirect(url_for('drst.page_login', redirect="/g/new"))
    else:
        if 'friend_code' in session:
            #그룹의 생성을 처리한다.
            from drst.database import db
            from drst.model import groups
            from drst.model import group_members
            #이때쯤 해줘야 none Type 에러가 나지 않는다.
            #self, friend_code, group_name, group_url):
            post = group_members.Group_members(session['friend_code'], request.form.get('group_url'))
            post2 = groups.Groups(request.form.get('group_url'), request.form.get('group_name'))
            db.session.add(post)
            db.session.add(post2)
            db.session.commit()
            return redirect(url_for('drst.page_group_list', group_url=request.form.get('group_url')))
        else:
            return redirect(url_for('drst.page_login', redirect="/g/new"))

@drst.route("/g/list/<string:group_url>", methods=['GET', 'POST'])
def page_group_list(group_url):
    if request.method == 'GET':
        from drst.database import db
        from drst.model import members
        from drst.model import groups
        from drst.model import group_members
        #articles=weblog.Weblog.query.all()
        group_info = groups.Groups.query.filter_by(group_url = group_url).first()
        #group_members = group_members.Group_members.query.filter_by(group_url = group_url).all()
        group_members_info = members.Members.query.join(group_members.Group_members).filter_by(friend_code = group_members.Group_members.friend_code, group_url = group_url).all()
        #조인한다.
        #그룹 멤버스의 그룹 URL이 현재 URL에 맞는 경우에만

        #유저 개인정보에 관련된 내용
        user = {}
        isLogin = False
        if 'friend_code' in session:
            isLogin = True
            email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
            user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash, "group" : group_url};
        return render_template('viewer.html', user=user, group_info=group_info, group_members=group_members_info, isLogin=isLogin)
    else:
        if 'friend_code' in session:
            dummy = 3#가입처리
            return "가입되었습니다"
        else:
            return redirect(url_for('drst.page_login', redirect="/g/list"+group_url))
