from flask import request, redirect, render_template, session, escape, url_for, Response, send_file
from drst.blueprint import drst
from validate_email import validate_email
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os.path
import datetime
import urllib.request

@drst.route("/api/v1.1/producer/<string:friend_code>" ,methods=['GET'])
def api_get_producer_status(friend_code):
    '''타입 : 이미지와 json
    #캐시 생성 이슈
    #friend_code_cache와 타임스탬프가 1시간 이상 차이 나면 다시 만들어 준다
    #그리고 friend_code_cache의 타임스탬프를 최신 정보로 고친다.

    a = dt.datetime(2013,12,30,23,59,59)
    b = dt.datetime(2013,12,31,23,59,59)

    (b-a).total_seconds()
    '''
    from drst.database import db
    from drst.model import friend_code_cache

    #1. 지금 타임스탬프 구하기
    now = datetime.datetime.now()
    #2. db에 저장되어 있는 타임스탬프 구하기
    dbtime = db.session.query(friend_code_cache.Friend_code_cache).filter_by(friend_code = friend_code).first()
    print(dbtime)
    dbtime2 = ""
    diff = 9999.99
    if(dbtime):
        dbtime2 = dbtime.last_modified
        diff = (now-dbtime2).total_seconds() / 86400 #시간

    if(diff < 1.0):
        return send_file("./static/i/user/"+str(friend_code)+".png", mimetype='image/png')
    else:
        #파일을 새로 복사하고 -> db에 갱신작업을 해야한다.
        #이미지파일 복사 및 새로운 개인정보 저장
        print("리소스 접근")
        req = Request("https://deresute.me/"+ str(friend_code) +"/json")
        try:
            response = urlopen(req)
        except HTTPError as e:
            return "Error"
        except URLError as e:
            return "Error"
        #친구정보 캐시 갱신
        encoding = response.info().get_content_charset('utf8')
        data = json.loads(response.read().decode(encoding))
        if(dbtime):
            dbtime.name = data['name']
            dbtime.level = data['level']
            dbtime.prp = data['prp']
            dbtime.comment = data['comment']
            dbtime.last_modified = now #마지막 캐시시간 바꿈
        else:
            post = friend_code_cache.Friend_code_cache(data['id'], data['name'], data['level'], data['prp'], data['comment'], now)
            db.session.add(post)
        urllib.request.urlretrieve("https://deresute.me/"+str(data['id'])+"/medium", "drst/static/i/user/"+str(data['id'])+".png")
        db.session.commit()
        return send_file("./static/i/user/"+str(friend_code)+".png", mimetype='image/png')

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
        post = friend_code_cache.Friend_code_cache(data['id'], data['name'], data['level'], data['prp'], data['comment'], datetime.datetime.now())
        #여기서 잠깐, 이미지 파일을 본떠야 한다.
        urllib.request.urlretrieve("https://deresute.me/"+str(data['id'])+"/medium", "drst/static/i/user/"+str(data['id'])+".png")

        db.session.add(post)
        db.session.commit()
        return resp
    else:
        resp = Response(response=json.dumps({'isValid': False, 'user_input':user_input.strip()}),
                        status=200,
                        mimetype="application/json")
        return resp
