# Views
from flask import Response, jsonify, render_template, request
from books.models import isbn_lookup

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
	return "This is where we will view, add, and delete books from a person's library"

######################## Internal calls (to be called by ajax) ##########################
def lookup_book(ISBN):
	book = isbn_lookup(ISBN)
	if book == False:
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
