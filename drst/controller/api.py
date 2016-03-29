from flask import request, redirect, render_template, session, escape, url_for
from drst.blueprint import drst
from validate_email import validate_email
import json

@drst.route("/api/v1.0/check", methods=['GET', 'POST'])
def api_checkMember():
    #isvalid : true, false
    #type : email, friend_code
    #is_mail = validate_email(request.form.get('user_input'))
    #is_friend_code = True
    isValid = False
    #if(is_mail or is_friend_code):
    #    isValid=True
    return json.dumps({'isValid': isValid, 'type': 'email'})
