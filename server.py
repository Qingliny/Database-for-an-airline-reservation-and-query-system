
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, flash, request, render_template, g, redirect, Response, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = ' '

DATABASEURI = "postgresql://zz2551:9306@34.73.21.127/proj1part2"
# DATABASEURI = " "

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
def home():
  return render_template("login.html")
#-------------------------------------login------------------------------------#
@app.route('/login')
def login_index():
  return render_template("login.html")

@app.route('/login', methods = ['GET','POST'])
def login():
  cid = request.form['cid']
  session['cid'] = cid
  password = request.form['password']
  error = None

  if request.method == 'POST':
    try:
      login_success = g.conn.execute('SELECT cid FROM customer WHERE cid = %s AND password = %s' % (cid, password))
      flash('You were successfully logged in')
      return redirect('homepage.html', error = error)
    except:
      error = 'Invalid username or password. Please try again!'
      print(error)
    return render_template('login.html', error = error)

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
    g.conn.execute('INSERT INTO customer (cid,cname,password,phone_no,passport_no,email) VALUES(%s,%s,%s,%s,%s,%s)' %
      (cid,cname,password,phone_no,passport_no,email))
    return redirect('login.html', session['cid'] = cid)
  except Exception as e:
    error = str(e)
    print(error)
  return render_template('register.html')
  
#-------------------------------------homepage------------------------------------#





if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
