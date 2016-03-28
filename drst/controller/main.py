from flask import request, redirect, render_template, session, escape, url_for
from drst.blueprint import drst
import hashlib
#세션에 이메일, 친구코드

def print_tree(rows):
    def get_level_diff(row1, row2):
        """ Returns tuple: (from, to) of different item positions.  """
        if row1 is None: # first row handling
            return (0, len(row2))
        assert len(row1) == len(row2)
        for col in range(len(row1)):
            if row1[col] != row2[col]:
                return (col, len(row2))
        assert False, "should not have duplicates"

    prev_row = None
    for row in rows:
        level = get_level_diff(prev_row, row)
        for l in range(*level):
            print (2 * l * " ", row[l])
            prev_row = row

@drst.route("/")
def page_index():
    if 'friend_code' in session:
        email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
        user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
        return render_template('index.html', user=user)
    else:
        return render_template('index.html', user=False)

@drst.route("/g/new", methods=['GET', 'POST'])
def page_new_group():
    user = {}
    if request.method == 'GET':
        if 'friend_code' in session:
            email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
            user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash};
            return render_template('new_group_form.html', user=user)
        else:
            return redirect(url_for('drst.page_login', redirect="/g/new"))
    else:
        if 'friend_code' in session:
            #그룹의 생성을 처리한다.
            from drst.database import db
            from drst.model import groups
            from drst.model import group_members
            #이때쯤 해줘야 none Type 에러가 나지 않는다.
            #self, friend_code, group_name, group_url):
            post = group_members.Group_members(session['friend_code'], request.form.get('group_url'))
            post2 = groups.Groups(request.form.get('group_url'), request.form.get('group_name'))
            db.session.add(post)
            db.session.add(post2)
            db.session.commit()
            return redirect(url_for('drst.page_group_list', group_url=request.form.get('group_url')))
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
        group_members = group_members.Group_members.query.join(members.Members).filter_by(friend_code = members.Members.friend_code).all()
        #이 조인문에 문제가 있다. (조인이 안 됨)

        #유저 개인정보에 관련된 내용
        user = {}
        if 'friend_code' in session:
            email_hash = hashlib.md5(session['email'].encode('utf-8')).hexdigest()
            user = {"friend_code" : session['friend_code'], "email" : session['email'], "email_hash" : email_hash, "group" : group_url};
        return render_template('viewer.html', user=user, group_info=group_info, group_members=group_members)
    else:
        if 'friend_code' in session:
            dummy = 3#가입처리
            return "가입되었습니다"
        else:
            return redirect(url_for('drst.page_login', redirect="/g/list"+group_url))
