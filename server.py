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
from datetime import datetime
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

#should delete/commentout before submitting 
#Only have it to view db stuff without going to the google cloud tbh
@app.route('/another')
def another():
	# DEBUG: this is debugging code to see what request looks like
	print(request.args)
	#
	# example of a database query
	#
	#select_query = "SELECT name from test"
	select_query = "SELECT * FROM seller"
	#"SELECT * FROM sale_request WHERE request_status = false"#"SELECT * from orders"#"SELECT * from account"#"SELECT * from admin"
	cursor = g.conn.execute(text(select_query))
	orders = []
	#print(cursor.keys()[0])# prints collumn names
	for result in cursor:
		orders.append(result)# result[0]
	cursor.close()
	
	context = dict(data = orders)
	return render_template("GivenByProf/index.html",**context)#render_template("GivenByProf/another.html")

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('auth/login.html')
	elif request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		
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
			select_query = 'select count(*) from account'
			cursor = g.conn.execute(text(select_query))
			new_id = cursor.fetchone()[0]

			
			## do this after insertion
			## need to add auto-increment to accounts table it would make our lives much easier
			session['user_id'] = new_id
			if account == 'seller':
				#might change to redirect (/consumer)
				insert_query1 = 'Insert INTO seller (account_id, username, password, first_name, last_name) VALUES (' + str(new_id) + ',\'' + str(username) + '\',\'' + str(password) + '\',\'' + str(firstname) + '\',\'' + str(lastname) + '\')'
				g.conn.execute(text(insert_query1))
				g.conn.commit()
				return  redirect('/')#render_template('accounts/seller.html')
			elif account == 'consumer':
				#might change to redirect (/consumer)
				insert_query1 = 'Insert INTO consumer (account_id, username, password, first_name, last_name) VALUES (' + str(new_id) + ',\'' + str(username) + '\',\'' + str(password) + '\',\'' + str(firstname) + '\',\'' + str(lastname) + '\')'
				g.conn.execute(text(insert_query1))
				g.conn.commit()
				return redirect('/')#render_template('accounts/consumer.html')
		return render_template('auth/register.html')
@app.route('/logout')
def logout():
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
		select_query = "SELECT * from seller where included_status = false"
		cursor = g.conn.execute(text(select_query))
		sellers = []
		for entry in cursor:
			sel = {}
			sel['account_id'] = entry[0]
			sel["first_name"] = entry[3]
			sel["last_name"] = entry[4]
			sellers.append(sel)
		#### add to table and then add option to approve 
		# for post option?
		return render_template('function/admin/approve_sellers.html',sellers = sellers)
	if request.method == 'POST':
		if 'approve' in request.form:
			seller_id = request.form["account_id"]
			##
			# update seller/ added allow privelleges
			update_query = "UPDATE seller set included_status = true where account_id = " +str(seller_id)
			cursor = g.conn.execute(text(update_query))
			g.conn.commit()
			return redirect("/admin")
		elif 'decline' in request.form:
			seller_id = request.form["account_id"]
			##
			# decline either delete account or resubmit?
			# DO nothing for part 3
			#  
			return redirect("/admin")
		
@app.route('/admin/approve-sale-request', methods=['GET','POST'])
def approve_sale_request():
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		select_query = "SELECT * FROM sale_request WHERE request_status = false"
		cursor = g.conn.execute(text(select_query))
		sale_req = []
		print(cursor.keys())
		for entry in cursor:
			# salereq: column info below
			#['sale_id', 'stock', 'price', 'category', 'description', 'image', 'request_status', 'seller_id', 'name']
			# name-> product/sale-request: name
			salreq = {}
			salreq['sale_id'] = entry[0]
			salreq["price"] = entry[2]
			salreq['category'] = entry[3]
			salreq['description'] =  entry[4]
			salreq['name'] = entry[8]
			sale_req.append(salreq)
		return render_template('function/admin/approve_sale_request.html', sale_request = sale_req)
	if request.method == 'POST':
		if 'approve' in request.form:
			sale_id = request.form["sale_id"]
			## add to product table
			# update sale_request->request_status
			update_query = "UPDATE sale_request set request_status = true where sale_id = " +str(sale_id)
			cursor = g.conn.execute(text(update_query))
			g.conn.commit()
			#### add to products
			select_query = "SELECT * FROM sale_request WHERE sale_id = " +str(sale_id)
			new_prod = g.conn.execute(text(select_query))
			############################################
			#new_id = NotImplemented
			#['sale_id', 'stock', 'price', 'category', 'description', 'image', 'request_status', 'seller_id', 'name']
			stock = new_prod.fetchone()[1] 
			price = new_prod.fetchone()[2]
			category = new_prod.fetchone()[3]
			description = new_prod.fetchone()[4]
			name = new_prod.fetchone()[8]
			select_query= 'select count(*) from product'
			result = g.conn.execute(text(select_query))
			new_id = result.fetchone()[0]
			#prod_id,price,name,category,description, image, popularity, quantity
			update_query = "Insert into product(prod_id,quantity,price,category,description,name) values("+ str(new_id)+"," +str(stock)+","+str(price)+",\'" +str(category)+"\',\'"+str(description)+"\',"+",\'" +str(name)+"\')"
			g.conn.execute(text(update_query))
			g.conn.commit()
			return redirect("/admin")
		elif 'decline' in request.form:
			#seller_id = request.form["account_id"]
			# do nothing
			return redirect("/admin")
		
