from google.appengine.ext import ndb
from GetBook import external_book_search
from datetime import datetime,timedelta
import logging
from bookout.accounts.models import UserAccount


class Book(ndb.Model):
	"""Cached representation of a book"""
	isbn = ndb.StringProperty(required=True)
	last_update = ndb.DateTimeProperty()
	
	title = ndb.StringProperty(required=True)
	author = ndb.StringProperty(required=True)
	
	
	def update_cache(self):
		"""update cached information about the book using the external book apis
		
		Book must have an isbn specified or this will always return False
		
		"""
		if self.isbn:
			logging.debug("update_cache(%s)" %self.isbn)
			book_data = external_book_search(self.isbn)
			if book_data:
				if self.title != book_data['volumeInfo']['title']:
					if self.title:
						logging.info("Title for %s changed from '%s' to '%s'" %(self.isbn,self.title,book_data['volumeInfo']['title']))
					self.title = book_data['volumeInfo']['title']
				if self.author != book_data['volumeInfo']['authors'][0]:
					if self.author:
						logging.info("Title for %s changed from '%s' to '%s'" %(self.isbn,self.author,book_data['volumeInfo']['authors'][0]))
					self.author = book_data['volumeInfo']['authors'][0]
				if not self.last_update:
					logging.info("ISBN:%s successfully resolved and added to cache" %self.isbn)
				self.last_update = datetime.now()
				self.put()
				return True
			else:
				# TODO: if there is already an object but the search failed, that is an error
				logging.debug("ISBN:%s was not found in external databases" %self.isbn)
				
		else:
			logging.error("update_cache() called on a Book without an ISBN")
		return False

	
	def cache_expired(self):
		"""determine if the cached information in the database needs to be refreshed
		
		"""
		return (datetime.now() - self.last_update) > timedelta(minutes=1)
	
	
	@classmethod
	def get_by_isbn(cls,isbn=None):
		"""Convert an ISBN to a Book object
		
		This is a factory method that converts an ISBN into a Book object (if possible),
		abstracting away any caching/external APIs necessary to the Book's use
		
		Arguments:
		isbn -- the ISBN being searched
		
		Return value:
		An instance of a Book object with the given ISBN; if the ISBN could not be resolved
		to a Book object, returns None
		
		"""
		if not isbn:
			logging.error("Book.get_by_isbn() called without an ISBN")
			return None
		logging.debug("Book.get_by_isbn(%s)" %isbn)
		book = Book.query(Book.isbn==isbn).get()
		if book:
			logging.debug("ISBN:%s was found in the book cache" %isbn)
			if book.cache_expired():
				book.update_cache()
		else:
			logging.debug("ISBN:%s not found in cache; performing external search" %isbn)
			book = Book(isbn=isbn)
			if not book.update_cache():
				book = None
		return book


class BookCopy(ndb.Model):
	"""A model for linking User to Books
	
	This method was chosen over a List object on the User Account because this allows more 
	flexibility for adding additional information about a particular copy of a Book
	
	"""
	
	book = ndb.KeyProperty(kind=Book)
	account = ndb.KeyProperty(kind=UserAccount)

	def display(self):
		book = Book.query(Book.key == self.book).get()
		return book.title


