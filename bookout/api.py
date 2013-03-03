################################### Web service calls ###################################
# Views
from flask import Response, jsonify, request
from books.models import Book
from accounts.models import UserAccount
from utilities.JsonIterable import *

def get_book(ISBN):
	book = Book.get_by_isbn(ISBN)
	if not book:
		return jsonify({"Message":"Book not found"})
	else:
		return jsonify(JsonIterable.dictionary(book.to_dict()))
		
def view_library():
	useraccount = UserAccount.get_current()
	if not useraccount:
		return jsonify({"Error":"User not signed in"})

	books = {}
	i = 0
	for copy in useraccount.get_library():
		book = Book.query(Book.key == copy.book).get()
		books[i] = book.to_dict()
		i += 1
	return jsonify(JsonIterable.dict_of_dict(books))
	
def library_book(ISBN):
	useraccount = UserAccount.get_current()
	if not useraccount:
		return jsonify({"Error":"User not signed in"})
		
	if request.method == 'GET':
		#check the database to see if the book is in the user's library
		book = Book.get_by_isbn(ISBN)
		if book:
			if useraccount.get_book(book):
				return jsonify(JsonIterable.dictionary(book.to_dict()))
			else:
				return jsonify({"Message":"This book is not in your library"})
		else:
			return jsonify({"Message":"Book not found"})
	elif request.method == 'POST':
		#add the book to the user's library
		#If not found, add it to the cache, then to the user's library
		book = Book.get_by_isbn(ISBN)

		if not book:
			return jsonify({"Message":"Book not found"})
		else:
			if useraccount.get_book(book):
				return jsonify({"Message":"This book is already in your library"})
			useraccount.add_book(book)
			return jsonify({"Message":"Book " + ISBN + " was added to your library"})
	elif request.method == 'DELETE':	
		#remove the book from the user's library
		book = Book.get_by_isbn(ISBN)
		if not book:
			return jsonify({"Message":"Book not found"})
		else:
			if useraccount.get_book(book):
				useraccount.remove_book(book)
			return jsonify({"Message":"Successfully deleted " + ISBN + " from your library"})
	else:
		#this should never be reached
		return jsonify({"Error":"Invalid http request"})


