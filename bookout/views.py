# Views
from flask import Response
from flask import jsonify
from GetBook import get_book
from books.models import isbn_lookup

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''
	
def index():
	return "Hello world!<br/><a href=/book/0671027360>Look up: Angels and Demons</a>"
	
def lookup_book(ISBN):
	#	return get_book(ISBN)
	book = isbn_lookup(ISBN)
	return Response(book.title)
	#return jsonify(get_book(ISBN))
