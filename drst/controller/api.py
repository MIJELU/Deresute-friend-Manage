from flask import request, redirect, render_template, session, escape, url_for
from flask import Flask, jsonify, Response, send_file
from drst.blueprint import drst
from validate_email import validate_email
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import os.path
import datetime
import urllib.request

@drst.route('/api/v1.2/test0/<string:eval_friend_or_email>')
def test_abcd(eval_friend_or_email):
    return get_friend_code_by_email(eval_friend_or_email)

#완성
def is_exist_user(eval_friend_or_email):
    ret_error_invalid =  jsonify({'error' : True, 'description' : 'invalid input'})
    ret_not_exist_user =  jsonify({'isexist' : False, 'description' : 'User doesn\'t exist'})
    ret_exist_user =  jsonify({'isexist' : True, 'description' : 'User exists'})
    from drst.database import db
    from drst.model import friend_code_cache
    from drst.model import members
    inVal = eval_friend_or_email
    if inVal is not None:
        inVal = inVal.strip()
    else:
        return ret_error_invalid
    if validate_email(inVal):
        member_info = db.session.query(members.Members).\
        filter_by(email = inVal).first()
        if(member_info):
            return ret_exist_user
        return ret_not_exist_user
    if(len(inVal) != 9) :
        return ret_error_invalid
    try:
        test99 = int(inVal)
    except ValueError:
        return ret_error_invalid
    member_info = db.session.query(friend_code_cache.Friend_code_cache).\
    filter_by(friend_code = inVal).first()
    if(member_info):
        return ret_exist_user
    return ret_not_exist_user

#미완
def get_friend_code_by_email(email):
    ret_not_exist_user =  jsonify({'error' : True, 'description' : 'User doesn\'t exist'})
    ret_exist_user =  jsonify({'friend_code' : '000000000', 'email' : email, 'description' : 'User exists'})
    from drst.database import db
    from drst.model import friend_code_cache
    from drst.model import members
    inVal = email
    if inVal is not None:
        inVal = inVal.strip()
        ret_exist_user.email = inVal
    else:
        return ret_not_exist_user
    print("출력")
    recv = json.loads(is_exist_user(email).data.decode('utf8'))
    print(recv)
    if ('error' in recv):
        return ret_not_exist_user
    if (recv['isexist'] is True):
        member_info = db.session.query(members.Members).\
        filter_by(email = inVal).first()
        member_info = db.session.query(friend_code_cache.Friend_code_cache).\
        filter_by(friend_code = member_info.friend_code).first()#reallocation
        ret_exist_user.friend_code = member_info.friend_code #json 화에 문제 있음
        print("member_info.friend_code")
        print(member_info.friend_code)
        return ret_exist_user
    else :
        return ret_not_exist_user

def get_email_by_friend_code(friend_code):
    from drst.model import members
    inVal = friend_code
    if inVal is not None:
        inVal = inVal.strip()
    else:
        return "000000000"
    return False

def is_cached_user(eval_friend_or_email):
    #cached : True
    #Not cached || old (3 hours ago) : False
    #3시간 초과인 경우에는 캐시되지 않은 것으로 간주한다 (추가)
    from drst.database import db
    from drst.model import friend_code_cache
    from drst.model import members
    inVal = eval_friend_or_email
    if inVal is not None:
        inVal = inVal.strip()
    else:
        return False

    #email validate
    if validate_email(inVal):
        #email -> 진짜 회원인 경우에만 있을 것이다. 회원 정보 테이블에서 해당하는 코드
        #불러오고 그게 캐시되었는지 본다. (last_modified 비교 필요)
        member_info = db.session.query(members.Members).\
        filter_by(email = inVal).first()
        if(member_info):
            member_info = db.session.query(friend_code_cache.Friend_code_cache).\
            filter_by(friend_code = member_info.friend_code).first()#reallocation
            now = datetime.datetime.now()
            diff = (now - member_info.last_modified).total_seconds() / (3600*3)
            if (diff > 3.0):
                return False
            else:
                return True
        else:
            return False

    #code validate
    if(len(inVal) != 9) :
        return False
    try:
        test99 = int(inVal)
    except ValueError:
        return False
    member_info = db.session.query(friend_code_cache.Friend_code_cache).\
    filter_by(friend_code = inVal).first()
    if(member_info):
        now = datetime.datetime.now()
        diff = (now - member_info.last_modified).total_seconds() / 86400
        if (diff > 3.0):
            return False
        else:
            return True
    return False

def cache_user(eval_friend_or_email):
    #유저를 (재)캐시한다. (내부적으로 시간체크 모듈이 있다. 아무렇게나 호출해도 서버부하에 무방)
    #유효한 캐시가 이미 있는 경우 아무것도 안 한다.
    if (is_cached_user(eval_friend_or_email)):
        return
    #deresute me 에 요청하여 데이터베이스와 파일들을 갱신한다.
    #데이터베이스에 무언가 있을 경우 -> 파일과 데이터를 새로 불러온다. ( png, json )
    #데이터베이스가 비었을 경우 -> 파일과 데이터를 새로 불러온다. ( png, json )
    #다른 점은 그것이 db가 삽입인지 수정인지 밖에 없다. 그것을 체크할 수 있는 방법은
    #이메일과 유저코드를 둘다 매칭하는 것이다.

    #친구코드일 시 그냥 캐시 가능, 이메일일시 회원만 캐시 가능
    if (is_exist_user(eval_friend_or_email)):
        a=3
    else:
        a=4
    return

def check_friend_code(eval_friend_code):
    #회원가입 여부와는 상관없이 정당한 친구코드인지를 알아보자
    #캐시되었으면 옳다.
    #캐시되지 않았을 경우, 기본 체크(9글자 정수)를 하고 난 뒤 deresute.me에 요청을 보낸다
    #cache데이터베이스에 갱신한다. 그리고 이것이 옳은 결과인지를 리턴한다 (T, F)
    from drst.database import db
    from drst.model import friend_code_cache
    from drst.model import members
    #기본적인 유효성 검증
    inVal = eval_friend_or_email
    if inVal is not None:
        inVal = inVal.strip()
    else:
        return False
    if (is_cached_user(inVal)):
        return True
    if(len(inVal) != 9) :
        return False
    try:
        test99 = int(inVal)
    except ValueError:
        return False

    #캐시되지 않은 코드에 대하여 deresute.me 에 요청을 보낸다.
    #이 요청 보내기 전에 꼭 failure List 확인 후 3시간 이하의 요청에 대해서는 무시한다.
    #요청해서 api_error 같은거 뜨면 failure List를 갱신하거나 등록한다.
    #요청했는데 있으면 캐시뜬다. 그리고 failure List에서 제거한다.(있다면, 확률 매우 낮음)


@drst.route('/api/v1.2/producer/<string:friend_code>')
def api_get_producer_status_v2(friend_code):
    return "producer Info Picture / JSON"

@drst.route('/api/v1.2/smartLogin/<string:friend_or_email>')
def api_smart_login(friend_or_email):
    return "smart_login"
