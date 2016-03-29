from flask import request, redirect, render_template, session, escape, url_for, Response
from drst.blueprint import drst
from validate_email import validate_email
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


@drst.route("/api/v1.1/check", methods=['GET', 'POST'])
def api_checkMember():
    user_input = request.form.get('user_input')
    #의미없는 값 입력시
    if(user_input is None):
        resp = Response(response=json.dumps({'isValid': False}),
                    status=200,
                    mimetype="application/json")
        return resp

    #메일주소인지 체크
    is_mail = validate_email(request.form.get('user_input'))
    if(is_mail):
        ret = json.dumps({'isValid': is_mail, 'type': 'email'})
        resp = Response(response=ret,
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
        #chkch.friend_code, name, level, prp, comment):
        strs = "friend code : " + chkch.friend_code + "<br>"
        strs += "name : " + chkch.name + "<br>"
        strs += "level : " + str(chkch.level) + "<br>"
        strs += "prp : " + str(chkch.prp) + "<br>"
        strs += "comment : " + chkch.comment + "<br>"
        return strs


    req = Request("https://deresute.me/"+ user_input.strip() +"/json")
    try:
        response = urlopen(req)
    except HTTPError as e:
        isValid = False
    except URLError as e:
        isValid = False
    if(isValid is True):
        ret = json.dumps({'isValid': True, 'type': 'friend_code'})
        resp = Response(response=ret,
                        status=200,
                        mimetype="application/json")

        #친구정보 캐시에 넣고가~~
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
        resp = Response(response=json.dumps({'isValid': False}),
                        status=200,
                        mimetype="application/json")
        return resp
