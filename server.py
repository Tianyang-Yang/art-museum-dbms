#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://ww2505: @35.196.158.126/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)

  # get entities data from databases 
  artpieces = g.conn.execute("select name from artpieces")
  apnames = []
  for result in artpieces:
    apnames.append(result['name'])
  artpieces.close()

  exhibitions = g.conn.execute("select name from exhibitions")
  exhibnames = []
  for result in exhibitions:
    exhibnames.append(result['name'])
  exhibitions.close()

  galleries = g.conn.execute("select name from galleries")
  galnames = []
  for result in galleries:
    galnames.append(result['name'])
  galleries.close()

  employees = g.conn.execute("select name from employees")
  empnames = []
  for result in employees:
    empnames.append(result['name'])
  employees.close()

  customers = g.conn.execute("select name from customers")
  custnames = []
  for result in customers:
    custnames.append(result['name'])
  customers.close()

  context = dict(ap_data = apnames, exhib_data = exhibnames, gal_data = galnames, \
                  emp_data = empnames, cust_data = custnames)
  return render_template("index.html", **context)


#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
# @app.route('/another')
# def another():
#   return render_template("another.html")

# urls decorators
@app.route('/addap')
def addap():
  artists = g.conn.execute("select name from artists;")
  artistnames = []
  for result in artists:
    artistnames.append(result['name'])
  return render_template("addap.html", artistdata = artistnames)

@app.route('/addexhib')
def addexhib():
  galleries = g.conn.execute("select name from galleries;")
  galnames = []
  for result in galleries:
    galnames.append(result['name'])
  
  artpieces = g.conn.execute("select name from artpieces left join belongs_to using(pid) \
                              where eid is null;")
  apnames = []
  for result in artpieces:
    apnames.append(result['name'])
  
  context = dict(galdata = galnames, apdata = apnames)
  return render_template("addexhib.html", **context)

@app.route('/addgal')
def addgal():
  return render_template("addgal.html")

@app.route('/adddept')
def adddept():
  return render_template("adddept.html")

@app.route('/addemp')
def addemp():
  departments = g.conn.execute("select name from departments;")
  deptnames = []
  for result in departments:
    deptnames.append(result['name'])
  return render_template("addemp.html", data = deptnames)

@app.route('/updateemp')
def updateemp():
  employees = g.conn.execute("select name from employees;")
  empnames = []
  for result in employees:
    empnames.append(result['name'])
  return render_template("updateemp.html", data = empnames)

@app.route('/addcust')
def addcust():
  return render_template("addcust.html")

@app.route('/personnel')
def personnel():
  # managers = g.conn.execute("select departments.name, employees.name from departments, manages, employees where departments.did=manages.did and manages.ssn=employees.ssn;")
  # mngnames = []
  # for result in managers:
  #   mngnames.append(result['name'])
  # managers.close()
  managers = g.conn.execute("select departments.name as dept, employees.name as mng \
                              from departments, manages, employees \
                              where departments.did=manages.did and manages.ssn=employees.ssn \
                              union select name, null from departments;")
  dept_mng = {}
  for result in managers:
    key = result['dept']
    if key not in dept_mng:
      if result['mng'] is not None:
        dept_mng[key] = [result['mng']]
    else:
      if result['mng'] is not None:
        dept_mng[key].append(result['mng'])
  managers.close()

  employees = g.conn.execute("select departments.name as dept, employees.name as emp \
                              from departments, works_in, employees \
                              where departments.did=works_in.did and works_in.ssn=employees.ssn \
                              union select name, null from departments;")
  dept_emp = {}
  for result in employees:
    key = result['dept']
    if key not in dept_emp:
      if result['emp'] is not None:
        dept_emp[key] = [result['emp']]
    else:
      if result['emp'] is not None:
        dept_emp[key].append(result['emp'])
  employees.close()

  emp = g.conn.execute("select name, ssn, age from employees;")
  empn = []
  empssn = []
  empage = []
  for result in emp:
    empn.append(result['name'])
    empssn.append(result['ssn'])
    empage.append(result['age'])
  emp.close()

  departments = g.conn.execute("select name from departments")
  deptnames = []
  for result in departments:
    deptnames.append(result['name'])
  departments.close()

  context = dict(dept = deptnames, mngbydept = dept_mng, empbydept = dept_emp, emp_info = zip(empn, empssn, empage))

  return render_template("personnel.html", **context)

@app.route('/customer')
def customer():

  customers = g.conn.execute("select name, visit from customers")
  cust = []
  for result in customers:
    cust.append(result)
  customers.close()

  context = dict(cust_data = cust)

  return render_template("customer.html", **context)

# # Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add():
#   name = request.form['name']
#   # g.conn.execute("INSERT INTO test(name) VALUES (?);", name)
#   s = "insert into test(name) values ('{}')".format(name)
#   g.conn.execute(s)
#   return redirect('/')


# update database