@app.route('/admin/view-orders', methods=['GET','POST'])
def view_orders():
	if session['account_type'] != 'admin':
		return redirect('/')
	if request.method == 'GET':
		select_query = "SELECT * FROM orders order by orders.date_time"
		cursor = g.conn.execute(text(select_query))
		orders = list()
		for result in cursor:
			ord = {}
			## key:value pair will map to parts in html
			## double check which is consumer-id and prod-id
			ord["Consumer"] = getOrderConsumername(result[2])
			# add picture ig instead of id later
			ord['Product name'] = getOrderProductname(result[1]) 
			ord['Order Time'] = result[3] ## date time object need to format properly
			ord['Address'] = result[4]
			ord['Quantity'] = result[5]
			orders.append(ord)
		return render_template('function/admin/view_orders.html', orders = orders)
	if request.method == 'POST':
		if 'button1' in request.form:           
			prod_id = request.form['button1']
		elif 'button2' in request.form:	
            # handle button2 click
			prod_id = request.form['button2']
####################################
####### seller functons here #######
#
@app.route('/seller/make-request', methods=['GET','POST'])
def make_request():
	if session['account_type'] != 'seller':
		return redirect('/')
	if request.method == "GET":
		return render_template('function/seller/make_request.html')
	if request.method == "POST":
		######################
		# salereq: column info below
		#['sale_id', 'stock', 'price', 'category', 'description', 'image', 'request_status', 'seller_id', 'name']
		stock = request.form['stock']
		price = request.form['price']
		description = request.form['description']
		category = request.form['category']
		name = request.form['name']
		
		#image = request.form['image'] #?
		select_query= 'select count(*) from sale_request'
		result = g.conn.execute(text(select_query))
		new_id = result.fetchone()[0]
		update_query = "Insert into sale_request(sale_id,stock,price,category,description,seller_id,name) values("+ str(new_id)+"," +str(stock)+","+str(price)+",\'" +str(category)+"\',\'"+str(description)+"\',"+ str(g.user["user_id"])+",\'" +str(name)+"\')"
		g.conn.execute(text(update_query))
		g.conn.commit()
		#'insert into shopping_cart values (' + str(userid) + ',' + str(prodid) + ')'
		return redirect("/seller")
@app.route('/seller/view-requests', methods=['GET','POST'])
def view_requests():
	if session['account_type'] != 'seller':
		return redirect('/')
	
	if request.method == "GET":
		### access db
		select_query = "SELECT *  FROM  sale_request WHERE seller_id ="+ str(session["user_id"])#:seller"
		#params = {'seller': g.user["user_id"]}
		cursor = g.conn.execute(text(select_query))
		sale_req = []
		print(len(cursor))
		print(g.user["user_id"])
		print(cursor.keys())
		for entry in cursor:
			# salereq: column info below
			#['sale_id', 'stock', 'price', 'category', 'description', 'image', 'request_status', 'seller_id', 'name']
			# name-> product/sale-request: name
			salreq = {}
			salreq["price"] = entry[2]
			salreq['category'] = entry[3]
			salreq['description'] =  entry[4]
			salreq['name'] = entry[8]
			#sale_req['image'] = entry[5]
			sale_req.append(salreq)
		
		return render_template('function/seller/view_requests.html',sale_request = sale_req)
	
