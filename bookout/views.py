# Views
from flask import jsonify
from GetBook import get_book

def warmup():
	# https://developers.google.com/appengine/docs/python/config/appconfig#Warmup_Requests
	# This function loads the views into the new instance when
	# one has to start up due to load increases on the app
	return ''
	
def index():
	return "Hello world!<br/><a href=/book/0671027360>Look up: Angels and Demons</a>"
	
def lookup_book(ISBN):
	return jsonify(get_book(ISBN))
	
