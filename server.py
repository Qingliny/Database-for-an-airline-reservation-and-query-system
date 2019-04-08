#!/usr/bin/env python2.7
import re
import datetime
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, abort, url_for, render_template, g, redirect, Response, session
import json
import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = ' '

DATABASEURI = " "
engine = create_engine(DATABASEURI)


@app.before_request
def before_request():
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback;
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def index():
    if session:
        session.clear()
    return render_template("index.html")
    # return render_template("template.html")


@app.route('/index2')
def index2():
    if session:
        print(session)
    return render_template("index2.html")


@app.route('/register')
def another():
    return render_template("register.html")


@app.route('/login')
def another2():
    return render_template("login.html")


@app.route('/update')
def another3():
    return render_template("update.html")


@app.route('/reviewAdd')
def another4():
    return render_template("reviewAdd.html")

@app.route('/keywordAdd')
def another5():
    return render_template("keywordAdd.html")


@app.route('/movieDisplay/<movieid>')
def displayMovie(movieid):
    try:
        if 'userid' not in session:
            return render_template("login.html")
        userid = session['userid']
        wishlistidl = g.conn.execute('''SELECT COUNT(*) FROM wishlist''')
        s = list(wishlistidl)
        # s='[(11L,)]'
        n = re.findall('(\d+L,)', str(s))
        if n != []:
            nS = re.findall('\d+', n[0])
            wishlistid = int(nS[0]) + 1
        else:
            print("emmm")
        t = str(datetime.datetime.now())
        modifiedtime = t[:10]
        g.conn.execute('''INSERT INTO wishlist (wishlistid,userid,movieid,modifiedtime) VALUES (%s,%s,%s,%s)''',
                       (wishlistid, userid, movieid, modifiedtime))
        wishlistidl.close()

        cursor = g.conn.execute(
            '''update movie set popularity = (Select (SUM(R.rating) + SUM(R.rating * R.liked))/(SUM(R.liked)+COUNT(R.rating))
							  From review R
							  Group By R.movieid
							  Having R.movieid = %s) where movieid = %s''',(movieid,movieid))
        user, review, wishlist, keyword= profile(userid)
        cursor.close()

        return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template("movieDisplay.html")


# ???????????
@app.route('/movieListID/<movieid>')
def movie3(movieid):
    try:
        movie, review, actor, director, keyword, region= movieinfo(movieid)
        return render_template("movieListID.html", m=movie, r=review, a=actor, d=director, k=keyword, rr=region)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('movieListGenre.html')


@app.route('/reviewDisplay/<reviewid>')
def displayReview(reviewid):
    cursor = g.conn.execute('''SELECT * FROM review WHERE reviewid=''' + str(reviewid))
    ss = cursor.fetchone()
    reviewid = str(reviewid)
    liked = str(ss[5] + 1)
    cursor.close()
    cursor = g.conn.execute('''UPDATE review SET liked=''' + liked + '''WHERE reviewid=''' + reviewid)
    cursor.close()
    session['liked'] = int(liked)
    context = reviewinfo(reviewid)
    return render_template("reviewDisplay.html", **context)


@app.route('/movieDisplay/reviewDisplay/<reviewid>')
def displayReview2(reviewid):
    cursor = g.conn.execute('''SELECT * FROM review WHERE reviewid=''' + str(reviewid))
    ss = cursor.fetchone()
    reviewid = str(reviewid)
    liked = str(ss[5] + 1)
    cursor.close()
    cursor = g.conn.execute('''UPDATE review SET liked=''' + liked + '''WHERE reviewid=''' + reviewid)
    cursor.close()
    context = reviewinfo(reviewid)
    return render_template("reviewDisplay.html", **context)


@app.route('/movieListID/reviewDisplay/<reviewid>')
def displayReview3(reviewid):
    cursor = g.conn.execute('''SELECT * FROM review WHERE reviewid=''' + str(reviewid))
    ss = cursor.fetchone()
    reviewid = str(reviewid)
    liked = str(ss[5] + 1)
    cursor.close()
    cursor = g.conn.execute('''UPDATE review SET liked=''' + liked + '''WHERE reviewid=''' + reviewid)
    cursor.close()
    context = reviewinfo(reviewid)
    return render_template("reviewDisplay.html", **context)


