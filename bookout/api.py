################################### Web service calls ###################################
# Views
from flask import Response, jsonify, request
from books.models import isbn_lookup

def get_book(ISBN):
	book = isbn_lookup(ISBN)
	if book == False:
		return "<b>Book Not Found!</b>"
	else:
		return book.title
		
def view_library():
	return "all books"
	
def library_book(ISBN):
	return "book"