# add art piece
@app.route('/add_ap', methods=['POST'])
def add_ap():
  name = request.form['name']
  year = request.form['year']
  genre = request.form['genre']
  fm = request.form['format']
  artist = request.form['artist']
  pid = g.conn.execute('select max(pid) from artpieces').first()
  pid = int(pid['max'])+1
  s = "insert into artpieces(pid, year, name, genre, format, artist) \
      values ('{}', '{}', '{}', '{}','{}','{}')" \
      .format(pid, year, name, genre, fm, artist)
  if artist == 'Other':
    artist_name = request.form['artist-name']
    birth = request.form['birth']
    death = request.form['death']
    country = request.form['country']
    aid = g.conn.execute('select max(aid) from artists').first()
    aid = int(aid['max'])+1
    s1 = "insert into artists(aid, name, birth, death, country) \
         values ('{}', '{}', '{}', '{}','{}');" \
         .format(aid, artist_name, birth, death, country)
    try:
      g.conn.execute(s1)
    except:
      return render_template("error.html")
  else:
    aid = g.conn.execute("select aid from artists where name = '{}';".format(artist)).first()
    aid = aid['aid']
  try:  
    g.conn.execute(s)
    g.conn.execute("insert into creates(pid, aid) values ('{}', '{}');".format(pid, aid))
  except:
    return render_template("error.html")
  return redirect('/index')

# add exhibition
@app.route('/add_exhib', methods=['POST'])
def add_exhib():
  name = request.form['name']
  begin = request.form['begin-date']
  until = request.form['end-date']
  gal = request.form['gal']
  ap = request.form.getlist('ap')
  eid = g.conn.execute('select max(eid) from exhibitions').first()
  eid = int(eid['max'])+1

  pids = []
  for a in ap:
      try:
        pid = g.conn.execute("select pid from artpieces where name = '{}';".format(a)).first()
        pid = int(pid['pid'])
      except: 
        return render_template("error.html")    
      pids.append(pid)

  s1 = "insert into exhibitions(eid, name, begin, until) \
        values ('{}', '{}', '{}', '{}');".format(eid, name, begin, until)  
  s2 = "insert into houses(name, eid) values ('{}', '{}');".format(gal, eid)

  try:
    g.conn.execute(s1)
    g.conn.execute(s2)
    for pid in pids:
      s3 = "insert into belongs_to(pid, eid) values ('{}', '{}');".format(pid, eid)
      s4 = "insert into locates(pid, name) values ('{}', '{}');".format(pid, gal)
      g.conn.execute(s3)
      g.conn.execute(s4)
  except:
    return render_template("error.html")    
  return redirect('/index')

# add gallery
@app.route('/add_gal', methods=['POST'])
def add_gal():
  # write code here
  #
  #
  return redirect('/index')

# add department
@app.route('/add_dept', methods=['POST'])
def add_dept():
  name = request.form['name']
  did = g.conn.execute('select max(did) from departments').first()
  did = int(did['max'])+1
  s = "insert into departments(did, name) \
        values ('{}', '{}');".format(did, name)
  try:
    g.conn.execute(s)
  except:
    return render_template("error.html")
  return redirect('/personnel')

# add employee
@app.route('/add_emp', methods=['POST'])
def add_emp():
  name = request.form['name']
  ssn = request.form['ssn']
  age = request.form['age']
  dept = request.form.get('dept')
  try:
    s1 = "insert into employees(ssn, name, age) \
      values ('{}', '{}', '{}');" \
      .format(ssn, name, age)
    g.conn.execute(s1)
    s2 = "select did from departments where name = '{}';".format(dept)
    did = g.conn.execute(s2).first()['did']
    s3 = "insert into works_in(did, ssn) values ('{}', '{}');".format(did, ssn)
    g.conn.execute(s3)
  except:
    return render_template("error.html")
  return redirect('/personnel')

# update employee info
@app.route('/update_emp', methods=['POST'])
def update_emp():
  name = request.form.get('name')
  ssn = request.form['ssn']
  age = request.form['age']
  dept = request.form['dept']
  pos = request.form['position']
  try:
    s1 = "insert into employees(ssn, name, age) \
      values ('{}', '{}', '{}');" \
      .format(ssn, name, age)
    s2 = "select did from departments where name = '{}';".format(dept)
    did = int(g.conn.execute(s2).first()['did'])
    s_1 = ""
    if pos == "Manager":
      s = "select exists(select true from manages where ssn = '{}');".format(ssn)
      exists = g.conn.execute(s).first()['exists']
      if exists == "t":
        s_1 = "update manages set did = '{}';".format(did)
      else:
        return render_template("error.html") 
    else:
      s = "select exists(select true from works_in where ssn = '{}');".format(ssn)
      exists = g.conn.execute(s).first()['exists']
      if exists == "t":
        s_1 = "update manages set did = '{}';".format(did)
      else:
        s_1 = "insert into works_in(did, ssn) values ('{}', '{}');".format(did, ssn) 
      g.conn.execute(s1)
      g.conn.execute(s_1)
  except:
    return render_template("error.html")
  # g.conn.execute("delete from artpieces where pid = '{}'".format(pid))
  return redirect('/personnel')

# add customer
@app.route('/add_cust', methods=['POST'])
def add_cust():
  # write code here
  #
  #
  return redirect('/')


# main
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
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
