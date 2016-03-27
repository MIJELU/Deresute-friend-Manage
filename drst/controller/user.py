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
        return render_template('login_form.html', redirect_url=redirect_url) #아직은 그냥 슬래시
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
        return redirect(url_for('drst.page_login')) #로그인 실패

@drst.route("/logout")
def page_logout():
    session.pop('email')
    session.pop('friend_code')
    return redirect(url_for('drst.page_index'))

@drst.route("/join", methods=['GET', 'POST'])
def page_join():
    if request.method == 'GET':
        if 'friend_code' in session:
            return redirect(url_for('page_index'))
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

"""
<input type="number" name="friend_code" class="form-control" maxlength="9" placeholder="ゲームIDを入力" onkeypress='return event.charCode >= 48 && event.charCode <= 57' autofocus>
<input type="email" name="email" class="form-control" placeholder="이메일 주소">
<input type="password" name="password_plain" class="form-control" placeholder="등록 비밀번호">
<input type="password" name="password_plain_re" class="form-control" placeholder="비밀번호 재입력">
<input type="submit" value="회원가입" class="form-control">
"""
