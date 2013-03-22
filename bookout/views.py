# Views
from google.appengine.api import users
from flask import Response, jsonify, render_template, request, url_for, redirect, flash
from books.models import Book
import logging
from decorators import crossdomain
from bookout import app
from utilities.JsonIterable import *
from accounts import authenticate as authenticate_account, login as login_account, logout as logout_account, current_user, login_required
from accounts.models import UserAccount

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''

@app.route("/crossdomain")
@crossdomain(origin='*')
def test_view():
	"""test view for checking accessibility of cross-domain ajax requests
	
	"""
	return "this is a response"

def render_response(template, *args, **kwargs):
	"""helper function for adding variables for the template processor
	
	"""
	return render_template(template, *args, user=current_user(), **kwargs)

################################ Website landing pages ##################################
def index():
	return render_response('home.html')
	
def library():
	booklist = []
	useraccount = current_user()
	for copy in useraccount.get_library():
		book = Book.query(Book.key == copy.book).get()
		booklist.append(book)
	return render_response('managelibrary.html', books=booklist)
	
def network():
	return render_response('network.html')
	
def discover():
	return render_response('discover.html')
	
def searchbooks(searchterm):
	booklist = Book.search_books_by_attribute(searchterm)
	return render_response('searchbooks.html', books=booklist, search=searchterm)
	
def settings():
	return render_response('settings.html')
	
def sign_up():
	return render_response('join.html')
	
def about():
	return render_response('aboutbookout.html')
	
def mobile_app():
	return render_response('mobileapp.html')
	
def donate():
	return render_response('donate.html')

def register():
	if request.method == "POST" and "name" in request.form and "username" in request.form and "password" in request.form and "email" in request.form:
		name = request.form["name"]
		username = request.form["username"]
		if UserAccount.get_by_username(username):
			flash("Invalid username. Please choose another.")
		else:
			password = request.form["password"]
			email = request.form["email"]
			#check email
			account = UserAccount.create_user(name, username, password, email)
			if account:
				if login_account(account):
					return redirect(request.args.get("next") or url_for("index"))
				else:
					flash("Could not log in")
			else:
				flash("User could not be created")
	return render_template("register.html")

def login():
	"""view for handling authentication requests
	
	"""
	if request.method == "POST" and "username" in request.form and "password" in request.form:
		# get the username from the form
		username = request.form["username"]
		password = request.form["password"]
		account = authenticate_account(username=username,password=password)
		if account:
			if login_account(account):
				return redirect(request.args.get("next") or url_for("library"))
	return render_response('signin.html')

def logout():
	logout_account()
	return redirect("/")

@login_required
def manage_library():
	retstring = ""
	for copy in current_user().get_library():
		retstring += copy.display() + "<br>"
	return  render_template('library.html',username=current_user().username,books=get_my_book_list(),logout_url="/logout")
	
def logout_url():
	return users.create_logout_url(url_for('index'))

######################## Internal calls (to be called by ajax) ##########################
def library_requests(OLKey):
	cur_user = current_user()
	if not cur_user:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		book = Book.get_by_key(OLKey)
		if book:
			if cur_user.get_book(book):
				return book.title
			else:
				return "You do not have this book in your library"
		else:
			return "This book was not found"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_key(OLKey)

		if not book:
			return "Book " + OLKey + " was not found"
		else:
			if cur_user.get_book(book):
				return "This book is already in your library"
			cur_user.add_book(book)
			return "Book " + OLKey + " was added to your library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		book = Book.get_by_key(OLKey)
		if not book:
			return "Book not found"
		else:
			if cur_user.get_book(book):
				cur_user.remove_book(book)
			return "Successfully deleted " + OLKey + " from your library"
	else:
		#this should never be reached
		return "Error: http request was invalid"

def get_my_book_list():
	cur_user = current_user()
	if not cur_user:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	retstring = "<table>"
	for copy in cur_user.get_library():
		book = Book.query(Book.key == copy.book).get()
		retstring += "<tr><td>" + book.title + "</td><td><button onclick=\"remove_book('" + book.OLKey + "');\">Remove</button></td></tr>"
	retstring += "</table>"
	return retstring

def search_for_book(value, attribute=None):
	books = Book.search_books_by_attribute(value,attribute)
	if len(books) == 0:
		return jsonify({"Message":"No books found"})
	else:
		return jsonify(JsonIterable.dict_of_dict(books))

def manage_connections(otherUserID = None):
	cur_user = current_user()

	if request.method == 'GET':
		connections = cur_user.get_all_connections()
		users = []
		result = "you have " + str(len(connections)) + " connections"
		for connection in connections:
			result += "<br>" + connection.name
			user = dict()
			user["name"] = connection.name
			user["email"] = connection.email
			user["username"] = connection.username
			user["id"] = connection.get_id()
			users.append(user)
		return jsonify({"connectedUsers":users})
	elif request.method == 'POST':
		cur_user = current_user()
		otherUser = UserAccount.getuser(int(otherUserID))
		if cur_user.add_connection(otherUser):
			return jsonify({"Message":"Connection successfully created"})
		else:
			return jsonify({"Message":"Connection already existed"})
	elif request.method == 'DELETE':
		cur_user = current_user()
		otherUser = UserAccount.getuser(int(otherUserID))
		if cur_user.remove_connection(otherUser):
			return jsonify({"Message":"Connection successfully created"})
		else:
			return jsonify({"Message":"Connection didn't existed"})
	else:
		#this should never be reached
		return "Error: http request was invalid"
