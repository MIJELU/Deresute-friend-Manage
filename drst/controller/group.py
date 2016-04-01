from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst
import hashlib
import random
import string
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

def random_string(length, letters):
    return ''.join(random.choice(letters) for i in range(length))

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

            group_name = request.form.get('group_name').strip()
            if(len(group_name) < 2) :
                return "그룹 이름이 너무 짧아요!"
            group_url = request.form.get('group_url').strip()
            #만약 위에 게 중복되었다면, URL을 생성
            check_duplicate_group_url = db.session.query(groups.Groups).filter_by(group_url = group_url).first()
            while(check_duplicate_group_url != None):
                urlLength = 10
                urlLetters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-'
                group_url = random_string(urlLength, urlLetters)
                check_duplicate_group_url = db.session.query(groups.Groups).filter_by(group_url = group_url).first()

            post = group_members.Group_members(session['friend_code'], group_url)
            post2 = groups.Groups(group_url, group_name)
            db.session.add(post)
            db.session.add(post2)
            db.session.commit()
            return redirect(url_for('drst.page_group_list', group_url=group_url))
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
        isJoin = False
        if 'friend_code' in session:
            isLogin = True
            email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
            user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash, "group" : group_url};
            isJoin = group_members.Group_members.query.filter_by(friend_code=session['friend_code'], group_url = group_url).first()
            if(isJoin):
                isJoin = True
        return render_template('viewer.html', user=user, group_info=group_info, group_members=group_members_info, isLogin=isLogin, isJoin=isJoin)
    else:
        if 'friend_code' in session:
            from drst.database import db
            from drst.model import members
            from drst.model import groups
            from drst.model import group_members
            #가입처리 루틴
            #이미 가입한 경우 탈퇴
            #탈퇴가 아니면 가입
            #카운트늘려주기 필요하다.
            group_isJoin = group_members.Group_members.query.filter_by(friend_code=session['friend_code'], group_url = group_url).first()
            if(group_isJoin):
                #탈퇴
                db.session.delete(group_isJoin)
                #회원수 1감소
                groupInfo = groups.Groups.query.filter_by(group_url=group_url).first()
                members = groupInfo.number_of_members - 1;
                groupInfo.number_of_members = members;
                db.session.commit()
                return redirect(request.referrer)
            else:
                #가입
                post = group_members.Group_members(session['friend_code'], group_url)
                groupInfo = groups.Groups.query.filter_by(group_url=group_url).first()
                members = groupInfo.number_of_members + 1;
                groupInfo.number_of_members = members;
                db.session.add(post)
                db.session.commit()
                return redirect(request.referrer)
        else:
            return redirect(url_for('drst.page_login', redirect="/g/list"+group_url))
