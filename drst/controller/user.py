from flask import request, redirect, render_template, session, escape
from drst.blueprint import drst
#세션에 이메일, 친구코드
#if 'email' in session:
#if 'friend_code' in session:
@drst.route("/login", methods=['GET', 'POST'])
def page_login():
    if 'friend_code' in session:
        return redirect(url_for('page_index'))
    return render_template('login_form.html')

@drst.route("/logout")
def page_logout():
    session.pop('', )
    return "logout"

@drst.route("/join")
def page_join():
    return "join"