@app.route('/reviewAdd', methods=['POST'])
def review():
    comment = request.form['comment']
    rating = request.form['rating']
    try:
        if 'userid' not in session:
            return render_template("login.html")
        userid = session['userid']
        reviewidl = g.conn.execute('''SELECT COUNT(*) FROM review''')
        s = list(reviewidl)
        # s='[(11L,)]'
        n = re.findall('(\d+L,)', str(s))
        if n != []:
            nS = re.findall('\d+', n[0])
            reviewid = int(nS[0]) + 1
        else:
            print("emmmmm")
        liked = 0
        t = str(datetime.datetime.now())
        modifiedtime = t[:10]
        movieid = session['movieid']
        g.conn.execute(
            '''INSERT INTO review (reviewid,userid,movieid,comment,rating,liked,modifiedtime) VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (reviewid, userid, movieid, comment, rating, liked, modifiedtime))
        reviewidl.close()

        cursor = g.conn.execute(
            '''update movie set popularity = (Select (SUM(R.rating) + SUM(R.rating * R.liked))/(SUM(R.liked)+COUNT(R.rating))
							  From review R
							  Group By R.movieid
							  Having R.movieid = %s) where movieid = %s''',(movieid,movieid))
        user, review, wishlist, keyword= profile(userid)
        cursor.close()

        return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('reviewAdd.html')

@app.route('/keywordAdd', methods=['POST'])
def keyword():
    content = request.form['content']
    try:
        if 'userid' not in session:
            return render_template("login.html")
        userid = session['userid']
        reviewidl = g.conn.execute('''SELECT COUNT(*) FROM keyword''')
        s = list(reviewidl)
        # s='[(11L,)]'
        n = re.findall('(\d+L,)', str(s))
        if n != []:
            nS = re.findall('\d+', n[0])
            keywordid = int(nS[0]) + 1
        else:
            print("emmmmm")
        t = str(datetime.datetime.now())
        modifiedtime = t[:10]
        movieid = session['movieid']
        g.conn.execute(
            '''INSERT INTO keyword (keywordid,userid,movieid,content,modifiedtime) VALUES (%s,%s,%s,%s,%s)''',
            (keywordid, userid, movieid, content, modifiedtime))
        reviewidl.close()

        movie, review, actor, director, keyword, region= movieinfo(movieid)
        return render_template("movieListID.html", m=movie, r=review, a=actor, d=director, k=keyword, rr=region)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('keywordAdd.html')


@app.route('/update', methods=['POST'])
def update():
    description = request.form['description']
    gender = request.form['gender']
    imageurl = request.form['imageurl']
    password = request.form['password']
    nickname = request.form['nickname']
    age = request.form['age']
    email = request.form['email']
    userid = session['userid']
    if not password:
        password = session['password']
    if not nickname:
        nickname = session['nickname']
    if not age:
        age = session['age']
    if not gender:
        gender = session['gender']
    if not imageurl:
        imageurl = session['imageurl']
    if not email:
        email = session['email']
    if not description:
        description = session['description']
    try:
        cursor = g.conn.execute(
            '''UPDATE users SET userid=%s,password=%s,nickname=%s,age=%s,gender=%s,imageurl=%s,email=%s,description=%s WHERE userid=''' + str(
                userid), (userid, password, nickname, age, gender, imageurl, email, description))
        user, review, wishlist, keyword= profile(userid)
        cursor.close()
        return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('update.html')


@app.route('/profile')
def profile2():
    try:
        if 'userid' not in session:
            return render_template("login.html")
        userid = session['userid']
        user, review, wishlist, keyword= profile(userid)
        return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')


@app.route('/login', methods=['POST'])
def login():
    userid = request.form['userid']
    session['userid'] = userid
    password = request.form['password']
    try:
        loginf = g.conn.execute('''SELECT userid FROM users WHERE userid = %s AND password = %s''',
                                (userid, password))
        loginff = loginf.fetchone()
        if loginff:
            user, review, wishlist, keyword= profile(userid)
            s = g.conn.execute('SELECT * FROM users WHERE userid=%s', userid)
            ss = s.fetchone()
            session['userid'] = ss[0]
            session['password'] = ss[1]
            session['nickname'] = ss[2]
            session['age'] = ss[3]
            session['gender'] = ss[4]
            session['imageurl'] = ss[5]
            session['email'] = ss[6]
            session['description'] = ss[7]
            loginf.close()
            s.close()
            return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('login.html')


@app.route('/register', methods=['POST'])
def register():
    description = request.form['description']
    gender = request.form['gender']
    imageurl = request.form['imageurl']
    password = request.form['password']
    nickname = request.form['nickname']
    age = request.form['age']
    email = request.form['email']
    try:
        useridl = g.conn.execute('''SELECT COUNT(*) FROM users''')
        s = list(useridl)
        # s='[(11L,)]'
        n = re.findall('(\d+L,)', str(s))
        if n != []:
            nS = re.findall('\d+', n[0])
            userid = int(nS[0]) + 1
        else:
            print("emmm")
        g.conn.execute(
            '''INSERT INTO users (userid,password,nickname,age,gender,imageurl,email,description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (userid, password, nickname, age, gender, imageurl, email, description))
        user, review, wishlist, keyword= profile(userid)
        useridl.close()
        return render_template("profile.html", u=user, r=review, w=wishlist, k=keyword)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('register.html')


def profile(id):
    cursor = g.conn.execute("SELECT * FROM users WHERE userid=" + str(id))
    datas = []
    for result in cursor:
        datas.append(result)
    cursor.close()
    # cursor2=g.conn.execute("SELECT * FROM review WHERE userid=%s",str(id))
    cursor2 = g.conn.execute(
        "SELECT M.title, R.movieid, R.comment, R.rating, R.liked, R.modifiedtime FROM movie M, review R WHERE M.movieid=R.movieid AND R.userid=%s",
        str(id))
    datas2 = []
    for result in cursor2:
        datas2.append(result)
    cursor2.close()
    # cursor3=g.conn.execute("SELECT * FROM wishlist WHERE userid=%s",str(id))
    cursor3 = g.conn.execute(
        "SELECT M.title, W.movieid, W.modifiedtime FROM movie M, wishlist W WHERE M.movieid=W.movieid AND W.userid=%s",
        str(id))
    datas3 = []
    for result in cursor3:
        datas3.append(result)
    cursor3.close()
    cursor4 = g.conn.execute(
        "SELECT M.title, K.movieid, K.content FROM movie M, keyword K WHERE M.movieid=K.movieid AND K.userid=%s",
        str(id))
    datas4 = []
    for result in cursor4:
        datas4.append(result)
    cursor4.close()
    return datas, datas2, datas3, datas4


def movieinfo(id):
    try:
        cursor = g.conn.execute('''SELECT * FROM movie WHERE movieid = ''' + str(id))
        datas = []
        for result in cursor:
            datas.append(result)
        cursor.close()
        cursor = g.conn.execute('''SELECT * FROM movie WHERE movieid = ''' + str(id))
        ss = cursor.fetchone()
        session['movieid'] = ss[0]
        session['title'] = ss[1]
        session['popularity'] = ss[2]
        session['genre'] = ss[3]
        session['revenue'] = ss[4]
        cursor.close()

        cursor = g.conn.execute(
            "SELECT A.name, A.gender, A.age FROM movie M, actor A, perform P WHERE A.actid=P.actid AND M.movieid=P.movieid AND M.movieid=%s",
            str(id))
        datas3 = []
        for result in cursor:
            datas3.append(result)
        cursor.close()

        cursor = g.conn.execute(
            "SELECT D.name, D.gender, D.age FROM movie M, director D, direct DD WHERE  D.directorid=DD.directorid AND DD.movieid=M.movieid AND M.movieid=%s",
            str(id))
        datas4 = []
        for result in cursor:
            datas4.append(result)
        cursor.close()

        cursor = g.conn.execute(
            "SELECT M.title, R.movieid, R.comment, R.rating, R.liked, R.modifiedtime, R.reviewid FROM movie M, review R WHERE M.movieid=R.movieid AND R.movieid=%s",
            str(id))
        datas2 = []
        for result in cursor:
            datas2.append(result)
        cursor.close()

        cursor = g.conn.execute(
            "SELECT DISTINCT M.title, M.movieid, K.content FROM keyword K, movie M WHERE K.movieid=M.movieid AND M.movieid=%s",
            str(id))
        datas5 = []
        for result in cursor:
            datas5.append(result)
        cursor.close()

        cursor = g.conn.execute(
            "SELECT M.title, M.movieID, R.country, R.language FROM regions R, movie M, show S WHERE R.regionid=S.regionid AND S.movieid=M.movieid AND M.movieid=%s",
            str(id))
        datas6 = []
        for result in cursor:
            datas6.append(result)
        cursor.close()

        return datas, datas2, datas3, datas4, datas5, datas6
        # return datas,datas2
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')


def reviewinfo(id):
    try:
        cursor2 = g.conn.execute(
        "SELECT M.title, R.movieid, R.comment, R.rating, R.liked, R.modifiedtime FROM movie M, review R WHERE M.movieid=R.movieid AND R.reviewid=%s",
        str(id))
        datas = []
        for result in cursor2:
            datas.append(result)
        cursor2.close()
        cursor = g.conn.execute('''SELECT * FROM review WHERE reviewid = ''' + str(id))
        ss = cursor.fetchone()
        session['reviewid'] = ss[0]
        session['ruserid'] = ss[1]
        session['rmovieid'] = ss[2]
        session['comment'] = ss[3]
        session['rating'] = ss[4]
        session['liked'] = ss[5]
        session['modifiedtime'] = ss[6]
        cursor.close()
        datastotal = datas
        context = dict(data=datastotal)
        return context
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')


@app.route('/movieListID', methods=['POST'])
def movie():
    movieid = request.form['movie']
    try:
        movie, review, actor, director, keyword, region= movieinfo(movieid)
        return render_template("movieListID.html", m=movie, r=review, a=actor, d=director, k=keyword, rr=region)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')


@app.route('/movieListTitle', methods=['POST'])
def movie4():
    movietitle = request.form['movie']
    print("movietitle", movietitle)
    try:
        cursor = g.conn.execute('''SELECT M.movieid FROM movie M WHERE M.title=''' + "'" + movietitle + "'")
        ss = cursor.fetchone()
        print("ss", ss)
        movieid = ss[0]
        print("movieid,ss[0]", movieid)
        cursor.close()
        movie, review, actor, director, keyword, region= movieinfo(movieid)
        return render_template("movieListID.html", m=movie, r=review, a=actor, d=director, k=keyword, rr=region)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')




@app.route('/movieListGenre', methods=['POST'])
def movie2():
    genre = request.form['option']
    try:
        cursor = g.conn.execute('''SELECT * FROM movie WHERE genre=%s''', genre)
        datas = []
        for result in cursor:
            datas.append(result)
        cursor.close()
        context = dict(data=datas)
        return render_template("movieListGenre.html", **context)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')

@app.route('/movieListKeyword', methods=['POST'])
def movie_keyword():
    keyword = request.form['movie']
    try:
        cursor = g.conn.execute('''SELECT * FROM movie M, keyword K WHERE M.movieid=K.movieid AND K.content=%s''', keyword)
        datas = []
        for result in cursor:
            datas.append(result)
        cursor.close()
        context = dict(data=datas)
        return render_template("movieListKeyword.html", **context)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')

@app.route('/movieListPopularity', methods=['POST'])
def movie_popularity():
    rating = request.form['option']
    try:
        cursor = g.conn.execute('''SELECT * FROM movie M WHERE M.popularity=%s''', str(rating))
        datas = []
        for result in cursor:
            datas.append(result)
        cursor.close()
        print("datas", datas)
        context = dict(data=datas)
        return render_template("movieListPopularity.html", **context)
    except Exception as e:
        error = str(e)
        print(error)
    return render_template('index2.html')


if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
