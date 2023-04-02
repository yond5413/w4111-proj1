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
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, flash, session
## added flash and session will double check if these are fine
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = 'mysecretkey'## standard practice to have secret key


# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "rm3932"
DATABASE_PASSWRD = "4577" 
DATABASE_HOST = '34.28.53.86'#"34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

#DATABASEURI = "postgresql://rm392:4577@34.28.53.86/project1"
# This line creates a database engine that knows how to connect to the URI above.
engine = create_engine(DATABASEURI)

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
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	
	return render_template("proj1/index.html",)

#should delete before submitting 
#Only have it to view db stuff without going to the google cloud tbh
@app.route('/another')
def another():
	# DEBUG: this is debugging code to see what request looks like
	print(request.args)
	#
	# example of a database query
	#
	#select_query = "SELECT name from test"
	select_query = "SELECT * from account"#"SELECT * from admin"
	cursor = g.conn.execute(text(select_query))
	names = []
	for result in cursor:
		names.append(result)# result[0]
	cursor.close()
	
	context = dict(data = names)
	return render_template("GivenByProf/index.html",**context)#render_template("GivenByProf/another.html")

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('auth/login.html')
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		#params = {}
		## double check account table !
		#params["username"] = username
		#params["password"] = password
		select_query = "SELECT * FROM account"
		cursor = g.conn.execute(text(select_query))
		for result in cursor:
			if result[1] == username:
				print('valid username ')
				print(password)
				print(result[2])
				if result[2] == password:
					print('in login ')
				# do login stuff
					flash("Login valid please wait shortly...")
					session['user_id'] = result[0]
					session['username'] = username
					session['password'] = password
					session['firstname'] = result[3]
					session['lastname'] = result[4]
					session['account_type'] = getAccountType(session['user_id'])
					session['logged_in'] = True
					session['first_login'] = False
					cursor.close()
					
					if session['account_type'] == 'admin':
						return redirect('/admin')
					elif session['account_type'] == 'seller':
						return redirect('/seller')
					elif session['account_type'] == 'consumer':
						return redirect('/consumer')
				else:
					break 
		cursor.close()
		flash('Invalid login info please try again.')
		return redirect('/login')#render_template('auth/login.html')
@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == 'GET':
		return render_template('auth/register.html')
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		firstname = request.form['firstname']
		lastname = request.form['lastname']
		account = request.form['account']
		if not(checkUsername(username)):
			flash("Username has already been claimed.\n If this is you please login otherwise try a new username")
			redirect('/register')
		elif checkUsername(username):
			#### some insert statements and stuff 
			#### need to edit schema so id is account_id is incremented
			####
			'''
			name = request.form['name']
    		age = request.form['age']
    		c.execute("INSERT INTO users (name, age) VALUES (?, ?)", (name, age))
			conn.commit()
    		conn.close()
			'''
			#session['user_id'] = getAccountId()#result[0]
			session['username'] = username
			session['password'] = password
			session['firstname']= firstname #result[3]
			session['lastname'] = lastname #result[4]
			session['account_type'] = account#getAccountType(session['user_id'])
			session['logged_in'] = True
			session['first_login'] = True
			# add whatever to go to 
			# based on account_type
			# # first login lets us know whether to update attributes for specific cases later
			insert_query1 = 'Insert INTO '
			insert_query2 = ' (username,password,firstname,lastname) VALUES(?,?,?,?)'
			g.conn.execute(text(insert_query1+account+insert_query2),username = username,
		  	password = password, firstname = firstname, lastname = lastname)
			## do this after insertion
			## need to add auto-increment to accounts table it would make our lives much easier
			session['user_id'] = getAccountId()#result[0]
			if account == 'seller':
				#might change to redirect (/consumer)
				return  redirect('/seller')#render_template('accounts/seller.html')
			elif account == 'consumer':
				#might change to redirect (/consumer)
				return redirect('/consumer')#render_template('accounts/consumer.html')
		return render_template('auth/register.html')
@app.route('/logout')
def logout():
	'''
	#general way of doing a loggout using session object 
	session.pop('user_id', None)
    session.pop('user_type', None)
    session['logged_in'] = False
	'''
	####################################
	'''
	## can pop keys in this manner too 
	for key in list(session.keys()):
    session.pop(key, None)
	'''
	session.clear()
	return redirect("/")
###
@app.route('/admin', methods=['GET','POST'])
def admin():
	## add some stuff to index when user is logged in 
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		return render_template('accounts/admin.html')
	#elif request.method == 'POST':
		
@app.route('/consumer', methods=['GET','POST'])
def consumer():
	if request.method == 'GET':
		return render_template('accounts/consumer.html')
	elif request.method == 'POST':
		pass
@app.route('/seller', methods=['GET','POST'])
def seller():
	if request.method == 'GET':
		return render_template('accounts/seller.html')
	elif request.method == 'POST':
		pass
# for index or url: '/' add a top ten list of popular items when not logged and a prompt to login/reg
# to see full stuff later
#will add html files and etc 
# basically just bneed to have option to scroll through request/products 
#try and make others account types in a similar structure
##### admin functons here ###########
@app.route('/admin/apporve-sellers', methods=['GET','POST'])
def approve_sellers():
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		return render_template()
app.route('/admin/approve-sales-requests', methods=['GET','POST'])
def approve_sales_requests():
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		return render_template()
app.route('/admin/view-orders', methods=['GET','POST'])
def view_orders():
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		return render_template()
####################################
####### seller functons here #######
#
####################################
###### consumer functons here ######
#
####################################
### some helper functions
@app.before_request
def user_in_session():
	user_id = session.get('user_id')
	if user_id is None:
		g.user = None
	else:
		g.user = list()
		for key in list(session.keys()):
			g.user.append(session.get(key))
def getAccountType(accountId):
	## used for login
	## essentially itterate accross each table and see if id is in table
	
	select_query = 'SELECT account_id From consumer'
	result = g.conn.execute(text(select))
	for id in result:
		if id == accountId:
			print("success")
			return 'consumer'
	result.close()
	select_query = 'SELECT account_id From seller'
	result = g.conn.execute(text(select))
	for id in result:
		if id == accountId:
			print("success")
			return 'seller'
	result.close()
	select_query = 'SELECT account_id From admin'
	result = g.conn.execute(text(select))
	for id in result:
		if id == accountId:
			print("success")
			result.close()
			return 'admin'
def checkUsername(username):
	### returns true or false 
	## if username is in db account table return false
	select_query = "SELECT username FROM account"
	result =  g.conn.execute(text(select_query))
	for user in result:
		if user == username:
			result.close()
			return False
	result.close()
	return True
def getAccountType(id):
	### get account type for login 
	select_query1 = "SELECT * FROM admin"
	select_query2 = "SELECT * FROM consumer"
	select_query3 = "SELECT * FROM seller"
	##### account type ######
	admin = 'admin'
	seller = 'seller'
	consumer = 'consumer'
	#########################
	result =  g.conn.execute(text(select_query1))
	for user in result:
		if user[0] == id:
			####
			print("success")
			result.close()
			return admin
	###################################
	result =  g.conn.execute(text(select_query3))
	for user in result:
		if user[0] == id:
			####
			result.close()
			return seller
	##################################
	result =  g.conn.execute(text(select_query2))
	for user in result:
		if user[0] == id:
			####
			result.close()
			return consumer
def getAccountId():
	## return last id because it is the newest
	# done after a new entry 
	select_query = "SELECT * FROM account"
	cursor = g.conn.execute(text(select_query))
	ret = cursor[-1][0]
	return ret
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
