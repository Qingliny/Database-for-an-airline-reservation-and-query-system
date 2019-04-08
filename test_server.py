import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")

@app.route('/another')
def another():
  	return render_template("another.html")

@app.route('/add', methods=['POST'])
def add():
	name = request.form['name']
	g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
	return redirect('/')


app.run(port=5000)