import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import time
from flask import Flask, flash, request, render_template, g, redirect, url_for, Response, session

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
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    return redirect('order')

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
#-------------------------------------View Orders----------------------------------------#
@app.route('/order')
def order_view():
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    try:
        cursor = g.conn.execute("with a as (select reserve_code,time,status,delay from forder),b as (select cid,ticket_no,reserve_code,flightno from reservation),c as (select ticket_no, flightno,price from soldtickets),d as (select flightno,ddate,dtime from flight) select * from a natural join b natural join c natural join d where b.cid = '%s'" % cid)
        order_data = []
        for result in cursor:
            order_data.append(result)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = order_data)
        return render_template("order.html",**context)
    except:
        return render_template("homepage.html")



#-------------------------------------homepage search------------------------------------#

@app.route('/homepage')
def homepage_index():
    return render_template("homepage.html")

@app.route('/homepage', methods = ['POST'])
def homepage():
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
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

#-------------------------------------flight details------------------------------------#

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

#-------------------------------------tickets selection and booking------------------------------------#
@app.route('/tickets/selection/<ticket_no>')
def reserve(ticket_no):
    print(ticket_no)
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    flightno = session['flightno']
    session['ticket_no'] = ticket_no

    try:
        # print "Hereing!!!!!!!!!!"
        # add the ticket record into reservation 
        g.conn.execute("INSERT INTO reservation (cid,ticket_no,flightno) VALUES('%s','%s','%s')" %
         (cid,ticket_no,flightno))
        # extract the reserver code
        # print "extract the reserver code!!!!!!!!!!"
        reservation = g.conn.execute("select reserve_code from reservation where cid = '%s' order by reserve_code desc limit 1" % cid)
        reserve_code = []
        for result in reservation:
            reserve_code.append(result[0])
        print reserve_code
        # creat a new record of order
        # print "creat a new record of order!!!!!!!!!!"
        time_stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print time_stamp
        delay_time = '0 hour'
        status = 'booked'
        # print "Lets do this !!!!!!!!!!!!!!!!!!!"
        g.conn.execute("INSERT INTO forder (reserve_code, customer_id, time, delay, status) VALUES ('%s','%s','%s','%s','%s')" % 
            (reserve_code[0], cid, time_stamp, delay_time, status)
            )
        # add the sold tickets into SoldTicket!!!!!!!!!!
        # print "add the sold tickets into SoldTicket!!!!!!!!!!"
        g.conn.execute("INSERT INTO SoldTickets (select * from tickets where ticket_no = '%s')" % ticket_no)

        # delete the tickets from tickets!!!!!!!!!!

        # print "delete the tickets from tickets!!!!!!!!!!"
        g.conn.execute("DELETE FROM tickets WHERE ticket_no = '%s'" % ticket_no)

        # show orders
        # cursor = g.conn.execute("with a as (select reserve_code,time,status,delay from forder), b as (select cid, reserve_code,flightno from reservation),c as (select flightno,price from soldtickets),d as (select flightno,ddate,dtime from flight) select * from a natural join b natural join c natural join d WHERE b.cid = '%s'" % cid)
        # order_data = []
        # for result in cursor:
        #     order_data.append(result)  # can also be accessed using result[0]
        # cursor.close()
        # context = dict(data = order_data)
        # return render_template("order.html",**context)
        return redirect('order')
    except:
        return redirect('homepage')
#-------------------------------------Return tickets------------------------------------#
@app.route('/return', methods = ['POST'])
def return_tickets():
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    reserve_code = request.form['return_ticket']
    
    # get corresponding ticket number
    cursor = g.conn.execute("select ticket_no from reservation where reserve_code = '%s'" % reserve_code)
    returned_tickets_no = []
    for result in cursor:
        returned_tickets_no.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    print returned_tickets_no

    try:
        status = 'Returned'
        # update the order information as status is returned
        g.conn.execute("UPDATE forder SET status = '%s' WHERE reserve_code = '%s'" % (status,reserve_code))
        g.conn.execute("INSERT INTO tickets (select * from SoldTickets where ticket_no = '%s')" % returned_tickets_no[0])
        g.conn.execute("DELETE FROM SoldTickets WHERE ticket_no = '%s'" % returned_tickets_no[0])
        
        # return order.html
        # cursor = g.conn.execute("with a as (select reserve_code,time,status,delay from forder), b as (select cid, reserve_code,flightno from reservation),c as (select flightno,price from soldtickets),d as (select flightno,ddate,dtime from flight) select * from a natural join b natural join c natural join d WHERE b.cid = '%s'" % cid)
        # order_data = []
        # for result in cursor:
        #     order_data.append(result)  # can also be accessed using result[0]
        # cursor.close()
        # context = dict(data = order_data)
        return redirect('order.html')
    except:
        return redirect('homepage.html')


#-------------------------------------Update Delay time of flight------------------------------------#
@app.route('/update', methods = ['POST'])
def update_delay():
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    flightno = request.form['update_flight']
    delay_time = request.form['delay_time']


    # find the corresponding reservation code
    cursor = g.conn.execute("select reserve_code from reservation where flightno = '%s'" % flightno)
    update_reserve_code = []
    for result in cursor:
        update_reserve_code.append(result[0])  # can also be accessed using result[0]
    cursor.close()
    print delay_time, update_reserve_code

    try:
        #update the order delay
        
        g.conn.execute("UPDATE forder SET delay = '%s' WHERE reserve_code = '%s'" % (delay_time,update_reserve_code[0]))
        # print "Hereing!!!!!!!!!!!!!!!!"
        # cursor = g.conn.execute("with a as (select reserve_code,time,status,delay from forder), b as (select cid, reserve_code,flightno from reservation),c as (select flightno,price from soldtickets),d as (select flightno,ddate,dtime from flight) select * from a natural join b natural join c natural join d WHERE b.cid = '%s'" % cid)
        # order_data = []
        # for result in cursor:
        #     order_data.append(result)  # can also be accessed using result[0]
        # cursor.close()
        # context = dict(data = order_data)
        return redirect('order')
    except:
        return redirect('homepage')
#-------------------------------------inquiry airplane and airline------------------------------------#
@app.route('/airplane/<flightno>')
def airplane(flightno):
    print flightno
    if 'cid' not in session:
        return render_template("login.html")
    cid = session['cid']
    session['flightno'] = flightno
    try: 
        airplane_name = g.conn.execute("select apname from airplane natural join airline natural join assigned_to where flightno = '%s'" % flightno)
        apname = []
        for result in airplane_name:
            apname.append(result[0])
        print apname
        cursor = g.conn.execute(
            # "SELECT * FROM flight WHERE (from_ap, to_ap, ddate) = ('%s','%s','%s')" % (from_ap[0], to_ap[0], ddate))
            "select * from airplane natural join airline natural join assigned_to where apname = '%s'" % apname[0])
        air_datas = []
        for result in cursor:
            air_datas.append(result)  # can also be accessed using result[0]
        cursor.close()
        context = dict(data = air_datas)
        # print context

        return render_template("airplane.html", **context)
    except:
        return redirect('homepage')

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




