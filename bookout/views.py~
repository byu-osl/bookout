# Views
from flask import Response, jsonify, render_template
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

######################## Internal calls (to be called by ajax) ##########################
def lookup_book(ISBN):
	book = isbn_lookup(ISBN)
	if book == False:
		return "<b>Book Not Found!</b>"
	else:
		return Response(book.title)

################################### Web service calls ###################################
def get_book(ISBN):
	book = isbn_lookup(ISBN)
	if book == False:
		return "<b>Book Not Found!</b>"
	else:
		return book.title
