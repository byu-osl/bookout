# Views
from google.appengine.api import users
from flask import Response, jsonify, render_template, request, url_for
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
	return "Welcome to Bookout!<br/><a href='/library'>View My Library</a><br/>"

def manage_library():
	useraccount = UserAccount.get_current()
	if not useraccount:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	retstring = ""
	for copy in useraccount.get_library():
		retstring += copy.display() + "<br>"
	return  render_template('library.html',username=users.get_current_user().nickname(),books=get_my_book_list())
	
def get_my_book_list():
	useraccount = UserAccount.get_current()
	if not useraccount:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('manage_library'))

	retstring = ""
	for copy in useraccount.get_library():
		retstring += copy.display() + "<br>"
	return retstring

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
	useraccount = UserAccount.get_current()
	if not useraccount:
		logging.info("there is not a user logged in")
		return "<a href='%s' >Login</a>" %users.create_login_url(dest_url=url_for('library_requests',ISBN=ISBN))
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		return "You sent a GET request.  If you want to add a book to your library, send a POST"
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_isbn(ISBN)
		if not book:
			return "Book " + ISBN + " was not found"
		else:
			useraccount.add_book(book)
			return "Book " + ISBN + " was added to " + users.get_current_user().nickname() + "'s library"
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		return "This will removed the book from your library, but it doesn't right now."
	else:
		#this should never be reached
		return "Error: http request was invalid"







