################################### Web service calls ###################################
# Views
from flask import Response, jsonify, request
from books.models import Book

def get_book(ISBN):
	book = Book.get_by_isbn(ISBN)
	if not book:
		return "<b>Book Not Found!</b>"
	else:
		return book.title
		
def view_library():
	return "all books"
	
def library_book(ISBN):
	return "book"
