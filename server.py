import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = ' '

# DATABASEURI = "postgresql://zz2551:9306@34.73.239.32/proj"
DATABASEURI = "postgresql://zz2551:9306@34.73.21.127/proj1part2"

engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
    try:
      g.conn = engine.connect()
    except:
      print "uh oh, problem connecting to database" 
      import traceback
      traceback.print_exc()
      g.conn = None

@app.teardown_request
def teardown_request(exception):
    try:
      g.conn.close()
    except Exception as e:
      pass
'''
Start
'''
# login first
@app.route('/')
def index():
    if session:
        session.clear()
    return render_template("homepage.html")
#-------------------------------------login------------------------------------#
@app.route('/login')
def login_index():
    return render_template("login.html")

@app.route('/login', methods = ['POST'])
def login():
    cid = request.form['cid']
    session['cid'] = cid
    password = request.form['password']
    error = None

    try:
        print "step-1"
        login_success = g.conn.execute("SELECT cid FROM customer WHERE cid = %s AND password = '%s'" % (cid, password))
        print('You were successfully logged in')
        return render_template("homepage.html")
    except Exception as e:
        error = str(e)
        print(error)

        #error = 'Invalid username or password. Please try again!'
        print(error)
    return render_template("login.html", error = error)

#-------------------------------------Register------------------------------------#
@app.route('/register')
def register_index():
    return render_template("register.html")

@app.route('/register',methods = ['POST'])
def register():
    cname = request.form['name']
    cid = request.form['cid']
    password = request.form['password']
    phone_no = request.form['phone_no']
    passport_no = request.form['passport_no']
    email = request.form['email']
  
    try:
        g.conn.execute("INSERT INTO customer (cid,cname,password,phone_no,passport_no,email) VALUES(%s,'%s','%s','%s','%s','%s')" %
          (cid,cname,password,phone_no,passport_no,email))
        session['cid'] = cid
        return render_template("login.html")
    except Exception as e:
        error = str(e)
        print(error)
    return render_template("register.html")

#-------------------------------------homepage------------------------------------#

@app.route('/homepage')
def homepage_index():
    return render_template("homepage.html")

@app.route('/homepage', methods = ['POST'])
def homepage():
    if 'cid' not in session:
        return render_template("login.html")
    from_city = request.form['from_city']
    to_city = request.form['to_city']
    ddate = request.form['d_date']
    ticket_type = request.form['ticket_type'] 

    # find the airport code of the corresponding city 
    from_airport = g.conn.execute("SELECT apcode FROM airport WHERE city = '%s'" % (from_city))
    to_airport = g.conn.execute("SELECT apcode FROM airport WHERE city = '%s'" % (to_city))
    from_ap = []
    to_ap = []
    for result in from_airport:
        from_ap.append(result[0])
    for result in to_airport:
        to_ap.append(result[0])
    print from_ap,to_ap

    # based on the airport code and the departure date, find all the flights 
    # flightno, from_ap, to_ap, ddate, dtime, adate, atime, price
    try:
        # find the flightno
        cursor = g.conn.execute(
            # "SELECT * FROM flight WHERE (from_ap, to_ap, ddate) = ('%s','%s','%s')" % (from_ap[0], to_ap[0], ddate))
            "select * from flight natural join (select tickets.flightno,tickets.type,min(tickets.price) as lowestprice from (SELECT flightno FROM flight WHERE (from_ap, to_ap, ddate) = ('%s','%s','%s')) as f left outer join tickets on f.flightno = tickets.flightno group by tickets.flightno,tickets.type) t" % 
            (from_ap[0], to_ap[0], ddate)
        )
        # flight number
        flights = []
        for result in cursor:
            flights.append(result)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = flights)
        # print context

        return render_template("flight.html", **context)

    except:
        return render_template("homepage.html")

#-------------------------------------tickets details------------------------------------#

@app.route('/tickets/<flightno>')
def tickets(flightno):
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    session['flightno'] = flightno
    print cid,flightno

    try: 
        
        cursor = g.conn.execute(
            # "SELECT * FROM flight WHERE (from_ap, to_ap, ddate) = ('%s','%s','%s')" % (from_ap[0], to_ap[0], ddate))
            "select * from tickets where flightno = '%s'" % flightno
        )
        tickets = []
        for result in cursor:
            tickets.append(result)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = tickets)
        # print context
        return render_template("tickets.html", **context)
    except:
        return render_template("homepage.html")

#-------------------------------------tickets details------------------------------------#
@app.route('/tickets/<ticket_no>')
def reserve(ticket_no):
    print(ticket_no)
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    flightno = session['flightno']
    try:
        print "Hereing!!!!!!!!!!"
        # g.conn.execute("INSERT INTO reservation (cid,ticket_no,flightno) VALUES('%s','%s','%s')" %
        #   (cid,ticket_no,flightno))
        # g.conn.execute("DELETE FROM tickets WHERE ticket_no = '%s'" % ticket_no)
        # t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        return render_template("homepage.html")
    except:
        return render_template("homepage.html")

#-------------------------------------inquiry airplane and airline------------------------------------#
@app.route('/airplane/<flightno>')
def airplane(flightno):
    print(ticket_no)
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    flightno = session['flightno']
    try: 
        airlane_name = g.conn.execute("select apname from airplane natural join airline natural join assigned_to where flightno = '%s'" % flightno)
        apname = []
        for result in airplane_name:
            apname.append(result[0])

        cursor = g.conn.execute(
            # "SELECT * FROM flight WHERE (from_ap, to_ap, ddate) = ('%s','%s','%s')" % (from_ap[0], to_ap[0], ddate))
            "select * from airplane natural join airline natural join assigned_to where apname = '%s'" % apname)
        air_datas = []
        for result in cursor:
            air_datas.append(result)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = air_datas)
        # print context
        return render_template("airplane.html", **context)
    except:
        return render_template("homepage.html")

#-------------------------------------run engin------------------------------------#

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


    run()
