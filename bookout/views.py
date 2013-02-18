# Views
from google.appengine.api import users
from flask import Response, jsonify, render_template, request
from books.models import Book
from accounts.models import UserAccount
import logging

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''

################################ Website landing pages ##################################
def index():
	return "Hello world!<br/><a href='/search'>Search</a><br/><a href='/book/0671027360'>Look up: Angels and Demons</a>"

def search():
	return render_template('search.html')

def manage_library():
	useraccount = UserAccount.get_current()
	if not useraccount:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url="/search")
	#useraccount.add_book(Book.get_by_isbn("9788420637747"))
	retstring = "Hello, %s" %users.get_current_user().nickname() + "<br>"
	for copy in useraccount.get_library():
		retstring += copy.display() + "<br>"
	retstring += "DONE"
	return  retstring

######################## Internal calls (to be called by ajax) ##########################
def lookup_book(ISBN):
	useraccount = UserAccount.get_current()
	if not useraccount:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url="/search")
	
	book = Book.get_by_isbn(ISBN)
	if not book:
		return "<b>Book Not Found!</b>"
	else:
		return Response(book.title)
		
def library_requests(ISBN):
	headers = request.headers
	if 'USER' not in headers:
		return "please include the user in the headers from your request"
	user = headers['USER']
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		return "Book " + ISBN + " was in " + user + "'s library"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		return "Book " + ISBN + " was added to " + user + "'s library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		return "Book " + ISBN + " was removed from " + user + "'s library"
	else:
		#this should never be reached
		return "Error: http request was invalid"







