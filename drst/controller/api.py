from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst
from validate_email import validate_email
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

@drst.route("/api/v1.1/checkEmail" ,methods=['POST'])
def api_checkEmail():
    return ""

@drst.route("/api/v1.1/checkJoin", methods=['POST'])
def api_checkJoin():
    #지정된 이메일이나 친구코드가 이미 가입되어있는지 아닌지 조회
    #가입된 이메일이면 친구코드로 컨버팅해서 로그인으로 넘겨줘야 겠다 ㅡㅡ (너무 복잡해용 ㅠㅠ)
    from drst.database import db
    from drst.model import members
    if(not(request.form.get('type') and request.form.get('user_input'))):
        return "error"
    utype = request.form.get('type').strip()
    user_input = request.form.get('user_input').strip()
    result = ""
    ret = ""
    resp = ""
    if(utype == 'friend_code'):
        result = db.session.query(members.Members).filter_by(friend_code = user_input).first()
    else:
        result = db.session.query(members.Members).filter_by(email = user_input).first()

    if (result):
        ret = json.dumps({'isJoin': True, 'type':'friend_code', 'friend_code': result.friend_code})
        resp = Response(response=ret,
                        status=200,
                        mimetype="application/json")
    else: #회원가입으로 가라..
        if(utype=='friend_code'):
            ret = json.dumps({'isJoin': False, 'type':'friend_code','friend_code': user_input})
            resp = Response(response=ret,
                            status=200,
                            mimetype="application/json")
        else:
            ret = json.dumps({'isJoin': False, 'type':'email','email': user_input})
            resp = Response(response=ret,
                            status=200,
                            mimetype="application/json")
    return resp






@drst.route("/api/v1.1/checkValidValue", methods=['POST'])
def api_checkMember():
    user_input = request.form.get('user_input')
    #의미없는 값 입력시
    print("시작")
    if(user_input is None):
        resp = Response(response=json.dumps({'isValid': False, 'user_input':user_input.strip()}),
                    status=200,
                    mimetype="application/json")
        return resp

    #메일주소인지 체크
    is_mail = validate_email(request.form.get('user_input'))
    if(is_mail):
        ret = json.dumps({'isValid': is_mail, 'type': 'email', 'user_input':user_input.strip()})
        resp = Response(response=ret,
                        status=200,
                        mimetype="application/json")
        return resp
    else:
        #9자리 숫자인지 체크
        if(len(user_input.strip()) == 9):
            try:
                test99 = int(user_input.strip())
            except ValueError:
                resp = Response(response=json.dumps({'isValid': False, 'user_input':user_input.strip()}),
                                status=200,
                                mimetype="application/json")
                return resp
        else:
            resp = Response(response=json.dumps({'isValid': False, 'user_input':user_input.strip()}),
                            status=200,
                            mimetype="application/json")
            return resp


    #친구코드인지 체크 (캐시 데이터베이스 필요)
    isValid = True
    is_friend_code = False
    response = ""

    from drst.database import db
    from drst.model.friend_code_cache import Friend_code_cache
    chkch = db.session.query(Friend_code_cache).filter_by(friend_code = user_input.strip()).first()
    if chkch != None:
        ret = json.dumps({'isValid': True, 'type': 'friend_code', 'user_input':user_input.strip()})
        resp = Response(response=ret,
                        status=200,
                        mimetype="application/json")
        return resp
    print("리소스 접근")
    req = Request("https://deresute.me/"+ user_input.strip() +"/json")
    try:
        response = urlopen(req)
    except HTTPError as e:
        isValid = False
    except URLError as e:
        isValid = False
    if(isValid is True):
        ret = json.dumps({'isValid': True, 'type': 'friend_code', 'user_input':user_input.strip()})
        resp = Response(response=ret,
                        status=200,
                        mimetype="application/json")
        #친구정보 캐시에넣기
        from drst.database import db
        from drst.model import friend_code_cache
        encoding = response.info().get_content_charset('utf8')
        data = json.loads(response.read().decode(encoding))
        print(data['prp'])
        post = friend_code_cache.Friend_code_cache(data['id'], data['name'], data['level'], data['prp'], data['comment'])
        db.session.add(post)
        db.session.commit()
        return resp
    else:
        resp = Response(response=json.dumps({'isValid': False, 'user_input':user_input.strip()}),
                        status=200,
                        mimetype="application/json")
        return resp