####################################
###### consumer functons here ######
#
@app.route('/consumer/view_products', methods=['GET','POST'])
def view_products():
	if request.method == 'GET':
		select_query = "Select * from product"
		cursor = g.conn.execute(text(select_query))
		products = list()
		
		for result in cursor:
			prod = {}
			prod["Name"] = result[2]
			prod["Price"] = result[1]
			prod["Category"] = result[3]
			prod["Description"] = result[4]
			prod["Popularity"] = result[5]
			prod["Quantity"] = result[6]
			prod["ID"] = result[0]
			products.append(prod)	
		return render_template('function/consumer/view_products.html', prods=products)
	
	if request.method == 'POST':
		userid = session['user_id']
		prodid = request.form['prod_id']
		if 'cart' in request.form:
			try:
				update_query = 'insert into shopping_cart values (' + str(userid) + ',' + str(prodid) + ')'
				g.conn.execute(text(update_query))
				g.conn.commit()
			except:
				pass

			return redirect('/consumer/view_products')
			#add to shopping list table
		elif 'order' in request.form:
			select_query = 'select address from consumer where account_id = ' + str(userid) 
			cursor = g.conn.execute(text(select_query))
			address = cursor.fetchone()[0]

			select_query2 = 'select count(*) from orders'
			cursor = g.conn.execute(text(select_query2))
			new_id = cursor.fetchone()[0]
			update_query = 'INSERT into orders values (' + str(new_id) + ',' + str(prodid) + ',' + str(userid) + ',\'' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\',\'' + str(address) + '\')'
			g.conn.execute(text(update_query))
			return redirect('/consumer/view_products')

@app.route('/consumer/shopping_cart', methods=['GET', 'POST'])
def shopping_cart():
	userid = session['user_id']
	if request.method == 'GET':
		select_query = 'SELECT shopping_cart.product_id, name, price from shopping_cart, product where consumer_id = ' + str(userid) + ' and shopping_cart.product_id = product.product_id'
		cursor = g.conn.execute(text(select_query))
		products = list()

		for result in cursor:
			prod = {}
			prod["Name"] = result[1]
			prod["Price"] = result[2]
			prod["ID"] = result[0]
			products.append(prod)
		
		return render_template('function/consumer/shopping_cart.html', prods=products)  
	
	if request.method == 'POST':
		userid = session['user_id']
		prodid = request.form['prod_id']
		if 'remove' in request.form:
			update_query = 'DELETE from shopping_cart where product_id = ' + str(prodid)
			g.conn.execute(text(update_query))
			g.conn.commit()
			return redirect('/consumer/shopping_cart')
			#remove from shopping list table
		elif 'order' in request.form:
			select_query = 'select address from consumer where account_id = ' + str(userid) 
			cursor = g.conn.execute(text(select_query))
			address = cursor.fetchone()[0]

			select_query2 = 'select count(*) from orders'
			cursor = g.conn.execute(text(select_query2))
			new_id = cursor.fetchone()[0]

			update_query = 'INSERT into orders values (' + str(new_id) + ',' + str(prodid) + ',' + str(userid) + ',\'' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\',\'' + str(address) + '\')'
			g.conn.execute(text(update_query))
			update_query2 = 'DELETE from shopping_cart where product_id = ' + str(prodid)
			g.conn.execute(text(update_query2))
			g.conn.commit()
			return redirect('/consumer/shopping_cart')

@app.route('/consumer/view_cust_orders', methods=['GET', 'POST'])
def view_cust_orders():
	userid = session['user_id']
	if request.method == 'GET':
		select_query = 'SELECT orders.product_id, name, price, date_time, delivery_address from orders, product where consumer_id = ' + str(userid) + ' and orders.product_id = product.product_id'
		cursor = g.conn.execute(text(select_query))
		orders = list()

		for result in cursor:
			ord = {}
			ord['name'] = result[1]
			ord['price'] = result[2]
			ord['time'] = result[3]
			ord['address'] = result[4]
			ord['id'] = result[0]
			orders.append(ord)
		
		return render_template('function/consumer/view_cust_orders.html', ords=orders)

####################################
### some helper functions
@app.before_request
def user_in_session():
	user_id = session.get('user_id')
	if user_id is None:
		g.user = None
	else:
		g.user =dict(zip(session.keys(), session.values()))# list()
		#for key in list(session.keys()):
		#	g.user.append(session.get(key))
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
def getOrderProductname(product_id):
	select_query = "SELECT name FROM product WHERE product_id = :prod_id"
	params = {'prod_id': product_id}
	result = g.conn.execute(text(select_query), params)
	names = result.fetchone()#cursor.fetchone()
	result.close()#cursor.close()
	if result is None:#if cursor is None:
		## should never happen but just error checking
		print("Not found")
		ret = result		
		return ret
	else:
		ret = names[0]
		return ret#cursor
def getOrderConsumername(consumer_id):
	#################################
	select_query = 'SELECT first_name, last_name FROM consumer WHERE account_id = :con_id'
	params = {'con_id': consumer_id}
	result = g.conn.execute(text(select_query), params)
	names = result.fetchone()#cursor.fetchone()
	result.close()#cursor.close()
	if result is None:#if cursor is None:
		## should never happen but just error checking
		print("Not found")
		ret = result		
		return ret
	else:
		ret = names[0] +' '+ names[1] 
		return ret#cursor
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
