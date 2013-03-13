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
	return render_response('managelibrary.html')
	
def network():
	return render_response('managenetworkconnections.html')
	
def discover():
	return render_response('discover.html')
	
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

def login():
	"""view for handling authentication requests
	
	"""
	if request.method == "POST" and "username" in request.form:
		# get the username from the form
		username = request.form["username"]
		account = authenticate_account(username=username)
		if account:
			if login_account(account):
				return redirect(request.args.get("next") or url_for("library"))
			else:
				pass
		else:
			pass
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
def library_requests(ISBN):
	useraccount = current_user()
	#if not useraccount:
	#	logging.info("there is not a user logged in")
	#	return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		book = Book.get_by_isbn(ISBN)
		if book:
			if useraccount.get_book(book):
				return book.title
			else:
				return "You do not have this book in your library"
		else:
			return "This book was not found"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_isbn(ISBN)

		if not book:
			return "Book " + ISBN + " was not found"
		else:
			if useraccount.get_book(book):
				return "This book is already in your library"
			useraccount.add_book(book)
			return "Book " + ISBN + " was added to " + users.get_current_user().nickname() + "'s library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		book = Book.get_by_isbn(ISBN)
		if not book:
			return "Book not found"
		else:
			if useraccount.get_book(book):
				useraccount.remove_book(book)
			return "Successfully deleted " + ISBN + " from your library"
	else:
		#this should never be reached
		return "Error: http request was invalid"

def get_my_book_list():
	useraccount = current_user()
	#if not useraccount:
	#	logging.info("there is not a user logged in")
	#	return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	retstring = "<table>"
	for copy in useraccount.get_library():
		book = Book.query(Book.key == copy.book).get()
		retstring += "<tr><td>" + book.title + "</td><td><button onclick=\"remove_book('" + book.isbn + "');\">Remove</button></td></tr>"
	retstring += "</table>"
	return retstring

def search_for_book(value, attribute=None, page = 0, per_page=10):
	books = Book.search_by_attribute(int(page), int(per_page), attribute, value)
	if books == False:
		return jsonify({"Message":"No books found"})
	else:
		return jsonify(JsonIterable.dict_of_dict(books))

