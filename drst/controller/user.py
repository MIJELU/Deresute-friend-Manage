from flask import request, redirect, render_template, session, escape, url_for
from drst.blueprint import drst

import hashlib

#세션에 이메일, 친구코드
#if 'email' in session:
#if 'friend_code' in session:


@drst.route("/login", methods=['GET', 'POST'])
def page_login():
    if request.method == 'GET':
        if 'friend_code' in session:
            return redirect(url_for('drst.page_index'))
        redirect_url = request.args.get('redirect')
        if(redirect_url is None):
            redirect_url = "/"
        fill = request.args.get('fill')
        login_type = request.args.get('type')
        if(login_type is None):
            return "로그인 과정 중 문제가 발생한 것 같습니다. 뒤로가기를 누르지 말고 (<a href="/">메인페이지</a>)에서 다시 시도해 주세요 [-2] Invalid Arguments"
        if(fill is not None):
            print("호출")
            return render_template('login_form.html', redirect_url=redirect_url, fill=fill, login_type=login_type)
        else:
            return render_template('login_form.html', redirect_url=redirect_url, fill=None, login_type=login_type)
    else:
        from drst.database import db
        from drst.model import members
        #from drst.model import groups
        #from drst.model import group_members
        #이때쯤 해줘야 none Type 에러가 나지 않는다.
        friend_code = request.form.get('friend_code')
        password_plain = request.form.get('password_plain')
        password_plain = password_plain.encode('utf-8')
        password_sha256 = hashlib.sha256(password_plain).hexdigest()
        result = db.session.query(members.Members).filter_by(friend_code = friend_code).first()
        if(result != None):
            print("로그인 시도 ID : " + result.friend_code)
            if(password_sha256 == result.password):
                #세션에 등록
                session['email'] = result.email
                session['friend_code'] = result.friend_code
                return redirect(request.form.get('redirect_url')) #로그인 처리
        #return redirect(url_for('drst.page_login')) #로그인 실패
        return render_template('login_form.html', redirect_url=redirect_url, fill=fill, login_type=login_type)

@drst.route("/logout")
def page_logout():
    session.pop('email')
    session.pop('friend_code')
    return redirect(url_for('drst.page_index'))

@drst.route("/join", methods=['GET', 'POST'])
def page_join():
    if request.method == 'GET':
        if 'friend_code' in session:
            return redirect(url_for('drst.page_index'))
        return render_template('join_form.html')
    else:
        from drst.database import db
        from drst.model import members
        #이때쯤 해줘야 none Type 에러가 나지 않는다.
        password_plain = request.form.get('password_plain')
        password_plain = password_plain.encode('utf-8')
        password_sha256 = hashlib.sha256(password_plain).hexdigest()
        post = members.Members(request.form.get('email'), request.form.get('friend_code'), password_sha256)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('drst.page_index'))
