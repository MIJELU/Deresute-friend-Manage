from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst

import hashlib
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

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
        return redirect(request.referrer) #go back your page

@drst.route("/logout")
def page_logout():
    if 'email' in session:
        session.pop('email')
    if 'friend_code' in session:
        session.pop('friend_code')
    return redirect(url_for('drst.page_index'))

@drst.route("/join", methods=['GET', 'POST'])
def page_join():
    if request.method == 'GET':
        if 'friend_code' in session:
            return redirect(url_for('drst.page_index'))

        fill = request.args.get('fill')
        fill_type = request.args.get('type')
        if(fill_type is not None):
            return render_template('join_form.html', fill=fill, fill_type=fill_type)
        else:
            return redirect(url_for('drst.page_index'))
    else:
        from drst.database import db
        from drst.model import members
        #이때쯤 해줘야 none Type 에러가 나지 않는다.
        #꼭 친구코드와 이메일 주소의 중복체크가 필요 (유효성은 검증하지 않은, (전단계 의존) -> 가벼운 방식)
        #result = db.session.query(members.Members).filter_by(friend_code = friend_code).first()
        email = request.form.get('email').strip()
        friend_code = request.form.get('friend_code').strip()
        password_plain = request.form.get('password_plain').strip()
        password_plain = password_plain.encode('utf-8')
        password_plain_re = request.form.get('password_plain_re').strip()
        password_plain_re = password_plain_re.encode('utf-8')
        password_sha256 = hashlib.sha256(password_plain).hexdigest()

        check_duplicate_friend_code = db.session.query(members.Members).filter_by(friend_code = friend_code).first()
        check_duplicate_email = db.session.query(members.Members).filter_by(email = email).first()

        if((check_duplicate_email != None) or (check_duplicate_friend_code != None)):
            return "죄송하지만 중복회원이 있습니다.. 로그인하세요"

        if(password_plain != password_plain_re):
            return "서로 입력한 패스워드가 상이합니다."

        #친구 코드 유효성 검사 (issue :Duplicated Code)
            #9자리 숫자인지 체크
        if(len(friend_code) == 9):
            try:
                test99 = int(friend_code.strip())
            except ValueError:
                return "죄송하지만 친구코드가 유효하지 않는 것 같습니다."
        else:
            return "죄송하지만 친구코드의 자리수가 맞지 않습니다. 9자리의 수를 입력하세요"

        #캐시에 있는 데이터베이스에 접근 (있다면 성공으로 간주.)
        from drst.model.friend_code_cache import Friend_code_cache
        chkch = db.session.query(Friend_code_cache).filter_by(friend_code = friend_code).first()
        if chkch == None: #캐시에 있으면 그냥 넘어가고 없으면 캐시에 저장하는 로직
            #캐시에 없으면 직접 deresute.me에 접근. (캐시에 저장)
            response = ""
            isValid = True
            print("리소스 접근")
            req = Request("https://deresute.me/"+ friend_code +"/json")
            try:
                response = urlopen(req)
            except HTTPError as e:
                return "회원 검증 과정에 문제가 있습니다. (404)"
            except URLError as e:
                return "회원 검증 과정에 문제가 있습니다. (404)"
            #친구정보 캐시에 넣기
            from drst.model import friend_code_cache
            encoding = response.info().get_content_charset('utf8')
            data = json.loads(response.read().decode(encoding))
            print(data['prp'])
            post = friend_code_cache.Friend_code_cache(data['id'], data['name'], data['level'], data['prp'], data['comment'])
            db.session.add(post)
            db.session.commit()
            ###############

        post = members.Members(email, friend_code, password_sha256)
        db.session.add(post)
        db.session.commit()
        session['email'] = email
        session['friend_code'] = friend_code
        return redirect(url_for('drst.page_index'))
