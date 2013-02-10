from google.appengine.ext import ndb
from bookout.GetBook import external_book_search
from datetime import datetime

class Book(ndb.Model):
	"""Cached representation of a book"""
	isbn = ndb.StringProperty(required=True)
	last_update = ndb.DateTimeProperty()

	title = ndb.StringProperty(required=True)
	author = ndb.StringProperty(required=True)



def isbn_lookup(isbn):
	"""Get information about a book from an ISBN (International Standard Book Number) 
	
	This function first checks the local database for a cached version of the requested ISBN. If no
	cache exists (or if the cached data is 'stale') it will lookup the ISBN through one or more 
	external APIs and cache the recieved data.
	
	Keyword arguments:
	isbn -- the isbn being searched
	
	Return value:
	An instance of a Book object which represents the book associated with the provided ISBN; else
	None if the ISBN could not be resolved to a Book object.
	"""
	book = Book.query(Book.isbn==isbn).get()
	if book:
		pass
	else:
		book_data = external_book_search(isbn)
		print "book not in datastore, but i got the book title from google: %s" %(book_data['volumeInfo']['title'])    #book_data['title'])
		book = Book(isbn=isbn,title=book_data['volumeInfo']['title'],author=book_data['volumeInfo']['authors'][0],last_update=datetime.now())
		book.put()
	return book



